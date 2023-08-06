# Copyright 2021 qclib project.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Optimized unitary gates.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.extensions.quantum_initializer.diagonal import DiagonalGate
import qiskit.quantum_info as qi
from qiskit.circuit.library import RXGate, RYGate, RZGate

# This gate E is called the "magic basis". It can be used to convert between
# SO(4) and SU(2) x SU(2). For A in SO(4), E A E^\dag is in SU(2) x SU(2).
E = np.array([[1, 1j, 0, 0], [0, 0, 1j, 1], [0, 0, 1j, -1], [1, -1j, 0, 0]]) / np.sqrt(2)
Edag = E.conj().T

# Helpful to have static copies of these since they are needed in a few places.
CNOT01 = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
CNOT10 = np.array([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]])
SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])

S_SX = np.array(
    [
        [0.5 + 0.5j, 0.5 - 0.5j, 0.0 + 0.0j, 0.0 + 0.0j],
        [0.5 - 0.5j, 0.5 + 0.5j, 0.0 + 0.0j, 0.0 + 0.0j],
        [0.0 + 0.0j, 0.0 + 0.0j, -0.5 + 0.5j, 0.5 + 0.5j],
        [0.0 + 0.0j, 0.0 + 0.0j, 0.5 + 0.5j, -0.5 + 0.5j],
    ]
)

def two_qubits_two_cnots(u):
    #from scipy.stats import ortho_group, unitary_group
    #U=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
    #u = ortho_group.rvs(4)
    #u = unitary_group.rvs(4)
    #w, v = np.linalg.eig(U)
    #U = np.diag(w)
    U = _convert_to_su4(u)
    print(_compute_num_cnots(U))

    #phases = np.angle(np.diagonal(U))
    #diag = np.exp(-1j * phases)

    # the trace has only a real part
    U1 = U #@ np.diag(diag)
    #print(np.trace(U1))
    #print(np.angle(np.diag(diag)))
    #print(np.angle(U))
    #print(np.angle(U1))
    #print(U1 @ np.conj(U1.T))
    reg = QuantumRegister(2)
    circuit = QuantumCircuit(reg)

    circuit.append(_decomposition_2_cnots(U1), [0,1])
    #diag_gate = DiagonalGate(diag.tolist())
    #circuit.append(diag_gate, [0,1])
    #circuit.append(_decomposition_3_cnots(U1), [0,1])

    det = np.linalg.det(u)
    angle = np.angle(det) / 4
    circuit.global_phase += angle

    #print('U1\n',u)
    #print('circuit\n',qi.Operator(circuit).data)

    return circuit


def _convert_to_su4(U):
    r"""Convert a 4x4 matrix to :math:`SU(4)`.

    Args:
        U (array[complex]): A matrix, presumed to be :math:`4 \times 4` and unitary.

    Returns:
        array[complex]: A :math:`4 \times 4` matrix in :math:`SU(4)` that is
        equivalent to U up to a global phase.
    """
    # Compute the determinant
    det = np.linalg.det(U)

    exp_angle = -1j * np.angle(det) / 4
    return U * np.exp(exp_angle)

def _compute_num_cnots(U):
    r"""Compute the number of CNOTs required to implement a U in SU(4). This is based on
    the trace of

    .. math::

        \gamma(U) = (E^\dag U E) (E^\dag U E)^T,

    and follows the arguments of this paper: https://arxiv.org/abs/quant-ph/0308045.
    """
    u = np.dot(Edag, np.dot(U, E))
    gammaU = np.dot(u, np.transpose(u))
    trace = np.trace(gammaU)

    # Case: 0 CNOTs (tensor product), the trace is +/- 4
    # We need a tolerance of around 1e-7 here in order to work with the case where U
    # is specified with 8 decimal places.
    if np.allclose(trace, 4, atol=1e-7) or np.allclose(trace, -4, atol=1e-7):
        return 0

    # To distinguish between 1/2 CNOT cases, we need to look at the eigenvalues
    evs = np.linalg.eigvals(gammaU)

    sorted_evs = sorted(np.imag(evs))

    # Case: 1 CNOT, the trace is 0, and the eigenvalues of gammaU are [-1j, -1j, 1j, 1j]
    # Checking the eigenvalues is needed because of some special 2-CNOT cases that yield
    # a trace 0.
    if np.allclose(trace, 0j, atol=1e-7) and np.allclose(sorted_evs, [-1, -1, 1, 1]):
        return 1

    # Case: 2 CNOTs, the trace has only a real part (or is 0)
    if np.allclose(np.imag(trace), 0.0, atol=1e-7):
        return 2

    # For the case with 3 CNOTs, the trace is a non-zero complex number
    # with both real and imaginary parts.
    return 3

