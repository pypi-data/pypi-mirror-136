"""XManager/XCloud launcher for both GPU and TPU jobs.

The launcher works with any Python binary with the following flags:

* `output_dir` is the directory for saving summaries and logs;
* `use_gpu` determines whether to run on GPU or otherwise TPU;
* `num_cores` is the number of TPU cores or GPUs;
* `tpu` is the TPU main address (flag not required if launching with GPU);
* `seed` is the experiment's random seed.

For binaries that support only certain accelerator settings, we recommend still
using these flags. Raise errors outside its support or rely on runtime errors.

To learn about experiment workflows, see
`third_party/py/qhbmlib/baselines/README.md`.

Forked from //uncertainty_baselines/baselines/xm_launcher.py
"""

import collections
import functools
import getpass
import importlib.util
import inspect
import json
import operator
import os
import random
import shutil
import tempfile
import time
from typing import Any, Dict, List, Optional, Text

from absl import app
from absl import flags
from absl import logging
from ml_collections.config_dict import config_dict
# pylint: disable=g-import-not-at-top
try:
  from xmanager import xm as xm_oss
  from xmanager import xm_local
  from xmanager.contrib import copybara
except (ImportError, ModuleNotFoundError):
  logging.exception('Cannot import open-sourced XM.')
  xm_oss = None
  xm_local = None
  copybara = None

hyper = None
xm = None

# pylint: enable=g-import-not-at-top

# Binary flags
flags.DEFINE_string(
    'binary', None,
    'Filepath to Python script to run. For external GCS experiments, it can be '
    'an absolute path to the binary, or a relative one with respect to the '
    'current folder.')
flags.mark_flag_as_required('binary')
flags.DEFINE_list(
    'args', [], 'Flag arguments to pass to binary. Follow the format '
    '--args=batch_size=64,train_epochs=300.')
flags.DEFINE_string(
    'config', None, 'Filepath to Python file with a function '
    'get_sweep(hyper) returning a hyperparameter sweep and/or '
    'a function get_config() returning a ConfigDict.')
flags.DEFINE_bool('launch_on_gcp', False, 'Whether or not to launch on GCS.')
flags.DEFINE_string(
    'cell', None,
    'Cloud region or cell for the worker (and coordinator if using TPU).')

# Accelerator flags
flags.DEFINE_string('platform', None, 'Platform (e.g., tpu-v2, tpu-v3, gpu).')
flags.DEFINE_string(
    'tpu_topology', '2x2',
    'TPU topology. Only used if platform is TPU. {x}x{y} means x*x **chips**, '
    'and because the number of devices is the number of cores, we further '
    'multiply by 2 because there are 2 cores per chip. For example, 2x2 is '
    'equivalent to an 8 core TPU slice, 8x8 = 128 cores, etc.')
flags.DEFINE_string('gpu_type', 'p100',
                    'GPU type. Only used if platform is GPU.')
flags.DEFINE_integer('num_gpus', None,
                     'Number of GPUs. Only used if platform is GPU.')
flags.DEFINE_integer('num_cpus', None, 'Number of CPUs.')
flags.DEFINE_integer('num_workers', 1, 'Number of workers (including chief)'
                     'in cluster.')
flags.DEFINE_integer(
    'memory', None, 'Amount of CPU memory in GB. Only used if launching on '
    'GCP.')
flags.DEFINE_string('experiment_name', None,
                    'Experiment name; defaults to timestamp.')
flags.DEFINE_integer('num_runs', 1,
                     'Number of runs each with a different seed.')

FLAGS = flags.FLAGS

_JobMetadata = collections.namedtuple('_JobMetadata', [
    'user',
    'cell',
    'platform_str',
    'num_workers',
    'gpu_type',
    'num_gpus',
    'tpu_topology',
    'num_cpus',
    'experiment_name',
    'memory',
])


