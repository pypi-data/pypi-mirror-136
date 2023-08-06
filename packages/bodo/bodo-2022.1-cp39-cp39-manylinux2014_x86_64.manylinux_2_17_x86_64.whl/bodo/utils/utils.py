"""
Collection of utility functions. Needs to be refactored in separate files.
"""
import hashlib
import inspect
import keyword
import re
import warnings
from enum import Enum
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir, ir_utils, types
from numba.core.imputils import lower_builtin, lower_constant
from numba.core.ir_utils import find_callname, find_const, get_definition, guard, mk_unique_var, require
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, overload
from numba.np.arrayobj import get_itemsize, make_array, populate_array
import bodo
from bodo.libs.binary_arr_ext import bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import num_total_chars, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import NOT_CONSTANT, BodoError, BodoWarning, MetaType
int128_type = types.Integer('int128', 128)


class CTypeEnum(Enum):
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
    Date = 13
    Datetime = 14
    Timedelta = 15
    Int128 = 16
    LIST = 18
    STRUCT = 19
    BINARY = 20


_numba_to_c_type_map = {types.int8: CTypeEnum.Int8.value, types.uint8:
    CTypeEnum.UInt8.value, types.int32: CTypeEnum.Int32.value, types.uint32:
    CTypeEnum.UInt32.value, types.int64: CTypeEnum.Int64.value, types.
    uint64: CTypeEnum.UInt64.value, types.float32: CTypeEnum.Float32.value,
    types.float64: CTypeEnum.Float64.value, types.NPDatetime('ns'):
    CTypeEnum.Datetime.value, types.NPTimedelta('ns'): CTypeEnum.Timedelta.
    value, types.bool_: CTypeEnum.Bool.value, types.int16: CTypeEnum.Int16.
    value, types.uint16: CTypeEnum.UInt16.value, int128_type: CTypeEnum.
    Int128.value}
numba.core.errors.error_extras = {'unsupported_error': '', 'typing': '',
    'reportable': '', 'interpreter': '', 'constant_inference': ''}
np_alloc_callnames = 'empty', 'zeros', 'ones', 'full'
CONST_DICT_SLOW_WARN_THRESHOLD = 100


def unliteral_all(args):
    return tuple(types.unliteral(a) for a in args)


def get_constant(func_ir, var, default=NOT_CONSTANT):
    aqzto__siax = guard(get_definition, func_ir, var)
    if aqzto__siax is None:
        return default
    if isinstance(aqzto__siax, ir.Const):
        return aqzto__siax.value
    if isinstance(aqzto__siax, ir.Var):
        return get_constant(func_ir, aqzto__siax, default)
    return default


def numba_to_c_type(t):
    if isinstance(t, bodo.libs.decimal_arr_ext.Decimal128Type):
        return CTypeEnum.Decimal.value
    if t == bodo.hiframes.datetime_date_ext.datetime_date_type:
        return CTypeEnum.Date.value
    return _numba_to_c_type_map[t]


def is_alloc_callname(func_name, mod_name):
    return isinstance(mod_name, str) and (mod_name == 'numpy' and func_name in
        np_alloc_callnames or func_name == 'empty_inferred' and mod_name in
        ('numba.extending', 'numba.np.unsafe.ndarray') or func_name ==
        'pre_alloc_string_array' and mod_name == 'bodo.libs.str_arr_ext' or
        func_name == 'pre_alloc_binary_array' and mod_name ==
        'bodo.libs.binary_arr_ext' or func_name ==
        'alloc_random_access_string_array' and mod_name ==
        'bodo.libs.str_ext' or func_name == 'pre_alloc_array_item_array' and
        mod_name == 'bodo.libs.array_item_arr_ext' or func_name ==
        'pre_alloc_struct_array' and mod_name == 'bodo.libs.struct_arr_ext' or
        func_name == 'pre_alloc_map_array' and mod_name ==
        'bodo.libs.map_arr_ext' or func_name == 'pre_alloc_tuple_array' and
        mod_name == 'bodo.libs.tuple_arr_ext' or func_name ==
        'alloc_bool_array' and mod_name == 'bodo.libs.bool_arr_ext' or 
        func_name == 'alloc_int_array' and mod_name ==
        'bodo.libs.int_arr_ext' or func_name == 'alloc_datetime_date_array' and
        mod_name == 'bodo.hiframes.datetime_date_ext' or func_name ==
        'alloc_datetime_timedelta_array' and mod_name ==
        'bodo.hiframes.datetime_timedelta_ext' or func_name ==
        'alloc_decimal_array' and mod_name == 'bodo.libs.decimal_arr_ext' or
        func_name == 'alloc_categorical_array' and mod_name ==
        'bodo.hiframes.pd_categorical_ext' or func_name == 'gen_na_array' and
        mod_name == 'bodo.libs.array_kernels')


