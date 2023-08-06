import datetime
import operator
import warnings
import llvmlite.llvmpy.core as lc
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_constant
from numba.core.typing.templates import AttributeTemplate, signature
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
import bodo.hiframes
import bodo.utils.conversion
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_overload_const_func, get_overload_const_str, get_udf_error_msg, get_udf_out_arr_type, get_val_type_maybe_str_literal, is_const_func_type, is_heterogeneous_tuple_type, is_iterable_type, is_overload_false, is_overload_none, is_overload_true, parse_dtype, raise_bodo_error
from bodo.utils.utils import is_null_value
_dt_index_data_typ = types.Array(types.NPDatetime('ns'), 1, 'C')
_timedelta_index_data_typ = types.Array(types.NPTimedelta('ns'), 1, 'C')
iNaT = pd._libs.tslibs.iNaT
NaT = types.NPDatetime('ns')('NaT')
idx_cpy_arg_defaults = dict(deep=False, dtype=None, names=None)
idx_typ_to_format_str_map = dict()


@typeof_impl.register(pd.Index)
def typeof_pd_index(val, c):
    if val.inferred_type == 'string' or pd._libs.lib.infer_dtype(val, True
        ) == 'string':
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'bytes' or pd._libs.lib.infer_dtype(val, True
        ) == 'bytes':
        return BinaryIndexType(get_val_type_maybe_str_literal(val.name))
    if val.equals(pd.Index([])):
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'date':
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'integer' or pd._libs.lib.infer_dtype(val, True
        ) == 'integer':
        return NumericIndexType(types.int64, get_val_type_maybe_str_literal
            (val.name), IntegerArrayType(types.int64))
    if val.inferred_type == 'boolean' or pd._libs.lib.infer_dtype(val, True
        ) == 'boolean':
        return NumericIndexType(types.bool_, get_val_type_maybe_str_literal
            (val.name), boolean_array)
    raise NotImplementedError(f'unsupported pd.Index type {val}')


class DatetimeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.datetime64ns, 1, 'C'
            ) if data is None else data
        super(DatetimeIndexType, self).__init__(name=
            f'DatetimeIndex({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.NPDatetime('ns')

    def copy(self):
        return DatetimeIndexType(self.name_typ)

    @property
    def key(self):
        return self.name_typ, self.data

    @property
    def iterator_type(self):
        return types.iterators.ArrayIterator(_dt_index_data_typ)

    @property
    def pandas_type_name(self):
        return 'datetime64'

    @property
    def numpy_type_name(self):
        return 'datetime64[ns]'


types.datetime_index = DatetimeIndexType()


@typeof_impl.register(pd.DatetimeIndex)
def typeof_datetime_index(val, c):
    return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(DatetimeIndexType)
class DatetimeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fnrg__wanxk = [('data', _dt_index_data_typ), ('name', fe_type.
            name_typ), ('dict', types.DictType(_dt_index_data_typ.dtype,
            types.int64))]
        super(DatetimeIndexModel, self).__init__(dmm, fe_type, fnrg__wanxk)


make_attribute_wrapper(DatetimeIndexType, 'data', '_data')
make_attribute_wrapper(DatetimeIndexType, 'name', '_name')
make_attribute_wrapper(DatetimeIndexType, 'dict', '_dict')


@overload_method(DatetimeIndexType, 'copy', no_unliteral=True)
def overload_datetime_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    qmp__dcp = dict(deep=deep, dtype=dtype, names=names)
    brsjr__dfpjg = idx_typ_to_format_str_map[DatetimeIndexType].format('copy()'
        )
    check_unsupported_args('copy', qmp__dcp, idx_cpy_arg_defaults, fn_str=
        brsjr__dfpjg, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), A._name)
    return impl


@box(DatetimeIndexType)
def box_dt_index(typ, val, c):
    ojfd__vmg = c.context.insert_const_string(c.builder.module, 'pandas')
    kfw__qdild = c.pyapi.import_module_noblock(ojfd__vmg)
    lzxi__nem = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, _dt_index_data_typ, lzxi__nem.data)
    qazic__rau = c.pyapi.from_native_value(_dt_index_data_typ, lzxi__nem.
        data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, lzxi__nem.name)
    cvck__hcmxt = c.pyapi.from_native_value(typ.name_typ, lzxi__nem.name, c
        .env_manager)
    args = c.pyapi.tuple_pack([qazic__rau])
    kws = c.pyapi.dict_pack([('name', cvck__hcmxt)])
    psuj__rkz = c.pyapi.object_getattr_string(kfw__qdild, 'DatetimeIndex')
    mcfhl__tjdzk = c.pyapi.call(psuj__rkz, args, kws)
    c.pyapi.decref(qazic__rau)
    c.pyapi.decref(cvck__hcmxt)
    c.pyapi.decref(kfw__qdild)
    c.pyapi.decref(psuj__rkz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return mcfhl__tjdzk


@unbox(DatetimeIndexType)
def unbox_datetime_index(typ, val, c):
    xgjge__pzstx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_dt_index_data_typ, xgjge__pzstx).value
    cvck__hcmxt = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, cvck__hcmxt).value
    c.pyapi.decref(xgjge__pzstx)
    c.pyapi.decref(cvck__hcmxt)
    ubzoy__lgm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ubzoy__lgm.data = data
    ubzoy__lgm.name = name
    dtype = _dt_index_data_typ.dtype
    onnz__sbn, oyv__dcjy = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    ubzoy__lgm.dict = oyv__dcjy
    return NativeValue(ubzoy__lgm._getvalue())


@intrinsic
def init_datetime_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        kpem__cxlm, ixiig__nyy = args
        lzxi__nem = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        lzxi__nem.data = kpem__cxlm
        lzxi__nem.name = ixiig__nyy
        context.nrt.incref(builder, signature.args[0], kpem__cxlm)
        context.nrt.incref(builder, signature.args[1], ixiig__nyy)
        dtype = _dt_index_data_typ.dtype
        lzxi__nem.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return lzxi__nem._getvalue()
    swp__oxh = DatetimeIndexType(name)
    sig = signature(swp__oxh, data, name)
    return sig, codegen


def init_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) >= 1 and not kws
    xeyi__nmhoe = args[0]
    if equiv_set.has_shape(xeyi__nmhoe):
        return ArrayAnalysis.AnalyzeResult(shape=xeyi__nmhoe, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_datetime_index
    ) = init_index_equiv


def gen_dti_field_impl(field):
    ecwp__wldbc = 'def impl(dti):\n'
    ecwp__wldbc += '    numba.parfors.parfor.init_prange()\n'
    ecwp__wldbc += '    A = bodo.hiframes.pd_index_ext.get_index_data(dti)\n'
    ecwp__wldbc += (
        '    name = bodo.hiframes.pd_index_ext.get_index_name(dti)\n')
    ecwp__wldbc += '    n = len(A)\n'
    ecwp__wldbc += '    S = np.empty(n, np.int64)\n'
    ecwp__wldbc += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    ecwp__wldbc += (
        '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(A[i])\n'
        )
    ecwp__wldbc += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
    if field in ['weekday']:
        ecwp__wldbc += '        S[i] = ts.' + field + '()\n'
    else:
        ecwp__wldbc += '        S[i] = ts.' + field + '\n'
    ecwp__wldbc += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    yoez__yxw = {}
    exec(ecwp__wldbc, {'numba': numba, 'np': np, 'bodo': bodo}, yoez__yxw)
    impl = yoez__yxw['impl']
    return impl


def _install_dti_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        if field in ['is_leap_year']:
            continue
        impl = gen_dti_field_impl(field)
        overload_attribute(DatetimeIndexType, field)(lambda dti: impl)


_install_dti_date_fields()