def _get_attr(config, name: str) -> Optional[Any]:
  """Get a given attribute from the passed FLAGS or ConfigDict."""
  # Note that if a flag is passed with its default value, this will not override
  # a conflicting config value.
  has_flag_value = name in FLAGS and FLAGS[name].value != FLAGS[name].default
  if has_flag_value:
    return FLAGS[name].value
  elif config and name in config:
    return config[name]
  elif name in FLAGS:
    return FLAGS[name].default
  return None


def _build_binary_metadata(config):
  """Extracts job metadata and args from the given ConfigDict and/or FLAGS."""
  if FLAGS.binary[:2] == '//':
    # We assume the path will have at least two cmds split by '/' and
    # We will use the last two to name the experiment.
    # Ideally, the path will look like //.../{dataset}/{baseline}.py
    # but {dataset} and {baseline} can be any string in practice.
    command = FLAGS.binary.split('/')
    if len(command) >= 2:
      dataset = command[-2]
      baseline = command[-1]
      baseline = os.path.splitext(baseline)[0]
    else:
      dataset = None
      baseline = None
  else:
    pieces = FLAGS.binary.split('/')
    dataset = pieces[-2]
    baseline = pieces[-1]
    baseline = os.path.splitext(baseline)[0]

  # Handle the case where we use fragmented_python MPM paths for the binaries,
  # for example
  # //third_party/py/qhbmlib/baselines/jft:batchensemble_fragmented_mpms.
  if ':' in baseline:
    baseline = baseline.split(':')[0]

  if config:
    flag_args = config.args
    experiment_name = _get_attr(config, 'experiment_name')
  else:
    flag_args = dict(arg.split('=', 1) for arg in FLAGS.args)
    experiment_name = FLAGS.experiment_name
  dataset = flag_args.get('dataset', dataset)

  if not experiment_name:  # default experiment name
    experiment_name = time.strftime('%m%d_%H%M%S')
    if baseline is not None:
      experiment_name = f'{baseline}-{experiment_name}'
    if dataset is not None:
      experiment_name = f'{dataset}-{experiment_name}'
    if not experiment_name.islower():
      experiment_name = f'ub-{experiment_name}'

  user = _get_attr(config, 'user')
  metadata = _JobMetadata(
      user=user,
      cell=_get_attr(config, 'cell'),
      platform_str=_get_attr(config, 'platform'),
      num_workers=_get_attr(config, 'num_workers'),
      gpu_type=_get_attr(config, 'gpu_type'),
      num_gpus=_get_attr(config, 'num_gpus'),
      tpu_topology=_get_attr(config, 'tpu_topology'),
      num_cpus=_get_attr(config, 'num_cpus'),
      memory=_get_attr(config, 'memory'),
      experiment_name=experiment_name,
  )

  use_gpu = 'gpu' in metadata.platform_str or metadata.platform_str == 'cpu'

  if metadata.platform_str == 'cpu':
    num_cores = 1
  elif 'gpu' in metadata.platform_str:
    num_cores = metadata.num_gpus
  else:
    num_cores = 2 * functools.reduce(
        operator.mul, [int(i) for i in metadata.tpu_topology.split('x')])
  if 'num_cores' in flag_args and flag_args['num_cores'] != num_cores:
    raise ValueError(
        '"num_cores" requested in binary incompatible with inferred number of '
        'cores based on tpu_topology and platform_str ({}!={} respectively)'
        .format(flag_args['num_cores'], num_cores))
  args = dict(num_cores=num_cores, use_gpu=use_gpu)
  args.update(flag_args)
  return args, metadata


def _map_experiment_names(wid, params):
  """Generates name of experiment based on parameters.

  Args:
    wid: WorkerID of this parameter run.
    params: Dictionary containing mapping from parameter name to value.

  Returns:
    Reformatted string encoding the different parameter names.
  """
  if not params:
    return str(wid)

  param_values = []
  for k, v in params.items():
    if isinstance(v, float):
      param_values.append('{}:{:.8f}'.format(k, v))
    else:
      param_values.append('{}:{}'.format(k, v))
  return '{}-{}'.format(wid, '-'.join(param_values))


