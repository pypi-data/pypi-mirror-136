"""typing for rolling window functions
"""
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model
import bodo
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.hiframes.pd_groupby_ext import DataFrameGroupByType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.rolling import supported_rolling_funcs, unsupported_rolling_methods
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, get_literal_value, is_const_func_type, is_literal_type, is_overload_bool, is_overload_constant_str, is_overload_int, is_overload_none, raise_bodo_error, raise_const_error


class RollingType(types.Type):

    def __init__(self, obj_type, window_type, on, selection,
        explicit_select=False, series_select=False):
        self.obj_type = obj_type
        self.window_type = window_type
        self.on = on
        self.selection = selection
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(RollingType, self).__init__(name=
            f'RollingType({obj_type}, {window_type}, {on}, {selection}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return RollingType(self.obj_type, self.window_type, self.on, self.
            selection, self.explicit_select, self.series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(RollingType)
class RollingModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ljs__nrsj = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, ljs__nrsj)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    lwzw__thg = dict(win_type=win_type, axis=axis, closed=closed)
    yjb__wjypd = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', lwzw__thg, yjb__wjypd,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(df, window, min_periods, center, on)

    def impl(df, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(df, window,
            min_periods, center, on)
    return impl


@overload_method(SeriesType, 'rolling', inline='always', no_unliteral=True)
def overload_series_rolling(S, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    lwzw__thg = dict(win_type=win_type, axis=axis, closed=closed)
    yjb__wjypd = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', lwzw__thg, yjb__wjypd,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(S, window, min_periods, center, on)

    def impl(S, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(S, window,
            min_periods, center, on)
    return impl


@intrinsic
def init_rolling(typingctx, obj_type, window_type, min_periods_type,
    center_type, on_type=None):

    def codegen(context, builder, signature, args):
        zfr__dvr, qgnz__poqn, dcvu__yjx, ktg__ylx, typr__snyxr = args
        fxgzd__rjb = signature.return_type
        vdc__ckrv = cgutils.create_struct_proxy(fxgzd__rjb)(context, builder)
        vdc__ckrv.obj = zfr__dvr
        vdc__ckrv.window = qgnz__poqn
        vdc__ckrv.min_periods = dcvu__yjx
        vdc__ckrv.center = ktg__ylx
        context.nrt.incref(builder, signature.args[0], zfr__dvr)
        context.nrt.incref(builder, signature.args[1], qgnz__poqn)
        context.nrt.incref(builder, signature.args[2], dcvu__yjx)
        context.nrt.incref(builder, signature.args[3], ktg__ylx)
        return vdc__ckrv._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    fxgzd__rjb = RollingType(obj_type, window_type, on, selection, False)
    return fxgzd__rjb(obj_type, window_type, min_periods_type, center_type,
        on_type), codegen


def _handle_default_min_periods(min_periods, window):
    return min_periods


@overload(_handle_default_min_periods)
def overload_handle_default_min_periods(min_periods, window):
    if is_overload_none(min_periods):
        if isinstance(window, types.Integer):
            return lambda min_periods, window: window
        else:
            return lambda min_periods, window: 1
    else:
        return lambda min_periods, window: min_periods


def _gen_df_rolling_out_data(rolling):
    msuxa__pnoxg = not isinstance(rolling.window_type, types.Integer)
    fsov__bnivy = 'variable' if msuxa__pnoxg else 'fixed'
    vvjle__wxkb = 'None'
    if msuxa__pnoxg:
        vvjle__wxkb = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    bkpd__ear = []
    kwy__egqql = 'on_arr, ' if msuxa__pnoxg else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{fsov__bnivy}(bodo.hiframes.pd_series_ext.get_series_data(df), {kwy__egqql}index_arr, window, minp, center, func, raw)'
            , vvjle__wxkb, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    bqb__ktcsc = rolling.obj_type.data
    out_cols = []
    for ovkn__efo in rolling.selection:
        cajws__uiva = rolling.obj_type.columns.index(ovkn__efo)
        if ovkn__efo == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            caxp__ehuh = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {cajws__uiva})'
                )
            out_cols.append(ovkn__efo)
        else:
            if not isinstance(bqb__ktcsc[cajws__uiva].dtype, (types.Boolean,
                types.Number)):
                continue
            caxp__ehuh = (
                f'bodo.hiframes.rolling.rolling_{fsov__bnivy}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {cajws__uiva}), {kwy__egqql}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(ovkn__efo)
        bkpd__ear.append(caxp__ehuh)
    return ', '.join(bkpd__ear), vvjle__wxkb, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    lwzw__thg = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    yjb__wjypd = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', lwzw__thg, yjb__wjypd,
        package_name='pandas', module_name='Window')
    if not is_const_func_type(func):
        raise BodoError(
            f"Rolling.apply(): 'func' parameter must be a function, not {func} (builtin functions not supported yet)."
            )
    if not is_overload_bool(raw):
        raise BodoError(
            f"Rolling.apply(): 'raw' parameter must be bool, not {raw}.")
    return _gen_rolling_impl(rolling, 'apply')


@overload_method(DataFrameGroupByType, 'rolling', inline='always',
    no_unliteral=True)
def groupby_rolling_overload(grp, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None, method='single'):
    lwzw__thg = dict(win_type=win_type, axis=axis, closed=closed, method=method
        )
    yjb__wjypd = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', lwzw__thg, yjb__wjypd,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(grp, window, min_periods, center, on)

    def _impl(grp, window, min_periods=None, center=False, win_type=None,
        on=None, axis=0, closed=None, method='single'):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(grp, window,
            min_periods, center, on)
    return _impl


def _gen_rolling_impl(rolling, fname, other=None):
    if isinstance(rolling.obj_type, DataFrameGroupByType):
        lfz__wjx = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        qot__yso = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{xvps__ajjtm}'" if
                isinstance(xvps__ajjtm, str) else f'{xvps__ajjtm}' for
                xvps__ajjtm in rolling.selection if xvps__ajjtm != rolling.on))
        yjz__hsw = fctz__zgm = ''
        if fname == 'apply':
            yjz__hsw = 'func, raw, args, kwargs'
            fctz__zgm = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            yjz__hsw = fctz__zgm = 'other, pairwise'
        if fname == 'cov':
            yjz__hsw = fctz__zgm = 'other, pairwise, ddof'
        mvv__tit = (
            f'lambda df, window, minp, center, {yjz__hsw}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {qot__yso}){selection}.{fname}({fctz__zgm})'
            )
        lfz__wjx += f"""  return rolling.obj.apply({mvv__tit}, rolling.window, rolling.min_periods, rolling.center, {yjz__hsw})
"""
        yewvj__rlwbn = {}
        exec(lfz__wjx, {'bodo': bodo}, yewvj__rlwbn)
        impl = yewvj__rlwbn['impl']
        return impl
    itj__fclb = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if itj__fclb else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if itj__fclb else rolling.obj_type.columns
        other_cols = None if itj__fclb else other.columns
        bkpd__ear, vvjle__wxkb = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        bkpd__ear, vvjle__wxkb, out_cols = _gen_df_rolling_out_data(rolling)
    ncpw__bpvif = itj__fclb or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    kxn__dotvv = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    kxn__dotvv += '  df = rolling.obj\n'
    kxn__dotvv += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if itj__fclb else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    hfzjy__ckm = 'None'
    if itj__fclb:
        hfzjy__ckm = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif ncpw__bpvif:
        ovkn__efo = (set(out_cols) - set([rolling.on])).pop()
        hfzjy__ckm = f"'{ovkn__efo}'" if isinstance(ovkn__efo, str) else str(
            ovkn__efo)
    kxn__dotvv += f'  name = {hfzjy__ckm}\n'
    kxn__dotvv += '  window = rolling.window\n'
    kxn__dotvv += '  center = rolling.center\n'
    kxn__dotvv += '  minp = rolling.min_periods\n'
    kxn__dotvv += f'  on_arr = {vvjle__wxkb}\n'
    if fname == 'apply':
        kxn__dotvv += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        kxn__dotvv += f"  func = '{fname}'\n"
        kxn__dotvv += f'  index_arr = None\n'
        kxn__dotvv += f'  raw = False\n'
    if ncpw__bpvif:
        kxn__dotvv += (
            f'  return bodo.hiframes.pd_series_ext.init_series({bkpd__ear}, index, name)'
            )
        yewvj__rlwbn = {}
        psn__dtr = {'bodo': bodo}
        exec(kxn__dotvv, psn__dtr, yewvj__rlwbn)
        impl = yewvj__rlwbn['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(kxn__dotvv, out_cols,
        bkpd__ear)


