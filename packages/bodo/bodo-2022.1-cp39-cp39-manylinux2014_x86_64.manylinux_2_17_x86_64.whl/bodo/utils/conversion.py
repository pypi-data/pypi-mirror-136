"""
Utility functions for conversion of data such as list to array.
Need to be inlined for better optimization.
"""
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.extending import overload
import bodo
from bodo.libs.binary_arr_ext import bytes_type
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, dtype_to_array_type, get_overload_const_list, get_overload_const_str, is_heterogeneous_tuple_type, is_np_arr_typ, is_overload_constant_list, is_overload_constant_str, is_overload_none, is_overload_true, to_nullable_type
NS_DTYPE = np.dtype('M8[ns]')
TD_DTYPE = np.dtype('m8[ns]')


def coerce_to_ndarray(data, error_on_nonarray=True, use_nullable_array=None,
    scalar_to_arr_len=None):
    return data


@overload(coerce_to_ndarray)
def overload_coerce_to_ndarray(data, error_on_nonarray=True,
    use_nullable_array=None, scalar_to_arr_len=None):
    from bodo.hiframes.pd_index_ext import DatetimeIndexType, NumericIndexType, RangeIndexType, TimedeltaIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    data = types.unliteral(data)
    if isinstance(data, types.Optional) and bodo.utils.typing.is_scalar_type(
        data.type):
        data = data.type
        use_nullable_array = True
    if isinstance(data, bodo.libs.int_arr_ext.IntegerArrayType
        ) and not is_overload_none(use_nullable_array):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.int_arr_ext.
            get_int_arr_data(data))
    if data == bodo.libs.bool_arr_ext.boolean_array and not is_overload_none(
        use_nullable_array):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.bool_arr_ext.
            get_bool_arr_data(data))
    if isinstance(data, types.Array):
        if not is_overload_none(use_nullable_array) and isinstance(data.
            dtype, (types.Boolean, types.Integer)):
            if data.dtype == types.bool_:
                if data.layout != 'C':
                    return (lambda data, error_on_nonarray=True,
                        use_nullable_array=None, scalar_to_arr_len=None:
                        bodo.libs.bool_arr_ext.init_bool_array(np.
                        ascontiguousarray(data), np.full(len(data) + 7 >> 3,
                        255, np.uint8)))
                else:
                    return (lambda data, error_on_nonarray=True,
                        use_nullable_array=None, scalar_to_arr_len=None:
                        bodo.libs.bool_arr_ext.init_bool_array(data, np.
                        full(len(data) + 7 >> 3, 255, np.uint8)))
            elif data.layout != 'C':
                return (lambda data, error_on_nonarray=True,
                    use_nullable_array=None, scalar_to_arr_len=None: bodo.
                    libs.int_arr_ext.init_integer_array(np.
                    ascontiguousarray(data), np.full(len(data) + 7 >> 3, 
                    255, np.uint8)))
            else:
                return (lambda data, error_on_nonarray=True,
                    use_nullable_array=None, scalar_to_arr_len=None: bodo.
                    libs.int_arr_ext.init_integer_array(data, np.full(len(
                    data) + 7 >> 3, 255, np.uint8)))
        if data.layout != 'C':
            return (lambda data, error_on_nonarray=True, use_nullable_array
                =None, scalar_to_arr_len=None: np.ascontiguousarray(data))
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if isinstance(data, (types.List, types.UniTuple)):
        ixzqr__ceqok = data.dtype
        if isinstance(ixzqr__ceqok, types.Optional):
            ixzqr__ceqok = ixzqr__ceqok.type
            if bodo.utils.typing.is_scalar_type(ixzqr__ceqok):
                use_nullable_array = True
        if isinstance(ixzqr__ceqok, (types.Boolean, types.Integer,
            Decimal128Type)) or ixzqr__ceqok in [bodo.hiframes.
            pd_timestamp_ext.pd_timestamp_type, bodo.hiframes.
            datetime_date_ext.datetime_date_type, bodo.hiframes.
            datetime_timedelta_ext.datetime_timedelta_type]:
            gea__cuo = dtype_to_array_type(ixzqr__ceqok)
            if not is_overload_none(use_nullable_array):
                gea__cuo = to_nullable_type(gea__cuo)

            def impl(data, error_on_nonarray=True, use_nullable_array=None,
                scalar_to_arr_len=None):
                hahmz__bxb = len(data)
                A = bodo.utils.utils.alloc_type(hahmz__bxb, gea__cuo, (-1,))
                bodo.utils.utils.tuple_list_to_array(A, data, ixzqr__ceqok)
                return A
            return impl
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.asarray(data))
    if isinstance(data, SeriesType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_series_ext.
            get_series_data(data))
    if isinstance(data, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_index_ext.
            get_index_data(data))
    if isinstance(data, RangeIndexType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.arange(data._start, data._stop,
            data._step))
    if isinstance(data, types.RangeType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.arange(data.start, data.stop,
            data.step))
    if not is_overload_none(scalar_to_arr_len):
        if isinstance(data, Decimal128Type):
            phdrk__brah = data.precision
            sufre__rwu = data.scale

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                hahmz__bxb = scalar_to_arr_len
                A = bodo.libs.decimal_arr_ext.alloc_decimal_array(hahmz__bxb,
                    phdrk__brah, sufre__rwu)
                for vmjp__pxqmr in numba.parfors.parfor.internal_prange(
                    hahmz__bxb):
                    A[vmjp__pxqmr] = data
                return A
            return impl_ts
        if data == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:
            larh__kud = np.dtype('datetime64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                hahmz__bxb = scalar_to_arr_len
                A = np.empty(hahmz__bxb, larh__kud)
                bsj__tsq = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(data))
                mpm__tqf = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    bsj__tsq)
                for vmjp__pxqmr in numba.parfors.parfor.internal_prange(
                    hahmz__bxb):
                    A[vmjp__pxqmr] = mpm__tqf
                return A
            return impl_ts
        if (data == bodo.hiframes.datetime_timedelta_ext.
            datetime_timedelta_type):
            jmpi__utra = np.dtype('timedelta64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                hahmz__bxb = scalar_to_arr_len
                A = np.empty(hahmz__bxb, jmpi__utra)
                vgwb__zijlj = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(data))
                for vmjp__pxqmr in numba.parfors.parfor.internal_prange(
                    hahmz__bxb):
                    A[vmjp__pxqmr] = vgwb__zijlj
                return A
            return impl_ts
        if data == bodo.hiframes.datetime_date_ext.datetime_date_type:

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                hahmz__bxb = scalar_to_arr_len
                A = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
                    hahmz__bxb)
                for vmjp__pxqmr in numba.parfors.parfor.internal_prange(
                    hahmz__bxb):
                    A[vmjp__pxqmr] = data
                return A
            return impl_ts
        if data == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            larh__kud = np.dtype('datetime64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                hahmz__bxb = scalar_to_arr_len
                A = np.empty(scalar_to_arr_len, larh__kud)
                bsj__tsq = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(data
                    .value)
                for vmjp__pxqmr in numba.parfors.parfor.internal_prange(
                    hahmz__bxb):
                    A[vmjp__pxqmr] = bsj__tsq
                return A
            return impl_ts
        dtype = types.unliteral(data)
        if not is_overload_none(use_nullable_array) and isinstance(dtype,
            types.Integer):

            def impl_null_integer(data, error_on_nonarray=True,
                use_nullable_array=None, scalar_to_arr_len=None):
                numba.parfors.parfor.init_prange()
                hahmz__bxb = scalar_to_arr_len
                dmenl__nwkpr = bodo.libs.int_arr_ext.alloc_int_array(hahmz__bxb
                    , dtype)
                for vmjp__pxqmr in numba.parfors.parfor.internal_prange(
                    hahmz__bxb):
                    dmenl__nwkpr[vmjp__pxqmr] = data
                return dmenl__nwkpr
            return impl_null_integer
        if not is_overload_none(use_nullable_array) and dtype == types.bool_:

            def impl_null_bool(data, error_on_nonarray=True,
                use_nullable_array=None, scalar_to_arr_len=None):
                numba.parfors.parfor.init_prange()
                hahmz__bxb = scalar_to_arr_len
                dmenl__nwkpr = bodo.libs.bool_arr_ext.alloc_bool_array(
                    hahmz__bxb)
                for vmjp__pxqmr in numba.parfors.parfor.internal_prange(
                    hahmz__bxb):
                    dmenl__nwkpr[vmjp__pxqmr] = data
                return dmenl__nwkpr
            return impl_null_bool

        def impl_num(data, error_on_nonarray=True, use_nullable_array=None,
            scalar_to_arr_len=None):
            numba.parfors.parfor.init_prange()
            hahmz__bxb = scalar_to_arr_len
            dmenl__nwkpr = np.empty(hahmz__bxb, dtype)
            for vmjp__pxqmr in numba.parfors.parfor.internal_prange(hahmz__bxb
                ):
                dmenl__nwkpr[vmjp__pxqmr] = data
            return dmenl__nwkpr
        return impl_num
    if isinstance(data, types.BaseTuple) and all(isinstance(atj__xqt, (
        types.Float, types.Integer)) for atj__xqt in data.types):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.array(data))
    if bodo.utils.utils.is_array_typ(data, False):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if is_overload_true(error_on_nonarray):
        raise BodoError(f'cannot coerce {data} to array')
    return (lambda data, error_on_nonarray=True, use_nullable_array=None,
        scalar_to_arr_len=None: data)


