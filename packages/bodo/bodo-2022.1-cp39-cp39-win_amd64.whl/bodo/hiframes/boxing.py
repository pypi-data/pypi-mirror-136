"""
Boxing and unboxing support for DataFrame, Series, etc.
"""
import datetime
import decimal
import warnings
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.ir_utils import GuardException, guard
from numba.core.typing import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, intrinsic, typeof_impl, unbox
from numba.np import numpy_support
from numba.typed.typeddict import Dict
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import PDCategoricalDtype
from bodo.hiframes.pd_dataframe_ext import DataFramePayloadType, DataFrameType, check_runtime_cols_unsupported, construct_dataframe
from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType, typeof_pd_int_dtype
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type, string_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import BodoError, BodoWarning, dtype_to_array_type, get_overload_const_bool, get_overload_const_int, get_overload_const_str, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, raise_bodo_error, to_nullable_type
ll.add_symbol('array_size', hstr_ext.array_size)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
TABLE_FORMAT_THRESHOLD = 20


def _set_bodo_meta_in_pandas():
    if '_bodo_meta' not in pd.Series._metadata:
        pd.Series._metadata.append('_bodo_meta')
    if '_bodo_meta' not in pd.DataFrame._metadata:
        pd.DataFrame._metadata.append('_bodo_meta')


_set_bodo_meta_in_pandas()


@typeof_impl.register(pd.DataFrame)
def typeof_pd_dataframe(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    qyenm__fpp = tuple(val.columns.to_list())
    okb__bbp = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        eal__nmj = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        eal__nmj = numba.typeof(val.index)
    ihv__xfmi = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    cdi__fycu = len(okb__bbp) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(okb__bbp, eal__nmj, qyenm__fpp, ihv__xfmi,
        is_table_format=cdi__fycu)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    ihv__xfmi = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        yqx__fgf = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        yqx__fgf = numba.typeof(val.index)
    return SeriesType(_infer_series_dtype(val), index=yqx__fgf, name_typ=
        numba.typeof(val.name), dist=ihv__xfmi)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    flodq__lmc = c.pyapi.object_getattr_string(val, 'index')
    heqty__pjlc = c.pyapi.to_native_value(typ.index, flodq__lmc).value
    c.pyapi.decref(flodq__lmc)
    if typ.is_table_format:
        ophzy__blpi = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        ophzy__blpi.parent = val
        for sgw__sowq, idf__ideb in typ.table_type.type_to_blk.items():
            qbag__ngdkg = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[idf__ideb]))
            sju__myz, zbhew__jwckn = ListInstance.allocate_ex(c.context, c.
                builder, types.List(sgw__sowq), qbag__ngdkg)
            zbhew__jwckn.size = qbag__ngdkg
            setattr(ophzy__blpi, f'block_{idf__ideb}', zbhew__jwckn.value)
        omwq__wssem = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [ophzy__blpi._getvalue()])
    else:
        pxsmh__yhiem = [c.context.get_constant_null(sgw__sowq) for
            sgw__sowq in typ.data]
        omwq__wssem = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            pxsmh__yhiem)
    pyv__yqgh = construct_dataframe(c.context, c.builder, typ, omwq__wssem,
        heqty__pjlc, val, None)
    return NativeValue(pyv__yqgh)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        waq__qhcs = df._bodo_meta['type_metadata'][1]
    else:
        waq__qhcs = [None] * len(df.columns)
    cgks__puxzh = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=waq__qhcs[i])) for i in range(len(df.columns))]
    return tuple(cgks__puxzh)


class SeriesDtypeEnum(Enum):
    Int8 = 0
    UInt8 = 1
    Int32 = 2
    UInt32 = 3
    Int64 = 4
    UInt64 = 7
    Float32 = 5
    Float64 = 6
    Int16 = 8
    UInt16 = 9
    STRING = 10
    Bool = 11
    Decimal = 12
    Datime_Date = 13
    NP_Datetime64ns = 14
    NP_Timedelta64ns = 15
    Int128 = 16
    LIST = 18
    STRUCT = 19
    BINARY = 21
    ARRAY = 22
    PD_nullable_Int8 = 23
    PD_nullable_UInt8 = 24
    PD_nullable_Int16 = 25
    PD_nullable_UInt16 = 26
    PD_nullable_Int32 = 27
    PD_nullable_UInt32 = 28
    PD_nullable_Int64 = 29
    PD_nullable_UInt64 = 30
    PD_nullable_bool = 31
    CategoricalType = 32
    NoneType = 33
    Literal = 34
    IntegerArray = 35
    RangeIndexType = 36
    DatetimeIndexType = 37
    NumericIndexType = 38
    PeriodIndexType = 39
    IntervalIndexType = 40
    CategoricalIndexType = 41
    StringIndexType = 42
    BinaryIndexType = 43
    TimedeltaIndexType = 44
    LiteralType = 45


