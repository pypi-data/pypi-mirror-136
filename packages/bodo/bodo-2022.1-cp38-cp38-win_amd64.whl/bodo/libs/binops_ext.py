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
        goi__cerew = lhs.data if isinstance(lhs, SeriesType) else lhs
        vsmi__iyuw = rhs.data if isinstance(rhs, SeriesType) else rhs
        if goi__cerew in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and vsmi__iyuw.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            goi__cerew = vsmi__iyuw.dtype
        elif vsmi__iyuw in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and goi__cerew.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            vsmi__iyuw = goi__cerew.dtype
        hvg__lvfv = goi__cerew, vsmi__iyuw
        fwezu__pjbr = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            zlohe__uauxy = self.context.resolve_function_type(self.key,
                hvg__lvfv, {}).return_type
        except Exception as mrh__rxcx:
            raise BodoError(fwezu__pjbr)
        if is_overload_bool(zlohe__uauxy):
            raise BodoError(fwezu__pjbr)
        fauki__bjku = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        nawep__mrfj = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        ynb__uese = types.bool_
        xrhdf__zszkk = SeriesType(ynb__uese, zlohe__uauxy, fauki__bjku,
            nawep__mrfj)
        return xrhdf__zszkk(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        rxzia__bxrz = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if rxzia__bxrz is None:
            rxzia__bxrz = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, rxzia__bxrz, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        goi__cerew = lhs.data if isinstance(lhs, SeriesType) else lhs
        vsmi__iyuw = rhs.data if isinstance(rhs, SeriesType) else rhs
        hvg__lvfv = goi__cerew, vsmi__iyuw
        fwezu__pjbr = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            zlohe__uauxy = self.context.resolve_function_type(self.key,
                hvg__lvfv, {}).return_type
        except Exception as gracu__mel:
            raise BodoError(fwezu__pjbr)
        fauki__bjku = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        nawep__mrfj = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        ynb__uese = zlohe__uauxy.dtype
        xrhdf__zszkk = SeriesType(ynb__uese, zlohe__uauxy, fauki__bjku,
            nawep__mrfj)
        return xrhdf__zszkk(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        rxzia__bxrz = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if rxzia__bxrz is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                rxzia__bxrz = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, rxzia__bxrz, sig, args)
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
            rxzia__bxrz = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return rxzia__bxrz(lhs, rhs)
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
            rxzia__bxrz = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return rxzia__bxrz(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    uydu__saq = lhs == datetime_timedelta_type and rhs == datetime_date_type
    spjba__tlggg = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return uydu__saq or spjba__tlggg


def add_timestamp(lhs, rhs):
    bvib__bojf = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    hpbz__dwhgw = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return bvib__bojf or hpbz__dwhgw


def add_datetime_and_timedeltas(lhs, rhs):
    gwll__cym = [datetime_timedelta_type, pd_timedelta_type]
    uxrl__ehog = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    ekc__bgnvi = lhs in gwll__cym and rhs in gwll__cym
    xsofu__yzy = (lhs == datetime_datetime_type and rhs in gwll__cym or rhs ==
        datetime_datetime_type and lhs in gwll__cym)
    return ekc__bgnvi or xsofu__yzy


def mul_string_arr_and_int(lhs, rhs):
    vsmi__iyuw = isinstance(lhs, types.Integer) and rhs == string_array_type
    goi__cerew = lhs == string_array_type and isinstance(rhs, types.Integer)
    return vsmi__iyuw or goi__cerew


def mul_timedelta_and_int(lhs, rhs):
    uydu__saq = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    spjba__tlggg = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return uydu__saq or spjba__tlggg


def mul_date_offset_and_int(lhs, rhs):
    yfpz__wtmxu = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    oxbg__goerb = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return yfpz__wtmxu or oxbg__goerb


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    rqew__raprs = [datetime_datetime_type, pd_timestamp_type,
        datetime_date_type]
    vyx__qjud = [date_offset_type, month_begin_type, month_end_type, week_type]
    return rhs in vyx__qjud and lhs in rqew__raprs


def sub_dt_index_and_timestamp(lhs, rhs):
    mzp__ugu = isinstance(lhs, DatetimeIndexType) and rhs == pd_timestamp_type
    wcsh__rtgv = isinstance(rhs, DatetimeIndexType
        ) and lhs == pd_timestamp_type
    return mzp__ugu or wcsh__rtgv


def sub_dt_or_td(lhs, rhs):
    hnxl__vat = lhs == datetime_date_type and rhs == datetime_timedelta_type
    bzbf__gmej = lhs == datetime_date_type and rhs == datetime_date_type
    zkdmp__ath = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return hnxl__vat or bzbf__gmej or zkdmp__ath


def sub_datetime_and_timedeltas(lhs, rhs):
    xxsz__jzz = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    gou__scy = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return xxsz__jzz or gou__scy


def div_timedelta_and_int(lhs, rhs):
    ekc__bgnvi = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    qrh__emvb = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return ekc__bgnvi or qrh__emvb


def div_datetime_timedelta(lhs, rhs):
    ekc__bgnvi = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    qrh__emvb = lhs == datetime_timedelta_type and rhs == types.int64
    return ekc__bgnvi or qrh__emvb


def mod_timedeltas(lhs, rhs):
    djpk__yyfu = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    qtqfw__mybf = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return djpk__yyfu or qtqfw__mybf


def cmp_dt_index_to_string(lhs, rhs):
    mzp__ugu = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    wcsh__rtgv = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return mzp__ugu or wcsh__rtgv


def cmp_timestamp_or_date(lhs, rhs):
    ixtzg__vzts = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    nsi__lua = (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and
        rhs == pd_timestamp_type)
    bbk__sdps = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    iut__ruchg = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    kvl__olng = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return ixtzg__vzts or nsi__lua or bbk__sdps or iut__ruchg or kvl__olng


def cmp_timeseries(lhs, rhs):
    jrlwx__pqxpa = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (
        bodo.utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs
        .str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    uknhp__zjm = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    cqq__arw = jrlwx__pqxpa or uknhp__zjm
    wbw__xiw = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    lsf__sgzof = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    iwt__bpqnd = wbw__xiw or lsf__sgzof
    return cqq__arw or iwt__bpqnd


def cmp_timedeltas(lhs, rhs):
    ekc__bgnvi = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in ekc__bgnvi and rhs in ekc__bgnvi


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    eodme__tsu = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return eodme__tsu


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    qpt__wre = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    ngp__qkh = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    cemhx__tnn = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    vqj__zxnmo = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return qpt__wre or ngp__qkh or cemhx__tnn or vqj__zxnmo


def args_td_and_int_array(lhs, rhs):
    fthzc__pxir = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    gugct__iip = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return fthzc__pxir and gugct__iip


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        spjba__tlggg = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        uydu__saq = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        nvd__jwdna = spjba__tlggg or uydu__saq
        lales__haen = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        pboce__uxyrl = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        oyfcy__ysj = lales__haen or pboce__uxyrl
        aiczd__paoz = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        qod__vsgq = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        lbrtt__wrbn = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        rltfk__yib = aiczd__paoz or qod__vsgq or lbrtt__wrbn
        oolj__piqiz = isinstance(lhs, types.List) and isinstance(rhs, types
            .Integer)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        ufv__cvj = isinstance(lhs, tys) or isinstance(rhs, tys)
        wtml__ybzry = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (nvd__jwdna or oyfcy__ysj or rltfk__yib or oolj__piqiz or
            ufv__cvj or wtml__ybzry)
    if op == operator.pow:
        xfas__lkyn = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        ptquh__iek = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        lbrtt__wrbn = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        wtml__ybzry = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return xfas__lkyn or ptquh__iek or lbrtt__wrbn or wtml__ybzry
    if op == operator.floordiv:
        qod__vsgq = lhs in types.real_domain and rhs in types.real_domain
        aiczd__paoz = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        iowve__duyoh = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        ekc__bgnvi = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        wtml__ybzry = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (qod__vsgq or aiczd__paoz or iowve__duyoh or ekc__bgnvi or
            wtml__ybzry)
    if op == operator.truediv:
        euewe__ueeq = lhs in machine_ints and rhs in machine_ints
        qod__vsgq = lhs in types.real_domain and rhs in types.real_domain
        lbrtt__wrbn = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        aiczd__paoz = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        iowve__duyoh = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        brclj__yuvby = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ekc__bgnvi = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        wtml__ybzry = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (euewe__ueeq or qod__vsgq or lbrtt__wrbn or aiczd__paoz or
            iowve__duyoh or brclj__yuvby or ekc__bgnvi or wtml__ybzry)
    if op == operator.mod:
        euewe__ueeq = lhs in machine_ints and rhs in machine_ints
        qod__vsgq = lhs in types.real_domain and rhs in types.real_domain
        aiczd__paoz = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        iowve__duyoh = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        wtml__ybzry = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (euewe__ueeq or qod__vsgq or aiczd__paoz or iowve__duyoh or
            wtml__ybzry)
    if op == operator.add or op == operator.sub:
        nvd__jwdna = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        aqld__cxrd = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        xsscl__bcnyd = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        fcw__xmhqw = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        aiczd__paoz = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        qod__vsgq = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        lbrtt__wrbn = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        rltfk__yib = aiczd__paoz or qod__vsgq or lbrtt__wrbn
        wtml__ybzry = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        jswix__mgx = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        oolj__piqiz = isinstance(lhs, types.List) and isinstance(rhs, types
            .List)
        bkr__egxoj = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        bvqsy__wyu = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        gcqy__dcvm = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        flrx__sbnhz = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        ikfb__lue = bkr__egxoj or bvqsy__wyu or gcqy__dcvm or flrx__sbnhz
        oyfcy__ysj = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        jxl__sbpf = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        iqxp__dky = oyfcy__ysj or jxl__sbpf
        dmxa__csom = lhs == types.NPTimedelta and rhs == types.NPDatetime
        rqz__lwzah = (jswix__mgx or oolj__piqiz or ikfb__lue or iqxp__dky or
            dmxa__csom)
        nkw__mfme = op == operator.add and rqz__lwzah
        return (nvd__jwdna or aqld__cxrd or xsscl__bcnyd or fcw__xmhqw or
            rltfk__yib or wtml__ybzry or nkw__mfme)


def cmp_op_supported_by_numba(lhs, rhs):
    wtml__ybzry = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    oolj__piqiz = isinstance(lhs, types.ListType) and isinstance(rhs, types
        .ListType)
    nvd__jwdna = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    rnt__tirn = isinstance(lhs, types.NPDatetime) and isinstance(rhs, types
        .NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    oyfcy__ysj = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    jswix__mgx = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types
        .BaseTuple)
    fcw__xmhqw = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    rltfk__yib = isinstance(lhs, types.Number) and isinstance(rhs, types.Number
        )
    qgo__jfp = isinstance(lhs, types.Boolean) and isinstance(rhs, types.Boolean
        )
    grn__fcp = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    afol__iqry = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    wfrv__stdp = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    gummg__khobx = isinstance(lhs, types.Literal) and isinstance(rhs, types
        .Literal)
    return (oolj__piqiz or nvd__jwdna or rnt__tirn or oyfcy__ysj or
        jswix__mgx or fcw__xmhqw or rltfk__yib or qgo__jfp or grn__fcp or
        afol__iqry or wtml__ybzry or wfrv__stdp or gummg__khobx)


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
        llxem__uvifg = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(llxem__uvifg)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        llxem__uvifg = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(llxem__uvifg)


install_arith_ops()
