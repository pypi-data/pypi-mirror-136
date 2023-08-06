"""Support for Pandas Groupby operations
"""
import operator
from enum import Enum
import numba
import numpy as np
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import NumericIndexType, RangeIndexType
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_table, delete_table_decref_arrays, get_groupby_labels, get_shuffle_info, info_from_table, info_to_array, reverse_shuffle_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import gen_const_tup, get_call_expr_arg, get_const_func_output_type
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_index_data_arr_types, get_index_name_types, get_literal_value, get_overload_const_bool, get_overload_const_func, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, get_udf_error_msg, get_udf_out_arr_type, is_dtype_nullable, is_literal_type, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_list, is_overload_constant_str, is_overload_none, is_overload_true, list_cumulative, raise_bodo_error, raise_const_error
from bodo.utils.utils import dt_err, is_expr


class DataFrameGroupByType(types.Type):

    def __init__(self, df_type, keys, selection, as_index, dropna=True,
        explicit_select=False, series_select=False):
        self.df_type = df_type
        self.keys = keys
        self.selection = selection
        self.as_index = as_index
        self.dropna = dropna
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(DataFrameGroupByType, self).__init__(name=
            f'DataFrameGroupBy({df_type}, {keys}, {selection}, {as_index}, {dropna}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return DataFrameGroupByType(self.df_type, self.keys, self.selection,
            self.as_index, self.dropna, self.explicit_select, self.
            series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFrameGroupByType)
class GroupbyModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mmdu__olf = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, mmdu__olf)


make_attribute_wrapper(DataFrameGroupByType, 'obj', 'obj')


def validate_udf(func_name, func):
    if not isinstance(func, (types.functions.MakeFunctionLiteral, bodo.
        utils.typing.FunctionLiteral, types.Dispatcher, CPUDispatcher)):
        raise_const_error(
            f"Groupby.{func_name}: 'func' must be user defined function")


@intrinsic
def init_groupby(typingctx, obj_type, by_type, as_index_type=None,
    dropna_type=None):

    def codegen(context, builder, signature, args):
        yrv__rka = args[0]
        gcqho__bzovl = signature.return_type
        whw__xhxmb = cgutils.create_struct_proxy(gcqho__bzovl)(context, builder
            )
        whw__xhxmb.obj = yrv__rka
        context.nrt.incref(builder, signature.args[0], yrv__rka)
        return whw__xhxmb._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for dvqa__ikik in keys:
        selection.remove(dvqa__ikik)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    gcqho__bzovl = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return gcqho__bzovl(obj_type, by_type, as_index_type, dropna_type), codegen


@lower_builtin('groupby.count', types.VarArg(types.Any))
@lower_builtin('groupby.size', types.VarArg(types.Any))
@lower_builtin('groupby.apply', types.VarArg(types.Any))
@lower_builtin('groupby.agg', types.VarArg(types.Any))
def lower_groupby_count_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