def coerce_to_array(data, error_on_nonarray=True, use_nullable_array=None,
    scalar_to_arr_len=None):
    return data


@overload(coerce_to_array, no_unliteral=True)
def overload_coerce_to_array(data, error_on_nonarray=True,
    use_nullable_array=None, scalar_to_arr_len=None):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, StringIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    data = types.unliteral(data)
    if isinstance(data, types.Optional) and bodo.utils.typing.is_scalar_type(
        data.type):
        data = data.type
        use_nullable_array = True
    if isinstance(data, SeriesType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_series_ext.
            get_series_data(data))
    if isinstance(data, (StringIndexType, BinaryIndexType,
        CategoricalIndexType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_index_ext.
            get_index_data(data))
    if isinstance(data, types.List) and data.dtype in (bodo.string_type,
        bodo.bytes_type):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            str_arr_from_sequence(data))
    if isinstance(data, types.BaseTuple) and data.count == 0:
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            empty_str_arr(data))
    if isinstance(data, types.UniTuple) and isinstance(data.dtype, (types.
        UnicodeType, types.StringLiteral)) or isinstance(data, types.BaseTuple
        ) and all(isinstance(atj__xqt, types.StringLiteral) for atj__xqt in
        data.types):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            str_arr_from_sequence(data))
    if data in (bodo.string_array_type, bodo.binary_array_type, bodo.libs.
        bool_arr_ext.boolean_array, bodo.hiframes.datetime_date_ext.
        datetime_date_array_type, bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type, bodo.hiframes.split_impl.
        string_array_split_view_type) or isinstance(data, (bodo.libs.
        int_arr_ext.IntegerArrayType, DecimalArrayType, bodo.libs.
        interval_arr_ext.IntervalArrayType, bodo.libs.tuple_arr_ext.
        TupleArrayType, bodo.libs.struct_arr_ext.StructArrayType, bodo.
        hiframes.pd_categorical_ext.CategoricalArrayType, bodo.libs.
        csr_matrix_ext.CSRMatrixType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if isinstance(data, (types.List, types.UniTuple)) and isinstance(data.
        dtype, types.BaseTuple):
        atapf__arlhd = tuple(dtype_to_array_type(atj__xqt) for atj__xqt in
            data.dtype.types)

        def impl_tuple_list(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            hahmz__bxb = len(data)
            arr = bodo.libs.tuple_arr_ext.pre_alloc_tuple_array(hahmz__bxb,
                (-1,), atapf__arlhd)
            for vmjp__pxqmr in range(hahmz__bxb):
                arr[vmjp__pxqmr] = data[vmjp__pxqmr]
            return arr
        return impl_tuple_list
    if isinstance(data, types.List) and (bodo.utils.utils.is_array_typ(data
        .dtype, False) or isinstance(data.dtype, types.List)):
        lntlv__kkel = dtype_to_array_type(data.dtype.dtype)

        def impl_array_item_arr(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            hahmz__bxb = len(data)
            swf__gkfo = init_nested_counts(lntlv__kkel)
            for vmjp__pxqmr in range(hahmz__bxb):
                ukwp__womyt = bodo.utils.conversion.coerce_to_array(data[
                    vmjp__pxqmr], use_nullable_array=True)
                swf__gkfo = add_nested_counts(swf__gkfo, ukwp__womyt)
            dmenl__nwkpr = (bodo.libs.array_item_arr_ext.
                pre_alloc_array_item_array(hahmz__bxb, swf__gkfo, lntlv__kkel))
            ebnlu__zcezb = bodo.libs.array_item_arr_ext.get_null_bitmap(
                dmenl__nwkpr)
            for ciap__xtlk in range(hahmz__bxb):
                ukwp__womyt = bodo.utils.conversion.coerce_to_array(data[
                    ciap__xtlk], use_nullable_array=True)
                dmenl__nwkpr[ciap__xtlk] = ukwp__womyt
                bodo.libs.int_arr_ext.set_bit_to_arr(ebnlu__zcezb,
                    ciap__xtlk, 1)
            return dmenl__nwkpr
        return impl_array_item_arr
    if not is_overload_none(scalar_to_arr_len) and isinstance(data, (types.
        UnicodeType, types.StringLiteral)):

        def impl_str(data, error_on_nonarray=True, use_nullable_array=None,
            scalar_to_arr_len=None):
            hahmz__bxb = scalar_to_arr_len
            A = bodo.libs.str_arr_ext.pre_alloc_string_array(hahmz__bxb, -1)
            for vmjp__pxqmr in numba.parfors.parfor.internal_prange(hahmz__bxb
                ):
                A[vmjp__pxqmr] = data
            return A
        return impl_str
    if isinstance(data, types.List) and data.dtype == bodo.pd_timestamp_type:

        def impl_list_timestamp(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            hahmz__bxb = len(data)
            A = np.empty(hahmz__bxb, np.dtype('datetime64[ns]'))
            for vmjp__pxqmr in range(hahmz__bxb):
                A[vmjp__pxqmr
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(data
                    [vmjp__pxqmr].value)
            return A
        return impl_list_timestamp
    if isinstance(data, types.List) and data.dtype == bodo.pd_timedelta_type:

        def impl_list_timedelta(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            hahmz__bxb = len(data)
            A = np.empty(hahmz__bxb, np.dtype('timedelta64[ns]'))
            for vmjp__pxqmr in range(hahmz__bxb):
                A[vmjp__pxqmr
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    data[vmjp__pxqmr].value)
            return A
        return impl_list_timedelta
    if not is_overload_none(scalar_to_arr_len) and data in [bodo.
        pd_timestamp_type, bodo.pd_timedelta_type]:
        dcjpb__ibntq = ('datetime64[ns]' if data == bodo.pd_timestamp_type else
            'timedelta64[ns]')

        def impl_timestamp(data, error_on_nonarray=True, use_nullable_array
            =None, scalar_to_arr_len=None):
            hahmz__bxb = scalar_to_arr_len
            A = np.empty(hahmz__bxb, dcjpb__ibntq)
            data = bodo.utils.conversion.unbox_if_timestamp(data)
            for vmjp__pxqmr in numba.parfors.parfor.internal_prange(hahmz__bxb
                ):
                A[vmjp__pxqmr] = data
            return A
        return impl_timestamp
    return (lambda data, error_on_nonarray=True, use_nullable_array=None,
        scalar_to_arr_len=None: bodo.utils.conversion.coerce_to_ndarray(
        data, error_on_nonarray, use_nullable_array, scalar_to_arr_len))


def _is_str_dtype(dtype):
    return isinstance(dtype, bodo.libs.str_arr_ext.StringDtype) or isinstance(
        dtype, types.Function) and dtype.key[0
        ] == str or is_overload_constant_str(dtype) and get_overload_const_str(
        dtype) == 'str'


def fix_arr_dtype(data, new_dtype, copy=None, nan_to_str=True, from_series=
    False):
    return data


@overload(fix_arr_dtype, no_unliteral=True)
def overload_fix_arr_dtype(data, new_dtype, copy=None, nan_to_str=True,
    from_series=False):
    nbhq__szrxj = is_overload_true(copy)
    if is_overload_none(new_dtype):
        if nbhq__szrxj:
            return (lambda data, new_dtype, copy=None, nan_to_str=True,
                from_series=False: data.copy())
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data)
    if _is_str_dtype(new_dtype):
        if isinstance(data.dtype, types.Integer):

            def impl_int_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                hahmz__bxb = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(hahmz__bxb, -1
                    )
                for evy__xqf in numba.parfors.parfor.internal_prange(hahmz__bxb
                    ):
                    if bodo.libs.array_kernels.isna(data, evy__xqf):
                        if nan_to_str:
                            bodo.libs.str_arr_ext.str_arr_setitem_NA_str(A,
                                evy__xqf)
                        else:
                            bodo.libs.array_kernels.setna(A, evy__xqf)
                    else:
                        bodo.libs.str_arr_ext.str_arr_setitem_int_to_str(A,
                            evy__xqf, data[evy__xqf])
                return A
            return impl_int_str
        if data.dtype == bytes_type:

            def impl_binary(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                hahmz__bxb = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(hahmz__bxb, -1
                    )
                for evy__xqf in numba.parfors.parfor.internal_prange(hahmz__bxb
                    ):
                    if bodo.libs.array_kernels.isna(data, evy__xqf):
                        bodo.libs.array_kernels.setna(A, evy__xqf)
                    else:
                        A[evy__xqf] = ''.join([chr(vmta__ylr) for vmta__ylr in
                            data[evy__xqf]])
                return A
            return impl_binary
        if is_overload_true(from_series) and data.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns):

            def impl_str_dt_series(data, new_dtype, copy=None, nan_to_str=
                True, from_series=False):
                numba.parfors.parfor.init_prange()
                hahmz__bxb = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(hahmz__bxb, -1
                    )
                for evy__xqf in numba.parfors.parfor.internal_prange(hahmz__bxb
                    ):
                    if bodo.libs.array_kernels.isna(data, evy__xqf):
                        if nan_to_str:
                            A[evy__xqf] = 'NaT'
                        else:
                            bodo.libs.array_kernels.setna(A, evy__xqf)
                        continue
                    A[evy__xqf] = str(box_if_dt64(data[evy__xqf]))
                return A
            return impl_str_dt_series
        else:

            def impl_str_array(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                hahmz__bxb = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(hahmz__bxb, -1
                    )
                for evy__xqf in numba.parfors.parfor.internal_prange(hahmz__bxb
                    ):
                    if bodo.libs.array_kernels.isna(data, evy__xqf):
                        if nan_to_str:
                            A[evy__xqf] = 'nan'
                        else:
                            bodo.libs.array_kernels.setna(A, evy__xqf)
                        continue
                    A[evy__xqf] = str(data[evy__xqf])
                return A
            return impl_str_array
    if isinstance(new_dtype, bodo.hiframes.pd_categorical_ext.
        PDCategoricalDtype):

        def impl_cat_dtype(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            hahmz__bxb = len(data)
            numba.parfors.parfor.init_prange()
            cehdn__tfi = (bodo.hiframes.pd_categorical_ext.
                get_label_dict_from_categories(new_dtype.categories.values))
            A = bodo.hiframes.pd_categorical_ext.alloc_categorical_array(
                hahmz__bxb, new_dtype)
            tnctu__irxol = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A))
            for vmjp__pxqmr in numba.parfors.parfor.internal_prange(hahmz__bxb
                ):
                if bodo.libs.array_kernels.isna(data, vmjp__pxqmr):
                    bodo.libs.array_kernels.setna(A, vmjp__pxqmr)
                    continue
                val = data[vmjp__pxqmr]
                if val not in cehdn__tfi:
                    bodo.libs.array_kernels.setna(A, vmjp__pxqmr)
                    continue
                tnctu__irxol[vmjp__pxqmr] = cehdn__tfi[val]
            return A
        return impl_cat_dtype
    if is_overload_constant_str(new_dtype) and get_overload_const_str(new_dtype
        ) == 'category':

        def impl_category(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            nvk__eogiz = bodo.libs.array_kernels.unique(data, dropna=True)
            nvk__eogiz = pd.Series(nvk__eogiz).sort_values().values
            nvk__eogiz = bodo.allgatherv(nvk__eogiz, False)
            fcn__zlewh = bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo
                .utils.conversion.index_from_array(nvk__eogiz, None), False,
                None, None)
            hahmz__bxb = len(data)
            numba.parfors.parfor.init_prange()
            cehdn__tfi = (bodo.hiframes.pd_categorical_ext.
                get_label_dict_from_categories_no_duplicates(nvk__eogiz))
            A = bodo.hiframes.pd_categorical_ext.alloc_categorical_array(
                hahmz__bxb, fcn__zlewh)
            tnctu__irxol = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A))
            for vmjp__pxqmr in numba.parfors.parfor.internal_prange(hahmz__bxb
                ):
                if bodo.libs.array_kernels.isna(data, vmjp__pxqmr):
                    bodo.libs.array_kernels.setna(A, vmjp__pxqmr)
                    continue
                val = data[vmjp__pxqmr]
                tnctu__irxol[vmjp__pxqmr] = cehdn__tfi[val]
            return A
        return impl_category
    nb_dtype = bodo.utils.typing.parse_dtype(new_dtype)
    if isinstance(data, bodo.libs.int_arr_ext.IntegerArrayType):
        btifj__vpo = isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype
            ) and data.dtype == nb_dtype.dtype
    else:
        btifj__vpo = data.dtype == nb_dtype
    if nbhq__szrxj and btifj__vpo:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data.copy())
    if btifj__vpo:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data)
    if isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype):
        if isinstance(nb_dtype, types.Integer):
            dcjpb__ibntq = nb_dtype
        else:
            dcjpb__ibntq = nb_dtype.dtype
        if isinstance(data.dtype, types.Float):

            def impl_float(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                hahmz__bxb = len(data)
                numba.parfors.parfor.init_prange()
                naex__alhzn = bodo.libs.int_arr_ext.alloc_int_array(hahmz__bxb,
                    dcjpb__ibntq)
                for vmjp__pxqmr in numba.parfors.parfor.internal_prange(
                    hahmz__bxb):
                    if bodo.libs.array_kernels.isna(data, vmjp__pxqmr):
                        bodo.libs.array_kernels.setna(naex__alhzn, vmjp__pxqmr)
                    else:
                        naex__alhzn[vmjp__pxqmr] = int(data[vmjp__pxqmr])
                return naex__alhzn
            return impl_float
        else:

            def impl(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                hahmz__bxb = len(data)
                numba.parfors.parfor.init_prange()
                naex__alhzn = bodo.libs.int_arr_ext.alloc_int_array(hahmz__bxb,
                    dcjpb__ibntq)
                for vmjp__pxqmr in numba.parfors.parfor.internal_prange(
                    hahmz__bxb):
                    if bodo.libs.array_kernels.isna(data, vmjp__pxqmr):
                        bodo.libs.array_kernels.setna(naex__alhzn, vmjp__pxqmr)
                    else:
                        naex__alhzn[vmjp__pxqmr] = np.int64(data[vmjp__pxqmr])
                return naex__alhzn
            return impl
    if isinstance(nb_dtype, types.Integer) and isinstance(data.dtype, types
        .Integer):

        def impl(data, new_dtype, copy=None, nan_to_str=True, from_series=False
            ):
            return data.astype(nb_dtype)
        return impl
    if nb_dtype == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            hahmz__bxb = len(data)
            numba.parfors.parfor.init_prange()
            naex__alhzn = bodo.libs.bool_arr_ext.alloc_bool_array(hahmz__bxb)
            for vmjp__pxqmr in numba.parfors.parfor.internal_prange(hahmz__bxb
                ):
                if bodo.libs.array_kernels.isna(data, vmjp__pxqmr):
                    bodo.libs.array_kernels.setna(naex__alhzn, vmjp__pxqmr)
                else:
                    naex__alhzn[vmjp__pxqmr] = bool(data[vmjp__pxqmr])
            return naex__alhzn
        return impl_bool
    if nb_dtype == bodo.datetime64ns:
        if data.dtype == bodo.string_type:

            def impl_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return bodo.hiframes.pd_timestamp_ext.series_str_dt64_astype(
                    data)
            return impl_str
        if data == bodo.datetime_date_array_type:

            def impl_date(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return (bodo.hiframes.pd_timestamp_ext.
                    datetime_date_arr_to_dt64_arr(data))
            return impl_date
        if isinstance(data.dtype, types.Number) or data.dtype in [bodo.
            timedelta64ns, types.bool_]:

            def impl_numeric(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                hahmz__bxb = len(data)
                numba.parfors.parfor.init_prange()
                dmenl__nwkpr = np.empty(hahmz__bxb, dtype=np.dtype(
                    'datetime64[ns]'))
                for vmjp__pxqmr in numba.parfors.parfor.internal_prange(
                    hahmz__bxb):
                    if bodo.libs.array_kernels.isna(data, vmjp__pxqmr):
                        bodo.libs.array_kernels.setna(dmenl__nwkpr, vmjp__pxqmr
                            )
                    else:
                        dmenl__nwkpr[vmjp__pxqmr
                            ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                            np.int64(data[vmjp__pxqmr]))
                return dmenl__nwkpr
            return impl_numeric
    if nb_dtype == bodo.timedelta64ns:
        if data.dtype == bodo.string_type:

            def impl_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return bodo.hiframes.pd_timestamp_ext.series_str_td64_astype(
                    data)
            return impl_str
        if isinstance(data.dtype, types.Number) or data.dtype in [bodo.
            datetime64ns, types.bool_]:
            if nbhq__szrxj:

                def impl_numeric(data, new_dtype, copy=None, nan_to_str=
                    True, from_series=False):
                    hahmz__bxb = len(data)
                    numba.parfors.parfor.init_prange()
                    dmenl__nwkpr = np.empty(hahmz__bxb, dtype=np.dtype(
                        'timedelta64[ns]'))
                    for vmjp__pxqmr in numba.parfors.parfor.internal_prange(
                        hahmz__bxb):
                        if bodo.libs.array_kernels.isna(data, vmjp__pxqmr):
                            bodo.libs.array_kernels.setna(dmenl__nwkpr,
                                vmjp__pxqmr)
                        else:
                            dmenl__nwkpr[vmjp__pxqmr] = (bodo.hiframes.
                                pd_timestamp_ext.integer_to_timedelta64(np.
                                int64(data[vmjp__pxqmr])))
                    return dmenl__nwkpr
                return impl_numeric
            else:
                return (lambda data, new_dtype, copy=None, nan_to_str=True,
                    from_series=False: data.view('int64'))
    if nb_dtype == types.int64 and data.dtype in [bodo.datetime64ns, bodo.
        timedelta64ns]:

        def impl_datelike_to_integer(data, new_dtype, copy=None, nan_to_str
            =True, from_series=False):
            hahmz__bxb = len(data)
            numba.parfors.parfor.init_prange()
            A = np.empty(hahmz__bxb, types.int64)
            for vmjp__pxqmr in numba.parfors.parfor.internal_prange(hahmz__bxb
                ):
                if bodo.libs.array_kernels.isna(data, vmjp__pxqmr):
                    bodo.libs.array_kernels.setna(A, vmjp__pxqmr)
                else:
                    A[vmjp__pxqmr] = np.int64(data[vmjp__pxqmr])
            return A
        return impl_datelike_to_integer
    if data.dtype != nb_dtype:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data.astype(nb_dtype))
    raise BodoError(f'Conversion from {data} to {new_dtype} not supported yet')


def array_type_from_dtype(dtype):
    return dtype_to_array_type(bodo.utils.typing.parse_dtype(dtype))


@overload(array_type_from_dtype)
def overload_array_type_from_dtype(dtype):
    arr_type = dtype_to_array_type(bodo.utils.typing.parse_dtype(dtype))
    return lambda dtype: arr_type


@numba.jit
def flatten_array(A):
    govty__xil = []
    hahmz__bxb = len(A)
    for vmjp__pxqmr in range(hahmz__bxb):
        neoj__hneq = A[vmjp__pxqmr]
        for jal__ugc in neoj__hneq:
            govty__xil.append(jal__ugc)
    return bodo.utils.conversion.coerce_to_array(govty__xil)


def parse_datetimes_from_strings(data):
    return data


@overload(parse_datetimes_from_strings, no_unliteral=True)
def overload_parse_datetimes_from_strings(data):
    assert data == bodo.string_array_type

    def parse_impl(data):
        numba.parfors.parfor.init_prange()
        hahmz__bxb = len(data)
        ctse__tqirx = np.empty(hahmz__bxb, bodo.utils.conversion.NS_DTYPE)
        for vmjp__pxqmr in numba.parfors.parfor.internal_prange(hahmz__bxb):
            ctse__tqirx[vmjp__pxqmr
                ] = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(data[
                vmjp__pxqmr])
        return ctse__tqirx
    return parse_impl


def convert_to_dt64ns(data):
    return data


@overload(convert_to_dt64ns, no_unliteral=True)
def overload_convert_to_dt64ns(data):
    if data == bodo.hiframes.datetime_date_ext.datetime_date_array_type:
        return (lambda data: bodo.hiframes.pd_timestamp_ext.
            datetime_date_arr_to_dt64_arr(data))
    if is_np_arr_typ(data, types.int64):
        return lambda data: data.view(bodo.utils.conversion.NS_DTYPE)
    if is_np_arr_typ(data, types.NPDatetime('ns')):
        return lambda data: data
    if data == bodo.string_array_type:
        return lambda data: bodo.utils.conversion.parse_datetimes_from_strings(
            data)
    raise BodoError(f'invalid data type {data} for dt64 conversion')


def convert_to_td64ns(data):
    return data


@overload(convert_to_td64ns, no_unliteral=True)
def overload_convert_to_td64ns(data):
    if is_np_arr_typ(data, types.int64):
        return lambda data: data.view(bodo.utils.conversion.TD_DTYPE)
    if is_np_arr_typ(data, types.NPTimedelta('ns')):
        return lambda data: data
    if data == bodo.string_array_type:
        raise BodoError('conversion to timedelta from string not supported yet'
            )
    raise BodoError(f'invalid data type {data} for timedelta64 conversion')


def convert_to_index(data, name=None):
    return data


@overload(convert_to_index, no_unliteral=True)
def overload_convert_to_index(data, name=None):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
    if isinstance(data, (RangeIndexType, NumericIndexType,
        DatetimeIndexType, TimedeltaIndexType, StringIndexType,
        BinaryIndexType, CategoricalIndexType, PeriodIndexType, types.NoneType)
        ):
        return lambda data, name=None: data

    def impl(data, name=None):
        fzmyp__bixcp = bodo.utils.conversion.coerce_to_array(data)
        return bodo.utils.conversion.index_from_array(fzmyp__bixcp, name)
    return impl


def force_convert_index(I1, I2):
    return I2


@overload(force_convert_index, no_unliteral=True)
def overload_force_convert_index(I1, I2):
    from bodo.hiframes.pd_index_ext import RangeIndexType
    if isinstance(I2, RangeIndexType):
        return lambda I1, I2: pd.RangeIndex(len(I1._data))
    return lambda I1, I2: I1


def index_from_array(data, name=None):
    return data


@overload(index_from_array, no_unliteral=True)
def overload_index_from_array(data, name=None):
    if data in [bodo.string_array_type, bodo.binary_array_type]:
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_binary_str_index(data, name))
    if (data == bodo.hiframes.datetime_date_ext.datetime_date_array_type or
        data.dtype == types.NPDatetime('ns')):
        return lambda data, name=None: pd.DatetimeIndex(data, name=name)
    if data.dtype == types.NPTimedelta('ns'):
        return lambda data, name=None: pd.TimedeltaIndex(data, name=name)
    if isinstance(data.dtype, (types.Integer, types.Float, types.Boolean)):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_numeric_index(data, name))
    if isinstance(data, bodo.libs.interval_arr_ext.IntervalArrayType):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_interval_index(data, name))
    if isinstance(data, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_categorical_index(data, name))
    raise BodoError(f'cannot convert {data} to Index')


