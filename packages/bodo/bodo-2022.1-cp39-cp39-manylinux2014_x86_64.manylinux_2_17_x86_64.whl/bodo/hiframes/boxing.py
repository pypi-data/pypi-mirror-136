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
    vgo__rogh = tuple(val.columns.to_list())
    colj__uin = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        pybi__brm = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        pybi__brm = numba.typeof(val.index)
    goyfd__rura = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    aec__wbehg = len(colj__uin) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(colj__uin, pybi__brm, vgo__rogh, goyfd__rura,
        is_table_format=aec__wbehg)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    goyfd__rura = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        ccqxe__wfog = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        ccqxe__wfog = numba.typeof(val.index)
    return SeriesType(_infer_series_dtype(val), index=ccqxe__wfog, name_typ
        =numba.typeof(val.name), dist=goyfd__rura)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    xizzr__ivwv = c.pyapi.object_getattr_string(val, 'index')
    uujyd__tpb = c.pyapi.to_native_value(typ.index, xizzr__ivwv).value
    c.pyapi.decref(xizzr__ivwv)
    if typ.is_table_format:
        mevul__sdqz = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        mevul__sdqz.parent = val
        for ulybs__inprz, mdu__rrpwo in typ.table_type.type_to_blk.items():
            wquh__njyck = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[mdu__rrpwo]))
            sch__nby, gxvq__ocgr = ListInstance.allocate_ex(c.context, c.
                builder, types.List(ulybs__inprz), wquh__njyck)
            gxvq__ocgr.size = wquh__njyck
            setattr(mevul__sdqz, f'block_{mdu__rrpwo}', gxvq__ocgr.value)
        pfqj__ywu = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [mevul__sdqz._getvalue()])
    else:
        woff__oerrk = [c.context.get_constant_null(ulybs__inprz) for
            ulybs__inprz in typ.data]
        pfqj__ywu = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            woff__oerrk)
    cfz__urly = construct_dataframe(c.context, c.builder, typ, pfqj__ywu,
        uujyd__tpb, val, None)
    return NativeValue(cfz__urly)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        icdd__bchbv = df._bodo_meta['type_metadata'][1]
    else:
        icdd__bchbv = [None] * len(df.columns)
    zeaa__bvkow = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=icdd__bchbv[i])) for i in range(len(df.columns))]
    return tuple(zeaa__bvkow)


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
    fzu__mywlm, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(fzu__mywlm) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {fzu__mywlm}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        vqlb__ruqud, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return vqlb__ruqud, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        vqlb__ruqud, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return vqlb__ruqud, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        gclgu__urcyr = typ_enum_list[1]
        whzj__albza = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(gclgu__urcyr, whzj__albza)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        tgpsb__suwhn = typ_enum_list[1]
        kxkpl__qkhi = tuple(typ_enum_list[2:2 + tgpsb__suwhn])
        nulq__xhmee = typ_enum_list[2 + tgpsb__suwhn:]
        malh__vawz = []
        for i in range(tgpsb__suwhn):
            nulq__xhmee, qxlwv__mfemn = _dtype_from_type_enum_list_recursor(
                nulq__xhmee)
            malh__vawz.append(qxlwv__mfemn)
        return nulq__xhmee, StructType(tuple(malh__vawz), kxkpl__qkhi)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        hxs__gafu = typ_enum_list[1]
        nulq__xhmee = typ_enum_list[2:]
        return nulq__xhmee, hxs__gafu
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        hxs__gafu = typ_enum_list[1]
        nulq__xhmee = typ_enum_list[2:]
        return nulq__xhmee, numba.types.literal(hxs__gafu)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        nulq__xhmee, zawqj__bqz = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        nulq__xhmee, ypvx__uxgc = _dtype_from_type_enum_list_recursor(
            nulq__xhmee)
        nulq__xhmee, qiu__qkbve = _dtype_from_type_enum_list_recursor(
            nulq__xhmee)
        nulq__xhmee, gpkhk__sgi = _dtype_from_type_enum_list_recursor(
            nulq__xhmee)
        nulq__xhmee, hkw__qspzy = _dtype_from_type_enum_list_recursor(
            nulq__xhmee)
        return nulq__xhmee, PDCategoricalDtype(zawqj__bqz, ypvx__uxgc,
            qiu__qkbve, gpkhk__sgi, hkw__qspzy)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        nulq__xhmee, dueau__jruod = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return nulq__xhmee, DatetimeIndexType(dueau__jruod)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        nulq__xhmee, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        nulq__xhmee, dueau__jruod = _dtype_from_type_enum_list_recursor(
            nulq__xhmee)
        nulq__xhmee, gpkhk__sgi = _dtype_from_type_enum_list_recursor(
            nulq__xhmee)
        return nulq__xhmee, NumericIndexType(dtype, dueau__jruod, gpkhk__sgi)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        nulq__xhmee, ydt__ppmnr = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        nulq__xhmee, dueau__jruod = _dtype_from_type_enum_list_recursor(
            nulq__xhmee)
        return nulq__xhmee, PeriodIndexType(ydt__ppmnr, dueau__jruod)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        nulq__xhmee, gpkhk__sgi = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        nulq__xhmee, dueau__jruod = _dtype_from_type_enum_list_recursor(
            nulq__xhmee)
        return nulq__xhmee, CategoricalIndexType(gpkhk__sgi, dueau__jruod)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        nulq__xhmee, dueau__jruod = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return nulq__xhmee, RangeIndexType(dueau__jruod)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        nulq__xhmee, dueau__jruod = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return nulq__xhmee, StringIndexType(dueau__jruod)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        nulq__xhmee, dueau__jruod = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return nulq__xhmee, BinaryIndexType(dueau__jruod)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        nulq__xhmee, dueau__jruod = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return nulq__xhmee, TimedeltaIndexType(dueau__jruod)
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
        eam__nkjiy = get_overload_const_int(typ)
        if numba.types.maybe_literal(eam__nkjiy) == typ:
            return [SeriesDtypeEnum.LiteralType.value, eam__nkjiy]
    elif is_overload_constant_str(typ):
        eam__nkjiy = get_overload_const_str(typ)
        if numba.types.maybe_literal(eam__nkjiy) == typ:
            return [SeriesDtypeEnum.LiteralType.value, eam__nkjiy]
    elif is_overload_constant_bool(typ):
        eam__nkjiy = get_overload_const_bool(typ)
        if numba.types.maybe_literal(eam__nkjiy) == typ:
            return [SeriesDtypeEnum.LiteralType.value, eam__nkjiy]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        bxir__vovja = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for exhgo__reu in typ.names:
            bxir__vovja.append(exhgo__reu)
        for ytkem__yhcp in typ.data:
            bxir__vovja += _dtype_to_type_enum_list_recursor(ytkem__yhcp)
        return bxir__vovja
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        nlgee__utp = _dtype_to_type_enum_list_recursor(typ.categories)
        zpa__rfqkt = _dtype_to_type_enum_list_recursor(typ.elem_type)
        vsbez__fchf = _dtype_to_type_enum_list_recursor(typ.ordered)
        ryahy__gzpv = _dtype_to_type_enum_list_recursor(typ.data)
        qtz__ldj = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + nlgee__utp + zpa__rfqkt + vsbez__fchf + ryahy__gzpv + qtz__ldj
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                zhz__nng = types.float64
                dqw__ybgz = types.Array(zhz__nng, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                zhz__nng = types.int64
                dqw__ybgz = types.Array(zhz__nng, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                zhz__nng = types.uint64
                dqw__ybgz = types.Array(zhz__nng, 1, 'C')
            elif typ.dtype == types.bool_:
                zhz__nng = typ.dtype
                dqw__ybgz = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(zhz__nng
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(dqw__ybgz)
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
                wngz__ipz = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(wngz__ipz)
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
    fvfv__pkt = cgutils.is_not_null(builder, parent_obj)
    gmvvc__szwfo = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(fvfv__pkt):
        hkkv__pdm = pyapi.object_getattr_string(parent_obj, 'columns')
        vjvx__genyo = pyapi.call_method(hkkv__pdm, '__len__', ())
        builder.store(pyapi.long_as_longlong(vjvx__genyo), gmvvc__szwfo)
        pyapi.decref(vjvx__genyo)
        pyapi.decref(hkkv__pdm)
    use_parent_obj = builder.and_(fvfv__pkt, builder.icmp_unsigned('==',
        builder.load(gmvvc__szwfo), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        nixb__bhwx = df_typ.runtime_colname_typ
        context.nrt.incref(builder, nixb__bhwx, dataframe_payload.columns)
        return pyapi.from_native_value(nixb__bhwx, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, int) for c in df_typ.columns):
        plt__vhr = np.array(df_typ.columns, 'int64')
    elif all(isinstance(c, str) for c in df_typ.columns):
        plt__vhr = pd.array(df_typ.columns, 'string')
    else:
        plt__vhr = df_typ.columns
    gwt__ddm = numba.typeof(plt__vhr)
    ttja__cyi = context.get_constant_generic(builder, gwt__ddm, plt__vhr)
    yynu__uicio = pyapi.from_native_value(gwt__ddm, ttja__cyi, c.env_manager)
    return yynu__uicio


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (use_parent, otherwise):
        with use_parent:
            pyapi.incref(obj)
            ovcx__sxtgg = context.insert_const_string(c.builder.module, 'numpy'
                )
            iytq__fkg = pyapi.import_module_noblock(ovcx__sxtgg)
            if df_typ.has_runtime_cols:
                oztjg__jvy = 0
            else:
                oztjg__jvy = len(df_typ.columns)
            noy__ncoe = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), oztjg__jvy))
            pfe__wwfr = pyapi.call_method(iytq__fkg, 'arange', (noy__ncoe,))
            pyapi.object_setattr_string(obj, 'columns', pfe__wwfr)
            pyapi.decref(iytq__fkg)
            pyapi.decref(pfe__wwfr)
            pyapi.decref(noy__ncoe)
        with otherwise:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            hyywy__lxmlp = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            ovcx__sxtgg = context.insert_const_string(c.builder.module,
                'pandas')
            iytq__fkg = pyapi.import_module_noblock(ovcx__sxtgg)
            df_obj = pyapi.call_method(iytq__fkg, 'DataFrame', (pyapi.
                borrow_none(), hyywy__lxmlp))
            pyapi.decref(iytq__fkg)
            pyapi.decref(hyywy__lxmlp)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    urchk__agl = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = urchk__agl.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        rff__fkggr = typ.table_type
        mevul__sdqz = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, rff__fkggr, mevul__sdqz)
        ahkml__ubsj = box_table(rff__fkggr, mevul__sdqz, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (then, orelse):
            with then:
                ivza__tzia = pyapi.object_getattr_string(ahkml__ubsj, 'arrays')
                rcrv__jjf = c.pyapi.make_none()
                if n_cols is None:
                    vjvx__genyo = pyapi.call_method(ivza__tzia, '__len__', ())
                    wquh__njyck = pyapi.long_as_longlong(vjvx__genyo)
                    pyapi.decref(vjvx__genyo)
                else:
                    wquh__njyck = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, wquh__njyck) as loop:
                    i = loop.index
                    pxgj__cul = pyapi.list_getitem(ivza__tzia, i)
                    iej__pobn = c.builder.icmp_unsigned('!=', pxgj__cul,
                        rcrv__jjf)
                    with builder.if_then(iej__pobn):
                        fqw__zqndp = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, fqw__zqndp, pxgj__cul)
                        pyapi.decref(fqw__zqndp)
                pyapi.decref(ivza__tzia)
                pyapi.decref(rcrv__jjf)
            with orelse:
                df_obj = builder.load(res)
                hyywy__lxmlp = pyapi.object_getattr_string(df_obj, 'index')
                bog__mscph = c.pyapi.call_method(ahkml__ubsj, 'to_pandas',
                    (hyywy__lxmlp,))
                builder.store(bog__mscph, res)
                pyapi.decref(df_obj)
                pyapi.decref(hyywy__lxmlp)
        pyapi.decref(ahkml__ubsj)
    else:
        ucuc__bbqq = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        vyn__ybdl = typ.data
        for i, biw__sbet, icr__vke in zip(range(n_cols), ucuc__bbqq, vyn__ybdl
            ):
            ffvds__sajbj = cgutils.alloca_once_value(builder, biw__sbet)
            nslqt__qctqp = cgutils.alloca_once_value(builder, context.
                get_constant_null(icr__vke))
            iej__pobn = builder.not_(is_ll_eq(builder, ffvds__sajbj,
                nslqt__qctqp))
            vqm__ovruj = builder.or_(builder.not_(use_parent_obj), builder.
                and_(use_parent_obj, iej__pobn))
            with builder.if_then(vqm__ovruj):
                fqw__zqndp = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, icr__vke, biw__sbet)
                arr_obj = pyapi.from_native_value(icr__vke, biw__sbet, c.
                    env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, fqw__zqndp, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(fqw__zqndp)
    df_obj = builder.load(res)
    yynu__uicio = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', yynu__uicio)
    pyapi.decref(yynu__uicio)
    if not typ.has_runtime_cols and (not typ.is_table_format or len(typ.
        columns) < TABLE_FORMAT_THRESHOLD):
        _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    rcrv__jjf = pyapi.borrow_none()
    zpgn__vlxvk = pyapi.unserialize(pyapi.serialize_object(slice))
    fkf__vgyzb = pyapi.call_function_objargs(zpgn__vlxvk, [rcrv__jjf])
    ttxa__wkl = pyapi.long_from_longlong(col_ind)
    rua__elax = pyapi.tuple_pack([fkf__vgyzb, ttxa__wkl])
    xlce__yxw = pyapi.object_getattr_string(df_obj, 'iloc')
    svd__vvtf = pyapi.object_getitem(xlce__yxw, rua__elax)
    rvv__lgg = pyapi.object_getattr_string(svd__vvtf, 'values')
    if isinstance(data_typ, types.Array):
        lpam__twhk = context.insert_const_string(builder.module, 'numpy')
        ofmhu__jnoz = pyapi.import_module_noblock(lpam__twhk)
        arr_obj = pyapi.call_method(ofmhu__jnoz, 'ascontiguousarray', (
            rvv__lgg,))
        pyapi.decref(rvv__lgg)
        pyapi.decref(ofmhu__jnoz)
    else:
        arr_obj = rvv__lgg
    pyapi.decref(zpgn__vlxvk)
    pyapi.decref(fkf__vgyzb)
    pyapi.decref(ttxa__wkl)
    pyapi.decref(rua__elax)
    pyapi.decref(xlce__yxw)
    pyapi.decref(svd__vvtf)
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
        urchk__agl = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            urchk__agl.parent, args[1], data_typ)
        ynz__seveu = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            mevul__sdqz = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            mdu__rrpwo = df_typ.table_type.type_to_blk[data_typ]
            ruifu__igtqk = getattr(mevul__sdqz, f'block_{mdu__rrpwo}')
            copv__ahy = ListInstance(c.context, c.builder, types.List(
                data_typ), ruifu__igtqk)
            fhfnc__utfes = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[col_ind])
            copv__ahy.inititem(fhfnc__utfes, ynz__seveu.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, ynz__seveu.value, col_ind)
        xhkbl__ibtl = DataFramePayloadType(df_typ)
        koy__isvi = context.nrt.meminfo_data(builder, urchk__agl.meminfo)
        rmiu__eedhg = context.get_value_type(xhkbl__ibtl).as_pointer()
        koy__isvi = builder.bitcast(koy__isvi, rmiu__eedhg)
        builder.store(dataframe_payload._getvalue(), koy__isvi)
    return signature(types.none, df, i), codegen