@infer
class StaticGetItemDataFrameGroupBy(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        grpby, woy__gmjne = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(woy__gmjne, (tuple, list)):
                if len(set(woy__gmjne).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_const_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(woy__gmjne).difference(set(grpby.
                        df_type.columns))))
                selection = woy__gmjne
            else:
                if woy__gmjne not in grpby.df_type.columns:
                    raise_const_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(woy__gmjne))
                selection = woy__gmjne,
                series_select = True
            wmkgp__uyux = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(wmkgp__uyux, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, woy__gmjne = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            woy__gmjne):
            wmkgp__uyux = StaticGetItemDataFrameGroupBy.generic(self, (
                grpby, get_literal_value(woy__gmjne)), {}).return_type
            return signature(wmkgp__uyux, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    jrv__exch = arr_type == ArrayItemArrayType(string_array_type)
    stmq__cfx = arr_type.dtype
    if isinstance(stmq__cfx, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {stmq__cfx} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(stmq__cfx, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {stmq__cfx} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(stmq__cfx,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(stmq__cfx, (types.Integer, types.Float, types.Boolean)):
        if jrv__exch or stmq__cfx == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(stmq__cfx, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not stmq__cfx.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {stmq__cfx} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(stmq__cfx, types.Boolean) and func_name in {'cumsum',
        'sum', 'mean', 'std', 'var'}:
        return (None,
            f'groupby built-in functions {func_name} does not support boolean column'
            )
    if func_name in {'idxmin', 'idxmax'}:
        return dtype_to_array_type(get_index_data_arr_types(index_type)[0].
            dtype), 'ok'
    if func_name in {'count', 'nunique'}:
        return dtype_to_array_type(types.int64), 'ok'
    else:
        return arr_type, 'ok'


def get_pivot_output_dtype(arr_type, func_name, index_type=None):
    stmq__cfx = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(stmq__cfx, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(stmq__cfx, types.Integer):
            return IntDtype(stmq__cfx)
        return stmq__cfx
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        orx__qys = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{orx__qys}'."
            )
    elif len(args) > len_args:
        raise BodoError(
            f'Groupby.{func_name}() takes {len_args + 1} positional argument but {len(args)} were given.'
            )


class ColumnType(Enum):
    KeyColumn = 0
    NumericalColumn = 1
    NonNumericalColumn = 2


def get_keys_not_as_index(grp, out_columns, out_data, out_column_type,
    multi_level_names=False):
    for dvqa__ikik in grp.keys:
        if multi_level_names:
            klo__yww = dvqa__ikik, ''
        else:
            klo__yww = dvqa__ikik
        kyje__triqh = grp.df_type.columns.index(dvqa__ikik)
        data = grp.df_type.data[kyje__triqh]
        out_columns.append(klo__yww)
        out_data.append(data)
        out_column_type.append(ColumnType.KeyColumn.value)


def get_agg_typ(grp, args, func_name, typing_context, target_context, func=
    None, kws=None):
    index = RangeIndexType(types.none)
    out_data = []
    out_columns = []
    out_column_type = []
    if func_name == 'head':
        grp.dropna = False
        grp.as_index = True
    if not grp.as_index:
        get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
    elif func_name == 'head':
        if grp.df_type.index == index:
            index = NumericIndexType(types.int64, types.none)
        else:
            index = grp.df_type.index
    elif len(grp.keys) > 1:
        tgghc__cqqii = tuple(grp.df_type.columns.index(grp.keys[crgo__ycmxn
            ]) for crgo__ycmxn in range(len(grp.keys)))
        gpawf__ubpkx = tuple(grp.df_type.data[kyje__triqh] for kyje__triqh in
            tgghc__cqqii)
        index = MultiIndexType(gpawf__ubpkx, tuple(types.StringLiteral(
            dvqa__ikik) for dvqa__ikik in grp.keys))
    else:
        kyje__triqh = grp.df_type.columns.index(grp.keys[0])
        index = bodo.hiframes.pd_index_ext.array_type_to_index(grp.df_type.
            data[kyje__triqh], types.StringLiteral(grp.keys[0]))
    ltd__lcnf = {}
    bobgs__zgi = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        ltd__lcnf[None, 'size'] = 'size'
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for qpxr__pwwh in columns:
            kyje__triqh = grp.df_type.columns.index(qpxr__pwwh)
            data = grp.df_type.data[kyje__triqh]
            opv__yid = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                opv__yid = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    mcw__ddr = SeriesType(data.dtype, data, None, string_type)
                    ihzle__aimhz = get_const_func_output_type(func, (
                        mcw__ddr,), {}, typing_context, target_context)
                    if ihzle__aimhz != ArrayItemArrayType(string_array_type):
                        ihzle__aimhz = dtype_to_array_type(ihzle__aimhz)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=qpxr__pwwh, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    nklyw__illdo = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    gcz__vmkf = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    njs__uqs = dict(numeric_only=nklyw__illdo, min_count=
                        gcz__vmkf)
                    hzo__homu = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}', njs__uqs,
                        hzo__homu, package_name='pandas', module_name='GroupBy'
                        )
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    nklyw__illdo = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    gcz__vmkf = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    njs__uqs = dict(numeric_only=nklyw__illdo, min_count=
                        gcz__vmkf)
                    hzo__homu = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}', njs__uqs,
                        hzo__homu, package_name='pandas', module_name='GroupBy'
                        )
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    nklyw__illdo = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    njs__uqs = dict(numeric_only=nklyw__illdo)
                    hzo__homu = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}', njs__uqs,
                        hzo__homu, package_name='pandas', module_name='GroupBy'
                        )
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    pfctp__hjnr = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    ifryi__zulv = args[1] if len(args) > 1 else kws.pop(
                        'skipna', True)
                    njs__uqs = dict(axis=pfctp__hjnr, skipna=ifryi__zulv)
                    hzo__homu = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}', njs__uqs,
                        hzo__homu, package_name='pandas', module_name='GroupBy'
                        )
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    jfjki__quz = args[0] if len(args) > 0 else kws.pop('ddof',
                        1)
                    njs__uqs = dict(ddof=jfjki__quz)
                    hzo__homu = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}', njs__uqs,
                        hzo__homu, package_name='pandas', module_name='GroupBy'
                        )
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                ihzle__aimhz, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                smtf__iutm = ihzle__aimhz
                out_data.append(smtf__iutm)
                out_columns.append(qpxr__pwwh)
                if func_name == 'agg':
                    yzh__dxxbm = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    ltd__lcnf[qpxr__pwwh, yzh__dxxbm] = qpxr__pwwh
                else:
                    ltd__lcnf[qpxr__pwwh, func_name] = qpxr__pwwh
                out_column_type.append(opv__yid)
            else:
                bobgs__zgi.append(err_msg)
    if func_name == 'sum':
        cbzy__qvokv = any([(vrc__wkkgf == ColumnType.NumericalColumn.value) for
            vrc__wkkgf in out_column_type])
        if cbzy__qvokv:
            out_data = [vrc__wkkgf for vrc__wkkgf, ifur__jmdlk in zip(
                out_data, out_column_type) if ifur__jmdlk != ColumnType.
                NonNumericalColumn.value]
            out_columns = [vrc__wkkgf for vrc__wkkgf, ifur__jmdlk in zip(
                out_columns, out_column_type) if ifur__jmdlk != ColumnType.
                NonNumericalColumn.value]
            ltd__lcnf = {}
            for qpxr__pwwh in out_columns:
                if grp.as_index is False and qpxr__pwwh in grp.keys:
                    continue
                ltd__lcnf[qpxr__pwwh, func_name] = qpxr__pwwh
    qscq__wqe = len(bobgs__zgi)
    if len(out_data) == 0:
        if qscq__wqe == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(qscq__wqe, ' was' if qscq__wqe == 1 else 's were',
                ','.join(bobgs__zgi)))
    qlecp__zngap = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index):
        if isinstance(out_data[0], IntegerArrayType):
            rcu__caces = IntDtype(out_data[0].dtype)
        else:
            rcu__caces = out_data[0].dtype
        oge__dnqt = types.none if func_name == 'size' else types.StringLiteral(
            grp.selection[0])
        qlecp__zngap = SeriesType(rcu__caces, index=index, name_typ=oge__dnqt)
    return signature(qlecp__zngap, *args), ltd__lcnf


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    gayv__ctgm = True
    if isinstance(f_val, str):
        gayv__ctgm = False
        fyhsf__ciz = f_val
    elif is_overload_constant_str(f_val):
        gayv__ctgm = False
        fyhsf__ciz = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        gayv__ctgm = False
        fyhsf__ciz = bodo.utils.typing.get_builtin_function_name(f_val)
    if not gayv__ctgm:
        if fyhsf__ciz not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {fyhsf__ciz}')
        wmkgp__uyux = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(wmkgp__uyux, (), fyhsf__ciz, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            gomnp__hwp = types.functions.MakeFunctionLiteral(f_val)
        else:
            gomnp__hwp = f_val
        validate_udf('agg', gomnp__hwp)
        func = get_overload_const_func(gomnp__hwp, None)
        jbh__xpqsy = func.code if hasattr(func, 'code') else func.__code__
        fyhsf__ciz = jbh__xpqsy.co_name
        wmkgp__uyux = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(wmkgp__uyux, (), 'agg', typing_context,
            target_context, gomnp__hwp)[0].return_type
    return fyhsf__ciz, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    pqxd__nrr = kws and all(isinstance(pjhg__iefa, types.Tuple) and len(
        pjhg__iefa) == 2 for pjhg__iefa in kws.values())
    if is_overload_none(func) and not pqxd__nrr:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not pqxd__nrr:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    vca__yqldm = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if pqxd__nrr or is_overload_constant_dict(func):
        if pqxd__nrr:
            dnixd__xbs = [get_literal_value(vese__acvgn) for vese__acvgn,
                pxor__urso in kws.values()]
            dtght__kiqg = [get_literal_value(byv__lrp) for pxor__urso,
                byv__lrp in kws.values()]
        else:
            blt__dcj = get_overload_constant_dict(func)
            dnixd__xbs = tuple(blt__dcj.keys())
            dtght__kiqg = tuple(blt__dcj.values())
        if 'head' in dtght__kiqg:
            raise BodoError(
                'Groupby.agg()/aggregate(): head cannot be mixed with other groupby operations.'
                )
        if any(qpxr__pwwh not in grp.selection and qpxr__pwwh not in grp.
            keys for qpxr__pwwh in dnixd__xbs):
            raise_const_error(
                f'Selected column names {dnixd__xbs} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            dtght__kiqg)
        if pqxd__nrr and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        ltd__lcnf = {}
        out_columns = []
        out_data = []
        out_column_type = []
        dxnr__ndsef = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for fjp__dzxmg, f_val in zip(dnixd__xbs, dtght__kiqg):
            if isinstance(f_val, (tuple, list)):
                ljvy__bjyk = 0
                for gomnp__hwp in f_val:
                    fyhsf__ciz, out_tp = get_agg_funcname_and_outtyp(grp,
                        fjp__dzxmg, gomnp__hwp, typing_context, target_context)
                    vca__yqldm = fyhsf__ciz in list_cumulative
                    if fyhsf__ciz == '<lambda>' and len(f_val) > 1:
                        fyhsf__ciz = '<lambda_' + str(ljvy__bjyk) + '>'
                        ljvy__bjyk += 1
                    out_columns.append((fjp__dzxmg, fyhsf__ciz))
                    ltd__lcnf[fjp__dzxmg, fyhsf__ciz] = fjp__dzxmg, fyhsf__ciz
                    _append_out_type(grp, out_data, out_tp)
            else:
                fyhsf__ciz, out_tp = get_agg_funcname_and_outtyp(grp,
                    fjp__dzxmg, f_val, typing_context, target_context)
                vca__yqldm = fyhsf__ciz in list_cumulative
                if multi_level_names:
                    out_columns.append((fjp__dzxmg, fyhsf__ciz))
                    ltd__lcnf[fjp__dzxmg, fyhsf__ciz] = fjp__dzxmg, fyhsf__ciz
                elif not pqxd__nrr:
                    out_columns.append(fjp__dzxmg)
                    ltd__lcnf[fjp__dzxmg, fyhsf__ciz] = fjp__dzxmg
                elif pqxd__nrr:
                    dxnr__ndsef.append(fyhsf__ciz)
                _append_out_type(grp, out_data, out_tp)
        if pqxd__nrr:
            for crgo__ycmxn, mytrr__unxts in enumerate(kws.keys()):
                out_columns.append(mytrr__unxts)
                ltd__lcnf[dnixd__xbs[crgo__ycmxn], dxnr__ndsef[crgo__ycmxn]
                    ] = mytrr__unxts
        if vca__yqldm:
            index = grp.df_type.index
        else:
            index = out_tp.index
        qlecp__zngap = DataFrameType(tuple(out_data), index, tuple(out_columns)
            )
        return signature(qlecp__zngap, *args), ltd__lcnf
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one functions supplied'
                )
        assert len(func) > 0
        out_data = []
        out_columns = []
        out_column_type = []
        ljvy__bjyk = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        ltd__lcnf = {}
        xvhh__kal = grp.selection[0]
        for f_val in func.types:
            fyhsf__ciz, out_tp = get_agg_funcname_and_outtyp(grp, xvhh__kal,
                f_val, typing_context, target_context)
            vca__yqldm = fyhsf__ciz in list_cumulative
            if fyhsf__ciz == '<lambda>':
                fyhsf__ciz = '<lambda_' + str(ljvy__bjyk) + '>'
                ljvy__bjyk += 1
            out_columns.append(fyhsf__ciz)
            ltd__lcnf[xvhh__kal, fyhsf__ciz] = fyhsf__ciz
            _append_out_type(grp, out_data, out_tp)
        if vca__yqldm:
            index = grp.df_type.index
        else:
            index = out_tp.index
        qlecp__zngap = DataFrameType(tuple(out_data), index, tuple(out_columns)
            )
        return signature(qlecp__zngap, *args), ltd__lcnf
    fyhsf__ciz = ''
    if types.unliteral(func) == types.unicode_type:
        fyhsf__ciz = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        fyhsf__ciz = bodo.utils.typing.get_builtin_function_name(func)
    if fyhsf__ciz:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, fyhsf__ciz, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = grp.df_type.index
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        pfctp__hjnr = args[0] if len(args) > 0 else kws.pop('axis', 0)
        nklyw__illdo = args[1] if len(args) > 1 else kws.pop('numeric_only',
            False)
        ifryi__zulv = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        njs__uqs = dict(axis=pfctp__hjnr, numeric_only=nklyw__illdo)
        hzo__homu = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', njs__uqs,
            hzo__homu, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        jcka__cij = args[0] if len(args) > 0 else kws.pop('periods', 1)
        nxfg__kddqf = args[1] if len(args) > 1 else kws.pop('freq', None)
        pfctp__hjnr = args[2] if len(args) > 2 else kws.pop('axis', 0)
        euat__fzb = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        njs__uqs = dict(freq=nxfg__kddqf, axis=pfctp__hjnr, fill_value=
            euat__fzb)
        hzo__homu = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', njs__uqs,
            hzo__homu, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        zpq__jtrua = args[0] if len(args) > 0 else kws.pop('func', None)
        dcteb__jcq = kws.pop('engine', None)
        jhhee__lqegi = kws.pop('engine_kwargs', None)
        njs__uqs = dict(engine=dcteb__jcq, engine_kwargs=jhhee__lqegi)
        hzo__homu = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', njs__uqs, hzo__homu,
            package_name='pandas', module_name='GroupBy')
    ltd__lcnf = {}
    for qpxr__pwwh in grp.selection:
        out_columns.append(qpxr__pwwh)
        ltd__lcnf[qpxr__pwwh, name_operation] = qpxr__pwwh
        kyje__triqh = grp.df_type.columns.index(qpxr__pwwh)
        data = grp.df_type.data[kyje__triqh]
        if name_operation == 'cumprod':
            if not isinstance(data.dtype, (types.Integer, types.Float)):
                raise BodoError(msg)
        if name_operation == 'cumsum':
            if data.dtype != types.unicode_type and data != ArrayItemArrayType(
                string_array_type) and not isinstance(data.dtype, (types.
                Integer, types.Float)):
                raise BodoError(msg)
        if name_operation in ('cummin', 'cummax'):
            if not isinstance(data.dtype, types.Integer
                ) and not is_dtype_nullable(data.dtype):
                raise BodoError(msg)
        if name_operation == 'shift':
            if isinstance(data, (TupleArrayType, ArrayItemArrayType)):
                raise BodoError(msg)
            if isinstance(data.dtype, bodo.hiframes.datetime_timedelta_ext.
                DatetimeTimeDeltaType):
                raise BodoError(
                    f"""column type of {data.dtype} is not supported in groupby built-in function shift.
{dt_err}"""
                    )
        if name_operation == 'transform':
            ihzle__aimhz, err_msg = get_groupby_output_dtype(data,
                get_literal_value(zpq__jtrua), grp.df_type.index)
            if err_msg == 'ok':
                data = ihzle__aimhz
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    qlecp__zngap = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        qlecp__zngap = SeriesType(out_data[0].dtype, data=out_data[0],
            index=index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(qlecp__zngap, *args), ltd__lcnf


def resolve_gb(grp, args, kws, func_name, typing_context, target_context,
    err_msg=''):
    if func_name in set(list_cumulative) | {'shift', 'transform'}:
        return resolve_transformative(grp, args, kws, err_msg, func_name)
    elif func_name in {'agg', 'aggregate'}:
        return resolve_agg(grp, args, kws, typing_context, target_context)
    else:
        return get_agg_typ(grp, args, func_name, typing_context,
            target_context, kws=kws)


@infer_getattr
class DataframeGroupByAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameGroupByType
    _attr_set = None

    @bound_function('groupby.agg', no_unliteral=True)
    def resolve_agg(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.aggregate', no_unliteral=True)
    def resolve_aggregate(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.sum', no_unliteral=True)
    def resolve_sum(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'sum', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.count', no_unliteral=True)
    def resolve_count(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'count', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.nunique', no_unliteral=True)
    def resolve_nunique(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'nunique', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.median', no_unliteral=True)
    def resolve_median(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'median', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.mean', no_unliteral=True)
    def resolve_mean(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'mean', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.min', no_unliteral=True)
    def resolve_min(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'min', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.max', no_unliteral=True)
    def resolve_max(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'max', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.prod', no_unliteral=True)
    def resolve_prod(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'prod', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.var', no_unliteral=True)
    def resolve_var(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'var', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.std', no_unliteral=True)
    def resolve_std(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'std', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.first', no_unliteral=True)
    def resolve_first(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'first', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.last', no_unliteral=True)
    def resolve_last(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'last', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmin', no_unliteral=True)
    def resolve_idxmin(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmin', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmax', no_unliteral=True)
    def resolve_idxmax(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmax', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.size', no_unliteral=True)
    def resolve_size(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'size', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.cumsum', no_unliteral=True)
    def resolve_cumsum(self, grp, args, kws):
        msg = (
            'Groupby.cumsum() only supports columns of types integer, float, string or liststring'
            )
        return resolve_gb(grp, args, kws, 'cumsum', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cumprod', no_unliteral=True)
    def resolve_cumprod(self, grp, args, kws):
        msg = (
            'Groupby.cumprod() only supports columns of types integer and float'
            )
        return resolve_gb(grp, args, kws, 'cumprod', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummin', no_unliteral=True)
    def resolve_cummin(self, grp, args, kws):
        msg = (
            'Groupby.cummin() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummin', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummax', no_unliteral=True)
    def resolve_cummax(self, grp, args, kws):
        msg = (
            'Groupby.cummax() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummax', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.shift', no_unliteral=True)
    def resolve_shift(self, grp, args, kws):
        msg = (
            'Column type of list/tuple is not supported in groupby built-in function shift'
            )
        return resolve_gb(grp, args, kws, 'shift', self.context, numba.core
            .registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.pipe', no_unliteral=True)
    def resolve_pipe(self, grp, args, kws):
        return resolve_obj_pipe(self, grp, args, kws, 'GroupBy')

    @bound_function('groupby.transform', no_unliteral=True)
    def resolve_transform(self, grp, args, kws):
        msg = (
            'Groupby.transform() only supports sum, count, min, max, mean, and std operations'
            )
        return resolve_gb(grp, args, kws, 'transform', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.head', no_unliteral=True)
    def resolve_head(self, grp, args, kws):
        msg = 'Unsupported Gropupby head operation.\n'
        return resolve_gb(grp, args, kws, 'head', self.context, numba.core.
            registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.apply', no_unliteral=True)
    def resolve_apply(self, grp, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws.pop('func', None)
        f_args = tuple(args[1:]) if len(args) > 0 else ()
        eite__qmq = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        ydvdl__gsdhv = isinstance(eite__qmq, (SeriesType,
            HeterogeneousSeriesType)
            ) and eite__qmq.const_info is not None or not isinstance(eite__qmq,
            (SeriesType, DataFrameType))
        if ydvdl__gsdhv:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                yxslu__ehuid = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                tgghc__cqqii = tuple(grp.df_type.columns.index(grp.keys[
                    crgo__ycmxn]) for crgo__ycmxn in range(len(grp.keys)))
                gpawf__ubpkx = tuple(grp.df_type.data[kyje__triqh] for
                    kyje__triqh in tgghc__cqqii)
                yxslu__ehuid = MultiIndexType(gpawf__ubpkx, tuple(types.
                    literal(dvqa__ikik) for dvqa__ikik in grp.keys))
            else:
                kyje__triqh = grp.df_type.columns.index(grp.keys[0])
                yxslu__ehuid = bodo.hiframes.pd_index_ext.array_type_to_index(
                    grp.df_type.data[kyje__triqh], types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            sqba__aie = tuple(grp.df_type.data[grp.df_type.columns.index(
                qpxr__pwwh)] for qpxr__pwwh in grp.keys)
            ndmub__iohvg = tuple(types.literal(pjhg__iefa) for pjhg__iefa in
                grp.keys) + get_index_name_types(eite__qmq.index)
            if not grp.as_index:
                sqba__aie = types.Array(types.int64, 1, 'C'),
                ndmub__iohvg = (types.none,) + get_index_name_types(eite__qmq
                    .index)
            yxslu__ehuid = MultiIndexType(sqba__aie +
                get_index_data_arr_types(eite__qmq.index), ndmub__iohvg)
        if ydvdl__gsdhv:
            if isinstance(eite__qmq, HeterogeneousSeriesType):
                pxor__urso, tzfzt__wqe = eite__qmq.const_info
                esbe__sflp = tuple(dtype_to_array_type(wqdaw__dtpr) for
                    wqdaw__dtpr in eite__qmq.data.types)
                czg__vouo = DataFrameType(out_data + esbe__sflp,
                    yxslu__ehuid, out_columns + tzfzt__wqe)
            elif isinstance(eite__qmq, SeriesType):
                eljcd__llhz, tzfzt__wqe = eite__qmq.const_info
                esbe__sflp = tuple(dtype_to_array_type(eite__qmq.dtype) for
                    pxor__urso in range(eljcd__llhz))
                czg__vouo = DataFrameType(out_data + esbe__sflp,
                    yxslu__ehuid, out_columns + tzfzt__wqe)
            else:
                nsyet__wpo = get_udf_out_arr_type(eite__qmq)
                if not grp.as_index:
                    czg__vouo = DataFrameType(out_data + (nsyet__wpo,),
                        yxslu__ehuid, out_columns + ('',))
                else:
                    czg__vouo = SeriesType(nsyet__wpo.dtype, nsyet__wpo,
                        yxslu__ehuid, None)
        elif isinstance(eite__qmq, SeriesType):
            czg__vouo = SeriesType(eite__qmq.dtype, eite__qmq.data,
                yxslu__ehuid, eite__qmq.name_typ)
        else:
            czg__vouo = DataFrameType(eite__qmq.data, yxslu__ehuid,
                eite__qmq.columns)
        phhk__batc = gen_apply_pysig(len(f_args), kws.keys())
        zqr__zul = (func, *f_args) + tuple(kws.values())
        return signature(czg__vouo, *zqr__zul).replace(pysig=phhk__batc)

    def generic_resolve(self, grpby, attr):
        if self._is_existing_attr(attr):
            return
        if attr not in grpby.df_type.columns:
            raise_const_error(
                f'groupby: invalid attribute {attr} (column not found in dataframe or unsupported function)'
                )
        return DataFrameGroupByType(grpby.df_type, grpby.keys, (attr,),
            grpby.as_index, grpby.dropna, True, True)


def _get_groupby_apply_udf_out_type(func, grp, f_args, kws, typing_context,
    target_context):
    bsssf__njidr = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            fjp__dzxmg = grp.selection[0]
            nsyet__wpo = bsssf__njidr.data[bsssf__njidr.columns.index(
                fjp__dzxmg)]
            xqol__upx = SeriesType(nsyet__wpo.dtype, nsyet__wpo,
                bsssf__njidr.index, types.literal(fjp__dzxmg))
        else:
            qlwwi__xttob = tuple(bsssf__njidr.data[bsssf__njidr.columns.
                index(qpxr__pwwh)] for qpxr__pwwh in grp.selection)
            xqol__upx = DataFrameType(qlwwi__xttob, bsssf__njidr.index,
                tuple(grp.selection))
    else:
        xqol__upx = bsssf__njidr
    bpq__qvwpo = xqol__upx,
    bpq__qvwpo += tuple(f_args)
    try:
        eite__qmq = get_const_func_output_type(func, bpq__qvwpo, kws,
            typing_context, target_context)
    except Exception as pqcsv__cel:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', pqcsv__cel),
            getattr(pqcsv__cel, 'loc', None))
    return eite__qmq


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    bpq__qvwpo = (grp,) + f_args
    try:
        eite__qmq = get_const_func_output_type(func, bpq__qvwpo, kws, self.
            context, numba.core.registry.cpu_target.target_context, False)
    except Exception as pqcsv__cel:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', pqcsv__cel
            ), getattr(pqcsv__cel, 'loc', None))
    phhk__batc = gen_apply_pysig(len(f_args), kws.keys())
    zqr__zul = (func, *f_args) + tuple(kws.values())
    return signature(eite__qmq, *zqr__zul).replace(pysig=phhk__batc)


def gen_apply_pysig(n_args, kws):
    dzccu__exkfi = ', '.join(f'arg{crgo__ycmxn}' for crgo__ycmxn in range(
        n_args))
    dzccu__exkfi = dzccu__exkfi + ', ' if dzccu__exkfi else ''
    sklp__huts = ', '.join(f"{xbqdd__oyek} = ''" for xbqdd__oyek in kws)
    euc__qoa = f'def apply_stub(func, {dzccu__exkfi}{sklp__huts}):\n'
    euc__qoa += '    pass\n'
    sbx__zus = {}
    exec(euc__qoa, {}, sbx__zus)
    eam__iodli = sbx__zus['apply_stub']
    return numba.core.utils.pysignature(eam__iodli)


def pivot_table_dummy(df, values, index, columns, aggfunc, _pivot_values):
    return 0


@infer_global(pivot_table_dummy)
class PivotTableTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, values, index, columns, aggfunc, _pivot_values = args
        if not (is_overload_constant_str(values) and
            is_overload_constant_str(index) and is_overload_constant_str(
            columns)):
            raise BodoError(
                "pivot_table() only support string constants for 'values', 'index' and 'columns' arguments"
                )
        values = values.literal_value
        index = index.literal_value
        columns = columns.literal_value
        data = df.data[df.columns.index(values)]
        ihzle__aimhz = get_pivot_output_dtype(data, aggfunc.literal_value)
        jaxds__zzsh = dtype_to_array_type(ihzle__aimhz)
        if is_overload_none(_pivot_values):
            raise_bodo_error(
                'Dataframe.pivot_table() requires explicit annotation to determine output columns. For more information, see: https://docs.bodo.ai/latest/source/programming_with_bodo/pandas.html'
                )
        sbv__zisak = _pivot_values.meta
        adimb__nrb = len(sbv__zisak)
        kyje__triqh = df.columns.index(index)
        jafm__qfapu = bodo.hiframes.pd_index_ext.array_type_to_index(df.
            data[kyje__triqh], types.StringLiteral(index))
        orrrp__ljyha = DataFrameType((jaxds__zzsh,) * adimb__nrb,
            jafm__qfapu, tuple(sbv__zisak))
        return signature(orrrp__ljyha, *args)


PivotTableTyper._no_unliteral = True


@lower_builtin(pivot_table_dummy, types.VarArg(types.Any))
def lower_pivot_table_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        jaxds__zzsh = types.Array(types.int64, 1, 'C')
        sbv__zisak = _pivot_values.meta
        adimb__nrb = len(sbv__zisak)
        jafm__qfapu = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        orrrp__ljyha = DataFrameType((jaxds__zzsh,) * adimb__nrb,
            jafm__qfapu, tuple(sbv__zisak))
        return signature(orrrp__ljyha, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    euc__qoa = 'def impl(keys, dropna, _is_parallel):\n'
    euc__qoa += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    euc__qoa += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{crgo__ycmxn}])' for crgo__ycmxn in range(len(
        keys.types))))
    euc__qoa += '    table = arr_info_list_to_table(info_list)\n'
    euc__qoa += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    euc__qoa += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    euc__qoa += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    euc__qoa += '    delete_table_decref_arrays(table)\n'
    euc__qoa += '    ev.finalize()\n'
    euc__qoa += '    return sort_idx, group_labels, ngroups\n'
    sbx__zus = {}
    exec(euc__qoa, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, sbx__zus)
    nqyei__zcrzj = sbx__zus['impl']
    return nqyei__zcrzj


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    lwghf__czrff = len(labels)
    lbrhw__alqel = np.zeros(ngroups, dtype=np.int64)
    wlf__gvk = np.zeros(ngroups, dtype=np.int64)
    ofm__vasd = 0
    nstcm__jiif = 0
    for crgo__ycmxn in range(lwghf__czrff):
        aig__htbm = labels[crgo__ycmxn]
        if aig__htbm < 0:
            ofm__vasd += 1
        else:
            nstcm__jiif += 1
            if crgo__ycmxn == lwghf__czrff - 1 or aig__htbm != labels[
                crgo__ycmxn + 1]:
                lbrhw__alqel[aig__htbm] = ofm__vasd
                wlf__gvk[aig__htbm] = ofm__vasd + nstcm__jiif
                ofm__vasd += nstcm__jiif
                nstcm__jiif = 0
    return lbrhw__alqel, wlf__gvk


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    eljcd__llhz = len(df.columns)
    ycr__zhcim = len(keys.types)
    qbxn__hgn = ', '.join('data_{}'.format(crgo__ycmxn) for crgo__ycmxn in
        range(eljcd__llhz))
    euc__qoa = 'def impl(df, keys, _is_parallel):\n'
    for crgo__ycmxn in range(eljcd__llhz):
        euc__qoa += f"""  in_arr{crgo__ycmxn} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {crgo__ycmxn})
"""
    euc__qoa += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    euc__qoa += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{crgo__ycmxn}])' for crgo__ycmxn in range(
        ycr__zhcim)), ', '.join(f'array_to_info(in_arr{crgo__ycmxn})' for
        crgo__ycmxn in range(eljcd__llhz)), 'array_to_info(in_index_arr)')
    euc__qoa += '  table = arr_info_list_to_table(info_list)\n'
    euc__qoa += (
        f'  out_table = shuffle_table(table, {ycr__zhcim}, _is_parallel, 1)\n')
    for crgo__ycmxn in range(ycr__zhcim):
        euc__qoa += f"""  out_key{crgo__ycmxn} = info_to_array(info_from_table(out_table, {crgo__ycmxn}), keys[{crgo__ycmxn}])
"""
    for crgo__ycmxn in range(eljcd__llhz):
        euc__qoa += f"""  out_arr{crgo__ycmxn} = info_to_array(info_from_table(out_table, {crgo__ycmxn + ycr__zhcim}), in_arr{crgo__ycmxn})
"""
    euc__qoa += f"""  out_arr_index = info_to_array(info_from_table(out_table, {ycr__zhcim + eljcd__llhz}), in_index_arr)
"""
    euc__qoa += '  shuffle_info = get_shuffle_info(out_table)\n'
    euc__qoa += '  delete_table(out_table)\n'
    euc__qoa += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{crgo__ycmxn}' for crgo__ycmxn in range(
        eljcd__llhz))
    euc__qoa += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    euc__qoa += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, {gen_const_tup(df.columns)})
"""
    euc__qoa += '  return out_df, ({},), shuffle_info\n'.format(', '.join(
        f'out_key{crgo__ycmxn}' for crgo__ycmxn in range(ycr__zhcim)))
    sbx__zus = {}
    exec(euc__qoa, {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info}, sbx__zus)
    nqyei__zcrzj = sbx__zus['impl']
    return nqyei__zcrzj


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        sppwj__ucc = len(data.array_types)
        euc__qoa = 'def impl(data, shuffle_info):\n'
        euc__qoa += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{crgo__ycmxn}])' for crgo__ycmxn in
            range(sppwj__ucc)))
        euc__qoa += '  table = arr_info_list_to_table(info_list)\n'
        euc__qoa += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for crgo__ycmxn in range(sppwj__ucc):
            euc__qoa += f"""  out_arr{crgo__ycmxn} = info_to_array(info_from_table(out_table, {crgo__ycmxn}), data._data[{crgo__ycmxn}])
"""
        euc__qoa += '  delete_table(out_table)\n'
        euc__qoa += '  delete_table(table)\n'
        euc__qoa += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{crgo__ycmxn}' for crgo__ycmxn in
            range(sppwj__ucc))))
        sbx__zus = {}
        exec(euc__qoa, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, sbx__zus)
        nqyei__zcrzj = sbx__zus['impl']
        return nqyei__zcrzj
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            pruz__itss = bodo.utils.conversion.index_to_array(data)
            smtf__iutm = reverse_shuffle(pruz__itss, shuffle_info)
            return bodo.utils.conversion.index_from_array(smtf__iutm)
        return impl_index

    def impl_arr(data, shuffle_info):
        pxnue__nytv = [array_to_info(data)]
        wipf__rnb = arr_info_list_to_table(pxnue__nytv)
        qdtdr__voap = reverse_shuffle_table(wipf__rnb, shuffle_info)
        smtf__iutm = info_to_array(info_from_table(qdtdr__voap, 0), data)
        delete_table(qdtdr__voap)
        delete_table(wipf__rnb)
        return smtf__iutm
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    njs__uqs = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    hzo__homu = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', njs__uqs, hzo__homu,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    zog__gtlvj = get_overload_const_bool(ascending)
    pcfel__uaa = grp.selection[0]
    euc__qoa = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    yidb__xdw = (
        f"lambda S: S.value_counts(ascending={zog__gtlvj}, _index_name='{pcfel__uaa}')"
        )
    euc__qoa += f'    return grp.apply({yidb__xdw})\n'
    sbx__zus = {}
    exec(euc__qoa, {'bodo': bodo}, sbx__zus)
    nqyei__zcrzj = sbx__zus['impl']
    return nqyei__zcrzj


groupby_unsupported_attr = {'groups', 'indices'}
groupby_unsupported = {'__iter__', 'get_group', 'all', 'any', 'bfill',
    'backfill', 'cumcount', 'cummax', 'cummin', 'cumprod', 'ffill',
    'ngroup', 'nth', 'ohlc', 'pad', 'rank', 'pct_change', 'sem', 'tail',
    'corr', 'cov', 'describe', 'diff', 'fillna', 'filter', 'hist', 'mad',
    'plot', 'quantile', 'resample', 'sample', 'skew', 'take', 'tshift'}
series_only_unsupported_attrs = {'is_monotonic_increasing',
    'is_monotonic_decreasing'}
series_only_unsupported = {'nlargest', 'nsmallest', 'unique'}
dataframe_only_unsupported = {'corrwith', 'boxplot'}


def _install_groupy_unsupported():
    for fzm__jmvyz in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, fzm__jmvyz, no_unliteral=True
            )(create_unsupported_overload(f'DataFrameGroupBy.{fzm__jmvyz}'))
    for fzm__jmvyz in groupby_unsupported:
        overload_method(DataFrameGroupByType, fzm__jmvyz, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{fzm__jmvyz}'))
    for fzm__jmvyz in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, fzm__jmvyz, no_unliteral=True
            )(create_unsupported_overload(f'SeriesGroupBy.{fzm__jmvyz}'))
    for fzm__jmvyz in series_only_unsupported:
        overload_method(DataFrameGroupByType, fzm__jmvyz, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{fzm__jmvyz}'))
    for fzm__jmvyz in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, fzm__jmvyz, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{fzm__jmvyz}'))


_install_groupy_unsupported()