def index_to_array(data):
    return data


@overload(index_to_array, no_unliteral=True)
def overload_index_to_array(I):
    from bodo.hiframes.pd_index_ext import RangeIndexType
    if isinstance(I, RangeIndexType):
        return lambda I: np.arange(I._start, I._stop, I._step)
    return lambda I: bodo.hiframes.pd_index_ext.get_index_data(I)


def false_if_none(val):
    return False if val is None else val


@overload(false_if_none, no_unliteral=True)
def overload_false_if_none(val):
    if is_overload_none(val):
        return lambda val: False
    return lambda val: val


def extract_name_if_none(data, name):
    return name


@overload(extract_name_if_none, no_unliteral=True)
def overload_extract_name_if_none(data, name):
    from bodo.hiframes.pd_index_ext import CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, TimedeltaIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    if not is_overload_none(name):
        return lambda data, name: name
    if isinstance(data, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType, PeriodIndexType, CategoricalIndexType)):
        return lambda data, name: bodo.hiframes.pd_index_ext.get_index_name(
            data)
    if isinstance(data, SeriesType):
        return lambda data, name: bodo.hiframes.pd_series_ext.get_series_name(
            data)
    return lambda data, name: name


def extract_index_if_none(data, index):
    return index


@overload(extract_index_if_none, no_unliteral=True)
def overload_extract_index_if_none(data, index):
    from bodo.hiframes.pd_series_ext import SeriesType
    if not is_overload_none(index):
        return lambda data, index: index
    if isinstance(data, SeriesType):
        return (lambda data, index: bodo.hiframes.pd_series_ext.
            get_series_index(data))
    return lambda data, index: bodo.hiframes.pd_index_ext.init_range_index(
        0, len(data), 1, None)