def _get_rolling_func_args(fname):
    if fname == 'apply':
        return (
            'func, raw=False, engine=None, engine_kwargs=None, args=None, kwargs=None\n'
            )
    elif fname == 'corr':
        return 'other=None, pairwise=None, ddof=1\n'
    elif fname == 'cov':
        return 'other=None, pairwise=None, ddof=1\n'
    return ''


def create_rolling_overload(fname):

    def overload_rolling_func(rolling):
        return _gen_rolling_impl(rolling, fname)
    return overload_rolling_func


def _install_rolling_methods():
    for fname in supported_rolling_funcs:
        if fname in ('apply', 'corr', 'cov'):
            continue
        dus__bcyev = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(dus__bcyev)


def _install_rolling_unsupported_methods():
    for fname in unsupported_rolling_methods:
        overload_method(RollingType, fname, no_unliteral=True)(
            create_unsupported_overload(
            f'pandas.core.window.rolling.Rolling.{fname}()'))


_install_rolling_methods()
_install_rolling_unsupported_methods()


def _get_corr_cov_out_cols(rolling, other, func_name):
    if not isinstance(other, DataFrameType):
        raise_bodo_error(
            f"DataFrame.rolling.{func_name}(): requires providing a DataFrame for 'other'"
            )
    ecas__hng = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(ecas__hng) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    msuxa__pnoxg = not isinstance(window_type, types.Integer)
    vvjle__wxkb = 'None'
    if msuxa__pnoxg:
        vvjle__wxkb = 'bodo.utils.conversion.index_to_array(index)'
    kwy__egqql = 'on_arr, ' if msuxa__pnoxg else ''
    bkpd__ear = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {kwy__egqql}window, minp, center)'
            , vvjle__wxkb)
    for ovkn__efo in out_cols:
        if ovkn__efo in df_cols and ovkn__efo in other_cols:
            lbo__zyoem = df_cols.index(ovkn__efo)
            jxe__eeehj = other_cols.index(ovkn__efo)
            caxp__ehuh = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {lbo__zyoem}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {jxe__eeehj}), {kwy__egqql}window, minp, center)'
                )
        else:
            caxp__ehuh = 'np.full(len(df), np.nan)'
        bkpd__ear.append(caxp__ehuh)
    return ', '.join(bkpd__ear), vvjle__wxkb


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    dduel__jjxfk = {'pairwise': pairwise, 'ddof': ddof}
    ggbqh__fdm = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        dduel__jjxfk, ggbqh__fdm, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    dduel__jjxfk = {'ddof': ddof, 'pairwise': pairwise}
    ggbqh__fdm = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        dduel__jjxfk, ggbqh__fdm, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, owwid__nffsv = args
        if isinstance(rolling, RollingType):
            ecas__hng = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(owwid__nffsv, (tuple, list)):
                if len(set(owwid__nffsv).difference(set(ecas__hng))) > 0:
                    raise_const_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(owwid__nffsv).difference(set(ecas__hng))))
                selection = list(owwid__nffsv)
            else:
                if owwid__nffsv not in ecas__hng:
                    raise_const_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(owwid__nffsv))
                selection = [owwid__nffsv]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            uxct__ugans = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(uxct__ugans, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        ecas__hng = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            ecas__hng = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            ecas__hng = rolling.obj_type.columns
        if attr in ecas__hng:
            return RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, (attr,) if rolling.on is None else (attr,
                rolling.on), True, True)


