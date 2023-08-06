"""
This contains the differentiation methods used to estimate the velocity
of a trajectory.
"""

import enum
from typing import Optional

import numpy as np

from yupi.vector import Vector


class DiffMethod(enum.Enum):
    """Enum to define the method to calculate the velocity."""

    LINEAR_DIFF = enum.auto()
    FORNBERG_DIFF = enum.auto()


class WindowType(enum.Enum):
    """Enum to define the type of window to use."""

    FORWARD = enum.auto()
    BACKWARD = enum.auto()
    CENTRAL = enum.auto()


def _get_coeff(x_0: float, a: np.ndarray, coeff_arr: Optional[np.ndarray] = None):
    # pylint: disable=invalid-name
    # The variables where named as in the original algorithm.

    N = len(a)
    M = 2  # Fixed to the second derivative.

    if coeff_arr is None:
        coeff_arr = np.zeros((M, N, N))

    coeff_arr[0, 0, 0] = 1
    c1 = 1
    for n in range(1, N):
        c2 = 1
        for v in range(n):
            c3 = a[n] - a[v]
            c2 = c2 * c3
            if n < M:
                coeff_arr[n, n - 1, v] = 0
            for m in range(min(n + 1, M)):
                d_1 = coeff_arr[m, n - 1, v]
                d_2 = coeff_arr[m - 1, n - 1, v] if m != 0 else 0
                coeff_arr[m, n, v] = ((a[n] - x_0) * d_1 - m * d_2) / c3
        for m in range(min(n + 1, M)):
            d_1 = coeff_arr[m - 1, n - 1, n - 1] if m != 0 else 0
            d_2 = coeff_arr[m, n - 1, n - 1]
            coeff_arr[m, n, n] = (c1 / c2) * (m * d_1 - (a[n - 1] - x_0) * d_2)
        c1 = c2

    return coeff_arr


def _validate_traj(traj, method, window_type, accuracy):
    length = len(traj)
    if method == DiffMethod.LINEAR_DIFF:
        return length >= 3 if window_type == WindowType.CENTRAL else length >= 2
    if method == DiffMethod.FORNBERG_DIFF:
        return length >= accuracy + 1
    raise ValueError("Invalid method to estimate the velocity.")


def _linear_diff(traj, window_type):
    vel = np.zeros_like(traj.r)
    if window_type == WindowType.FORWARD:
        diff = ((traj.r[1:] - traj.r[:-1]).T / (traj.t[1:] - traj.t[:-1])).T
        vel[:-1] = diff
        vel[-1] = diff[-1]
    elif window_type == WindowType.BACKWARD:
        diff = ((traj.r[1:] - traj.r[:-1]).T / (traj.t[1:] - traj.t[:-1])).T
        vel[1:] = diff
        vel[0] = diff[0]
    elif window_type == WindowType.CENTRAL:
        diff = ((traj.r[2:] - traj.r[:-2]).T / (traj.t[2:] - traj.t[:-2])).T
        vel[1:-1] = diff
        vel[0] = diff[0]
        vel[-1] = diff[-1]
    else:
        raise ValueError("Invalid window type to estimate the velocity.")
    return Vector(vel)


def _fornberg_diff_forward(traj, n):  # pylint: disable=invalid-name
    vel = np.zeros_like(traj.r)
    _coeff = None
    a_len = n + 1
    for i in range(len(traj.r)):
        alpha = traj.t[i : i + a_len] if i < len(traj.r) - a_len else traj.t[-a_len:]
        _y = traj.r[i : i + a_len] if i < len(traj.r) - a_len else traj.r[-a_len:]
        _coeff = _get_coeff(traj.t[i], alpha, _coeff)
        vel[i] = np.sum(_coeff[1, n, :] * _y.T, axis=1)
    return Vector(vel)


def _fornberg_diff_backward(traj, n):  # pylint: disable=invalid-name
    vel = np.zeros_like(traj.r)
    _coeff = None
    a_len = n + 1
    for i in range(len(traj.r)):
        alpha = traj.t[i - a_len : i] if i >= a_len else traj.t[:a_len]
        _y = traj.r[i - a_len : i] if i >= a_len else traj.r[:a_len]
        _coeff = _get_coeff(traj.t[i], alpha, _coeff)
        vel[i] = np.sum(_coeff[1, n, :] * _y.T, axis=1)
    return Vector(vel)


def _fornberg_diff_central(traj, n):  # pylint: disable=invalid-name
    vel = np.zeros_like(traj.r)
    _coeff = None
    a_len = n + 1
    midd = n // 2
    for i in range(len(traj.r)):
        if midd <= i < len(traj.r) - midd:
            alpha = traj.t[i - midd : i + midd + 1]
            _y = traj.r[i - midd : i + midd + 1]
        elif i < midd:
            alpha = traj.t[:a_len]
            _y = traj.r[:a_len]
        else:
            alpha = traj.t[-a_len:]
            _y = traj.r[-a_len:]
        _coeff = _get_coeff(traj.t[i], alpha, _coeff)
        vel[i] = np.sum(_coeff[1, n, :] * _y.T, axis=1)
    return Vector(vel)


def estimate_velocity(
    traj,
    method: DiffMethod,
    window_type: WindowType = WindowType.CENTRAL,
    accuracy: int = 1,
) -> Vector:
    """
    Estimate the velocity of a trajectory.

    Parameters
    ----------
    traj : Trajectory
        Trajectory to estimate the velocity.
    method : VelocityMethod
        Method to use to estimate the velocity.
    window_type : WindowType
        Type of window to use.
    accuracy : int
        Accuracy of the estimation (only used if method is FORNBERG_DIFF).

    Returns
    -------
    Vector
        Estimated velocity.

    Raises
    ------
    ValueError
        If the trajectory is too short to estimate the velocity.
    """
    if not _validate_traj(traj, method, window_type, accuracy):
        raise ValueError("Trajectory is too short to estimate the velocity.")

    if method == DiffMethod.LINEAR_DIFF:
        return _linear_diff(traj, window_type)
    if method == DiffMethod.FORNBERG_DIFF:
        if window_type == WindowType.FORWARD:
            return _fornberg_diff_forward(traj, accuracy)
        if window_type == WindowType.BACKWARD:
            return _fornberg_diff_backward(traj, accuracy)
        if window_type == WindowType.CENTRAL:
            if accuracy % 2 != 0:
                raise ValueError(
                    "The accuracy must be an EVEN integer for"
                    " central window type in FORNBERG_DIFF method."
                )
            return _fornberg_diff_central(traj, accuracy)
        raise ValueError("Invalid window type to estimate the velocity.")
    raise ValueError("Invalid method to estimate the velocity.")