def box_if_dt64(val):
    return val


@overload(box_if_dt64, no_unliteral=True)
def overload_box_if_dt64(val):
    if val == types.NPDatetime('ns'):
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            convert_datetime64_to_timestamp(val))
    if val == types.NPTimedelta('ns'):
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            convert_numpy_timedelta64_to_pd_timedelta(val))
    return lambda val: val


def unbox_if_timestamp(val):
    return val


@overload(unbox_if_timestamp, no_unliteral=True)
def overload_unbox_if_timestamp(val):
    if val == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        return lambda val: bodo.hiframes.pd_timestamp_ext.integer_to_dt64(val
            .value)
    if val == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:
        return lambda val: bodo.hiframes.pd_timestamp_ext.integer_to_dt64(pd
            .Timestamp(val).value)
    if val == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            integer_to_timedelta64(val.value))
    if val == types.Optional(bodo.hiframes.pd_timestamp_ext.pd_timestamp_type):

        def impl_optional(val):
            if val is None:
                ebag__qof = None
            else:
                ebag__qof = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(bodo
                    .utils.indexing.unoptional(val).value)
            return ebag__qof
        return impl_optional
    if val == types.Optional(bodo.hiframes.datetime_timedelta_ext.
        pd_timedelta_type):

        def impl_optional_td(val):
            if val is None:
                ebag__qof = None
            else:
                ebag__qof = (bodo.hiframes.pd_timestamp_ext.
                    integer_to_timedelta64(bodo.utils.indexing.unoptional(
                    val).value))
            return ebag__qof
        return impl_optional_td
    return lambda val: val