_one_to_one_type_to_enum_map = {types.int8: SeriesDtypeEnum.Int8.value,
    types.uint8: SeriesDtypeEnum.UInt8.value, types.int32: SeriesDtypeEnum.
    Int32.value, types.uint32: SeriesDtypeEnum.UInt32.value, types.int64:
    SeriesDtypeEnum.Int64.value, types.uint64: SeriesDtypeEnum.UInt64.value,
    types.float32: SeriesDtypeEnum.Float32.value, types.float64:
    SeriesDtypeEnum.Float64.value, types.NPDatetime('ns'): SeriesDtypeEnum.
    NP_Datetime64ns.value, types.NPTimedelta('ns'): SeriesDtypeEnum.
    NP_Timedelta64ns.value, types.bool_: SeriesDtypeEnum.Bool.value, types.
    int16: SeriesDtypeEnum.Int16.value, types.uint16: SeriesDtypeEnum.
    UInt16.value, types.Integer('int128', 128): SeriesDtypeEnum.Int128.
    value, bodo.hiframes.datetime_date_ext.datetime_date_type:
    SeriesDtypeEnum.Datime_Date.value, IntDtype(types.int8):
    SeriesDtypeEnum.PD_nullable_Int8.value, IntDtype(types.uint8):
    SeriesDtypeEnum.PD_nullable_UInt8.value, IntDtype(types.int16):
    SeriesDtypeEnum.PD_nullable_Int16.value, IntDtype(types.uint16):
    SeriesDtypeEnum.PD_nullable_UInt16.value, IntDtype(types.int32):
    SeriesDtypeEnum.PD_nullable_Int32.value, IntDtype(types.uint32):
    SeriesDtypeEnum.PD_nullable_UInt32.value, IntDtype(types.int64):
    SeriesDtypeEnum.PD_nullable_Int64.value, IntDtype(types.uint64):
    SeriesDtypeEnum.PD_nullable_UInt64.value, bytes_type: SeriesDtypeEnum.
    BINARY.value, string_type: SeriesDtypeEnum.STRING.value, bodo.bool_:
    SeriesDtypeEnum.Bool.value, types.none: SeriesDtypeEnum.NoneType.value}
_one_to_one_enum_to_type_map = {SeriesDtypeEnum.Int8.value: types.int8,
    SeriesDtypeEnum.UInt8.value: types.uint8, SeriesDtypeEnum.Int32.value:
    types.int32, SeriesDtypeEnum.UInt32.value: types.uint32,
    SeriesDtypeEnum.Int64.value: types.int64, SeriesDtypeEnum.UInt64.value:
    types.uint64, SeriesDtypeEnum.Float32.value: types.float32,
    SeriesDtypeEnum.Float64.value: types.float64, SeriesDtypeEnum.
    NP_Datetime64ns.value: types.NPDatetime('ns'), SeriesDtypeEnum.
    NP_Timedelta64ns.value: types.NPTimedelta('ns'), SeriesDtypeEnum.Int16.
    value: types.int16, SeriesDtypeEnum.UInt16.value: types.uint16,
    SeriesDtypeEnum.Int128.value: types.Integer('int128', 128),
    SeriesDtypeEnum.Datime_Date.value: bodo.hiframes.datetime_date_ext.
    datetime_date_type, SeriesDtypeEnum.PD_nullable_Int8.value: IntDtype(
    types.int8), SeriesDtypeEnum.PD_nullable_UInt8.value: IntDtype(types.
    uint8), SeriesDtypeEnum.PD_nullable_Int16.value: IntDtype(types.int16),
    SeriesDtypeEnum.PD_nullable_UInt16.value: IntDtype(types.uint16),
    SeriesDtypeEnum.PD_nullable_Int32.value: IntDtype(types.int32),
    SeriesDtypeEnum.PD_nullable_UInt32.value: IntDtype(types.uint32),
    SeriesDtypeEnum.PD_nullable_Int64.value: IntDtype(types.int64),
    SeriesDtypeEnum.PD_nullable_UInt64.value: IntDtype(types.uint64),
    SeriesDtypeEnum.BINARY.value: bytes_type, SeriesDtypeEnum.STRING.value:
    string_type, SeriesDtypeEnum.Bool.value: bodo.bool_, SeriesDtypeEnum.
    NoneType.value: types.none}


