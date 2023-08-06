import random
from typing import Tuple, Union

import numpy as np
from numpy import linalg


def cosine_similarity(a: np.array, targets: np.array) -> np.array:
    """Calculate query cosine similarity with targets."""

    cos_sim = np.dot(targets, a) / (linalg.norm(targets, axis=1) * linalg.norm(a))
    return cos_sim


def multiply_one_or_minus_one(x: float) -> float:
    return (1 if random.choice([True, False]) is True else -1) * x


def random_array(dims: Union[int, Tuple], use_negative: bool = True):
    """Get random array."""

    if isinstance(dims, int):
        dims = (dims, )

    arr = np.random.rand(*dims)
    if use_negative is True:
        arr = np.vectorize(multiply_one_or_minus_one)(arr)
    return arr