def to_tuple(val):
    return val


@overload(to_tuple, no_unliteral=True)
def overload_to_tuple(val):
    if not isinstance(val, types.BaseTuple) and is_overload_constant_list(val):
        nrcgs__rbr = len(val.types if isinstance(val, types.LiteralList) else
            get_overload_const_list(val))
        eeez__yzaq = 'def f(val):\n'
        xnhz__mvyyr = ','.join(f'val[{vmjp__pxqmr}]' for vmjp__pxqmr in
            range(nrcgs__rbr))
        eeez__yzaq += f'  return ({xnhz__mvyyr},)\n'
        ldy__xgmhc = {}
        exec(eeez__yzaq, {}, ldy__xgmhc)
        impl = ldy__xgmhc['f']
        return impl
    assert isinstance(val, types.BaseTuple), 'tuple type expected'
    return lambda val: val


def get_array_if_series_or_index(data):
    return data


@overload(get_array_if_series_or_index)
def overload_get_array_if_series_or_index(data):
    from bodo.hiframes.pd_series_ext import SeriesType
    if isinstance(data, SeriesType):
        return lambda data: bodo.hiframes.pd_series_ext.get_series_data(data)
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        return lambda data: bodo.utils.conversion.coerce_to_array(data)
    if isinstance(data, bodo.hiframes.pd_index_ext.HeterogeneousIndexType):
        if not is_heterogeneous_tuple_type(data.data):

            def impl(data):
                gjd__zfx = bodo.hiframes.pd_index_ext.get_index_data(data)
                return bodo.utils.conversion.coerce_to_array(gjd__zfx)
            return impl

        def impl(data):
            return bodo.hiframes.pd_index_ext.get_index_data(data)
        return impl
    return lambda data: data


