from torch.utils.data import IterableDataset
from typing import Optional, Any, List
from datasets import interleave_datasets
from itertools import chain


def _nrows_from_info(dataset: Any, split_name: str = 'train'):
    num_rows = -1
    if hasattr(dataset, "info") and hasattr(dataset.info, "splits"):
        sp_info = dataset.info.splits.get(split_name)
        if sp_info and hasattr(sp_info, "num_examples"):
            num_rows = sp_info.num_examples
    return num_rows


class IterableDatasetWrapper(IterableDataset):
    def __init__(self,
                 datasets: List[IterableDataset],
                 split_names: List[str] = None,
                 length: Optional[int] = None,
                 data_format: str = "torch") -> None:
        super(IterableDatasetWrapper, self).__init__()
        split_names = ['train']*len(datasets) if split_names is None else split_names
        assert len(datasets) == len(split_names)
        _datasets, _lengths = [], []
        for dataset, split_name in zip(datasets, split_names):
            print(dataset)
            _length = _nrows_from_info(dataset, split_name)
            _length = 1000000 if _length < 0 else _length
            _datasets.append(dataset.with_format(data_format))
            _lengths.append(_length)

        self.dataset = chain(*[interleave_datasets([d]) for d in _datasets])
        self.length = sum(_lengths) if length is None else length

    def __iter__(self):
        return iter(self.dataset)

    def __len__(self) -> int:
        return self.length