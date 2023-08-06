import numpy as np
import numba
import scipy.spatial.distance
from typing import List


@numba.jit
def hammingsim_two(v1: List[bool], v2: List[bool], sz: int) -> float:
    """ Matching coefficient """
    return (v1 == v2).sum() / sz


@numba.jit
def hammingsim_matrix(x: List[List[bool]]) -> List[List[float]]:
    """ Matching coefficient between two boolean vectors as matrix """
    n, sz = x.shape
    s = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            if i < j:
                s[i, j] = hammingsim_two(x[i], x[j], sz)
                s[j, i] = s[i, j]
    return s


@numba.jit
def hammingsim_list(x: List[List[bool]]) -> List[float]:
    """ Matching coefficient between two boolean vectors as list """
    n, sz = x.shape
    s = []
    for i in range(n):
        for j in range(n):
            if i < j:
                s.append(hammingsim_two(x[i], x[j], sz))
    return s


def cossim_list(x: List[List[float]]) -> List[float]:
    """ Cosine Similarities as lists

    Notes:
    ------
    Use `sbert.util.cos_sim(x, x)` to return a matrix.
    """
    n, sz = x.shape
    s = []
    for i in range(n):
        for j in range(n):
            if i < j:
                s.append(1. - scipy.spatial.distance.cosine(x[i], x[j]))
    return s
