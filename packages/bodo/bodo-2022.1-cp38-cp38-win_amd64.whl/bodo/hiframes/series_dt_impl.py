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
        adq__gtn = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(adq__gtn)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        oxk__zgsja = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, oxk__zgsja)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        yvwkk__aupn, = args
        jkakf__xjcv = signature.return_type
        nwpqh__kdjb = cgutils.create_struct_proxy(jkakf__xjcv)(context, builder
            )
        nwpqh__kdjb.obj = yvwkk__aupn
        context.nrt.incref(builder, signature.args[0], yvwkk__aupn)
        return nwpqh__kdjb._getvalue()
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
        mtwc__qlt = 'def impl(S_dt):\n'
        mtwc__qlt += '    S = S_dt._obj\n'
        mtwc__qlt += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        mtwc__qlt += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        mtwc__qlt += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        mtwc__qlt += '    numba.parfors.parfor.init_prange()\n'
        mtwc__qlt += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            mtwc__qlt += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            mtwc__qlt += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        mtwc__qlt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        mtwc__qlt += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        mtwc__qlt += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        mtwc__qlt += '            continue\n'
        mtwc__qlt += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            mtwc__qlt += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                mtwc__qlt += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            mtwc__qlt += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            bvjfk__ahrg = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            mtwc__qlt += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            mtwc__qlt += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            mtwc__qlt += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(bvjfk__ahrg[field]))
        elif field == 'is_leap_year':
            mtwc__qlt += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            mtwc__qlt += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)\n'
                )
        elif field in ('daysinmonth', 'days_in_month'):
            bvjfk__ahrg = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            mtwc__qlt += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            mtwc__qlt += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            mtwc__qlt += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(bvjfk__ahrg[field]))
        else:
            mtwc__qlt += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            mtwc__qlt += '        out_arr[i] = ts.' + field + '\n'
        mtwc__qlt += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        igsu__qgssy = {}
        exec(mtwc__qlt, {'bodo': bodo, 'numba': numba, 'np': np}, igsu__qgssy)
        impl = igsu__qgssy['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        vclmg__fqhov = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(vclmg__fqhov)


_install_date_fields()


def create_date_method_overload(method):
    ysxh__dpo = method in ['day_name', 'month_name']
    if ysxh__dpo:
        mtwc__qlt = 'def overload_method(S_dt, locale=None):\n'
        mtwc__qlt += '    unsupported_args = dict(locale=locale)\n'
        mtwc__qlt += '    arg_defaults = dict(locale=None)\n'
        mtwc__qlt += '    bodo.utils.typing.check_unsupported_args(\n'
        mtwc__qlt += f"        'Series.dt.{method}',\n"
        mtwc__qlt += '        unsupported_args,\n'
        mtwc__qlt += '        arg_defaults,\n'
        mtwc__qlt += "        package_name='pandas',\n"
        mtwc__qlt += "        module_name='Series',\n"
        mtwc__qlt += '    )\n'
    else:
        mtwc__qlt = 'def overload_method(S_dt):\n'
    mtwc__qlt += '    if not S_dt.stype.dtype == bodo.datetime64ns:\n'
    mtwc__qlt += '        return\n'
    if ysxh__dpo:
        mtwc__qlt += '    def impl(S_dt, locale=None):\n'
    else:
        mtwc__qlt += '    def impl(S_dt):\n'
    mtwc__qlt += '        S = S_dt._obj\n'
    mtwc__qlt += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    mtwc__qlt += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    mtwc__qlt += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    mtwc__qlt += '        numba.parfors.parfor.init_prange()\n'
    mtwc__qlt += '        n = len(arr)\n'
    if ysxh__dpo:
        mtwc__qlt += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        mtwc__qlt += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    mtwc__qlt += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    mtwc__qlt += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    mtwc__qlt += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    mtwc__qlt += '                continue\n'
    mtwc__qlt += """            ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(arr[i])
"""
    mtwc__qlt += f'            method_val = ts.{method}()\n'
    if ysxh__dpo:
        mtwc__qlt += '            out_arr[i] = method_val\n'
    else:
        mtwc__qlt += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    mtwc__qlt += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    mtwc__qlt += '    return impl\n'
    igsu__qgssy = {}
    exec(mtwc__qlt, {'bodo': bodo, 'numba': numba, 'np': np}, igsu__qgssy)
    overload_method = igsu__qgssy['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        vclmg__fqhov = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vclmg__fqhov)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not S_dt.stype.dtype == types.NPDatetime('ns'):
        return

    def impl(S_dt):
        pzc__hcbga = S_dt._obj
        ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(pzc__hcbga)
        riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(pzc__hcbga)
        adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(pzc__hcbga)
        numba.parfors.parfor.init_prange()
        jsdmc__evblp = len(ugnm__yej)
        vhh__ede = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            jsdmc__evblp)
        for gug__mpmq in numba.parfors.parfor.internal_prange(jsdmc__evblp):
            puqvk__fhlqb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                ugnm__yej[gug__mpmq])
            elebh__mzbdi = (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(puqvk__fhlqb))
            vhh__ede[gug__mpmq] = datetime.date(elebh__mzbdi.year,
                elebh__mzbdi.month, elebh__mzbdi.day)
        return bodo.hiframes.pd_series_ext.init_series(vhh__ede, riv__jyjcu,
            adq__gtn)
    return impl