def _dtype_from_type_enum_list(typ_enum_list):
    obkpp__jelq, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(obkpp__jelq) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {obkpp__jelq}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        lrs__vpl, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return lrs__vpl, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        lrs__vpl, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return lrs__vpl, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        qzpg__wwog = typ_enum_list[1]
        ydj__uqy = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(qzpg__wwog, ydj__uqy)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        ajk__sbq = typ_enum_list[1]
        qngcz__hfrug = tuple(typ_enum_list[2:2 + ajk__sbq])
        syh__xvjhw = typ_enum_list[2 + ajk__sbq:]
        eebqz__lagps = []
        for i in range(ajk__sbq):
            syh__xvjhw, gypc__dpxtr = _dtype_from_type_enum_list_recursor(
                syh__xvjhw)
            eebqz__lagps.append(gypc__dpxtr)
        return syh__xvjhw, StructType(tuple(eebqz__lagps), qngcz__hfrug)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        xhfk__qhvju = typ_enum_list[1]
        syh__xvjhw = typ_enum_list[2:]
        return syh__xvjhw, xhfk__qhvju
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        xhfk__qhvju = typ_enum_list[1]
        syh__xvjhw = typ_enum_list[2:]
        return syh__xvjhw, numba.types.literal(xhfk__qhvju)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        syh__xvjhw, mrry__xkyxt = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        syh__xvjhw, lmq__umude = _dtype_from_type_enum_list_recursor(syh__xvjhw
            )
        syh__xvjhw, mrd__fgum = _dtype_from_type_enum_list_recursor(syh__xvjhw)
        syh__xvjhw, oiw__roqoz = _dtype_from_type_enum_list_recursor(syh__xvjhw
            )
        syh__xvjhw, ebboq__xjag = _dtype_from_type_enum_list_recursor(
            syh__xvjhw)
        return syh__xvjhw, PDCategoricalDtype(mrry__xkyxt, lmq__umude,
            mrd__fgum, oiw__roqoz, ebboq__xjag)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        syh__xvjhw, kdfxc__ndt = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return syh__xvjhw, DatetimeIndexType(kdfxc__ndt)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        syh__xvjhw, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        syh__xvjhw, kdfxc__ndt = _dtype_from_type_enum_list_recursor(syh__xvjhw
            )
        syh__xvjhw, oiw__roqoz = _dtype_from_type_enum_list_recursor(syh__xvjhw
            )
        return syh__xvjhw, NumericIndexType(dtype, kdfxc__ndt, oiw__roqoz)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        syh__xvjhw, szfa__bul = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        syh__xvjhw, kdfxc__ndt = _dtype_from_type_enum_list_recursor(syh__xvjhw
            )
        return syh__xvjhw, PeriodIndexType(szfa__bul, kdfxc__ndt)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        syh__xvjhw, oiw__roqoz = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        syh__xvjhw, kdfxc__ndt = _dtype_from_type_enum_list_recursor(syh__xvjhw
            )
        return syh__xvjhw, CategoricalIndexType(oiw__roqoz, kdfxc__ndt)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        syh__xvjhw, kdfxc__ndt = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return syh__xvjhw, RangeIndexType(kdfxc__ndt)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        syh__xvjhw, kdfxc__ndt = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return syh__xvjhw, StringIndexType(kdfxc__ndt)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        syh__xvjhw, kdfxc__ndt = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return syh__xvjhw, BinaryIndexType(kdfxc__ndt)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        syh__xvjhw, kdfxc__ndt = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return syh__xvjhw, TimedeltaIndexType(kdfxc__ndt)
    else:
        raise_bodo_error(
            f'Unexpected Internal Error while converting typing metadata: unable to infer dtype for type enum {typ_enum_list[0]}. Please file the error here: https://github.com/Bodo-inc/Feedback'
            )


def _dtype_to_type_enum_list(typ):
    return guard(_dtype_to_type_enum_list_recursor, typ)


