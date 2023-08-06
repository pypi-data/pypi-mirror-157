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
The backend provided by QCompute on Quantum Leaf.
"""

import QCompute

__all__ = [
    "DEFAULT_BACKEND",
    "DEFAULT_TOKEN",
    "set_qcompute_default_backend",
    "get_qcompute_default_backend",
    "set_qcompute_default_token",
    "get_qcompute_default_token",
    "run_circuit"
]


DEFAULT_BACKEND = 'local_baidu_sim2'
DEFAULT_TOKEN = None
QCompute.Define.Settings.outputInfo = False
QCompute.Define.Settings.drawCircuitControl = []


def set_qcompute_default_backend(backend: str) -> None:
    r"""Set the default backend for QCompute.

    Args:
        backend (str): the backend to set
    """
    assert isinstance(backend, str), "Should input the name of the backend in string."
    global DEFAULT_BACKEND
    DEFAULT_BACKEND = backend


def get_qcompute_default_backend() -> str:
    r"""Get the default backend of QCompute.

    Returns:
        str: current backend of QCompute
    """
    return DEFAULT_BACKEND


def set_qcompute_default_token(token: str) -> None:
    r"""Set the default token for QCompute backend.

    Warning:
        A valid token is required to use the QCompute cloud server. Please refer to the
        `website <https://quantum-hub.baidu.com/>`__ to get a valid token.

    Args:
        token (str): your token for QCompute backend
    """
    global DEFAULT_TOKEN
    DEFAULT_TOKEN = token


def get_qcompute_default_token() -> str:
    r"""Get the token you set.

    Returns:
        str: the current default token of QCompute
    """
    return DEFAULT_TOKEN


def run_circuit(circuit: "Circuit", shots: int, backend=None) -> dict:
    r"""Run a quantum circuit by QCompute backends.

    Warning:
        Note that the labels of returning result is reversed from QCompute. That is, if the counting result
        from QCompute is given by ``{'01': 5, '00': 3}``, then our return gives ``{'10': 5, '00': 3}``.

    Args:
        circuit (Circuit): quantum circuit to run
        shots (int): number of sampling
        backend (Enum): specific QCompute backend

    Raises:
        NotImplementedError: Some quantum gates are not supported in QCompute yet.

    Returns:
        dict: circuit sampling results
    """
    single_qubit_gates = {
        's': QCompute.S, 't': QCompute.T,
        'h': QCompute.H, 'x': QCompute.X, 'y': QCompute.Y, 'z': QCompute.Z,
        'u3': QCompute.U, 'rx': QCompute.RX, 'ry': QCompute.RY, 'rz': QCompute.RZ,
        'm': QCompute.MeasureZ
    }

    multi_qubits_gates = {
        'cnot': QCompute.CX, 'cz': QCompute.CZ, 'swap': QCompute.SWAP
    }

    QCompute.Define.hubToken = get_qcompute_default_token()
    qcompute_env = QCompute.QEnv()

    backend = QCompute.BackendName(get_qcompute_default_backend()) if backend is None else backend.value
    if backend != QCompute.BackendName.LocalBaiduSim2:
        assert get_qcompute_default_token() is not None, \
            "A valid QCompute token is required to use the cloud backend. " \
            "Please set a QCompute token by calling `set_qcompute_default_token`."
    qcompute_env.backend(backendName=backend)

    for gate in circuit.gate_history:
        name = gate['name']
        which_qubit = gate['which_qubit']
        params = gate['params']

        if name in single_qubit_gates:
            gate_func = single_qubit_gates[name]
            if name in ['s', 't', 'h', 'x', 'y', 'z']:
                gate_func(qcompute_env.Q[which_qubit[0]])
            elif name in ['rx', 'ry', 'rz']:
                gate_func(params)(qcompute_env.Q[which_qubit[0]])
            elif name in ['u3']:
                gate_func(*params)(qcompute_env.Q[which_qubit[0]])
            elif name in ['m']:
                gate_func([qcompute_env.Q[which_qubit[0]]], [which_qubit[0]])
        elif name in multi_qubits_gates:
            gate_func = multi_qubits_gates[name]
            if name in ['cnot', 'cz', 'swap']:
                gate_func(qcompute_env.Q[which_qubit[0]], qcompute_env.Q[which_qubit[1]])
        else:
            raise NotImplementedError

    results = qcompute_env.commit(shots, fetchMeasure=True)
    if results['status'] == 'success':
        origin_counts = results['counts']
        counts = {}
        for key in origin_counts:
            key_reverse = key[::-1]  # reverse the bit string
            counts[key_reverse] = origin_counts[key]

        return counts

    else:
        raise InterruptedError("QCompute running fails.")
