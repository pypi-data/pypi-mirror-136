# Copyright 2021 The QHBM Library Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tools for inference on quantum Hamiltonians."""

from typing import Union

import tensorflow as tf
import tensorflow_quantum as tfq

from qhbmlib import circuit_infer
from qhbmlib import energy_infer
from qhbmlib import energy_model
from qhbmlib import hamiltonian_model
from qhbmlib import utils


class QHBM(tf.keras.layers.Layer):
  r"""Methods for inference involving normalized exponentials of Hamiltonians.

  We also call the normalized exponential of a Hamiltonian a "thermal state".
  Here we formalize some aspects of thermal states, which will be used later
  to explain particular methods of this class.

  # TODO(#119): add reference to updated QHBM paper.

  Each method takes as input some modular Hamiltonian
  $$K_{\theta\phi} = U_\phi K_\theta U_\phi^\dagger.$$
  The [thermal state][1] corresponding to the model is
  $$ \rho_T = Z^{-1} e^{-\beta K_{\theta\phi}}.$$
  For QHBMs, we assume $\beta = 1$, effectively absorbing it into the definition
  of the modular Hamiltonian.  Then $\rho_T$ can be expanded as
  $$\rho_T = \sum_x p_\theta(x)U_\phi\ket{x}\bra{x}U_\phi^\dagger,$$
  where the probability is given by
  $$p_\theta(x) = \tr[\exp(-K_\theta)]\bra{x}\exp(-K_\theta)\ket{x}$$
  for $x\in\{1, \ldots, \dim(K_{\theta\phi})\} = \mathcal{X}$. Note that each
  $U_\phi\ket{x}$ is an eigenvector of both $\rho_T$ and $K_{\theta\phi}$.

  Corresponding to this density operator is an [ensemble of quantum states][2].
  Using the terms above, we define the particular ensemble
  $$\mathcal{E} = \{p_\theta(x), U_\phi\ket{x}\}_{x\in\mathcal{X}},$$
  also known as the [canonical ensemble][2] corresponding to $\rho_T$.
  Each method of this class implicitly samples from this ensemble, then
  post-processes to perform a particular inference task.

  #### References
  [1]: Nielsen, Michael A. and Chuang, Isaac L. (2010).
       Quantum Computation and Quantum Information.
       Cambridge University Press.
  [2]: Wilde, Mark M. (2017).
       Quantum Information Theory (second edition).
       Cambridge University Press.
  """

  def __init__(self,
               e_inference: energy_infer.EnergyInference,
               q_inference: circuit_infer.QuantumInference,
               name: Union[None, str] = None):
    """Initializes a QHBM.

    Args:
      e_inference: Attends to density operator eigenvalues.
      q_inference: Attends to density operator eigenvectors.
      name: Optional name for the model.
    """
    super().__init__(name=name)
    self._e_inference = e_inference
    self._q_inference = q_inference

  @property
  def e_inference(self):
    """The object used for inference on density operator eigenvalues."""
    return self._e_inference

  @property
  def q_inference(self):
    """The object used for inference on density operator eigenvectors."""
    return self._q_inference

  def circuits(self, model: hamiltonian_model.Hamiltonian, num_samples: int):
    r"""Draws thermally distributed eigenstates from the model Hamiltonian.

    Here we explain the algorithm.  First, construct $X$ to be a classical
    random variable with probability distribution $p_\theta(x)$ set by
    `model.energy`.  Then, draw $n = $`num\_samples` bitstrings,
    $S=\{x_1, \ldots, x_n\}$, from $X$.  For each unique $x_i\in S$, set
    `states[i]` to the TFQ string representation of $U_\phi\ket{x_i}$, where
    $U_\phi$ is set by `model.circuit`.  Finally, set `counts[i]` equal to the
    number of times $x_i$ occurs in $S$.

    Args:
      model: The modular Hamiltonian whose normalized exponential is the
        density operator governing the ensemble of states from which to sample.
      num_samples: Number of states to draw from the ensemble.

    Returns:
      states: 1D `tf.Tensor` of dtype `tf.string`.  Each entry is a TFQ string
        representation of an eigenstate of the Hamiltonian `model`.
      counts: 1D `tf.Tensor` of dtype `tf.int32`.  `counts[i]` is the number of
        times `states[i]` was drawn from the ensemble.
    """
    self.e_inference.infer(model.energy)
    samples = self.e_inference.sample(num_samples)
    bitstrings, counts = utils.unique_bitstrings_with_counts(samples)
    states = model.circuit(bitstrings)
    return states, counts

  def expectation(self, model: hamiltonian_model.Hamiltonian,
                  ops: Union[tf.Tensor,
                             hamiltonian_model.Hamiltonian], num_samples: int):
    """Estimates observable expectation values against the density operator.

    TODO(#119): add expectation and derivative equations and discussions
                from updated paper.

    Implicitly sample `num_samples` pure states from the canonical ensemble
    corresponding to the thermal state defined by `model`.  For each such state
    |psi>, estimate the expectation value <psi|op_j|psi> for each `ops[j]`.
    Then, average these expectation values over the sampled states.

    Args:
      model: The modular Hamiltonian whose normalized exponential is the
        density operator against which expectation values will be estimated.
      ops: The observables to measure.  If `tf.Tensor`, strings with shape
        [n_ops], result of calling `tfq.convert_to_tensor` on a list of
        cirq.PauliSum, `[op1, op2, ...]`.  Otherwise, a Hamiltonian.
      num_samples: Number of draws from the EBM associated with `model` to
        average over.

    Returns:
      `tf.Tensor` with shape [n_ops] whose entries are are the sample averaged
      expectation values of each entry in `ops`.
    """
    self.e_inference.infer(model.energy)
    samples = self.e_inference.sample(num_samples)
    bitstrings, counts = utils.unique_bitstrings_with_counts(samples)
    if isinstance(ops, tf.Tensor):
      return self.q_inference.expectation(
          model.circuit, bitstrings, counts, ops, reduce=True)
    elif isinstance(ops.energy, energy_model.PauliMixin):
      u_dagger_u = model.circuit + ops.circuit_dagger
      expectation_shards = self.q_inference.expectation(
          u_dagger_u, bitstrings, counts, ops.operator_shards, reduce=True)
      return tf.expand_dims(
          ops.energy.operator_expectation(expectation_shards), 0)
    else:
      raise NotImplementedError(
          "General `BitstringEnergy` models not yet supported.")