def _su2su2_to_tensor_products(U):
    r"""Given a matrix :math:`U = A \otimes B` in SU(2) x SU(2), extract the two SU(2)
    operations A and B.

    This process has been described in detail in the Appendix of Coffey & Deiotte
    https://link.springer.com/article/10.1007/s11128-009-0156-3
    """

    # First, write A = [[a1, a2], [-a2*, a1*]], which we can do for any SU(2) element.
    # Then, A \otimes B = [[a1 B, a2 B], [-a2*B, a1*B]] = [[C1, C2], [C3, C4]]
    # where the Ci are 2x2 matrices.
    C1 = U[0:2, 0:2]
    C2 = U[0:2, 2:4]
    C3 = U[2:4, 0:2]
    C4 = U[2:4, 2:4]

    # From the definition of A \otimes B, C1 C4^\dag = a1^2 I, so we can extract a1
    C14 = np.dot(C1, np.conj(np.transpose(C4)))
    a1 = np.sqrt(C14[0, 0])

    # Similarly, -C2 C3^\dag = a2^2 I, so we can extract a2
    C23 = np.dot(C2, np.conj(np.transpose(C3)))
    a2 = np.sqrt(-C23[0, 0])

    # This gets us a1, a2 up to a sign. To resolve the sign, ensure that
    # C1 C2^dag = a1 a2* I
    C12 = np.dot(C1, np.conj(np.transpose(C2)))

    if not np.allclose(a1 * np.conj(a2), C12[0, 0]):
        a2 *= -1

    # Construct A
    A = np.stack([np.stack([a1, a2]), np.stack([-np.conj(a2), np.conj(a1)])])

    # Next, extract B. Can do from any of the C, just need to be careful in
    # case one of the elements of A is 0.
    if not np.allclose(A[0, 0], 0.0, atol=1e-6):
        B = C1 / A[0, 0]
    else:
        B = C2 / A[0, 1]

    return A, B

def _extract_su2su2_prefactors(U, V):
    r"""This function is used for the case of 2 CNOTs and 3 CNOTs. It does something
    similar as the 1-CNOT case, but there is no special form for one of the
    SO(4) operations.

    Suppose U, V are SU(4) matrices for which there exists A, B, C, D such that
    (A \otimes B) V (C \otimes D) = U. The problem is to find A, B, C, D in SU(2)
    in an analytic and fully differentiable manner.

    This decomposition is possible when U and V are in the same double coset of
    SU(4), meaning there exists G, H in SO(4) s.t. G (Edag V E) H = (Edag U
    E). This is guaranteed here by how V was constructed in both the
    _decomposition_2_cnots and _decomposition_3_cnots methods.

    Then, we can use the fact that E SO(4) Edag gives us something in SU(2) x
    SU(2) to give A, B, C, D.
    """

    # A lot of the work here happens in the magic basis. Essentially, we
    # don't look explicitly at some U = G V H, but rather at
    #     E^\dagger U E = G E^\dagger V E H
    # so that we can recover
    #     U = (E G E^\dagger) V (E H E^\dagger) = (A \otimes B) V (C \otimes D).
    # There is some math in the paper explaining how when we define U in this way,
    # we can simultaneously diagonalize functions of U and V to ensure they are
    # in the same coset and recover the decomposition.
    u = np.dot(Edag, np.dot(U, E))
    v = np.dot(Edag, np.dot(V, E))

    uuT = np.dot(u, np.transpose(u))
    vvT = np.dot(v, np.transpose(v))

    # Get the p and q in SO(4) that diagonalize uuT and vvT respectively (and
    # their eigenvalues). We are looking for a simultaneous diagonalization,
    # which we know exists because of how U and V were constructed. Furthermore,
    # The way we will do this is by noting that, since uuT/vvT are complex and
    # symmetric, so both their real and imaginary parts share a set of
    # real-valued eigenvectors, which are also eigenvectors of uuT/vvT
    # themselves. So we can use eigh, which orders the eigenvectors, and so we
    # are guaranteed that the p and q returned will be "in the same order".
    _, p = np.linalg.eigh(np.real(uuT) + np.imag(uuT))
    _, q = np.linalg.eigh(np.real(vvT) + np.imag(vvT))

    # If determinant of p/q is not 1, it is in O(4) but not SO(4), and has determinant
    # We can transform it to SO(4) by simply negating one of the columns.
    p = np.dot(p, np.diag([1, 1, 1, np.sign(np.linalg.det(p))]))
    q = np.dot(q, np.diag([1, 1, 1, np.sign(np.linalg.det(q))]))

    # Now, we should have p, q in SO(4) such that p^T u u^T p = q^T v v^T q.
    # Then (v^\dag q p^T u)(v^\dag q p^T u)^T = I.
    # So we can set G = p q^T, H = v^\dag q p^T u to obtain G v H = u.
    G = np.dot(p, np.transpose(q))
    H = np.dot(np.conj(np.transpose(v)), np.dot(np.transpose(G), u))

    # These are still in SO(4) though - we want to convert things into SU(2) x SU(2)
    # so use the entangler. Since u = E^\dagger U E and v = E^\dagger V E where U, V
    # are the target matrices, we can reshuffle as in the docstring above,
    #     U = (E G E^\dagger) V (E H E^\dagger) = (A \otimes B) V (C \otimes D)
    # where A, B, C, D are in SU(2) x SU(2).
    AB = np.dot(E, np.dot(G, Edag))
    CD = np.dot(E, np.dot(H, Edag))

    # Now, we just need to extract the constituent tensor products.
    A, B = _su2su2_to_tensor_products(AB)
    C, D = _su2su2_to_tensor_products(CD)

    return A, B, C, D


