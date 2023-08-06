import numpy as np
from scipy.stats import iqr
from sklearn.preprocessing import PowerTransformer


def auto_normalize(X: np.ndarray) -> np.ndarray:
    if X.ndim == 1:
        X = X.reshape(-1, 1)

    pt = PowerTransformer(method='yeo-johnson', standardize=True)
    return pt.fit_transform(X)


def bound_outliers(X: np.ndarray) -> np.ndarray:
    IQR = iqr(X, axis=0)
    a_min = np.median(X, axis=0) - 5 * IQR
    a_max = np.median(X, axis=0) + 5 * IQR

    return np.clip(X, a_min, a_max)
