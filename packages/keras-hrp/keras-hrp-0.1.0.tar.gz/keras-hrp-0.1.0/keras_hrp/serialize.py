import numpy as np
from typing import List


def bool_to_int8(hashvalues: List[bool]) -> List[np.int8]:
    return np.packbits(
        hashvalues.reshape(-1, 8),
        bitorder='big').astype(np.int8)


def int8_to_bool(serialized: List[np.int8]) -> List[bool]:
    return np.unpackbits(
        serialized.astype(np.uint8),
        bitorder='big').reshape(-1)
