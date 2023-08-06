"""Support scikit-learn using object mode of Numba """
import itertools
import numbers
import types as pytypes
import warnings
import numba
import numpy as np
import pandas as pd
import sklearn.cluster
import sklearn.ensemble
import sklearn.feature_extraction
import sklearn.linear_model
import sklearn.metrics
import sklearn.model_selection
import sklearn.naive_bayes
import sklearn.svm
import sklearn.utils
from mpi4py import MPI
from numba.core import types
from numba.extending import NativeValue, box, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from sklearn.exceptions import UndefinedMetricWarning
from sklearn.metrics import hinge_loss, log_loss, mean_squared_error
from sklearn.preprocessing import LabelBinarizer
from sklearn.preprocessing._data import _handle_zeros_in_scale as sklearn_handle_zeros_in_scale
from sklearn.utils.extmath import _safe_accumulator_op as sklearn_safe_accumulator_op
from sklearn.utils.validation import _check_sample_weight, column_or_1d
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import NumericIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.libs.csr_matrix_ext import CSRMatrixType
from bodo.libs.distributed_api import Reduce_Type, create_subcomm_mpi4py, get_host_ranks, get_nodes_first_ranks, get_num_nodes
from bodo.utils.typing import BodoError, BodoWarning, check_unsupported_args, get_overload_const_int, get_overload_const_str, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true


def check_sklearn_version():
    if not bodo.compiler._is_sklearn_supported_version:
        bnew__tmn = f""" Bodo requires at most version {bodo.compiler._max_sklearn_ver_str} of scikit-learn.
             Installed version is {sklearn.__version__}.
"""
        raise BodoError(bnew__tmn)


def random_forest_model_fit(m, X, y):
    ejc__jbvfx = m.n_estimators
    wkpse__znnw = MPI.Get_processor_name()
    poby__apvvl = get_host_ranks()
    fkim__aeb = len(poby__apvvl)
    ysxhi__iakl = bodo.get_rank()
    m.n_estimators = bodo.libs.distributed_api.get_node_portion(ejc__jbvfx,
        fkim__aeb, ysxhi__iakl)
    if ysxhi__iakl == poby__apvvl[wkpse__znnw][0]:
        m.n_jobs = len(poby__apvvl[wkpse__znnw])
        if m.random_state is None:
            m.random_state = np.random.RandomState()
        from sklearn.utils import parallel_backend
        with parallel_backend('threading'):
            m.fit(X, y)
        m.n_jobs = 1
    with numba.objmode(first_rank_node='int32[:]'):
        first_rank_node = get_nodes_first_ranks()
    ipi__eroh = create_subcomm_mpi4py(first_rank_node)
    if ipi__eroh != MPI.COMM_NULL:
        hwiql__qar = 10
        fedo__ohgm = bodo.libs.distributed_api.get_node_portion(ejc__jbvfx,
            fkim__aeb, 0)
        jya__zqc = fedo__ohgm // hwiql__qar
        if fedo__ohgm % hwiql__qar != 0:
            jya__zqc += 1
        hlaj__oato = []
        for pcfwn__qwkc in range(jya__zqc):
            wuvwl__baibp = ipi__eroh.gather(m.estimators_[pcfwn__qwkc *
                hwiql__qar:pcfwn__qwkc * hwiql__qar + hwiql__qar])
            if ysxhi__iakl == 0:
                hlaj__oato += list(itertools.chain.from_iterable(wuvwl__baibp))
        if ysxhi__iakl == 0:
            m.estimators_ = hlaj__oato
    axfge__qisy = MPI.COMM_WORLD
    if ysxhi__iakl == 0:
        for pcfwn__qwkc in range(0, ejc__jbvfx, 10):
            axfge__qisy.bcast(m.estimators_[pcfwn__qwkc:pcfwn__qwkc + 10])
        if isinstance(m, sklearn.ensemble.RandomForestClassifier):
            axfge__qisy.bcast(m.n_classes_)
            axfge__qisy.bcast(m.classes_)
        axfge__qisy.bcast(m.n_outputs_)
    else:
        earvp__djj = []
        for pcfwn__qwkc in range(0, ejc__jbvfx, 10):
            earvp__djj += axfge__qisy.bcast(None)
        if isinstance(m, sklearn.ensemble.RandomForestClassifier):
            m.n_classes_ = axfge__qisy.bcast(None)
            m.classes_ = axfge__qisy.bcast(None)
        m.n_outputs_ = axfge__qisy.bcast(None)
        m.estimators_ = earvp__djj
    assert len(m.estimators_) == ejc__jbvfx
    m.n_estimators = ejc__jbvfx
    m.n_features_ = X.shape[1]


class BodoRandomForestClassifierType(types.Opaque):

    def __init__(self):
        super(BodoRandomForestClassifierType, self).__init__(name=
            'BodoRandomForestClassifierType')


random_forest_classifier_type = BodoRandomForestClassifierType()
types.random_forest_classifier_type = random_forest_classifier_type
register_model(BodoRandomForestClassifierType)(models.OpaqueModel)


@typeof_impl.register(sklearn.ensemble.RandomForestClassifier)
def typeof_random_forest_classifier(val, c):
    return random_forest_classifier_type


@box(BodoRandomForestClassifierType)
def box_random_forest_classifier(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoRandomForestClassifierType)
def unbox_random_forest_classifier(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.ensemble.RandomForestClassifier, no_unliteral=True)
def sklearn_ensemble_RandomForestClassifier_overload(n_estimators=100,
    criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf
    =1, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=
    None, min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=
    True, oob_score=False, n_jobs=None, random_state=None, verbose=0,
    warm_start=False, class_weight=None, ccp_alpha=0.0, max_samples=None):
    check_sklearn_version()

    def _sklearn_ensemble_RandomForestClassifier_impl(n_estimators=100,
        criterion='gini', max_depth=None, min_samples_split=2,
        min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=
        'auto', max_leaf_nodes=None, min_impurity_decrease=0.0,
        min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=
        None, random_state=None, verbose=0, warm_start=False, class_weight=
        None, ccp_alpha=0.0, max_samples=None):
        with numba.objmode(m='random_forest_classifier_type'):
            if random_state is not None and get_num_nodes() > 1:
                print(
                    'With multinode, fixed random_state seed values are ignored.\n'
                    )
                random_state = None
            m = sklearn.ensemble.RandomForestClassifier(n_estimators=
                n_estimators, criterion=criterion, max_depth=max_depth,
                min_samples_split=min_samples_split, min_samples_leaf=
                min_samples_leaf, min_weight_fraction_leaf=
                min_weight_fraction_leaf, max_features=max_features,
                max_leaf_nodes=max_leaf_nodes, min_impurity_decrease=
                min_impurity_decrease, min_impurity_split=
                min_impurity_split, bootstrap=bootstrap, oob_score=
                oob_score, n_jobs=1, random_state=random_state, verbose=
                verbose, warm_start=warm_start, class_weight=class_weight,
                ccp_alpha=ccp_alpha, max_samples=max_samples)
        return m
    return _sklearn_ensemble_RandomForestClassifier_impl


def parallel_predict_regression(m, X):
    check_sklearn_version()

    def _model_predict_impl(m, X):
        with numba.objmode(result='float64[:]'):
            m.n_jobs = 1
            if len(X) == 0:
                result = np.empty(0, dtype=np.float64)
            else:
                result = m.predict(X).astype(np.float64).flatten()
        return result
    return _model_predict_impl


def parallel_predict(m, X):
    check_sklearn_version()

    def _model_predict_impl(m, X):
        with numba.objmode(result='int64[:]'):
            m.n_jobs = 1
            if X.shape[0] == 0:
                result = np.empty(0, dtype=np.int64)
            else:
                result = m.predict(X).astype(np.int64).flatten()
        return result
    return _model_predict_impl


def parallel_predict_proba(m, X):
    check_sklearn_version()

    def _model_predict_proba_impl(m, X):
        with numba.objmode(result='float64[:,:]'):
            m.n_jobs = 1
            if X.shape[0] == 0:
                result = np.empty((0, 0), dtype=np.float64)
            else:
                result = m.predict_proba(X).astype(np.float64)
        return result
    return _model_predict_proba_impl


def parallel_predict_log_proba(m, X):
    check_sklearn_version()

    def _model_predict_log_proba_impl(m, X):
        with numba.objmode(result='float64[:,:]'):
            m.n_jobs = 1
            if X.shape[0] == 0:
                result = np.empty((0, 0), dtype=np.float64)
            else:
                result = m.predict_log_proba(X).astype(np.float64)
        return result
    return _model_predict_log_proba_impl


def parallel_score(m, X, y, sample_weight=None, _is_data_distributed=False):
    check_sklearn_version()

    def _model_score_impl(m, X, y, sample_weight=None, _is_data_distributed
        =False):
        with numba.objmode(result='float64[:]'):
            result = m.score(X, y, sample_weight=sample_weight)
            if _is_data_distributed:
                result = np.full(len(y), result)
            else:
                result = np.array([result])
        if _is_data_distributed:
            result = bodo.allgatherv(result)
        return result.mean()
    return _model_score_impl


@overload_method(BodoRandomForestClassifierType, 'predict', no_unliteral=True)
def overload_model_predict(m, X):
    check_sklearn_version()
    """Overload Random Forest Classifier predict. (Data parallelization)"""
    return parallel_predict(m, X)


@overload_method(BodoRandomForestClassifierType, 'predict_proba',
    no_unliteral=True)
def overload_rf_predict_proba(m, X):
    check_sklearn_version()
    """Overload Random Forest Classifier predict_proba. (Data parallelization)"""
    return parallel_predict_proba(m, X)


@overload_method(BodoRandomForestClassifierType, 'predict_log_proba',
    no_unliteral=True)
def overload_rf_predict_log_proba(m, X):
    check_sklearn_version()
    """Overload Random Forest Classifier predict_log_proba. (Data parallelization)"""
    return parallel_predict_log_proba(m, X)


