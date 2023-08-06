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
        xnih__ujg = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, xnih__ujg)


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
        iscsm__yapf = args[0]
        mqwe__wypqb = signature.return_type
        qtxam__jwau = cgutils.create_struct_proxy(mqwe__wypqb)(context, builder
            )
        qtxam__jwau.obj = iscsm__yapf
        context.nrt.incref(builder, signature.args[0], iscsm__yapf)
        return qtxam__jwau._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for xgdr__cbl in keys:
        selection.remove(xgdr__cbl)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    mqwe__wypqb = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return mqwe__wypqb(obj_type, by_type, as_index_type, dropna_type), codegen


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
        grpby, oreny__aycue = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(oreny__aycue, (tuple, list)):
                if len(set(oreny__aycue).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_const_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(oreny__aycue).difference(set(grpby.
                        df_type.columns))))
                selection = oreny__aycue
            else:
                if oreny__aycue not in grpby.df_type.columns:
                    raise_const_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(oreny__aycue))
                selection = oreny__aycue,
                series_select = True
            utvi__bhs = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(utvi__bhs, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, oreny__aycue = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            oreny__aycue):
            utvi__bhs = StaticGetItemDataFrameGroupBy.generic(self, (grpby,
                get_literal_value(oreny__aycue)), {}).return_type
            return signature(utvi__bhs, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    cmzi__nyny = arr_type == ArrayItemArrayType(string_array_type)
    zobj__corej = arr_type.dtype
    if isinstance(zobj__corej, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {zobj__corej} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(zobj__corej, (
        Decimal128Type, types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {zobj__corej} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(zobj__corej
        , (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(zobj__corej, (types.Integer, types.Float, types.Boolean)
        ):
        if cmzi__nyny or zobj__corej == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(zobj__corej, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not zobj__corej.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {zobj__corej} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(zobj__corej, types.Boolean) and func_name in {'cumsum',
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
    zobj__corej = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(zobj__corej, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(zobj__corej, types.Integer):
            return IntDtype(zobj__corej)
        return zobj__corej
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        kdpvj__hhb = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{kdpvj__hhb}'."
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
    for xgdr__cbl in grp.keys:
        if multi_level_names:
            beqj__lxewu = xgdr__cbl, ''
        else:
            beqj__lxewu = xgdr__cbl
        vomva__snkj = grp.df_type.columns.index(xgdr__cbl)
        data = grp.df_type.data[vomva__snkj]
        out_columns.append(beqj__lxewu)
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
        eiq__kdnow = tuple(grp.df_type.columns.index(grp.keys[lzbu__xnf]) for
            lzbu__xnf in range(len(grp.keys)))
        cul__dgo = tuple(grp.df_type.data[vomva__snkj] for vomva__snkj in
            eiq__kdnow)
        index = MultiIndexType(cul__dgo, tuple(types.StringLiteral(
            xgdr__cbl) for xgdr__cbl in grp.keys))
    else:
        vomva__snkj = grp.df_type.columns.index(grp.keys[0])
        index = bodo.hiframes.pd_index_ext.array_type_to_index(grp.df_type.
            data[vomva__snkj], types.StringLiteral(grp.keys[0]))
    siwrj__ihu = {}
    game__ebl = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        siwrj__ihu[None, 'size'] = 'size'
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for oyle__buykr in columns:
            vomva__snkj = grp.df_type.columns.index(oyle__buykr)
            data = grp.df_type.data[vomva__snkj]
            lxp__ggew = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                lxp__ggew = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    qnmy__egwv = SeriesType(data.dtype, data, None, string_type
                        )
                    mns__bnc = get_const_func_output_type(func, (qnmy__egwv
                        ,), {}, typing_context, target_context)
                    if mns__bnc != ArrayItemArrayType(string_array_type):
                        mns__bnc = dtype_to_array_type(mns__bnc)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=oyle__buykr, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    gnca__ebnki = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    vkd__xlny = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    eljq__bpa = dict(numeric_only=gnca__ebnki, min_count=
                        vkd__xlny)
                    rfwo__wke = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        eljq__bpa, rfwo__wke, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    gnca__ebnki = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    vkd__xlny = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    eljq__bpa = dict(numeric_only=gnca__ebnki, min_count=
                        vkd__xlny)
                    rfwo__wke = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        eljq__bpa, rfwo__wke, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    gnca__ebnki = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    eljq__bpa = dict(numeric_only=gnca__ebnki)
                    rfwo__wke = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        eljq__bpa, rfwo__wke, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    huw__dbx = args[0] if len(args) > 0 else kws.pop('axis', 0)
                    fuslh__gmq = args[1] if len(args) > 1 else kws.pop('skipna'
                        , True)
                    eljq__bpa = dict(axis=huw__dbx, skipna=fuslh__gmq)
                    rfwo__wke = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        eljq__bpa, rfwo__wke, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    zuyn__wcl = args[0] if len(args) > 0 else kws.pop('ddof', 1
                        )
                    eljq__bpa = dict(ddof=zuyn__wcl)
                    rfwo__wke = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        eljq__bpa, rfwo__wke, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                mns__bnc, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                slnb__xli = mns__bnc
                out_data.append(slnb__xli)
                out_columns.append(oyle__buykr)
                if func_name == 'agg':
                    dju__zmhjp = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    siwrj__ihu[oyle__buykr, dju__zmhjp] = oyle__buykr
                else:
                    siwrj__ihu[oyle__buykr, func_name] = oyle__buykr
                out_column_type.append(lxp__ggew)
            else:
                game__ebl.append(err_msg)
    if func_name == 'sum':
        ewgm__uix = any([(giurg__hdz == ColumnType.NumericalColumn.value) for
            giurg__hdz in out_column_type])
        if ewgm__uix:
            out_data = [giurg__hdz for giurg__hdz, cwkqe__kctpg in zip(
                out_data, out_column_type) if cwkqe__kctpg != ColumnType.
                NonNumericalColumn.value]
            out_columns = [giurg__hdz for giurg__hdz, cwkqe__kctpg in zip(
                out_columns, out_column_type) if cwkqe__kctpg != ColumnType
                .NonNumericalColumn.value]
            siwrj__ihu = {}
            for oyle__buykr in out_columns:
                if grp.as_index is False and oyle__buykr in grp.keys:
                    continue
                siwrj__ihu[oyle__buykr, func_name] = oyle__buykr
    bbif__topzc = len(game__ebl)
    if len(out_data) == 0:
        if bbif__topzc == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(bbif__topzc, ' was' if bbif__topzc == 1 else
                's were', ','.join(game__ebl)))
    ucebn__dtfeu = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index):
        if isinstance(out_data[0], IntegerArrayType):
            kon__usmvp = IntDtype(out_data[0].dtype)
        else:
            kon__usmvp = out_data[0].dtype
        rconc__odjir = (types.none if func_name == 'size' else types.
            StringLiteral(grp.selection[0]))
        ucebn__dtfeu = SeriesType(kon__usmvp, index=index, name_typ=
            rconc__odjir)
    return signature(ucebn__dtfeu, *args), siwrj__ihu


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    gmj__erfv = True
    if isinstance(f_val, str):
        gmj__erfv = False
        hsko__gml = f_val
    elif is_overload_constant_str(f_val):
        gmj__erfv = False
        hsko__gml = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        gmj__erfv = False
        hsko__gml = bodo.utils.typing.get_builtin_function_name(f_val)
    if not gmj__erfv:
        if hsko__gml not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {hsko__gml}')
        utvi__bhs = DataFrameGroupByType(grp.df_type, grp.keys, (col,), grp
            .as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(utvi__bhs, (), hsko__gml, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            kecga__mviio = types.functions.MakeFunctionLiteral(f_val)
        else:
            kecga__mviio = f_val
        validate_udf('agg', kecga__mviio)
        func = get_overload_const_func(kecga__mviio, None)
        fusj__wcse = func.code if hasattr(func, 'code') else func.__code__
        hsko__gml = fusj__wcse.co_name
        utvi__bhs = DataFrameGroupByType(grp.df_type, grp.keys, (col,), grp
            .as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(utvi__bhs, (), 'agg', typing_context,
            target_context, kecga__mviio)[0].return_type
    return hsko__gml, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    kgc__hifx = kws and all(isinstance(imxz__sxh, types.Tuple) and len(
        imxz__sxh) == 2 for imxz__sxh in kws.values())
    if is_overload_none(func) and not kgc__hifx:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not kgc__hifx:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    pemq__ysphz = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if kgc__hifx or is_overload_constant_dict(func):
        if kgc__hifx:
            ywwxg__fzlm = [get_literal_value(icsm__icigx) for icsm__icigx,
                bhcm__iydsx in kws.values()]
            gbhiv__kidd = [get_literal_value(bfu__hxz) for bhcm__iydsx,
                bfu__hxz in kws.values()]
        else:
            npw__nbik = get_overload_constant_dict(func)
            ywwxg__fzlm = tuple(npw__nbik.keys())
            gbhiv__kidd = tuple(npw__nbik.values())
        if 'head' in gbhiv__kidd:
            raise BodoError(
                'Groupby.agg()/aggregate(): head cannot be mixed with other groupby operations.'
                )
        if any(oyle__buykr not in grp.selection and oyle__buykr not in grp.
            keys for oyle__buykr in ywwxg__fzlm):
            raise_const_error(
                f'Selected column names {ywwxg__fzlm} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            gbhiv__kidd)
        if kgc__hifx and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        siwrj__ihu = {}
        out_columns = []
        out_data = []
        out_column_type = []
        dmw__dgwxu = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for gntb__kwadn, f_val in zip(ywwxg__fzlm, gbhiv__kidd):
            if isinstance(f_val, (tuple, list)):
                eueho__sapxz = 0
                for kecga__mviio in f_val:
                    hsko__gml, out_tp = get_agg_funcname_and_outtyp(grp,
                        gntb__kwadn, kecga__mviio, typing_context,
                        target_context)
                    pemq__ysphz = hsko__gml in list_cumulative
                    if hsko__gml == '<lambda>' and len(f_val) > 1:
                        hsko__gml = '<lambda_' + str(eueho__sapxz) + '>'
                        eueho__sapxz += 1
                    out_columns.append((gntb__kwadn, hsko__gml))
                    siwrj__ihu[gntb__kwadn, hsko__gml] = gntb__kwadn, hsko__gml
                    _append_out_type(grp, out_data, out_tp)
            else:
                hsko__gml, out_tp = get_agg_funcname_and_outtyp(grp,
                    gntb__kwadn, f_val, typing_context, target_context)
                pemq__ysphz = hsko__gml in list_cumulative
                if multi_level_names:
                    out_columns.append((gntb__kwadn, hsko__gml))
                    siwrj__ihu[gntb__kwadn, hsko__gml] = gntb__kwadn, hsko__gml
                elif not kgc__hifx:
                    out_columns.append(gntb__kwadn)
                    siwrj__ihu[gntb__kwadn, hsko__gml] = gntb__kwadn
                elif kgc__hifx:
                    dmw__dgwxu.append(hsko__gml)
                _append_out_type(grp, out_data, out_tp)
        if kgc__hifx:
            for lzbu__xnf, crfp__bqv in enumerate(kws.keys()):
                out_columns.append(crfp__bqv)
                siwrj__ihu[ywwxg__fzlm[lzbu__xnf], dmw__dgwxu[lzbu__xnf]
                    ] = crfp__bqv
        if pemq__ysphz:
            index = grp.df_type.index
        else:
            index = out_tp.index
        ucebn__dtfeu = DataFrameType(tuple(out_data), index, tuple(out_columns)
            )
        return signature(ucebn__dtfeu, *args), siwrj__ihu
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
        eueho__sapxz = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        siwrj__ihu = {}
        duuad__lkkl = grp.selection[0]
        for f_val in func.types:
            hsko__gml, out_tp = get_agg_funcname_and_outtyp(grp,
                duuad__lkkl, f_val, typing_context, target_context)
            pemq__ysphz = hsko__gml in list_cumulative
            if hsko__gml == '<lambda>':
                hsko__gml = '<lambda_' + str(eueho__sapxz) + '>'
                eueho__sapxz += 1
            out_columns.append(hsko__gml)
            siwrj__ihu[duuad__lkkl, hsko__gml] = hsko__gml
            _append_out_type(grp, out_data, out_tp)
        if pemq__ysphz:
            index = grp.df_type.index
        else:
            index = out_tp.index
        ucebn__dtfeu = DataFrameType(tuple(out_data), index, tuple(out_columns)
            )
        return signature(ucebn__dtfeu, *args), siwrj__ihu
    hsko__gml = ''
    if types.unliteral(func) == types.unicode_type:
        hsko__gml = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        hsko__gml = bodo.utils.typing.get_builtin_function_name(func)
    if hsko__gml:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, hsko__gml, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = grp.df_type.index
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        huw__dbx = args[0] if len(args) > 0 else kws.pop('axis', 0)
        gnca__ebnki = args[1] if len(args) > 1 else kws.pop('numeric_only',
            False)
        fuslh__gmq = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        eljq__bpa = dict(axis=huw__dbx, numeric_only=gnca__ebnki)
        rfwo__wke = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', eljq__bpa,
            rfwo__wke, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        kfq__sft = args[0] if len(args) > 0 else kws.pop('periods', 1)
        eww__itoji = args[1] if len(args) > 1 else kws.pop('freq', None)
        huw__dbx = args[2] if len(args) > 2 else kws.pop('axis', 0)
        kdl__kyoz = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        eljq__bpa = dict(freq=eww__itoji, axis=huw__dbx, fill_value=kdl__kyoz)
        rfwo__wke = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', eljq__bpa,
            rfwo__wke, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        pafic__bakjs = args[0] if len(args) > 0 else kws.pop('func', None)
        sqywx__pffu = kws.pop('engine', None)
        ydp__asfk = kws.pop('engine_kwargs', None)
        eljq__bpa = dict(engine=sqywx__pffu, engine_kwargs=ydp__asfk)
        rfwo__wke = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', eljq__bpa, rfwo__wke,
            package_name='pandas', module_name='GroupBy')
    siwrj__ihu = {}
    for oyle__buykr in grp.selection:
        out_columns.append(oyle__buykr)
        siwrj__ihu[oyle__buykr, name_operation] = oyle__buykr
        vomva__snkj = grp.df_type.columns.index(oyle__buykr)
        data = grp.df_type.data[vomva__snkj]
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
            mns__bnc, err_msg = get_groupby_output_dtype(data,
                get_literal_value(pafic__bakjs), grp.df_type.index)
            if err_msg == 'ok':
                data = mns__bnc
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    ucebn__dtfeu = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        ucebn__dtfeu = SeriesType(out_data[0].dtype, data=out_data[0],
            index=index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(ucebn__dtfeu, *args), siwrj__ihu


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
        zla__xsgc = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        ngyh__zprke = isinstance(zla__xsgc, (SeriesType,
            HeterogeneousSeriesType)
            ) and zla__xsgc.const_info is not None or not isinstance(zla__xsgc,
            (SeriesType, DataFrameType))
        if ngyh__zprke:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                sdtrb__fvroo = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                eiq__kdnow = tuple(grp.df_type.columns.index(grp.keys[
                    lzbu__xnf]) for lzbu__xnf in range(len(grp.keys)))
                cul__dgo = tuple(grp.df_type.data[vomva__snkj] for
                    vomva__snkj in eiq__kdnow)
                sdtrb__fvroo = MultiIndexType(cul__dgo, tuple(types.literal
                    (xgdr__cbl) for xgdr__cbl in grp.keys))
            else:
                vomva__snkj = grp.df_type.columns.index(grp.keys[0])
                sdtrb__fvroo = bodo.hiframes.pd_index_ext.array_type_to_index(
                    grp.df_type.data[vomva__snkj], types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            hbgmx__lunz = tuple(grp.df_type.data[grp.df_type.columns.index(
                oyle__buykr)] for oyle__buykr in grp.keys)
            tpxhe__rvkfm = tuple(types.literal(imxz__sxh) for imxz__sxh in
                grp.keys) + get_index_name_types(zla__xsgc.index)
            if not grp.as_index:
                hbgmx__lunz = types.Array(types.int64, 1, 'C'),
                tpxhe__rvkfm = (types.none,) + get_index_name_types(zla__xsgc
                    .index)
            sdtrb__fvroo = MultiIndexType(hbgmx__lunz +
                get_index_data_arr_types(zla__xsgc.index), tpxhe__rvkfm)
        if ngyh__zprke:
            if isinstance(zla__xsgc, HeterogeneousSeriesType):
                bhcm__iydsx, xyir__mgvn = zla__xsgc.const_info
                dwb__ybml = tuple(dtype_to_array_type(nfx__jlopy) for
                    nfx__jlopy in zla__xsgc.data.types)
                wbv__mfmp = DataFrameType(out_data + dwb__ybml,
                    sdtrb__fvroo, out_columns + xyir__mgvn)
            elif isinstance(zla__xsgc, SeriesType):
                myd__kwkak, xyir__mgvn = zla__xsgc.const_info
                dwb__ybml = tuple(dtype_to_array_type(zla__xsgc.dtype) for
                    bhcm__iydsx in range(myd__kwkak))
                wbv__mfmp = DataFrameType(out_data + dwb__ybml,
                    sdtrb__fvroo, out_columns + xyir__mgvn)
            else:
                uuwsp__llf = get_udf_out_arr_type(zla__xsgc)
                if not grp.as_index:
                    wbv__mfmp = DataFrameType(out_data + (uuwsp__llf,),
                        sdtrb__fvroo, out_columns + ('',))
                else:
                    wbv__mfmp = SeriesType(uuwsp__llf.dtype, uuwsp__llf,
                        sdtrb__fvroo, None)
        elif isinstance(zla__xsgc, SeriesType):
            wbv__mfmp = SeriesType(zla__xsgc.dtype, zla__xsgc.data,
                sdtrb__fvroo, zla__xsgc.name_typ)
        else:
            wbv__mfmp = DataFrameType(zla__xsgc.data, sdtrb__fvroo,
                zla__xsgc.columns)
        aih__seotb = gen_apply_pysig(len(f_args), kws.keys())
        cad__kpgnx = (func, *f_args) + tuple(kws.values())
        return signature(wbv__mfmp, *cad__kpgnx).replace(pysig=aih__seotb)

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
    pvkv__radfu = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            gntb__kwadn = grp.selection[0]
            uuwsp__llf = pvkv__radfu.data[pvkv__radfu.columns.index(
                gntb__kwadn)]
            euhp__vgbfq = SeriesType(uuwsp__llf.dtype, uuwsp__llf,
                pvkv__radfu.index, types.literal(gntb__kwadn))
        else:
            zyoae__dktq = tuple(pvkv__radfu.data[pvkv__radfu.columns.index(
                oyle__buykr)] for oyle__buykr in grp.selection)
            euhp__vgbfq = DataFrameType(zyoae__dktq, pvkv__radfu.index,
                tuple(grp.selection))
    else:
        euhp__vgbfq = pvkv__radfu
    svyl__jutil = euhp__vgbfq,
    svyl__jutil += tuple(f_args)
    try:
        zla__xsgc = get_const_func_output_type(func, svyl__jutil, kws,
            typing_context, target_context)
    except Exception as ebj__cop:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', ebj__cop),
            getattr(ebj__cop, 'loc', None))
    return zla__xsgc


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    svyl__jutil = (grp,) + f_args
    try:
        zla__xsgc = get_const_func_output_type(func, svyl__jutil, kws, self
            .context, numba.core.registry.cpu_target.target_context, False)
    except Exception as ebj__cop:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', ebj__cop),
            getattr(ebj__cop, 'loc', None))
    aih__seotb = gen_apply_pysig(len(f_args), kws.keys())
    cad__kpgnx = (func, *f_args) + tuple(kws.values())
    return signature(zla__xsgc, *cad__kpgnx).replace(pysig=aih__seotb)


def gen_apply_pysig(n_args, kws):
    kpaau__frtbs = ', '.join(f'arg{lzbu__xnf}' for lzbu__xnf in range(n_args))
    kpaau__frtbs = kpaau__frtbs + ', ' if kpaau__frtbs else ''
    tivdy__ysuu = ', '.join(f"{nttk__npbda} = ''" for nttk__npbda in kws)
    yylie__lzj = f'def apply_stub(func, {kpaau__frtbs}{tivdy__ysuu}):\n'
    yylie__lzj += '    pass\n'
    jzt__kezc = {}
    exec(yylie__lzj, {}, jzt__kezc)
    pdskb__ahlyz = jzt__kezc['apply_stub']
    return numba.core.utils.pysignature(pdskb__ahlyz)


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
        mns__bnc = get_pivot_output_dtype(data, aggfunc.literal_value)
        dcy__lwym = dtype_to_array_type(mns__bnc)
        if is_overload_none(_pivot_values):
            raise_bodo_error(
                'Dataframe.pivot_table() requires explicit annotation to determine output columns. For more information, see: https://docs.bodo.ai/latest/source/programming_with_bodo/pandas.html'
                )
        uksix__senwt = _pivot_values.meta
        uex__xqb = len(uksix__senwt)
        vomva__snkj = df.columns.index(index)
        cgtg__rxyv = bodo.hiframes.pd_index_ext.array_type_to_index(df.data
            [vomva__snkj], types.StringLiteral(index))
        zpscz__eswlu = DataFrameType((dcy__lwym,) * uex__xqb, cgtg__rxyv,
            tuple(uksix__senwt))
        return signature(zpscz__eswlu, *args)


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
        dcy__lwym = types.Array(types.int64, 1, 'C')
        uksix__senwt = _pivot_values.meta
        uex__xqb = len(uksix__senwt)
        cgtg__rxyv = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        zpscz__eswlu = DataFrameType((dcy__lwym,) * uex__xqb, cgtg__rxyv,
            tuple(uksix__senwt))
        return signature(zpscz__eswlu, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    yylie__lzj = 'def impl(keys, dropna, _is_parallel):\n'
    yylie__lzj += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    yylie__lzj += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{lzbu__xnf}])' for lzbu__xnf in range(len(keys
        .types))))
    yylie__lzj += '    table = arr_info_list_to_table(info_list)\n'
    yylie__lzj += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    yylie__lzj += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    yylie__lzj += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    yylie__lzj += '    delete_table_decref_arrays(table)\n'
    yylie__lzj += '    ev.finalize()\n'
    yylie__lzj += '    return sort_idx, group_labels, ngroups\n'
    jzt__kezc = {}
    exec(yylie__lzj, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, jzt__kezc)
    nndz__flf = jzt__kezc['impl']
    return nndz__flf


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    ufdu__btj = len(labels)
    xtuvj__qxmud = np.zeros(ngroups, dtype=np.int64)
    hdr__yqtq = np.zeros(ngroups, dtype=np.int64)
    obrg__vqtty = 0
    oznvg__lspt = 0
    for lzbu__xnf in range(ufdu__btj):
        vwpac__uxfn = labels[lzbu__xnf]
        if vwpac__uxfn < 0:
            obrg__vqtty += 1
        else:
            oznvg__lspt += 1
            if lzbu__xnf == ufdu__btj - 1 or vwpac__uxfn != labels[
                lzbu__xnf + 1]:
                xtuvj__qxmud[vwpac__uxfn] = obrg__vqtty
                hdr__yqtq[vwpac__uxfn] = obrg__vqtty + oznvg__lspt
                obrg__vqtty += oznvg__lspt
                oznvg__lspt = 0
    return xtuvj__qxmud, hdr__yqtq


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    myd__kwkak = len(df.columns)
    pvklv__aac = len(keys.types)
    iedoy__ogu = ', '.join('data_{}'.format(lzbu__xnf) for lzbu__xnf in
        range(myd__kwkak))
    yylie__lzj = 'def impl(df, keys, _is_parallel):\n'
    for lzbu__xnf in range(myd__kwkak):
        yylie__lzj += f"""  in_arr{lzbu__xnf} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {lzbu__xnf})
"""
    yylie__lzj += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    yylie__lzj += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{lzbu__xnf}])' for lzbu__xnf in range(
        pvklv__aac)), ', '.join(f'array_to_info(in_arr{lzbu__xnf})' for
        lzbu__xnf in range(myd__kwkak)), 'array_to_info(in_index_arr)')
    yylie__lzj += '  table = arr_info_list_to_table(info_list)\n'
    yylie__lzj += (
        f'  out_table = shuffle_table(table, {pvklv__aac}, _is_parallel, 1)\n')
    for lzbu__xnf in range(pvklv__aac):
        yylie__lzj += f"""  out_key{lzbu__xnf} = info_to_array(info_from_table(out_table, {lzbu__xnf}), keys[{lzbu__xnf}])
"""
    for lzbu__xnf in range(myd__kwkak):
        yylie__lzj += f"""  out_arr{lzbu__xnf} = info_to_array(info_from_table(out_table, {lzbu__xnf + pvklv__aac}), in_arr{lzbu__xnf})
"""
    yylie__lzj += f"""  out_arr_index = info_to_array(info_from_table(out_table, {pvklv__aac + myd__kwkak}), in_index_arr)
"""
    yylie__lzj += '  shuffle_info = get_shuffle_info(out_table)\n'
    yylie__lzj += '  delete_table(out_table)\n'
    yylie__lzj += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{lzbu__xnf}' for lzbu__xnf in range(
        myd__kwkak))
    yylie__lzj += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    yylie__lzj += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, {gen_const_tup(df.columns)})
