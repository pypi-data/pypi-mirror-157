import keras_hrp as khrp
import numpy as np


def test_1():
    hashemb = np.array([
        [1, 0, 1, 0, 1, 1, 0, 0],
        [1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 1]
    ])
    simis = khrp.hammingsim_list(hashemb)
    assert simis == [0.875, 0.625, 0.75]


def test_2():
    hashemb = np.array([
        [1, 0, 1, 0, 1, 1, 0, 0],
        [1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1]
    ])
    mat = khrp.hammingsim_matrix(hashemb)
    assert (np.diag(mat) == 1).all()
    np.testing.assert_array_equal(
        np.tril(mat, k=-1).T,
        np.triu(mat, k=1)
    )


def test_3():
    fltemb = np.array([
        [.1, 0, .1, 0, .1, .1, 0, 0],
        [.1, 0, .1, 0, .1, .1, 0, .1],
        [.1, 0, .1, 0, .1, 0, .1, .1]
    ])
    simis = khrp.cossim_list(fltemb)
    np.testing.assert_array_equal(
        simis, [0.8944271909999159, 0.6708203932499369, 0.8])
