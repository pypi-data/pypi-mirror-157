import logging
from dataclasses import dataclass, field
from itertools import compress

import numpy as np
import pandas as pd
from scipy.stats import mode

from . import preprocessing
from .pilot import PilotOutput, pilot, adjust_rotation
from .trace import TraceOutput, trace


_feature_prefix = 'feature_'
_algo_prefix = 'algo_'


@dataclass
class Data:
    instlabels: pd.Index = field(init=False)
    X: np.ndarray = field(init=False)
    Y: np.ndarray = field(init=False)
    Yraw: np.ndarray = field(init=False, default=np.array([]))
    Xraw: np.ndarray = field(init=False, default=np.array([]))
    Ybin: np.ndarray = field(init=False)
    beta: np.ndarray = field(init=False)
    numGoodAlgos: list = field(init=False, default_factory=list)
    bestPerformace: list = field(init=False, default_factory=list)
    P: np.ndarray = field(init=False)
    featlabels: list = field(init=False, default_factory=list)
    algolabels: list = field(init=False, default_factory=list)


@dataclass
class Model:
    data: Data = field(init=False)
    pilot: PilotOutput = field(init=False)
    trace: TraceOutput = field(init=False)


def train_is(metadata: pd.DataFrame, opts: dict, rotation_adjust: bool = False) -> Model:
    """
    Train Instance Space model.

    :param pandas.DataFrame metadata: dataframe where each row corresponds to an instance
    :param dict opts: (nested) dictionary with options
    :param bool rotation_adjust: attempts to adjust the IS angle (bad instances at 135 degrees) - default False
    :return: model with results for all the steps according to the options passed
    :rtype: Model
    """
    logger = logging.getLogger(__name__)
    eps = np.spacing(1)

    data = Data()
    data.instlabels = metadata.index.copy()
    Xraw = metadata.filter(regex=f'^{_feature_prefix}')
    Yraw = metadata.filter(regex=f'^{_algo_prefix}')
    data.Xraw = Xraw.values
    data.Yraw = Yraw.values
    data.X = Xraw.values
    data.Y = Yraw.values
    data.featlabels = [x.replace(_feature_prefix, '') for x in Xraw.columns.tolist()]
    data.algolabels = [y.replace(_algo_prefix, '') for y in Yraw.columns.tolist()]

    logger.info("Calculating the binary measure of performance")
    msg = "An algorithm is good if its performace is "
    epsilon = opts['perf']['epsilon']
    if opts['perf']['MaxPerf']:
        Yaux = Yraw.fillna(-np.inf).values
        rankPerf = np.sort(Yaux, axis=1)[:, ::-1]
        rankAlgo = np.argsort(Yaux, axis=1)[:, ::-1]
        data.bestPerformace = rankPerf[:, [0]]
        data.P = rankAlgo[:, 0]
        if opts['perf']['AbsPerf']:
            data.Ybin = Yaux >= epsilon
            msg = msg + f"higher than {epsilon}"
        else:
            data.bestPerformace[data.bestPerformace == 0] = eps
            data.Y[data.Y == 0] = eps
            data.Y = 1 - data.Y / data.bestPerformace
            data.Ybin = np.greater_equal(Yaux, (1 - epsilon) * data.bestPerformace)
            msg = msg + f"within {np.round(100 * epsilon)}% of the best."
    else:
        Yaux = Yraw.fillna(np.inf).values
        rankPerf = np.sort(Yaux, axis=1)
        rankAlgo = np.argsort(Yaux, axis=1)
        data.bestPerformace = rankPerf[:, [0]]
        data.P = rankAlgo[:, 0]
        if opts['perf']['AbsPerf']:
            data.Ybin = Yaux <= epsilon
            msg = msg + f"less than {epsilon}"
        else:
            data.bestPerformace[data.bestPerformace == 0] = eps
            data.Y[data.Y == 0] = eps
            data.Y = data.Y / data.bestPerformace - 1
            data.Ybin = np.less_equal(Yaux, (1 + epsilon) * data.bestPerformace)
            msg = msg + f"within {np.round(100 * epsilon)}% of the best."
    logger.info(msg)

    nalgos = data.Y.shape[1]
    idx = np.all(~data.Ybin, axis=0)
    if np.any(idx):
        logger.warning("There are algorithms with no 'good' instances. They are being removed to increase speed.")
        data.Yraw = data.Yraw[:, ~idx]
        data.Y = data.Y[:, ~idx]
        data.Ybin = data.Ybin[:, ~idx]
        data.algolabels = list(compress(data.algolabels, ~idx))
        nalgos = data.Y.shape[1]
        if nalgos == 0:
            logger.error("There are no 'good' algorithms. Please verify the binary performance measure. STOPPING!")
            raise RuntimeError("There are no 'good' algorithms.")

    # Testing for ties
    bestAlgos = np.equal(data.Y, data.bestPerformace)
    multipleBestAlgos = np.sum(bestAlgos, axis=1) > 1
    aidx = np.arange(nalgos)
    for i in range(data.Y.shape[0]):
        if multipleBestAlgos[i]:
            data.P[i] = np.random.choice(aidx[bestAlgos[i]])
    logger.info(f"For {np.round(100 * np.mean(multipleBestAlgos))}% of the instances there is more than one best "
                f"algorithm. Random selection is used to break ties.")

    data.numGoodAlgos = np.sum(data.Ybin, axis=1)
    data.beta = data.numGoodAlgos > opts['general']['betaThreshold'] * nalgos

    if opts['auto']['preproc']:
        logger.info("Auto pre-processing.")
        if opts['bound']['flag']:
            logger.info("Removing extreme outliers from the feature values.")
            data.X = preprocessing.bound_outliers(data.X)
        if opts['norm']['flag']:
            logger.info("Auto-normalizing the data using Box-Cox and Z transformations.")
            # data.X, data.Y = preprocessing.auto_normalize(data.X, data.Y)
            data.X = preprocessing.auto_normalize(data.X)
            data.Y = preprocessing.auto_normalize(data.Y)

    model = Model()
    model.data = data

    logger.info("Calling PILOT to find the optimal projection.")
    model.pilot = pilot(data.X, data.Y, featlabels=data.featlabels, **opts['pilot'])

    if rotation_adjust:
        bad_instances = mode(model.data.Ybin, axis=1)[0] == 0
        if bad_instances.any():
            logger.info("Adjusting the IS rotation.")
            model.pilot.Z, R_theta = adjust_rotation(model.pilot.Z, bad_instances[:, 0])
            model.pilot.A = R_theta.dot(model.pilot.A)
            logger.info(f"The space was rotated by {np.round(np.degrees(np.arccos(R_theta[0, 0])), 1)} degrees.")
        else:
            logger.info("It is not possible to adjust the IS rotation because there are no bad instances.")

    logger.info("Calling TRACE to perform the footprint analysis.")
    model.trace = trace(model.pilot.Z, model.data.Ybin, model.data.P,
                        model.data.beta, model.data.algolabels, **opts['trace'])

    return model