def _dtype_to_type_enum_list_recursor(typ, upcast_numeric_index=True):
    if typ.__hash__ and typ in _one_to_one_type_to_enum_map:
        return [_one_to_one_type_to_enum_map[typ]]
    if isinstance(typ, (dict, int, list, tuple, str, bool, bytes, float)):
        return [SeriesDtypeEnum.Literal.value, typ]
    elif typ is None:
        return [SeriesDtypeEnum.Literal.value, typ]
    elif is_overload_constant_int(typ):
        dwqr__toht = get_overload_const_int(typ)
        if numba.types.maybe_literal(dwqr__toht) == typ:
            return [SeriesDtypeEnum.LiteralType.value, dwqr__toht]
    elif is_overload_constant_str(typ):
        dwqr__toht = get_overload_const_str(typ)
        if numba.types.maybe_literal(dwqr__toht) == typ:
            return [SeriesDtypeEnum.LiteralType.value, dwqr__toht]
    elif is_overload_constant_bool(typ):
        dwqr__toht = get_overload_const_bool(typ)
        if numba.types.maybe_literal(dwqr__toht) == typ:
            return [SeriesDtypeEnum.LiteralType.value, dwqr__toht]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        vjd__isp = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for zezas__vhlzf in typ.names:
            vjd__isp.append(zezas__vhlzf)
        for sphsj__zdqai in typ.data:
            vjd__isp += _dtype_to_type_enum_list_recursor(sphsj__zdqai)
        return vjd__isp
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        hpycz__dma = _dtype_to_type_enum_list_recursor(typ.categories)
        wbdwn__kva = _dtype_to_type_enum_list_recursor(typ.elem_type)
        bfz__sdkz = _dtype_to_type_enum_list_recursor(typ.ordered)
        ffjj__szoe = _dtype_to_type_enum_list_recursor(typ.data)
        kyqfc__qlok = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + hpycz__dma + wbdwn__kva + bfz__sdkz + ffjj__szoe + kyqfc__qlok
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                blxsk__nawlx = types.float64
                hvp__lxwz = types.Array(blxsk__nawlx, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                blxsk__nawlx = types.int64
                hvp__lxwz = types.Array(blxsk__nawlx, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                blxsk__nawlx = types.uint64
                hvp__lxwz = types.Array(blxsk__nawlx, 1, 'C')
            elif typ.dtype == types.bool_:
                blxsk__nawlx = typ.dtype
                hvp__lxwz = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(blxsk__nawlx
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(hvp__lxwz)
        else:
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(typ.dtype
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(typ.data)
    elif isinstance(typ, PeriodIndexType):
        return [SeriesDtypeEnum.PeriodIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.freq
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, CategoricalIndexType):
        return [SeriesDtypeEnum.CategoricalIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.data
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, RangeIndexType):
        return [SeriesDtypeEnum.RangeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, StringIndexType):
        return [SeriesDtypeEnum.StringIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, BinaryIndexType):
        return [SeriesDtypeEnum.BinaryIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, TimedeltaIndexType):
        return [SeriesDtypeEnum.TimedeltaIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    else:
        raise GuardException('Unable to convert type')


def _infer_series_dtype(S, array_metadata=None):
    if S.dtype == np.dtype('O'):
        if len(S.values) == 0:
            if (hasattr(S, '_bodo_meta') and S._bodo_meta is not None and 
                'type_metadata' in S._bodo_meta and S._bodo_meta[
                'type_metadata'][1] is not None):
                itok__llkg = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(itok__llkg)
            elif array_metadata != None:
                return _dtype_from_type_enum_list(array_metadata).dtype
        return numba.typeof(S.values).dtype
    if isinstance(S.dtype, pd.core.arrays.integer._IntegerDtype):
        return typeof_pd_int_dtype(S.dtype, None)
    elif isinstance(S.dtype, pd.CategoricalDtype):
        return bodo.typeof(S.dtype)
    elif isinstance(S.dtype, pd.StringDtype):
        return string_type
    elif isinstance(S.dtype, pd.BooleanDtype):
        return types.bool_
    if isinstance(S.dtype, pd.DatetimeTZDtype):
        raise BodoError('Timezone-aware datetime data type not supported yet')
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    qdj__wnwmb = cgutils.is_not_null(builder, parent_obj)
    smooc__orwmn = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(qdj__wnwmb):
        xemqm__zmgv = pyapi.object_getattr_string(parent_obj, 'columns')
        fri__dqmk = pyapi.call_method(xemqm__zmgv, '__len__', ())
        builder.store(pyapi.long_as_longlong(fri__dqmk), smooc__orwmn)
        pyapi.decref(fri__dqmk)
        pyapi.decref(xemqm__zmgv)
    use_parent_obj = builder.and_(qdj__wnwmb, builder.icmp_unsigned('==',
        builder.load(smooc__orwmn), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        vnd__igr = df_typ.runtime_colname_typ
        context.nrt.incref(builder, vnd__igr, dataframe_payload.columns)
        return pyapi.from_native_value(vnd__igr, dataframe_payload.columns,
            c.env_manager)
    if all(isinstance(c, int) for c in df_typ.columns):
        ubu__kbl = np.array(df_typ.columns, 'int64')
    elif all(isinstance(c, str) for c in df_typ.columns):
        ubu__kbl = pd.array(df_typ.columns, 'string')
    else:
        ubu__kbl = df_typ.columns
    jpe__ivleq = numba.typeof(ubu__kbl)
    bxo__kvatj = context.get_constant_generic(builder, jpe__ivleq, ubu__kbl)
    aqm__afqsk = pyapi.from_native_value(jpe__ivleq, bxo__kvatj, c.env_manager)
    return aqm__afqsk


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (use_parent, otherwise):
        with use_parent:
            pyapi.incref(obj)
            qzxaq__fqyyt = context.insert_const_string(c.builder.module,
                'numpy')
            yspy__txssx = pyapi.import_module_noblock(qzxaq__fqyyt)
            if df_typ.has_runtime_cols:
                dzmj__wjuw = 0
            else:
                dzmj__wjuw = len(df_typ.columns)
            dlrpk__cbsoo = pyapi.long_from_longlong(lir.Constant(lir.
                IntType(64), dzmj__wjuw))
            fzf__van = pyapi.call_method(yspy__txssx, 'arange', (dlrpk__cbsoo,)
                )
            pyapi.object_setattr_string(obj, 'columns', fzf__van)
            pyapi.decref(yspy__txssx)
            pyapi.decref(fzf__van)
            pyapi.decref(dlrpk__cbsoo)
        with otherwise:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            xmf__kajxp = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            qzxaq__fqyyt = context.insert_const_string(c.builder.module,
                'pandas')
            yspy__txssx = pyapi.import_module_noblock(qzxaq__fqyyt)
            df_obj = pyapi.call_method(yspy__txssx, 'DataFrame', (pyapi.
                borrow_none(), xmf__kajxp))
            pyapi.decref(yspy__txssx)
            pyapi.decref(xmf__kajxp)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    roufc__hcbs = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = roufc__hcbs.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        goqe__ahum = typ.table_type
        ophzy__blpi = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, goqe__ahum, ophzy__blpi)
        uapda__izxb = box_table(goqe__ahum, ophzy__blpi, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (then, orelse):
            with then:
                khfjd__ivgn = pyapi.object_getattr_string(uapda__izxb, 'arrays'
                    )
                mgunx__fel = c.pyapi.make_none()
                if n_cols is None:
                    fri__dqmk = pyapi.call_method(khfjd__ivgn, '__len__', ())
                    qbag__ngdkg = pyapi.long_as_longlong(fri__dqmk)
                    pyapi.decref(fri__dqmk)
                else:
                    qbag__ngdkg = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, qbag__ngdkg) as loop:
                    i = loop.index
                    bvt__hdhw = pyapi.list_getitem(khfjd__ivgn, i)
                    iip__ovtmi = c.builder.icmp_unsigned('!=', bvt__hdhw,
                        mgunx__fel)
                    with builder.if_then(iip__ovtmi):
                        ljpm__xvmd = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, ljpm__xvmd, bvt__hdhw)
                        pyapi.decref(ljpm__xvmd)
                pyapi.decref(khfjd__ivgn)
                pyapi.decref(mgunx__fel)
            with orelse:
                df_obj = builder.load(res)
                xmf__kajxp = pyapi.object_getattr_string(df_obj, 'index')
                gavfw__wdvfs = c.pyapi.call_method(uapda__izxb, 'to_pandas',
                    (xmf__kajxp,))
                builder.store(gavfw__wdvfs, res)
                pyapi.decref(df_obj)
                pyapi.decref(xmf__kajxp)
        pyapi.decref(uapda__izxb)
    else:
        knqk__ncj = [builder.extract_value(dataframe_payload.data, i) for i in
            range(n_cols)]
        zqh__cvxxj = typ.data
        for i, xwrt__znfy, pfb__bcw in zip(range(n_cols), knqk__ncj, zqh__cvxxj
            ):
            twtgi__eeefx = cgutils.alloca_once_value(builder, xwrt__znfy)
            zxzp__bqe = cgutils.alloca_once_value(builder, context.
                get_constant_null(pfb__bcw))
            iip__ovtmi = builder.not_(is_ll_eq(builder, twtgi__eeefx,
                zxzp__bqe))
            pnie__thhql = builder.or_(builder.not_(use_parent_obj), builder
                .and_(use_parent_obj, iip__ovtmi))
            with builder.if_then(pnie__thhql):
                ljpm__xvmd = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, pfb__bcw, xwrt__znfy)
                arr_obj = pyapi.from_native_value(pfb__bcw, xwrt__znfy, c.
                    env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, ljpm__xvmd, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(ljpm__xvmd)
    df_obj = builder.load(res)
    aqm__afqsk = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', aqm__afqsk)
    pyapi.decref(aqm__afqsk)
    if not typ.has_runtime_cols and (not typ.is_table_format or len(typ.
        columns) < TABLE_FORMAT_THRESHOLD):
        _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    mgunx__fel = pyapi.borrow_none()
    oea__ubgc = pyapi.unserialize(pyapi.serialize_object(slice))
    wje__kcy = pyapi.call_function_objargs(oea__ubgc, [mgunx__fel])
    xys__dpkvf = pyapi.long_from_longlong(col_ind)
    ynho__cxj = pyapi.tuple_pack([wje__kcy, xys__dpkvf])
    nlffc__wzsi = pyapi.object_getattr_string(df_obj, 'iloc')
    nenod__dqhx = pyapi.object_getitem(nlffc__wzsi, ynho__cxj)
    onj__nllsz = pyapi.object_getattr_string(nenod__dqhx, 'values')
    if isinstance(data_typ, types.Array):
        uuuhg__dehm = context.insert_const_string(builder.module, 'numpy')
        rnd__indi = pyapi.import_module_noblock(uuuhg__dehm)
        arr_obj = pyapi.call_method(rnd__indi, 'ascontiguousarray', (
            onj__nllsz,))
        pyapi.decref(onj__nllsz)
        pyapi.decref(rnd__indi)
    else:
        arr_obj = onj__nllsz
    pyapi.decref(oea__ubgc)
    pyapi.decref(wje__kcy)
    pyapi.decref(xys__dpkvf)
    pyapi.decref(ynho__cxj)
    pyapi.decref(nlffc__wzsi)
    pyapi.decref(nenod__dqhx)
    return arr_obj


@intrinsic
def unbox_dataframe_column(typingctx, df, i=None):
    assert isinstance(df, DataFrameType) and is_overload_constant_int(i)

    def codegen(context, builder, sig, args):
        pyapi = context.get_python_api(builder)
        c = numba.core.pythonapi._UnboxContext(context, builder, pyapi)
        df_typ = sig.args[0]
        col_ind = get_overload_const_int(sig.args[1])
        data_typ = df_typ.data[col_ind]
        roufc__hcbs = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            roufc__hcbs.parent, args[1], data_typ)
        uanni__hwixu = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            ophzy__blpi = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            idf__ideb = df_typ.table_type.type_to_blk[data_typ]
            xfyq__azsw = getattr(ophzy__blpi, f'block_{idf__ideb}')
            zuy__dxo = ListInstance(c.context, c.builder, types.List(
                data_typ), xfyq__azsw)
            ffx__cer = context.get_constant(types.int64, df_typ.table_type.
                block_offsets[col_ind])
            zuy__dxo.inititem(ffx__cer, uanni__hwixu.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, uanni__hwixu.value, col_ind)
        ntcd__utv = DataFramePayloadType(df_typ)
        syi__gdy = context.nrt.meminfo_data(builder, roufc__hcbs.meminfo)
        lrro__lae = context.get_value_type(ntcd__utv).as_pointer()
        syi__gdy = builder.bitcast(syi__gdy, lrro__lae)
        builder.store(dataframe_payload._getvalue(), syi__gdy)
    return signature(types.none, df, i), codegen


@unbox(SeriesType)
def unbox_series(typ, val, c):
    onj__nllsz = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        uuuhg__dehm = c.context.insert_const_string(c.builder.module, 'numpy')
        rnd__indi = c.pyapi.import_module_noblock(uuuhg__dehm)
        arr_obj = c.pyapi.call_method(rnd__indi, 'ascontiguousarray', (
            onj__nllsz,))
        c.pyapi.decref(onj__nllsz)
        c.pyapi.decref(rnd__indi)
    else:
        arr_obj = onj__nllsz
    nsyc__ioygp = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    xmf__kajxp = c.pyapi.object_getattr_string(val, 'index')
    heqty__pjlc = c.pyapi.to_native_value(typ.index, xmf__kajxp).value
    jlts__lcr = c.pyapi.object_getattr_string(val, 'name')
    lkk__mdcfv = c.pyapi.to_native_value(typ.name_typ, jlts__lcr).value
    qdubr__rotfp = bodo.hiframes.pd_series_ext.construct_series(c.context,
        c.builder, typ, nsyc__ioygp, heqty__pjlc, lkk__mdcfv)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(xmf__kajxp)
    c.pyapi.decref(jlts__lcr)
    return NativeValue(qdubr__rotfp)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        qwwg__xbrl = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(qwwg__xbrl._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    qzxaq__fqyyt = c.context.insert_const_string(c.builder.module, 'pandas')
    vvc__gxm = c.pyapi.import_module_noblock(qzxaq__fqyyt)
    roht__rrw = bodo.hiframes.pd_series_ext.get_series_payload(c.context, c
        .builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, roht__rrw.data)
    c.context.nrt.incref(c.builder, typ.index, roht__rrw.index)
    c.context.nrt.incref(c.builder, typ.name_typ, roht__rrw.name)
    arr_obj = c.pyapi.from_native_value(typ.data, roht__rrw.data, c.env_manager
        )
    xmf__kajxp = c.pyapi.from_native_value(typ.index, roht__rrw.index, c.
        env_manager)
    jlts__lcr = c.pyapi.from_native_value(typ.name_typ, roht__rrw.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(vvc__gxm, 'Series', (arr_obj, xmf__kajxp,
        dtype, jlts__lcr))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(xmf__kajxp)
    c.pyapi.decref(jlts__lcr)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(vvc__gxm)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    rlkd__ppwgg = []
    for kmm__zbi in typ_list:
        if isinstance(kmm__zbi, int) and not isinstance(kmm__zbi, bool):
            qgf__divpk = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), kmm__zbi))
        else:
            etgdz__kdfbs = numba.typeof(kmm__zbi)
            tftix__phdom = context.get_constant_generic(builder,
                etgdz__kdfbs, kmm__zbi)
            qgf__divpk = pyapi.from_native_value(etgdz__kdfbs, tftix__phdom,
                env_manager)
        rlkd__ppwgg.append(qgf__divpk)
    ffn__rgun = pyapi.list_pack(rlkd__ppwgg)
    for val in rlkd__ppwgg:
        pyapi.decref(val)
    return ffn__rgun


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    biayj__kydge = _dtype_to_type_enum_list(typ.index)
    if biayj__kydge != None:
        wnq__nvpm = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, biayj__kydge)
    else:
        wnq__nvpm = pyapi.make_none()
    hyy__hbkb = []
    for dtype in typ.data:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            ffn__rgun = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            ffn__rgun = pyapi.make_none()
        hyy__hbkb.append(ffn__rgun)
    dpnuc__ohc = pyapi.dict_new(2)
    gno__qav = pyapi.list_pack(hyy__hbkb)
    sdcs__jikg = pyapi.list_pack([wnq__nvpm, gno__qav])
    for val in hyy__hbkb:
        pyapi.decref(val)
    qht__mhil = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ.
        dist.value))
    pyapi.dict_setitem_string(dpnuc__ohc, 'dist', qht__mhil)
    pyapi.dict_setitem_string(dpnuc__ohc, 'type_metadata', sdcs__jikg)
    pyapi.object_setattr_string(obj, '_bodo_meta', dpnuc__ohc)
    pyapi.decref(dpnuc__ohc)
    pyapi.decref(qht__mhil)