@unbox(SeriesType)
def unbox_series(typ, val, c):
    rvv__lgg = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        lpam__twhk = c.context.insert_const_string(c.builder.module, 'numpy')
        ofmhu__jnoz = c.pyapi.import_module_noblock(lpam__twhk)
        arr_obj = c.pyapi.call_method(ofmhu__jnoz, 'ascontiguousarray', (
            rvv__lgg,))
        c.pyapi.decref(rvv__lgg)
        c.pyapi.decref(ofmhu__jnoz)
    else:
        arr_obj = rvv__lgg
    ogpfg__yiy = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    hyywy__lxmlp = c.pyapi.object_getattr_string(val, 'index')
    uujyd__tpb = c.pyapi.to_native_value(typ.index, hyywy__lxmlp).value
    lafy__gonhv = c.pyapi.object_getattr_string(val, 'name')
    lenp__xpktt = c.pyapi.to_native_value(typ.name_typ, lafy__gonhv).value
    pxtue__pyi = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, ogpfg__yiy, uujyd__tpb, lenp__xpktt)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(hyywy__lxmlp)
    c.pyapi.decref(lafy__gonhv)
    return NativeValue(pxtue__pyi)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        pxvkc__dlu = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(pxvkc__dlu._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    ovcx__sxtgg = c.context.insert_const_string(c.builder.module, 'pandas')
    yjy__phqsp = c.pyapi.import_module_noblock(ovcx__sxtgg)
    geka__pofra = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, geka__pofra.data)
    c.context.nrt.incref(c.builder, typ.index, geka__pofra.index)
    c.context.nrt.incref(c.builder, typ.name_typ, geka__pofra.name)
    arr_obj = c.pyapi.from_native_value(typ.data, geka__pofra.data, c.
        env_manager)
    hyywy__lxmlp = c.pyapi.from_native_value(typ.index, geka__pofra.index,
        c.env_manager)
    lafy__gonhv = c.pyapi.from_native_value(typ.name_typ, geka__pofra.name,
        c.env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(yjy__phqsp, 'Series', (arr_obj, hyywy__lxmlp,
        dtype, lafy__gonhv))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(hyywy__lxmlp)
    c.pyapi.decref(lafy__gonhv)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(yjy__phqsp)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    aeh__jmxm = []
    for zwu__zftoo in typ_list:
        if isinstance(zwu__zftoo, int) and not isinstance(zwu__zftoo, bool):
            cko__zgj = pyapi.long_from_longlong(lir.Constant(lir.IntType(64
                ), zwu__zftoo))
        else:
            gxl__mpmir = numba.typeof(zwu__zftoo)
            inpz__hto = context.get_constant_generic(builder, gxl__mpmir,
                zwu__zftoo)
            cko__zgj = pyapi.from_native_value(gxl__mpmir, inpz__hto,
                env_manager)
        aeh__jmxm.append(cko__zgj)
    alo__dhbb = pyapi.list_pack(aeh__jmxm)
    for val in aeh__jmxm:
        pyapi.decref(val)
    return alo__dhbb


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    xbl__hdfc = _dtype_to_type_enum_list(typ.index)
    if xbl__hdfc != None:
        gubh__lgz = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, xbl__hdfc)
    else:
        gubh__lgz = pyapi.make_none()
    ccp__pfby = []
    for dtype in typ.data:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            alo__dhbb = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            alo__dhbb = pyapi.make_none()
        ccp__pfby.append(alo__dhbb)
    znhc__lxn = pyapi.dict_new(2)
    mbvbs__fkvqn = pyapi.list_pack(ccp__pfby)
    kxc__weogb = pyapi.list_pack([gubh__lgz, mbvbs__fkvqn])
    for val in ccp__pfby:
        pyapi.decref(val)
    pfje__jvfrp = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    pyapi.dict_setitem_string(znhc__lxn, 'dist', pfje__jvfrp)
    pyapi.dict_setitem_string(znhc__lxn, 'type_metadata', kxc__weogb)
    pyapi.object_setattr_string(obj, '_bodo_meta', znhc__lxn)
    pyapi.decref(znhc__lxn)
    pyapi.decref(pfje__jvfrp)


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
    znhc__lxn = pyapi.dict_new(2)
    pfje__jvfrp = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    xbl__hdfc = _dtype_to_type_enum_list(typ.index)
    if xbl__hdfc != None:
        gubh__lgz = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, xbl__hdfc)
    else:
        gubh__lgz = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            pphnt__tmm = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            pphnt__tmm = pyapi.make_none()
    else:
        pphnt__tmm = pyapi.make_none()
    pxf__pti = pyapi.list_pack([gubh__lgz, pphnt__tmm])
    pyapi.dict_setitem_string(znhc__lxn, 'type_metadata', pxf__pti)
    pyapi.decref(pxf__pti)
    pyapi.dict_setitem_string(znhc__lxn, 'dist', pfje__jvfrp)
    pyapi.object_setattr_string(obj, '_bodo_meta', znhc__lxn)
    pyapi.decref(znhc__lxn)
    pyapi.decref(pfje__jvfrp)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as oqgt__vcpc:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    msu__dmby = numba.np.numpy_support.map_layout(val)
    vifl__fgvz = not val.flags.writeable
    return types.Array(dtype, val.ndim, msu__dmby, readonly=vifl__fgvz)


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
    ifmjv__xzhn = val[i]
    if isinstance(ifmjv__xzhn, str):
        return string_array_type
    elif isinstance(ifmjv__xzhn, bytes):
        return binary_array_type
    elif isinstance(ifmjv__xzhn, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(ifmjv__xzhn, (int, np.int32, np.int64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(ifmjv__xzhn)
            )
    elif isinstance(ifmjv__xzhn, (dict, Dict)) and all(isinstance(
        lagl__vriag, str) for lagl__vriag in ifmjv__xzhn.keys()):
        kxkpl__qkhi = tuple(ifmjv__xzhn.keys())
        aidk__lbcut = tuple(_get_struct_value_arr_type(v) for v in
            ifmjv__xzhn.values())
        return StructArrayType(aidk__lbcut, kxkpl__qkhi)
    elif isinstance(ifmjv__xzhn, (dict, Dict)):
        jqcr__eojfc = numba.typeof(_value_to_array(list(ifmjv__xzhn.keys())))
        wml__wfc = numba.typeof(_value_to_array(list(ifmjv__xzhn.values())))
        return MapArrayType(jqcr__eojfc, wml__wfc)
    elif isinstance(ifmjv__xzhn, tuple):
        aidk__lbcut = tuple(_get_struct_value_arr_type(v) for v in ifmjv__xzhn)
        return TupleArrayType(aidk__lbcut)
    if isinstance(ifmjv__xzhn, (list, np.ndarray, pd.arrays.BooleanArray,
        pd.arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(ifmjv__xzhn, list):
            ifmjv__xzhn = _value_to_array(ifmjv__xzhn)
        jfc__ktfgy = numba.typeof(ifmjv__xzhn)
        return ArrayItemArrayType(jfc__ktfgy)
    if isinstance(ifmjv__xzhn, datetime.date):
        return datetime_date_array_type
    if isinstance(ifmjv__xzhn, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(ifmjv__xzhn, decimal.Decimal):
        return DecimalArrayType(38, 18)
    raise BodoError('Unsupported object array with first value: {}'.format(
        ifmjv__xzhn))


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    xbxqp__mndhv = val.copy()
    xbxqp__mndhv.append(None)
    biw__sbet = np.array(xbxqp__mndhv, np.object_)
    if len(val) and isinstance(val[0], float):
        biw__sbet = np.array(val, np.float64)
    return biw__sbet


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
    icr__vke = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        icr__vke = to_nullable_type(icr__vke)
    return icr__vke