def find_build_tuple(func_ir, var):
    require(isinstance(var, (ir.Var, str)))
    rng__hkb = get_definition(func_ir, var)
    require(isinstance(rng__hkb, ir.Expr))
    require(rng__hkb.op == 'build_tuple')
    return rng__hkb.items


def cprint(*s):
    print(*s)


@infer_global(cprint)
class CprintInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.none, *unliteral_all(args))


typ_to_format = {types.int32: 'd', types.uint32: 'u', types.int64: 'lld',
    types.uint64: 'llu', types.float32: 'f', types.float64: 'lf', types.
    voidptr: 's'}


@lower_builtin(cprint, types.VarArg(types.Any))
def cprint_lower(context, builder, sig, args):
    for gzml__zrzx, val in enumerate(args):
        typ = sig.args[gzml__zrzx]
        if isinstance(typ, types.ArrayCTypes):
            cgutils.printf(builder, '%p ', val)
            continue
        zyb__kjzcq = typ_to_format[typ]
        cgutils.printf(builder, '%{} '.format(zyb__kjzcq), val)
    cgutils.printf(builder, '\n')
    return context.get_dummy_value()


def is_whole_slice(typemap, func_ir, var, accept_stride=False):
    require(typemap[var.name] == types.slice2_type or accept_stride and 
        typemap[var.name] == types.slice3_type)
    taz__losa = get_definition(func_ir, var)
    require(isinstance(taz__losa, ir.Expr) and taz__losa.op == 'call')
    assert len(taz__losa.args) == 2 or accept_stride and len(taz__losa.args
        ) == 3
    assert find_callname(func_ir, taz__losa) == ('slice', 'builtins')
    deba__ntsfx = get_definition(func_ir, taz__losa.args[0])
    wrj__bdi = get_definition(func_ir, taz__losa.args[1])
    require(isinstance(deba__ntsfx, ir.Const) and deba__ntsfx.value == None)
    require(isinstance(wrj__bdi, ir.Const) and wrj__bdi.value == None)
    return True


def is_slice_equiv_arr(arr_var, index_var, func_ir, equiv_set,
    accept_stride=False):
    uzlsd__jfabj = get_definition(func_ir, index_var)
    require(find_callname(func_ir, uzlsd__jfabj) == ('slice', 'builtins'))
    require(len(uzlsd__jfabj.args) in (2, 3))
    require(find_const(func_ir, uzlsd__jfabj.args[0]) in (0, None))
    require(equiv_set.is_equiv(uzlsd__jfabj.args[1], arr_var.name + '#0'))
    require(accept_stride or len(uzlsd__jfabj.args) == 2 or find_const(
        func_ir, uzlsd__jfabj.args[2]) == 1)
    return True


def get_slice_step(typemap, func_ir, var):
    require(typemap[var.name] == types.slice3_type)
    taz__losa = get_definition(func_ir, var)
    require(isinstance(taz__losa, ir.Expr) and taz__losa.op == 'call')
    assert len(taz__losa.args) == 3
    return taz__losa.args[2]


def is_array_typ(var_typ, include_index_series=True):
    return is_np_array_typ(var_typ) or var_typ in (string_array_type, bodo.
        binary_array_type, bodo.hiframes.split_impl.
        string_array_split_view_type, bodo.hiframes.datetime_date_ext.
        datetime_date_array_type, bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type, boolean_array, bodo.libs.str_ext.
        random_access_string_array) or isinstance(var_typ, (
        IntegerArrayType, bodo.libs.decimal_arr_ext.DecimalArrayType, bodo.
        hiframes.pd_categorical_ext.CategoricalArrayType, bodo.libs.
        array_item_arr_ext.ArrayItemArrayType, bodo.libs.struct_arr_ext.
        StructArrayType, bodo.libs.interval_arr_ext.IntervalArrayType, bodo
        .libs.tuple_arr_ext.TupleArrayType, bodo.libs.map_arr_ext.
        MapArrayType, bodo.libs.csr_matrix_ext.CSRMatrixType)
        ) or include_index_series and (isinstance(var_typ, (bodo.hiframes.
        pd_series_ext.SeriesType, bodo.hiframes.pd_multi_index_ext.
        MultiIndexType)) or bodo.hiframes.pd_index_ext.is_pd_index_type(
        var_typ))