def _validate_rolling_args(obj, window, min_periods, center, on):
    assert isinstance(obj, (SeriesType, DataFrameType, DataFrameGroupByType)
        ), 'invalid rolling obj'
    func_name = 'Series' if isinstance(obj, SeriesType
        ) else 'DataFrame' if isinstance(obj, DataFrameType
        ) else 'DataFrameGroupBy'
    if not (is_overload_int(window) or is_overload_constant_str(window) or 
        window == bodo.string_type or window in (pd_timedelta_type,
        datetime_timedelta_type)):
        raise BodoError(
            f"{func_name}.rolling(): 'window' should be int or time offset (str, pd.Timedelta, datetime.timedelta), not {window}"
            )
    if not is_overload_bool(center):
        raise BodoError(
            f'{func_name}.rolling(): center must be a boolean, not {center}')
    if not (is_overload_none(min_periods) or isinstance(min_periods, types.
        Integer)):
        raise BodoError(
            f'{func_name}.rolling(): min_periods must be an integer, not {min_periods}'
            )
    if isinstance(obj, SeriesType) and not is_overload_none(on):
        raise BodoError(
            f"{func_name}.rolling(): 'on' not supported for Series yet (can use a DataFrame instead)."
            )
    sjajc__pucsa = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    bqb__ktcsc = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in sjajc__pucsa):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        bwtv__jsk = bqb__ktcsc[sjajc__pucsa.index(get_literal_value(on))]
        if not isinstance(bwtv__jsk, types.Array
            ) or bwtv__jsk.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(rnw__rmu.dtype, (types.Boolean, types.Number)) for
        rnw__rmu in bqb__ktcsc):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