def _build_xm_binary(use_fragmented_python, binary_path, name, runtime,
                     platform, binary_args, adhoc_imports, config_filepath):
  """Builds an XM binary using FragmentedPythonPackage or LocalG3Packages."""
  resources = None
  # We use config_flags for JFT baselines.
  # TODO(dusenberrymw): Allow the config path to be relative to
  # third_party/py/qhbmlib.
  # `config_filepath`: Path to config to define the LocalFile resource
  # `config_ref`: Config filename, we do not support ":" parameterization.
  if config_filepath.startswith('//'):
    config_filepath = config_filepath[2:]
  config_ref = os.path.basename(config_filepath)
  google3_dir = file_util.FindGoogle3Dir(os.path.abspath('.'))
  absolute_config_filepath = os.path.join(google3_dir, config_filepath)
  config_resource = xm.LocalFile(absolute_config_filepath)
  binary_args['config'] = config_resource.path_to(config_ref)
  resources = [config_resource]
  if use_fragmented_python:
    # This is slow to build compared to the instant LocalG3Packages, so we only
    # enable this when we have to, when we are testing.
    binary_args['xprof_port'] = '%port_xprof%'
    packages_mixin = xm.FragmentedPythonPackage(binary_path, platform=platform)
    mixins = [packages_mixin]
    if '/jft' in binary_path:
      mixins.append(xm_tpu.JaxTpuMixin())
    return xm.Binary(
        binary=packages_mixin.launcher_path(),
        name=name,
        runtime=runtime,
        platform=platform,
        mixins=mixins,
        args=binary_args,
        resources=resources)
  if '/jft' in binary_path:
    raise ValueError(
        'Must run with --use_fragmented_python when launching JFT experiments, '
        'and pass the path to the fragmented MPM BUILD rule as --binary, '
        '--binary=third_party/py/qhbmlib/baselines/jft:'
        'deterministic_fragmented_mpms for example.')
  else:
    local_g3_packages = xm.LocalG3Packages(ADHOC_IMPORTS + adhoc_imports)
    if binary_path[:2].startswith('//'):
      script_path = binary_path[2:]
    else:
      script_path = (f'third_party/py/qhbmlib/baselines/' f'{binary_path}')
    return xm.MLPythonScript(
        script_path=local_g3_packages.path_to(script_path),
        name=name,
        runtime=runtime,
        platform=platform,
        mixins=[local_g3_packages],
        interpreter_args={'xprof_port': '%port_xprof%'},
        args=binary_args)


def _tpu_platform_str_to_fish(platform_str):
  if platform_str == 'tpu-v2':
    platform_str = 'jf'
  if platform_str == 'tpu-v3':
    platform_str = 'df'
  if platform_str == 'tpu-v4':
    platform_str = 'pf'
  return platform_str