def create_series_dt_df_output_overload(attr):

    def series_dt_df_output_overload(S_dt):
        if not (attr == 'components' and S_dt.stype.dtype == types.
            NPTimedelta('ns') or attr == 'isocalendar' and S_dt.stype.dtype ==
            types.NPDatetime('ns')):
            return
        if attr == 'components':
            vaf__pyik = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            mgoyt__axect = 'convert_numpy_timedelta64_to_pd_timedelta'
            mxb__xuqj = 'np.empty(n, np.int64)'
            hpsl__lyeq = attr
        elif attr == 'isocalendar':
            vaf__pyik = ['year', 'week', 'day']
            mgoyt__axect = 'convert_datetime64_to_timestamp'
            mxb__xuqj = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            hpsl__lyeq = attr + '()'
        mtwc__qlt = 'def impl(S_dt):\n'
        mtwc__qlt += '    S = S_dt._obj\n'
        mtwc__qlt += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        mtwc__qlt += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        mtwc__qlt += '    numba.parfors.parfor.init_prange()\n'
        mtwc__qlt += '    n = len(arr)\n'
        for field in vaf__pyik:
            mtwc__qlt += '    {} = {}\n'.format(field, mxb__xuqj)
        mtwc__qlt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        mtwc__qlt += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in vaf__pyik:
            mtwc__qlt += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        mtwc__qlt += '            continue\n'
        wcqge__auw = '(' + '[i], '.join(vaf__pyik) + '[i])'
        mtwc__qlt += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(wcqge__auw, mgoyt__axect, hpsl__lyeq))
        kgb__cukr = '(' + ', '.join(vaf__pyik) + ')'
        ovfrn__iuuou = "('" + "', '".join(vaf__pyik) + "')"
        mtwc__qlt += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, {})\n'
            .format(kgb__cukr, ovfrn__iuuou))
        igsu__qgssy = {}
        exec(mtwc__qlt, {'bodo': bodo, 'numba': numba, 'np': np}, igsu__qgssy)
        impl = igsu__qgssy['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    aivae__xjdm = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, gev__qmnkt in aivae__xjdm:
        vclmg__fqhov = create_series_dt_df_output_overload(attr)
        gev__qmnkt(SeriesDatetimePropertiesType, attr, inline='always')(
            vclmg__fqhov)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        mtwc__qlt = 'def impl(S_dt):\n'
        mtwc__qlt += '    S = S_dt._obj\n'
        mtwc__qlt += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        mtwc__qlt += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        mtwc__qlt += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        mtwc__qlt += '    numba.parfors.parfor.init_prange()\n'
        mtwc__qlt += '    n = len(A)\n'
        mtwc__qlt += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        mtwc__qlt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        mtwc__qlt += '        if bodo.libs.array_kernels.isna(A, i):\n'
        mtwc__qlt += '            bodo.libs.array_kernels.setna(B, i)\n'
        mtwc__qlt += '            continue\n'
        mtwc__qlt += (
            '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
            )
        if field == 'nanoseconds':
            mtwc__qlt += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            mtwc__qlt += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            mtwc__qlt += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            mtwc__qlt += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        mtwc__qlt += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        igsu__qgssy = {}
        exec(mtwc__qlt, {'numba': numba, 'np': np, 'bodo': bodo}, igsu__qgssy)
        impl = igsu__qgssy['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        mtwc__qlt = 'def impl(S_dt):\n'
        mtwc__qlt += '    S = S_dt._obj\n'
        mtwc__qlt += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        mtwc__qlt += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        mtwc__qlt += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        mtwc__qlt += '    numba.parfors.parfor.init_prange()\n'
        mtwc__qlt += '    n = len(A)\n'
        if method == 'total_seconds':
            mtwc__qlt += '    B = np.empty(n, np.float64)\n'
        else:
            mtwc__qlt += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        mtwc__qlt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        mtwc__qlt += '        if bodo.libs.array_kernels.isna(A, i):\n'
        mtwc__qlt += '            bodo.libs.array_kernels.setna(B, i)\n'
        mtwc__qlt += '            continue\n'
        mtwc__qlt += (
            '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
            )
        if method == 'total_seconds':
            mtwc__qlt += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            mtwc__qlt += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            mtwc__qlt += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            mtwc__qlt += '    return B\n'
        igsu__qgssy = {}
        exec(mtwc__qlt, {'numba': numba, 'np': np, 'bodo': bodo, 'datetime':
            datetime}, igsu__qgssy)
        impl = igsu__qgssy['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        vclmg__fqhov = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(vclmg__fqhov)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        vclmg__fqhov = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vclmg__fqhov)


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
        pzc__hcbga = S_dt._obj
        erry__jpumu = bodo.hiframes.pd_series_ext.get_series_data(pzc__hcbga)
        riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(pzc__hcbga)
        adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(pzc__hcbga)
        numba.parfors.parfor.init_prange()
        jsdmc__evblp = len(erry__jpumu)
        dnzdh__hbi = bodo.libs.str_arr_ext.pre_alloc_string_array(jsdmc__evblp,
            -1)
        for iwl__xyi in numba.parfors.parfor.internal_prange(jsdmc__evblp):
            if bodo.libs.array_kernels.isna(erry__jpumu, iwl__xyi):
                bodo.libs.array_kernels.setna(dnzdh__hbi, iwl__xyi)
                continue
            dnzdh__hbi[iwl__xyi
                ] = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(
                erry__jpumu[iwl__xyi]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(dnzdh__hbi,
            riv__jyjcu, adq__gtn)
    return impl


def create_timedelta_freq_overload(method):

    def freq_overload(S_dt, freq, ambiguous='raise', nonexistent='raise'):
        if S_dt.stype.dtype != types.NPTimedelta('ns'
            ) and S_dt.stype.dtype != types.NPDatetime('ns'):
            return
        tmgh__sznpb = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        jmffb__jqh = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', tmgh__sznpb,
            jmffb__jqh, package_name='pandas', module_name='Series')
        mtwc__qlt = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        mtwc__qlt += '    S = S_dt._obj\n'
        mtwc__qlt += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        mtwc__qlt += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        mtwc__qlt += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        mtwc__qlt += '    numba.parfors.parfor.init_prange()\n'
        mtwc__qlt += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            mtwc__qlt += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            mtwc__qlt += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        mtwc__qlt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        mtwc__qlt += '        if bodo.libs.array_kernels.isna(A, i):\n'
        mtwc__qlt += '            bodo.libs.array_kernels.setna(B, i)\n'
        mtwc__qlt += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            wscp__zbwj = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            mev__alj = 'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64'
        else:
            wscp__zbwj = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            mev__alj = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        mtwc__qlt += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            mev__alj, wscp__zbwj, method)
        mtwc__qlt += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        igsu__qgssy = {}
        exec(mtwc__qlt, {'numba': numba, 'np': np, 'bodo': bodo}, igsu__qgssy)
        impl = igsu__qgssy['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    jwqo__ulku = ['ceil', 'floor', 'round']
    for method in jwqo__ulku:
        vclmg__fqhov = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vclmg__fqhov)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            ibjr__jsgrz = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ghwer__zmngq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                yvn__amvf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                jsdmc__evblp = len(ghwer__zmngq)
                pzc__hcbga = np.empty(jsdmc__evblp, timedelta64_dtype)
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    yrixp__zkb = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ghwer__zmngq[gug__mpmq]))
                    wdum__iouu = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yvn__amvf[gug__mpmq]))
                    if yrixp__zkb == iwg__pupa or wdum__iouu == iwg__pupa:
                        rrk__oakl = iwg__pupa
                    else:
                        rrk__oakl = op(yrixp__zkb, wdum__iouu)
                    pzc__hcbga[gug__mpmq
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrk__oakl)
                return bodo.hiframes.pd_series_ext.init_series(pzc__hcbga,
                    riv__jyjcu, adq__gtn)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            ibjr__jsgrz = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                yvn__amvf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                jsdmc__evblp = len(ugnm__yej)
                pzc__hcbga = np.empty(jsdmc__evblp, dt64_dtype)
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    spc__ftbfv = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ugnm__yej[gug__mpmq]))
                    vfcik__nfjz = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yvn__amvf[gug__mpmq]))
                    if spc__ftbfv == iwg__pupa or vfcik__nfjz == iwg__pupa:
                        rrk__oakl = iwg__pupa
                    else:
                        rrk__oakl = op(spc__ftbfv, vfcik__nfjz)
                    pzc__hcbga[gug__mpmq
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rrk__oakl)
                return bodo.hiframes.pd_series_ext.init_series(pzc__hcbga,
                    riv__jyjcu, adq__gtn)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            ibjr__jsgrz = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                yvn__amvf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                jsdmc__evblp = len(ugnm__yej)
                pzc__hcbga = np.empty(jsdmc__evblp, dt64_dtype)
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    spc__ftbfv = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ugnm__yej[gug__mpmq]))
                    vfcik__nfjz = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yvn__amvf[gug__mpmq]))
                    if spc__ftbfv == iwg__pupa or vfcik__nfjz == iwg__pupa:
                        rrk__oakl = iwg__pupa
                    else:
                        rrk__oakl = op(spc__ftbfv, vfcik__nfjz)
                    pzc__hcbga[gug__mpmq
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rrk__oakl)
                return bodo.hiframes.pd_series_ext.init_series(pzc__hcbga,
                    riv__jyjcu, adq__gtn)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            ibjr__jsgrz = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                jsdmc__evblp = len(ugnm__yej)
                pzc__hcbga = np.empty(jsdmc__evblp, timedelta64_dtype)
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                kiuea__wfi = rhs.value
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    spc__ftbfv = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ugnm__yej[gug__mpmq]))
                    if spc__ftbfv == iwg__pupa or kiuea__wfi == iwg__pupa:
                        rrk__oakl = iwg__pupa
                    else:
                        rrk__oakl = op(spc__ftbfv, kiuea__wfi)
                    pzc__hcbga[gug__mpmq
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrk__oakl)
                return bodo.hiframes.pd_series_ext.init_series(pzc__hcbga,
                    riv__jyjcu, adq__gtn)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            ibjr__jsgrz = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                jsdmc__evblp = len(ugnm__yej)
                pzc__hcbga = np.empty(jsdmc__evblp, timedelta64_dtype)
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                kiuea__wfi = lhs.value
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    spc__ftbfv = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ugnm__yej[gug__mpmq]))
                    if kiuea__wfi == iwg__pupa or spc__ftbfv == iwg__pupa:
                        rrk__oakl = iwg__pupa
                    else:
                        rrk__oakl = op(kiuea__wfi, spc__ftbfv)
                    pzc__hcbga[gug__mpmq
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrk__oakl)
                return bodo.hiframes.pd_series_ext.init_series(pzc__hcbga,
                    riv__jyjcu, adq__gtn)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            ibjr__jsgrz = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                jsdmc__evblp = len(ugnm__yej)
                pzc__hcbga = np.empty(jsdmc__evblp, dt64_dtype)
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                ozbup__ndvjh = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                vfcik__nfjz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ozbup__ndvjh))
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    spc__ftbfv = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ugnm__yej[gug__mpmq]))
                    if spc__ftbfv == iwg__pupa or vfcik__nfjz == iwg__pupa:
                        rrk__oakl = iwg__pupa
                    else:
                        rrk__oakl = op(spc__ftbfv, vfcik__nfjz)
                    pzc__hcbga[gug__mpmq
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rrk__oakl)
                return bodo.hiframes.pd_series_ext.init_series(pzc__hcbga,
                    riv__jyjcu, adq__gtn)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            ibjr__jsgrz = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                jsdmc__evblp = len(ugnm__yej)
                pzc__hcbga = np.empty(jsdmc__evblp, dt64_dtype)
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                ozbup__ndvjh = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                vfcik__nfjz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ozbup__ndvjh))
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    spc__ftbfv = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ugnm__yej[gug__mpmq]))
                    if spc__ftbfv == iwg__pupa or vfcik__nfjz == iwg__pupa:
                        rrk__oakl = iwg__pupa
                    else:
                        rrk__oakl = op(spc__ftbfv, vfcik__nfjz)
                    pzc__hcbga[gug__mpmq
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rrk__oakl)
                return bodo.hiframes.pd_series_ext.init_series(pzc__hcbga,
                    riv__jyjcu, adq__gtn)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            ibjr__jsgrz = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                jsdmc__evblp = len(ugnm__yej)
                pzc__hcbga = np.empty(jsdmc__evblp, timedelta64_dtype)
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                puqvk__fhlqb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                spc__ftbfv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    puqvk__fhlqb)
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    usfgv__bqczp = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ugnm__yej[gug__mpmq]))
                    if usfgv__bqczp == iwg__pupa or spc__ftbfv == iwg__pupa:
                        rrk__oakl = iwg__pupa
                    else:
                        rrk__oakl = op(usfgv__bqczp, spc__ftbfv)
                    pzc__hcbga[gug__mpmq
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrk__oakl)
                return bodo.hiframes.pd_series_ext.init_series(pzc__hcbga,
                    riv__jyjcu, adq__gtn)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            ibjr__jsgrz = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                jsdmc__evblp = len(ugnm__yej)
                pzc__hcbga = np.empty(jsdmc__evblp, timedelta64_dtype)
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                puqvk__fhlqb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                spc__ftbfv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    puqvk__fhlqb)
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    usfgv__bqczp = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ugnm__yej[gug__mpmq]))
                    if spc__ftbfv == iwg__pupa or usfgv__bqczp == iwg__pupa:
                        rrk__oakl = iwg__pupa
                    else:
                        rrk__oakl = op(spc__ftbfv, usfgv__bqczp)
                    pzc__hcbga[gug__mpmq
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrk__oakl)
                return bodo.hiframes.pd_series_ext.init_series(pzc__hcbga,
                    riv__jyjcu, adq__gtn)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ibjr__jsgrz = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                jsdmc__evblp = len(ugnm__yej)
                pzc__hcbga = np.empty(jsdmc__evblp, timedelta64_dtype)
                iwg__pupa = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ibjr__jsgrz))
                ozbup__ndvjh = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                vfcik__nfjz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ozbup__ndvjh))
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    zshf__wxo = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ugnm__yej[gug__mpmq]))
                    if vfcik__nfjz == iwg__pupa or zshf__wxo == iwg__pupa:
                        rrk__oakl = iwg__pupa
                    else:
                        rrk__oakl = op(zshf__wxo, vfcik__nfjz)
                    pzc__hcbga[gug__mpmq
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrk__oakl)
                return bodo.hiframes.pd_series_ext.init_series(pzc__hcbga,
                    riv__jyjcu, adq__gtn)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ibjr__jsgrz = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                jsdmc__evblp = len(ugnm__yej)
                pzc__hcbga = np.empty(jsdmc__evblp, timedelta64_dtype)
                iwg__pupa = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ibjr__jsgrz))
                ozbup__ndvjh = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                vfcik__nfjz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ozbup__ndvjh))
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    zshf__wxo = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ugnm__yej[gug__mpmq]))
                    if vfcik__nfjz == iwg__pupa or zshf__wxo == iwg__pupa:
                        rrk__oakl = iwg__pupa
                    else:
                        rrk__oakl = op(vfcik__nfjz, zshf__wxo)
                    pzc__hcbga[gug__mpmq
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrk__oakl)
                return bodo.hiframes.pd_series_ext.init_series(pzc__hcbga,
                    riv__jyjcu, adq__gtn)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            wbr__qzr = True
        else:
            wbr__qzr = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ibjr__jsgrz = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                jsdmc__evblp = len(ugnm__yej)
                vhh__ede = bodo.libs.bool_arr_ext.alloc_bool_array(jsdmc__evblp
                    )
                iwg__pupa = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ibjr__jsgrz))
                vdk__tegkh = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                xzk__opi = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(vdk__tegkh))
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    qqy__ukv = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ugnm__yej[gug__mpmq]))
                    if qqy__ukv == iwg__pupa or xzk__opi == iwg__pupa:
                        rrk__oakl = wbr__qzr
                    else:
                        rrk__oakl = op(qqy__ukv, xzk__opi)
                    vhh__ede[gug__mpmq] = rrk__oakl
                return bodo.hiframes.pd_series_ext.init_series(vhh__ede,
                    riv__jyjcu, adq__gtn)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ibjr__jsgrz = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                jsdmc__evblp = len(ugnm__yej)
                vhh__ede = bodo.libs.bool_arr_ext.alloc_bool_array(jsdmc__evblp
                    )
                iwg__pupa = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ibjr__jsgrz))
                opvkq__wcgwe = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                qqy__ukv = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(opvkq__wcgwe))
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    xzk__opi = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ugnm__yej[gug__mpmq]))
                    if qqy__ukv == iwg__pupa or xzk__opi == iwg__pupa:
                        rrk__oakl = wbr__qzr
                    else:
                        rrk__oakl = op(qqy__ukv, xzk__opi)
                    vhh__ede[gug__mpmq] = rrk__oakl
                return bodo.hiframes.pd_series_ext.init_series(vhh__ede,
                    riv__jyjcu, adq__gtn)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            ibjr__jsgrz = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                jsdmc__evblp = len(ugnm__yej)
                vhh__ede = bodo.libs.bool_arr_ext.alloc_bool_array(jsdmc__evblp
                    )
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    qqy__ukv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        ugnm__yej[gug__mpmq])
                    if qqy__ukv == iwg__pupa or rhs.value == iwg__pupa:
                        rrk__oakl = wbr__qzr
                    else:
                        rrk__oakl = op(qqy__ukv, rhs.value)
                    vhh__ede[gug__mpmq] = rrk__oakl
                return bodo.hiframes.pd_series_ext.init_series(vhh__ede,
                    riv__jyjcu, adq__gtn)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            ibjr__jsgrz = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                jsdmc__evblp = len(ugnm__yej)
                vhh__ede = bodo.libs.bool_arr_ext.alloc_bool_array(jsdmc__evblp
                    )
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    xzk__opi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        ugnm__yej[gug__mpmq])
                    if xzk__opi == iwg__pupa or lhs.value == iwg__pupa:
                        rrk__oakl = wbr__qzr
                    else:
                        rrk__oakl = op(lhs.value, xzk__opi)
                    vhh__ede[gug__mpmq] = rrk__oakl
                return bodo.hiframes.pd_series_ext.init_series(vhh__ede,
                    riv__jyjcu, adq__gtn)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            ibjr__jsgrz = lhs.dtype('NaT')

            def impl(lhs, rhs):
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                jsdmc__evblp = len(ugnm__yej)
                vhh__ede = bodo.libs.bool_arr_ext.alloc_bool_array(jsdmc__evblp
                    )
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                thmfl__fqds = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(rhs))
                bmcg__vkon = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    thmfl__fqds)
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    qqy__ukv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        ugnm__yej[gug__mpmq])
                    if qqy__ukv == iwg__pupa or bmcg__vkon == iwg__pupa:
                        rrk__oakl = wbr__qzr
                    else:
                        rrk__oakl = op(qqy__ukv, bmcg__vkon)
                    vhh__ede[gug__mpmq] = rrk__oakl
                return bodo.hiframes.pd_series_ext.init_series(vhh__ede,
                    riv__jyjcu, adq__gtn)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            ibjr__jsgrz = rhs.dtype('NaT')

            def impl(lhs, rhs):
                ugnm__yej = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                riv__jyjcu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                adq__gtn = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                jsdmc__evblp = len(ugnm__yej)
                vhh__ede = bodo.libs.bool_arr_ext.alloc_bool_array(jsdmc__evblp
                    )
                iwg__pupa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ibjr__jsgrz)
                thmfl__fqds = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(lhs))
                bmcg__vkon = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    thmfl__fqds)
                for gug__mpmq in numba.parfors.parfor.internal_prange(
                    jsdmc__evblp):
                    puqvk__fhlqb = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ugnm__yej[gug__mpmq]))
                    if puqvk__fhlqb == iwg__pupa or bmcg__vkon == iwg__pupa:
                        rrk__oakl = wbr__qzr
                    else:
                        rrk__oakl = op(bmcg__vkon, puqvk__fhlqb)
                    vhh__ede[gug__mpmq] = rrk__oakl
                return bodo.hiframes.pd_series_ext.init_series(vhh__ede,
                    riv__jyjcu, adq__gtn)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'tz_convert', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for rrypn__lxi in series_dt_unsupported_attrs:
        hqsp__fvunk = 'Series.dt.' + rrypn__lxi
        overload_attribute(SeriesDatetimePropertiesType, rrypn__lxi)(
            create_unsupported_overload(hqsp__fvunk))
    for czwx__bviy in series_dt_unsupported_methods:
        hqsp__fvunk = 'Series.dt.' + czwx__bviy
        overload_method(SeriesDatetimePropertiesType, czwx__bviy,
            no_unliteral=True)(create_unsupported_overload(hqsp__fvunk))


_install_series_dt_unsupported()