@overload_method(BodoRandomForestClassifierType, 'score', no_unliteral=True)
def overload_model_score(m, X, y, sample_weight=None, _is_data_distributed=
    False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


def precision_recall_fscore_support_helper(MCM, average):

    def multilabel_confusion_matrix(y_true, y_pred, *, sample_weight=None,
        labels=None, samplewise=False):
        return MCM
    ekkb__tlg = sklearn.metrics._classification.multilabel_confusion_matrix
    result = -1.0
    try:
        sklearn.metrics._classification.multilabel_confusion_matrix = (
            multilabel_confusion_matrix)
        result = (sklearn.metrics._classification.
            precision_recall_fscore_support([], [], average=average))
    finally:
        sklearn.metrics._classification.multilabel_confusion_matrix = ekkb__tlg
    return result


@numba.njit
def precision_recall_fscore_parallel(y_true, y_pred, operation, average=
    'binary'):
    labels = bodo.libs.array_kernels.unique(y_true, parallel=True)
    labels = bodo.allgatherv(labels, False)
    labels = bodo.libs.array_kernels.sort(labels, ascending=True, inplace=False
        )
    eywd__krjy = len(labels)
    ibb__amc = np.zeros(eywd__krjy, np.int64)
    vndq__owbb = np.zeros(eywd__krjy, np.int64)
    vwxq__lwukm = np.zeros(eywd__krjy, np.int64)
    gpoyc__xlk = (bodo.hiframes.pd_categorical_ext.
        get_label_dict_from_categories(labels))
    for pcfwn__qwkc in range(len(y_true)):
        vndq__owbb[gpoyc__xlk[y_true[pcfwn__qwkc]]] += 1
        if y_pred[pcfwn__qwkc] not in gpoyc__xlk:
            continue
        hnk__trq = gpoyc__xlk[y_pred[pcfwn__qwkc]]
        vwxq__lwukm[hnk__trq] += 1
        if y_true[pcfwn__qwkc] == y_pred[pcfwn__qwkc]:
            ibb__amc[hnk__trq] += 1
    ibb__amc = bodo.libs.distributed_api.dist_reduce(ibb__amc, np.int32(
        Reduce_Type.Sum.value))
    vndq__owbb = bodo.libs.distributed_api.dist_reduce(vndq__owbb, np.int32
        (Reduce_Type.Sum.value))
    vwxq__lwukm = bodo.libs.distributed_api.dist_reduce(vwxq__lwukm, np.
        int32(Reduce_Type.Sum.value))
    kqg__wjkt = vwxq__lwukm - ibb__amc
    iszr__txj = vndq__owbb - ibb__amc
    quch__wksvx = ibb__amc
    yldna__zye = y_true.shape[0] - quch__wksvx - kqg__wjkt - iszr__txj
    with numba.objmode(result='float64[:]'):
        MCM = np.array([yldna__zye, kqg__wjkt, iszr__txj, quch__wksvx]
            ).T.reshape(-1, 2, 2)
        if operation == 'precision':
            result = precision_recall_fscore_support_helper(MCM, average)[0]
        elif operation == 'recall':
            result = precision_recall_fscore_support_helper(MCM, average)[1]
        elif operation == 'f1':
            result = precision_recall_fscore_support_helper(MCM, average)[2]
        if average is not None:
            result = np.array([result])
    return result


@overload(sklearn.metrics.precision_score, no_unliteral=True)
def overload_precision_score(y_true, y_pred, average='binary',
    _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_none(average):
        if is_overload_false(_is_data_distributed):

            def _precision_score_impl(y_true, y_pred, average='binary',
                _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(score='float64[:]'):
                    score = sklearn.metrics.precision_score(y_true, y_pred,
                        average=average)
                return score
            return _precision_score_impl
        else:

            def _precision_score_impl(y_true, y_pred, average='binary',
                _is_data_distributed=False):
                return precision_recall_fscore_parallel(y_true, y_pred,
                    'precision', average=average)
            return _precision_score_impl
    elif is_overload_false(_is_data_distributed):

        def _precision_score_impl(y_true, y_pred, average='binary',
            _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(score='float64'):
                score = sklearn.metrics.precision_score(y_true, y_pred,
                    average=average)
            return score
        return _precision_score_impl
    else:

        def _precision_score_impl(y_true, y_pred, average='binary',
            _is_data_distributed=False):
            score = precision_recall_fscore_parallel(y_true, y_pred,
                'precision', average=average)
            return score[0]
        return _precision_score_impl


@overload(sklearn.metrics.recall_score, no_unliteral=True)
def overload_recall_score(y_true, y_pred, average='binary',
    _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_none(average):
        if is_overload_false(_is_data_distributed):

            def _recall_score_impl(y_true, y_pred, average='binary',
                _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(score='float64[:]'):
                    score = sklearn.metrics.recall_score(y_true, y_pred,
                        average=average)
                return score
            return _recall_score_impl
        else:

            def _recall_score_impl(y_true, y_pred, average='binary',
                _is_data_distributed=False):
                return precision_recall_fscore_parallel(y_true, y_pred,
                    'recall', average=average)
            return _recall_score_impl
    elif is_overload_false(_is_data_distributed):

        def _recall_score_impl(y_true, y_pred, average='binary',
            _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(score='float64'):
                score = sklearn.metrics.recall_score(y_true, y_pred,
                    average=average)
            return score
        return _recall_score_impl
    else:

        def _recall_score_impl(y_true, y_pred, average='binary',
            _is_data_distributed=False):
            score = precision_recall_fscore_parallel(y_true, y_pred,
                'recall', average=average)
            return score[0]
        return _recall_score_impl


@overload(sklearn.metrics.f1_score, no_unliteral=True)
def overload_f1_score(y_true, y_pred, average='binary',
    _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_none(average):
        if is_overload_false(_is_data_distributed):

            def _f1_score_impl(y_true, y_pred, average='binary',
                _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(score='float64[:]'):
                    score = sklearn.metrics.f1_score(y_true, y_pred,
                        average=average)
                return score
            return _f1_score_impl
        else:

            def _f1_score_impl(y_true, y_pred, average='binary',
                _is_data_distributed=False):
                return precision_recall_fscore_parallel(y_true, y_pred,
                    'f1', average=average)
            return _f1_score_impl
    elif is_overload_false(_is_data_distributed):

        def _f1_score_impl(y_true, y_pred, average='binary',
            _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(score='float64'):
                score = sklearn.metrics.f1_score(y_true, y_pred, average=
                    average)
            return score
        return _f1_score_impl
    else:

        def _f1_score_impl(y_true, y_pred, average='binary',
            _is_data_distributed=False):
            score = precision_recall_fscore_parallel(y_true, y_pred, 'f1',
                average=average)
            return score[0]
        return _f1_score_impl


def mse_mae_dist_helper(y_true, y_pred, sample_weight, multioutput, squared,
    metric):
    if metric == 'mse':
        uwie__ilk = sklearn.metrics.mean_squared_error(y_true, y_pred,
            sample_weight=sample_weight, multioutput='raw_values', squared=True
            )
    elif metric == 'mae':
        uwie__ilk = sklearn.metrics.mean_absolute_error(y_true, y_pred,
            sample_weight=sample_weight, multioutput='raw_values')
    else:
        raise RuntimeError(
            f"Unrecognized metric {metric}. Must be one of 'mae' and 'mse'")
    axfge__qisy = MPI.COMM_WORLD
    hjp__gpy = axfge__qisy.Get_size()
    if sample_weight is not None:
        ncfk__vbyur = np.sum(sample_weight)
    else:
        ncfk__vbyur = np.float64(y_true.shape[0])
    znrm__bnpmq = np.zeros(hjp__gpy, dtype=type(ncfk__vbyur))
    axfge__qisy.Allgather(ncfk__vbyur, znrm__bnpmq)
    unsnu__scebv = np.zeros((hjp__gpy, *uwie__ilk.shape), dtype=uwie__ilk.dtype
        )
    axfge__qisy.Allgather(uwie__ilk, unsnu__scebv)
    afz__fxt = np.average(unsnu__scebv, weights=znrm__bnpmq, axis=0)
    if metric == 'mse' and not squared:
        afz__fxt = np.sqrt(afz__fxt)
    if isinstance(multioutput, str) and multioutput == 'raw_values':
        return afz__fxt
    elif isinstance(multioutput, str) and multioutput == 'uniform_average':
        return np.average(afz__fxt)
    else:
        return np.average(afz__fxt, weights=multioutput)


@overload(sklearn.metrics.mean_squared_error, no_unliteral=True)
def overload_mean_squared_error(y_true, y_pred, sample_weight=None,
    multioutput='uniform_average', squared=True, _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_constant_str(multioutput) and get_overload_const_str(
        multioutput) == 'raw_values':
        if is_overload_none(sample_weight):

            def _mse_impl(y_true, y_pred, sample_weight=None, multioutput=
                'uniform_average', squared=True, _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(err='float64[:]'):
                    if _is_data_distributed:
                        err = mse_mae_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput, squared=squared, metric='mse')
                    else:
                        err = sklearn.metrics.mean_squared_error(y_true,
                            y_pred, sample_weight=sample_weight,
                            multioutput=multioutput, squared=squared)
                return err
            return _mse_impl
        else:

            def _mse_impl(y_true, y_pred, sample_weight=None, multioutput=
                'uniform_average', squared=True, _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                sample_weight = bodo.utils.conversion.coerce_to_array(
                    sample_weight)
                with numba.objmode(err='float64[:]'):
                    if _is_data_distributed:
                        err = mse_mae_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput, squared=squared, metric='mse')
                    else:
                        err = sklearn.metrics.mean_squared_error(y_true,
                            y_pred, sample_weight=sample_weight,
                            multioutput=multioutput, squared=squared)
                return err
            return _mse_impl
    elif is_overload_none(sample_weight):

        def _mse_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', squared=True, _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(err='float64'):
                if _is_data_distributed:
                    err = mse_mae_dist_helper(y_true, y_pred, sample_weight
                        =sample_weight, multioutput=multioutput, squared=
                        squared, metric='mse')
                else:
                    err = sklearn.metrics.mean_squared_error(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=
                        multioutput, squared=squared)
            return err
        return _mse_impl
    else:

        def _mse_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', squared=True, _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            sample_weight = bodo.utils.conversion.coerce_to_array(sample_weight
                )
            with numba.objmode(err='float64'):
                if _is_data_distributed:
                    err = mse_mae_dist_helper(y_true, y_pred, sample_weight
                        =sample_weight, multioutput=multioutput, squared=
                        squared, metric='mse')
                else:
                    err = sklearn.metrics.mean_squared_error(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=
                        multioutput, squared=squared)
            return err
        return _mse_impl


@overload(sklearn.metrics.mean_absolute_error, no_unliteral=True)
def overload_mean_absolute_error(y_true, y_pred, sample_weight=None,
    multioutput='uniform_average', _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_constant_str(multioutput) and get_overload_const_str(
        multioutput) == 'raw_values':
        if is_overload_none(sample_weight):

            def _mae_impl(y_true, y_pred, sample_weight=None, multioutput=
                'uniform_average', _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(err='float64[:]'):
                    if _is_data_distributed:
                        err = mse_mae_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput, squared=True, metric='mae')
                    else:
                        err = sklearn.metrics.mean_absolute_error(y_true,
                            y_pred, sample_weight=sample_weight,
                            multioutput=multioutput)
                return err
            return _mae_impl
        else:

            def _mae_impl(y_true, y_pred, sample_weight=None, multioutput=
                'uniform_average', _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                sample_weight = bodo.utils.conversion.coerce_to_array(
                    sample_weight)
                with numba.objmode(err='float64[:]'):
                    if _is_data_distributed:
                        err = mse_mae_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput, squared=True, metric='mae')
                    else:
                        err = sklearn.metrics.mean_absolute_error(y_true,
                            y_pred, sample_weight=sample_weight,
                            multioutput=multioutput)
                return err
            return _mae_impl
    elif is_overload_none(sample_weight):

        def _mae_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(err='float64'):
                if _is_data_distributed:
                    err = mse_mae_dist_helper(y_true, y_pred, sample_weight
                        =sample_weight, multioutput=multioutput, squared=
                        True, metric='mae')
                else:
                    err = sklearn.metrics.mean_absolute_error(y_true,
                        y_pred, sample_weight=sample_weight, multioutput=
                        multioutput)
            return err
        return _mae_impl
    else:

        def _mae_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            sample_weight = bodo.utils.conversion.coerce_to_array(sample_weight
                )
            with numba.objmode(err='float64'):
                if _is_data_distributed:
                    err = mse_mae_dist_helper(y_true, y_pred, sample_weight
                        =sample_weight, multioutput=multioutput, squared=
                        True, metric='mae')
                else:
                    err = sklearn.metrics.mean_absolute_error(y_true,
                        y_pred, sample_weight=sample_weight, multioutput=
                        multioutput)
            return err
        return _mae_impl


def accuracy_score_dist_helper(y_true, y_pred, normalize, sample_weight):
    score = sklearn.metrics.accuracy_score(y_true, y_pred, normalize=False,
        sample_weight=sample_weight)
    axfge__qisy = MPI.COMM_WORLD
    score = axfge__qisy.allreduce(score, op=MPI.SUM)
    if normalize:
        rsfac__jmrwe = np.sum(sample_weight
            ) if sample_weight is not None else len(y_true)
        rsfac__jmrwe = axfge__qisy.allreduce(rsfac__jmrwe, op=MPI.SUM)
        score = score / rsfac__jmrwe
    return score


@overload(sklearn.metrics.accuracy_score, no_unliteral=True)
def overload_accuracy_score(y_true, y_pred, normalize=True, sample_weight=
    None, _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_false(_is_data_distributed):
        if is_overload_none(sample_weight):

            def _accuracy_score_impl(y_true, y_pred, normalize=True,
                sample_weight=None, _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(score='float64'):
                    score = sklearn.metrics.accuracy_score(y_true, y_pred,
                        normalize=normalize, sample_weight=sample_weight)
                return score
            return _accuracy_score_impl
        else:

            def _accuracy_score_impl(y_true, y_pred, normalize=True,
                sample_weight=None, _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                sample_weight = bodo.utils.conversion.coerce_to_array(
                    sample_weight)
                with numba.objmode(score='float64'):
                    score = sklearn.metrics.accuracy_score(y_true, y_pred,
                        normalize=normalize, sample_weight=sample_weight)
                return score
            return _accuracy_score_impl
    elif is_overload_none(sample_weight):

        def _accuracy_score_impl(y_true, y_pred, normalize=True,
            sample_weight=None, _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(score='float64'):
                score = accuracy_score_dist_helper(y_true, y_pred,
                    normalize=normalize, sample_weight=sample_weight)
            return score
        return _accuracy_score_impl
    else:

        def _accuracy_score_impl(y_true, y_pred, normalize=True,
            sample_weight=None, _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            sample_weight = bodo.utils.conversion.coerce_to_array(sample_weight
                )
            with numba.objmode(score='float64'):
                score = accuracy_score_dist_helper(y_true, y_pred,
                    normalize=normalize, sample_weight=sample_weight)
            return score
        return _accuracy_score_impl


def check_consistent_length_parallel(*arrays):
    axfge__qisy = MPI.COMM_WORLD
    huk__yrvnd = True
    fasqe__dgo = [len(xrc__qzywl) for xrc__qzywl in arrays if xrc__qzywl is not
        None]
    if len(np.unique(fasqe__dgo)) > 1:
        huk__yrvnd = False
    huk__yrvnd = axfge__qisy.allreduce(huk__yrvnd, op=MPI.LAND)
    return huk__yrvnd


def r2_score_dist_helper(y_true, y_pred, sample_weight, multioutput):
    axfge__qisy = MPI.COMM_WORLD
    if y_true.ndim == 1:
        y_true = y_true.reshape((-1, 1))
    if y_pred.ndim == 1:
        y_pred = y_pred.reshape((-1, 1))
    if not check_consistent_length_parallel(y_true, y_pred, sample_weight):
        raise ValueError(
            'y_true, y_pred and sample_weight (if not None) have inconsistent number of samples'
            )
    qhgy__mqhrk = y_true.shape[0]
    mhwe__kqyjb = axfge__qisy.allreduce(qhgy__mqhrk, op=MPI.SUM)
    if mhwe__kqyjb < 2:
        warnings.warn(
            'R^2 score is not well-defined with less than two samples.',
            UndefinedMetricWarning)
        return np.array([float('nan')])
    if sample_weight is not None:
        sample_weight = column_or_1d(sample_weight)
        ewj__ocr = sample_weight[:, np.newaxis]
    else:
        sample_weight = np.float64(y_true.shape[0])
        ewj__ocr = 1.0
    jdhi__air = (ewj__ocr * (y_true - y_pred) ** 2).sum(axis=0, dtype=np.
        float64)
    pbp__cesdw = np.zeros(jdhi__air.shape, dtype=jdhi__air.dtype)
    axfge__qisy.Allreduce(jdhi__air, pbp__cesdw, op=MPI.SUM)
    yvjnj__xaczr = np.nansum(y_true * ewj__ocr, axis=0, dtype=np.float64)
    jcmo__yldnw = np.zeros_like(yvjnj__xaczr)
    axfge__qisy.Allreduce(yvjnj__xaczr, jcmo__yldnw, op=MPI.SUM)
    gbir__srh = np.nansum(sample_weight, dtype=np.float64)
    avldg__evqrz = axfge__qisy.allreduce(gbir__srh, op=MPI.SUM)
    dwdnr__idpr = jcmo__yldnw / avldg__evqrz
    qhxh__qpjcr = (ewj__ocr * (y_true - dwdnr__idpr) ** 2).sum(axis=0,
        dtype=np.float64)
    qap__aseq = np.zeros(qhxh__qpjcr.shape, dtype=qhxh__qpjcr.dtype)
    axfge__qisy.Allreduce(qhxh__qpjcr, qap__aseq, op=MPI.SUM)
    dpnz__eulpb = qap__aseq != 0
    ywcsb__qkgq = pbp__cesdw != 0
    yuit__wel = dpnz__eulpb & ywcsb__qkgq
    stndi__goazs = np.ones([y_true.shape[1] if len(y_true.shape) > 1 else 1])
    stndi__goazs[yuit__wel] = 1 - pbp__cesdw[yuit__wel] / qap__aseq[yuit__wel]
    stndi__goazs[ywcsb__qkgq & ~dpnz__eulpb] = 0.0
    if isinstance(multioutput, str):
        if multioutput == 'raw_values':
            return stndi__goazs
        elif multioutput == 'uniform_average':
            pku__yfgn = None
        elif multioutput == 'variance_weighted':
            pku__yfgn = qap__aseq
            if not np.any(dpnz__eulpb):
                if not np.any(ywcsb__qkgq):
                    return np.array([1.0])
                else:
                    return np.array([0.0])
    else:
        pku__yfgn = multioutput
    return np.array([np.average(stndi__goazs, weights=pku__yfgn)])


@overload(sklearn.metrics.r2_score, no_unliteral=True)
def overload_r2_score(y_true, y_pred, sample_weight=None, multioutput=
    'uniform_average', _is_data_distributed=False):
    check_sklearn_version()
    if is_overload_constant_str(multioutput) and get_overload_const_str(
        multioutput) not in ['raw_values', 'uniform_average',
        'variance_weighted']:
        raise BodoError(
            f"Unsupported argument {get_overload_const_str(multioutput)} specified for 'multioutput'"
            )
    if is_overload_constant_str(multioutput) and get_overload_const_str(
        multioutput) == 'raw_values':
        if is_overload_none(sample_weight):

            def _r2_score_impl(y_true, y_pred, sample_weight=None,
                multioutput='uniform_average', _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                with numba.objmode(score='float64[:]'):
                    if _is_data_distributed:
                        score = r2_score_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput)
                    else:
                        score = sklearn.metrics.r2_score(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput)
                return score
            return _r2_score_impl
        else:

            def _r2_score_impl(y_true, y_pred, sample_weight=None,
                multioutput='uniform_average', _is_data_distributed=False):
                y_true = bodo.utils.conversion.coerce_to_array(y_true)
                y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
                sample_weight = bodo.utils.conversion.coerce_to_array(
                    sample_weight)
                with numba.objmode(score='float64[:]'):
                    if _is_data_distributed:
                        score = r2_score_dist_helper(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput)
                    else:
                        score = sklearn.metrics.r2_score(y_true, y_pred,
                            sample_weight=sample_weight, multioutput=
                            multioutput)
                return score
            return _r2_score_impl
    elif is_overload_none(sample_weight):

        def _r2_score_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            with numba.objmode(score='float64'):
                if _is_data_distributed:
                    score = r2_score_dist_helper(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=multioutput)
                    score = score[0]
                else:
                    score = sklearn.metrics.r2_score(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=multioutput)
            return score
        return _r2_score_impl
    else:

        def _r2_score_impl(y_true, y_pred, sample_weight=None, multioutput=
            'uniform_average', _is_data_distributed=False):
            y_true = bodo.utils.conversion.coerce_to_array(y_true)
            y_pred = bodo.utils.conversion.coerce_to_array(y_pred)
            sample_weight = bodo.utils.conversion.coerce_to_array(sample_weight
                )
            with numba.objmode(score='float64'):
                if _is_data_distributed:
                    score = r2_score_dist_helper(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=multioutput)
                    score = score[0]
                else:
                    score = sklearn.metrics.r2_score(y_true, y_pred,
                        sample_weight=sample_weight, multioutput=multioutput)
            return score
        return _r2_score_impl


def confusion_matrix_dist_helper(y_true, y_pred, labels=None, sample_weight
    =None, normalize=None):
    if normalize not in ['true', 'pred', 'all', None]:
        raise ValueError(
            "normalize must be one of {'true', 'pred', 'all', None}")
    axfge__qisy = MPI.COMM_WORLD
    try:
        pmur__qnad = sklearn.metrics.confusion_matrix(y_true, y_pred,
            labels=labels, sample_weight=sample_weight, normalize=None)
    except ValueError as joped__ynpy:
        pmur__qnad = joped__ynpy
    hulpe__koq = isinstance(pmur__qnad, ValueError
        ) and 'At least one label specified must be in y_true' in pmur__qnad.args[
        0]
    hge__yzld = axfge__qisy.allreduce(hulpe__koq, op=MPI.LAND)
    if hge__yzld:
        raise pmur__qnad
    elif hulpe__koq:
        dtype = np.int64
        if sample_weight is not None and sample_weight.dtype.kind not in {'i',
            'u', 'b'}:
            dtype = np.float64
        hjli__ipete = np.zeros((labels.size, labels.size), dtype=dtype)
    else:
        hjli__ipete = pmur__qnad
    feje__btove = np.zeros_like(hjli__ipete)
    axfge__qisy.Allreduce(hjli__ipete, feje__btove)
    with np.errstate(all='ignore'):
        if normalize == 'true':
            feje__btove = feje__btove / feje__btove.sum(axis=1, keepdims=True)
        elif normalize == 'pred':
            feje__btove = feje__btove / feje__btove.sum(axis=0, keepdims=True)
        elif normalize == 'all':
            feje__btove = feje__btove / feje__btove.sum()
        feje__btove = np.nan_to_num(feje__btove)
    return feje__btove


@overload(sklearn.metrics.confusion_matrix, no_unliteral=True)
def overload_confusion_matrix(y_true, y_pred, labels=None, sample_weight=
    None, normalize=None, _is_data_distributed=False):
    check_sklearn_version()
    eqb__zycml = 'def _confusion_matrix_impl(\n'
    eqb__zycml += '    y_true, y_pred, labels=None,\n'
    eqb__zycml += '    sample_weight=None, normalize=None,\n'
    eqb__zycml += '    _is_data_distributed=False,\n'
    eqb__zycml += '):\n'
    eqb__zycml += (
        '    y_true = bodo.utils.conversion.coerce_to_array(y_true)\n')
    eqb__zycml += (
        '    y_pred = bodo.utils.conversion.coerce_to_array(y_pred)\n')
    kkcw__vjec = 'int64[:,:]', 'np.int64'
    if not is_overload_none(normalize):
        kkcw__vjec = 'float64[:,:]', 'np.float64'
    if not is_overload_none(sample_weight):
        eqb__zycml += (
            '    sample_weight = bodo.utils.conversion.coerce_to_array(sample_weight)\n'
            )
        if numba.np.numpy_support.as_dtype(sample_weight.dtype).kind not in {
            'i', 'u', 'b'}:
            kkcw__vjec = 'float64[:,:]', 'np.float64'
    if not is_overload_none(labels):
        eqb__zycml += (
            '    labels = bodo.utils.conversion.coerce_to_array(labels)\n')
    elif is_overload_true(_is_data_distributed):
        eqb__zycml += (
            '    labels = bodo.libs.array_kernels.concat([y_true, y_pred])\n')
        eqb__zycml += (
            '    labels = bodo.libs.array_kernels.unique(labels, parallel=True)\n'
            )
        eqb__zycml += '    labels = bodo.allgatherv(labels, False)\n'
        eqb__zycml += """    labels = bodo.libs.array_kernels.sort(labels, ascending=True, inplace=False)
"""
    eqb__zycml += f"    with numba.objmode(cm='{kkcw__vjec[0]}'):\n"
    if is_overload_false(_is_data_distributed):
        eqb__zycml += '      cm = sklearn.metrics.confusion_matrix(\n'
    else:
        eqb__zycml += '      cm = confusion_matrix_dist_helper(\n'
    eqb__zycml += '        y_true, y_pred, labels=labels,\n'
    eqb__zycml += '        sample_weight=sample_weight, normalize=normalize,\n'
    eqb__zycml += f'      ).astype({kkcw__vjec[1]})\n'
    eqb__zycml += '    return cm\n'
    www__jks = {}
    exec(eqb__zycml, globals(), www__jks)
    shak__ltf = www__jks['_confusion_matrix_impl']
    return shak__ltf


class BodoSGDRegressorType(types.Opaque):

    def __init__(self):
        super(BodoSGDRegressorType, self).__init__(name='BodoSGDRegressorType')


sgd_regressor_type = BodoSGDRegressorType()
types.sgd_regressor_type = sgd_regressor_type
register_model(BodoSGDRegressorType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.SGDRegressor)
def typeof_sgd_regressor(val, c):
    return sgd_regressor_type


@box(BodoSGDRegressorType)
def box_sgd_regressor(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoSGDRegressorType)
def unbox_sgd_regressor(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.SGDRegressor, no_unliteral=True)
def sklearn_linear_model_SGDRegressor_overload(loss='squared_loss', penalty
    ='l2', alpha=0.0001, l1_ratio=0.15, fit_intercept=True, max_iter=1000,
    tol=0.001, shuffle=True, verbose=0, epsilon=0.1, random_state=None,
    learning_rate='invscaling', eta0=0.01, power_t=0.25, early_stopping=
    False, validation_fraction=0.1, n_iter_no_change=5, warm_start=False,
    average=False):
    check_sklearn_version()

    def _sklearn_linear_model_SGDRegressor_impl(loss='squared_loss',
        penalty='l2', alpha=0.0001, l1_ratio=0.15, fit_intercept=True,
        max_iter=1000, tol=0.001, shuffle=True, verbose=0, epsilon=0.1,
        random_state=None, learning_rate='invscaling', eta0=0.01, power_t=
        0.25, early_stopping=False, validation_fraction=0.1,
        n_iter_no_change=5, warm_start=False, average=False):
        with numba.objmode(m='sgd_regressor_type'):
            m = sklearn.linear_model.SGDRegressor(loss=loss, penalty=
                penalty, alpha=alpha, l1_ratio=l1_ratio, fit_intercept=
                fit_intercept, max_iter=max_iter, tol=tol, shuffle=shuffle,
                verbose=verbose, epsilon=epsilon, random_state=random_state,
                learning_rate=learning_rate, eta0=eta0, power_t=power_t,
                early_stopping=early_stopping, validation_fraction=
                validation_fraction, n_iter_no_change=n_iter_no_change,
                warm_start=warm_start, average=average)
        return m
    return _sklearn_linear_model_SGDRegressor_impl


@overload_method(BodoSGDRegressorType, 'fit', no_unliteral=True)
def overload_sgdr_model_fit(m, X, y, _is_data_distributed=False):
    check_sklearn_version()

    def _model_sgdr_fit_impl(m, X, y, _is_data_distributed=False):
        with numba.objmode(m='sgd_regressor_type'):
            m = fit_sgd(m, X, y, _is_data_distributed)
        bodo.barrier()
        return m
    return _model_sgdr_fit_impl


@overload_method(BodoSGDRegressorType, 'predict', no_unliteral=True)
def overload_sgdr_model_predict(m, X):
    return parallel_predict_regression(m, X)


@overload_method(BodoSGDRegressorType, 'score', no_unliteral=True)
def overload_sgdr_model_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


class BodoSGDClassifierType(types.Opaque):

    def __init__(self):
        super(BodoSGDClassifierType, self).__init__(name=
            'BodoSGDClassifierType')


sgd_classifier_type = BodoSGDClassifierType()
types.sgd_classifier_type = sgd_classifier_type
register_model(BodoSGDClassifierType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.SGDClassifier)
def typeof_sgd_classifier(val, c):
    return sgd_classifier_type


@box(BodoSGDClassifierType)
def box_sgd_classifier(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoSGDClassifierType)
def unbox_sgd_classifier(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.SGDClassifier, no_unliteral=True)
def sklearn_linear_model_SGDClassifier_overload(loss='hinge', penalty='l2',
    alpha=0.0001, l1_ratio=0.15, fit_intercept=True, max_iter=1000, tol=
    0.001, shuffle=True, verbose=0, epsilon=0.1, n_jobs=None, random_state=
    None, learning_rate='optimal', eta0=0.0, power_t=0.5, early_stopping=
    False, validation_fraction=0.1, n_iter_no_change=5, class_weight=None,
    warm_start=False, average=False):
    check_sklearn_version()

    def _sklearn_linear_model_SGDClassifier_impl(loss='hinge', penalty='l2',
        alpha=0.0001, l1_ratio=0.15, fit_intercept=True, max_iter=1000, tol
        =0.001, shuffle=True, verbose=0, epsilon=0.1, n_jobs=None,
        random_state=None, learning_rate='optimal', eta0=0.0, power_t=0.5,
        early_stopping=False, validation_fraction=0.1, n_iter_no_change=5,
        class_weight=None, warm_start=False, average=False):
        with numba.objmode(m='sgd_classifier_type'):
            m = sklearn.linear_model.SGDClassifier(loss=loss, penalty=
                penalty, alpha=alpha, l1_ratio=l1_ratio, fit_intercept=
                fit_intercept, max_iter=max_iter, tol=tol, shuffle=shuffle,
                verbose=verbose, epsilon=epsilon, n_jobs=n_jobs,
                random_state=random_state, learning_rate=learning_rate,
                eta0=eta0, power_t=power_t, early_stopping=early_stopping,
                validation_fraction=validation_fraction, n_iter_no_change=
                n_iter_no_change, class_weight=class_weight, warm_start=
                warm_start, average=average)
        return m
    return _sklearn_linear_model_SGDClassifier_impl


def fit_sgd(m, X, y, y_classes=None, _is_data_distributed=False):
    axfge__qisy = MPI.COMM_WORLD
    vtaue__ffznc = axfge__qisy.allreduce(len(X), op=MPI.SUM)
    tepi__acy = len(X) / vtaue__ffznc
    axbti__cvf = axfge__qisy.Get_size()
    m.n_jobs = 1
    m.early_stopping = False
    ifqdm__kty = np.inf
    ujco__rqecc = 0
    if m.loss == 'hinge':
        amm__ben = hinge_loss
    elif m.loss == 'log':
        amm__ben = log_loss
    elif m.loss == 'squared_loss':
        amm__ben = mean_squared_error
    else:
        raise ValueError('loss {} not supported'.format(m.loss))
    qmloz__zvtc = False
    if isinstance(m, sklearn.linear_model.SGDRegressor):
        qmloz__zvtc = True
    for cxxc__ztxco in range(m.max_iter):
        if qmloz__zvtc:
            m.partial_fit(X, y)
        else:
            m.partial_fit(X, y, classes=y_classes)
        m.coef_ = m.coef_ * tepi__acy
        m.coef_ = axfge__qisy.allreduce(m.coef_, op=MPI.SUM)
        m.intercept_ = m.intercept_ * tepi__acy
        m.intercept_ = axfge__qisy.allreduce(m.intercept_, op=MPI.SUM)
        if qmloz__zvtc:
            y_pred = m.predict(X)
            lwg__hnu = amm__ben(y, y_pred)
        else:
            y_pred = m.decision_function(X)
            lwg__hnu = amm__ben(y, y_pred, labels=y_classes)
        ogg__npi = axfge__qisy.allreduce(lwg__hnu, op=MPI.SUM)
        lwg__hnu = ogg__npi / axbti__cvf
        if m.tol > np.NINF and lwg__hnu > ifqdm__kty - m.tol * vtaue__ffznc:
            ujco__rqecc += 1
        else:
            ujco__rqecc = 0
        if lwg__hnu < ifqdm__kty:
            ifqdm__kty = lwg__hnu
        if ujco__rqecc >= m.n_iter_no_change:
            break
    return m


@overload_method(BodoSGDClassifierType, 'fit', no_unliteral=True)
def overload_sgdc_model_fit(m, X, y, _is_data_distributed=False):
    check_sklearn_version()
    """
    Provide implementations for the fit function.
    In case input is replicated, we simply call sklearn,
    else we use partial_fit on each rank then use we re-compute the attributes using MPI operations.
    """
    if is_overload_true(_is_data_distributed):

        def _model_sgdc_fit_impl(m, X, y, _is_data_distributed=False):
            y_classes = bodo.libs.array_kernels.unique(y, parallel=True)
            y_classes = bodo.allgatherv(y_classes, False)
            with numba.objmode(m='sgd_classifier_type'):
                m = fit_sgd(m, X, y, y_classes, _is_data_distributed)
            return m
        return _model_sgdc_fit_impl
    else:

        def _model_sgdc_fit_impl(m, X, y, _is_data_distributed=False):
            with numba.objmode(m='sgd_classifier_type'):
                m = m.fit(X, y)
            return m
        return _model_sgdc_fit_impl


@overload_method(BodoSGDClassifierType, 'predict', no_unliteral=True)
def overload_sgdc_model_predict(m, X):
    return parallel_predict(m, X)


@overload_method(BodoSGDClassifierType, 'predict_proba', no_unliteral=True)
def overload_sgdc_model_predict_proba(m, X):
    return parallel_predict_proba(m, X)


@overload_method(BodoSGDClassifierType, 'predict_log_proba', no_unliteral=True)
def overload_sgdc_model_predict_log_proba(m, X):
    return parallel_predict_log_proba(m, X)


@overload_method(BodoSGDClassifierType, 'score', no_unliteral=True)
def overload_sgdc_model_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


@overload_attribute(BodoSGDClassifierType, 'coef_')
def get_sgdc_coef(m):

    def impl(m):
        with numba.objmode(result='float64[:,:]'):
            result = m.coef_
        return result
    return impl


class BodoKMeansClusteringType(types.Opaque):

    def __init__(self):
        super(BodoKMeansClusteringType, self).__init__(name=
            'BodoKMeansClusteringType')


kmeans_clustering_type = BodoKMeansClusteringType()
types.kmeans_clustering_type = kmeans_clustering_type
register_model(BodoKMeansClusteringType)(models.OpaqueModel)


@typeof_impl.register(sklearn.cluster.KMeans)
def typeof_kmeans_clustering(val, c):
    return kmeans_clustering_type


@box(BodoKMeansClusteringType)
def box_kmeans_clustering(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoKMeansClusteringType)
def unbox_kmeans_clustering(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.cluster.KMeans, no_unliteral=True)
def sklearn_cluster_kmeans_overload(n_clusters=8, init='k-means++', n_init=
    10, max_iter=300, tol=0.0001, precompute_distances='deprecated',
    verbose=0, random_state=None, copy_x=True, n_jobs='deprecated',
    algorithm='auto'):
    check_sklearn_version()

    def _sklearn_cluster_kmeans_impl(n_clusters=8, init='k-means++', n_init
        =10, max_iter=300, tol=0.0001, precompute_distances='deprecated',
        verbose=0, random_state=None, copy_x=True, n_jobs='deprecated',
        algorithm='auto'):
        with numba.objmode(m='kmeans_clustering_type'):
            m = sklearn.cluster.KMeans(n_clusters=n_clusters, init=init,
                n_init=n_init, max_iter=max_iter, tol=tol,
                precompute_distances=precompute_distances, verbose=verbose,
                random_state=random_state, copy_x=copy_x, n_jobs=n_jobs,
                algorithm=algorithm)
        return m
    return _sklearn_cluster_kmeans_impl


def kmeans_fit_helper(m, len_X, all_X, all_sample_weight, _is_data_distributed
    ):
    axfge__qisy = MPI.COMM_WORLD
    ysxhi__iakl = axfge__qisy.Get_rank()
    wkpse__znnw = MPI.Get_processor_name()
    poby__apvvl = get_host_ranks()
    nps__kul = m.n_jobs if hasattr(m, 'n_jobs') else None
    pdy__jsxyl = m._n_threads if hasattr(m, '_n_threads') else None
    m.n_jobs = len(poby__apvvl[wkpse__znnw])
    m._n_threads = len(poby__apvvl[wkpse__znnw])
    if ysxhi__iakl == 0:
        m.fit(X=all_X, y=None, sample_weight=all_sample_weight)
    if ysxhi__iakl == 0:
        axfge__qisy.bcast(m.cluster_centers_)
        axfge__qisy.bcast(m.inertia_)
        axfge__qisy.bcast(m.n_iter_)
    else:
        m.cluster_centers_ = axfge__qisy.bcast(None)
        m.inertia_ = axfge__qisy.bcast(None)
        m.n_iter_ = axfge__qisy.bcast(None)
    if _is_data_distributed:
        xqa__uxdjw = axfge__qisy.allgather(len_X)
        if ysxhi__iakl == 0:
            wrma__hne = np.empty(len(xqa__uxdjw) + 1, dtype=int)
            np.cumsum(xqa__uxdjw, out=wrma__hne[1:])
            wrma__hne[0] = 0
            pwz__xpgn = [m.labels_[wrma__hne[gnu__mfb]:wrma__hne[gnu__mfb +
                1]] for gnu__mfb in range(len(xqa__uxdjw))]
            ndyvn__xyjed = axfge__qisy.scatter(pwz__xpgn)
        else:
            ndyvn__xyjed = axfge__qisy.scatter(None)
        m.labels_ = ndyvn__xyjed
    elif ysxhi__iakl == 0:
        axfge__qisy.bcast(m.labels_)
    else:
        m.labels_ = axfge__qisy.bcast(None)
    m.n_jobs = nps__kul
    m._n_threads = pdy__jsxyl
    return m


@overload_method(BodoKMeansClusteringType, 'fit', no_unliteral=True)
def overload_kmeans_clustering_fit(m, X, y=None, sample_weight=None,
    _is_data_distributed=False):

    def _cluster_kmeans_fit_impl(m, X, y=None, sample_weight=None,
        _is_data_distributed=False):
        if _is_data_distributed:
            all_X = bodo.gatherv(X)
            if sample_weight is not None:
                all_sample_weight = bodo.gatherv(sample_weight)
            else:
                all_sample_weight = None
        else:
            all_X = X
            all_sample_weight = sample_weight
        with numba.objmode(m='kmeans_clustering_type'):
            m = kmeans_fit_helper(m, len(X), all_X, all_sample_weight,
                _is_data_distributed)
        return m
    return _cluster_kmeans_fit_impl


def kmeans_predict_helper(m, X, sample_weight):
    pdy__jsxyl = m._n_threads if hasattr(m, '_n_threads') else None
    nps__kul = m.n_jobs if hasattr(m, 'n_jobs') else None
    m._n_threads = 1
    m.n_jobs = 1
    if len(X) == 0:
        preds = np.empty(0, dtype=np.int64)
    else:
        preds = m.predict(X, sample_weight).astype(np.int64).flatten()
    m._n_threads = pdy__jsxyl
    m.n_jobs = nps__kul
    return preds


@overload_method(BodoKMeansClusteringType, 'predict', no_unliteral=True)
def overload_kmeans_clustering_predict(m, X, sample_weight=None):

    def _cluster_kmeans_predict(m, X, sample_weight=None):
        with numba.objmode(preds='int64[:]'):
            preds = kmeans_predict_helper(m, X, sample_weight)
        return preds
    return _cluster_kmeans_predict


@overload_method(BodoKMeansClusteringType, 'score', no_unliteral=True)
def overload_kmeans_clustering_score(m, X, y=None, sample_weight=None,
    _is_data_distributed=False):

    def _cluster_kmeans_score(m, X, y=None, sample_weight=None,
        _is_data_distributed=False):
        with numba.objmode(result='float64'):
            pdy__jsxyl = m._n_threads if hasattr(m, '_n_threads') else None
            nps__kul = m.n_jobs if hasattr(m, 'n_jobs') else None
            m._n_threads = 1
            m.n_jobs = 1
            if len(X) == 0:
                result = 0
            else:
                result = m.score(X, y=y, sample_weight=sample_weight)
            if _is_data_distributed:
                axfge__qisy = MPI.COMM_WORLD
                result = axfge__qisy.allreduce(result, op=MPI.SUM)
            m._n_threads = pdy__jsxyl
            m.n_jobs = nps__kul
        return result
    return _cluster_kmeans_score


@overload_method(BodoKMeansClusteringType, 'transform', no_unliteral=True)
def overload_kmeans_clustering_transform(m, X):

    def _cluster_kmeans_transform(m, X):
        with numba.objmode(X_new='float64[:,:]'):
            pdy__jsxyl = m._n_threads if hasattr(m, '_n_threads') else None
            nps__kul = m.n_jobs if hasattr(m, 'n_jobs') else None
            m._n_threads = 1
            m.n_jobs = 1
            if len(X) == 0:
                X_new = np.empty((0, m.n_clusters), dtype=np.int64)
            else:
                X_new = m.transform(X).astype(np.float64)
            m._n_threads = pdy__jsxyl
            m.n_jobs = nps__kul
        return X_new
    return _cluster_kmeans_transform


class BodoMultinomialNBType(types.Opaque):

    def __init__(self):
        super(BodoMultinomialNBType, self).__init__(name=
            'BodoMultinomialNBType')


multinomial_nb_type = BodoMultinomialNBType()
types.multinomial_nb_type = multinomial_nb_type
register_model(BodoMultinomialNBType)(models.OpaqueModel)


@typeof_impl.register(sklearn.naive_bayes.MultinomialNB)
def typeof_multinomial_nb(val, c):
    return multinomial_nb_type


@box(BodoMultinomialNBType)
def box_multinomial_nb(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoMultinomialNBType)
def unbox_multinomial_nb(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.naive_bayes.MultinomialNB, no_unliteral=True)
def sklearn_naive_bayes_multinomialnb_overload(alpha=1.0, fit_prior=True,
    class_prior=None):
    check_sklearn_version()

    def _sklearn_naive_bayes_multinomialnb_impl(alpha=1.0, fit_prior=True,
        class_prior=None):
        with numba.objmode(m='multinomial_nb_type'):
            m = sklearn.naive_bayes.MultinomialNB(alpha=alpha, fit_prior=
                fit_prior, class_prior=class_prior)
        return m
    return _sklearn_naive_bayes_multinomialnb_impl


@overload_method(BodoMultinomialNBType, 'fit', no_unliteral=True)
def overload_multinomial_nb_model_fit(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    if is_overload_false(_is_data_distributed):

        def _naive_bayes_multinomial_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight)
            return m
        return _naive_bayes_multinomial_impl
    else:
        eqb__zycml = 'def _model_multinomial_nb_fit_impl(\n'
        eqb__zycml += (
            '    m, X, y, sample_weight=None, _is_data_distributed=False\n')
        eqb__zycml += '):  # pragma: no cover\n'
        eqb__zycml += '    y = bodo.utils.conversion.coerce_to_ndarray(y)\n'
        if isinstance(X, DataFrameType):
            eqb__zycml += '    X = X.to_numpy()\n'
        else:
            eqb__zycml += (
                '    X = bodo.utils.conversion.coerce_to_ndarray(X)\n')
        eqb__zycml += '    my_rank = bodo.get_rank()\n'
        eqb__zycml += '    nranks = bodo.get_size()\n'
        eqb__zycml += '    total_cols = X.shape[1]\n'
        eqb__zycml += '    for i in range(nranks):\n'
        eqb__zycml += """        start = bodo.libs.distributed_api.get_start(total_cols, nranks, i)
"""
        eqb__zycml += (
            '        end = bodo.libs.distributed_api.get_end(total_cols, nranks, i)\n'
            )
        eqb__zycml += '        if i == my_rank:\n'
        eqb__zycml += (
            '            X_train = bodo.gatherv(X[:, start:end:1], root=i)\n')
        eqb__zycml += '        else:\n'
        eqb__zycml += '            bodo.gatherv(X[:, start:end:1], root=i)\n'
        eqb__zycml += '    y_train = bodo.allgatherv(y, False)\n'
        eqb__zycml += '    with numba.objmode(m="multinomial_nb_type"):\n'
        eqb__zycml += '        m = fit_multinomial_nb(\n'
        eqb__zycml += """            m, X_train, y_train, sample_weight, total_cols, _is_data_distributed
"""
        eqb__zycml += '        )\n'
        eqb__zycml += '    bodo.barrier()\n'
        eqb__zycml += '    return m\n'
        www__jks = {}
        exec(eqb__zycml, globals(), www__jks)
        evd__ete = www__jks['_model_multinomial_nb_fit_impl']
        return evd__ete


def fit_multinomial_nb(m, X_train, y_train, sample_weight=None, total_cols=
    0, _is_data_distributed=False):
    m._check_X_y(X_train, y_train)
    cxxc__ztxco, n_features = X_train.shape
    m.n_features_ = n_features
    gmh__uwt = LabelBinarizer()
    hspzw__jfuq = gmh__uwt.fit_transform(y_train)
    m.classes_ = gmh__uwt.classes_
    if hspzw__jfuq.shape[1] == 1:
        hspzw__jfuq = np.concatenate((1 - hspzw__jfuq, hspzw__jfuq), axis=1)
    if sample_weight is not None:
        hspzw__jfuq = hspzw__jfuq.astype(np.float64, copy=False)
        sample_weight = _check_sample_weight(sample_weight, X_train)
        sample_weight = np.atleast_2d(sample_weight)
        hspzw__jfuq *= sample_weight.T
    class_prior = m.class_prior
    quay__pmb = hspzw__jfuq.shape[1]
    m._init_counters(quay__pmb, n_features)
    m._count(X_train.astype('float64'), hspzw__jfuq)
    alpha = m._check_alpha()
    m._update_class_log_prior(class_prior=class_prior)
    zicbt__pnrw = m.feature_count_ + alpha
    gdvv__jqb = zicbt__pnrw.sum(axis=1)
    axfge__qisy = MPI.COMM_WORLD
    axbti__cvf = axfge__qisy.Get_size()
    sdd__zrbpf = np.zeros(quay__pmb)
    axfge__qisy.Allreduce(gdvv__jqb, sdd__zrbpf, op=MPI.SUM)
    zzcbx__dnt = np.log(zicbt__pnrw) - np.log(sdd__zrbpf.reshape(-1, 1))
    cnp__nps = zzcbx__dnt.T.reshape(n_features * quay__pmb)
    iax__lev = np.ones(axbti__cvf) * (total_cols // axbti__cvf)
    wjtim__hsy = total_cols % axbti__cvf
    for zwy__ofoel in range(wjtim__hsy):
        iax__lev[zwy__ofoel] += 1
    iax__lev *= quay__pmb
    zfr__ttvg = np.zeros(axbti__cvf, dtype=np.int32)
    zfr__ttvg[1:] = np.cumsum(iax__lev)[:-1]
    gmt__opj = np.zeros((total_cols, quay__pmb), dtype=np.float64)
    axfge__qisy.Allgatherv(cnp__nps, [gmt__opj, iax__lev, zfr__ttvg, MPI.
        DOUBLE_PRECISION])
    m.feature_log_prob_ = gmt__opj.T
    m.n_features_ = m.feature_log_prob_.shape[1]
    return m


@overload_method(BodoMultinomialNBType, 'predict', no_unliteral=True)
def overload_multinomial_nb_model_predict(m, X):
    return parallel_predict(m, X)


@overload_method(BodoMultinomialNBType, 'score', no_unliteral=True)
def overload_multinomial_nb_model_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


class BodoLogisticRegressionType(types.Opaque):

    def __init__(self):
        super(BodoLogisticRegressionType, self).__init__(name=
            'BodoLogisticRegressionType')


logistic_regression_type = BodoLogisticRegressionType()
types.logistic_regression_type = logistic_regression_type
register_model(BodoLogisticRegressionType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.LogisticRegression)
def typeof_logistic_regression(val, c):
    return logistic_regression_type


@box(BodoLogisticRegressionType)
def box_logistic_regression(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoLogisticRegressionType)
def unbox_logistic_regression(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.LogisticRegression, no_unliteral=True)
def sklearn_linear_model_logistic_regression_overload(penalty='l2', dual=
    False, tol=0.0001, C=1.0, fit_intercept=True, intercept_scaling=1,
    class_weight=None, random_state=None, solver='lbfgs', max_iter=100,
    multi_class='auto', verbose=0, warm_start=False, n_jobs=None, l1_ratio=None
    ):
    check_sklearn_version()

    def _sklearn_linear_model_logistic_regression_impl(penalty='l2', dual=
        False, tol=0.0001, C=1.0, fit_intercept=True, intercept_scaling=1,
        class_weight=None, random_state=None, solver='lbfgs', max_iter=100,
        multi_class='auto', verbose=0, warm_start=False, n_jobs=None,
        l1_ratio=None):
        with numba.objmode(m='logistic_regression_type'):
            m = sklearn.linear_model.LogisticRegression(penalty=penalty,
                dual=dual, tol=tol, C=C, fit_intercept=fit_intercept,
                intercept_scaling=intercept_scaling, class_weight=
                class_weight, random_state=random_state, solver=solver,
                max_iter=max_iter, multi_class=multi_class, verbose=verbose,
                warm_start=warm_start, n_jobs=n_jobs, l1_ratio=l1_ratio)
        return m
    return _sklearn_linear_model_logistic_regression_impl


@register_jitable
def _raise_SGD_warning(sgd_name):
    with numba.objmode:
        warnings.warn(
            f'Data is distributed so Bodo will fit model with SGD solver optimization ({sgd_name})'
            , BodoWarning)


@overload_method(BodoLogisticRegressionType, 'fit', no_unliteral=True)
def overload_logistic_regression_fit(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    if is_overload_false(_is_data_distributed):

        def _logistic_regression_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight)
            return m
        return _logistic_regression_fit_impl
    else:

        def _sgdc_logistic_regression_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            if bodo.get_rank() == 0:
                _raise_SGD_warning('SGDClassifier')
            with numba.objmode(clf='sgd_classifier_type'):
                if m.l1_ratio is None:
                    l1_ratio = 0.15
                else:
                    l1_ratio = m.l1_ratio
                clf = sklearn.linear_model.SGDClassifier(loss='log',
                    penalty=m.penalty, tol=m.tol, fit_intercept=m.
                    fit_intercept, class_weight=m.class_weight,
                    random_state=m.random_state, max_iter=m.max_iter,
                    verbose=m.verbose, warm_start=m.warm_start, n_jobs=m.
                    n_jobs, l1_ratio=l1_ratio)
            clf.fit(X, y, _is_data_distributed=True)
            with numba.objmode():
                m.coef_ = clf.coef_
                m.intercept_ = clf.intercept_
                m.n_iter_ = clf.n_iter_
                m.classes_ = clf.classes_
            return m
        return _sgdc_logistic_regression_fit_impl


@overload_method(BodoLogisticRegressionType, 'predict', no_unliteral=True)
def overload_logistic_regression_predict(m, X):
    return parallel_predict(m, X)


@overload_method(BodoLogisticRegressionType, 'predict_proba', no_unliteral=True
    )
def overload_logistic_regression_predict_proba(m, X):
    return parallel_predict_proba(m, X)


@overload_method(BodoLogisticRegressionType, 'predict_log_proba',
    no_unliteral=True)
def overload_logistic_regression_predict_log_proba(m, X):
    return parallel_predict_log_proba(m, X)


@overload_method(BodoLogisticRegressionType, 'score', no_unliteral=True)
def overload_logistic_regression_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


@overload_attribute(BodoLogisticRegressionType, 'coef_')
def get_logisticR_coef(m):

    def impl(m):
        with numba.objmode(result='float64[:,:]'):
            result = m.coef_
        return result
    return impl


class BodoLinearRegressionType(types.Opaque):

    def __init__(self):
        super(BodoLinearRegressionType, self).__init__(name=
            'BodoLinearRegressionType')


linear_regression_type = BodoLinearRegressionType()
types.linear_regression_type = linear_regression_type
register_model(BodoLinearRegressionType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.LinearRegression)
def typeof_linear_regression(val, c):
    return linear_regression_type


@box(BodoLinearRegressionType)
def box_linear_regression(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoLinearRegressionType)
def unbox_linear_regression(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.LinearRegression, no_unliteral=True)
def sklearn_linear_model_linear_regression_overload(fit_intercept=True,
    normalize=False, copy_X=True, n_jobs=None):
    check_sklearn_version()

    def _sklearn_linear_model_linear_regression_impl(fit_intercept=True,
        normalize=False, copy_X=True, n_jobs=None):
        with numba.objmode(m='linear_regression_type'):
            m = sklearn.linear_model.LinearRegression(fit_intercept=
                fit_intercept, normalize=normalize, copy_X=copy_X, n_jobs=
                n_jobs)
        return m
    return _sklearn_linear_model_linear_regression_impl


@overload_method(BodoLinearRegressionType, 'fit', no_unliteral=True)
def overload_linear_regression_fit(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    if is_overload_false(_is_data_distributed):

        def _linear_regression_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight)
            return m
        return _linear_regression_fit_impl
    else:

        def _sgdc_linear_regression_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            if bodo.get_rank() == 0:
                _raise_SGD_warning('SGDRegressor')
            with numba.objmode(clf='sgd_regressor_type'):
                clf = sklearn.linear_model.SGDRegressor(loss='squared_loss',
                    penalty=None, fit_intercept=m.fit_intercept)
            clf.fit(X, y, _is_data_distributed=True)
            with numba.objmode():
                m.coef_ = clf.coef_
                m.intercept_ = clf.intercept_
            return m
        return _sgdc_linear_regression_fit_impl


@overload_method(BodoLinearRegressionType, 'predict', no_unliteral=True)
def overload_linear_regression_predict(m, X):
    return parallel_predict_regression(m, X)


@overload_method(BodoLinearRegressionType, 'score', no_unliteral=True)
def overload_linear_regression_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


@overload_attribute(BodoLinearRegressionType, 'coef_')
def get_lr_coef(m):

    def impl(m):
        with numba.objmode(result='float64[:]'):
            result = m.coef_
        return result
    return impl


class BodoLassoType(types.Opaque):

    def __init__(self):
        super(BodoLassoType, self).__init__(name='BodoLassoType')


lasso_type = BodoLassoType()
types.lasso_type = lasso_type
register_model(BodoLassoType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.Lasso)
def typeof_lasso(val, c):
    return lasso_type


@box(BodoLassoType)
def box_lasso(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoLassoType)
def unbox_lasso(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.Lasso, no_unliteral=True)
def sklearn_linear_model_lasso_overload(alpha=1.0, fit_intercept=True,
    normalize=False, precompute=False, copy_X=True, max_iter=1000, tol=
    0.0001, warm_start=False, positive=False, random_state=None, selection=
    'cyclic'):
    check_sklearn_version()

    def _sklearn_linear_model_lasso_impl(alpha=1.0, fit_intercept=True,
        normalize=False, precompute=False, copy_X=True, max_iter=1000, tol=
        0.0001, warm_start=False, positive=False, random_state=None,
        selection='cyclic'):
        with numba.objmode(m='lasso_type'):
            m = sklearn.linear_model.Lasso(alpha=alpha, fit_intercept=
                fit_intercept, normalize=normalize, precompute=precompute,
                copy_X=copy_X, max_iter=max_iter, tol=tol, warm_start=
                warm_start, positive=positive, random_state=random_state,
                selection=selection)
        return m
    return _sklearn_linear_model_lasso_impl


@overload_method(BodoLassoType, 'fit', no_unliteral=True)
def overload_lasso_fit(m, X, y, sample_weight=None, check_input=True,
    _is_data_distributed=False):
    if is_overload_false(_is_data_distributed):

        def _lasso_fit_impl(m, X, y, sample_weight=None, check_input=True,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight, check_input)
            return m
        return _lasso_fit_impl
    else:

        def _sgdc_lasso_fit_impl(m, X, y, sample_weight=None, check_input=
            True, _is_data_distributed=False):
            if bodo.get_rank() == 0:
                _raise_SGD_warning('SGDRegressor')
            with numba.objmode(clf='sgd_regressor_type'):
                clf = sklearn.linear_model.SGDRegressor(loss='squared_loss',
                    penalty='l1', alpha=m.alpha, fit_intercept=m.
                    fit_intercept, max_iter=m.max_iter, tol=m.tol,
                    warm_start=m.warm_start, random_state=m.random_state)
            clf.fit(X, y, _is_data_distributed=True)
            with numba.objmode():
                m.coef_ = clf.coef_
                m.intercept_ = clf.intercept_
                m.n_iter_ = clf.n_iter_
            return m
        return _sgdc_lasso_fit_impl


@overload_method(BodoLassoType, 'predict', no_unliteral=True)
def overload_lass_predict(m, X):
    return parallel_predict_regression(m, X)


@overload_method(BodoLassoType, 'score', no_unliteral=True)
def overload_lasso_score(m, X, y, sample_weight=None, _is_data_distributed=
    False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


class BodoRidgeType(types.Opaque):

    def __init__(self):
        super(BodoRidgeType, self).__init__(name='BodoRidgeType')


ridge_type = BodoRidgeType()
types.ridge_type = ridge_type
register_model(BodoRidgeType)(models.OpaqueModel)


@typeof_impl.register(sklearn.linear_model.Ridge)
def typeof_ridge(val, c):
    return ridge_type


@box(BodoRidgeType)
def box_ridge(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoRidgeType)
def unbox_ridge(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.linear_model.Ridge, no_unliteral=True)
def sklearn_linear_model_ridge_overload(alpha=1.0, fit_intercept=True,
    normalize=False, copy_X=True, max_iter=None, tol=0.001, solver='auto',
    random_state=None):
    check_sklearn_version()

    def _sklearn_linear_model_ridge_impl(alpha=1.0, fit_intercept=True,
        normalize=False, copy_X=True, max_iter=None, tol=0.001, solver=
        'auto', random_state=None):
        with numba.objmode(m='ridge_type'):
            m = sklearn.linear_model.Ridge(alpha=alpha, fit_intercept=
                fit_intercept, normalize=normalize, copy_X=copy_X, max_iter
                =max_iter, tol=tol, solver=solver, random_state=random_state)
        return m
    return _sklearn_linear_model_ridge_impl


@overload_method(BodoRidgeType, 'fit', no_unliteral=True)
def overload_ridge_fit(m, X, y, sample_weight=None, _is_data_distributed=False
    ):
    if is_overload_false(_is_data_distributed):

        def _ridge_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight)
            return m
        return _ridge_fit_impl
    else:

        def _ridge_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            if bodo.get_rank() == 0:
                _raise_SGD_warning('SGDRegressor')
            with numba.objmode(clf='sgd_regressor_type'):
                if m.max_iter is None:
                    max_iter = 1000
                else:
                    max_iter = m.max_iter
                clf = sklearn.linear_model.SGDRegressor(loss='squared_loss',
                    penalty='l2', alpha=0.001, fit_intercept=m.
                    fit_intercept, max_iter=max_iter, tol=m.tol,
                    random_state=m.random_state)
            clf.fit(X, y, _is_data_distributed=True)
            with numba.objmode():
                m.coef_ = clf.coef_
                m.intercept_ = clf.intercept_
                m.n_iter_ = clf.n_iter_
            return m
        return _ridge_fit_impl


@overload_method(BodoRidgeType, 'predict', no_unliteral=True)
def overload_linear_regression_predict(m, X):
    return parallel_predict_regression(m, X)


@overload_method(BodoRidgeType, 'score', no_unliteral=True)
def overload_linear_regression_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


@overload_attribute(BodoRidgeType, 'coef_')
def get_ridge_coef(m):

    def impl(m):
        with numba.objmode(result='float64[:]'):
            result = m.coef_
        return result
    return impl


class BodoLinearSVCType(types.Opaque):

    def __init__(self):
        super(BodoLinearSVCType, self).__init__(name='BodoLinearSVCType')


linear_svc_type = BodoLinearSVCType()
types.linear_svc_type = linear_svc_type
register_model(BodoLinearSVCType)(models.OpaqueModel)


@typeof_impl.register(sklearn.svm.LinearSVC)
def typeof_linear_svc(val, c):
    return linear_svc_type


@box(BodoLinearSVCType)
def box_linear_svc(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoLinearSVCType)
def unbox_linear_svc(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.svm.LinearSVC, no_unliteral=True)
def sklearn_svm_linear_svc_overload(penalty='l2', loss='squared_hinge',
    dual=True, tol=0.0001, C=1.0, multi_class='ovr', fit_intercept=True,
    intercept_scaling=1, class_weight=None, verbose=0, random_state=None,
    max_iter=1000):
    check_sklearn_version()

    def _sklearn_svm_linear_svc_impl(penalty='l2', loss='squared_hinge',
        dual=True, tol=0.0001, C=1.0, multi_class='ovr', fit_intercept=True,
        intercept_scaling=1, class_weight=None, verbose=0, random_state=
        None, max_iter=1000):
        with numba.objmode(m='linear_svc_type'):
            m = sklearn.svm.LinearSVC(penalty=penalty, loss=loss, dual=dual,
                tol=tol, C=C, multi_class=multi_class, fit_intercept=
                fit_intercept, intercept_scaling=intercept_scaling,
                class_weight=class_weight, verbose=verbose, random_state=
                random_state, max_iter=max_iter)
        return m
    return _sklearn_svm_linear_svc_impl


@overload_method(BodoLinearSVCType, 'fit', no_unliteral=True)
def overload_linear_svc_fit(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    if is_overload_false(_is_data_distributed):

        def _svm_linear_svc_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            with numba.objmode():
                m.fit(X, y, sample_weight)
            return m
        return _svm_linear_svc_fit_impl
    else:

        def _svm_linear_svc_fit_impl(m, X, y, sample_weight=None,
            _is_data_distributed=False):
            if bodo.get_rank() == 0:
                _raise_SGD_warning('SGDClassifier')
            with numba.objmode(clf='sgd_classifier_type'):
                clf = sklearn.linear_model.SGDClassifier(loss='hinge',
                    penalty=m.penalty, tol=m.tol, fit_intercept=m.
                    fit_intercept, class_weight=m.class_weight,
                    random_state=m.random_state, max_iter=m.max_iter,
                    verbose=m.verbose)
            clf.fit(X, y, _is_data_distributed=True)
            with numba.objmode():
                m.coef_ = clf.coef_
                m.intercept_ = clf.intercept_
                m.n_iter_ = clf.n_iter_
                m.classes_ = clf.classes_
            return m
        return _svm_linear_svc_fit_impl


@overload_method(BodoLinearSVCType, 'predict', no_unliteral=True)
def overload_svm_linear_svc_predict(m, X):
    return parallel_predict(m, X)


@overload_method(BodoLinearSVCType, 'score', no_unliteral=True)
def overload_svm_linear_svc_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


class BodoPreprocessingStandardScalerType(types.Opaque):

    def __init__(self):
        super(BodoPreprocessingStandardScalerType, self).__init__(name=
            'BodoPreprocessingStandardScalerType')


preprocessing_standard_scaler_type = BodoPreprocessingStandardScalerType()
types.preprocessing_standard_scaler_type = preprocessing_standard_scaler_type
register_model(BodoPreprocessingStandardScalerType)(models.OpaqueModel)


@typeof_impl.register(sklearn.preprocessing.StandardScaler)
def typeof_preprocessing_standard_scaler(val, c):
    return preprocessing_standard_scaler_type


@box(BodoPreprocessingStandardScalerType)
def box_preprocessing_standard_scaler(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoPreprocessingStandardScalerType)
def unbox_preprocessing_standard_scaler(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.preprocessing.StandardScaler, no_unliteral=True)
def sklearn_preprocessing_standard_scaler_overload(copy=True, with_mean=
    True, with_std=True):
    check_sklearn_version()

    def _sklearn_preprocessing_standard_scaler_impl(copy=True, with_mean=
        True, with_std=True):
        with numba.objmode(m='preprocessing_standard_scaler_type'):
            m = sklearn.preprocessing.StandardScaler(copy=copy, with_mean=
                with_mean, with_std=with_std)
        return m
    return _sklearn_preprocessing_standard_scaler_impl


def sklearn_preprocessing_standard_scaler_fit_dist_helper(m, X):
    axfge__qisy = MPI.COMM_WORLD
    hjp__gpy = axfge__qisy.Get_size()
    nsvej__uijm = m.with_std
    sttwq__bed = m.with_mean
    m.with_std = False
    if nsvej__uijm:
        m.with_mean = True
    m = m.fit(X)
    m.with_std = nsvej__uijm
    m.with_mean = sttwq__bed
    if not isinstance(m.n_samples_seen_, numbers.Integral):
        qzlo__ifb = False
    else:
        qzlo__ifb = True
        m.n_samples_seen_ = np.repeat(m.n_samples_seen_, X.shape[1]).astype(np
            .int64, copy=False)
    iwx__gabs = np.zeros((hjp__gpy, *m.n_samples_seen_.shape), dtype=m.
        n_samples_seen_.dtype)
    axfge__qisy.Allgather(m.n_samples_seen_, iwx__gabs)
    xds__ozpc = np.sum(iwx__gabs, axis=0)
    m.n_samples_seen_ = xds__ozpc
    if m.with_mean or m.with_std:
        hir__lpy = np.zeros((hjp__gpy, *m.mean_.shape), dtype=m.mean_.dtype)
        axfge__qisy.Allgather(m.mean_, hir__lpy)
        hir__lpy[np.isnan(hir__lpy)] = 0
        crgi__icpdv = np.average(hir__lpy, axis=0, weights=iwx__gabs)
        m.mean_ = crgi__icpdv
    if m.with_std:
        pbq__jxz = sklearn_safe_accumulator_op(np.nansum, (X - crgi__icpdv) **
            2, axis=0) / xds__ozpc
        doacu__vkzmr = np.zeros_like(pbq__jxz)
        axfge__qisy.Allreduce(pbq__jxz, doacu__vkzmr, op=MPI.SUM)
        m.var_ = doacu__vkzmr
        m.scale_ = sklearn_handle_zeros_in_scale(np.sqrt(m.var_))
    qzlo__ifb = axfge__qisy.allreduce(qzlo__ifb, op=MPI.LAND)
    if qzlo__ifb:
        m.n_samples_seen_ = m.n_samples_seen_[0]
    return m


@overload_method(BodoPreprocessingStandardScalerType, 'fit', no_unliteral=True)
def overload_preprocessing_standard_scaler_fit(m, X, y=None,
    _is_data_distributed=False):

    def _preprocessing_standard_scaler_fit_impl(m, X, y=None,
        _is_data_distributed=False):
        with numba.objmode(m='preprocessing_standard_scaler_type'):
            if _is_data_distributed:
                m = sklearn_preprocessing_standard_scaler_fit_dist_helper(m, X)
            else:
                m = m.fit(X, y)
        return m
    return _preprocessing_standard_scaler_fit_impl


@overload_method(BodoPreprocessingStandardScalerType, 'transform',
    no_unliteral=True)
def overload_preprocessing_standard_scaler_transform(m, X, copy=None):

    def _preprocessing_standard_scaler_transform_impl(m, X, copy=None):
        with numba.objmode(transformed_X='float64[:,:]'):
            transformed_X = m.transform(X, copy=copy)
        return transformed_X
    return _preprocessing_standard_scaler_transform_impl


@overload_method(BodoPreprocessingStandardScalerType, 'inverse_transform',
    no_unliteral=True)
def overload_preprocessing_standard_scaler_inverse_transform(m, X, copy=None):

    def _preprocessing_standard_scaler_inverse_transform_impl(m, X, copy=None):
        with numba.objmode(inverse_transformed_X='float64[:,:]'):
            inverse_transformed_X = m.inverse_transform(X, copy=copy)
        return inverse_transformed_X
    return _preprocessing_standard_scaler_inverse_transform_impl


def get_data_slice_parallel(data, labels, len_train):
    myj__ovs = data[:len_train]
    aafc__ebxdu = data[len_train:]
    myj__ovs = bodo.rebalance(myj__ovs)
    aafc__ebxdu = bodo.rebalance(aafc__ebxdu)
    adp__asz = labels[:len_train]
    ovqc__qpgx = labels[len_train:]
    adp__asz = bodo.rebalance(adp__asz)
    ovqc__qpgx = bodo.rebalance(ovqc__qpgx)
    return myj__ovs, aafc__ebxdu, adp__asz, ovqc__qpgx


@numba.njit
def get_train_test_size(train_size, test_size):
    if train_size is None:
        train_size = -1.0
    if test_size is None:
        test_size = -1.0
    if train_size == -1.0 and test_size == -1.0:
        return 0.75, 0.25
    elif test_size == -1.0:
        return train_size, 1.0 - train_size
    elif train_size == -1.0:
        return 1.0 - test_size, test_size
    elif train_size + test_size > 1:
        raise ValueError(
            'The sum of test_size and train_size, should be in the (0, 1) range. Reduce test_size and/or train_size.'
            )
    else:
        return train_size, test_size


def set_labels_type(labels, label_type):
    return labels


@overload(set_labels_type, no_unliteral=True)
def overload_set_labels_type(labels, label_type):
    if get_overload_const_int(label_type) == 1:

        def _set_labels(labels, label_type):
            return pd.Series(labels)
        return _set_labels
    elif get_overload_const_int(label_type) == 2:

        def _set_labels(labels, label_type):
            return labels.values
        return _set_labels
    else:

        def _set_labels(labels, label_type):
            return labels
        return _set_labels


def reset_labels_type(labels, label_type):
    return labels


@overload(reset_labels_type, no_unliteral=True)
def overload_reset_labels_type(labels, label_type):
    if get_overload_const_int(label_type) == 1:

        def _reset_labels(labels, label_type):
            return labels.values
        return _reset_labels
    elif get_overload_const_int(label_type) == 2:

        def _reset_labels(labels, label_type):
            return pd.Series(labels, index=np.arange(len(labels)))
        return _reset_labels
    else:

        def _reset_labels(labels, label_type):
            return labels
        return _reset_labels


@overload(sklearn.model_selection.train_test_split, no_unliteral=True)
def overload_train_test_split(data, labels=None, train_size=None, test_size
    =None, random_state=None, shuffle=True, stratify=None,
    _is_data_distributed=False):
    check_sklearn_version()
    qyhuj__nhd = {'stratify': stratify}
    gnp__ppcz = {'stratify': None}
    check_unsupported_args('train_test_split', qyhuj__nhd, gnp__ppcz, 'ml')
    if is_overload_false(_is_data_distributed):
        jxtr__wnfdm = f'data_split_type_{numba.core.ir_utils.next_label()}'
        lqe__yrsvw = f'labels_split_type_{numba.core.ir_utils.next_label()}'
        for smudh__xdtkw, svlrd__mco in ((data, jxtr__wnfdm), (labels,
            lqe__yrsvw)):
            if isinstance(smudh__xdtkw, (DataFrameType, SeriesType)):
                olz__xmmr = smudh__xdtkw.copy(index=NumericIndexType(types.
                    int64))
                setattr(types, svlrd__mco, olz__xmmr)
            else:
                setattr(types, svlrd__mco, smudh__xdtkw)
        eqb__zycml = 'def _train_test_split_impl(\n'
        eqb__zycml += '    data,\n'
        eqb__zycml += '    labels=None,\n'
        eqb__zycml += '    train_size=None,\n'
        eqb__zycml += '    test_size=None,\n'
        eqb__zycml += '    random_state=None,\n'
        eqb__zycml += '    shuffle=True,\n'
        eqb__zycml += '    stratify=None,\n'
        eqb__zycml += '    _is_data_distributed=False,\n'
        eqb__zycml += '):  # pragma: no cover\n'
        eqb__zycml += (
            """    with numba.objmode(data_train='{}', data_test='{}', labels_train='{}', labels_test='{}'):
"""
            .format(jxtr__wnfdm, jxtr__wnfdm, lqe__yrsvw, lqe__yrsvw))
        eqb__zycml += """        data_train, data_test, labels_train, labels_test = sklearn.model_selection.train_test_split(
"""
        eqb__zycml += '            data,\n'
        eqb__zycml += '            labels,\n'
        eqb__zycml += '            train_size=train_size,\n'
        eqb__zycml += '            test_size=test_size,\n'
        eqb__zycml += '            random_state=random_state,\n'
        eqb__zycml += '            shuffle=shuffle,\n'
        eqb__zycml += '            stratify=stratify,\n'
        eqb__zycml += '        )\n'
        eqb__zycml += (
            '    return data_train, data_test, labels_train, labels_test\n')
        www__jks = {}
        exec(eqb__zycml, globals(), www__jks)
        _train_test_split_impl = www__jks['_train_test_split_impl']
        return _train_test_split_impl
    else:
        global get_data_slice_parallel
        if isinstance(get_data_slice_parallel, pytypes.FunctionType):
            get_data_slice_parallel = bodo.jit(get_data_slice_parallel,
                all_args_distributed_varlength=True,
                all_returns_distributed=True)
        label_type = 0
        if isinstance(data, DataFrameType) and isinstance(labels, types.Array):
            label_type = 1
        elif isinstance(data, types.Array) and isinstance(labels, SeriesType):
            label_type = 2
        if is_overload_none(random_state):
            random_state = 42

        def _train_test_split_impl(data, labels=None, train_size=None,
            test_size=None, random_state=None, shuffle=True, stratify=None,
            _is_data_distributed=False):
            if data.shape[0] != labels.shape[0]:
                raise ValueError(
                    'Found input variables with inconsistent number of samples\n'
                    )
            train_size, test_size = get_train_test_size(train_size, test_size)
            dyet__hub = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            len_train = int(dyet__hub * train_size)
            ydvo__ccj = dyet__hub - len_train
            if shuffle:
                labels = set_labels_type(labels, label_type)
                ysxhi__iakl = bodo.get_rank()
                axbti__cvf = bodo.get_size()
                maai__qow = np.empty(axbti__cvf, np.int64)
                bodo.libs.distributed_api.allgather(maai__qow, len(data))
                ttr__dscq = np.cumsum(maai__qow[0:ysxhi__iakl + 1])
                hjed__fusnq = np.full(dyet__hub, True)
                hjed__fusnq[:ydvo__ccj] = False
                np.random.seed(42)
                np.random.permutation(hjed__fusnq)
                if ysxhi__iakl:
                    sxl__psn = ttr__dscq[ysxhi__iakl - 1]
                else:
                    sxl__psn = 0
                yaq__vfq = ttr__dscq[ysxhi__iakl]
                mqu__ckz = hjed__fusnq[sxl__psn:yaq__vfq]
                myj__ovs = data[mqu__ckz]
                aafc__ebxdu = data[~mqu__ckz]
                adp__asz = labels[mqu__ckz]
                ovqc__qpgx = labels[~mqu__ckz]
                myj__ovs = bodo.random_shuffle(myj__ovs, seed=random_state,
                    parallel=True)
                aafc__ebxdu = bodo.random_shuffle(aafc__ebxdu, seed=
                    random_state, parallel=True)
                adp__asz = bodo.random_shuffle(adp__asz, seed=random_state,
                    parallel=True)
                ovqc__qpgx = bodo.random_shuffle(ovqc__qpgx, seed=
                    random_state, parallel=True)
                adp__asz = reset_labels_type(adp__asz, label_type)
                ovqc__qpgx = reset_labels_type(ovqc__qpgx, label_type)
            else:
                myj__ovs, aafc__ebxdu, adp__asz, ovqc__qpgx = (
                    get_data_slice_parallel(data, labels, len_train))
            return myj__ovs, aafc__ebxdu, adp__asz, ovqc__qpgx
        return _train_test_split_impl


class BodoPreprocessingMinMaxScalerType(types.Opaque):

    def __init__(self):
        super(BodoPreprocessingMinMaxScalerType, self).__init__(name=
            'BodoPreprocessingMinMaxScalerType')


preprocessing_minmax_scaler_type = BodoPreprocessingMinMaxScalerType()
types.preprocessing_minmax_scaler_type = preprocessing_minmax_scaler_type
register_model(BodoPreprocessingMinMaxScalerType)(models.OpaqueModel)


@typeof_impl.register(sklearn.preprocessing.MinMaxScaler)
def typeof_preprocessing_minmax_scaler(val, c):
    return preprocessing_minmax_scaler_type


@box(BodoPreprocessingMinMaxScalerType)
def box_preprocessing_minmax_scaler(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoPreprocessingMinMaxScalerType)
def unbox_preprocessing_minmax_scaler(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.preprocessing.MinMaxScaler, no_unliteral=True)
def sklearn_preprocessing_minmax_scaler_overload(feature_range=(0, 1), copy
    =True, clip=False):
    check_sklearn_version()

    def _sklearn_preprocessing_minmax_scaler_impl(feature_range=(0, 1),
        copy=True, clip=False):
        with numba.objmode(m='preprocessing_minmax_scaler_type'):
            m = sklearn.preprocessing.MinMaxScaler(feature_range=
                feature_range, copy=copy, clip=clip)
        return m
    return _sklearn_preprocessing_minmax_scaler_impl


def sklearn_preprocessing_minmax_scaler_fit_dist_helper(m, X):
    axfge__qisy = MPI.COMM_WORLD
    hjp__gpy = axfge__qisy.Get_size()
    m = m.fit(X)
    xds__ozpc = axfge__qisy.allreduce(m.n_samples_seen_, op=MPI.SUM)
    m.n_samples_seen_ = xds__ozpc
    pfu__cmm = np.zeros((hjp__gpy, *m.data_min_.shape), dtype=m.data_min_.dtype
        )
    axfge__qisy.Allgather(m.data_min_, pfu__cmm)
    ggkm__sljr = np.nanmin(pfu__cmm, axis=0)
    cbx__mrhfd = np.zeros((hjp__gpy, *m.data_max_.shape), dtype=m.data_max_
        .dtype)
    axfge__qisy.Allgather(m.data_max_, cbx__mrhfd)
    hto__dnhn = np.nanmax(cbx__mrhfd, axis=0)
    cqbef__srqib = hto__dnhn - ggkm__sljr
    m.scale_ = (m.feature_range[1] - m.feature_range[0]
        ) / sklearn_handle_zeros_in_scale(cqbef__srqib)
    m.min_ = m.feature_range[0] - ggkm__sljr * m.scale_
    m.data_min_ = ggkm__sljr
    m.data_max_ = hto__dnhn
    m.data_range_ = cqbef__srqib
    return m


@overload_method(BodoPreprocessingMinMaxScalerType, 'fit', no_unliteral=True)
def overload_preprocessing_minmax_scaler_fit(m, X, y=None,
    _is_data_distributed=False):

    def _preprocessing_minmax_scaler_fit_impl(m, X, y=None,
        _is_data_distributed=False):
        with numba.objmode(m='preprocessing_minmax_scaler_type'):
            if _is_data_distributed:
                m = sklearn_preprocessing_minmax_scaler_fit_dist_helper(m, X)
            else:
                m = m.fit(X, y)
        return m
    return _preprocessing_minmax_scaler_fit_impl


@overload_method(BodoPreprocessingMinMaxScalerType, 'transform',
    no_unliteral=True)
def overload_preprocessing_minmax_scaler_transform(m, X):

    def _preprocessing_minmax_scaler_transform_impl(m, X):
        with numba.objmode(transformed_X='float64[:,:]'):
            transformed_X = m.transform(X)
        return transformed_X
    return _preprocessing_minmax_scaler_transform_impl


@overload_method(BodoPreprocessingMinMaxScalerType, 'inverse_transform',
    no_unliteral=True)
def overload_preprocessing_minmax_scaler_inverse_transform(m, X):

    def _preprocessing_minmax_scaler_inverse_transform_impl(m, X):
        with numba.objmode(inverse_transformed_X='float64[:,:]'):
            inverse_transformed_X = m.inverse_transform(X)
        return inverse_transformed_X
    return _preprocessing_minmax_scaler_inverse_transform_impl


class BodoPreprocessingLabelEncoderType(types.Opaque):

    def __init__(self):
        super(BodoPreprocessingLabelEncoderType, self).__init__(name=
            'BodoPreprocessingLabelEncoderType')


preprocessing_label_encoder_type = BodoPreprocessingLabelEncoderType()
types.preprocessing_label_encoder_type = preprocessing_label_encoder_type
register_model(BodoPreprocessingLabelEncoderType)(models.OpaqueModel)


@typeof_impl.register(sklearn.preprocessing.LabelEncoder)
def typeof_preprocessing_label_encoder(val, c):
    return preprocessing_label_encoder_type


@box(BodoPreprocessingLabelEncoderType)
def box_preprocessing_label_encoder(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoPreprocessingLabelEncoderType)
def unbox_preprocessing_label_encoder(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.preprocessing.LabelEncoder, no_unliteral=True)
def sklearn_preprocessing_label_encoder_overload():
    check_sklearn_version()

    def _sklearn_preprocessing_label_encoder_impl():
        with numba.objmode(m='preprocessing_label_encoder_type'):
            m = sklearn.preprocessing.LabelEncoder()
        return m
    return _sklearn_preprocessing_label_encoder_impl


@overload_method(BodoPreprocessingLabelEncoderType, 'fit', no_unliteral=True)
def overload_preprocessing_label_encoder_fit(m, y, _is_data_distributed=False):
    if is_overload_true(_is_data_distributed):

        def _sklearn_preprocessing_label_encoder_fit_impl(m, y,
            _is_data_distributed=False):
            y_classes = bodo.libs.array_kernels.unique(y, parallel=True)
            y_classes = bodo.allgatherv(y_classes, False)
            y_classes = bodo.libs.array_kernels.sort(y_classes, ascending=
                True, inplace=False)
            with numba.objmode:
                m.classes_ = y_classes
            return m
        return _sklearn_preprocessing_label_encoder_fit_impl
    else:

        def _sklearn_preprocessing_label_encoder_fit_impl(m, y,
            _is_data_distributed=False):
            with numba.objmode(m='preprocessing_label_encoder_type'):
                m = m.fit(y)
            return m
        return _sklearn_preprocessing_label_encoder_fit_impl


@overload_method(BodoPreprocessingLabelEncoderType, 'transform',
    no_unliteral=True)
def overload_preprocessing_label_encoder_transform(m, y,
    _is_data_distributed=False):

    def _preprocessing_label_encoder_transform_impl(m, y,
        _is_data_distributed=False):
        with numba.objmode(transformed_y='int64[:]'):
            transformed_y = m.transform(y)
        return transformed_y
    return _preprocessing_label_encoder_transform_impl


@numba.njit
def le_fit_transform(m, y):
    m = m.fit(y, _is_data_distributed=True)
    transformed_y = m.transform(y, _is_data_distributed=True)
    return transformed_y


@overload_method(BodoPreprocessingLabelEncoderType, 'fit_transform',
    no_unliteral=True)
def overload_preprocessing_label_encoder_fit_transform(m, y,
    _is_data_distributed=False):
    if is_overload_true(_is_data_distributed):

        def _preprocessing_label_encoder_fit_transform_impl(m, y,
            _is_data_distributed=False):
            transformed_y = le_fit_transform(m, y)
            return transformed_y
        return _preprocessing_label_encoder_fit_transform_impl
    else:

        def _preprocessing_label_encoder_fit_transform_impl(m, y,
            _is_data_distributed=False):
            with numba.objmode(transformed_y='int64[:]'):
                transformed_y = m.fit_transform(y)
            return transformed_y
        return _preprocessing_label_encoder_fit_transform_impl


class BodoFExtractHashingVectorizerType(types.Opaque):

    def __init__(self):
        super(BodoFExtractHashingVectorizerType, self).__init__(name=
            'BodoFExtractHashingVectorizerType')


f_extract_hashing_vectorizer_type = BodoFExtractHashingVectorizerType()
types.f_extract_hashing_vectorizer_type = f_extract_hashing_vectorizer_type
register_model(BodoFExtractHashingVectorizerType)(models.OpaqueModel)


@typeof_impl.register(sklearn.feature_extraction.text.HashingVectorizer)
def typeof_f_extract_hashing_vectorizer(val, c):
    return f_extract_hashing_vectorizer_type


@box(BodoFExtractHashingVectorizerType)
def box_f_extract_hashing_vectorizer(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoFExtractHashingVectorizerType)
def unbox_f_extract_hashing_vectorizer(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.feature_extraction.text.HashingVectorizer, no_unliteral=True)
def sklearn_hashing_vectorizer_overload(input='content', encoding='utf-8',
    decode_error='strict', strip_accents=None, lowercase=True, preprocessor
    =None, tokenizer=None, stop_words=None, token_pattern=
    '(?u)\\b\\w\\w+\\b', ngram_range=(1, 1), analyzer='word', n_features=2 **
    20, binary=False, norm='l2', alternate_sign=True, dtype=np.float64):
    check_sklearn_version()

    def _sklearn_hashing_vectorizer_impl(input='content', encoding='utf-8',
        decode_error='strict', strip_accents=None, lowercase=True,
        preprocessor=None, tokenizer=None, stop_words=None, token_pattern=
        '(?u)\\b\\w\\w+\\b', ngram_range=(1, 1), analyzer='word',
        n_features=2 ** 20, binary=False, norm='l2', alternate_sign=True,
        dtype=np.float64):
        with numba.objmode(m='f_extract_hashing_vectorizer_type'):
            m = sklearn.feature_extraction.text.HashingVectorizer(input=
                input, encoding=encoding, decode_error=decode_error,
                strip_accents=strip_accents, lowercase=lowercase,
                preprocessor=preprocessor, tokenizer=tokenizer, stop_words=
                stop_words, token_pattern=token_pattern, ngram_range=
                ngram_range, analyzer=analyzer, n_features=n_features,
                binary=binary, norm=norm, alternate_sign=alternate_sign,
                dtype=dtype)
        return m
    return _sklearn_hashing_vectorizer_impl


@overload_method(BodoFExtractHashingVectorizerType, 'fit_transform',
    no_unliteral=True)
def overload_hashing_vectorizer_fit_transform(m, X, y=None,
    _is_data_distributed=False):
    types.csr_matrix_float64_int64 = CSRMatrixType(types.float64, types.int64)

    def _hashing_vectorizer_fit_transform_impl(m, X, y=None,
        _is_data_distributed=False):
        with numba.objmode(transformed_X='csr_matrix_float64_int64'):
            transformed_X = m.fit_transform(X, y)
            transformed_X.indices = transformed_X.indices.astype(np.int64)
            transformed_X.indptr = transformed_X.indptr.astype(np.int64)
        return transformed_X
    return _hashing_vectorizer_fit_transform_impl


class BodoRandomForestRegressorType(types.Opaque):

    def __init__(self):
        super(BodoRandomForestRegressorType, self).__init__(name=
            'BodoRandomForestRegressorType')


random_forest_regressor_type = BodoRandomForestRegressorType()
types.random_forest_regressor_type = random_forest_regressor_type
register_model(BodoRandomForestRegressorType)(models.OpaqueModel)


@typeof_impl.register(sklearn.ensemble.RandomForestRegressor)
def typeof_random_forest_regressor(val, c):
    return random_forest_regressor_type


@box(BodoRandomForestRegressorType)
def box_random_forest_regressor(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoRandomForestRegressorType)
def unbox_random_forest_regressor(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.ensemble.RandomForestRegressor, no_unliteral=True)
def overload_sklearn_rf_regressor(n_estimators=100, criterion='mse',
    max_depth=None, min_samples_split=2, min_samples_leaf=1,
    min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=None,
    min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True,
    oob_score=False, n_jobs=None, random_state=None, verbose=0, warm_start=
    False, ccp_alpha=0.0, max_samples=None):
    check_sklearn_version()

    def _sklearn_ensemble_RandomForestRegressor_impl(n_estimators=100,
        criterion='mse', max_depth=None, min_samples_split=2,
        min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=
        'auto', max_leaf_nodes=None, min_impurity_decrease=0.0,
        min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=
        None, random_state=None, verbose=0, warm_start=False, ccp_alpha=0.0,
        max_samples=None):
        with numba.objmode(m='random_forest_regressor_type'):
            if random_state is not None and get_num_nodes() > 1:
                print(
                    'With multinode, fixed random_state seed values are ignored.\n'
                    )
                random_state = None
            m = sklearn.ensemble.RandomForestRegressor(n_estimators=
                n_estimators, criterion=criterion, max_depth=max_depth,
                min_samples_split=min_samples_split, min_samples_leaf=
                min_samples_leaf, min_weight_fraction_leaf=
                min_weight_fraction_leaf, max_features=max_features,
                max_leaf_nodes=max_leaf_nodes, min_impurity_decrease=
                min_impurity_decrease, min_impurity_split=
                min_impurity_split, bootstrap=bootstrap, oob_score=
                oob_score, n_jobs=1, random_state=random_state, verbose=
                verbose, warm_start=warm_start, ccp_alpha=ccp_alpha,
                max_samples=max_samples)
        return m
    return _sklearn_ensemble_RandomForestRegressor_impl


@overload_method(BodoRandomForestRegressorType, 'predict', no_unliteral=True)
def overload_rf_regressor_predict(m, X):
    return parallel_predict_regression(m, X)


@overload_method(BodoRandomForestRegressorType, 'score', no_unliteral=True)
def overload_rf_regressor_score(m, X, y, sample_weight=None,
    _is_data_distributed=False):
    return parallel_score(m, X, y, sample_weight, _is_data_distributed)


@overload_method(BodoRandomForestRegressorType, 'fit', no_unliteral=True)
@overload_method(BodoRandomForestClassifierType, 'fit', no_unliteral=True)
def overload_rf_classifier_model_fit(m, X, y, _is_data_distributed=False):

    def _model_fit_impl(m, X, y, _is_data_distributed=False):
        with numba.objmode(first_rank_node='int32[:]'):
            first_rank_node = get_nodes_first_ranks()
        if _is_data_distributed:
            fkim__aeb = len(first_rank_node)
            X = bodo.gatherv(X)
            y = bodo.gatherv(y)
            if fkim__aeb > 1:
                X = bodo.libs.distributed_api.bcast_comm(X, comm_ranks=
                    first_rank_node, nranks=fkim__aeb)
                y = bodo.libs.distributed_api.bcast_comm(y, comm_ranks=
                    first_rank_node, nranks=fkim__aeb)
        with numba.objmode:
            random_forest_model_fit(m, X, y)
        bodo.barrier()
        return m
    return _model_fit_impl


class BodoFExtractCountVectorizerType(types.Opaque):

    def __init__(self):
        super(BodoFExtractCountVectorizerType, self).__init__(name=
            'BodoFExtractCountVectorizerType')


f_extract_count_vectorizer_type = BodoFExtractCountVectorizerType()
types.f_extract_count_vectorizer_type = f_extract_count_vectorizer_type
register_model(BodoFExtractCountVectorizerType)(models.OpaqueModel)


@typeof_impl.register(sklearn.feature_extraction.text.CountVectorizer)
def typeof_f_extract_count_vectorizer(val, c):
    return f_extract_count_vectorizer_type


@box(BodoFExtractCountVectorizerType)
def box_f_extract_count_vectorizer(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(BodoFExtractCountVectorizerType)
def unbox_f_extract_count_vectorizer(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@overload(sklearn.feature_extraction.text.CountVectorizer, no_unliteral=True)
def sklearn_count_vectorizer_overload(input='content', encoding='utf-8',
    decode_error='strict', strip_accents=None, lowercase=True, preprocessor
    =None, tokenizer=None, stop_words=None, token_pattern=
    '(?u)\\b\\w\\w+\\b', ngram_range=(1, 1), analyzer='word', max_df=1.0,
    max_features=None, vocabulary=None, binary=False, dtype=np.int64):
    check_sklearn_version()

    def _sklearn_count_vectorizer_impl(input='content', encoding='utf-8',
        decode_error='strict', strip_accents=None, lowercase=True,
        preprocessor=None, tokenizer=None, stop_words=None, token_pattern=
        '(?u)\\b\\w\\w+\\b', ngram_range=(1, 1), analyzer='word', max_df=
        1.0, max_features=None, vocabulary=None, binary=False, dtype=np.int64):
        with numba.objmode(m='f_extract_count_vectorizer_type'):
            m = sklearn.feature_extraction.text.CountVectorizer(input=input,
                encoding=encoding, decode_error=decode_error, strip_accents
                =strip_accents, lowercase=lowercase, preprocessor=
                preprocessor, tokenizer=tokenizer, stop_words=stop_words,
                token_pattern=token_pattern, ngram_range=ngram_range,
                analyzer=analyzer, max_df=max_df, max_features=max_features,
                vocabulary=vocabulary, binary=binary, dtype=dtype)
        return m
    return _sklearn_count_vectorizer_impl


@overload_attribute(BodoFExtractCountVectorizerType, 'vocabulary_')
def get_cv_vocabulary_(m):
    types.dict_string_int = types.DictType(types.unicode_type, types.int64)

    def impl(m):
        with numba.objmode(result='dict_string_int'):
            result = m.vocabulary_
        return result
    return impl


def _cv_fit_transform_helper(m, X):
    tyyvo__achtr = False
    local_vocabulary = m.vocabulary
    if m.vocabulary is None:
        m.fit(X)
        local_vocabulary = m.vocabulary_
        tyyvo__achtr = True
    return tyyvo__achtr, local_vocabulary


@overload_method(BodoFExtractCountVectorizerType, 'fit_transform',
    no_unliteral=True)
def overload_count_vectorizer_fit_transform(m, X, y=None,
    _is_data_distributed=False):
    check_sklearn_version()
    types.csr_matrix_int64_int64 = CSRMatrixType(types.int64, types.int64)
    if is_overload_true(_is_data_distributed):
        types.dict_str_int = types.DictType(types.unicode_type, types.int64)

        def _count_vectorizer_fit_transform_impl(m, X, y=None,
            _is_data_distributed=False):
            with numba.objmode(local_vocabulary='dict_str_int', changeVoc=
                'bool_'):
                changeVoc, local_vocabulary = _cv_fit_transform_helper(m, X)
            if changeVoc:
                local_vocabulary = bodo.utils.conversion.coerce_to_array(list
                    (local_vocabulary.keys()))
                rsd__wyy = bodo.libs.array_kernels.unique(local_vocabulary,
                    parallel=True)
                rsd__wyy = bodo.allgatherv(rsd__wyy, False)
                rsd__wyy = bodo.libs.array_kernels.sort(rsd__wyy, ascending
                    =True, inplace=True)
                svgi__lyrv = {}
                for pcfwn__qwkc in range(len(rsd__wyy)):
                    svgi__lyrv[rsd__wyy[pcfwn__qwkc]] = pcfwn__qwkc
            else:
                svgi__lyrv = local_vocabulary
            with numba.objmode(transformed_X='csr_matrix_int64_int64'):
                if changeVoc:
                    m.vocabulary = svgi__lyrv
                transformed_X = m.fit_transform(X, y)
                transformed_X.indices = transformed_X.indices.astype(np.int64)
                transformed_X.indptr = transformed_X.indptr.astype(np.int64)
            return transformed_X
        return _count_vectorizer_fit_transform_impl
    else:

        def _count_vectorizer_fit_transform_impl(m, X, y=None,
            _is_data_distributed=False):
            with numba.objmode(transformed_X='csr_matrix_int64_int64'):
                transformed_X = m.fit_transform(X, y)
                transformed_X.indices = transformed_X.indices.astype(np.int64)
                transformed_X.indptr = transformed_X.indptr.astype(np.int64)
            return transformed_X
        return _count_vectorizer_fit_transform_impl


@overload_method(BodoFExtractCountVectorizerType, 'get_feature_names',
    no_unliteral=True)
def overload_count_vectorizer_get_feature_names(m):
    check_sklearn_version()

    def impl(m):
        with numba.objmode(result=bodo.string_array_type):
            result = m.get_feature_names()
        return result
    return impl
