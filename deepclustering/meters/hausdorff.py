from typing import *
import warnings
import numpy as np
import torch
from torch import Tensor
from scipy.spatial.distance import directed_hausdorff
from .metric import Metric
from ..utils import one_hot

__all__ = ['HaussdorffDistance']


class HaussdorffDistance(Metric):
    default_class_num = 4

    def __init__(self, C=None, report_axises=None) -> None:
        super().__init__()
        self._haussdorff_log: List[Tensor] = []
        self._C = C
        self._report_axises = report_axises

    def reset(self):
        self._haussdorff_log = []

    def add(self, pred: Tensor, label: Tensor) -> None:
        """
        Add function to add torch.Tensor for pred and label, which are all one-hot matrices.
        :param pred: one-hot prediction matrix
        :param label: one-hot label matrix
        :return: None
        """
        assert one_hot(pred), pred
        assert one_hot(label), label
        assert len(pred.shape) == 4, f"Input tensor is restricted to 4-D tensor, given {pred.shape}."
        assert pred.shape == label.shape, f"The shape of pred and label should be the same, " \
            f"given {pred.shape, label.shape}"
        B, C, _, _ = pred.shape  # here we only accept 4 dimensional input.
        if self._C is None:
            self._C = C
        else:
            assert self._C == C, f"Input dimension C: {C} is not consistent with the registered C:{self._C}"

        res = torch.zeros((B, C), dtype=torch.float32, device=pred.device)
        n_pred = pred.cpu().numpy()
        n_target = label.cpu().numpy()
        for b in range(B):
            if C == 2:
                res[b, :] = numpy_haussdorf(n_pred[b, 0], n_target[b, 0])
                continue

            for c in range(C):
                res[b, c] = numpy_haussdorf(n_pred[b, c], n_target[b, c])

        self._haussdorff_log.append(res)

    def value(self, **kwargs):
        log: Tensor = self.log
        means = log.mean(0)
        stds = log.std(0)
        report_means = log.mean(1) if self._report_axises == 'all' else log[:, self._report_axises].mean(1)
        report_std = report_means.std()
        report_mean = report_means.mean()
        return (report_mean, report_std), (means, stds)

    def summary(self) -> dict:
        if self._report_axises is None:
            self._report_axises = [i for i in range(self._C if self._C is not None else self.default_class_num)]

        _, (means, _) = self.value()
        return {f"HD{i}": means[i].item() for i in self._report_axises}

    def detailed_summary(self) -> dict:
        if self._report_axises is None:
            self._report_axises = [i for i in range(self._C if self._C is not None else self.default_class_num)]
        _, (means, _) = self.value()
        return {f'HD{i}': means[i].item() for i in range(len(means))}

    @property
    def log(self):
        try:
            log = torch.cat(self._haussdorff_log)
        except RuntimeError:
            warnings.warn(f'No log has been found', RuntimeWarning)
            log = torch.Tensor([0 for _ in range(self._C if self._C is not None else \
                                                          self.default_class_num)])
            log = log.unsqueeze(0)
        assert len(log.shape) == 2
        return log


def numpy_haussdorf(pred: np.ndarray, target: np.ndarray) -> float:
    assert len(pred.shape) == 2
    assert pred.shape == target.shape

    return max(directed_hausdorff(pred, target)[0], directed_hausdorff(target, pred)[0])