def get_series_dtype_handle_null_int_and_hetrogenous(series_typ):
    if isinstance(series_typ, HeterogeneousSeriesType):
        return None
    if isinstance(series_typ.dtype, types.Number) and isinstance(series_typ
        .data, IntegerArrayType):
        return IntDtype(series_typ.dtype)
    return series_typ.dtype


def _set_bodo_meta_series(obj, c, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    dpnuc__ohc = pyapi.dict_new(2)
    qht__mhil = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ.
        dist.value))
    biayj__kydge = _dtype_to_type_enum_list(typ.index)
    if biayj__kydge != None:
        wnq__nvpm = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, biayj__kydge)
    else:
        wnq__nvpm = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            sfxrk__rwrbf = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            sfxrk__rwrbf = pyapi.make_none()
    else:
        sfxrk__rwrbf = pyapi.make_none()
    rpl__qnouu = pyapi.list_pack([wnq__nvpm, sfxrk__rwrbf])
    pyapi.dict_setitem_string(dpnuc__ohc, 'type_metadata', rpl__qnouu)
    pyapi.decref(rpl__qnouu)
    pyapi.dict_setitem_string(dpnuc__ohc, 'dist', qht__mhil)
    pyapi.object_setattr_string(obj, '_bodo_meta', dpnuc__ohc)
    pyapi.decref(dpnuc__ohc)
    pyapi.decref(qht__mhil)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as ddhec__unko:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    csfm__tjvcr = numba.np.numpy_support.map_layout(val)
    pogy__jdjje = not val.flags.writeable
    return types.Array(dtype, val.ndim, csfm__tjvcr, readonly=pogy__jdjje)