@overload_attribute(DatetimeIndexType, 'is_leap_year')
def overload_datetime_index_is_leap_year(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        ful__jwfl = len(A)
        S = np.empty(ful__jwfl, np.bool_)
        for i in numba.parfors.parfor.internal_prange(ful__jwfl):
            wsm__pbok = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(A[i])
            tiwxx__dhivy = (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(wsm__pbok))
            S[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(tiwxx__dhivy
                .year)
        return S
    return impl


@overload_attribute(DatetimeIndexType, 'date')
def overload_datetime_index_date(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        ful__jwfl = len(A)
        S = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(ful__jwfl
            )
        for i in numba.parfors.parfor.internal_prange(ful__jwfl):
            wsm__pbok = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(A[i])
            tiwxx__dhivy = (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(wsm__pbok))
            S[i] = datetime.date(tiwxx__dhivy.year, tiwxx__dhivy.month,
                tiwxx__dhivy.day)
        return S
    return impl


@numba.njit(no_cpython_wrapper=True)
def _dti_val_finalize(s, count):
    if not count:
        s = iNaT
    return bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(s)


@numba.njit(no_cpython_wrapper=True)
def _tdi_val_finalize(s, count):
    return pd.Timedelta('nan') if not count else pd.Timedelta(s)


@overload_method(DatetimeIndexType, 'min', no_unliteral=True)
def overload_datetime_index_min(dti, axis=None, skipna=True):
    lrz__cta = dict(axis=axis, skipna=skipna)
    unip__jwg = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.min', lrz__cta, unip__jwg,
        package_name='pandas', module_name='Index')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        kqz__mkxne = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_max_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(kqz__mkxne)):
            if not bodo.libs.array_kernels.isna(kqz__mkxne, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(kqz__mkxne
                    [i])
                s = min(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'max', no_unliteral=True)
def overload_datetime_index_max(dti, axis=None, skipna=True):
    lrz__cta = dict(axis=axis, skipna=skipna)
    unip__jwg = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.max', lrz__cta, unip__jwg,
        package_name='pandas', module_name='Index')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        kqz__mkxne = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_min_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(kqz__mkxne)):
            if not bodo.libs.array_kernels.isna(kqz__mkxne, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(kqz__mkxne
                    [i])
                s = max(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@infer_getattr
class DatetimeIndexAttribute(AttributeTemplate):
    key = DatetimeIndexType

    def resolve_values(self, ary):
        return _dt_index_data_typ


@overload(pd.DatetimeIndex, no_unliteral=True)
def pd_datetimeindex_overload(data=None, freq=None, tz=None, normalize=
    False, closed=None, ambiguous='raise', dayfirst=False, yearfirst=False,
    dtype=None, copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.DatetimeIndex() expected')
    lrz__cta = dict(freq=freq, tz=tz, normalize=normalize, closed=closed,
        ambiguous=ambiguous, dayfirst=dayfirst, yearfirst=yearfirst, dtype=
        dtype, copy=copy)
    unip__jwg = dict(freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False)
    check_unsupported_args('pandas.DatetimeIndex', lrz__cta, unip__jwg,
        package_name='pandas', module_name='Index')

    def f(data=None, freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False, name=None):
        uefyi__euhha = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_dt64ns(uefyi__euhha)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


def overload_sub_operator_datetime_index(lhs, rhs):
    if isinstance(lhs, DatetimeIndexType
        ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        bof__qyrp = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            kqz__mkxne = bodo.hiframes.pd_index_ext.get_index_data(lhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(lhs)
            ful__jwfl = len(kqz__mkxne)
            S = np.empty(ful__jwfl, bof__qyrp)
            yrad__oxng = rhs.value
            for i in numba.parfors.parfor.internal_prange(ful__jwfl):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kqz__mkxne[i]) - yrad__oxng)
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl
    if isinstance(rhs, DatetimeIndexType
        ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        bof__qyrp = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            kqz__mkxne = bodo.hiframes.pd_index_ext.get_index_data(rhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(rhs)
            ful__jwfl = len(kqz__mkxne)
            S = np.empty(ful__jwfl, bof__qyrp)
            yrad__oxng = lhs.value
            for i in numba.parfors.parfor.internal_prange(ful__jwfl):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    yrad__oxng - bodo.hiframes.pd_timestamp_ext.
                    dt64_to_integer(kqz__mkxne[i]))
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl


def gen_dti_str_binop_impl(op, is_lhs_dti):
    snh__qcrrv = numba.core.utils.OPERATORS_TO_BUILTINS[op]
    ecwp__wldbc = 'def impl(lhs, rhs):\n'
    if is_lhs_dti:
        ecwp__wldbc += '  dt_index, _str = lhs, rhs\n'
        kie__ugka = 'arr[i] {} other'.format(snh__qcrrv)
    else:
        ecwp__wldbc += '  dt_index, _str = rhs, lhs\n'
        kie__ugka = 'other {} arr[i]'.format(snh__qcrrv)
    ecwp__wldbc += (
        '  arr = bodo.hiframes.pd_index_ext.get_index_data(dt_index)\n')
    ecwp__wldbc += '  l = len(arr)\n'
    ecwp__wldbc += (
        '  other = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(_str)\n')
    ecwp__wldbc += '  S = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    ecwp__wldbc += '  for i in numba.parfors.parfor.internal_prange(l):\n'
    ecwp__wldbc += '    S[i] = {}\n'.format(kie__ugka)
    ecwp__wldbc += '  return S\n'
    yoez__yxw = {}
    exec(ecwp__wldbc, {'bodo': bodo, 'numba': numba, 'np': np}, yoez__yxw)
    impl = yoez__yxw['impl']
    return impl


def overload_binop_dti_str(op):

    def overload_impl(lhs, rhs):
        if isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, True)
        if isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, False)
    return overload_impl


@overload(pd.Index, inline='always', no_unliteral=True)
def pd_index_overload(data=None, dtype=None, copy=False, name=None,
    tupleize_cols=True):
    data = types.unliteral(data) if not isinstance(data, types.LiteralList
        ) else data
    lan__vjfg = getattr(data, 'dtype', None)
    if not is_overload_none(dtype):
        gnf__haa = parse_dtype(dtype, 'pandas.Index')
    else:
        gnf__haa = lan__vjfg
    if isinstance(gnf__haa, types.misc.PyObject):
        raise BodoError(
            "pd.Index() object 'dtype' is not specific enough for typing. Please provide a more exact type (e.g. str)."
            )
    if isinstance(data, RangeIndexType):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.RangeIndex(data, name=name)
    elif isinstance(data, DatetimeIndexType) or gnf__haa == types.NPDatetime(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.DatetimeIndex(data, name=name)
    elif isinstance(data, TimedeltaIndexType) or gnf__haa == types.NPTimedelta(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.TimedeltaIndex(data, name=name)
    elif is_heterogeneous_tuple_type(data):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return bodo.hiframes.pd_index_ext.init_heter_index(data, name)
        return impl
    elif bodo.utils.utils.is_array_typ(data, False) or isinstance(data, (
        SeriesType, types.List, types.UniTuple)):
        if isinstance(gnf__haa, (types.Integer, types.Float, types.Boolean)):

            def impl(data=None, dtype=None, copy=False, name=None,
                tupleize_cols=True):
                uefyi__euhha = bodo.utils.conversion.coerce_to_array(data)
                qsrhq__qhfp = bodo.utils.conversion.fix_arr_dtype(uefyi__euhha,
                    gnf__haa)
                return bodo.hiframes.pd_index_ext.init_numeric_index(
                    qsrhq__qhfp, name)
        elif gnf__haa in [types.string, bytes_type]:

            def impl(data=None, dtype=None, copy=False, name=None,
                tupleize_cols=True):
                return bodo.hiframes.pd_index_ext.init_binary_str_index(bodo
                    .utils.conversion.coerce_to_array(data), name)
        else:
            raise BodoError(
                'pd.Index(): provided array is of unsupported type.')
    elif is_overload_none(data):
        raise BodoError(
            'data argument in pd.Index() is invalid: None or scalar is not acceptable'
            )
    else:
        raise BodoError(
            f'pd.Index(): the provided argument type {data} is not supported')
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_datetime_index_getitem(dti, ind):
    if isinstance(dti, DatetimeIndexType):
        if isinstance(ind, types.Integer):

            def impl(dti, ind):
                iaaj__ozda = bodo.hiframes.pd_index_ext.get_index_data(dti)
                wsm__pbok = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iaaj__ozda[ind])
                return (bodo.hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(wsm__pbok))
            return impl
        else:

            def impl(dti, ind):
                iaaj__ozda = bodo.hiframes.pd_index_ext.get_index_data(dti)
                name = bodo.hiframes.pd_index_ext.get_index_name(dti)
                blwhr__cmiww = iaaj__ozda[ind]
                return bodo.hiframes.pd_index_ext.init_datetime_index(
                    blwhr__cmiww, name)
            return impl


@overload(operator.getitem, no_unliteral=True)
def overload_timedelta_index_getitem(I, ind):
    if not isinstance(I, TimedeltaIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            jern__vjkao = bodo.hiframes.pd_index_ext.get_index_data(I)
            return pd.Timedelta(jern__vjkao[ind])
        return impl

    def impl(I, ind):
        jern__vjkao = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        blwhr__cmiww = jern__vjkao[ind]
        return bodo.hiframes.pd_index_ext.init_timedelta_index(blwhr__cmiww,
            name)
    return impl


@numba.njit(no_cpython_wrapper=True)
def validate_endpoints(closed):
    kvsnn__hnx = False
    zrmw__dgvt = False
    if closed is None:
        kvsnn__hnx = True
        zrmw__dgvt = True
    elif closed == 'left':
        kvsnn__hnx = True
    elif closed == 'right':
        zrmw__dgvt = True
    else:
        raise ValueError("Closed has to be either 'left', 'right' or None")
    return kvsnn__hnx, zrmw__dgvt


@numba.njit(no_cpython_wrapper=True)
def to_offset_value(freq):
    if freq is None:
        return None
    with numba.objmode(r='int64'):
        r = pd.tseries.frequencies.to_offset(freq).nanos
    return r


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _dummy_convert_none_to_int(val):
    if is_overload_none(val):

        def impl(val):
            return 0
        return impl
    if isinstance(val, types.Optional):

        def impl(val):
            if val is None:
                return 0
            return bodo.utils.indexing.unoptional(val)
        return impl
    return lambda val: val


@overload(pd.date_range, no_unliteral=True)
def pd_date_range_overload(start=None, end=None, periods=None, freq=None,
    tz=None, normalize=False, name=None, closed=None):
    lrz__cta = dict(tz=tz, normalize=normalize)
    unip__jwg = dict(tz=None, normalize=False)
    check_unsupported_args('pandas.date_range', lrz__cta, unip__jwg,
        package_name='pandas', module_name='General')
    if not is_overload_none(tz):
        raise BodoError('pd.date_range(): tz argument not supported yet')
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise BodoError(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )

    def f(start=None, end=None, periods=None, freq=None, tz=None, normalize
        =False, name=None, closed=None):
        if freq is None and (start is None or end is None or periods is None):
            freq = 'D'
        freq = bodo.hiframes.pd_index_ext.to_offset_value(freq)
        xfu__kddwy = pd.Timestamp('2018-01-01')
        if start is not None:
            xfu__kddwy = pd.Timestamp(start)
        dbk__zoqp = pd.Timestamp('2018-01-01')
        if end is not None:
            dbk__zoqp = pd.Timestamp(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of startand end are defined'
                )
        kvsnn__hnx, zrmw__dgvt = bodo.hiframes.pd_index_ext.validate_endpoints(
            closed)
        if freq is not None:
            bfg__fzyo = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = xfu__kddwy.value
                asnf__sdgw = b + (dbk__zoqp.value - b
                    ) // bfg__fzyo * bfg__fzyo + bfg__fzyo // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = xfu__kddwy.value
                jltmv__rvg = np.int64(periods) * np.int64(bfg__fzyo)
                asnf__sdgw = np.int64(b) + jltmv__rvg
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                asnf__sdgw = dbk__zoqp.value + bfg__fzyo
                jltmv__rvg = np.int64(periods) * np.int64(-bfg__fzyo)
                b = np.int64(asnf__sdgw) + jltmv__rvg
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            zggg__rdkrr = np.arange(b, asnf__sdgw, bfg__fzyo, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            eta__jhhpw = dbk__zoqp.value - xfu__kddwy.value
            step = eta__jhhpw / (periods - 1)
            ovrxh__iao = np.arange(0, periods, 1, np.float64)
            ovrxh__iao *= step
            ovrxh__iao += xfu__kddwy.value
            zggg__rdkrr = ovrxh__iao.astype(np.int64)
            zggg__rdkrr[-1] = dbk__zoqp.value
        if not kvsnn__hnx and len(zggg__rdkrr) and zggg__rdkrr[0
            ] == xfu__kddwy.value:
            zggg__rdkrr = zggg__rdkrr[1:]
        if not zrmw__dgvt and len(zggg__rdkrr) and zggg__rdkrr[-1
            ] == dbk__zoqp.value:
            zggg__rdkrr = zggg__rdkrr[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(zggg__rdkrr)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


@overload(pd.timedelta_range, no_unliteral=True)
def pd_timedelta_range_overload(start=None, end=None, periods=None, freq=
    None, name=None, closed=None):
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise BodoError(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )

    def f(start=None, end=None, periods=None, freq=None, name=None, closed=None
        ):
        if freq is None and (start is None or end is None or periods is None):
            freq = 'D'
        freq = bodo.hiframes.pd_index_ext.to_offset_value(freq)
        xfu__kddwy = pd.Timedelta('1 day')
        if start is not None:
            xfu__kddwy = pd.Timedelta(start)
        dbk__zoqp = pd.Timedelta('1 day')
        if end is not None:
            dbk__zoqp = pd.Timedelta(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of start and end are defined'
                )
        kvsnn__hnx, zrmw__dgvt = bodo.hiframes.pd_index_ext.validate_endpoints(
            closed)
        if freq is not None:
            bfg__fzyo = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = xfu__kddwy.value
                asnf__sdgw = b + (dbk__zoqp.value - b
                    ) // bfg__fzyo * bfg__fzyo + bfg__fzyo // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = xfu__kddwy.value
                jltmv__rvg = np.int64(periods) * np.int64(bfg__fzyo)
                asnf__sdgw = np.int64(b) + jltmv__rvg
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                asnf__sdgw = dbk__zoqp.value + bfg__fzyo
                jltmv__rvg = np.int64(periods) * np.int64(-bfg__fzyo)
                b = np.int64(asnf__sdgw) + jltmv__rvg
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            zggg__rdkrr = np.arange(b, asnf__sdgw, bfg__fzyo, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            eta__jhhpw = dbk__zoqp.value - xfu__kddwy.value
            step = eta__jhhpw / (periods - 1)
            ovrxh__iao = np.arange(0, periods, 1, np.float64)
            ovrxh__iao *= step
            ovrxh__iao += xfu__kddwy.value
            zggg__rdkrr = ovrxh__iao.astype(np.int64)
            zggg__rdkrr[-1] = dbk__zoqp.value
        if not kvsnn__hnx and len(zggg__rdkrr) and zggg__rdkrr[0
            ] == xfu__kddwy.value:
            zggg__rdkrr = zggg__rdkrr[1:]
        if not zrmw__dgvt and len(zggg__rdkrr) and zggg__rdkrr[-1
            ] == dbk__zoqp.value:
            zggg__rdkrr = zggg__rdkrr[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(zggg__rdkrr)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return f


@overload_method(DatetimeIndexType, 'isocalendar', inline='always',
    no_unliteral=True)
def overload_pd_timestamp_isocalendar(idx):

    def impl(idx):
        A = bodo.hiframes.pd_index_ext.get_index_data(idx)
        numba.parfors.parfor.init_prange()
        ful__jwfl = len(A)
        okm__fib = bodo.libs.int_arr_ext.alloc_int_array(ful__jwfl, np.uint32)
        ewnx__plgxv = bodo.libs.int_arr_ext.alloc_int_array(ful__jwfl, np.
            uint32)
        ohzc__jsjx = bodo.libs.int_arr_ext.alloc_int_array(ful__jwfl, np.uint32
            )
        for i in numba.parfors.parfor.internal_prange(ful__jwfl):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(okm__fib, i)
                bodo.libs.array_kernels.setna(ewnx__plgxv, i)
                bodo.libs.array_kernels.setna(ohzc__jsjx, i)
                continue
            okm__fib[i], ewnx__plgxv[i], ohzc__jsjx[i
                ] = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(
                A[i]).isocalendar()
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((okm__fib,
            ewnx__plgxv, ohzc__jsjx), idx, ('year', 'week', 'day'))
    return impl


class TimedeltaIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.timedelta64ns, 1, 'C'
            ) if data is None else data
        super(TimedeltaIndexType, self).__init__(name=
            f'TimedeltaIndexType({name_typ}, {self.data})')
    ndim = 1

    def copy(self):
        return TimedeltaIndexType(self.name_typ)

    @property
    def dtype(self):
        return types.NPTimedelta('ns')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.name_typ, self.data

    @property
    def iterator_type(self):
        return types.iterators.ArrayIterator(_timedelta_index_data_typ)

    @property
    def pandas_type_name(self):
        return 'timedelta'

    @property
    def numpy_type_name(self):
        return 'timedelta64[ns]'


timedelta_index = TimedeltaIndexType()
types.timedelta_index = timedelta_index


@register_model(TimedeltaIndexType)
class TimedeltaIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fnrg__wanxk = [('data', _timedelta_index_data_typ), ('name',
            fe_type.name_typ), ('dict', types.DictType(
            _timedelta_index_data_typ.dtype, types.int64))]
        super(TimedeltaIndexTypeModel, self).__init__(dmm, fe_type, fnrg__wanxk
            )


@typeof_impl.register(pd.TimedeltaIndex)
def typeof_timedelta_index(val, c):
    return TimedeltaIndexType(get_val_type_maybe_str_literal(val.name))


@box(TimedeltaIndexType)
def box_timedelta_index(typ, val, c):
    ojfd__vmg = c.context.insert_const_string(c.builder.module, 'pandas')
    kfw__qdild = c.pyapi.import_module_noblock(ojfd__vmg)
    timedelta_index = numba.core.cgutils.create_struct_proxy(typ)(c.context,
        c.builder, val)
    c.context.nrt.incref(c.builder, _timedelta_index_data_typ,
        timedelta_index.data)
    qazic__rau = c.pyapi.from_native_value(_timedelta_index_data_typ,
        timedelta_index.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, timedelta_index.name)
    cvck__hcmxt = c.pyapi.from_native_value(typ.name_typ, timedelta_index.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([qazic__rau])
    kws = c.pyapi.dict_pack([('name', cvck__hcmxt)])
    psuj__rkz = c.pyapi.object_getattr_string(kfw__qdild, 'TimedeltaIndex')
    mcfhl__tjdzk = c.pyapi.call(psuj__rkz, args, kws)
    c.pyapi.decref(qazic__rau)
    c.pyapi.decref(cvck__hcmxt)
    c.pyapi.decref(kfw__qdild)
    c.pyapi.decref(psuj__rkz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return mcfhl__tjdzk


@unbox(TimedeltaIndexType)
def unbox_timedelta_index(typ, val, c):
    xgjge__pzstx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_timedelta_index_data_typ, xgjge__pzstx
        ).value
    cvck__hcmxt = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, cvck__hcmxt).value
    c.pyapi.decref(xgjge__pzstx)
    c.pyapi.decref(cvck__hcmxt)
    ubzoy__lgm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ubzoy__lgm.data = data
    ubzoy__lgm.name = name
    dtype = _timedelta_index_data_typ.dtype
    onnz__sbn, oyv__dcjy = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    ubzoy__lgm.dict = oyv__dcjy
    return NativeValue(ubzoy__lgm._getvalue())


@intrinsic
def init_timedelta_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        kpem__cxlm, ixiig__nyy = args
        timedelta_index = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        timedelta_index.data = kpem__cxlm
        timedelta_index.name = ixiig__nyy
        context.nrt.incref(builder, signature.args[0], kpem__cxlm)
        context.nrt.incref(builder, signature.args[1], ixiig__nyy)
        dtype = _timedelta_index_data_typ.dtype
        timedelta_index.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return timedelta_index._getvalue()
    swp__oxh = TimedeltaIndexType(name)
    sig = signature(swp__oxh, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_timedelta_index
    ) = init_index_equiv


@infer_getattr
class TimedeltaIndexAttribute(AttributeTemplate):
    key = TimedeltaIndexType

    def resolve_values(self, ary):
        return _timedelta_index_data_typ


make_attribute_wrapper(TimedeltaIndexType, 'data', '_data')
make_attribute_wrapper(TimedeltaIndexType, 'name', '_name')
make_attribute_wrapper(TimedeltaIndexType, 'dict', '_dict')


@overload_method(TimedeltaIndexType, 'copy', no_unliteral=True)
def overload_timedelta_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    qmp__dcp = dict(deep=deep, dtype=dtype, names=names)
    brsjr__dfpjg = idx_typ_to_format_str_map[TimedeltaIndexType].format(
        'copy()')
    check_unsupported_args('TimedeltaIndex.copy', qmp__dcp,
        idx_cpy_arg_defaults, fn_str=brsjr__dfpjg, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), A._name)
    return impl


@overload_method(TimedeltaIndexType, 'min', inline='always', no_unliteral=True)
def overload_timedelta_index_min(tdi, axis=None, skipna=True):
    lrz__cta = dict(axis=axis, skipna=skipna)
    unip__jwg = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.min', lrz__cta, unip__jwg,
        package_name='pandas', module_name='Index')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        ful__jwfl = len(data)
        evytf__doscz = numba.cpython.builtins.get_type_max_value(numba.core
            .types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(ful__jwfl):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            evytf__doscz = min(evytf__doscz, val)
        qaffv__dtbdk = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            evytf__doscz)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(qaffv__dtbdk, count
            )
    return impl


@overload_method(TimedeltaIndexType, 'max', inline='always', no_unliteral=True)
def overload_timedelta_index_max(tdi, axis=None, skipna=True):
    lrz__cta = dict(axis=axis, skipna=skipna)
    unip__jwg = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.max', lrz__cta, unip__jwg,
        package_name='pandas', module_name='Index')
    if not is_overload_none(axis) or not is_overload_true(skipna):
        raise BodoError(
            'Index.min(): axis and skipna arguments not supported yet')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        ful__jwfl = len(data)
        wonio__idlpg = numba.cpython.builtins.get_type_min_value(numba.core
            .types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(ful__jwfl):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            wonio__idlpg = max(wonio__idlpg, val)
        qaffv__dtbdk = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            wonio__idlpg)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(qaffv__dtbdk, count
            )
    return impl


def gen_tdi_field_impl(field):
    ecwp__wldbc = 'def impl(tdi):\n'
    ecwp__wldbc += '    numba.parfors.parfor.init_prange()\n'
    ecwp__wldbc += '    A = bodo.hiframes.pd_index_ext.get_index_data(tdi)\n'
    ecwp__wldbc += (
        '    name = bodo.hiframes.pd_index_ext.get_index_name(tdi)\n')
    ecwp__wldbc += '    n = len(A)\n'
    ecwp__wldbc += '    S = np.empty(n, np.int64)\n'
    ecwp__wldbc += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    ecwp__wldbc += (
        '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
        )
    if field == 'nanoseconds':
        ecwp__wldbc += '        S[i] = td64 % 1000\n'
    elif field == 'microseconds':
        ecwp__wldbc += '        S[i] = td64 // 1000 % 100000\n'
    elif field == 'seconds':
        ecwp__wldbc += (
            '        S[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
    elif field == 'days':
        ecwp__wldbc += (
            '        S[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
    else:
        assert False, 'invalid timedelta field'
    ecwp__wldbc += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    yoez__yxw = {}
    exec(ecwp__wldbc, {'numba': numba, 'np': np, 'bodo': bodo}, yoez__yxw)
    impl = yoez__yxw['impl']
    return impl


def _install_tdi_time_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        impl = gen_tdi_field_impl(field)
        overload_attribute(TimedeltaIndexType, field)(lambda tdi: impl)


_install_tdi_time_fields()


@overload(pd.TimedeltaIndex, no_unliteral=True)
def pd_timedelta_index_overload(data=None, unit=None, freq=None, dtype=None,
    copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.TimedeltaIndex() expected')
    lrz__cta = dict(unit=unit, freq=freq, dtype=dtype, copy=copy)
    unip__jwg = dict(unit=None, freq=None, dtype=None, copy=False)
    check_unsupported_args('pandas.TimedeltaIndex', lrz__cta, unip__jwg,
        package_name='pandas', module_name='Index')

    def impl(data=None, unit=None, freq=None, dtype=None, copy=False, name=None
        ):
        uefyi__euhha = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_td64ns(uefyi__euhha)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return impl


class RangeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None):
        if name_typ is None:
            name_typ = types.none
        self.name_typ = name_typ
        super(RangeIndexType, self).__init__(name='RangeIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return RangeIndexType(self.name_typ)

    @property
    def iterator_type(self):
        return types.iterators.RangeIteratorType(types.int64)

    @property
    def dtype(self):
        return types.int64

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)

    def unify(self, typingctx, other):
        if isinstance(other, NumericIndexType):
            name_typ = self.name_typ.unify(typingctx, other.name_typ)
            if name_typ is None:
                name_typ = types.none
            return NumericIndexType(types.int64, name_typ)


@typeof_impl.register(pd.RangeIndex)
def typeof_pd_range_index(val, c):
    return RangeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(RangeIndexType)
class RangeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fnrg__wanxk = [('start', types.int64), ('stop', types.int64), (
            'step', types.int64), ('name', fe_type.name_typ)]
        super(RangeIndexModel, self).__init__(dmm, fe_type, fnrg__wanxk)


make_attribute_wrapper(RangeIndexType, 'start', '_start')
make_attribute_wrapper(RangeIndexType, 'stop', '_stop')
make_attribute_wrapper(RangeIndexType, 'step', '_step')
make_attribute_wrapper(RangeIndexType, 'name', '_name')


@overload_method(RangeIndexType, 'copy', no_unliteral=True)
def overload_range_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    qmp__dcp = dict(deep=deep, dtype=dtype, names=names)
    brsjr__dfpjg = idx_typ_to_format_str_map[RangeIndexType].format('copy()')
    check_unsupported_args('RangeIndex.copy', qmp__dcp,
        idx_cpy_arg_defaults, fn_str=brsjr__dfpjg, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, A._name)
    return impl


@box(RangeIndexType)
def box_range_index(typ, val, c):
    ojfd__vmg = c.context.insert_const_string(c.builder.module, 'pandas')
    igdqj__ibfsl = c.pyapi.import_module_noblock(ojfd__vmg)
    xwcj__rtia = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    pgwaj__ohu = c.pyapi.from_native_value(types.int64, xwcj__rtia.start, c
        .env_manager)
    reh__otrg = c.pyapi.from_native_value(types.int64, xwcj__rtia.stop, c.
        env_manager)
    mvlyr__vxfm = c.pyapi.from_native_value(types.int64, xwcj__rtia.step, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, xwcj__rtia.name)
    cvck__hcmxt = c.pyapi.from_native_value(typ.name_typ, xwcj__rtia.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([pgwaj__ohu, reh__otrg, mvlyr__vxfm])
    kws = c.pyapi.dict_pack([('name', cvck__hcmxt)])
    psuj__rkz = c.pyapi.object_getattr_string(igdqj__ibfsl, 'RangeIndex')
    zpqdi__hiqhc = c.pyapi.call(psuj__rkz, args, kws)
    c.pyapi.decref(pgwaj__ohu)
    c.pyapi.decref(reh__otrg)
    c.pyapi.decref(mvlyr__vxfm)
    c.pyapi.decref(cvck__hcmxt)
    c.pyapi.decref(igdqj__ibfsl)
    c.pyapi.decref(psuj__rkz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return zpqdi__hiqhc


@intrinsic
def init_range_index(typingctx, start, stop, step, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 4
        xwcj__rtia = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        xwcj__rtia.start = args[0]
        xwcj__rtia.stop = args[1]
        xwcj__rtia.step = args[2]
        xwcj__rtia.name = args[3]
        context.nrt.incref(builder, signature.return_type.name_typ, args[3])
        return xwcj__rtia._getvalue()
    return RangeIndexType(name)(start, stop, step, name), codegen


def init_range_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    start, stop, step, pdvax__caa = args
    if self.typemap[start.name] == types.IntegerLiteral(0) and self.typemap[
        step.name] == types.IntegerLiteral(1) and equiv_set.has_shape(stop):
        return ArrayAnalysis.AnalyzeResult(shape=stop, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_range_index
    ) = init_range_index_equiv


@unbox(RangeIndexType)
def unbox_range_index(typ, val, c):
    pgwaj__ohu = c.pyapi.object_getattr_string(val, 'start')
    start = c.pyapi.to_native_value(types.int64, pgwaj__ohu).value
    reh__otrg = c.pyapi.object_getattr_string(val, 'stop')
    stop = c.pyapi.to_native_value(types.int64, reh__otrg).value
    mvlyr__vxfm = c.pyapi.object_getattr_string(val, 'step')
    step = c.pyapi.to_native_value(types.int64, mvlyr__vxfm).value
    cvck__hcmxt = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, cvck__hcmxt).value
    c.pyapi.decref(pgwaj__ohu)
    c.pyapi.decref(reh__otrg)
    c.pyapi.decref(mvlyr__vxfm)
    c.pyapi.decref(cvck__hcmxt)
    xwcj__rtia = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xwcj__rtia.start = start
    xwcj__rtia.stop = stop
    xwcj__rtia.step = step
    xwcj__rtia.name = name
    return NativeValue(xwcj__rtia._getvalue())


@lower_constant(RangeIndexType)
def lower_constant_range_index(context, builder, ty, pyval):
    start = context.get_constant(types.int64, pyval.start)
    stop = context.get_constant(types.int64, pyval.stop)
    step = context.get_constant(types.int64, pyval.step)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    return lir.Constant.literal_struct([start, stop, step, name])


@overload(pd.RangeIndex, no_unliteral=True, inline='always')
def range_index_overload(start=None, stop=None, step=None, dtype=None, copy
    =False, name=None):

    def _ensure_int_or_none(value, field):
        woisj__tuso = (
            'RangeIndex(...) must be called with integers, {value} was passed for {field}'
            )
        if not is_overload_none(value) and not isinstance(value, types.
            IntegerLiteral) and not isinstance(value, types.Integer):
            raise BodoError(woisj__tuso.format(value=value, field=field))
    _ensure_int_or_none(start, 'start')
    _ensure_int_or_none(stop, 'stop')
    _ensure_int_or_none(step, 'step')
    if is_overload_none(start) and is_overload_none(stop) and is_overload_none(
        step):
        woisj__tuso = 'RangeIndex(...) must be called with integers'
        raise BodoError(woisj__tuso)
    cdnxn__rvi = 'start'
    rgz__fbcg = 'stop'
    yofgh__bez = 'step'
    if is_overload_none(start):
        cdnxn__rvi = '0'
    if is_overload_none(stop):
        rgz__fbcg = 'start'
        cdnxn__rvi = '0'
    if is_overload_none(step):
        yofgh__bez = '1'
    ecwp__wldbc = """def _pd_range_index_imp(start=None, stop=None, step=None, dtype=None, copy=False, name=None):
"""
    ecwp__wldbc += '  return init_range_index({}, {}, {}, name)\n'.format(
        cdnxn__rvi, rgz__fbcg, yofgh__bez)
    yoez__yxw = {}
    exec(ecwp__wldbc, {'init_range_index': init_range_index}, yoez__yxw)
    nsaxu__ngmp = yoez__yxw['_pd_range_index_imp']
    return nsaxu__ngmp


@overload(pd.CategoricalIndex, no_unliteral=True, inline='always')
def categorical_index_overload(data=None, categories=None, ordered=None,
    dtype=None, copy=False, name=None):
    raise BodoError('pd.CategoricalIndex() initializer not yet supported.')


@overload_attribute(RangeIndexType, 'start')
def rangeIndex_get_start(ri):

    def impl(ri):
        return ri._start
    return impl


@overload_attribute(RangeIndexType, 'stop')
def rangeIndex_get_stop(ri):

    def impl(ri):
        return ri._stop
    return impl


@overload_attribute(RangeIndexType, 'step')
def rangeIndex_get_step(ri):

    def impl(ri):
        return ri._step
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_range_index_getitem(I, idx):
    if isinstance(I, RangeIndexType):
        if isinstance(types.unliteral(idx), types.Integer):
            return lambda I, idx: idx * I._step + I._start
        if isinstance(idx, types.SliceType):

            def impl(I, idx):
                qedld__usf = numba.cpython.unicode._normalize_slice(idx, len(I)
                    )
                name = bodo.hiframes.pd_index_ext.get_index_name(I)
                start = I._start + I._step * qedld__usf.start
                stop = I._start + I._step * qedld__usf.stop
                step = I._step * qedld__usf.step
                return bodo.hiframes.pd_index_ext.init_range_index(start,
                    stop, step, name)
            return impl
        return lambda I, idx: bodo.hiframes.pd_index_ext.init_numeric_index(np
            .arange(I._start, I._stop, I._step, np.int64)[idx], bodo.
            hiframes.pd_index_ext.get_index_name(I))


@overload(len, no_unliteral=True)
def overload_range_len(r):
    if isinstance(r, RangeIndexType):
        return lambda r: max(0, -(-(r._stop - r._start) // r._step))


class PeriodIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, freq, name_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.freq = freq
        self.name_typ = name_typ
        super(PeriodIndexType, self).__init__(name=
            'PeriodIndexType({}, {})'.format(freq, name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return PeriodIndexType(self.freq, self.name_typ)

    @property
    def iterator_type(self):
        return types.iterators.ArrayIterator(types.Array(types.int64, 1, 'C'))

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'period[{self.freq}]'


@typeof_impl.register(pd.PeriodIndex)
def typeof_pd_period_index(val, c):
    return PeriodIndexType(val.freqstr, get_val_type_maybe_str_literal(val.
        name))


@register_model(PeriodIndexType)
class PeriodIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fnrg__wanxk = [('data', bodo.IntegerArrayType(types.int64)), (
            'name', fe_type.name_typ), ('dict', types.DictType(types.int64,
            types.int64))]
        super(PeriodIndexModel, self).__init__(dmm, fe_type, fnrg__wanxk)


make_attribute_wrapper(PeriodIndexType, 'data', '_data')
make_attribute_wrapper(PeriodIndexType, 'name', '_name')
make_attribute_wrapper(PeriodIndexType, 'dict', '_dict')


@overload_method(PeriodIndexType, 'copy', no_unliteral=True)
def overload_period_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    freq = A.freq
    qmp__dcp = dict(deep=deep, dtype=dtype, names=names)
    brsjr__dfpjg = idx_typ_to_format_str_map[PeriodIndexType].format('copy()')
    check_unsupported_args('PeriodIndex.copy', qmp__dcp,
        idx_cpy_arg_defaults, fn_str=brsjr__dfpjg, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), name, freq)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), A._name, freq)
    return impl


@intrinsic
def init_period_index(typingctx, data, name, freq):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        kpem__cxlm, ixiig__nyy, pdvax__caa = args
        uvpl__yfd = signature.return_type
        tuw__mrwg = cgutils.create_struct_proxy(uvpl__yfd)(context, builder)
        tuw__mrwg.data = kpem__cxlm
        tuw__mrwg.name = ixiig__nyy
        context.nrt.incref(builder, signature.args[0], args[0])
        context.nrt.incref(builder, signature.args[1], args[1])
        tuw__mrwg.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(types.int64, types.int64), types.DictType(
            types.int64, types.int64)(), [])
        return tuw__mrwg._getvalue()
    muwoi__axgdi = get_overload_const_str(freq)
    swp__oxh = PeriodIndexType(muwoi__axgdi, name)
    sig = signature(swp__oxh, data, name, freq)
    return sig, codegen


@box(PeriodIndexType)
def box_period_index(typ, val, c):
    ojfd__vmg = c.context.insert_const_string(c.builder.module, 'pandas')
    igdqj__ibfsl = c.pyapi.import_module_noblock(ojfd__vmg)
    ubzoy__lgm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, bodo.IntegerArrayType(types.int64),
        ubzoy__lgm.data)
    zesyf__dzqs = c.pyapi.from_native_value(bodo.IntegerArrayType(types.
        int64), ubzoy__lgm.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ubzoy__lgm.name)
    cvck__hcmxt = c.pyapi.from_native_value(typ.name_typ, ubzoy__lgm.name,
        c.env_manager)
    epj__dlmr = c.pyapi.string_from_constant_string(typ.freq)
    args = c.pyapi.tuple_pack([])
    kws = c.pyapi.dict_pack([('ordinal', zesyf__dzqs), ('name', cvck__hcmxt
        ), ('freq', epj__dlmr)])
    psuj__rkz = c.pyapi.object_getattr_string(igdqj__ibfsl, 'PeriodIndex')
    zpqdi__hiqhc = c.pyapi.call(psuj__rkz, args, kws)
    c.pyapi.decref(zesyf__dzqs)
    c.pyapi.decref(cvck__hcmxt)
    c.pyapi.decref(epj__dlmr)
    c.pyapi.decref(igdqj__ibfsl)
    c.pyapi.decref(psuj__rkz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return zpqdi__hiqhc


@unbox(PeriodIndexType)
def unbox_period_index(typ, val, c):
    arr_typ = bodo.IntegerArrayType(types.int64)
    dpl__ptydh = c.pyapi.object_getattr_string(val, 'asi8')
    tovo__fjp = c.pyapi.call_method(val, 'isna', ())
    cvck__hcmxt = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, cvck__hcmxt).value
    ojfd__vmg = c.context.insert_const_string(c.builder.module, 'pandas')
    kfw__qdild = c.pyapi.import_module_noblock(ojfd__vmg)
    iev__ctpc = c.pyapi.object_getattr_string(kfw__qdild, 'arrays')
    zesyf__dzqs = c.pyapi.call_method(iev__ctpc, 'IntegerArray', (
        dpl__ptydh, tovo__fjp))
    data = c.pyapi.to_native_value(arr_typ, zesyf__dzqs).value
    c.pyapi.decref(dpl__ptydh)
    c.pyapi.decref(tovo__fjp)
    c.pyapi.decref(cvck__hcmxt)
    c.pyapi.decref(kfw__qdild)
    c.pyapi.decref(iev__ctpc)
    c.pyapi.decref(zesyf__dzqs)
    ubzoy__lgm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ubzoy__lgm.data = data
    ubzoy__lgm.name = name
    onnz__sbn, oyv__dcjy = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(types.int64, types.int64), types.DictType(types.int64, types.
        int64)(), [])
    ubzoy__lgm.dict = oyv__dcjy
    return NativeValue(ubzoy__lgm._getvalue())


class CategoricalIndexType(types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
        assert isinstance(data, CategoricalArrayType
            ), 'CategoricalIndexType expects CategoricalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(CategoricalIndexType, self).__init__(name=
            f'CategoricalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return CategoricalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'categorical'

    @property
    def numpy_type_name(self):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        return str(get_categories_int_type(self.dtype))


@register_model(CategoricalIndexType)
class CategoricalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        tcnm__qxb = get_categories_int_type(fe_type.data.dtype)
        fnrg__wanxk = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(tcnm__qxb, types.int64))]
        super(CategoricalIndexTypeModel, self).__init__(dmm, fe_type,
            fnrg__wanxk)


@typeof_impl.register(pd.CategoricalIndex)
def typeof_categorical_index(val, c):
    return CategoricalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(CategoricalIndexType)
def box_categorical_index(typ, val, c):
    ojfd__vmg = c.context.insert_const_string(c.builder.module, 'pandas')
    kfw__qdild = c.pyapi.import_module_noblock(ojfd__vmg)
    vfc__zlf = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, vfc__zlf.data)
    qazic__rau = c.pyapi.from_native_value(typ.data, vfc__zlf.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, vfc__zlf.name)
    cvck__hcmxt = c.pyapi.from_native_value(typ.name_typ, vfc__zlf.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([qazic__rau])
    kws = c.pyapi.dict_pack([('name', cvck__hcmxt)])
    psuj__rkz = c.pyapi.object_getattr_string(kfw__qdild, 'CategoricalIndex')
    mcfhl__tjdzk = c.pyapi.call(psuj__rkz, args, kws)
    c.pyapi.decref(qazic__rau)
    c.pyapi.decref(cvck__hcmxt)
    c.pyapi.decref(kfw__qdild)
    c.pyapi.decref(psuj__rkz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return mcfhl__tjdzk


@unbox(CategoricalIndexType)
def unbox_categorical_index(typ, val, c):
    from bodo.hiframes.pd_categorical_ext import get_categories_int_type
    xgjge__pzstx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, xgjge__pzstx).value
    cvck__hcmxt = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, cvck__hcmxt).value
    c.pyapi.decref(xgjge__pzstx)
    c.pyapi.decref(cvck__hcmxt)
    ubzoy__lgm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ubzoy__lgm.data = data
    ubzoy__lgm.name = name
    dtype = get_categories_int_type(typ.data.dtype)
    onnz__sbn, oyv__dcjy = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    ubzoy__lgm.dict = oyv__dcjy
    return NativeValue(ubzoy__lgm._getvalue())


@intrinsic
def init_categorical_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        kpem__cxlm, ixiig__nyy = args
        vfc__zlf = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        vfc__zlf.data = kpem__cxlm
        vfc__zlf.name = ixiig__nyy
        context.nrt.incref(builder, signature.args[0], kpem__cxlm)
        context.nrt.incref(builder, signature.args[1], ixiig__nyy)
        dtype = get_categories_int_type(signature.return_type.data.dtype)
        vfc__zlf.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return vfc__zlf._getvalue()
    swp__oxh = CategoricalIndexType(data, name)
    sig = signature(swp__oxh, data, name)
    return sig, codegen


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_categorical_index
    ) = init_index_equiv
make_attribute_wrapper(CategoricalIndexType, 'data', '_data')
make_attribute_wrapper(CategoricalIndexType, 'name', '_name')
make_attribute_wrapper(CategoricalIndexType, 'dict', '_dict')


@overload_method(CategoricalIndexType, 'copy', no_unliteral=True)
def overload_categorical_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    brsjr__dfpjg = idx_typ_to_format_str_map[CategoricalIndexType].format(
        'copy()')
    qmp__dcp = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('CategoricalIndex.copy', qmp__dcp,
        idx_cpy_arg_defaults, fn_str=brsjr__dfpjg, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), A._name)
    return impl


class IntervalIndexType(types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.libs.interval_arr_ext import IntervalArrayType
        assert isinstance(data, IntervalArrayType
            ), 'IntervalIndexType expects IntervalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(IntervalIndexType, self).__init__(name=
            f'IntervalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return IntervalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'interval[{self.data.arr_type.dtype}, right]'


@register_model(IntervalIndexType)
class IntervalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fnrg__wanxk = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(types.UniTuple(fe_type.data.arr_type.
            dtype, 2), types.int64))]
        super(IntervalIndexTypeModel, self).__init__(dmm, fe_type, fnrg__wanxk)


@typeof_impl.register(pd.IntervalIndex)
def typeof_interval_index(val, c):
    return IntervalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(IntervalIndexType)
def box_interval_index(typ, val, c):
    ojfd__vmg = c.context.insert_const_string(c.builder.module, 'pandas')
    kfw__qdild = c.pyapi.import_module_noblock(ojfd__vmg)
    bmfp__dut = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, bmfp__dut.data)
    qazic__rau = c.pyapi.from_native_value(typ.data, bmfp__dut.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, bmfp__dut.name)
    cvck__hcmxt = c.pyapi.from_native_value(typ.name_typ, bmfp__dut.name, c
        .env_manager)
    args = c.pyapi.tuple_pack([qazic__rau])
    kws = c.pyapi.dict_pack([('name', cvck__hcmxt)])
    psuj__rkz = c.pyapi.object_getattr_string(kfw__qdild, 'IntervalIndex')
    mcfhl__tjdzk = c.pyapi.call(psuj__rkz, args, kws)
    c.pyapi.decref(qazic__rau)
    c.pyapi.decref(cvck__hcmxt)
    c.pyapi.decref(kfw__qdild)
    c.pyapi.decref(psuj__rkz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return mcfhl__tjdzk


@unbox(IntervalIndexType)
def unbox_interval_index(typ, val, c):
    xgjge__pzstx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, xgjge__pzstx).value
    cvck__hcmxt = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, cvck__hcmxt).value
    c.pyapi.decref(xgjge__pzstx)
    c.pyapi.decref(cvck__hcmxt)
    ubzoy__lgm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ubzoy__lgm.data = data
    ubzoy__lgm.name = name
    dtype = types.UniTuple(typ.data.arr_type.dtype, 2)
    onnz__sbn, oyv__dcjy = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    ubzoy__lgm.dict = oyv__dcjy
    return NativeValue(ubzoy__lgm._getvalue())


