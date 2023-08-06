import itertools
from typing import Iterable


def batch_chunks(items: Iterable, batch_size: int = 10):
    """Batch items helper function."""

    it = iter(items)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))
