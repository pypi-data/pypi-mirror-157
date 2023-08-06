
__module_name__ = "_split_train_validation_test_at_random.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# import packages #
# --------------- #
import numpy as np


def _get_test_validation_train_proportions(
    X, proportion_test=0.2, proportion_valid=0.2
):

    n_samples = X.shape[0]

    n_test = int(n_samples * proportion_test)
    n_valid = int(n_samples * proportion_valid)
    n_train = n_samples - n_valid - n_test

    return [n_test, n_valid, n_train]


def _split_train_validation_test_at_random(X):

    X_data = {}

    n_test, n_valid, n_train = _get_test_validation_train_proportions(X)
    idx = np.arange(X.shape[0])
    mask = np.ones(len(idx), dtype=bool)
    test_idx = np.random.choice(idx, n_test, replace=False)
    X_data["test"] = X[test_idx]
    mask[test_idx] = False
    valid_idx = np.random.choice(idx[mask], n_valid, replace=False)
    X_data["valid"] = X[valid_idx]
    mask[valid_idx] = False
    train_idx = np.random.choice(idx[mask], n_train, replace=False)
    X_data["train"] = X[train_idx]

    return X_data