@intrinsic
def init_interval_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        kpem__cxlm, ixiig__nyy = args
        bmfp__dut = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        bmfp__dut.data = kpem__cxlm
        bmfp__dut.name = ixiig__nyy
        context.nrt.incref(builder, signature.args[0], kpem__cxlm)
        context.nrt.incref(builder, signature.args[1], ixiig__nyy)
        dtype = types.UniTuple(data.arr_type.dtype, 2)
        bmfp__dut.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return bmfp__dut._getvalue()
    swp__oxh = IntervalIndexType(data, name)
    sig = signature(swp__oxh, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_interval_index
    ) = init_index_equiv
make_attribute_wrapper(IntervalIndexType, 'data', '_data')
make_attribute_wrapper(IntervalIndexType, 'name', '_name')
make_attribute_wrapper(IntervalIndexType, 'dict', '_dict')


class NumericIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, dtype, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.dtype = dtype
        self.name_typ = name_typ
        data = dtype_to_array_type(dtype) if data is None else data
        self.data = data
        super(NumericIndexType, self).__init__(name=
            f'NumericIndexType({dtype}, {name_typ}, {data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return NumericIndexType(self.dtype, self.name_typ, self.data)

    @property
    def iterator_type(self):
        return types.iterators.ArrayIterator(types.Array(self.dtype, 1, 'C'))

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)


