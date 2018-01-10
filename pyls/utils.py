# -*- coding: utf-8 -*-

import numpy as np


def xcorr(X, Y, grouping=None):
    """
    Calculates the cross-covariance matrix of ``X`` and ``Y``

    Parameters
    ----------
    X : (N x J) array_like
    Y : (N x K) array_like
    grouping : (N,) array_like, optional
        Grouping array, where ``len(np.unique(grouping))`` is the number of
        distinct groups in ``X`` and ``Y``. Cross-covariance matrices are
        computed separately for each group and are stacked row-wise.

    Returns
    -------
    (K[*G] x J) np.ndarray
        Cross-covariance of ``X`` and ``Y``
    """

    if grouping is None:
        return _compute_xcorr(X, Y)
    else:
        return np.row_stack([_compute_xcorr(X[grouping == grp],
                                            Y[grouping == grp])
                             for grp in np.unique(grouping)])


def _compute_xcorr(X, Y):
    """
    Calculates the cross-covariance matrix of ``X`` and ``Y``

    Parameters
    ----------
    X : (N x J) array_like
    Y : (N x K) array_like

    Returns
    -------
    xprod : (K x J) np.ndarray
        Cross-covariance of ``X`` and ``Y``
    """

    Xnz, Ynz = normalize(zscore(X)), normalize(zscore(Y))
    xprod = (Ynz.T @ Xnz) / (Xnz.shape[0] - 1)

    return xprod


def zscore(X):
    """
    Z-scores ``X`` by subtracting mean and dividing by standard deviation

    Effectively the same as ``np.nan_to_num(scipy.stats.zscore(X))`` but
    handles DivideByZero without issuing annoying warnings.

    Parameters
    ----------
    X : (N x J) array_like

    Returns
    -------
    zarr : (N x J) np.ndarray
        Z-scored ``X``
    """

    arr = np.array(X)

    avg, stdev = arr.mean(axis=0), arr.std(axis=0)
    zero_items = np.where(stdev == 0)[0]

    if zero_items.size > 0:
        avg[zero_items], stdev[zero_items] = 0, 1

    zarr = (arr - avg) / stdev
    zarr[:, zero_items] = 0

    return zarr


def normalize(X, axis=0):
    """
    Normalizes ``X`` along ``axis``

    Utilizes Frobenius norm (or Hilbert-Schmidt norm, L_{p,q} norm where p=q=2)

    Parameters
    ----------
    X : (N x K) array_like
        Data to be normalized
    axis : int, optional
        Axis for normalization. Default: 0

    Returns
    -------
    normed : (N x K) np.ndarray
        Normalized ``X``
    """

    normed = np.array(X)
    normal_base = np.linalg.norm(normed, axis=axis, keepdims=True)

    # avoid DivideByZero errors
    zero_items = np.where(normal_base == 0)
    normal_base[zero_items] = 1
    # normalize and re-set zero_items to 0
    normed = normed / normal_base
    normed[zero_items] = 0

    return normed


def get_seed(seed=None):
    """
    Determines type of ``seed`` and returns RandomState instance

    Parameters
    ----------
    seed : {int, RandomState instance, None}, optional
        The seed of the pseudo random number generator to use when shuffling
        the data.  If int, ``seed`` is the seed used by the random number
        generator. If RandomState instance, ``seed`` is the random number
        generator. If None, the random number generator is the RandomState
        instance used by ``np.random``. Default: None

    Returns
    -------
    RandomState instance
    """

    if seed is not None:
        if isinstance(seed, int):
            return np.random.RandomState(seed)
        elif isinstance(seed, np.random.RandomState):
            return seed
    return np.random


def dummy_code(grouping):
    """
    Dummy codes ``grouping``

    Parameters
    ----------
    grouping : (N,) array_like
        Array with labels separating ``N`` subjects into ``G`` groups

    Returns
    -------
    Y : (N x G) np.ndarray
        Dummy coded grouping array
    """

    groups = np.unique(grouping)
    Y = np.column_stack([(grouping == grp).astype(int) for grp in groups])

    return Y


def reverse_dummy_code(Y):
    """
    Reverse engineers input of ``dummy_code()`` from outputs

    Parameters
    ----------
    Y : (N x G) array_like
        Dummy coded grouping array

    Returns
    -------
    grouping : (N,) array_like
        Array with labels separating ``N`` subjects into ``G`` groups
    """

    grouping = np.row_stack([grp * n for n, grp in enumerate(Y.T, 1)]).sum(0)

    return grouping
