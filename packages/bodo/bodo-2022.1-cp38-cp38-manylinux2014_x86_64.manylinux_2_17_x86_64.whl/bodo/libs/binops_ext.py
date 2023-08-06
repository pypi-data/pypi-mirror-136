""" Implementation of binary operators for the different types.
    Currently implemented operators:
        arith: add, sub, mul, truediv, floordiv, mod, pow
        cmp: lt, le, eq, ne, ge, gt
"""
import operator
import numba
from numba.core import types
from numba.core.imputils import lower_builtin
from numba.core.typing.builtins import machine_ints
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type, datetime_timedelta_type
from bodo.hiframes.datetime_timedelta_ext import datetime_datetime_type, datetime_timedelta_array_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import DatetimeIndexType, HeterogeneousIndexType, is_index_type
from bodo.hiframes.pd_offsets_ext import date_offset_type, month_begin_type, month_end_type, week_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.series_impl import SeriesType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.typing import BodoError, is_overload_bool, is_timedelta_type


class SeriesCmpOpTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        lhs, rhs = args
        if cmp_timeseries(lhs, rhs) or (isinstance(lhs, DataFrameType) or
            isinstance(rhs, DataFrameType)) or not (isinstance(lhs,
            SeriesType) or isinstance(rhs, SeriesType)):
            return
        xags__hjhbx = lhs.data if isinstance(lhs, SeriesType) else lhs
        wyj__ygo = rhs.data if isinstance(rhs, SeriesType) else rhs
        if xags__hjhbx in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and wyj__ygo.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            xags__hjhbx = wyj__ygo.dtype
        elif wyj__ygo in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and xags__hjhbx.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            wyj__ygo = xags__hjhbx.dtype
        ayavg__vtf = xags__hjhbx, wyj__ygo
        ugxx__qzs = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            lejuq__ozisr = self.context.resolve_function_type(self.key,
                ayavg__vtf, {}).return_type
        except Exception as kqgvr__agnnj:
            raise BodoError(ugxx__qzs)
        if is_overload_bool(lejuq__ozisr):
            raise BodoError(ugxx__qzs)
        qxaww__qdq = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        plmp__exbvl = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        ncd__ziwip = types.bool_
        iad__tqrbx = SeriesType(ncd__ziwip, lejuq__ozisr, qxaww__qdq,
            plmp__exbvl)
        return iad__tqrbx(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        ile__owj = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if ile__owj is None:
            ile__owj = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, ile__owj, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        xags__hjhbx = lhs.data if isinstance(lhs, SeriesType) else lhs
        wyj__ygo = rhs.data if isinstance(rhs, SeriesType) else rhs
        ayavg__vtf = xags__hjhbx, wyj__ygo
        ugxx__qzs = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            lejuq__ozisr = self.context.resolve_function_type(self.key,
                ayavg__vtf, {}).return_type
        except Exception as ezljo__etcqj:
            raise BodoError(ugxx__qzs)
        qxaww__qdq = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        plmp__exbvl = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        ncd__ziwip = lejuq__ozisr.dtype
        iad__tqrbx = SeriesType(ncd__ziwip, lejuq__ozisr, qxaww__qdq,
            plmp__exbvl)
        return iad__tqrbx(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        ile__owj = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if ile__owj is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                ile__owj = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, ile__owj, sig, args)
    return lower_and_or_impl


def overload_add_operator_scalars(lhs, rhs):
    if lhs == week_type or rhs == week_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_week_offset_type(lhs, rhs))
    if lhs == month_begin_type or rhs == month_begin_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_begin_offset_type(lhs, rhs))
    if lhs == month_end_type or rhs == month_end_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_end_offset_type(lhs, rhs))
    if lhs == date_offset_type or rhs == date_offset_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_date_offset_type(lhs, rhs))
    if add_timestamp(lhs, rhs):
        return bodo.hiframes.pd_timestamp_ext.overload_add_operator_timestamp(
            lhs, rhs)
    if add_dt_td_and_dt_date(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_add_operator_datetime_date(lhs, rhs))
    if add_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_add_operator_datetime_timedelta(lhs, rhs))
    raise_error_if_not_numba_supported(operator.add, lhs, rhs)


