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
        qnmlc__ppku = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, qnmlc__ppku)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    syt__smx = dict(win_type=win_type, axis=axis, closed=closed)
    vman__crej = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', syt__smx, vman__crej,
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
    syt__smx = dict(win_type=win_type, axis=axis, closed=closed)
    vman__crej = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', syt__smx, vman__crej,
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
        pqwlo__qwzpj, oou__kai, pcw__kzc, tyfqb__ymdy, zbrks__bvpsp = args
        tpe__wtlo = signature.return_type
        cekv__mzm = cgutils.create_struct_proxy(tpe__wtlo)(context, builder)
        cekv__mzm.obj = pqwlo__qwzpj
        cekv__mzm.window = oou__kai
        cekv__mzm.min_periods = pcw__kzc
        cekv__mzm.center = tyfqb__ymdy
        context.nrt.incref(builder, signature.args[0], pqwlo__qwzpj)
        context.nrt.incref(builder, signature.args[1], oou__kai)
        context.nrt.incref(builder, signature.args[2], pcw__kzc)
        context.nrt.incref(builder, signature.args[3], tyfqb__ymdy)
        return cekv__mzm._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    tpe__wtlo = RollingType(obj_type, window_type, on, selection, False)
    return tpe__wtlo(obj_type, window_type, min_periods_type, center_type,
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
    mhndt__tpx = not isinstance(rolling.window_type, types.Integer)
    qoc__cpju = 'variable' if mhndt__tpx else 'fixed'
    hrq__rinu = 'None'
    if mhndt__tpx:
        hrq__rinu = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    ezt__tbz = []
    oupur__eyjwd = 'on_arr, ' if mhndt__tpx else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{qoc__cpju}(bodo.hiframes.pd_series_ext.get_series_data(df), {oupur__eyjwd}index_arr, window, minp, center, func, raw)'
            , hrq__rinu, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    jgddo__vyw = rolling.obj_type.data
    out_cols = []
    for ceo__mot in rolling.selection:
        buh__szf = rolling.obj_type.columns.index(ceo__mot)
        if ceo__mot == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            khsvd__eluut = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {buh__szf})'
                )
            out_cols.append(ceo__mot)
        else:
            if not isinstance(jgddo__vyw[buh__szf].dtype, (types.Boolean,
                types.Number)):
                continue
            khsvd__eluut = (
                f'bodo.hiframes.rolling.rolling_{qoc__cpju}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {buh__szf}), {oupur__eyjwd}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(ceo__mot)
        ezt__tbz.append(khsvd__eluut)
    return ', '.join(ezt__tbz), hrq__rinu, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    syt__smx = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    vman__crej = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', syt__smx, vman__crej,
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
    syt__smx = dict(win_type=win_type, axis=axis, closed=closed, method=method)
    vman__crej = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', syt__smx, vman__crej,
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
        dwy__ptj = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        sfmxk__fpjqv = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{cdiv__cstr}'" if
                isinstance(cdiv__cstr, str) else f'{cdiv__cstr}' for
                cdiv__cstr in rolling.selection if cdiv__cstr != rolling.on))
        faap__wec = jkra__cwhe = ''
        if fname == 'apply':
            faap__wec = 'func, raw, args, kwargs'
            jkra__cwhe = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            faap__wec = jkra__cwhe = 'other, pairwise'
        if fname == 'cov':
            faap__wec = jkra__cwhe = 'other, pairwise, ddof'
        qmgef__rlj = (
            f'lambda df, window, minp, center, {faap__wec}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {sfmxk__fpjqv}){selection}.{fname}({jkra__cwhe})'
            )
        dwy__ptj += f"""  return rolling.obj.apply({qmgef__rlj}, rolling.window, rolling.min_periods, rolling.center, {faap__wec})
"""
        idcyi__pavc = {}
        exec(dwy__ptj, {'bodo': bodo}, idcyi__pavc)
        impl = idcyi__pavc['impl']
        return impl
    uby__lhofi = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if uby__lhofi else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if uby__lhofi else rolling.obj_type.columns
        other_cols = None if uby__lhofi else other.columns
        ezt__tbz, hrq__rinu = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        ezt__tbz, hrq__rinu, out_cols = _gen_df_rolling_out_data(rolling)
    oyl__lvx = uby__lhofi or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    twqq__czqz = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    twqq__czqz += '  df = rolling.obj\n'
    twqq__czqz += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if uby__lhofi else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    srgsw__lbeyf = 'None'
    if uby__lhofi:
        srgsw__lbeyf = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif oyl__lvx:
        ceo__mot = (set(out_cols) - set([rolling.on])).pop()
        srgsw__lbeyf = f"'{ceo__mot}'" if isinstance(ceo__mot, str) else str(
            ceo__mot)
    twqq__czqz += f'  name = {srgsw__lbeyf}\n'
    twqq__czqz += '  window = rolling.window\n'
    twqq__czqz += '  center = rolling.center\n'
    twqq__czqz += '  minp = rolling.min_periods\n'
    twqq__czqz += f'  on_arr = {hrq__rinu}\n'
    if fname == 'apply':
        twqq__czqz += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        twqq__czqz += f"  func = '{fname}'\n"
        twqq__czqz += f'  index_arr = None\n'
        twqq__czqz += f'  raw = False\n'
    if oyl__lvx:
        twqq__czqz += (
            f'  return bodo.hiframes.pd_series_ext.init_series({ezt__tbz}, index, name)'
            )
        idcyi__pavc = {}
        ehf__qns = {'bodo': bodo}
        exec(twqq__czqz, ehf__qns, idcyi__pavc)
        impl = idcyi__pavc['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(twqq__czqz, out_cols,
        ezt__tbz)


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
        zxcw__ookh = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(zxcw__ookh)


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
    gga__zvld = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(gga__zvld) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    mhndt__tpx = not isinstance(window_type, types.Integer)
    hrq__rinu = 'None'
    if mhndt__tpx:
        hrq__rinu = 'bodo.utils.conversion.index_to_array(index)'
    oupur__eyjwd = 'on_arr, ' if mhndt__tpx else ''
    ezt__tbz = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {oupur__eyjwd}window, minp, center)'
            , hrq__rinu)
    for ceo__mot in out_cols:
        if ceo__mot in df_cols and ceo__mot in other_cols:
            ovrzu__vmll = df_cols.index(ceo__mot)
            igaqp__jnlqo = other_cols.index(ceo__mot)
            khsvd__eluut = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ovrzu__vmll}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {igaqp__jnlqo}), {oupur__eyjwd}window, minp, center)'
                )
        else:
            khsvd__eluut = 'np.full(len(df), np.nan)'
        ezt__tbz.append(khsvd__eluut)
    return ', '.join(ezt__tbz), hrq__rinu


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    zegxn__lwu = {'pairwise': pairwise, 'ddof': ddof}
    iskp__doc = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        zegxn__lwu, iskp__doc, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    zegxn__lwu = {'ddof': ddof, 'pairwise': pairwise}
    iskp__doc = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        zegxn__lwu, iskp__doc, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, sskey__aijxu = args
        if isinstance(rolling, RollingType):
            gga__zvld = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(sskey__aijxu, (tuple, list)):
                if len(set(sskey__aijxu).difference(set(gga__zvld))) > 0:
                    raise_const_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(sskey__aijxu).difference(set(gga__zvld))))
                selection = list(sskey__aijxu)
            else:
                if sskey__aijxu not in gga__zvld:
                    raise_const_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(sskey__aijxu))
                selection = [sskey__aijxu]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            gqck__auzls = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(gqck__auzls, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        gga__zvld = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            gga__zvld = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            gga__zvld = rolling.obj_type.columns
        if attr in gga__zvld:
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
    bcd__xzpkn = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    jgddo__vyw = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in bcd__xzpkn):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        lhuqk__osno = jgddo__vyw[bcd__xzpkn.index(get_literal_value(on))]
        if not isinstance(lhuqk__osno, types.Array
            ) or lhuqk__osno.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(smqke__ova.dtype, (types.Boolean, types.Number)) for
        smqke__ova in jgddo__vyw):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