@typeof_impl.register(pd.Int64Index)
def typeof_pd_int64_index(val, c):
    return NumericIndexType(types.int64, get_val_type_maybe_str_literal(val
        .name))


@typeof_impl.register(pd.UInt64Index)
def typeof_pd_uint64_index(val, c):
    return NumericIndexType(types.uint64, get_val_type_maybe_str_literal(
        val.name))


@typeof_impl.register(pd.Float64Index)
def typeof_pd_float64_index(val, c):
    return NumericIndexType(types.float64, get_val_type_maybe_str_literal(
        val.name))


@register_model(NumericIndexType)
class NumericIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fnrg__wanxk = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(fe_type.dtype, types.int64))]
        super(NumericIndexModel, self).__init__(dmm, fe_type, fnrg__wanxk)


make_attribute_wrapper(NumericIndexType, 'data', '_data')
make_attribute_wrapper(NumericIndexType, 'name', '_name')
make_attribute_wrapper(NumericIndexType, 'dict', '_dict')


@overload_method(NumericIndexType, 'copy', no_unliteral=True)
def overload_numeric_index_copy(A, name=None, deep=False, dtype=None, names
    =None):
    brsjr__dfpjg = idx_typ_to_format_str_map[NumericIndexType].format('copy()')
    qmp__dcp = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', qmp__dcp, idx_cpy_arg_defaults,
        fn_str=brsjr__dfpjg, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(NumericIndexType)