"""
    yylie__lzj += '  return out_df, ({},), shuffle_info\n'.format(', '.join
        (f'out_key{lzbu__xnf}' for lzbu__xnf in range(pvklv__aac)))
    jzt__kezc = {}
    exec(yylie__lzj, {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info}, jzt__kezc)
    nndz__flf = jzt__kezc['impl']
    return nndz__flf


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        eoczq__hmmpz = len(data.array_types)
        yylie__lzj = 'def impl(data, shuffle_info):\n'
        yylie__lzj += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{lzbu__xnf}])' for lzbu__xnf in
            range(eoczq__hmmpz)))
        yylie__lzj += '  table = arr_info_list_to_table(info_list)\n'
        yylie__lzj += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for lzbu__xnf in range(eoczq__hmmpz):
            yylie__lzj += f"""  out_arr{lzbu__xnf} = info_to_array(info_from_table(out_table, {lzbu__xnf}), data._data[{lzbu__xnf}])
"""
        yylie__lzj += '  delete_table(out_table)\n'
        yylie__lzj += '  delete_table(table)\n'
        yylie__lzj += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{lzbu__xnf}' for lzbu__xnf in range(
            eoczq__hmmpz))))
        jzt__kezc = {}
        exec(yylie__lzj, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, jzt__kezc)
        nndz__flf = jzt__kezc['impl']
        return nndz__flf
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            ncomi__odgh = bodo.utils.conversion.index_to_array(data)
            slnb__xli = reverse_shuffle(ncomi__odgh, shuffle_info)
            return bodo.utils.conversion.index_from_array(slnb__xli)
        return impl_index

    def impl_arr(data, shuffle_info):
        npck__kgtap = [array_to_info(data)]
        ulirk__ntwa = arr_info_list_to_table(npck__kgtap)
        aapor__otg = reverse_shuffle_table(ulirk__ntwa, shuffle_info)
        slnb__xli = info_to_array(info_from_table(aapor__otg, 0), data)
        delete_table(aapor__otg)
        delete_table(ulirk__ntwa)
        return slnb__xli
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    eljq__bpa = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    rfwo__wke = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', eljq__bpa, rfwo__wke,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    wstt__ggte = get_overload_const_bool(ascending)
    wsu__zzxu = grp.selection[0]
    yylie__lzj = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    ijc__nuyjt = (
        f"lambda S: S.value_counts(ascending={wstt__ggte}, _index_name='{wsu__zzxu}')"
        )
    yylie__lzj += f'    return grp.apply({ijc__nuyjt})\n'
    jzt__kezc = {}
    exec(yylie__lzj, {'bodo': bodo}, jzt__kezc)
    nndz__flf = jzt__kezc['impl']
    return nndz__flf


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
    for isxu__najwb in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, isxu__najwb, no_unliteral=True
            )(create_unsupported_overload(f'DataFrameGroupBy.{isxu__najwb}'))
    for isxu__najwb in groupby_unsupported:
        overload_method(DataFrameGroupByType, isxu__najwb, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{isxu__najwb}'))
    for isxu__najwb in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, isxu__najwb, no_unliteral=True
            )(create_unsupported_overload(f'SeriesGroupBy.{isxu__najwb}'))
    for isxu__najwb in series_only_unsupported:
        overload_method(DataFrameGroupByType, isxu__najwb, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{isxu__najwb}'))
    for isxu__najwb in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, isxu__najwb, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{isxu__najwb}'))


_install_groupy_unsupported()