def _launch_xcloud_experiment(sweep, args, metadata):
  """Create an experiment to launch on XCloud."""
  if metadata.cell != metadata.coordinator_cell:
    logging.warning(
        'Ignoring different coordinator and accelerator cells, defaulting to '
        'the accelerator cell.')

  if metadata.coordinator_priority != 'prod':
    # TODO(znado): support batch CPUs.
    logging.warning('Ignoring pre-emptible priority for CPUs.')

  output_dir = args.get('output_dir', None)
  if output_dir and output_dir.startswith('/cns'):
    raise ValueError(
        'Must pass an output_dir that points to a GCS bucket, for example: '
        'gs://xcloud_public_bucket/rdl-moonshot/USER/MY_OUTPUT_DIR instead of '
        f'/cns/cell-d/home/USER/MY_OUTPUT_DIR (received {output_dir}).')
  if output_dir is None:
    # TODO(znado): set up RDL specific GCS.
    output_dir = f'gs://xcloud_public_bucket/rdl-moonshot/{metadata.user}/'
    if metadata.experiment_name == FLAGS.experiment_name:
      # Default experiment_name is unique, but a custom one may not be. So add
      # timestamp to its directory name.
      timestamp = time.strftime('%m%d_%H%M%S')
      output_dir = os.path.join(output_dir,
                                f'{metadata.experiment_name}_{timestamp}')
    else:
      output_dir = os.path.join(output_dir, f'{metadata.experiment_name}')

  # XCloud doesn't support magic commands like xm.experiment.work_unit_id. As a
  # workaround, set output directory as a hyperparameter in the sweep if it
  # isn't already there.
  add_output_dir = True
  for hparams in sweep:
    if 'output_dir' in hparams:
      add_output_dir = False
  if add_output_dir:
    work_unit_ids = range(1, len(sweep) + 1)
    output_dirs = [os.path.join(output_dir, str(wid)) for wid in work_unit_ids]
    output_dirs = hyper.sweep('output_dir', hyper.categorical(output_dirs))
    sweep = hyper.zipit([sweep, output_dirs])

  if FLAGS.binary[:2].startswith('//'):
    script_path = FLAGS.binary[2:]
  else:
    script_path = (f'third_party/py/qhbmlib/baselines/' f'{FLAGS.binary}')

  accelerator = None
  platform_str = _tpu_platform_str_to_fish(metadata.platform_str)
  if platform_str in ['jf', 'df']:
    if metadata.priority == 'batch':
      platform_str += '-pre'
    accelerator = xcloud.TPU(
        platform_str, metadata.tpu_topology, tf_version='nightly')
    if 'data_dir' not in args:
      args['data_dir'] = 'gs://tfds-data/datasets'
      # Switching to the google-only version of the bucket go/tfds/gcs.
      args['data_dir'] = 'gs://tensorflow-datasets/datasets'
  elif platform_str == 'gpu':
    if metadata.priority == 'batch':
      # TODO(znado): support batch GPUs.
      logging.warning('Ignoring pre-emptible priority for GPUs.')
    accelerator = xcloud.GPU('nvidia-tesla-' + metadata.gpu_type,
                             metadata.num_gpus)
  cell = metadata.cell
  if cell not in ['america', 'europe', 'asia']:
    logging.warning(
        'Ignoring cell, specify one of [\'america\', \'europe\', \'asia\'] '
        'as an XCloud location.')
    cell = None
  runtime = xcloud.CloudRuntime(
      location=cell,
      cpu=metadata.num_cpus,
      memory=metadata.memory,
      accelerator=accelerator)

  # TODO(znado): generate a pre-built Docker image that just needs the current
  # workspace copied over.

  def get_g3_path():
    # Based on `google3.ads.production.capacity.google3_root.GetRepositoryRoot
    path = os.path.dirname(os.path.abspath(__file__))
    idx = path.rfind('/google3')
    if idx != -1:
      google3_root = path[:idx] + '/google3'
      if os.path.isdir(google3_root):
        return google3_root
    raise ValueError('Error: PWD is not a CITC client.')

  g3 = get_g3_path()
  xcloud_copybara = xcloud.Copybara(
      copybara_file=os.path.join(g3, 'third_party/py/qhbmlib/copy.bara.sky'),
      workflow='local',
      origin_folder=os.path.dirname(g3))
  upgrade_python_step = (
      xcloud.steps.upgrade_system_python(FLAGS.python_version)
      if FLAGS.python_version else [])
  build_steps = (
      xcloud.steps.install_base_dependencies() + upgrade_python_step +
      xcloud.steps.copy_project_files('qhbmlib') + [
          # Install the dependencies for the latest qhbmlib, while
          # also incorporating local workspace changes.
          'pip3 --no-cache-dir install -e '
          '/workdir/qhbmlib[experimental,models,datasets]'
      ])
  # Get the directory the binary is in, without the 'third_party/py/'.
  script_dir = '/'.join(script_path.split('/')[2:-1])
  script_name = script_path.split('/')[-1]
  exec_cmds = [
      f'cd {script_dir}',  # cd into the dir containing the binary.
      f'python3 {script_name} "$@"'  # Call binary, passing the flags.
  ]
  # if we collect tensorboard logs, they should be written to GCS / not locally
  if args.get('collect_profile'):
    args['output_dir'] = output_dir
  executable = xcloud.CloudPython(
      name=metadata.experiment_name.replace('_', '-'),
      runtime=runtime,
      project_path='qhbmlib',
      args=args,
      copybara=xcloud_copybara,
      build_steps=build_steps,
      exec_cmds=exec_cmds)

  # TODO(b/191094036): Re-enable ParallelExecutable as needed after bug fix.
  experiment = xcloud.ParameterSweep(executable, sweep)
  experiment = xcloud.WithTensorBoard(experiment, output_dir)
  description = xcloud.ExperimentDescription(
      experiment_name=metadata.experiment_name.replace('_', '-'),
      project_name='qhbmlib',
      tags=metadata.tags)
  if FLAGS.config:
    description.add_config_file(FLAGS.config.strip('/'))

  xcloud.launch(description, experiment)


