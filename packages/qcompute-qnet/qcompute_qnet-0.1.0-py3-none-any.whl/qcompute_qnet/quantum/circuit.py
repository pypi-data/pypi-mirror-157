#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Baidu, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r"""
Module for quantum circuits.
"""

from argparse import ArgumentTypeError
from enum import Enum
from typing import List, Union
import pandas as pd
from qcompute_qnet.quantum.backends import qcompute, Backend, mbqc

__all__ = [
    "Circuit"
]


class Circuit:
    r"""Class for creating a quantum circuit.

    Warning:
        The current version only supports gates in [H, X, Y, Z, S, T, Rx, Ry, Rz, U3, CNOT, CZ, SWAP].

    Attributes:
        _width (int): circuit width
        _history (List[dict]): history of quantum gates
    """

    def __init__(self, width: int):
        r"""Constructor for Circuit class.

        Args:
            width (int): circuit width
        """
        assert isinstance(width, int), f"Circuit width should be a int value."

        self._history = []
        self.__measured_qubits = []
        self._width = width

    def __add_single_qubit_gate(self, name: str, which_qubit: int, params=None) -> None:
        r"""Add a single qubit gate to the circuit list.

        Args:
            name (str): single qubit gate name
            which_qubit (int): qubit index
            params (any): gate parameters
        """
        assert isinstance(which_qubit, int), f"'which_qubit' should be a int value."
        assert 0 <= which_qubit < self._width, f"Invalid qubit index: {which_qubit}!\n" \
                                               "Qubit index must be smaller than the circuit width."
        assert which_qubit not in self.__measured_qubits, f"Invalid qubit index: {which_qubit}!\n" \
                                                          "This qubit has already been measured."

        gate = {"name": name, "which_qubit": [which_qubit], "params": params}
        self._history.append(gate)

    def __add_double_qubit_gate(self, name: str, which_qubit: List[int], params=None) -> None:
        r"""Add a double qubit gate to the circuit list.

        Args:
            name (str): double qubit gate name
            which_qubit (list): qubit indices in the order of [control, target]
            params (any): gate parameters
        """
        ctrl = which_qubit[0]
        targ = which_qubit[1]

        assert isinstance(ctrl, int), f"Invalid qubit index {ctrl} with the type: `{type(ctrl)}`!\n"\
                                      "Only 'int' is supported as the type of qubit index."
        assert 0 <= ctrl < self._width, f"Invalid qubit index: {ctrl}!\n"\
                                        "Qubit index must be smaller than the circuit width."
        if ctrl in self.__measured_qubits:
            raise TypeError(f"Invalid qubit index: {ctrl}! This qubit has already been measured.")

        assert isinstance(targ, int), f"Invalid qubit index {targ} with the type: `{type(targ)}`!\n"\
                                      "Only 'int' is supported as the type of qubit index."
        assert 0 <= targ < self._width, f"Invalid qubit index: {targ}!\n"\
                                        "Qubit index must be smaller than the circuit width."
        if targ in self.__measured_qubits:
            raise TypeError(f"Invalid qubit index: {targ}! This qubit has already been measured.")

        if ctrl == targ:
            raise TypeError(f"Invalid qubit indices: {ctrl} and {targ}!\n"
                            "Control qubit must not be the same as target qubit.")

        gate = {"name": name, "which_qubit": which_qubit, "params": params}
        self._history.append(gate)

    def h(self, which_qubit: int) -> None:
        r"""Add a Hadamard gate.

        The matrix form is:

        .. math::

            \frac{1}{\sqrt{2}} \begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix}

        Args:
            which_qubit (int): qubit index
        """
        self.__add_single_qubit_gate('h', which_qubit)

    def x(self, which_qubit: int) -> None:
        r"""Add a Pauli-X gate.

        The matrix form is:

        .. math::

            \begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}

        Args:
            which_qubit (int): qubit index
        """
        self.__add_single_qubit_gate('x', which_qubit)

    def y(self, which_qubit: int) -> None:
        r"""Add a Pauli-Y gate.

        The matrix form is:

        .. math::

            \begin{bmatrix} 0 & -i \\ i & 0 \end{bmatrix}

        Args:
            which_qubit (int): qubit index
        """
        self.__add_single_qubit_gate('y', which_qubit)

    def z(self, which_qubit: int) -> None:
        r"""Add a Pauli-Z gate.

        The matrix form is:

        .. math::

            \begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}

        Args:
            which_qubit (int): qubit index
        """
        self.__add_single_qubit_gate('z', which_qubit)

    def s(self, which_qubit: int) -> None:
        r"""Add a S gate.

        The matrix form is:

        .. math::

            \begin{bmatrix} 1 & 0 \\ 0 & i \end{bmatrix}

        Args:
            which_qubit (int): qubit index
        """
        self.__add_single_qubit_gate('s', which_qubit)

    def t(self, which_qubit: int) -> None:
        r"""Add a T gate.

        The matrix form is:

        .. math::

            \begin{bmatrix} 1 & 0 \\ 0 & e^{i \pi / 4} \end{bmatrix}

        Args:
            which_qubit (int): qubit index
        """
        self.__add_single_qubit_gate('t', which_qubit)

    def rx(self, theta: Union[float, int], which_qubit: int) -> None:
        r"""Add a rotation gate around x-axis.

        The matrix form is:

        .. math::

            \begin{bmatrix}
            \cos\frac{\theta}{2} & -i\sin\frac{\theta}{2} \\
            -i\sin\frac{\theta}{2} & \cos\frac{\theta}{2}
            \end{bmatrix}

        Args:
            theta (Union[float, int]): rotation angle
            which_qubit (int): qubit index
        """
        assert isinstance(theta, float) or isinstance(theta, int),\
            f"Invalid rotation angle ({theta}) with the type: `{type(theta)}`!\n"\
            "Only `float` and `int` are supported as the type of rotation angle."

        self.__add_single_qubit_gate('rx', which_qubit, theta)

    def ry(self, theta: Union[float, int], which_qubit: int) -> None:
        r"""Add a rotation gate around y-axis.

        The matrix form is:

        .. math::

            \begin{bmatrix}
            \cos\frac{\theta}{2} & -\sin\frac{\theta}{2} \\
            \sin\frac{\theta}{2} & \cos\frac{\theta}{2}
            \end{bmatrix}

        Args:
            theta (Union[float, int]): rotation angle
            which_qubit (int): qubit index
        """
        assert isinstance(theta, float) or isinstance(theta, int), \
            f"Invalid rotation angle ({theta}) with the type: `{type(theta)}`!\n" \
            "Only `float` and `int` are supported as the type of rotation angle."

        self.__add_single_qubit_gate('ry', which_qubit, theta)

    def rz(self, theta: Union[float, int], which_qubit: int) -> None:
        r"""Add a rotation gate around z axis.

        The matrix form is:

        .. math::

            \begin{bmatrix}
            e^{-i\frac{\theta}{2}} & 0 \\
            0 & e^{i\frac{\theta}{2}}
            \end{bmatrix}

        Args:
            theta (Union[float, int]): rotation angle
            which_qubit (int): qubit index
        """
        assert isinstance(theta, float) or isinstance(theta, int), \
            f"Invalid rotation angle ({theta}) with the type: `{type(theta)}`!\n" \
            "Only `float` and `int` are supported as the type of rotation angle."

        self.__add_single_qubit_gate('rz', which_qubit, theta)

    def u3(self, theta: Union[float, int], phi: Union[float, int], gamma: Union[float, int], which_qubit: int) -> None:
        r"""Add a single qubit unitary gate.

        It has a decomposition form:

        .. math::

            \begin{align}
            U3(\theta, \phi, \gamma) = Rz(\varphi) Rx(\theta) Rz(\gamma) =
                \begin{bmatrix}
                    \cos\frac\theta2&-e^{i\gamma}\sin\frac\theta2\\
                    e^{i\phi}\sin\frac\theta2&e^{i(\phi+\gamma)}\cos\frac\theta2
                \end{bmatrix}
            \end{align}

        Warnings:
            Please be aware of the order of the rotation angles.

        Args:
            theta (Union[float, int]): the rotation angle of the Rx gate
            phi (Union[float, int]): the rotation angle of the left Rz gate
            gamma (Union[float, int]): the rotation angle of the right Rz gate
            which_qubit (int): qubit index
       """
        params = [theta, phi, gamma]
        self.__add_single_qubit_gate('u3', which_qubit, params)

    def cnot(self, which_qubit: List[int]) -> None:
        r"""Add a Controlled-NOT gate.

        Let ``which_qubit`` be ``[0, 1]``, the matrix form is:

        .. math::

            \begin{align}
                \begin{bmatrix}
                1 & 0 & 0 & 0 \\
                0 & 1 & 0 & 0 \\
                0 & 0 & 0 & 1 \\
                0 & 0 & 1 & 0
                \end{bmatrix}
            \end{align}

        Args:
            which_qubit (list): a list of qubit indices in the order of [control, target]
        """
        self.__add_double_qubit_gate('cnot', which_qubit)

    def cnot15(self, which_qubit: List[int]) -> None:
        r"""Add a Controlled-NOT gate whose measurement pattern has 15 qubits.

        Let ``which_qubit`` be ``[0, 1]``, the matrix form is:

        .. math::

            \begin{align}
                \begin{bmatrix}
                1 & 0 & 0 & 0 \\
                0 & 1 & 0 & 0 \\
                0 & 0 & 0 & 1 \\
                0 & 0 & 1 & 0
                \end{bmatrix}
            \end{align}

        Args:
            which_qubit (list): a list of qubit indices in the order of [control, target]
        """
        self.__add_double_qubit_gate('cnot15', which_qubit)

    def cz(self, which_qubit: List[int]) -> None:
        r"""Add a Controlled-Z gate.

        Let ``which_qubit`` be ``[0, 1]``, the matrix form is:

        .. math::

            \begin{align}
                \begin{bmatrix}
                1 & 0 & 0 & 0 \\
                0 & 1 & 0 & 0 \\
                0 & 0 & 1 & 0 \\
                0 & 0 & 0 & -1
                \end{bmatrix}
            \end{align}

        Args:
            which_qubit (list): a list of qubit indices in the order of [control, target]
        """
        self.__add_double_qubit_gate('cz', which_qubit)

    def swap(self, which_qubit: List[int]) -> None:
        r"""Add a SWAP gate.

        Let ``which_qubit`` be ``[0, 1]``, the matrix form is:

        .. math::

            \begin{align}
                \begin{bmatrix}
                    1 & 0 & 0 & 0 \\
                    0 & 0 & 1 & 0 \\
                    0 & 1 & 0 & 0 \\
                    0 & 0 & 0 & 1
                \end{bmatrix}
            \end{align}

        Args:
            which_qubit (list): qubits to swap
        """
        # self.__add_double_qubit_gate('swap', which_qubit)
        self.__add_double_qubit_gate('cnot', which_qubit)
        self.__add_double_qubit_gate('cnot', [which_qubit[1], which_qubit[0]])
        self.__add_double_qubit_gate('cnot', which_qubit)

    def measure(self, which_qubit=None) -> None:
        r"""Measure a quantum state in the computational basis.

        Measure all the qubits if no specific qubit index is given.

        Args:
            which_qubit (int): qubit index
        """
        assert which_qubit is None or isinstance(which_qubit, int), \
            f"Input {which_qubit} should be an int value."

        if which_qubit is None:
            for idx in range(self._width):
                self.__add_single_qubit_gate('m', idx, [0, 'YZ', [], []])  # Z measurement
                self.__measured_qubits.append(idx)

        else:
            self.__add_single_qubit_gate('m', which_qubit, [0, 'YZ', [], []])  # Z measurement
            self.__measured_qubits.append(which_qubit)

    def run(self, shots: int, backend: Enum) -> dict:
        r"""Run the quantum circuit with a given backend.

        Args:
            shots (int): the number of sampling
            backend (Enum): backend to run the quantum circuit

        Returns:
            dict: circuit sampling results
        """
        if not hasattr(backend, 'name'):
            raise ArgumentTypeError(f"{backend} has no attribute 'name'. "
                                    f"Please assign a specific backend for {backend}.")

        if backend.name in Backend.QCompute.__members__:
            results = qcompute.run_circuit(self, shots=shots, backend=backend)
        elif backend.name in Backend.MBQC.__members__:
            results = mbqc.run_circuit(self, shots=shots)
        else:
            raise ArgumentTypeError(f"Cannot find the backend {backend}")

        return results

    def is_valid(self) -> bool:
        r"""Check the validity of a quantum circuit.

        Warnings:
            We restrict that there is at least one quantum gate acting on each qubit of the circuit.

        Returns:
            bool: validity of the quantum circuit
        """
        all_qubits = []
        for gate in self._history:
            if gate["name"] != 'm':
                all_qubits += gate["which_qubit"]
        effective_qubits = list(set(all_qubits))

        return self._width == len(effective_qubits)

    @property
    def width(self) -> int:
        r"""Return the quantum circuit width.

        Returns:
           int: circuit width
        """
        return self._width

    @property
    def gate_history(self) -> List[dict]:
        r"""Return the gate history of the quantum circuit.

        Returns:
            List[dict]: a list of quantum gates
        """
        return self._history

    @property
    def measured_qubits(self):
        r"""Return indices of measurement qubits in the circuit.

        Returns:
            list: a list of indices of measured qubits in the circuit
        """
        return self.__measured_qubits

    def print(self) -> None:
        r"""Print the quantum circuit list.
        """
        df = pd.DataFrame(columns=["name", "which_qubit", "params"])
        for i, gate in enumerate(self._history):
            circuit_info = pd.DataFrame({"name": gate['name'],
                                         "which_qubit": str(gate['which_qubit']),
                                         "params": str(gate['params'])}, index=[f"Gate {i + 1}"])
            df = pd.concat([df, circuit_info])

        print(f"\nCircuit details:\n{df.to_string()}")