def _infer_ndarray_obj_dtype(val):
    if not val.dtype == np.dtype('O'):
        raise BodoError('Unsupported array dtype: {}'.format(val.dtype))
    i = 0
    while i < len(val) and (pd.api.types.is_scalar(val[i]) and pd.isna(val[
        i]) or not pd.api.types.is_scalar(val[i]) and len(val[i]) == 0):
        i += 1
    if i == len(val):
        warnings.warn(BodoWarning(
            'Empty object array passed to Bodo, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return string_array_type
    mzqd__xeo = val[i]
    if isinstance(mzqd__xeo, str):
        return string_array_type
    elif isinstance(mzqd__xeo, bytes):
        return binary_array_type
    elif isinstance(mzqd__xeo, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(mzqd__xeo, (int, np.int32, np.int64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(mzqd__xeo))
    elif isinstance(mzqd__xeo, (dict, Dict)) and all(isinstance(sqq__qtnx,
        str) for sqq__qtnx in mzqd__xeo.keys()):
        qngcz__hfrug = tuple(mzqd__xeo.keys())
        azd__aulaa = tuple(_get_struct_value_arr_type(v) for v in mzqd__xeo
            .values())
        return StructArrayType(azd__aulaa, qngcz__hfrug)
    elif isinstance(mzqd__xeo, (dict, Dict)):
        ehc__zrc = numba.typeof(_value_to_array(list(mzqd__xeo.keys())))
        rfot__nel = numba.typeof(_value_to_array(list(mzqd__xeo.values())))
        return MapArrayType(ehc__zrc, rfot__nel)
    elif isinstance(mzqd__xeo, tuple):
        azd__aulaa = tuple(_get_struct_value_arr_type(v) for v in mzqd__xeo)
        return TupleArrayType(azd__aulaa)
    if isinstance(mzqd__xeo, (list, np.ndarray, pd.arrays.BooleanArray, pd.
        arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(mzqd__xeo, list):
            mzqd__xeo = _value_to_array(mzqd__xeo)
        papbz__bfq = numba.typeof(mzqd__xeo)
        return ArrayItemArrayType(papbz__bfq)
    if isinstance(mzqd__xeo, datetime.date):
        return datetime_date_array_type
    if isinstance(mzqd__xeo, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(mzqd__xeo, decimal.Decimal):
        return DecimalArrayType(38, 18)
    raise BodoError('Unsupported object array with first value: {}'.format(
        mzqd__xeo))


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    tutis__whsqf = val.copy()
    tutis__whsqf.append(None)
    xwrt__znfy = np.array(tutis__whsqf, np.object_)
    if len(val) and isinstance(val[0], float):
        xwrt__znfy = np.array(val, np.float64)
    return xwrt__znfy


def _get_struct_value_arr_type(v):
    if isinstance(v, (dict, Dict)):
        return numba.typeof(_value_to_array(v))
    if isinstance(v, list):
        return dtype_to_array_type(numba.typeof(_value_to_array(v)))
    if pd.api.types.is_scalar(v) and pd.isna(v):
        warnings.warn(BodoWarning(
            'Field value in struct array is NA, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return string_array_type
    pfb__bcw = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        pfb__bcw = to_nullable_type(pfb__bcw)
    return pfb__bcw