def _decomposition_2_cnots(U):
    r"""If 2 CNOTs are required, we can write the circuit as
     -╭U- = -A--╭X--RZ(d)--╭X--C-
     -╰U- = -B--╰C--RX(p)--╰C--D-
    We need to find the angles for the Z and X rotations such that the inner
    part has the same spectrum as U, and then we can recover A, B, C, D.
    """
    phases = np.angle(np.diagonal(U))
    diag = np.diag(np.exp(1j * phases))
    U = np.dot(-diag, U)

    # Compute the rotation angles
    u = np.dot(Edag, np.dot(U, E))
    gammaU = np.dot(u, np.transpose(u))

    evs, _ = np.linalg.eig(gammaU)

    # These choices are based on Proposition III.3 of
    # https://arxiv.org/abs/quant-ph/0308045
    # There is, however, a special case where the circuit has the form
    # -╭U- = -A--╭C--╭X--C-
    # -╰U- = -B--╰X--╰C--D-
    #
    # or some variant of this, where the two CNOTs are adjacent.
    #
    # What happens here is that the set of evs is -1, -1, 1, 1 and we can write
    # -╭U- = -A--╭X--SZ--╭X--C-
    # -╰U- = -B--╰C--SX--╰C--D-
    # where SZ and SX are square roots of Z and X respectively. (This
    # decomposition comes from using Hadamards to flip the direction of the
    # first CNOT, and then decomposing them and merging single-qubit gates.) For
    # some reason this case is not handled properly with the full algorithm, so
    # we treat it separately.

    sorted_evs = sorted(np.real(evs))

    wires = QuantumRegister(2)
    qml = QuantumCircuit(wires)

    if np.allclose(sorted_evs, [-1, -1, 1, 1]):
        qml.cx(wires[1], wires[0])
        qml.s(wires[0])
        qml.sx(wires[1])
        qml.cx(wires[1], wires[0])

        # S \otimes SX
        inner_matrix = S_SX
    else:
        # For the non-special case, the eigenvalues come in conjugate pairs.
        # We need to find two non-conjugate eigenvalues to extract the angles.
        x = np.angle(evs[0])
        y = np.angle(evs[1])

        # If it was the conjugate, grab a different eigenvalue.
        if np.allclose(x, -y):
            y = np.angle(evs[2])

        delta = (x + y) / 2
        phi = (x - y) / 2

        qml.cx(wires[1], wires[0])
        qml.rz(delta, wires[0])
        qml.rx(phi, wires[1])
        qml.cx(wires[1], wires[0])

        #inner_reg = QuantumRegister(2)
        #inner_circuit = QuantumCircuit(inner_reg)
        #inner_circuit.rz(delta, inner_reg[0])
        #inner_circuit.rx(phi, inner_reg[1])
        #inner_matrix = qi.Operator(inner_circuit).data
        RZd = RZGate(delta).to_matrix()
        RXp = RXGate(phi).to_matrix()
        inner_matrix = np.kron(RZd, RXp)

    # We need the matrix representation of this interior part, V, in order to
    # decompose U = (A \otimes B) V (C \otimes D)
    V = np.dot(np.dot(CNOT10, np.dot(inner_matrix, CNOT10)), diag)
    #qml = qml.reverse_bits()
    #V = qi.Operator(qml).data

    # Now we find the A, B, C, D in SU(2), and return the decomposition
    A, B, C, D = _extract_su2su2_prefactors(U, V)

    wires2 = QuantumRegister(2)
    qml2 = QuantumCircuit(wires2)

    qml2.unitary(C, wires2[1])
    qml2.unitary(D, wires2[0])
    qml2.append(qml, wires2[::-1])
    qml2.unitary(A, wires2[1])
    qml2.unitary(B, wires2[0])

    return qml2
    #return C_ops + D_ops + interior_decomp + A_ops + B_ops