def extract_index_array(A):
    return np.arange(len(A))


@overload(extract_index_array, no_unliteral=True)
def overload_extract_index_array(A):
    from bodo.hiframes.pd_series_ext import SeriesType
    if isinstance(A, SeriesType):

        def impl(A):
            index = bodo.hiframes.pd_series_ext.get_series_index(A)
            lnhsk__brbty = bodo.utils.conversion.coerce_to_array(index)
            return lnhsk__brbty
        return impl
    return lambda A: np.arange(len(A))


def ensure_contig_if_np(arr):
    return np.ascontiguousarray(arr)


@overload(ensure_contig_if_np, no_unliteral=True)
def overload_ensure_contig_if_np(arr):
    if isinstance(arr, types.Array):
        return lambda arr: np.ascontiguousarray(arr)
    return lambda arr: arr


def struct_if_heter_dict(values, names):
    return {tolz__diifc: bsj__tsq for tolz__diifc, bsj__tsq in zip(names,
        values)}


@overload(struct_if_heter_dict, no_unliteral=True)
def overload_struct_if_heter_dict(values, names):
    if not types.is_homogeneous(*values.types):
        return lambda values, names: bodo.libs.struct_arr_ext.init_struct(
            values, names)
    mge__ewbrt = len(values.types)
    eeez__yzaq = 'def f(values, names):\n'
    xnhz__mvyyr = ','.join("'{}': values[{}]".format(get_overload_const_str
        (names.types[vmjp__pxqmr]), vmjp__pxqmr) for vmjp__pxqmr in range(
        mge__ewbrt))
    eeez__yzaq += '  return {{{}}}\n'.format(xnhz__mvyyr)
    ldy__xgmhc = {}
    exec(eeez__yzaq, {}, ldy__xgmhc)
    impl = ldy__xgmhc['f']
    return impl