def box_numeric_index(typ, val, c):
    ojfd__vmg = c.context.insert_const_string(c.builder.module, 'pandas')
    igdqj__ibfsl = c.pyapi.import_module_noblock(ojfd__vmg)
    ubzoy__lgm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, ubzoy__lgm.data)
    zesyf__dzqs = c.pyapi.from_native_value(typ.data, ubzoy__lgm.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ubzoy__lgm.name)
    cvck__hcmxt = c.pyapi.from_native_value(typ.name_typ, ubzoy__lgm.name,
        c.env_manager)
    wcv__xjmuj = c.pyapi.make_none()
    yoyz__onahf = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    zpqdi__hiqhc = c.pyapi.call_method(igdqj__ibfsl, 'Index', (zesyf__dzqs,
        wcv__xjmuj, yoyz__onahf, cvck__hcmxt))
    c.pyapi.decref(zesyf__dzqs)
    c.pyapi.decref(wcv__xjmuj)
    c.pyapi.decref(yoyz__onahf)
    c.pyapi.decref(cvck__hcmxt)
    c.pyapi.decref(igdqj__ibfsl)
    c.context.nrt.decref(c.builder, typ, val)
    return zpqdi__hiqhc


@intrinsic
def init_numeric_index(typingctx, data, name=None):
    name = types.none if is_overload_none(name) else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        uvpl__yfd = signature.return_type
        ubzoy__lgm = cgutils.create_struct_proxy(uvpl__yfd)(context, builder)
        ubzoy__lgm.data = args[0]
        ubzoy__lgm.name = args[1]
        context.nrt.incref(builder, uvpl__yfd.data, args[0])
        context.nrt.incref(builder, uvpl__yfd.name_typ, args[1])
        dtype = uvpl__yfd.dtype
        ubzoy__lgm.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return ubzoy__lgm._getvalue()
    return NumericIndexType(data.dtype, name, data)(data, name), codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_numeric_index
    ) = init_index_equiv


@unbox(NumericIndexType)
def unbox_numeric_index(typ, val, c):
    xgjge__pzstx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, xgjge__pzstx).value
    cvck__hcmxt = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, cvck__hcmxt).value
    c.pyapi.decref(xgjge__pzstx)
    c.pyapi.decref(cvck__hcmxt)
    ubzoy__lgm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ubzoy__lgm.data = data
    ubzoy__lgm.name = name
    dtype = typ.dtype
    onnz__sbn, oyv__dcjy = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    ubzoy__lgm.dict = oyv__dcjy
    return NativeValue(ubzoy__lgm._getvalue())


def create_numeric_constructor(func, func_str, default_dtype):

    def overload_impl(data=None, dtype=None, copy=False, name=None):
        sqrwb__zvdxa = dict(dtype=dtype)
        hfidb__pecs = dict(dtype=None)
        check_unsupported_args(func_str, sqrwb__zvdxa, hfidb__pecs,
            package_name='pandas', module_name='Index')
        if is_overload_false(copy):

            def impl(data=None, dtype=None, copy=False, name=None):
                uefyi__euhha = bodo.utils.conversion.coerce_to_ndarray(data)
                jpsz__lru = bodo.utils.conversion.fix_arr_dtype(uefyi__euhha,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(jpsz__lru,
                    name)
        else:

            def impl(data=None, dtype=None, copy=False, name=None):
                uefyi__euhha = bodo.utils.conversion.coerce_to_ndarray(data)
                if copy:
                    uefyi__euhha = uefyi__euhha.copy()
                jpsz__lru = bodo.utils.conversion.fix_arr_dtype(uefyi__euhha,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(jpsz__lru,
                    name)
        return impl
    return overload_impl


def _install_numeric_constructors():
    for func, func_str, default_dtype in ((pd.Int64Index,
        'pandas.Int64Index', np.int64), (pd.UInt64Index,
        'pandas.UInt64Index', np.uint64), (pd.Float64Index,
        'pandas.Float64Index', np.float64)):
        overload_impl = create_numeric_constructor(func, func_str,
            default_dtype)
        overload(func, no_unliteral=True)(overload_impl)


_install_numeric_constructors()


class StringIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = string_array_type
        super(StringIndexType, self).__init__(name='StringIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return StringIndexType(self.name_typ)

    @property
    def dtype(self):
        return string_type

    @property
    def pandas_type_name(self):
        return 'unicode'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.libs.str_arr_ext.StringArrayIterator()


@register_model(StringIndexType)
class StringIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fnrg__wanxk = [('data', string_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(string_type, types.int64))]
        super(StringIndexModel, self).__init__(dmm, fe_type, fnrg__wanxk)


make_attribute_wrapper(StringIndexType, 'data', '_data')
make_attribute_wrapper(StringIndexType, 'name', '_name')
make_attribute_wrapper(StringIndexType, 'dict', '_dict')


class BinaryIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = binary_array_type
        super(BinaryIndexType, self).__init__(name='BinaryIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return BinaryIndexType(self.name_typ)

    @property
    def dtype(self):
        return bytes_type

    @property
    def pandas_type_name(self):
        return 'bytes'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.libs.binary_arr_ext.BinaryArrayIterator()


@register_model(BinaryIndexType)
class BinaryIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fnrg__wanxk = [('data', binary_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(bytes_type, types.int64))]
        super(BinaryIndexModel, self).__init__(dmm, fe_type, fnrg__wanxk)


make_attribute_wrapper(BinaryIndexType, 'data', '_data')
make_attribute_wrapper(BinaryIndexType, 'name', '_name')
make_attribute_wrapper(BinaryIndexType, 'dict', '_dict')


@unbox(BinaryIndexType)
@unbox(StringIndexType)
def unbox_binary_str_index(typ, val, c):
    zboe__lyq = typ.data
    scalar_type = typ.data.dtype
    xgjge__pzstx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(zboe__lyq, xgjge__pzstx).value
    cvck__hcmxt = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, cvck__hcmxt).value
    c.pyapi.decref(xgjge__pzstx)
    c.pyapi.decref(cvck__hcmxt)
    ubzoy__lgm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ubzoy__lgm.data = data
    ubzoy__lgm.name = name
    onnz__sbn, oyv__dcjy = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(scalar_type, types.int64), types.DictType(scalar_type, types.
        int64)(), [])
    ubzoy__lgm.dict = oyv__dcjy
    return NativeValue(ubzoy__lgm._getvalue())


@box(BinaryIndexType)
@box(StringIndexType)
def box_binary_str_index(typ, val, c):
    zboe__lyq = typ.data
    ojfd__vmg = c.context.insert_const_string(c.builder.module, 'pandas')
    igdqj__ibfsl = c.pyapi.import_module_noblock(ojfd__vmg)
    ubzoy__lgm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, zboe__lyq, ubzoy__lgm.data)
    zesyf__dzqs = c.pyapi.from_native_value(zboe__lyq, ubzoy__lgm.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ubzoy__lgm.name)
    cvck__hcmxt = c.pyapi.from_native_value(typ.name_typ, ubzoy__lgm.name,
        c.env_manager)
    wcv__xjmuj = c.pyapi.make_none()
    yoyz__onahf = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    zpqdi__hiqhc = c.pyapi.call_method(igdqj__ibfsl, 'Index', (zesyf__dzqs,
        wcv__xjmuj, yoyz__onahf, cvck__hcmxt))
    c.pyapi.decref(zesyf__dzqs)
    c.pyapi.decref(wcv__xjmuj)
    c.pyapi.decref(yoyz__onahf)
    c.pyapi.decref(cvck__hcmxt)
    c.pyapi.decref(igdqj__ibfsl)
    c.context.nrt.decref(c.builder, typ, val)
    return zpqdi__hiqhc


@intrinsic
def init_binary_str_index(typingctx, data, name=None):
    name = types.none if name is None else name
    sig = type(bodo.utils.typing.get_index_type_from_dtype(data.dtype))(name)(
        data, name)
    zcfy__htb = get_binary_str_codegen(is_binary=data.dtype == bytes_type)
    return sig, zcfy__htb


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_binary_str_index
    ) = init_index_equiv