def is_np_array_typ(var_typ):
    return isinstance(var_typ, types.Array)


def is_distributable_typ(var_typ):
    return is_array_typ(var_typ) or isinstance(var_typ, bodo.hiframes.table
        .TableType) or isinstance(var_typ, bodo.hiframes.pd_dataframe_ext.
        DataFrameType) or isinstance(var_typ, types.List
        ) and is_distributable_typ(var_typ.dtype) or isinstance(var_typ,
        types.DictType) and is_distributable_typ(var_typ.value_type)


def is_distributable_tuple_typ(var_typ):
    return isinstance(var_typ, types.BaseTuple) and any(
        is_distributable_typ(t) or is_distributable_tuple_typ(t) for t in
        var_typ.types) or isinstance(var_typ, types.List
        ) and is_distributable_tuple_typ(var_typ.dtype) or isinstance(var_typ,
        types.DictType) and is_distributable_tuple_typ(var_typ.value_type
        ) or isinstance(var_typ, types.iterators.EnumerateType) and (
        is_distributable_typ(var_typ.yield_type[1]) or
        is_distributable_tuple_typ(var_typ.yield_type[1]))


@numba.generated_jit(nopython=True, cache=True)
def build_set_seen_na(A):

    def impl(A):
        s = dict()
        qyi__cuvn = False
        for gzml__zrzx in range(len(A)):
            if bodo.libs.array_kernels.isna(A, gzml__zrzx):
                qyi__cuvn = True
                continue
            s[A[gzml__zrzx]] = 0
        return s, qyi__cuvn
    return impl


@numba.generated_jit(nopython=True, cache=True)
def build_set(A):
    if isinstance(A, IntegerArrayType) or A in (string_array_type,
        boolean_array):

        def impl_int_arr(A):
            s = dict()
            for gzml__zrzx in range(len(A)):
                if not bodo.libs.array_kernels.isna(A, gzml__zrzx):
                    s[A[gzml__zrzx]] = 0
            return s
        return impl_int_arr
    else:

        def impl(A):
            s = dict()
            for gzml__zrzx in range(len(A)):
                s[A[gzml__zrzx]] = 0
            return s
        return impl


def to_array(A):
    return np.array(A)


