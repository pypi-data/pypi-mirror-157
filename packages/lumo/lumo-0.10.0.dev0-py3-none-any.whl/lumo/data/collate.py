"""

"""
from functools import wraps
from typing import Any, Mapping, Sequence

import numpy as np
import torch
from torch.utils.data._utils.collate import default_collate


class CollateBase:

    def __init__(self, collate_fn=default_collate, *args, **kwargs) -> None:
        super().__init__()
        if collate_fn is None:
            collate_fn = default_collate
        self._collate_fn = collate_fn
        self.initial(*args, **kwargs)

    def initial(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        res = self.before_collate(*args, **kwargs)
        res = self._collate_fn(res)
        res = self.after_collate(res)
        return res

    def before_collate(self, sample_list):
        return sample_list

    def raw_collate(self, sample_list):
        return self._collate_fn(sample_list)

    def collate(self, sample_list):
        return self._collate_fn(sample_list)

    def after_collate(self, batch):
        return batch


class IgnoreNoneCollate(CollateBase):

    def _filter_none(self, item):
        if item is None:
            return False
        if isinstance(item, (list, tuple)):
            return all([self._filter_none(i) for i in item])
        if isinstance(item, dict):
            return all(self._filter_none(i) for i in item.values())
        return True

    def before_collate(self, sample_list):
        return list(filter(self._filter_none, sample_list))


def numpy_collate(batch):
    r"""Puts each data field into a tensor with outer dimension batch size"""

    elem = batch[0]
    elem_type = type(elem)
    if isinstance(elem, torch.Tensor):
        batch = [elem.detach().cpu().numpy() for elem in batch]
        return np.stack(batch, 0)
    elif elem_type.__module__ == 'numpy' and elem_type.__name__ != 'str_' \
            and elem_type.__name__ != 'string_':
        if elem_type.__name__ == 'ndarray' or elem_type.__name__ == 'memmap':
            return numpy_collate([np.array(b) for b in batch])
        elif elem.shape == ():  # scalars
            return np.array(batch)
    elif isinstance(elem, float):
        return np.array(batch, dtype=np.float)
    elif isinstance(elem, int):
        return np.array(batch)
    elif isinstance(elem, (str, bytes)):
        return batch
    elif isinstance(elem, Mapping):
        return {key: numpy_collate([d[key] for d in batch]) for key in elem}
    elif isinstance(elem, tuple) and hasattr(elem, '_fields'):  # namedtuple
        return elem_type(*(numpy_collate(samples) for samples in zip(*batch)))
    elif isinstance(elem, Sequence):
        # check to make sure that the elements in batch have consistent size
        it = iter(batch)
        elem_size = len(next(it))
        if not all(len(elem) == elem_size for elem in it):
            raise RuntimeError('each element in list of batch should be of equal size')
        transposed = zip(*batch)
        return [numpy_collate(samples) for samples in transposed]
