"""
Support for Series.dt attributes and methods
"""
import datetime
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, raise_bodo_error
dt64_dtype = np.dtype('datetime64[ns]')
timedelta64_dtype = np.dtype('timedelta64[ns]')


class SeriesDatetimePropertiesType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        auon__eltaf = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(auon__eltaf)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bet__odsb = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, bet__odsb)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        btzb__znk, = args
        zktd__amvu = signature.return_type
        xgqrh__dzym = cgutils.create_struct_proxy(zktd__amvu)(context, builder)
        xgqrh__dzym.obj = btzb__znk
        context.nrt.incref(builder, signature.args[0], btzb__znk)
        return xgqrh__dzym._getvalue()
    return SeriesDatetimePropertiesType(obj)(obj), codegen


@overload_attribute(SeriesType, 'dt')
def overload_series_dt(s):
    if not (bodo.hiframes.pd_series_ext.is_dt64_series_typ(s) or bodo.
        hiframes.pd_series_ext.is_timedelta64_series_typ(s)):
        raise_bodo_error('Can only use .dt accessor with datetimelike values.')
    return lambda s: bodo.hiframes.series_dt_impl.init_series_dt_properties(s)


def create_date_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPDatetime('ns'):
            return
        wtcb__rfmj = 'def impl(S_dt):\n'
        wtcb__rfmj += '    S = S_dt._obj\n'
        wtcb__rfmj += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        wtcb__rfmj += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        wtcb__rfmj += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        wtcb__rfmj += '    numba.parfors.parfor.init_prange()\n'
        wtcb__rfmj += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            wtcb__rfmj += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            wtcb__rfmj += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        wtcb__rfmj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        wtcb__rfmj += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        wtcb__rfmj += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        wtcb__rfmj += '            continue\n'
        wtcb__rfmj += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            wtcb__rfmj += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                wtcb__rfmj += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            wtcb__rfmj += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            wdz__laby = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            wtcb__rfmj += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            wtcb__rfmj += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            wtcb__rfmj += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(wdz__laby[field]))
        elif field == 'is_leap_year':
            wtcb__rfmj += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            wtcb__rfmj += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            wdz__laby = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            wtcb__rfmj += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            wtcb__rfmj += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            wtcb__rfmj += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(wdz__laby[field]))
        else:
            wtcb__rfmj += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            wtcb__rfmj += '        out_arr[i] = ts.' + field + '\n'
        wtcb__rfmj += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        xlb__mwrki = {}
        exec(wtcb__rfmj, {'bodo': bodo, 'numba': numba, 'np': np}, xlb__mwrki)
        impl = xlb__mwrki['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        siesi__dwub = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(siesi__dwub)


_install_date_fields()


def create_date_method_overload(method):
    qbwgk__owiv = method in ['day_name', 'month_name']
    if qbwgk__owiv:
        wtcb__rfmj = 'def overload_method(S_dt, locale=None):\n'
        wtcb__rfmj += '    unsupported_args = dict(locale=locale)\n'
        wtcb__rfmj += '    arg_defaults = dict(locale=None)\n'
        wtcb__rfmj += '    bodo.utils.typing.check_unsupported_args(\n'
        wtcb__rfmj += f"        'Series.dt.{method}',\n"
        wtcb__rfmj += '        unsupported_args,\n'
        wtcb__rfmj += '        arg_defaults,\n'
        wtcb__rfmj += "        package_name='pandas',\n"
        wtcb__rfmj += "        module_name='Series',\n"
        wtcb__rfmj += '    )\n'
    else:
        wtcb__rfmj = 'def overload_method(S_dt):\n'
    wtcb__rfmj += '    if not S_dt.stype.dtype == bodo.datetime64ns:\n'
    wtcb__rfmj += '        return\n'
    if qbwgk__owiv:
        wtcb__rfmj += '    def impl(S_dt, locale=None):\n'
    else:
        wtcb__rfmj += '    def impl(S_dt):\n'
    wtcb__rfmj += '        S = S_dt._obj\n'
    wtcb__rfmj += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    wtcb__rfmj += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    wtcb__rfmj += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    wtcb__rfmj += '        numba.parfors.parfor.init_prange()\n'
    wtcb__rfmj += '        n = len(arr)\n'
    if qbwgk__owiv:
        wtcb__rfmj += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        wtcb__rfmj += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    wtcb__rfmj += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    wtcb__rfmj += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    wtcb__rfmj += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    wtcb__rfmj += '                continue\n'
    wtcb__rfmj += """            ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(arr[i])
"""
    wtcb__rfmj += f'            method_val = ts.{method}()\n'
    if qbwgk__owiv:
        wtcb__rfmj += '            out_arr[i] = method_val\n'
    else:
        wtcb__rfmj += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    wtcb__rfmj += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    wtcb__rfmj += '    return impl\n'
    xlb__mwrki = {}
    exec(wtcb__rfmj, {'bodo': bodo, 'numba': numba, 'np': np}, xlb__mwrki)
    overload_method = xlb__mwrki['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        siesi__dwub = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            siesi__dwub)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not S_dt.stype.dtype == types.NPDatetime('ns'):
        return

    def impl(S_dt):
        pdpjq__xqcer = S_dt._obj
        oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(pdpjq__xqcer)
        oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(pdpjq__xqcer)
        auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(pdpjq__xqcer)
        numba.parfors.parfor.init_prange()
        spixh__lxfe = len(oax__fxvcz)
        zimlu__ngg = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            spixh__lxfe)
        for pzrkt__gkhf in numba.parfors.parfor.internal_prange(spixh__lxfe):
            gxbvl__fra = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                oax__fxvcz[pzrkt__gkhf])
            sfprx__qqa = (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(gxbvl__fra))
            zimlu__ngg[pzrkt__gkhf] = datetime.date(sfprx__qqa.year,
                sfprx__qqa.month, sfprx__qqa.day)
        return bodo.hiframes.pd_series_ext.init_series(zimlu__ngg,
            oocuz__qni, auon__eltaf)
    return impl