def _launch_xmanager_experiment(sweep, args, metadata, config_filepath):
  """Create an experiment to launch on XM."""
  cell = metadata.cell or xm.Borg.default_cell_selector()
  # Build flag arguments to pass to binary.
  output_dir = args.get('output_dir')
  if output_dir is None:
    output_dir = f'/cns/{cell}-d/home/%{xm.experiment.author}%/'
    if metadata.ttl > 0:
      output_dir = os.path.join(output_dir, f'ttl={metadata.ttl}d')
    if metadata.experiment_name == FLAGS.experiment_name:
      # Default experiment_name is unique, but a custom one may not be. So add
      # experiment ID to its directory name.
      output_dir = os.path.join(
          output_dir, f'{metadata.experiment_name}_%{xm.experiment.id}%')
    else:
      output_dir = os.path.join(output_dir, f'{metadata.experiment_name}')
  work_unit_output_dir = os.path.join(
      output_dir, f'%{xm_helper.experiment.work_unit_hyper_str}%')
  args['output_dir'] = work_unit_output_dir

  is_jft_job = '/jft' in FLAGS.binary

  # Build executable for either GPU or TPU.
  priority = xm.ServiceTier.from_str(metadata.priority)
  scheduling = dict(
      max_task_failures=metadata.max_task_failures,
      max_per_task_failures=metadata.max_per_task_failures)
  overrides = xm.BorgOverrides(scheduling=scheduling)
  platform_str = _tpu_platform_str_to_fish(metadata.platform_str)
  platform = xm.Platform.from_str(platform_str)
  if platform in [xm.Platform.CPU, xm.Platform.GPU]:
    if is_jft_job:
      raise ValueError('JFT only supported on TPUs.')
    if platform == xm.Platform.CPU:
      requirements = xm.Requirements(
          cpu=metadata.num_cpus,
          tmp_ram_fs_size=FLAGS.tmp_ram_fs_size,
          # ram=100 * xm.GiB,
          # autopilot=False
      )
    else:
      requirements = xm.Requirements(
          gpu=metadata.num_gpus,
          gpu_types=[xm.GpuType.from_str(metadata.gpu_type)],
          tmp_ram_fs_size=FLAGS.tmp_ram_fs_size)
    worker_runtime = xm.Borg(
        cell=cell,
        service_tier=priority,
        requirements=requirements,
        overrides=overrides,
        logs_read_access_roles=['all'])
    if metadata.gfs_user:
      args['gfs_user'] = metadata.gfs_user
    experiment = _build_xm_binary(
        use_fragmented_python=FLAGS.use_fragmented_python,
        binary_path=FLAGS.binary,
        name='chief',
        runtime=worker_runtime,
        platform=platform,
        binary_args=args,
        adhoc_imports=FLAGS.adhoc_imports,
        config_filepath=config_filepath)
    # jobs = list(
    #     xm_dist_strat_helper.build_multi_worker_mirrored_strategy_jobs(
    #         chief=experiment,
    #         num_workers=metadata.num_workers,
    #         worker_name='worker'),)
    jobs = [experiment]
  else:
    assert xm.Platform.is_tpu(platform)
    if is_jft_job:
      requirements = xm.Requirements(
          topology=xm.TpuTopology(metadata.tpu_topology))
      runtime = xm.Borg(
          cell=cell,
          service_tier=priority,
          requirements=requirements,
          overrides=overrides,
          logs_read_access_roles=['all'])
      if metadata.gfs_user:
        args['gfs_user'] = metadata.gfs_user
      job = _build_xm_binary(
          use_fragmented_python=FLAGS.use_fragmented_python,
          binary_path=FLAGS.binary,
          name='chief',
          runtime=runtime,
          platform=platform,
          binary_args=args,
          adhoc_imports=FLAGS.adhoc_imports,
          config_filepath=config_filepath)
      jobs = [job]
    else:
      coordinator_requirements = xm.Requirements(
          tmp_ram_fs_size=FLAGS.tmp_ram_fs_size)
      coordinator_runtime = xm.Borg(
          cell=metadata.coordinator_cell or cell,
          service_tier=xm.ServiceTier.from_str(metadata.coordinator_priority),
          requirements=coordinator_requirements,
          overrides=xm.BorgOverrides(scheduling=scheduling),
          logs_read_access_roles=['all'])
      coordinator = _build_xm_binary(
          use_fragmented_python=FLAGS.use_fragmented_python,
          binary_path=FLAGS.binary,
          name='coordinator',
          runtime=coordinator_runtime,
          platform=xm.Platform.CPU,
          binary_args=args,
          adhoc_imports=FLAGS.adhoc_imports,
          config_filepath=config_filepath)
      worker_requirements = xm.Requirements(
          topology=xm.TpuTopology(metadata.tpu_topology))
      worker_runtime = xm.Borg(
          cell=cell,
          service_tier=priority,
          requirements=worker_requirements,
          overrides=overrides,
          logs_read_access_roles=['all'])

      tpu_args = {
          'brain_rpc_layer': 'grpc',
          'brain_session_gc_seconds': 86400,
          # http://g/tpu-users/ddzRXr1l-Ls
          'grpc_register_default_sigterm_handler': False,
      }
      if metadata.gfs_user:
        tpu_args['gfs_user'] = metadata.gfs_user
      coordinator, worker = xm_helper.build_tpu_jobs(
          coordinator=coordinator,
          tpu_runtime=worker_runtime,
          tpu_platform=platform,
          brain_port_name='',
          args=tpu_args,
      )

      # Pass main address to the --tpu flag.
      # pylint: disable=protected-access
      def tpu_mixin(spec):
        spec.args = xm_helper.update_args(
            spec.args,
            tpu=xm_tpu.get_master_address(worker._name),
            **xm_helper.get_common_args())

      # This relies on the first mixin to be the one that adds the correct flag.
      mixin = coordinator._mixins.pop(1)
      assert mixin.__name__ == 'coordinator_mixin'
      coordinator._mixins.insert(0, tpu_mixin)
      # pylint: enable=protected-access
      jobs = [coordinator, worker]

  experiment = xm.ParallelExecutable(jobs, name=metadata.experiment_name)

  if is_jft_job:
    map_fn = lambda wid, params: _map_experiment_names(wid, None)
  else:
    map_fn = _map_experiment_names

  experiment = xm_helper.parameter_sweep(
      experiment,
      sweep,
      map_fns={'work_unit_hyper_str': map_fn},
      max_parallel_work_units=2**3)
  experiment = xm.WithTensorBoard(experiment, output_dir)
  experiment = xm_helper.WithMLDash(
      experiment,
      output_dir,
      description=' '.join(['#' + tag for tag in metadata.tags]),
      experiment_name=metadata.experiment_name)

  description = xm.ExperimentDescription(
      experiment_name=metadata.experiment_name,
      project_name='qhbmlib',
      tags=metadata.tags)
  if FLAGS.config:
    description.add_config_file(FLAGS.config.strip('/'))

  xm.launch_experiment(description, experiment)


