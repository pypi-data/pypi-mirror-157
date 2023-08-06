import keras_hrp as khrp
import numpy as np


def test_1():
    hashvalues = np.array([1, 0, 1, 0, 1, 1, 0, 0])
    serialized = khrp.bool_to_int8(hashvalues)
    deserialized = khrp.int8_to_bool(serialized)
    np.testing.assert_array_equal(deserialized, hashvalues)