def create_series_dt_df_output_overload(attr):

    def series_dt_df_output_overload(S_dt):
        if not (attr == 'components' and S_dt.stype.dtype == types.
            NPTimedelta('ns') or attr == 'isocalendar' and S_dt.stype.dtype ==
            types.NPDatetime('ns')):
            return
        if attr == 'components':
            fxyq__xwrl = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            dnfh__avtf = 'convert_numpy_timedelta64_to_pd_timedelta'
            zegtb__iyau = 'np.empty(n, np.int64)'
            wbjc__hhyr = attr
        elif attr == 'isocalendar':
            fxyq__xwrl = ['year', 'week', 'day']
            dnfh__avtf = 'convert_datetime64_to_timestamp'
            zegtb__iyau = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            wbjc__hhyr = attr + '()'
        wtcb__rfmj = 'def impl(S_dt):\n'
        wtcb__rfmj += '    S = S_dt._obj\n'
        wtcb__rfmj += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        wtcb__rfmj += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        wtcb__rfmj += '    numba.parfors.parfor.init_prange()\n'
        wtcb__rfmj += '    n = len(arr)\n'
        for field in fxyq__xwrl:
            wtcb__rfmj += '    {} = {}\n'.format(field, zegtb__iyau)
        wtcb__rfmj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        wtcb__rfmj += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in fxyq__xwrl:
            wtcb__rfmj += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        wtcb__rfmj += '            continue\n'
        iign__ofu = '(' + '[i], '.join(fxyq__xwrl) + '[i])'
        wtcb__rfmj += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(iign__ofu, dnfh__avtf, wbjc__hhyr))
        dkgpt__ssy = '(' + ', '.join(fxyq__xwrl) + ')'
        gqmbj__gjte = "('" + "', '".join(fxyq__xwrl) + "')"
        wtcb__rfmj += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, {})\n'
            .format(dkgpt__ssy, gqmbj__gjte))
        xlb__mwrki = {}
        exec(wtcb__rfmj, {'bodo': bodo, 'numba': numba, 'np': np}, xlb__mwrki)
        impl = xlb__mwrki['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    vuhf__aiwaq = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, xew__ojfkj in vuhf__aiwaq:
        siesi__dwub = create_series_dt_df_output_overload(attr)
        xew__ojfkj(SeriesDatetimePropertiesType, attr, inline='always')(
            siesi__dwub)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        wtcb__rfmj = 'def impl(S_dt):\n'
        wtcb__rfmj += '    S = S_dt._obj\n'
        wtcb__rfmj += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        wtcb__rfmj += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        wtcb__rfmj += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        wtcb__rfmj += '    numba.parfors.parfor.init_prange()\n'
        wtcb__rfmj += '    n = len(A)\n'
        wtcb__rfmj += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        wtcb__rfmj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        wtcb__rfmj += '        if bodo.libs.array_kernels.isna(A, i):\n'
        wtcb__rfmj += '            bodo.libs.array_kernels.setna(B, i)\n'
        wtcb__rfmj += '            continue\n'
        wtcb__rfmj += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            wtcb__rfmj += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            wtcb__rfmj += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            wtcb__rfmj += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            wtcb__rfmj += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        wtcb__rfmj += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        xlb__mwrki = {}
        exec(wtcb__rfmj, {'numba': numba, 'np': np, 'bodo': bodo}, xlb__mwrki)
        impl = xlb__mwrki['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        wtcb__rfmj = 'def impl(S_dt):\n'
        wtcb__rfmj += '    S = S_dt._obj\n'
        wtcb__rfmj += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        wtcb__rfmj += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        wtcb__rfmj += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        wtcb__rfmj += '    numba.parfors.parfor.init_prange()\n'
        wtcb__rfmj += '    n = len(A)\n'
        if method == 'total_seconds':
            wtcb__rfmj += '    B = np.empty(n, np.float64)\n'
        else:
            wtcb__rfmj += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        wtcb__rfmj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        wtcb__rfmj += '        if bodo.libs.array_kernels.isna(A, i):\n'
        wtcb__rfmj += '            bodo.libs.array_kernels.setna(B, i)\n'
        wtcb__rfmj += '            continue\n'
        wtcb__rfmj += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            wtcb__rfmj += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            wtcb__rfmj += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            wtcb__rfmj += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            wtcb__rfmj += '    return B\n'
        xlb__mwrki = {}
        exec(wtcb__rfmj, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, xlb__mwrki)
        impl = xlb__mwrki['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        siesi__dwub = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(siesi__dwub)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        siesi__dwub = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            siesi__dwub)


_install_S_dt_timedelta_methods()


@overload_method(SeriesDatetimePropertiesType, 'strftime', inline='always',
    no_unliteral=True)
def dt_strftime(S_dt, date_format):
    if S_dt.stype.dtype != types.NPDatetime('ns'):
        return
    if types.unliteral(date_format) != types.unicode_type:
        raise BodoError(
            "Series.str.strftime(): 'date_format' argument must be a string")

    def impl(S_dt, date_format):
        pdpjq__xqcer = S_dt._obj
        kqzkq__lhn = bodo.hiframes.pd_series_ext.get_series_data(pdpjq__xqcer)
        oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(pdpjq__xqcer)
        auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(pdpjq__xqcer)
        numba.parfors.parfor.init_prange()
        spixh__lxfe = len(kqzkq__lhn)
        ryl__evhud = bodo.libs.str_arr_ext.pre_alloc_string_array(spixh__lxfe,
            -1)
        for mdlvf__big in numba.parfors.parfor.internal_prange(spixh__lxfe):
            if bodo.libs.array_kernels.isna(kqzkq__lhn, mdlvf__big):
                bodo.libs.array_kernels.setna(ryl__evhud, mdlvf__big)
                continue
            ryl__evhud[mdlvf__big
                ] = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(
                kqzkq__lhn[mdlvf__big]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(ryl__evhud,
            oocuz__qni, auon__eltaf)
    return impl


def create_timedelta_freq_overload(method):

    def freq_overload(S_dt, freq, ambiguous='raise', nonexistent='raise'):
        if S_dt.stype.dtype != types.NPTimedelta('ns'
            ) and S_dt.stype.dtype != types.NPDatetime('ns'):
            return
        xyznx__ttjh = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        khl__rrp = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', xyznx__ttjh, khl__rrp,
            package_name='pandas', module_name='Series')
        wtcb__rfmj = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        wtcb__rfmj += '    S = S_dt._obj\n'
        wtcb__rfmj += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        wtcb__rfmj += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        wtcb__rfmj += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        wtcb__rfmj += '    numba.parfors.parfor.init_prange()\n'
        wtcb__rfmj += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            wtcb__rfmj += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            wtcb__rfmj += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        wtcb__rfmj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        wtcb__rfmj += '        if bodo.libs.array_kernels.isna(A, i):\n'
        wtcb__rfmj += '            bodo.libs.array_kernels.setna(B, i)\n'
        wtcb__rfmj += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            evwz__zeyt = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            inme__xval = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            evwz__zeyt = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            inme__xval = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        wtcb__rfmj += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            inme__xval, evwz__zeyt, method)
        wtcb__rfmj += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        xlb__mwrki = {}
        exec(wtcb__rfmj, {'numba': numba, 'np': np, 'bodo': bodo}, xlb__mwrki)
        impl = xlb__mwrki['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    vpjh__fst = ['ceil', 'floor', 'round']
    for method in vpjh__fst:
        siesi__dwub = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            siesi__dwub)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            wqgs__xvah = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                iraoc__ekizi = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lqzzz__mtnon = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                spixh__lxfe = len(iraoc__ekizi)
                pdpjq__xqcer = np.empty(spixh__lxfe, timedelta64_dtype)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    vdj__tvssq = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(iraoc__ekizi[pzrkt__gkhf]))
                    rftc__bnqi = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(lqzzz__mtnon[pzrkt__gkhf]))
                    if vdj__tvssq == zuc__ulqm or rftc__bnqi == zuc__ulqm:
                        rsj__ger = zuc__ulqm
                    else:
                        rsj__ger = op(vdj__tvssq, rftc__bnqi)
                    pdpjq__xqcer[pzrkt__gkhf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rsj__ger)
                return bodo.hiframes.pd_series_ext.init_series(pdpjq__xqcer,
                    oocuz__qni, auon__eltaf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            wqgs__xvah = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                lqzzz__mtnon = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                spixh__lxfe = len(oax__fxvcz)
                pdpjq__xqcer = np.empty(spixh__lxfe, dt64_dtype)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    sdlq__mjk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        oax__fxvcz[pzrkt__gkhf])
                    iydh__pam = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(lqzzz__mtnon[pzrkt__gkhf]))
                    if sdlq__mjk == zuc__ulqm or iydh__pam == zuc__ulqm:
                        rsj__ger = zuc__ulqm
                    else:
                        rsj__ger = op(sdlq__mjk, iydh__pam)
                    pdpjq__xqcer[pzrkt__gkhf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rsj__ger)
                return bodo.hiframes.pd_series_ext.init_series(pdpjq__xqcer,
                    oocuz__qni, auon__eltaf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            wqgs__xvah = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                lqzzz__mtnon = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                spixh__lxfe = len(oax__fxvcz)
                pdpjq__xqcer = np.empty(spixh__lxfe, dt64_dtype)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    sdlq__mjk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        oax__fxvcz[pzrkt__gkhf])
                    iydh__pam = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(lqzzz__mtnon[pzrkt__gkhf]))
                    if sdlq__mjk == zuc__ulqm or iydh__pam == zuc__ulqm:
                        rsj__ger = zuc__ulqm
                    else:
                        rsj__ger = op(sdlq__mjk, iydh__pam)
                    pdpjq__xqcer[pzrkt__gkhf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rsj__ger)
                return bodo.hiframes.pd_series_ext.init_series(pdpjq__xqcer,
                    oocuz__qni, auon__eltaf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            wqgs__xvah = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                spixh__lxfe = len(oax__fxvcz)
                pdpjq__xqcer = np.empty(spixh__lxfe, timedelta64_dtype)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                lmuk__hmavt = rhs.value
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    sdlq__mjk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        oax__fxvcz[pzrkt__gkhf])
                    if sdlq__mjk == zuc__ulqm or lmuk__hmavt == zuc__ulqm:
                        rsj__ger = zuc__ulqm
                    else:
                        rsj__ger = op(sdlq__mjk, lmuk__hmavt)
                    pdpjq__xqcer[pzrkt__gkhf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rsj__ger)
                return bodo.hiframes.pd_series_ext.init_series(pdpjq__xqcer,
                    oocuz__qni, auon__eltaf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            wqgs__xvah = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                spixh__lxfe = len(oax__fxvcz)
                pdpjq__xqcer = np.empty(spixh__lxfe, timedelta64_dtype)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                lmuk__hmavt = lhs.value
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    sdlq__mjk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        oax__fxvcz[pzrkt__gkhf])
                    if lmuk__hmavt == zuc__ulqm or sdlq__mjk == zuc__ulqm:
                        rsj__ger = zuc__ulqm
                    else:
                        rsj__ger = op(lmuk__hmavt, sdlq__mjk)
                    pdpjq__xqcer[pzrkt__gkhf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rsj__ger)
                return bodo.hiframes.pd_series_ext.init_series(pdpjq__xqcer,
                    oocuz__qni, auon__eltaf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            wqgs__xvah = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                spixh__lxfe = len(oax__fxvcz)
                pdpjq__xqcer = np.empty(spixh__lxfe, dt64_dtype)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                cwc__gpnxd = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                iydh__pam = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(cwc__gpnxd))
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    sdlq__mjk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        oax__fxvcz[pzrkt__gkhf])
                    if sdlq__mjk == zuc__ulqm or iydh__pam == zuc__ulqm:
                        rsj__ger = zuc__ulqm
                    else:
                        rsj__ger = op(sdlq__mjk, iydh__pam)
                    pdpjq__xqcer[pzrkt__gkhf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rsj__ger)
                return bodo.hiframes.pd_series_ext.init_series(pdpjq__xqcer,
                    oocuz__qni, auon__eltaf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            wqgs__xvah = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                spixh__lxfe = len(oax__fxvcz)
                pdpjq__xqcer = np.empty(spixh__lxfe, dt64_dtype)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                cwc__gpnxd = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                iydh__pam = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(cwc__gpnxd))
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    sdlq__mjk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        oax__fxvcz[pzrkt__gkhf])
                    if sdlq__mjk == zuc__ulqm or iydh__pam == zuc__ulqm:
                        rsj__ger = zuc__ulqm
                    else:
                        rsj__ger = op(sdlq__mjk, iydh__pam)
                    pdpjq__xqcer[pzrkt__gkhf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rsj__ger)
                return bodo.hiframes.pd_series_ext.init_series(pdpjq__xqcer,
                    oocuz__qni, auon__eltaf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            wqgs__xvah = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                spixh__lxfe = len(oax__fxvcz)
                pdpjq__xqcer = np.empty(spixh__lxfe, timedelta64_dtype)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                gxbvl__fra = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                sdlq__mjk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    gxbvl__fra)
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    tvnx__qbll = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oax__fxvcz[pzrkt__gkhf]))
                    if tvnx__qbll == zuc__ulqm or sdlq__mjk == zuc__ulqm:
                        rsj__ger = zuc__ulqm
                    else:
                        rsj__ger = op(tvnx__qbll, sdlq__mjk)
                    pdpjq__xqcer[pzrkt__gkhf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rsj__ger)
                return bodo.hiframes.pd_series_ext.init_series(pdpjq__xqcer,
                    oocuz__qni, auon__eltaf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            wqgs__xvah = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                spixh__lxfe = len(oax__fxvcz)
                pdpjq__xqcer = np.empty(spixh__lxfe, timedelta64_dtype)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                gxbvl__fra = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                sdlq__mjk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    gxbvl__fra)
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    tvnx__qbll = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oax__fxvcz[pzrkt__gkhf]))
                    if sdlq__mjk == zuc__ulqm or tvnx__qbll == zuc__ulqm:
                        rsj__ger = zuc__ulqm
                    else:
                        rsj__ger = op(sdlq__mjk, tvnx__qbll)
                    pdpjq__xqcer[pzrkt__gkhf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rsj__ger)
                return bodo.hiframes.pd_series_ext.init_series(pdpjq__xqcer,
                    oocuz__qni, auon__eltaf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            wqgs__xvah = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                spixh__lxfe = len(oax__fxvcz)
                pdpjq__xqcer = np.empty(spixh__lxfe, timedelta64_dtype)
                zuc__ulqm = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(wqgs__xvah))
                cwc__gpnxd = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                iydh__pam = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(cwc__gpnxd))
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    mbz__hct = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(oax__fxvcz[pzrkt__gkhf]))
                    if iydh__pam == zuc__ulqm or mbz__hct == zuc__ulqm:
                        rsj__ger = zuc__ulqm
                    else:
                        rsj__ger = op(mbz__hct, iydh__pam)
                    pdpjq__xqcer[pzrkt__gkhf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rsj__ger)
                return bodo.hiframes.pd_series_ext.init_series(pdpjq__xqcer,
                    oocuz__qni, auon__eltaf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            wqgs__xvah = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                spixh__lxfe = len(oax__fxvcz)
                pdpjq__xqcer = np.empty(spixh__lxfe, timedelta64_dtype)
                zuc__ulqm = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(wqgs__xvah))
                cwc__gpnxd = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                iydh__pam = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(cwc__gpnxd))
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    mbz__hct = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(oax__fxvcz[pzrkt__gkhf]))
                    if iydh__pam == zuc__ulqm or mbz__hct == zuc__ulqm:
                        rsj__ger = zuc__ulqm
                    else:
                        rsj__ger = op(iydh__pam, mbz__hct)
                    pdpjq__xqcer[pzrkt__gkhf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rsj__ger)
                return bodo.hiframes.pd_series_ext.init_series(pdpjq__xqcer,
                    oocuz__qni, auon__eltaf)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            wvut__kwhiu = True
        else:
            wvut__kwhiu = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            wqgs__xvah = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                spixh__lxfe = len(oax__fxvcz)
                zimlu__ngg = bodo.libs.bool_arr_ext.alloc_bool_array(
                    spixh__lxfe)
                zuc__ulqm = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(wqgs__xvah))
                lcxml__mzza = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                fdueu__ylhn = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(lcxml__mzza))
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    yvhcj__hclf = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(oax__fxvcz[pzrkt__gkhf]))
                    if yvhcj__hclf == zuc__ulqm or fdueu__ylhn == zuc__ulqm:
                        rsj__ger = wvut__kwhiu
                    else:
                        rsj__ger = op(yvhcj__hclf, fdueu__ylhn)
                    zimlu__ngg[pzrkt__gkhf] = rsj__ger
                return bodo.hiframes.pd_series_ext.init_series(zimlu__ngg,
                    oocuz__qni, auon__eltaf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            wqgs__xvah = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                spixh__lxfe = len(oax__fxvcz)
                zimlu__ngg = bodo.libs.bool_arr_ext.alloc_bool_array(
                    spixh__lxfe)
                zuc__ulqm = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(wqgs__xvah))
                atuj__sqrn = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                yvhcj__hclf = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(atuj__sqrn))
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    fdueu__ylhn = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(oax__fxvcz[pzrkt__gkhf]))
                    if yvhcj__hclf == zuc__ulqm or fdueu__ylhn == zuc__ulqm:
                        rsj__ger = wvut__kwhiu
                    else:
                        rsj__ger = op(yvhcj__hclf, fdueu__ylhn)
                    zimlu__ngg[pzrkt__gkhf] = rsj__ger
                return bodo.hiframes.pd_series_ext.init_series(zimlu__ngg,
                    oocuz__qni, auon__eltaf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            wqgs__xvah = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                spixh__lxfe = len(oax__fxvcz)
                zimlu__ngg = bodo.libs.bool_arr_ext.alloc_bool_array(
                    spixh__lxfe)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    yvhcj__hclf = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oax__fxvcz[pzrkt__gkhf]))
                    if yvhcj__hclf == zuc__ulqm or rhs.value == zuc__ulqm:
                        rsj__ger = wvut__kwhiu
                    else:
                        rsj__ger = op(yvhcj__hclf, rhs.value)
                    zimlu__ngg[pzrkt__gkhf] = rsj__ger
                return bodo.hiframes.pd_series_ext.init_series(zimlu__ngg,
                    oocuz__qni, auon__eltaf)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            wqgs__xvah = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                spixh__lxfe = len(oax__fxvcz)
                zimlu__ngg = bodo.libs.bool_arr_ext.alloc_bool_array(
                    spixh__lxfe)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    fdueu__ylhn = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oax__fxvcz[pzrkt__gkhf]))
                    if fdueu__ylhn == zuc__ulqm or lhs.value == zuc__ulqm:
                        rsj__ger = wvut__kwhiu
                    else:
                        rsj__ger = op(lhs.value, fdueu__ylhn)
                    zimlu__ngg[pzrkt__gkhf] = rsj__ger
                return bodo.hiframes.pd_series_ext.init_series(zimlu__ngg,
                    oocuz__qni, auon__eltaf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            wqgs__xvah = lhs.dtype('NaT')

            def impl(lhs, rhs):
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                spixh__lxfe = len(oax__fxvcz)
                zimlu__ngg = bodo.libs.bool_arr_ext.alloc_bool_array(
                    spixh__lxfe)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                javl__hfl = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                cthmr__xhlr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    javl__hfl)
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    yvhcj__hclf = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oax__fxvcz[pzrkt__gkhf]))
                    if yvhcj__hclf == zuc__ulqm or cthmr__xhlr == zuc__ulqm:
                        rsj__ger = wvut__kwhiu
                    else:
                        rsj__ger = op(yvhcj__hclf, cthmr__xhlr)
                    zimlu__ngg[pzrkt__gkhf] = rsj__ger
                return bodo.hiframes.pd_series_ext.init_series(zimlu__ngg,
                    oocuz__qni, auon__eltaf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            wqgs__xvah = rhs.dtype('NaT')

            def impl(lhs, rhs):
                oax__fxvcz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                oocuz__qni = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                auon__eltaf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                spixh__lxfe = len(oax__fxvcz)
                zimlu__ngg = bodo.libs.bool_arr_ext.alloc_bool_array(
                    spixh__lxfe)
                zuc__ulqm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wqgs__xvah)
                javl__hfl = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                cthmr__xhlr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    javl__hfl)
                for pzrkt__gkhf in numba.parfors.parfor.internal_prange(
                    spixh__lxfe):
                    gxbvl__fra = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oax__fxvcz[pzrkt__gkhf]))
                    if gxbvl__fra == zuc__ulqm or cthmr__xhlr == zuc__ulqm:
                        rsj__ger = wvut__kwhiu
                    else:
                        rsj__ger = op(cthmr__xhlr, gxbvl__fra)
                    zimlu__ngg[pzrkt__gkhf] = rsj__ger
                return bodo.hiframes.pd_series_ext.init_series(zimlu__ngg,
                    oocuz__qni, auon__eltaf)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'tz_convert', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for wxuq__lvg in series_dt_unsupported_attrs:
        ynb__npqla = 'Series.dt.' + wxuq__lvg
        overload_attribute(SeriesDatetimePropertiesType, wxuq__lvg)(
            create_unsupported_overload(ynb__npqla))
    for lpbbp__jgayi in series_dt_unsupported_methods:
        ynb__npqla = 'Series.dt.' + lpbbp__jgayi
        overload_method(SeriesDatetimePropertiesType, lpbbp__jgayi,
            no_unliteral=True)(create_unsupported_overload(ynb__npqla))


_install_series_dt_unsupported()