def overload_sub_operator_scalars(lhs, rhs):
    if sub_offset_to_datetime_or_timestamp(lhs, rhs):
        return bodo.hiframes.pd_offsets_ext.overload_sub_operator_offsets(lhs,
            rhs)
    if lhs == pd_timestamp_type and rhs in [pd_timestamp_type,
        datetime_timedelta_type, pd_timedelta_type]:
        return bodo.hiframes.pd_timestamp_ext.overload_sub_operator_timestamp(
            lhs, rhs)
    if sub_dt_or_td(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_sub_operator_datetime_date(lhs, rhs))
    if sub_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_sub_operator_datetime_timedelta(lhs, rhs))
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
        return (bodo.hiframes.datetime_datetime_ext.
            overload_sub_operator_datetime_datetime(lhs, rhs))
    raise_error_if_not_numba_supported(operator.sub, lhs, rhs)


def create_overload_arith_op(op):

    def overload_arith_operator(lhs, rhs):
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if time_series_operation(lhs, rhs) and op in [operator.add,
            operator.sub]:
            return bodo.hiframes.series_dt_impl.create_bin_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return bodo.hiframes.series_impl.create_binary_op_overload(op)(lhs,
                rhs)
        if sub_dt_index_and_timestamp(lhs, rhs) and op == operator.sub:
            return (bodo.hiframes.pd_index_ext.
                overload_sub_operator_datetime_index(lhs, rhs))
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if args_td_and_int_array(lhs, rhs):
            return bodo.libs.int_arr_ext.get_int_array_op_pd_td(op)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if op == operator.add and (lhs == string_array_type or types.
            unliteral(lhs) == string_type):
            return bodo.libs.str_arr_ext.overload_add_operator_string_array(lhs
                , rhs)
        if op == operator.add:
            return overload_add_operator_scalars(lhs, rhs)
        if op == operator.sub:
            return overload_sub_operator_scalars(lhs, rhs)
        if op == operator.mul:
            if mul_timedelta_and_int(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mul_operator_timedelta(lhs, rhs))
            if mul_string_arr_and_int(lhs, rhs):
                return bodo.libs.str_arr_ext.overload_mul_operator_str_arr(lhs,
                    rhs)
            if mul_date_offset_and_int(lhs, rhs):
                return (bodo.hiframes.pd_offsets_ext.
                    overload_mul_date_offset_types(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op in [operator.truediv, operator.floordiv]:
            if div_timedelta_and_int(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_pd_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_pd_timedelta(lhs, rhs))
            if div_datetime_timedelta(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_dt_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_dt_timedelta(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.mod:
            if mod_timedeltas(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mod_operator_timedeltas(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.pow:
            raise_error_if_not_numba_supported(op, lhs, rhs)
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_arith_operator


def create_overload_cmp_operator(op):

    def overload_cmp_operator(lhs, rhs):
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if cmp_timeseries(lhs, rhs):
            return bodo.hiframes.series_dt_impl.create_cmp_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return
        if lhs == datetime_date_array_type or rhs == datetime_date_array_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload_arr(
                op)(lhs, rhs)
        if (lhs == datetime_timedelta_array_type or rhs ==
            datetime_timedelta_array_type):
            ile__owj = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return ile__owj(lhs, rhs)
        if lhs == string_array_type or rhs == string_array_type:
            return bodo.libs.str_arr_ext.create_binary_op_overload(op)(lhs, rhs
                )
        if isinstance(lhs, Decimal128Type) and isinstance(rhs, Decimal128Type):
            return bodo.libs.decimal_arr_ext.decimal_create_cmp_op_overload(op
                )(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if binary_array_cmp(lhs, rhs):
            return bodo.libs.binary_arr_ext.create_binary_cmp_op_overload(op)(
                lhs, rhs)
        if cmp_dt_index_to_string(lhs, rhs):
            return bodo.hiframes.pd_index_ext.overload_binop_dti_str(op)(lhs,
                rhs)
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if lhs == datetime_date_type and rhs == datetime_date_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload(op)(
                lhs, rhs)
        if can_cmp_date_datetime(lhs, rhs, op):
            return (bodo.hiframes.datetime_date_ext.
                create_datetime_date_cmp_op_overload(op)(lhs, rhs))
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
            return bodo.hiframes.datetime_datetime_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:
            return bodo.hiframes.datetime_timedelta_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if cmp_timedeltas(lhs, rhs):
            ile__owj = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return ile__owj(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    ekdv__ovby = lhs == datetime_timedelta_type and rhs == datetime_date_type
    qxcji__dsli = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return ekdv__ovby or qxcji__dsli


def add_timestamp(lhs, rhs):
    dnv__httm = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    ekhc__dyhn = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return dnv__httm or ekhc__dyhn


def add_datetime_and_timedeltas(lhs, rhs):
    vldq__bfejy = [datetime_timedelta_type, pd_timedelta_type]
    ftmq__hio = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    mrq__guv = lhs in vldq__bfejy and rhs in vldq__bfejy
    czr__hqbi = (lhs == datetime_datetime_type and rhs in vldq__bfejy or 
        rhs == datetime_datetime_type and lhs in vldq__bfejy)
    return mrq__guv or czr__hqbi


def mul_string_arr_and_int(lhs, rhs):
    wyj__ygo = isinstance(lhs, types.Integer) and rhs == string_array_type
    xags__hjhbx = lhs == string_array_type and isinstance(rhs, types.Integer)
    return wyj__ygo or xags__hjhbx


def mul_timedelta_and_int(lhs, rhs):
    ekdv__ovby = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    qxcji__dsli = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return ekdv__ovby or qxcji__dsli


def mul_date_offset_and_int(lhs, rhs):
    evhyk__gsrqp = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    een__cha = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return evhyk__gsrqp or een__cha


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    qxr__qsdy = [datetime_datetime_type, pd_timestamp_type, datetime_date_type]
    frxzb__pda = [date_offset_type, month_begin_type, month_end_type, week_type
        ]
    return rhs in frxzb__pda and lhs in qxr__qsdy


def sub_dt_index_and_timestamp(lhs, rhs):
    hiub__nyt = isinstance(lhs, DatetimeIndexType) and rhs == pd_timestamp_type
    iswh__llh = isinstance(rhs, DatetimeIndexType) and lhs == pd_timestamp_type
    return hiub__nyt or iswh__llh


def sub_dt_or_td(lhs, rhs):
    nikww__apo = lhs == datetime_date_type and rhs == datetime_timedelta_type
    jvwn__caql = lhs == datetime_date_type and rhs == datetime_date_type
    aznu__vzeix = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return nikww__apo or jvwn__caql or aznu__vzeix


def sub_datetime_and_timedeltas(lhs, rhs):
    yrw__uiu = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    sxa__vyky = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return yrw__uiu or sxa__vyky


def div_timedelta_and_int(lhs, rhs):
    mrq__guv = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    fuae__gawh = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return mrq__guv or fuae__gawh


def div_datetime_timedelta(lhs, rhs):
    mrq__guv = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    fuae__gawh = lhs == datetime_timedelta_type and rhs == types.int64
    return mrq__guv or fuae__gawh


def mod_timedeltas(lhs, rhs):
    iwja__rpv = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    rjvn__bqg = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return iwja__rpv or rjvn__bqg


def cmp_dt_index_to_string(lhs, rhs):
    hiub__nyt = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    iswh__llh = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return hiub__nyt or iswh__llh


def cmp_timestamp_or_date(lhs, rhs):
    ess__kcps = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    bimdv__vtztt = (lhs == bodo.hiframes.datetime_date_ext.
        datetime_date_type and rhs == pd_timestamp_type)
    vqpva__kyv = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    bcksb__ryskk = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    rjl__iwni = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return ess__kcps or bimdv__vtztt or vqpva__kyv or bcksb__ryskk or rjl__iwni


def cmp_timeseries(lhs, rhs):
    lmj__xmv = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    sgbns__fha = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    spifd__evjgf = lmj__xmv or sgbns__fha
    jgjlx__adav = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    ocg__msi = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    xam__zxjon = jgjlx__adav or ocg__msi
    return spifd__evjgf or xam__zxjon


def cmp_timedeltas(lhs, rhs):
    mrq__guv = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in mrq__guv and rhs in mrq__guv


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    jdqqr__ysxf = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return jdqqr__ysxf


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    pwd__cxvex = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    vdqiy__giqkm = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    exb__syhk = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    pqrr__siw = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return pwd__cxvex or vdqiy__giqkm or exb__syhk or pqrr__siw


def args_td_and_int_array(lhs, rhs):
    rsgku__ukux = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    romb__kbwb = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return rsgku__ukux and romb__kbwb


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        qxcji__dsli = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        ekdv__ovby = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        nvn__gdn = qxcji__dsli or ekdv__ovby
        hwnq__gns = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        dzxd__ojfvy = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        afm__knds = hwnq__gns or dzxd__ojfvy
        cwq__jsw = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        gbdv__agiut = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        zbjm__kww = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        wjpxc__isb = cwq__jsw or gbdv__agiut or zbjm__kww
        yuz__jnv = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        qne__dqs = isinstance(lhs, tys) or isinstance(rhs, tys)
        cafa__frbs = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (nvn__gdn or afm__knds or wjpxc__isb or yuz__jnv or qne__dqs or
            cafa__frbs)
    if op == operator.pow:
        bln__hie = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        vttd__szi = isinstance(lhs, types.Float) and isinstance(rhs, (types
            .IntegerLiteral, types.Float, types.Integer) or rhs in types.
            unsigned_domain or rhs in types.signed_domain)
        zbjm__kww = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        cafa__frbs = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return bln__hie or vttd__szi or zbjm__kww or cafa__frbs
    if op == operator.floordiv:
        gbdv__agiut = lhs in types.real_domain and rhs in types.real_domain
        cwq__jsw = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        sido__ifs = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        mrq__guv = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, (
            types.Integer, types.Float, types.NPTimedelta))
        cafa__frbs = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return gbdv__agiut or cwq__jsw or sido__ifs or mrq__guv or cafa__frbs
    if op == operator.truediv:
        hdzvd__ftc = lhs in machine_ints and rhs in machine_ints
        gbdv__agiut = lhs in types.real_domain and rhs in types.real_domain
        zbjm__kww = lhs in types.complex_domain and rhs in types.complex_domain
        cwq__jsw = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        sido__ifs = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        skgyz__jqop = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        mrq__guv = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, (
            types.Integer, types.Float, types.NPTimedelta))
        cafa__frbs = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (hdzvd__ftc or gbdv__agiut or zbjm__kww or cwq__jsw or
            sido__ifs or skgyz__jqop or mrq__guv or cafa__frbs)
    if op == operator.mod:
        hdzvd__ftc = lhs in machine_ints and rhs in machine_ints
        gbdv__agiut = lhs in types.real_domain and rhs in types.real_domain
        cwq__jsw = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        sido__ifs = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        cafa__frbs = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return hdzvd__ftc or gbdv__agiut or cwq__jsw or sido__ifs or cafa__frbs
    if op == operator.add or op == operator.sub:
        nvn__gdn = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        dnqkk__ljo = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        dvysd__zikt = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        tqi__tph = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        cwq__jsw = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        gbdv__agiut = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        zbjm__kww = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        wjpxc__isb = cwq__jsw or gbdv__agiut or zbjm__kww
        cafa__frbs = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        mltd__leya = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        yuz__jnv = isinstance(lhs, types.List) and isinstance(rhs, types.List)
        gqis__tphw = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        hdv__rsefk = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        nii__ctmq = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        vwnk__inj = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        jtyr__csqw = gqis__tphw or hdv__rsefk or nii__ctmq or vwnk__inj
        afm__knds = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        mpcoj__dxnap = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        qarr__yfvp = afm__knds or mpcoj__dxnap
        bzyhd__hremq = lhs == types.NPTimedelta and rhs == types.NPDatetime
        tgct__iqew = (mltd__leya or yuz__jnv or jtyr__csqw or qarr__yfvp or
            bzyhd__hremq)
        bhytp__sxd = op == operator.add and tgct__iqew
        return (nvn__gdn or dnqkk__ljo or dvysd__zikt or tqi__tph or
            wjpxc__isb or cafa__frbs or bhytp__sxd)


def cmp_op_supported_by_numba(lhs, rhs):
    cafa__frbs = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    yuz__jnv = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    nvn__gdn = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, types
        .NPTimedelta)
    pzmdi__gfhaw = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    afm__knds = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    mltd__leya = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types
        .BaseTuple)
    tqi__tph = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    wjpxc__isb = isinstance(lhs, types.Number) and isinstance(rhs, types.Number
        )
    uxjxt__aes = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    dyeyg__bnfb = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    xea__mde = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    njmsu__vsay = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    mrth__frn = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (yuz__jnv or nvn__gdn or pzmdi__gfhaw or afm__knds or mltd__leya or
        tqi__tph or wjpxc__isb or uxjxt__aes or dyeyg__bnfb or xea__mde or
        cafa__frbs or njmsu__vsay or mrth__frn)


def raise_error_if_not_numba_supported(op, lhs, rhs):
    if arith_op_supported_by_numba(op, lhs, rhs):
        return
    raise BodoError(
        f'{op} operator not supported for data types {lhs} and {rhs}.')


def _install_series_and_or():
    for op in (operator.or_, operator.and_):
        infer_global(op)(SeriesAndOrTyper)
        lower_impl = lower_series_and_or(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)


_install_series_and_or()


def _install_cmp_ops():
    for op in (operator.lt, operator.eq, operator.ne, operator.ge, operator
        .gt, operator.le):
        infer_global(op)(SeriesCmpOpTemplate)
        lower_impl = series_cmp_op_lower(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)
        vmun__uoug = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(vmun__uoug)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        vmun__uoug = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(vmun__uoug)


install_arith_ops()