def _split_path_to_ub(filepath):
  """For a path '/a/b/c/baselines/...', return '/a/b/c', 'baselines/...'."""
  filepath = os.path.abspath(filepath)
  pieces = filepath.split('/')
  dir_index = None
  for pi, piece in enumerate(pieces):
    if piece in ['experimental', 'baselines']:
      dir_index = pi
      break
  if dir_index is None:
    raise ValueError(
        'Unable to parse FLAGS.binary ({}) to find the location of the '
        'qhbmlib project.'.format(filepath))
  project_dir = '/'.join(pieces[:dir_index])
  binary_path = '/'.join(pieces[dir_index:])
  return project_dir, binary_path


def _launch_gcp_experiment(project_dir, binary_path, sweep, args, metadata):
  """Launch a job on GCP using the Cloud AI Platform."""
  logging.info('Using %s as the project dir.', project_dir)

  # TODO(znado): support different caip regions, etc.?
  with xm_local.create_experiment(metadata.experiment_name) as experiment:
    # Note that we normally would need to append a "$@" in order to properly
    # forward the args passed to the job into the python command, but the XM
    # library already does this for us.
    run_cmd = f'python {binary_path}'
    # These images are necessary to get tf-nightly pre-installed.
    # Our lazy loading `__getattr__ = _lazy_import` in `__init__.py` requires
    # at least Python 3.7, so we use a base image that has Python 3.7.
    if metadata.platform_str == 'gpu':
      base_image = 'tensorflow/tensorflow:nightly-gpu'
      # base_image = 'gcr.io/deeplearning-platform-release/tf2-gpu.2-5'
    else:
      base_image = 'tensorflow/tensorflow:nightly'
      # base_image = 'gcr.io/deeplearning-platform-release/tf2-cpu.2-5'
    pip_cmd = 'pip --no-cache-dir install'
    spec = xm_oss.PythonContainer(
        path=project_dir,
        base_image=base_image,
        entrypoint=xm_oss.CommandList([run_cmd]),
        docker_instructions=[
            f'COPY {os.path.basename(project_dir)}/ uncertainty-baselines',
            'RUN apt-get update && apt-get install -y git netcat',
            'RUN python -m pip install --upgrade pip setuptools wheel',
            # # Uninstall TF2.5 so that the UB pip install will install nightly.
            # 'RUN python -m pip uninstall -y tensorflow tf-nightly',
            f'RUN {pip_cmd} google-cloud-storage',
            f'RUN {pip_cmd} ./uncertainty-baselines[experimental,models]',
            'WORKDIR uncertainty-baselines',
        ],
    )
    [executable] = experiment.package([
        xm_oss.Packageable(
            executable_spec=spec,
            executor_spec=xm_local.Caip.Spec(),
        ),
    ])

    platform = {}
    if 'tpu' in metadata.platform_str:
      # To run on a tpu-v2-8, tpu_topology should be 2x2.
      pieces = map(int, metadata.tpu_topology.split('x'))
      num_tpus = pieces[0] * pieces[1] * 2  # 2 cores per TPU chip.
      platform = {metadata.platform_str.split('-')[-1]: num_tpus}
    elif metadata.platform_str == 'gpu':
      platform = {metadata.gpu_type: metadata.num_gpus}

    if metadata.num_cpus is not None:
      platform['cpu'] = metadata.num_cpus * xm_oss.vCPU
    if metadata.memory is not None:
      platform['memory'] = metadata.memory * xm_oss.GiB
    executor = xm_local.Caip(xm_oss.JobRequirements(**platform))

    # Create one job per setting in the hyperparameter sweep. The default case
    # is a length 1 sweep with a single argument name "seed".
    for ji, sweep_args in enumerate(sweep):
      job_args = args.copy()
      if 'output_dir' in job_args:
        job_args['output_dir'] = os.path.join(job_args['output_dir'], str(ji))
      if 'data_dir' in job_args and job_args.get('download_data', False):
        job_args['data_dir'] = os.path.join(job_args['data_dir'], str(ji))
      # Overwrite any values in `args` with the `sweep_args`.
      job_args.update(sweep_args)
      logging.info('Launching job %d/%d with args %s.\n', ji + 1, len(sweep),
                   json.dumps(job_args, indent=4, sort_keys=True))
      job = xm_oss.Job(
          executable=executable,
          executor=executor,
          args=job_args,
      )
      experiment.add(job)


