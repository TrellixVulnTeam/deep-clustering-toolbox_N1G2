import random
from unittest import TestCase

import torch
from deepclustering.dataset import default_cifar10_img_transform, Cifar10DatasetInterface


class TestCifar(TestCase):
    def setUp(self) -> None:
        self.transform_list = default_cifar10_img_transform
        cifar10_option = {"shuffle": True, "batch_size": 4, "num_workers": 1}
        self.cifarGenerator = Cifar10DatasetInterface(**cifar10_option)

    def _build_concat_dataloader(self, transform):
        return self.cifarGenerator.SerialDataLoader(image_transform=transform)

    def test_concatdataloader(self):
        for _ in range(5):
            dataloader = self._build_concat_dataloader(
                random.sample(self.transform_list.items(), 1)[0][1])
            dataiter = iter(dataloader)
            for i in range(4):
                batch = dataiter.__next__()
                assert batch.__len__() == 2
                assert batch[0].shape.__len__() == 4
                assert batch[0].shape[0] == 4
                assert batch[0].shape[1] == 1

    def test_combinedataloader(self):
        combineLoader = self.cifarGenerator.ParallelDataLoader(
            self.transform_list['tf1'],
            self.transform_list['tf2'],
            self.transform_list['tf3']
        )
        combineIter = iter(combineLoader)
        for _ in range(5):
            batch_1, batch_2, batch_3 = combineIter.__next__()
            assert torch.allclose(batch_1[1], batch_2[1]) and torch.allclose(batch_1[1], batch_3[1])
