__version__ = '0.1.0'

from .hrp import (
    HashedRandomProjection
)
from .serialize import (
    bool_to_int8,
    int8_to_bool
)
from .distance import (
    cossim_list,
    hammingsim_list,
    hammingsim_matrix
)