def _generate_hyperparameter_sweep(
    config_module, config: config_dict.ConfigDict,
    project_dir: Optional[str]) -> List[Dict[Text, Any]]:
  """Generate the hyperparameter sweep."""
  hyper_module = hyper
  if FLAGS.config and 'get_sweep' in dir(config_module):
    if hyper_module is None:
      raise ValueError('Need a hyperparameter module to construct sweep.')
    if FLAGS.num_runs != 1:
      raise ValueError('FLAGS.num_runs not supported with config.get_sweep().')
    sweep = config_module.get_sweep(hyper_module)
  else:
    sweep = [{
        'seed': seed + random.randint(0, 1e10)
    } for seed in range(FLAGS.num_runs)]
  return sweep


def _load_config_helper(config_path, launch_on_gcp):
  """Get the ConfigDict from config_path:get_config()."""
  config_module_spec = importlib.util.spec_from_file_location(
      '', os.path.abspath(config_path))
  config_module = importlib.util.module_from_spec(config_module_spec)
  config_module_spec.loader.exec_module(config_module)
  config = None
  if 'get_config' in dir(config_module):
    # Check if get_config takes a parameter called launch_on_gcp, and if so then
    # pass in FLAGS.launch_on_gcp.
    get_config_inspect = inspect.getfullargspec(config_module.get_config)
    get_config_params = get_config_inspect.args
    if 'launch_on_gcp' in get_config_params:
      config = config_module.get_config(launch_on_gcp=launch_on_gcp)
    else:
      config = config_module.get_config()
  return config_module, config


def _load_config(config_path, launch_on_gcp):
  """Load the ConfigDict if one was passed in as FLAGS.config."""
  if config_path:
    config_module = None
    if not config_module:
      config_module, config = _load_config_helper(config_path, launch_on_gcp)
  else:
    config_module = None
    config = None
  return config_module, config


def main(argv):
  del argv  # unused arg
  config_module, config = _load_config(FLAGS.config, FLAGS.launch_on_gcp)
  args, metadata = _build_binary_metadata(config)
  if FLAGS.launch_on_gcp:
    project_dir, binary_path = _split_path_to_ub(FLAGS.binary)
    sweep = _generate_hyperparameter_sweep(config_module, config, project_dir)
    return _launch_gcp_experiment(project_dir, binary_path, sweep, args,
                                  metadata)

  sweep = _generate_hyperparameter_sweep(
      config_module, config, project_dir=None)
  if FLAGS.launch_on_xcloud:
    if xcloud is None:
      raise ValueError('xcloud could not be imported.')
    return _launch_xcloud_experiment(sweep, args, metadata)
  else:
    return _launch_xmanager_experiment(sweep, args, metadata, FLAGS.config)


if __name__ == '__main__':
  app.run(main)
