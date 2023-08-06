import numpy as np


def pooled_std(group1: np.ndarray, group2: np.ndarray):
    """
    Calculates pooled standard deviation.
    :param group1: the first data array
    :param group2: the second data array
    :returns: computed value
    """
    def _pooled_var(data: np.ndarray) -> np.ndarray:
        return np.sum(np.power(data - data.mean(axis=0), 2), axis=0)
    return np.sqrt(
        (_pooled_var(group1) + _pooled_var(group2)) /
        (group1.shape[0] + group2.shape[0] - 2)
    )