def density_matrix(model: hamiltonian_model.Hamiltonian):
  e_inf = energy_infer.AnalyticEnergyInference(model.energy.num_bits)
  e_inf.infer(model.energy)
  probabilities = tf.cast(e_inf.all_probabilities, tf.complex64)
  resolved_pqc = tfq.resolve_parameters(
      model.circuit.pqc, model.circuit.symbol_names,
      tf.expand_dims(model.circuit.symbol_values, 0))
  unitary_matrix = tfq.layers.Unitary()(resolved_pqc).to_tensor()[0]
  unitary_probs = tf.multiply(
      unitary_matrix,
      tf.tile(
          tf.expand_dims(probabilities, 0), [tf.shape(unitary_matrix)[0], 1]))
  return tf.matmul(unitary_probs, tf.linalg.adjoint(unitary_matrix))


def fidelity(model: hamiltonian_model.Hamiltonian, sigma: tf.Tensor):
  e_inf = energy_infer.AnalyticEnergyInference(model.energy.num_bits)
  e_inf.infer(model.energy)
  e_rho = tf.cast(e_inf.all_probabilities, tf.complex128)
  resolved_pqc = tfq.resolve_parameters(
      model.circuit.pqc, model.circuit.symbol_names,
      tf.expand_dims(model.circuit.symbol_values, 0))
  unitary_matrix = tfq.layers.Unitary()(resolved_pqc).to_tensor()[0]
  v_rho = tf.cast(unitary_matrix, tf.complex128)
  sqrt_e_rho = tf.sqrt(e_rho)
  v_rho_sqrt_e_rho = tf.multiply(
      v_rho, tf.tile(tf.expand_dims(sqrt_e_rho, 0), (tf.shape(v_rho)[0], 1)))
  rho_sqrt = tf.linalg.matmul(v_rho_sqrt_e_rho, tf.linalg.adjoint(v_rho))
  omega = tf.linalg.matmul(
      tf.linalg.matmul(rho_sqrt, tf.cast(sigma, tf.complex128)), rho_sqrt)
  # TODO(zaqqwerty): find convincing proof that omega is hermitian,
  # in order to go back to eigvalsh.
  e_omega = tf.linalg.eigvals(omega)
  return tf.cast(
      tf.math.abs(tf.math.reduce_sum(tf.math.sqrt(e_omega)))**2, tf.float32)