def _decomposition_3_cnots(U):
    r"""The most general form of this decomposition is U = (A \otimes B) V (C \otimes D),
    where V is as depicted in the circuit below:
     -╭U- = -C--╭X--RZ(d)--╭C---------╭X--A-
     -╰U- = -D--╰C--RY(b)--╰X--RY(a)--╰C--B-
    """

    # First we add a SWAP as per v1 of arXiv:0308033, which helps with some
    # rearranging of gates in the decomposition (it will cancel out the fact
    # that we need to add a SWAP to fix the determinant in another part later).
    swap_U = np.exp(1j * np.pi / 4) * np.dot(SWAP, U)

    # Choose the rotation angles of RZ, RY in the two-qubit decomposition.
    # They are chosen as per Proposition V.1 in quant-ph/0308033 and are based
    # on the phases of the eigenvalues of :math:`E^\dagger \gamma(U) E`, where
    #    \gamma(U) = (E^\dag U E) (E^\dag U E)^T.
    # The rotation angles can be computed as follows (any three eigenvalues can be used)
    u = np.dot(Edag, np.dot(swap_U, E))
    gammaU = np.dot(u, np.transpose(u))
    evs, _ = np.linalg.eig(gammaU)

    # We will sort the angles so that results are consistent across interfaces.
    angles = np.sort([np.angle(ev) for ev in evs])

    x, y, z = angles[0], angles[1], angles[2]

    # Compute functions of the eigenvalues; there are different options in v1
    # vs. v3 of the paper, I'm not entirely sure why. This is the version from v3.
    alpha = (x + y) / 2
    beta = (x + z) / 2
    delta = (z + y) / 2

    wires = QuantumRegister(2)
    qml = QuantumCircuit(wires)

    # This is the interior portion of the decomposition circuit
    qml.cx(wires[1], wires[0])
    qml.rz(delta, wires[0])
    qml.ry(beta, wires[1])
    qml.cx(wires[0], wires[1])
    qml.ry(alpha, wires[1])
    qml.cx(wires[1], wires[0])

    # We need the matrix representation of this interior part, V, in order to
    # decompose U = (A \otimes B) V (C \otimes D)
    #
    # Looking at the decomposition above, V has determinant -1 (because there
    # are 3 CNOTs, each with determinant -1). The relationship between U and V
    # requires that both are in SU(4), so we add a SWAP after to V. We will see
    # how this gets fixed later.
    #
    # -╭V- = -╭X--RZ(d)--╭C---------╭X--╭SWAP-
    # -╰V- = -╰C--RY(b)--╰X--RY(a)--╰C--╰SWAP-

    RZd = RZGate(delta).to_matrix()
    RYb = RYGate(beta).to_matrix()
    RYa = RYGate(alpha).to_matrix()

    V_mats = [CNOT10, np.kron(RZd, RYb), CNOT01, np.kron(np.eye(2), RYa), CNOT10, SWAP]

    V = np.eye(4)

    for mat in V_mats:
        V = np.dot(mat, V)

    # Now we need to find the four SU(2) operations A, B, C, D
    A, B, C, D = _extract_su2su2_prefactors(swap_U, V)
    #print(A@np.conj(A.T), B@np.conj(B.T), C@np.conj(C.T), D@np.conj(D.T))
    # At this point, we have the following:
    # -╭U-╭SWAP- = --C--╭X-RZ(d)-╭C-------╭X-╭SWAP--A
    # -╰U-╰SWAP- = --D--╰C-RZ(b)-╰X-RY(a)-╰C-╰SWAP--B
    #
    # Using the relationship that SWAP(A \otimes B) SWAP = B \otimes A,
    # -╭U-╭SWAP- = --C--╭X-RZ(d)-╭C-------╭X--B--╭SWAP-
    # -╰U-╰SWAP- = --D--╰C-RZ(b)-╰X-RY(a)-╰C--A--╰SWAP-
    #
    # Now the SWAPs cancel, giving us the desired decomposition
    # (up to a global phase).
    # -╭U- = --C--╭X-RZ(d)-╭C-------╭X--B--
    # -╰U- = --D--╰C-RZ(b)-╰X-RY(a)-╰C--A--

    wires2 = QuantumRegister(2)
    qml2 = QuantumCircuit(wires2)

    qml2.unitary(C, wires2[1])
    qml2.unitary(D, wires2[0])
    qml2.append(qml, wires2[::-1])
    qml2.unitary(A, wires2[0])
    qml2.unitary(B, wires2[1])

    qml2.global_phase -= np.pi/4

    # Return the full decomposition
    return qml2