@overload(to_array, no_unliteral=True)
def to_array_overload(A):
    if isinstance(A, types.DictType):
        dtype = A.key_type

        def impl(A):
            n = len(A)
            arr = alloc_type(n, dtype, (-1,))
            gzml__zrzx = 0
            for v in A.keys():
                arr[gzml__zrzx] = v
                gzml__zrzx += 1
            return arr
        return impl

    def to_array_impl(A):
        return np.array(A)
    try:
        numba.njit(to_array_impl).get_call_template((A,), {})
        return to_array_impl
    except:
        pass


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def unique(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:
        return lambda A: A.unique()
    return lambda A: to_array(build_set(A))


def empty_like_type(n, arr):
    return np.empty(n, arr.dtype)


@overload(empty_like_type, no_unliteral=True)
def empty_like_type_overload(n, arr):
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return (lambda n, arr: bodo.hiframes.pd_categorical_ext.
            alloc_categorical_array(n, arr.dtype))
    if isinstance(arr, types.Array):
        return lambda n, arr: np.empty(n, arr.dtype)
    if isinstance(arr, types.List) and arr.dtype == string_type:

        def empty_like_type_str_list(n, arr):
            return [''] * n
        return empty_like_type_str_list
    if isinstance(arr, types.List) and arr.dtype == bytes_type:

        def empty_like_type_binary_list(n, arr):
            return [b''] * n
        return empty_like_type_binary_list
    if isinstance(arr, IntegerArrayType):
        wrs__nye = arr.dtype

        def empty_like_type_int_arr(n, arr):
            return bodo.libs.int_arr_ext.alloc_int_array(n, wrs__nye)
        return empty_like_type_int_arr
    if arr == boolean_array:

        def empty_like_type_bool_arr(n, arr):
            return bodo.libs.bool_arr_ext.alloc_bool_array(n)
        return empty_like_type_bool_arr
    if arr == bodo.hiframes.datetime_date_ext.datetime_date_array_type:

        def empty_like_type_datetime_date_arr(n, arr):
            return bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(n)
        return empty_like_type_datetime_date_arr
    if (arr == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type):

        def empty_like_type_datetime_timedelta_arr(n, arr):
            return (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(n))
        return empty_like_type_datetime_timedelta_arr
    if isinstance(arr, bodo.libs.decimal_arr_ext.DecimalArrayType):
        precision = arr.precision
        scale = arr.scale

        def empty_like_type_decimal_arr(n, arr):
            return bodo.libs.decimal_arr_ext.alloc_decimal_array(n,
                precision, scale)
        return empty_like_type_decimal_arr
    assert arr == string_array_type

    def empty_like_type_str_arr(n, arr):
        gvlhy__ncgou = 20
        if len(arr) != 0:
            gvlhy__ncgou = num_total_chars(arr) // len(arr)
        return pre_alloc_string_array(n, n * gvlhy__ncgou)
    return empty_like_type_str_arr


def _empty_nd_impl(context, builder, arrtype, shapes):
    ycpnu__wmm = make_array(arrtype)
    yrx__pdbv = ycpnu__wmm(context, builder)
    urb__jzu = context.get_data_type(arrtype.dtype)
    scrzz__dbwnt = context.get_constant(types.intp, get_itemsize(context,
        arrtype))
    ecpn__ppuq = context.get_constant(types.intp, 1)
    deyx__wghd = lir.Constant(lir.IntType(1), 0)
    for s in shapes:
        ksag__actce = builder.smul_with_overflow(ecpn__ppuq, s)
        ecpn__ppuq = builder.extract_value(ksag__actce, 0)
        deyx__wghd = builder.or_(deyx__wghd, builder.extract_value(
            ksag__actce, 1))
    if arrtype.ndim == 0:
        alxx__zfgp = ()
    elif arrtype.layout == 'C':
        alxx__zfgp = [scrzz__dbwnt]
        for cgj__ogyx in reversed(shapes[1:]):
            alxx__zfgp.append(builder.mul(alxx__zfgp[-1], cgj__ogyx))
        alxx__zfgp = tuple(reversed(alxx__zfgp))
    elif arrtype.layout == 'F':
        alxx__zfgp = [scrzz__dbwnt]
        for cgj__ogyx in shapes[:-1]:
            alxx__zfgp.append(builder.mul(alxx__zfgp[-1], cgj__ogyx))
        alxx__zfgp = tuple(alxx__zfgp)
    else:
        raise NotImplementedError(
            "Don't know how to allocate array with layout '{0}'.".format(
            arrtype.layout))
    dijv__mpv = builder.smul_with_overflow(ecpn__ppuq, scrzz__dbwnt)
    zcx__eclo = builder.extract_value(dijv__mpv, 0)
    deyx__wghd = builder.or_(deyx__wghd, builder.extract_value(dijv__mpv, 1))
    with builder.if_then(deyx__wghd, likely=False):
        cgutils.printf(builder,
            'array is too big; `arr.size * arr.dtype.itemsize` is larger than the maximum possible size.'
            )
    dtype = arrtype.dtype
    dbf__ovf = context.get_preferred_array_alignment(dtype)
    dud__owe = context.get_constant(types.uint32, dbf__ovf)
    uus__vsfze = context.nrt.meminfo_alloc_aligned(builder, size=zcx__eclo,
        align=dud__owe)
    data = context.nrt.meminfo_data(builder, uus__vsfze)
    zqo__juwt = context.get_value_type(types.intp)
    rgjc__znjze = cgutils.pack_array(builder, shapes, ty=zqo__juwt)
    mpclo__qes = cgutils.pack_array(builder, alxx__zfgp, ty=zqo__juwt)
    populate_array(yrx__pdbv, data=builder.bitcast(data, urb__jzu.
        as_pointer()), shape=rgjc__znjze, strides=mpclo__qes, itemsize=
        scrzz__dbwnt, meminfo=uus__vsfze)
    return yrx__pdbv


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.np.arrayobj._empty_nd_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b6a998927680caa35917a553c79704e9d813d8f1873d83a5f8513837c159fa29':
        warnings.warn('numba.np.arrayobj._empty_nd_impl has changed')


def alloc_arr_tup(n, arr_tup, init_vals=()):
    enbr__duowg = []
    for yyzb__ben in arr_tup:
        enbr__duowg.append(np.empty(n, yyzb__ben.dtype))
    return tuple(enbr__duowg)


@overload(alloc_arr_tup, no_unliteral=True)
def alloc_arr_tup_overload(n, data, init_vals=()):
    rpmsq__zup = data.count
    arbhi__euh = ','.join(['empty_like_type(n, data[{}])'.format(gzml__zrzx
        ) for gzml__zrzx in range(rpmsq__zup)])
    if init_vals != ():
        arbhi__euh = ','.join(['np.full(n, init_vals[{}], data[{}].dtype)'.
            format(gzml__zrzx, gzml__zrzx) for gzml__zrzx in range(rpmsq__zup)]
            )
    nuvnn__jmofi = 'def f(n, data, init_vals=()):\n'
    nuvnn__jmofi += '  return ({}{})\n'.format(arbhi__euh, ',' if 
        rpmsq__zup == 1 else '')
    clgy__zzhhi = {}
    exec(nuvnn__jmofi, {'empty_like_type': empty_like_type, 'np': np},
        clgy__zzhhi)
    momjo__ylmoo = clgy__zzhhi['f']
    return momjo__ylmoo


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def tuple_to_scalar(n):
    if isinstance(n, types.BaseTuple) and len(n.types) == 1:
        return lambda n: n[0]
    return lambda n: n


def alloc_type(n, t, s=None):
    return np.empty(n, t.dtype)


@overload(alloc_type)
def overload_alloc_type(n, t, s=None):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    if typ == string_array_type:
        return (lambda n, t, s=None: bodo.libs.str_arr_ext.
            pre_alloc_string_array(n, s[0]))
    if typ == bodo.binary_array_type:
        return (lambda n, t, s=None: bodo.libs.binary_arr_ext.
            pre_alloc_binary_array(n, s[0]))
    if isinstance(typ, bodo.libs.array_item_arr_ext.ArrayItemArrayType):
        dtype = typ.dtype
        return (lambda n, t, s=None: bodo.libs.array_item_arr_ext.
            pre_alloc_array_item_array(n, s, dtype))
    if isinstance(typ, bodo.libs.struct_arr_ext.StructArrayType):
        dtypes = typ.data
        names = typ.names
        return (lambda n, t, s=None: bodo.libs.struct_arr_ext.
            pre_alloc_struct_array(n, s, dtypes, names))
    if isinstance(typ, bodo.libs.map_arr_ext.MapArrayType):
        struct_typ = bodo.libs.struct_arr_ext.StructArrayType((typ.
            key_arr_type, typ.value_arr_type), ('key', 'value'))
        return lambda n, t, s=None: bodo.libs.map_arr_ext.pre_alloc_map_array(n
            , s, struct_typ)
    if isinstance(typ, bodo.libs.tuple_arr_ext.TupleArrayType):
        dtypes = typ.data
        return (lambda n, t, s=None: bodo.libs.tuple_arr_ext.
            pre_alloc_tuple_array(n, s, dtypes))
    if isinstance(typ, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        if isinstance(t, types.TypeRef):
            if typ.dtype.categories is None:
                raise BodoError(
                    'UDFs or Groupbys that return Categorical values must have categories known at compile time.'
                    )
            is_ordered = typ.dtype.ordered
            int_type = typ.dtype.int_type
            new_cats_arr = pd.CategoricalDtype(typ.dtype.categories, is_ordered
                ).categories.values
            new_cats_tup = MetaType(tuple(new_cats_arr))
            return (lambda n, t, s=None: bodo.hiframes.pd_categorical_ext.
                alloc_categorical_array(n, bodo.hiframes.pd_categorical_ext
                .init_cat_dtype(bodo.utils.conversion.index_from_array(
                new_cats_arr), is_ordered, int_type, new_cats_tup)))
        else:
            return (lambda n, t, s=None: bodo.hiframes.pd_categorical_ext.
                alloc_categorical_array(n, t.dtype))
    if typ.dtype == bodo.hiframes.datetime_date_ext.datetime_date_type:
        return (lambda n, t, s=None: bodo.hiframes.datetime_date_ext.
            alloc_datetime_date_array(n))
    if (typ.dtype == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_type):
        return (lambda n, t, s=None: bodo.hiframes.datetime_timedelta_ext.
            alloc_datetime_timedelta_array(n))
    if isinstance(typ, DecimalArrayType):
        precision = typ.dtype.precision
        scale = typ.dtype.scale
        return (lambda n, t, s=None: bodo.libs.decimal_arr_ext.
            alloc_decimal_array(n, precision, scale))
    dtype = numba.np.numpy_support.as_dtype(typ.dtype)
    if isinstance(typ, IntegerArrayType):
        return lambda n, t, s=None: bodo.libs.int_arr_ext.alloc_int_array(n,
            dtype)
    if typ == boolean_array:
        return lambda n, t, s=None: bodo.libs.bool_arr_ext.alloc_bool_array(n)
    return lambda n, t, s=None: np.empty(n, dtype)


def astype(A, t):
    return A.astype(t.dtype)


@overload(astype, no_unliteral=True)
def overload_astype(A, t):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    dtype = typ.dtype
    if A == typ:
        return lambda A, t: A
    if isinstance(A, (types.Array, IntegerArrayType)) and isinstance(typ,
        types.Array):
        return lambda A, t: A.astype(dtype)
    if isinstance(typ, IntegerArrayType):
        return lambda A, t: bodo.libs.int_arr_ext.init_integer_array(A.
            astype(dtype), np.full(len(A) + 7 >> 3, 255, np.uint8))
    raise BodoError(f'cannot convert array type {A} to {typ}')


def full_type(n, val, t):
    return np.full(n, val, t.dtype)


@overload(full_type, no_unliteral=True)
def overload_full_type(n, val, t):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    if isinstance(typ, types.Array):
        dtype = numba.np.numpy_support.as_dtype(typ.dtype)
        return lambda n, val, t: np.full(n, val, dtype)
    if isinstance(typ, IntegerArrayType):
        dtype = numba.np.numpy_support.as_dtype(typ.dtype)
        return lambda n, val, t: bodo.libs.int_arr_ext.init_integer_array(np
            .full(n, val, dtype), np.full(tuple_to_scalar(n) + 7 >> 3, 255,
            np.uint8))
    if typ == boolean_array:
        return lambda n, val, t: bodo.libs.bool_arr_ext.init_bool_array(np.
            full(n, val, np.bool_), np.full(tuple_to_scalar(n) + 7 >> 3, 
            255, np.uint8))
    if typ == string_array_type:

        def impl_str(n, val, t):
            uov__thnpv = n * len(val)
            A = pre_alloc_string_array(n, uov__thnpv)
            for gzml__zrzx in range(n):
                A[gzml__zrzx] = val
            return A
        return impl_str

    def impl(n, val, t):
        A = alloc_type(n, typ, (-1,))
        for gzml__zrzx in range(n):
            A[gzml__zrzx] = val
        return A
    return impl


@intrinsic
def get_ctypes_ptr(typingctx, ctypes_typ=None):
    assert isinstance(ctypes_typ, types.ArrayCTypes)

    def codegen(context, builder, sig, args):
        twc__ros, = args
        fsj__hullq = context.make_helper(builder, sig.args[0], twc__ros)
        return fsj__hullq.data
    return types.voidptr(ctypes_typ), codegen


@intrinsic
def is_null_pointer(typingctx, ptr_typ=None):

    def codegen(context, builder, signature, args):
        liuj__yzmn, = args
        dnxg__zxfwg = context.get_constant_null(ptr_typ)
        return builder.icmp_unsigned('==', liuj__yzmn, dnxg__zxfwg)
    return types.bool_(ptr_typ), codegen


@intrinsic
def is_null_value(typingctx, val_typ=None):

    def codegen(context, builder, signature, args):
        val, = args
        cat__wlctp = cgutils.alloca_once_value(builder, val)
        jobfg__kyyzq = cgutils.alloca_once_value(builder, context.
            get_constant_null(val_typ))
        return is_ll_eq(builder, cat__wlctp, jobfg__kyyzq)
    return types.bool_(val_typ), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def tuple_list_to_array(A, data, elem_type):
    elem_type = elem_type.instance_type if isinstance(elem_type, types.TypeRef
        ) else elem_type
    nuvnn__jmofi = 'def impl(A, data, elem_type):\n'
    nuvnn__jmofi += '  for i, d in enumerate(data):\n'
    if elem_type == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        nuvnn__jmofi += (
            '    A[i] = bodo.utils.conversion.unbox_if_timestamp(d)\n')
    else:
        nuvnn__jmofi += '    A[i] = d\n'
    clgy__zzhhi = {}
    exec(nuvnn__jmofi, {'bodo': bodo}, clgy__zzhhi)
    impl = clgy__zzhhi['impl']
    return impl


def object_length(c, obj):
    edqpn__wjscs = c.context.get_argument_type(types.pyobject)
    guuxe__nwlmb = lir.FunctionType(lir.IntType(64), [edqpn__wjscs])
    btvdo__umjk = cgutils.get_or_insert_function(c.builder.module,
        guuxe__nwlmb, name='PyObject_Length')
    return c.builder.call(btvdo__umjk, (obj,))


def sequence_getitem(c, obj, ind):
    edqpn__wjscs = c.context.get_argument_type(types.pyobject)
    guuxe__nwlmb = lir.FunctionType(edqpn__wjscs, [edqpn__wjscs, lir.
        IntType(64)])
    btvdo__umjk = cgutils.get_or_insert_function(c.builder.module,
        guuxe__nwlmb, name='PySequence_GetItem')
    return c.builder.call(btvdo__umjk, (obj, ind))


@intrinsic
def incref(typingctx, data=None):

    def codegen(context, builder, signature, args):
        bgl__uyiir, = args
        context.nrt.incref(builder, signature.args[0], bgl__uyiir)
    return types.void(data), codegen


def gen_getitem(out_var, in_var, ind, calltypes, nodes):
    udhng__irdzn = out_var.loc
    zqude__awpx = ir.Expr.static_getitem(in_var, ind, None, udhng__irdzn)
    calltypes[zqude__awpx] = None
    nodes.append(ir.Assign(zqude__awpx, out_var, udhng__irdzn))


def is_static_getsetitem(node):
    return is_expr(node, 'static_getitem') or isinstance(node, ir.StaticSetItem
        )


def get_getsetitem_index_var(node, typemap, nodes):
    index_var = node.index_var if is_static_getsetitem(node) else node.index
    if index_var is None:
        assert is_static_getsetitem(node)
        try:
            hrhr__fzkr = types.literal(node.index)
        except:
            hrhr__fzkr = numba.typeof(node.index)
        index_var = ir.Var(node.value.scope, ir_utils.mk_unique_var(
            'dummy_index'), node.loc)
        typemap[index_var.name] = hrhr__fzkr
        nodes.append(ir.Assign(ir.Const(node.index, node.loc), index_var,
            node.loc))
    return index_var


import copy
ir.Const.__deepcopy__ = lambda self, memo: ir.Const(self.value, copy.
    deepcopy(self.loc))


def is_call_assign(stmt):
    return isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
        ) and stmt.value.op == 'call'


def is_call(expr):
    return isinstance(expr, ir.Expr) and expr.op == 'call'


def is_var_assign(inst):
    return isinstance(inst, ir.Assign) and isinstance(inst.value, ir.Var)


def is_assign(inst):
    return isinstance(inst, ir.Assign)


def is_expr(val, op):
    return isinstance(val, ir.Expr) and val.op == op


def sanitize_varname(varname):
    if isinstance(varname, (tuple, list)):
        varname = '_'.join(sanitize_varname(v) for v in varname)
    varname = str(varname)
    egks__supn = re.sub('\\W+', '_', varname)
    if not egks__supn or not egks__supn[0].isalpha():
        egks__supn = '_' + egks__supn
    if not egks__supn.isidentifier() or keyword.iskeyword(egks__supn):
        egks__supn = mk_unique_var('new_name').replace('.', '_')
    return egks__supn


def dump_node_list(node_list):
    for n in node_list:
        print('   ', n)


def debug_prints():
    return numba.core.config.DEBUG_ARRAY_OPT == 1


@overload(reversed)
def list_reverse(A):
    if isinstance(A, types.List):

        def impl_reversed(A):
            ajjpi__fvh = len(A)
            for gzml__zrzx in range(ajjpi__fvh):
                yield A[ajjpi__fvh - 1 - gzml__zrzx]
        return impl_reversed


@numba.njit()
def count_nonnan(a):
    return np.count_nonzero(~np.isnan(a))


@numba.njit()
def nanvar_ddof1(a):
    vdlie__xihip = count_nonnan(a)
    if vdlie__xihip <= 1:
        return np.nan
    return np.nanvar(a) * (vdlie__xihip / (vdlie__xihip - 1))


@numba.njit()
def nanstd_ddof1(a):
    return np.sqrt(nanvar_ddof1(a))


def has_supported_h5py():
    try:
        import h5py
        from bodo.io import _hdf5
    except ImportError as nlmbv__jnpi:
        auy__dbifk = False
    else:
        auy__dbifk = h5py.version.hdf5_version_tuple[1] == 10
    return auy__dbifk


def check_h5py():
    if not has_supported_h5py():
        raise BodoError("install 'h5py' package to enable hdf5 support")


def has_pyarrow():
    try:
        import pyarrow
    except ImportError as nlmbv__jnpi:
        tjykq__vzquv = False
    else:
        tjykq__vzquv = True
    return tjykq__vzquv


def has_scipy():
    try:
        import scipy
    except ImportError as nlmbv__jnpi:
        spsu__xfe = False
    else:
        spsu__xfe = True
    return spsu__xfe


@intrinsic
def check_and_propagate_cpp_exception(typingctx):

    def codegen(context, builder, sig, args):
        saq__ovzj = context.get_python_api(builder)
        evzhs__smq = saq__ovzj.err_occurred()
        kxhfo__lhxcm = cgutils.is_not_null(builder, evzhs__smq)
        with builder.if_then(kxhfo__lhxcm):
            builder.ret(numba.core.callconv.RETCODE_EXC)
    return types.void(), codegen


def inlined_check_and_propagate_cpp_exception(context, builder):
    saq__ovzj = context.get_python_api(builder)
    evzhs__smq = saq__ovzj.err_occurred()
    kxhfo__lhxcm = cgutils.is_not_null(builder, evzhs__smq)
    with builder.if_then(kxhfo__lhxcm):
        builder.ret(numba.core.callconv.RETCODE_EXC)


@numba.njit
def check_java_installation(fname):
    with numba.objmode():
        check_java_installation_(fname)


def check_java_installation_(fname):
    if not fname.startswith('hdfs://'):
        return
    import shutil
    if not shutil.which('java'):
        zvxk__ifwmi = (
            "Java not found. Make sure openjdk is installed for hdfs. openjdk can be installed by calling 'conda install openjdk=8 -c conda-forge'."
            )
        raise BodoError(zvxk__ifwmi)


dt_err = """
        If you are trying to set NULL values for timedelta64 in regular Python, 

        consider using np.timedelta64('nat') instead of None
        """


def lower_const_dict_fast_path(context, builder, typ, pyval):
    from bodo.utils.typing import can_replace
    hqk__uxey = pd.Series(pyval.keys()).values
    xqyee__zolay = pd.Series(pyval.values()).values
    kpicb__qkp = bodo.typeof(hqk__uxey)
    phmhn__ftx = bodo.typeof(xqyee__zolay)
    require(kpicb__qkp.dtype == typ.key_type or can_replace(typ.key_type,
        kpicb__qkp.dtype))
    require(phmhn__ftx.dtype == typ.value_type or can_replace(typ.
        value_type, phmhn__ftx.dtype))
    bnwsy__tseqt = context.get_constant_generic(builder, kpicb__qkp, hqk__uxey)
    pgxcs__hgcs = context.get_constant_generic(builder, phmhn__ftx,
        xqyee__zolay)

    def create_dict(keys, vals):
        eunij__tnsz = {}
        for k, v in zip(keys, vals):
            eunij__tnsz[k] = v
        return eunij__tnsz
    nrh__gzkl = context.compile_internal(builder, create_dict, typ(
        kpicb__qkp, phmhn__ftx), [bnwsy__tseqt, pgxcs__hgcs])
    return nrh__gzkl


@lower_constant(types.DictType)
def lower_constant_dict(context, builder, typ, pyval):
    try:
        return lower_const_dict_fast_path(context, builder, typ, pyval)
    except:
        pass
    if len(pyval) > CONST_DICT_SLOW_WARN_THRESHOLD:
        warnings.warn(BodoWarning(
            'Using large global dictionaries can result in long compilation times. Please pass large dictionaries as arguments to JIT functions.'
            ))
    xmvn__cmx = typ.key_type
    ddonj__igt = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(xmvn__cmx, ddonj__igt)
    nrh__gzkl = context.compile_internal(builder, make_dict, typ(), [])

    def set_dict_val(d, k, v):
        d[k] = v
    for k, v in pyval.items():
        fhlft__mgezj = context.get_constant_generic(builder, xmvn__cmx, k)
        xovkv__jnsyt = context.get_constant_generic(builder, ddonj__igt, v)
        context.compile_internal(builder, set_dict_val, types.none(typ,
            xmvn__cmx, ddonj__igt), [nrh__gzkl, fhlft__mgezj, xovkv__jnsyt])
    return nrh__gzkl
