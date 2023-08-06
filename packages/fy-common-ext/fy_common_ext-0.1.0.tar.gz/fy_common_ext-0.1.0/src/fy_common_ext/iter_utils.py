#! /usr/bin/python
# -*- coding: utf-8 -*-

__all__ = [
    'iter_multi_slice',
]

from typing import Iterable, Sequence


def iter_multi_slice(iterable: Iterable, indices: Sequence[int], must_ordered=True, get_index=False):
    """Implement multi-slice on iterable, like itertools.islice.
    
    Usage:

    >>> iterable = range(10, 20)
    >>> indices = [3, 7, 9, 12]
    >>> list(iter_multi_slice(iterable, indices))
    13, 17, 19
    """
    if not indices:
        return
    if not must_ordered:
        indices = sorted(indices)
    index_it = iter(indices)
    next_index = next(index_it)
    for index, item in enumerate(iterable):
        if index != next_index:
            continue
        if get_index:
            yield index, item
        else:
            yield item
        try:
            next_index = next(index_it)
        except StopIteration:
            break