def get_binary_str_codegen(is_binary=False):
    if is_binary:
        yto__wbu = 'binary_array_type'
        kwa__bpbk = 'bytes_type'
    else:
        yto__wbu = 'string_array_type'
        kwa__bpbk = 'string_type'
    ecwp__wldbc = 'def impl(context, builder, signature, args):\n'
    ecwp__wldbc += '    assert len(args) == 2\n'
    ecwp__wldbc += '    index_typ = signature.return_type\n'
    ecwp__wldbc += (
        '    index_val = cgutils.create_struct_proxy(index_typ)(context, builder)\n'
        )
    ecwp__wldbc += '    index_val.data = args[0]\n'
    ecwp__wldbc += '    index_val.name = args[1]\n'
    ecwp__wldbc += '    # increase refcount of stored values\n'
    ecwp__wldbc += f'    context.nrt.incref(builder, {yto__wbu}, args[0])\n'
    ecwp__wldbc += (
        '    context.nrt.incref(builder, index_typ.name_typ, args[1])\n')
    ecwp__wldbc += '    # create empty dict for get_loc hashmap\n'
    ecwp__wldbc += '    index_val.dict = context.compile_internal(\n'
    ecwp__wldbc += '       builder,\n'
    ecwp__wldbc += (
        f'       lambda: numba.typed.Dict.empty({kwa__bpbk}, types.int64),\n')
    ecwp__wldbc += (
        f'        types.DictType({kwa__bpbk}, types.int64)(), [],)\n')
    ecwp__wldbc += '    return index_val._getvalue()\n'
    yoez__yxw = {}
    exec(ecwp__wldbc, {'bodo': bodo, 'signature': signature, 'cgutils':
        cgutils, 'numba': numba, 'types': types, 'bytes_type': bytes_type,
        'string_type': string_type, 'string_array_type': string_array_type,
        'binary_array_type': binary_array_type}, yoez__yxw)
    impl = yoez__yxw['impl']
    return impl


@overload_method(BinaryIndexType, 'copy', no_unliteral=True)
@overload_method(StringIndexType, 'copy', no_unliteral=True)
def overload_binary_string_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    typ = type(A)
    brsjr__dfpjg = idx_typ_to_format_str_map[typ].format('copy()')
    qmp__dcp = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', qmp__dcp, idx_cpy_arg_defaults,
        fn_str=brsjr__dfpjg, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), A._name)
    return impl


@overload_attribute(BinaryIndexType, 'name')
@overload_attribute(StringIndexType, 'name')
@overload_attribute(DatetimeIndexType, 'name')
@overload_attribute(TimedeltaIndexType, 'name')
@overload_attribute(RangeIndexType, 'name')
@overload_attribute(PeriodIndexType, 'name')
@overload_attribute(NumericIndexType, 'name')
@overload_attribute(IntervalIndexType, 'name')
@overload_attribute(CategoricalIndexType, 'name')
@overload_attribute(MultiIndexType, 'name')
def Index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_index_getitem(I, ind):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType)
        ) and isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, NumericIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_numeric_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))
    if isinstance(I, (StringIndexType, BinaryIndexType)):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_binary_str_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))


def array_type_to_index(arr_typ, name_typ=None):
    if arr_typ == bodo.string_array_type:
        return StringIndexType(name_typ)
    if arr_typ == bodo.binary_array_type:
        return BinaryIndexType(name_typ)
    assert isinstance(arr_typ, (types.Array, IntegerArrayType, bodo.
        CategoricalArrayType)) or arr_typ in (bodo.datetime_date_array_type,
        bodo.boolean_array
        ), f'Converting array type {arr_typ} to index not supported'
    if (arr_typ == bodo.datetime_date_array_type or arr_typ.dtype == types.
        NPDatetime('ns')):
        return DatetimeIndexType(name_typ)
    if isinstance(arr_typ, bodo.CategoricalArrayType):
        return CategoricalIndexType(arr_typ, name_typ)
    if arr_typ.dtype == types.NPTimedelta('ns'):
        return TimedeltaIndexType(name_typ)
    if isinstance(arr_typ.dtype, (types.Integer, types.Float, types.Boolean)):
        return NumericIndexType(arr_typ.dtype, name_typ, arr_typ)
    raise BodoError(f'invalid index type {arr_typ}')


def is_pd_index_type(t):
    return isinstance(t, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType,
        PeriodIndexType, StringIndexType, BinaryIndexType, RangeIndexType,
        HeterogeneousIndexType))


@overload_method(RangeIndexType, 'take', no_unliteral=True)
@overload_method(NumericIndexType, 'take', no_unliteral=True)
@overload_method(StringIndexType, 'take', no_unliteral=True)
@overload_method(BinaryIndexType, 'take', no_unliteral=True)
@overload_method(CategoricalIndexType, 'take', no_unliteral=True)
@overload_method(PeriodIndexType, 'take', no_unliteral=True)
@overload_method(DatetimeIndexType, 'take', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'take', no_unliteral=True)
def overload_index_take(I, indices, axis=0, allow_fill=True, fill_value=None):
    lrz__cta = dict(axis=axis, allow_fill=allow_fill, fill_value=fill_value)
    gwlux__hyn = dict(axis=0, allow_fill=True, fill_value=None)
    check_unsupported_args('Index.take', lrz__cta, gwlux__hyn, package_name
        ='pandas', module_name='Index')
    return lambda I, indices: I[indices]


@numba.njit(no_cpython_wrapper=True)
def _init_engine(I):
    if len(I) > 0 and not I._dict:
        zggg__rdkrr = bodo.utils.conversion.coerce_to_array(I)
        for i in range(len(zggg__rdkrr)):
            val = zggg__rdkrr[i]
            if val in I._dict:
                raise ValueError(
                    'Index.get_loc(): non-unique Index not supported yet')
            I._dict[val] = i


@overload(operator.contains, no_unliteral=True)
def index_contains(I, val):
    if not is_index_type(I):
        return
    if isinstance(I, RangeIndexType):
        return lambda I, val: range_contains(I.start, I.stop, I.step, val)

    def impl(I, val):
        key = bodo.utils.conversion.unbox_if_timestamp(val)
        if not is_null_value(I._dict):
            _init_engine(I)
            return key in I._dict
        else:
            woisj__tuso = (
                'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                )
            warnings.warn(woisj__tuso)
            zggg__rdkrr = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(zggg__rdkrr)):
                if zggg__rdkrr[i] == key:
                    if ind != -1:
                        raise ValueError(
                            'Index.get_loc(): non-unique Index not supported yet'
                            )
                    ind = i
        return ind != -1
    return impl


@register_jitable
def range_contains(start, stop, step, val):
    if step > 0 and not start <= val < stop:
        return False
    if step < 0 and not stop <= val < start:
        return False
    return (val - start) % step == 0


@overload_method(RangeIndexType, 'get_loc', no_unliteral=True)
@overload_method(NumericIndexType, 'get_loc', no_unliteral=True)
@overload_method(StringIndexType, 'get_loc', no_unliteral=True)
@overload_method(BinaryIndexType, 'get_loc', no_unliteral=True)
@overload_method(PeriodIndexType, 'get_loc', no_unliteral=True)
@overload_method(DatetimeIndexType, 'get_loc', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'get_loc', no_unliteral=True)
def overload_index_get_loc(I, key, method=None, tolerance=None):
    lrz__cta = dict(method=method, tolerance=tolerance)
    unip__jwg = dict(method=None, tolerance=None)
    check_unsupported_args('Index.get_loc', lrz__cta, unip__jwg,
        package_name='pandas', module_name='Index')
    key = types.unliteral(key)
    if key == pd_timestamp_type:
        key = bodo.datetime64ns
    if key == pd_timedelta_type:
        key = bodo.timedelta64ns
    if key != I.dtype:
        raise_bodo_error(
            'Index.get_loc(): invalid label type in Index.get_loc()')
    if isinstance(I, RangeIndexType):

        def impl_range(I, key, method=None, tolerance=None):
            if not range_contains(I.start, I.stop, I.step, key):
                raise KeyError('Index.get_loc(): key not found')
            return key - I.start if I.step == 1 else (key - I.start) // I.step
        return impl_range

    def impl(I, key, method=None, tolerance=None):
        key = bodo.utils.conversion.unbox_if_timestamp(key)
        if not is_null_value(I._dict):
            _init_engine(I)
            ind = I._dict.get(key, -1)
        else:
            woisj__tuso = (
                'Index.get_loc() can be slow for global Index objects (pass as argument to JIT function for better performance).'
                )
            warnings.warn(woisj__tuso)
            zggg__rdkrr = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(zggg__rdkrr)):
                if zggg__rdkrr[i] == key:
                    if ind != -1:
                        raise ValueError(
                            'Index.get_loc(): non-unique Index not supported yet'
                            )
                    ind = i
        if ind == -1:
            raise KeyError('Index.get_loc(): key not found')
        return ind
    return impl


def create_isna_specific_method(overload_name):

    def overload_index_isna_specific_method(I):
        jpvzo__jfk = overload_name in {'isna', 'isnull'}
        if isinstance(I, RangeIndexType):

            def impl(I):
                numba.parfors.parfor.init_prange()
                ful__jwfl = len(I)
                dvfa__jgssn = np.empty(ful__jwfl, np.bool_)
                for i in numba.parfors.parfor.internal_prange(ful__jwfl):
                    dvfa__jgssn[i] = not jpvzo__jfk
                return dvfa__jgssn
            return impl
        ecwp__wldbc = f"""def impl(I):
    numba.parfors.parfor.init_prange()
    arr = bodo.hiframes.pd_index_ext.get_index_data(I)
    n = len(arr)
    out_arr = np.empty(n, np.bool_)
    for i in numba.parfors.parfor.internal_prange(n):
       out_arr[i] = {'' if jpvzo__jfk else 'not '}bodo.libs.array_kernels.isna(arr, i)
    return out_arr
"""
        yoez__yxw = {}
        exec(ecwp__wldbc, {'bodo': bodo, 'np': np, 'numba': numba}, yoez__yxw)
        impl = yoez__yxw['impl']
        return impl
    return overload_index_isna_specific_method


isna_overload_types = (RangeIndexType, NumericIndexType, StringIndexType,
    BinaryIndexType, CategoricalIndexType, PeriodIndexType,
    DatetimeIndexType, TimedeltaIndexType)
isna_specific_methods = 'isna', 'notna', 'isnull', 'notnull'


def _install_isna_specific_methods():
    for yvhc__jzjt in isna_overload_types:
        for overload_name in isna_specific_methods:
            overload_impl = create_isna_specific_method(overload_name)
            overload_method(yvhc__jzjt, overload_name, no_unliteral=True,
                inline='always')(overload_impl)


_install_isna_specific_methods()


@overload_attribute(RangeIndexType, 'values')
@overload_attribute(NumericIndexType, 'values')
@overload_attribute(StringIndexType, 'values')
@overload_attribute(BinaryIndexType, 'values')
@overload_attribute(CategoricalIndexType, 'values')
@overload_attribute(PeriodIndexType, 'values')
@overload_attribute(DatetimeIndexType, 'values')
@overload_attribute(TimedeltaIndexType, 'values')
def overload_values(I):
    return lambda I: bodo.utils.conversion.coerce_to_array(I)


@overload(len, no_unliteral=True)
def overload_index_len(I):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType,
        PeriodIndexType, IntervalIndexType, CategoricalIndexType,
        DatetimeIndexType, TimedeltaIndexType, HeterogeneousIndexType)):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I))


@overload_attribute(DatetimeIndexType, 'shape')
@overload_attribute(NumericIndexType, 'shape')
@overload_attribute(StringIndexType, 'shape')
@overload_attribute(BinaryIndexType, 'shape')
@overload_attribute(PeriodIndexType, 'shape')
@overload_attribute(TimedeltaIndexType, 'shape')
@overload_attribute(IntervalIndexType, 'shape')
@overload_attribute(CategoricalIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)),)


@overload_attribute(RangeIndexType, 'shape')
def overload_range_index_shape(s):
    return lambda s: (len(s),)


