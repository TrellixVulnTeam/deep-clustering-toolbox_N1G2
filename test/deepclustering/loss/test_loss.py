import unittest

import torch
import torch.nn.functional as F

from deepclustering.loss import loss
from deepclustering.loss.IID_losses import IIDLoss
from deepclustering.utils import simplex

device = "cuda" if torch.cuda.is_available() else "cpu"


class Test_CrossEntropyLoss2D(unittest.TestCase):
    def setUp(self):
        self.weight = torch.Tensor([1, 2, 3, 4])
        self.loss = loss.CrossEntropyLoss2d
        self.predict = torch.randn(10, 4, 224, 224)
        b, c, h, w = self.predict.shape
        self.label = torch.randint(0, 4, size=(b, h, w))

    def test_weight(self):
        self.criterion = self.loss(weight=self.weight)
        loss = self.criterion(self.predict, self.label)
        # assert loss ==1

    def test_cuda(self):
        for arg in self.__dict__:
            if isinstance(arg, torch.Tensor):
                arg = arg.to("cpu")

        self.weight = self.weight.to(device)
        self.predict = self.predict.to(device)
        self.label = self.label.to(device)
        self.test_weight()


class Test_IIC(unittest.TestCase):
    def setUp(self) -> None:
        self.x1 = F.softmax(torch.randn(1, 10), 1)
        self.x2 = F.softmax(torch.randn(1, 10), 1)
        assert simplex(self.x1)
        assert simplex(self.x2)

    def test_iic(self):
        criterion = IIDLoss(lamb=1.0)
        loss = criterion(self.x1, self.x2)
        with self.assertRaises(AssertionError):
            loss = criterion(self.x1, torch.randn(5, 10))

    def test_iic2(self):
        criterion = IIDLoss(1.0)
        loss1, _ = criterion(self.x1, self.x1)
        loss2, _ = criterion(self.x2, self.x1)
        loss3, _ = criterion(self.x1, self.x2)
        assert loss2 == loss3
