from functools import reduce
from typing import List, Callable

from torchvision import transforms

from .clustering_helper import ClusterDatasetInterface
from .stl10 import STL10
from ... import DATA_PATH
from ...augment import augment

__all__ = ['STL10DatasetInterface', 'default_stl10_img_transform']


class STL10DatasetInterface(ClusterDatasetInterface):
    ALLOWED_SPLIT = ['train', 'test', 'train+unlabeled']

    def __init__(self, split_partitions: List[str] = [], batch_size: int = 1, shuffle: bool = False,
                 num_workers: int = 1, pin_memory: bool = True) -> None:
        super().__init__(STL10, split_partitions, batch_size, shuffle, num_workers, pin_memory)

    def _creat_concatDataset(self, image_transform: Callable, target_transform: Callable, dataset_dict: dict = {}):
        for split in self.split_partitions:
            assert split in self.ALLOWED_SPLIT, f"Allowed split in STL-10:{self.ALLOWED_SPLIT}, given {split}."

        _datasets = []
        for split in self.split_partitions:
            dataset = self.DataClass(DATA_PATH, split=split,
                                     transform=image_transform, target_transform=target_transform,
                                     download=True, **dataset_dict)
            _datasets.append(dataset)
        serial_dataset = reduce(lambda x, y: x + y, _datasets)
        return serial_dataset


default_stl10_img_transform = {
    'tf1': transforms.Compose([augment.RandomCrop(size=(64, 64), padding=None),
                               augment.Resize(size=(64, 64), interpolation=0),
                               augment.Img2Tensor(include_grey=True, include_rgb=False)]),
    'tf2': transforms.Compose([augment.RandomCrop(size=(64, 64), padding=None),
                               augment.Resize(size=(64, 64), interpolation=0),
                               transforms.RandomHorizontalFlip(p=0.5),
                               transforms.ColorJitter(
                                   brightness=[0.6, 1.4],
                                   contrast=[0.6, 1.4],
                                   saturation=[0.6, 1.4],
                                   hue=[-0.125, 0.125]
                               ),
                               augment.Img2Tensor(include_grey=True, include_rgb=False)]),
    'tf3': transforms.Compose([augment.CenterCrop(size=(64, 64)),
                               augment.Resize(size=(64, 64), interpolation=0),
                               augment.Img2Tensor(include_grey=True, include_rgb=False)]),

}