@overload_attribute(NumericIndexType, 'is_monotonic', inline='always')
@overload_attribute(RangeIndexType, 'is_monotonic', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic', inline='always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic', inline='always')
@overload_attribute(NumericIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_increasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_increasing', inline=
    'always')
def overload_index_is_montonic(I):
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            zggg__rdkrr = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(zggg__rdkrr, 1)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step > 0 or len(I) <= 1
        return impl


@overload_attribute(NumericIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_decreasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_decreasing', inline=
    'always')
def overload_index_is_montonic_decreasing(I):
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            zggg__rdkrr = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(zggg__rdkrr, 2)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step < 0 or len(I) <= 1
        return impl


@overload_method(RangeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(NumericIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(StringIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(BinaryIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(CategoricalIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(PeriodIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
def overload_index_drop_duplicates(I, keep='first'):
    lrz__cta = dict(keep=keep)
    unip__jwg = dict(keep='first')
    check_unsupported_args('Index.drop_duplicates', lrz__cta, unip__jwg,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):
        return lambda I, keep='first': I.copy()
    ecwp__wldbc = """def impl(I, keep='first'):
    data = bodo.hiframes.pd_index_ext.get_index_data(I)
    arr = bodo.libs.array_kernels.drop_duplicates_array(data)
    name = bodo.hiframes.pd_index_ext.get_index_name(I)
"""
    if isinstance(I, PeriodIndexType):
        ecwp__wldbc += f"""    return bodo.hiframes.pd_index_ext.init_period_index(arr, name, '{I.freq}')
"""
    else:
        ecwp__wldbc += (
            '    return bodo.utils.conversion.index_from_array(arr, name)')
    yoez__yxw = {}
    exec(ecwp__wldbc, {'bodo': bodo}, yoez__yxw)
    impl = yoez__yxw['impl']
    return impl


@numba.generated_jit(nopython=True)
def get_index_data(S):
    return lambda S: S._data


@numba.generated_jit(nopython=True)
def get_index_name(S):
    return lambda S: S._name


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_index_data',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_datetime_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_timedelta_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_numeric_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_binary_str_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_categorical_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func


def get_index_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    xeyi__nmhoe = args[0]
    if isinstance(self.typemap[xeyi__nmhoe.name], HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(xeyi__nmhoe):
        return ArrayAnalysis.AnalyzeResult(shape=xeyi__nmhoe, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_get_index_data
    ) = get_index_data_equiv


@overload_method(RangeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(NumericIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(StringIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(BinaryIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(CategoricalIndexType, 'map', inline='always', no_unliteral
    =True)
@overload_method(PeriodIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(DatetimeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'map', inline='always', no_unliteral=True)
def overload_index_map(I, mapper, na_action=None):
    if not is_const_func_type(mapper):
        raise BodoError("Index.map(): 'mapper' should be a function")
    dtype = I.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = pd_timestamp_type
    if dtype == types.NPTimedelta('ns'):
        dtype = pd_timedelta_type
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = dtype.elem_type
    pnwa__zvd = numba.core.registry.cpu_target.typing_context
    iyh__hkace = numba.core.registry.cpu_target.target_context
    try:
        pvxp__zqgr = get_const_func_output_type(mapper, (dtype,), {},
            pnwa__zvd, iyh__hkace)
    except Exception as asnf__sdgw:
        raise_bodo_error(get_udf_error_msg('Index.map()', asnf__sdgw))
    fcq__qiphj = get_udf_out_arr_type(pvxp__zqgr)
    func = get_overload_const_func(mapper, None)
    ecwp__wldbc = 'def f(I, mapper, na_action=None):\n'
    ecwp__wldbc += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    ecwp__wldbc += '  A = bodo.utils.conversion.coerce_to_array(I)\n'
    ecwp__wldbc += '  numba.parfors.parfor.init_prange()\n'
    ecwp__wldbc += '  n = len(A)\n'
    ecwp__wldbc += '  S = bodo.utils.utils.alloc_type(n, _arr_typ, (-1,))\n'
    ecwp__wldbc += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ecwp__wldbc += '    t2 = bodo.utils.conversion.box_if_dt64(A[i])\n'
    ecwp__wldbc += '    v = map_func(t2)\n'
    ecwp__wldbc += '    S[i] = bodo.utils.conversion.unbox_if_timestamp(v)\n'
    ecwp__wldbc += '  return bodo.utils.conversion.index_from_array(S, name)\n'
    krvvg__mpgb = bodo.compiler.udf_jit(func)
    yoez__yxw = {}
    exec(ecwp__wldbc, {'numba': numba, 'np': np, 'pd': pd, 'bodo': bodo,
        'map_func': krvvg__mpgb, '_arr_typ': fcq__qiphj,
        'init_nested_counts': bodo.utils.indexing.init_nested_counts,
        'add_nested_counts': bodo.utils.indexing.add_nested_counts,
        'data_arr_type': fcq__qiphj.dtype}, yoez__yxw)
    f = yoez__yxw['f']
    return f


@lower_builtin(operator.is_, NumericIndexType, NumericIndexType)
@lower_builtin(operator.is_, StringIndexType, StringIndexType)
@lower_builtin(operator.is_, BinaryIndexType, BinaryIndexType)
@lower_builtin(operator.is_, PeriodIndexType, PeriodIndexType)
@lower_builtin(operator.is_, DatetimeIndexType, DatetimeIndexType)
@lower_builtin(operator.is_, TimedeltaIndexType, TimedeltaIndexType)
@lower_builtin(operator.is_, IntervalIndexType, IntervalIndexType)
@lower_builtin(operator.is_, CategoricalIndexType, CategoricalIndexType)
def index_is(context, builder, sig, args):
    evt__evq, kdpc__mzk = sig.args
    if evt__evq != kdpc__mzk:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return a._data is b._data and a._name is b._name
    return context.compile_internal(builder, index_is_impl, sig, args)


@lower_builtin(operator.is_, RangeIndexType, RangeIndexType)
def range_index_is(context, builder, sig, args):
    evt__evq, kdpc__mzk = sig.args
    if evt__evq != kdpc__mzk:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._start == b._start and a._stop == b._stop and a._step ==
            b._step and a._name is b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)


def create_binary_op_overload(op):

    def overload_index_binary_op(lhs, rhs):
        if is_index_type(lhs):

            def impl(lhs, rhs):
                zggg__rdkrr = bodo.utils.conversion.coerce_to_array(lhs)
                swi__lcv = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                dvfa__jgssn = op(zggg__rdkrr, swi__lcv)
                return dvfa__jgssn
            return impl
        if is_index_type(rhs):

            def impl2(lhs, rhs):
                zggg__rdkrr = bodo.utils.conversion.coerce_to_array(rhs)
                swi__lcv = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                dvfa__jgssn = op(swi__lcv, zggg__rdkrr)
                return dvfa__jgssn
            return impl2
        if isinstance(lhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(lhs.data):

                def impl3(lhs, rhs):
                    data = bodo.utils.conversion.coerce_to_array(lhs)
                    zggg__rdkrr = bodo.utils.conversion.coerce_to_array(data)
                    swi__lcv = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    dvfa__jgssn = op(zggg__rdkrr, swi__lcv)
                    return dvfa__jgssn
                return impl3
            count = len(lhs.data.types)
            ecwp__wldbc = 'def f(lhs, rhs):\n'
            ecwp__wldbc += '  return [{}]\n'.format(','.join(
                'op(lhs[{}], rhs{})'.format(i, f'[{i}]' if is_iterable_type
                (rhs) else '') for i in range(count)))
            yoez__yxw = {}
            exec(ecwp__wldbc, {'op': op, 'np': np}, yoez__yxw)
            impl = yoez__yxw['f']
            return impl
        if isinstance(rhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(rhs.data):

                def impl4(lhs, rhs):
                    data = bodo.hiframes.pd_index_ext.get_index_data(rhs)
                    zggg__rdkrr = bodo.utils.conversion.coerce_to_array(data)
                    swi__lcv = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    dvfa__jgssn = op(swi__lcv, zggg__rdkrr)
                    return dvfa__jgssn
                return impl4
            count = len(rhs.data.types)
            ecwp__wldbc = 'def f(lhs, rhs):\n'
            ecwp__wldbc += '  return [{}]\n'.format(','.join(
                'op(lhs{}, rhs[{}])'.format(f'[{i}]' if is_iterable_type(
                lhs) else '', i) for i in range(count)))
            yoez__yxw = {}
            exec(ecwp__wldbc, {'op': op, 'np': np}, yoez__yxw)
            impl = yoez__yxw['f']
            return impl
    return overload_index_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        overload_impl = create_binary_op_overload(op)
        overload(op, inline='always')(overload_impl)


_install_binary_ops()


def is_index_type(t):
    return isinstance(t, (RangeIndexType, NumericIndexType, StringIndexType,
        BinaryIndexType, PeriodIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType))


@lower_cast(RangeIndexType, NumericIndexType)
def cast_range_index_to_int_index(context, builder, fromty, toty, val):
    f = lambda I: init_numeric_index(np.arange(I._start, I._stop, I._step),
        bodo.hiframes.pd_index_ext.get_index_name(I))
    return context.compile_internal(builder, f, toty(fromty), [val])


class HeterogeneousIndexType(types.Type):
    ndim = 1

    def __init__(self, data=None, name_type=None):
        self.data = data
        name_type = types.none if name_type is None else name_type
        self.name_type = name_type
        super(HeterogeneousIndexType, self).__init__(name=
            f'heter_index({data}, {name_type})')

    def copy(self):
        return HeterogeneousIndexType(self.data, self.name_type)

    @property
    def key(self):
        return self.data, self.name_type

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return 'object'


@register_model(HeterogeneousIndexType)
class HeterogeneousIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fnrg__wanxk = [('data', fe_type.data), ('name', fe_type.name_type)]
        super(HeterogeneousIndexModel, self).__init__(dmm, fe_type, fnrg__wanxk
            )


make_attribute_wrapper(HeterogeneousIndexType, 'data', '_data')
make_attribute_wrapper(HeterogeneousIndexType, 'name', '_name')


@overload_method(HeterogeneousIndexType, 'copy', no_unliteral=True)
def overload_heter_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    brsjr__dfpjg = idx_typ_to_format_str_map[HeterogeneousIndexType].format(
        'copy()')
    qmp__dcp = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', qmp__dcp, idx_cpy_arg_defaults,
        fn_str=brsjr__dfpjg, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(HeterogeneousIndexType)
def box_heter_index(typ, val, c):
    ojfd__vmg = c.context.insert_const_string(c.builder.module, 'pandas')
    igdqj__ibfsl = c.pyapi.import_module_noblock(ojfd__vmg)
    ubzoy__lgm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, ubzoy__lgm.data)
    zesyf__dzqs = c.pyapi.from_native_value(typ.data, ubzoy__lgm.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_type, ubzoy__lgm.name)
    cvck__hcmxt = c.pyapi.from_native_value(typ.name_type, ubzoy__lgm.name,
        c.env_manager)
    wcv__xjmuj = c.pyapi.make_none()
    yoyz__onahf = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    zpqdi__hiqhc = c.pyapi.call_method(igdqj__ibfsl, 'Index', (zesyf__dzqs,
        wcv__xjmuj, yoyz__onahf, cvck__hcmxt))
    c.pyapi.decref(zesyf__dzqs)
    c.pyapi.decref(wcv__xjmuj)
    c.pyapi.decref(yoyz__onahf)
    c.pyapi.decref(cvck__hcmxt)
    c.pyapi.decref(igdqj__ibfsl)
    c.context.nrt.decref(c.builder, typ, val)
    return zpqdi__hiqhc


@intrinsic
def init_heter_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        uvpl__yfd = signature.return_type
        ubzoy__lgm = cgutils.create_struct_proxy(uvpl__yfd)(context, builder)
        ubzoy__lgm.data = args[0]
        ubzoy__lgm.name = args[1]
        context.nrt.incref(builder, uvpl__yfd.data, args[0])
        context.nrt.incref(builder, uvpl__yfd.name_type, args[1])
        return ubzoy__lgm._getvalue()
    return HeterogeneousIndexType(data, name)(data, name), codegen


@overload_attribute(HeterogeneousIndexType, 'name')
def heter_index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload_attribute(NumericIndexType, 'nbytes')
@overload_attribute(DatetimeIndexType, 'nbytes')
@overload_attribute(TimedeltaIndexType, 'nbytes')
@overload_attribute(RangeIndexType, 'nbytes')
@overload_attribute(StringIndexType, 'nbytes')
@overload_attribute(BinaryIndexType, 'nbytes')
@overload_attribute(CategoricalIndexType, 'nbytes')
@overload_attribute(PeriodIndexType, 'nbytes')
def overload_nbytes(I):
    if isinstance(I, RangeIndexType):

        def _impl_nbytes(I):
            return bodo.io.np_io.get_dtype_size(type(I._start)
                ) + bodo.io.np_io.get_dtype_size(type(I._step)
                ) + bodo.io.np_io.get_dtype_size(type(I._stop))
        return _impl_nbytes
    else:

        def _impl_nbytes(I):
            return I._data.nbytes
        return _impl_nbytes


@overload_method(NumericIndexType, 'rename', inline='always')
@overload_method(DatetimeIndexType, 'rename', inline='always')
@overload_method(TimedeltaIndexType, 'rename', inline='always')
@overload_method(RangeIndexType, 'rename', inline='always')
@overload_method(StringIndexType, 'rename', inline='always')
@overload_method(BinaryIndexType, 'rename', inline='always')
@overload_method(CategoricalIndexType, 'rename', inline='always')
@overload_method(PeriodIndexType, 'rename', inline='always')
@overload_method(IntervalIndexType, 'rename', inline='always')
@overload_method(HeterogeneousIndexType, 'rename', inline='always')
def overload_rename(I, name, inplace=False):
    if is_overload_true(inplace):
        raise BodoError('Index.rename(): inplace index renaming unsupported')
    return init_index(I, name)


def init_index(I, name):
    fjoq__eno = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index}
    if type(I) in fjoq__eno:
        init_func = fjoq__eno[type(I)]
        return lambda I, name, inplace=False: init_func(I._data.copy(), name)
    if isinstance(I, RangeIndexType):
        return lambda I, name, inplace=False: I.copy(name=name)
    if isinstance(I, PeriodIndexType):
        freq = I.freq
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_period_index(I._data.copy(), name, freq))
    if isinstance(I, HeterogeneousIndexType):
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_heter_index(bodo.hiframes.pd_index_ext.get_index_data(I),
            name))
    raise TypeError(f'init_index(): Unknown type {type(I)}')


@overload(operator.getitem, no_unliteral=True)
def overload_heter_index_getitem(I, ind):
    if not isinstance(I, HeterogeneousIndexType):
        return
    if isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, HeterogeneousIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_heter_index(bodo
            .hiframes.pd_index_ext.get_index_data(I)[ind], bodo.hiframes.
            pd_index_ext.get_index_name(I))


@lower_constant(DatetimeIndexType)
@lower_constant(TimedeltaIndexType)
def lower_constant_time_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, types.Array(types.int64, 1,
        'C'), pyval.values.view(np.int64))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    nsqkl__pjmos = context.get_constant_null(types.DictType(dtype, types.int64)
        )
    return lir.Constant.literal_struct([data, name, nsqkl__pjmos])


@lower_constant(PeriodIndexType)
def lower_constant_period_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, bodo.IntegerArrayType(
        types.int64), pd.arrays.IntegerArray(pyval.asi8, pyval.isna()))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    nsqkl__pjmos = context.get_constant_null(types.DictType(types.int64,
        types.int64))
    return lir.Constant.literal_struct([data, name, nsqkl__pjmos])


@lower_constant(NumericIndexType)
def lower_constant_numeric_index(context, builder, ty, pyval):
    assert isinstance(ty.dtype, (types.Integer, types.Float, types.Boolean))
    data = context.get_constant_generic(builder, types.Array(ty.dtype, 1,
        'C'), pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    nsqkl__pjmos = context.get_constant_null(types.DictType(dtype, types.int64)
        )
    return lir.Constant.literal_struct([data, name, nsqkl__pjmos])


@lower_constant(StringIndexType)
@lower_constant(BinaryIndexType)
def lower_constant_binary_string_index(context, builder, ty, pyval):
    zboe__lyq = ty.data
    scalar_type = ty.data.dtype
    data = context.get_constant_generic(builder, zboe__lyq, pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    nsqkl__pjmos = context.get_constant_null(types.DictType(scalar_type,
        types.int64))
    return lir.Constant.literal_struct([data, name, nsqkl__pjmos])


@lower_builtin('getiter', RangeIndexType)
def getiter_range_index(context, builder, sig, args):
    [eggw__sacir] = sig.args
    [iifa__ndcz] = args
    xiot__mgwx = context.make_helper(builder, eggw__sacir, value=iifa__ndcz)
    zvs__aznw = context.make_helper(builder, sig.return_type)
    claab__oumus = cgutils.alloca_once_value(builder, xiot__mgwx.start)
    ysxop__fjp = context.get_constant(types.intp, 0)
    gknnq__onmrr = cgutils.alloca_once_value(builder, ysxop__fjp)
    zvs__aznw.iter = claab__oumus
    zvs__aznw.stop = xiot__mgwx.stop
    zvs__aznw.step = xiot__mgwx.step
    zvs__aznw.count = gknnq__onmrr
    jxhjh__kxrxo = builder.sub(xiot__mgwx.stop, xiot__mgwx.start)
    kggar__xmotc = context.get_constant(types.intp, 1)
    ewu__efqjy = builder.icmp(lc.ICMP_SGT, jxhjh__kxrxo, ysxop__fjp)
    hndep__tegz = builder.icmp(lc.ICMP_SGT, xiot__mgwx.step, ysxop__fjp)
    rbt__ypz = builder.not_(builder.xor(ewu__efqjy, hndep__tegz))
    with builder.if_then(rbt__ypz):
        aue__hbo = builder.srem(jxhjh__kxrxo, xiot__mgwx.step)
        aue__hbo = builder.select(ewu__efqjy, aue__hbo, builder.neg(aue__hbo))
        owsid__sbr = builder.icmp(lc.ICMP_SGT, aue__hbo, ysxop__fjp)
        pytd__ceo = builder.add(builder.sdiv(jxhjh__kxrxo, xiot__mgwx.step),
            builder.select(owsid__sbr, kggar__xmotc, ysxop__fjp))
        builder.store(pytd__ceo, gknnq__onmrr)
    mcfhl__tjdzk = zvs__aznw._getvalue()
    gvgft__plx = impl_ret_new_ref(context, builder, sig.return_type,
        mcfhl__tjdzk)
    return gvgft__plx


def getiter_index(context, builder, sig, args):
    [eggw__sacir] = sig.args
    [iifa__ndcz] = args
    xiot__mgwx = context.make_helper(builder, eggw__sacir, value=iifa__ndcz)
    return numba.np.arrayobj.getiter_array(context, builder, signature(sig.
        return_type, sig.args[0].data), (xiot__mgwx.data,))


def _install_index_getiter():
    index_types = [NumericIndexType, StringIndexType, BinaryIndexType,
        CategoricalIndexType, TimedeltaIndexType, DatetimeIndexType]
    for typ in index_types:
        lower_builtin('getiter', typ)(getiter_index)


_install_index_getiter()
index_unsupported_methods = ['all', 'any', 'append', 'argmax', 'argmin',
    'argsort', 'asof', 'asof_locs', 'astype', 'delete', 'difference',
    'drop', 'droplevel', 'dropna', 'duplicated', 'equals', 'factorize',
    'fillna', 'format', 'get_indexer', 'get_indexer_for',
    'get_indexer_non_unique', 'get_level_values', 'get_slice_bound',
    'get_value', 'groupby', 'holds_integer', 'identical', 'insert',
    'intersection', 'is_', 'is_boolean', 'is_categorical', 'is_floating',
    'is_integer', 'is_interval', 'is_mixed', 'is_numeric', 'is_object',
    'is_type_compatible', 'isin', 'item', 'join', 'memory_usage', 'nunique',
    'putmask', 'ravel', 'reindex', 'repeat', 'searchsorted', 'set_names',
    'set_value', 'shift', 'slice_indexer', 'slice_locs', 'sort',
    'sort_values', 'sortlevel', 'str', 'symmetric_difference',
    'to_flat_index', 'to_frame', 'to_list', 'to_native_types', 'to_numpy',
    'to_series', 'tolist', 'transpose', 'union', 'unique', 'value_counts',
    'view', 'where']
index_unsupported_atrs = ['T', 'array', 'asi8', 'dtype', 'has_duplicates',
    'hasnans', 'inferred_type', 'is_all_dates', 'is_unique', 'ndim',
    'nlevels', 'size', 'names', 'empty']
cat_idx_unsupported_atrs = ['codes', 'categories', 'ordered',
    'is_monotonic', 'is_monotonic_increasing', 'is_monotonic_decreasing']
cat_idx_unsupported_methods = ['rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered', 'get_loc']
interval_idx_unsupported_atrs = ['closed', 'is_empty',
    'is_non_overlapping_monotonic', 'is_overlapping', 'left', 'right',
    'mid', 'length', 'values', 'shape', 'nbytes', 'is_monotonic',
    'is_monotonic_increasing', 'is_monotonic_decreasing']
interval_idx_unsupported_methods = ['contains', 'copy', 'overlaps',
    'set_closed', 'to_tuples', 'take', 'get_loc', 'isna', 'isnull', 'map']
multi_index_unsupported_atrs = ['levshape', 'levels', 'codes', 'dtypes',
    'values', 'shape', 'nbytes', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
multi_index_unsupported_methods = ['copy', 'set_levels', 'set_codes',
    'swaplevel', 'reorder_levels', 'remove_unused_levels', 'get_loc',
    'get_locs', 'get_loc_level', 'take', 'isna', 'isnull', 'map']
dt_index_unsupported_atrs = ['time', 'timez', 'tz', 'freq', 'freqstr',
    'inferred_freq']
dt_index_unsupported_methods = ['normalize', 'strftime', 'snap',
    'tz_convert', 'tz_localize', 'round', 'floor', 'ceil', 'to_period',
    'to_perioddelta', 'to_pydatetime', 'month_name', 'day_name', 'mean',
    'indexer_at_time', 'indexer_between', 'indexer_between_time']
td_index_unsupported_atrs = ['components', 'inferred_freq']
td_index_unsupported_methods = ['to_pydatetime', 'round', 'floor', 'ceil',
    'mean']
period_index_unsupported_atrs = ['day', 'dayofweek', 'day_of_week',
    'dayofyear', 'day_of_year', 'days_in_month', 'daysinmonth', 'freq',
    'freqstr', 'hour', 'is_leap_year', 'minute', 'month', 'quarter',
    'second', 'week', 'weekday', 'weekofyear', 'year', 'end_time', 'qyear',
    'start_time', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
string_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
binary_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
period_index_unsupported_methods = ['asfreq', 'strftime', 'to_timestamp']
index_types = [('pandas.RangeIndex.{}', RangeIndexType), (
    'pandas.Index.{} with numeric data', NumericIndexType), (
    'pandas.Index.{} with string data', StringIndexType), (
    'pandas.Index.{} with binary data', BinaryIndexType), (
    'pandas.TimedeltaIndex.{}', TimedeltaIndexType), (
    'pandas.IntervalIndex.{}', IntervalIndexType), (
    'pandas.CategoricalIndex.{}', CategoricalIndexType), (
    'pandas.PeriodIndex.{}', PeriodIndexType), ('pandas.DatetimeIndex.{}',
    DatetimeIndexType), ('pandas.MultiIndex.{}', MultiIndexType)]
for name, typ in index_types:
    idx_typ_to_format_str_map[typ] = name


def _install_index_unsupported():
    for aza__evrf in index_unsupported_methods:
        for zerqa__jwuy, typ in index_types:
            overload_method(typ, aza__evrf, no_unliteral=True)(
                create_unsupported_overload(zerqa__jwuy.format(aza__evrf +
                '()')))
    for hiy__yod in index_unsupported_atrs:
        for zerqa__jwuy, typ in index_types:
            overload_attribute(typ, hiy__yod, no_unliteral=True)(
                create_unsupported_overload(zerqa__jwuy.format(hiy__yod)))
    zjvs__mgzm = [(StringIndexType, string_index_unsupported_atrs), (
        BinaryIndexType, binary_index_unsupported_atrs), (
        CategoricalIndexType, cat_idx_unsupported_atrs), (IntervalIndexType,
        interval_idx_unsupported_atrs), (MultiIndexType,
        multi_index_unsupported_atrs), (DatetimeIndexType,
        dt_index_unsupported_atrs), (TimedeltaIndexType,
        td_index_unsupported_atrs), (PeriodIndexType,
        period_index_unsupported_atrs)]
    xpo__equq = [(CategoricalIndexType, cat_idx_unsupported_methods), (
        IntervalIndexType, interval_idx_unsupported_methods), (
        MultiIndexType, multi_index_unsupported_methods), (
        DatetimeIndexType, dt_index_unsupported_methods), (
        TimedeltaIndexType, td_index_unsupported_methods), (PeriodIndexType,
        period_index_unsupported_methods)]
    for typ, pdylq__poj in xpo__equq:
        zerqa__jwuy = idx_typ_to_format_str_map[typ]
        for lalv__vkt in pdylq__poj:
            overload_method(typ, lalv__vkt, no_unliteral=True)(
                create_unsupported_overload(zerqa__jwuy.format(lalv__vkt +
                '()')))
    for typ, klm__xsxel in zjvs__mgzm:
        zerqa__jwuy = idx_typ_to_format_str_map[typ]
        for hiy__yod in klm__xsxel:
            overload_attribute(typ, hiy__yod, no_unliteral=True)(
                create_unsupported_overload(zerqa__jwuy.format(hiy__yod)))
    for zzo__eywdd in [RangeIndexType, NumericIndexType, StringIndexType,
        BinaryIndexType, IntervalIndexType, CategoricalIndexType,
        PeriodIndexType, MultiIndexType]:
        for lalv__vkt in ['max', 'min']:
            zerqa__jwuy = idx_typ_to_format_str_map[zzo__eywdd]
            overload_method(zzo__eywdd, lalv__vkt, no_unliteral=True)(
                create_unsupported_overload(zerqa__jwuy.format(lalv__vkt +
                '()')))


_install_index_unsupported()
