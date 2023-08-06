"""
Support for Series.str methods
"""
import operator
import re
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_index_ext import StringIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.split_impl import get_split_view_data_ptr, get_split_view_index, string_array_split_view_type
from bodo.libs.array import get_search_regex
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.str_arr_ext import get_utf8_size, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import str_findall_count
from bodo.utils.typing import BodoError, create_unsupported_overload, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_str_len, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, raise_bodo_error


class SeriesStrMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        uoopt__bqs = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(uoopt__bqs)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wiwqy__xtfa = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, wiwqy__xtfa)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        yoz__pbbo, = args
        jjp__hdw = signature.return_type
        agx__fcna = cgutils.create_struct_proxy(jjp__hdw)(context, builder)
        agx__fcna.obj = yoz__pbbo
        context.nrt.incref(builder, signature.args[0], yoz__pbbo)
        return agx__fcna._getvalue()
    return SeriesStrMethodType(obj)(obj), codegen


def str_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.UnicodeType) and not is_overload_constant_str(
        arg):
        raise_bodo_error(
            "Series.str.{}(): parameter '{}' expected a string object, not {}"
            .format(func_name, arg_name, arg))


def int_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.Integer) and not is_overload_constant_int(arg
        ):
        raise BodoError(
            "Series.str.{}(): parameter '{}' expected an int object, not {}"
            .format(func_name, arg_name, arg))


def not_supported_arg_check(func_name, arg_name, arg, defval):
    if arg_name == 'na':
        if not isinstance(arg, types.Omitted) and (not isinstance(arg,
            float) or not np.isnan(arg)):
            raise BodoError(
                "Series.str.{}(): parameter '{}' is not supported, default: np.nan"
                .format(func_name, arg_name))
    elif not isinstance(arg, types.Omitted) and arg != defval:
        raise BodoError(
            "Series.str.{}(): parameter '{}' is not supported, default: {}"
            .format(func_name, arg_name, defval))


def common_validate_padding(func_name, width, fillchar):
    if is_overload_constant_str(fillchar):
        if get_overload_const_str_len(fillchar) != 1:
            raise BodoError(
                'Series.str.{}(): fillchar must be a character, not str'.
                format(func_name))
    elif not isinstance(fillchar, types.UnicodeType):
        raise BodoError('Series.str.{}(): fillchar must be a character, not {}'
            .format(func_name, fillchar))
    int_arg_check(func_name, 'width', width)


@overload_attribute(SeriesType, 'str')
def overload_series_str(S):
    if not isinstance(S, SeriesType) or not (S.data in (string_array_type,
        string_array_split_view_type) or isinstance(S.data, ArrayItemArrayType)
        ):
        raise_bodo_error(
            'Series.str: input should be a series of string or arrays')
    return lambda S: bodo.hiframes.series_str_impl.init_series_str_method(S)


@overload_method(SeriesStrMethodType, 'len', inline='always', no_unliteral=True
    )
def overload_str_method_len(S_str):

    def impl(S_str):
        S = S_str._obj
        cay__tarw = bodo.hiframes.pd_series_ext.get_series_data(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(cay__tarw)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(cay__tarw, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = len(cay__tarw[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'split', inline='always',
    no_unliteral=True)
def overload_str_method_split(S_str, pat=None, n=-1, expand=False):
    if not is_overload_none(pat):
        str_arg_check('split', 'pat', pat)
    int_arg_check('split', 'n', n)
    not_supported_arg_check('split', 'expand', expand, False)
    if is_overload_constant_str(pat) and len(get_overload_const_str(pat)
        ) == 1 and get_overload_const_str(pat).isascii(
        ) and is_overload_constant_int(n) and get_overload_const_int(n) == -1:

        def _str_split_view_impl(S_str, pat=None, n=-1, expand=False):
            S = S_str._obj
            cay__tarw = bodo.hiframes.pd_series_ext.get_series_data(S)
            rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
            uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(cay__tarw,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rhay__uju, uoopt__bqs)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        cay__tarw = bodo.hiframes.pd_series_ext.get_series_data(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(cay__tarw, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    xml__jvqol = S_str.stype.data
    if (xml__jvqol != string_array_split_view_type and xml__jvqol !=
        string_array_type) and not isinstance(xml__jvqol, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(xml__jvqol, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            cay__tarw = bodo.hiframes.pd_series_ext.get_series_data(S)
            rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
            uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(cay__tarw, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rhay__uju, uoopt__bqs)
        return _str_get_array_impl
    if xml__jvqol == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            cay__tarw = bodo.hiframes.pd_series_ext.get_series_data(S)
            rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
            uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(cay__tarw)
            adf__rvoq = 0
            for yoiw__fadw in numba.parfors.parfor.internal_prange(n):
                szbfh__ikoop, szbfh__ikoop, gwb__eco = get_split_view_index(
                    cay__tarw, yoiw__fadw, i)
                adf__rvoq += gwb__eco
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, adf__rvoq)
            for cod__sjn in numba.parfors.parfor.internal_prange(n):
                mved__nyd, adflt__pfpj, gwb__eco = get_split_view_index(
                    cay__tarw, cod__sjn, i)
                if mved__nyd == 0:
                    bodo.libs.array_kernels.setna(out_arr, cod__sjn)
                    ejncz__zxl = get_split_view_data_ptr(cay__tarw, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr, cod__sjn)
                    ejncz__zxl = get_split_view_data_ptr(cay__tarw, adflt__pfpj
                        )
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr, cod__sjn,
                    ejncz__zxl, gwb__eco)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rhay__uju, uoopt__bqs)
        return _str_get_split_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        cay__tarw = bodo.hiframes.pd_series_ext.get_series_data(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(cay__tarw)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for cod__sjn in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(cay__tarw, cod__sjn) or not len(
                cay__tarw[cod__sjn]) > i >= -len(cay__tarw[cod__sjn]):
                out_arr[cod__sjn] = ''
                bodo.libs.array_kernels.setna(out_arr, cod__sjn)
            else:
                out_arr[cod__sjn] = cay__tarw[cod__sjn][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    xml__jvqol = S_str.stype.data
    if (xml__jvqol != string_array_split_view_type and xml__jvqol !=
        ArrayItemArrayType(string_array_type) and xml__jvqol !=
        string_array_type):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(tftf__qrfs)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for cod__sjn in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(tftf__qrfs, cod__sjn):
                out_arr[cod__sjn] = ''
                bodo.libs.array_kernels.setna(out_arr, cod__sjn)
            else:
                eko__zlefu = tftf__qrfs[cod__sjn]
                out_arr[cod__sjn] = sep.join(eko__zlefu)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'replace', inline='always',
    no_unliteral=True)
def overload_str_method_replace(S_str, pat, repl, n=-1, case=None, flags=0,
    regex=True):
    not_supported_arg_check('replace', 'n', n, -1)
    not_supported_arg_check('replace', 'case', case, None)
    str_arg_check('replace', 'pat', pat)
    str_arg_check('replace', 'repl', repl)
    int_arg_check('replace', 'flags', flags)
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            cay__tarw = bodo.hiframes.pd_series_ext.get_series_data(S)
            rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
            uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            wwfzf__bxw = re.compile(pat, flags)
            sevsa__cxdm = len(cay__tarw)
            out_arr = pre_alloc_string_array(sevsa__cxdm, -1)
            for cod__sjn in numba.parfors.parfor.internal_prange(sevsa__cxdm):
                if bodo.libs.array_kernels.isna(cay__tarw, cod__sjn):
                    out_arr[cod__sjn] = ''
                    bodo.libs.array_kernels.setna(out_arr, cod__sjn)
                    continue
                out_arr[cod__sjn] = wwfzf__bxw.sub(repl, cay__tarw[cod__sjn])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rhay__uju, uoopt__bqs)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        cay__tarw = bodo.hiframes.pd_series_ext.get_series_data(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(cay__tarw)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(sevsa__cxdm, -1)
        for cod__sjn in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(cay__tarw, cod__sjn):
                out_arr[cod__sjn] = ''
                bodo.libs.array_kernels.setna(out_arr, cod__sjn)
                continue
            out_arr[cod__sjn] = cay__tarw[cod__sjn].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return _str_replace_noregex_impl


@numba.njit
def series_contains_regex(S, pat, case, flags, na, regex):
    with numba.objmode(out_arr=bodo.boolean_array):
        out_arr = S.array._str_contains(pat, case, flags, na, regex)
    return out_arr


def is_regex_unsupported(pat):
    vxng__njy = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(ywcw__ngfrs in pat) for ywcw__ngfrs in vxng__njy])
    else:
        return True


@overload_method(SeriesStrMethodType, 'contains', no_unliteral=True)
def overload_str_method_contains(S_str, pat, case=True, flags=0, na=np.nan,
    regex=True):
    not_supported_arg_check('contains', 'na', na, np.nan)
    str_arg_check('contains', 'pat', pat)
    int_arg_check('contains', 'flags', flags)
    if not is_overload_constant_bool(regex):
        raise BodoError(
            "Series.str.contains(): 'regex' argument should be a constant boolean"
            )
    if not is_overload_constant_bool(case):
        raise BodoError(
            "Series.str.contains(): 'case' argument should be a constant boolean"
            )
    urovv__poxzo = re.IGNORECASE.value
    ykp__bqest = 'def impl(\n'
    ykp__bqest += '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n'
    ykp__bqest += '):\n'
    ykp__bqest += '  S = S_str._obj\n'
    ykp__bqest += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ykp__bqest += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    ykp__bqest += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    ykp__bqest += '  l = len(arr)\n'
    ykp__bqest += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            ykp__bqest += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            ykp__bqest += """  get_search_regex(arr, case, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    else:
        ykp__bqest += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            ykp__bqest += '  upper_pat = pat.upper()\n'
        ykp__bqest += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        ykp__bqest += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        ykp__bqest += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        ykp__bqest += '      else: \n'
        if is_overload_true(case):
            ykp__bqest += '          out_arr[i] = pat in arr[i]\n'
        else:
            ykp__bqest += (
                '          out_arr[i] = upper_pat in arr[i].upper()\n')
    ykp__bqest += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    mdc__ecr = {}
    exec(ykp__bqest, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': urovv__poxzo, 'get_search_regex':
        get_search_regex}, mdc__ecr)
    impl = mdc__ecr['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        wwfzf__bxw = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(sevsa__cxdm, np.int64)
        for i in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(wwfzf__bxw, tftf__qrfs[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'find', inline='always', no_unliteral
    =True)
def overload_str_method_find(S_str, sub, start=0, end=None):
    str_arg_check('find', 'sub', sub)
    int_arg_check('find', 'start', start)
    if not is_overload_none(end):
        int_arg_check('find', 'end', end)

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(sevsa__cxdm, np.int64)
        for i in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = tftf__qrfs[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'rfind', inline='always',
    no_unliteral=True)
def overload_str_method_rfind(S_str, sub, start=0, end=None):
    str_arg_check('rfind', 'sub', sub)
    if start != 0:
        int_arg_check('rfind', 'start', start)
    if not is_overload_none(end):
        int_arg_check('rfind', 'end', end)

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(sevsa__cxdm, np.int64)
        for i in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = tftf__qrfs[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'center', inline='always',
    no_unliteral=True)
def overload_str_method_center(S_str, width, fillchar=' '):
    common_validate_padding('center', width, fillchar)

    def impl(S_str, width, fillchar=' '):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(sevsa__cxdm, -1)
        for cod__sjn in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, cod__sjn):
                out_arr[cod__sjn] = ''
                bodo.libs.array_kernels.setna(out_arr, cod__sjn)
            else:
                out_arr[cod__sjn] = tftf__qrfs[cod__sjn].center(width, fillchar
                    )
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'slice_replace', inline='always',
    no_unliteral=True)
def overload_str_method_slice_replace(S_str, start=0, stop=None, repl=''):
    int_arg_check('slice_replace', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice_replace', 'stop', stop)
    str_arg_check('slice_replace', 'repl', repl)

    def impl(S_str, start=0, stop=None, repl=''):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(sevsa__cxdm, -1)
        for cod__sjn in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, cod__sjn):
                bodo.libs.array_kernels.setna(out_arr, cod__sjn)
            else:
                if stop is not None:
                    adb__bsq = tftf__qrfs[cod__sjn][stop:]
                else:
                    adb__bsq = ''
                out_arr[cod__sjn] = tftf__qrfs[cod__sjn][:start
                    ] + repl + adb__bsq
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):

        def impl(S_str, repeats):
            S = S_str._obj
            tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
            uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
            rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            sevsa__cxdm = len(tftf__qrfs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(sevsa__cxdm,
                -1)
            for cod__sjn in numba.parfors.parfor.internal_prange(sevsa__cxdm):
                if bodo.libs.array_kernels.isna(tftf__qrfs, cod__sjn):
                    bodo.libs.array_kernels.setna(out_arr, cod__sjn)
                else:
                    out_arr[cod__sjn] = tftf__qrfs[cod__sjn] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rhay__uju, uoopt__bqs)
        return impl
    elif is_overload_constant_list(repeats):
        wba__hyjs = get_overload_const_list(repeats)
        wye__sacm = all([isinstance(uzn__yqmf, int) for uzn__yqmf in wba__hyjs]
            )
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        wye__sacm = True
    else:
        wye__sacm = False
    if wye__sacm:

        def impl(S_str, repeats):
            S = S_str._obj
            tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
            uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
            rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
            jmsa__pvy = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            sevsa__cxdm = len(tftf__qrfs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(sevsa__cxdm,
                -1)
            for cod__sjn in numba.parfors.parfor.internal_prange(sevsa__cxdm):
                if bodo.libs.array_kernels.isna(tftf__qrfs, cod__sjn):
                    bodo.libs.array_kernels.setna(out_arr, cod__sjn)
                else:
                    out_arr[cod__sjn] = tftf__qrfs[cod__sjn] * jmsa__pvy[
                        cod__sjn]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rhay__uju, uoopt__bqs)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


@overload_method(SeriesStrMethodType, 'ljust', inline='always',
    no_unliteral=True)
def overload_str_method_ljust(S_str, width, fillchar=' '):
    common_validate_padding('ljust', width, fillchar)

    def impl(S_str, width, fillchar=' '):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(sevsa__cxdm, -1)
        for cod__sjn in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, cod__sjn):
                out_arr[cod__sjn] = ''
                bodo.libs.array_kernels.setna(out_arr, cod__sjn)
            else:
                out_arr[cod__sjn] = tftf__qrfs[cod__sjn].ljust(width, fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'rjust', inline='always',
    no_unliteral=True)
def overload_str_method_rjust(S_str, width, fillchar=' '):
    common_validate_padding('rjust', width, fillchar)

    def impl(S_str, width, fillchar=' '):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(sevsa__cxdm, -1)
        for cod__sjn in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, cod__sjn):
                out_arr[cod__sjn] = ''
                bodo.libs.array_kernels.setna(out_arr, cod__sjn)
            else:
                out_arr[cod__sjn] = tftf__qrfs[cod__sjn].rjust(width, fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'pad', no_unliteral=True)
def overload_str_method_pad(S_str, width, side='left', fillchar=' '):
    common_validate_padding('pad', width, fillchar)
    if is_overload_constant_str(side):
        if get_overload_const_str(side) not in ['left', 'right', 'both']:
            raise BodoError('Series.str.pad(): Invalid Side')
    else:
        raise BodoError('Series.str.pad(): Invalid Side')

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(sevsa__cxdm, -1)
        for cod__sjn in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, cod__sjn):
                out_arr[cod__sjn] = ''
                bodo.libs.array_kernels.setna(out_arr, cod__sjn)
            elif side == 'left':
                out_arr[cod__sjn] = tftf__qrfs[cod__sjn].rjust(width, fillchar)
            elif side == 'right':
                out_arr[cod__sjn] = tftf__qrfs[cod__sjn].ljust(width, fillchar)
            elif side == 'both':
                out_arr[cod__sjn] = tftf__qrfs[cod__sjn].center(width, fillchar
                    )
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)

    def impl(S_str, width):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(sevsa__cxdm, -1)
        for cod__sjn in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, cod__sjn):
                out_arr[cod__sjn] = ''
                bodo.libs.array_kernels.setna(out_arr, cod__sjn)
            else:
                out_arr[cod__sjn] = tftf__qrfs[cod__sjn].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'slice', no_unliteral=True)
def overload_str_method_slice(S_str, start=None, stop=None, step=None):
    if not is_overload_none(start):
        int_arg_check('slice', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice', 'stop', stop)
    if not is_overload_none(step):
        int_arg_check('slice', 'step', step)

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(sevsa__cxdm, -1)
        for cod__sjn in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, cod__sjn):
                out_arr[cod__sjn] = ''
                bodo.libs.array_kernels.setna(out_arr, cod__sjn)
            else:
                out_arr[cod__sjn] = tftf__qrfs[cod__sjn][start:stop:step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(sevsa__cxdm)
        for i in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = tftf__qrfs[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        tftf__qrfs = bodo.hiframes.pd_series_ext.get_series_data(S)
        uoopt__bqs = bodo.hiframes.pd_series_ext.get_series_name(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        sevsa__cxdm = len(tftf__qrfs)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(sevsa__cxdm)
        for i in numba.parfors.parfor.internal_prange(sevsa__cxdm):
            if bodo.libs.array_kernels.isna(tftf__qrfs, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = tftf__qrfs[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, rhay__uju,
            uoopt__bqs)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_str_method_getitem(S_str, ind):
    if not isinstance(S_str, SeriesStrMethodType):
        return
    if not isinstance(types.unliteral(ind), (types.SliceType, types.Integer)):
        raise BodoError(
            'index input to Series.str[] should be a slice or an integer')
    if isinstance(ind, types.SliceType):
        return lambda S_str, ind: S_str.slice(ind.start, ind.stop, ind.step)
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda S_str, ind: S_str.get(ind)


@overload_method(SeriesStrMethodType, 'extract', inline='always',
    no_unliteral=True)
def overload_str_method_extract(S_str, pat, flags=0, expand=True):
    if not is_overload_constant_bool(expand):
        raise BodoError(
            "Series.str.extract(): 'expand' argument should be a constant bool"
            )
    dhg__kanb, regex = _get_column_names_from_regex(pat, flags, 'extract')
    vudg__qtwvc = len(dhg__kanb)
    ykp__bqest = 'def impl(S_str, pat, flags=0, expand=True):\n'
    ykp__bqest += '  regex = re.compile(pat, flags=flags)\n'
    ykp__bqest += '  S = S_str._obj\n'
    ykp__bqest += (
        '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ykp__bqest += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    ykp__bqest += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    ykp__bqest += '  numba.parfors.parfor.init_prange()\n'
    ykp__bqest += '  n = len(str_arr)\n'
    for i in range(vudg__qtwvc):
        ykp__bqest += (
            '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
            .format(i))
    ykp__bqest += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    ykp__bqest += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
    for i in range(vudg__qtwvc):
        ykp__bqest += "          out_arr_{}[j] = ''\n".format(i)
        ykp__bqest += (
            '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
            format(i))
    ykp__bqest += '      else:\n'
    ykp__bqest += '          m = regex.search(str_arr[j])\n'
    ykp__bqest += '          if m:\n'
    ykp__bqest += '            g = m.groups()\n'
    for i in range(vudg__qtwvc):
        ykp__bqest += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
    ykp__bqest += '          else:\n'
    for i in range(vudg__qtwvc):
        ykp__bqest += "            out_arr_{}[j] = ''\n".format(i)
        ykp__bqest += (
            '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
            format(i))
    if is_overload_false(expand) and regex.groups == 1:
        uoopt__bqs = "'{}'".format(list(regex.groupindex.keys()).pop()) if len(
            regex.groupindex.keys()) > 0 else 'name'
        ykp__bqest += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(uoopt__bqs))
        mdc__ecr = {}
        exec(ykp__bqest, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, mdc__ecr)
        impl = mdc__ecr['impl']
        return impl
    drrqf__xdyq = ', '.join('out_arr_{}'.format(i) for i in range(vudg__qtwvc))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(ykp__bqest, dhg__kanb,
        drrqf__xdyq, 'index', extra_globals={'get_utf8_size': get_utf8_size,
        're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    dhg__kanb, szbfh__ikoop = _get_column_names_from_regex(pat, flags,
        'extractall')
    vudg__qtwvc = len(dhg__kanb)
    wzrx__owgh = isinstance(S_str.stype.index, StringIndexType)
    ykp__bqest = 'def impl(S_str, pat, flags=0):\n'
    ykp__bqest += '  regex = re.compile(pat, flags=flags)\n'
    ykp__bqest += '  S = S_str._obj\n'
    ykp__bqest += (
        '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ykp__bqest += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    ykp__bqest += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    ykp__bqest += '  index_arr = bodo.utils.conversion.index_to_array(index)\n'
    ykp__bqest += (
        '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n')
    ykp__bqest += '  numba.parfors.parfor.init_prange()\n'
    ykp__bqest += '  n = len(str_arr)\n'
    ykp__bqest += '  out_n_l = [0]\n'
    for i in range(vudg__qtwvc):
        ykp__bqest += '  num_chars_{} = 0\n'.format(i)
    if wzrx__owgh:
        ykp__bqest += '  index_num_chars = 0\n'
    ykp__bqest += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    if wzrx__owgh:
        ykp__bqest += '      index_num_chars += get_utf8_size(index_arr[i])\n'
    ykp__bqest += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
    ykp__bqest += '          continue\n'
    ykp__bqest += '      m = regex.findall(str_arr[i])\n'
    ykp__bqest += '      out_n_l[0] += len(m)\n'
    for i in range(vudg__qtwvc):
        ykp__bqest += '      l_{} = 0\n'.format(i)
    ykp__bqest += '      for s in m:\n'
    for i in range(vudg__qtwvc):
        ykp__bqest += '        l_{} += get_utf8_size(s{})\n'.format(i, 
            '[{}]'.format(i) if vudg__qtwvc > 1 else '')
    for i in range(vudg__qtwvc):
        ykp__bqest += '      num_chars_{0} += l_{0}\n'.format(i)
    ykp__bqest += (
        '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
        )
    for i in range(vudg__qtwvc):
        ykp__bqest += (
            """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
            .format(i))
    if wzrx__owgh:
        ykp__bqest += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
    else:
        ykp__bqest += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
    ykp__bqest += '  out_match_arr = np.empty(out_n, np.int64)\n'
    ykp__bqest += '  out_ind = 0\n'
    ykp__bqest += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    ykp__bqest += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
    ykp__bqest += '          continue\n'
    ykp__bqest += '      m = regex.findall(str_arr[j])\n'
    ykp__bqest += '      for k, s in enumerate(m):\n'
    for i in range(vudg__qtwvc):
        ykp__bqest += (
            '        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})\n'
            .format(i, '[{}]'.format(i) if vudg__qtwvc > 1 else ''))
    ykp__bqest += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
    ykp__bqest += (
        '        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)\n'
        )
    ykp__bqest += '        out_ind += 1\n'
    ykp__bqest += (
        '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n')
    ykp__bqest += "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n"
    drrqf__xdyq = ', '.join('out_arr_{}'.format(i) for i in range(vudg__qtwvc))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(ykp__bqest, dhg__kanb,
        drrqf__xdyq, 'out_index', extra_globals={'get_utf8_size':
        get_utf8_size, 're': re})
    return impl


def _get_column_names_from_regex(pat, flags, func_name):
    if not is_overload_constant_str(pat):
        raise BodoError(
            "Series.str.{}(): 'pat' argument should be a constant string".
            format(func_name))
    if not is_overload_constant_int(flags):
        raise BodoError(
            "Series.str.{}(): 'flags' argument should be a constant int".
            format(func_name))
    pat = get_overload_const_str(pat)
    flags = get_overload_const_int(flags)
    regex = re.compile(pat, flags=flags)
    if regex.groups == 0:
        raise BodoError(
            'Series.str.{}(): pattern {} contains no capture groups'.format
            (func_name, pat))
    fbn__pao = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    dhg__kanb = [fbn__pao.get(1 + i, i) for i in range(regex.groups)]
    return dhg__kanb, regex


def create_str2str_methods_overload(func_name):
    if func_name in ['lstrip', 'rstrip', 'strip']:
        ykp__bqest = 'def f(S_str, to_strip=None):\n'
    else:
        ykp__bqest = 'def f(S_str):\n'
    ykp__bqest += '    S = S_str._obj\n'
    ykp__bqest += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ykp__bqest += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ykp__bqest += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    ykp__bqest += '    numba.parfors.parfor.init_prange()\n'
    ykp__bqest += '    n = len(str_arr)\n'
    if func_name in ('capitalize', 'lower', 'swapcase', 'title', 'upper'):
        ykp__bqest += '    num_chars = num_total_chars(str_arr)\n'
    else:
        ykp__bqest += '    num_chars = -1\n'
    ykp__bqest += (
        '    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)\n'
        )
    ykp__bqest += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    ykp__bqest += '        if bodo.libs.array_kernels.isna(str_arr, j):\n'
    ykp__bqest += '            out_arr[j] = ""\n'
    ykp__bqest += '            bodo.libs.array_kernels.setna(out_arr, j)\n'
    ykp__bqest += '        else:\n'
    if func_name in ['lstrip', 'rstrip', 'strip']:
        ykp__bqest += ('            out_arr[j] = str_arr[j].{}(to_strip)\n'
            .format(func_name))
    else:
        ykp__bqest += '            out_arr[j] = str_arr[j].{}()\n'.format(
            func_name)
    ykp__bqest += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    mdc__ecr = {}
    exec(ykp__bqest, {'bodo': bodo, 'numba': numba, 'num_total_chars': bodo
        .libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size}, mdc__ecr)
    qwkjj__nxgqc = mdc__ecr['f']
    if func_name in ['lstrip', 'rstrip', 'strip']:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            return qwkjj__nxgqc
        return overload_strip_method
    else:

        def overload_str2str_methods(S_str):
            return qwkjj__nxgqc
        return overload_str2str_methods


def create_str2bool_methods_overload(func_name):

    def overload_str2bool_methods(S_str):
        ykp__bqest = 'def f(S_str):\n'
        ykp__bqest += '    S = S_str._obj\n'
        ykp__bqest += (
            '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ykp__bqest += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ykp__bqest += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ykp__bqest += '    numba.parfors.parfor.init_prange()\n'
        ykp__bqest += '    l = len(str_arr)\n'
        ykp__bqest += (
            '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        ykp__bqest += '    for i in numba.parfors.parfor.internal_prange(l):\n'
        ykp__bqest += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
        ykp__bqest += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        ykp__bqest += '        else:\n'
        ykp__bqest += ('            out_arr[i] = np.bool_(str_arr[i].{}())\n'
            .format(func_name))
        ykp__bqest += '    return bodo.hiframes.pd_series_ext.init_series(\n'
        ykp__bqest += '      out_arr,index, name)\n'
        mdc__ecr = {}
        exec(ykp__bqest, {'bodo': bodo, 'numba': numba, 'np': np}, mdc__ecr)
        qwkjj__nxgqc = mdc__ecr['f']
        return qwkjj__nxgqc
    return overload_str2bool_methods


def _install_str2str_methods():
    for fozg__xybhy in bodo.hiframes.pd_series_ext.str2str_methods:
        cng__isdj = create_str2str_methods_overload(fozg__xybhy)
        overload_method(SeriesStrMethodType, fozg__xybhy, inline='always',
            no_unliteral=True)(cng__isdj)


def _install_str2bool_methods():
    for fozg__xybhy in bodo.hiframes.pd_series_ext.str2bool_methods:
        cng__isdj = create_str2bool_methods_overload(fozg__xybhy)
        overload_method(SeriesStrMethodType, fozg__xybhy, inline='always',
            no_unliteral=True)(cng__isdj)


_install_str2str_methods()
_install_str2bool_methods()


@overload_attribute(SeriesType, 'cat')
def overload_series_cat(s):
    if not isinstance(s.dtype, bodo.hiframes.pd_categorical_ext.
        PDCategoricalDtype):
        raise BodoError('Can only use .cat accessor with categorical values.')
    return lambda s: bodo.hiframes.series_str_impl.init_series_cat_method(s)


class SeriesCatMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        uoopt__bqs = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(uoopt__bqs)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wiwqy__xtfa = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, wiwqy__xtfa)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        yoz__pbbo, = args
        uwxac__sku = signature.return_type
        kpkdy__ncuj = cgutils.create_struct_proxy(uwxac__sku)(context, builder)
        kpkdy__ncuj.obj = yoz__pbbo
        context.nrt.incref(builder, signature.args[0], yoz__pbbo)
        return kpkdy__ncuj._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        cay__tarw = bodo.hiframes.pd_series_ext.get_series_data(S)
        rhay__uju = bodo.hiframes.pd_series_ext.get_series_index(S)
        uoopt__bqs = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(cay__tarw),
            rhay__uju, uoopt__bqs)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for gju__wzfup in unsupported_cat_attrs:
        hcnjw__arzl = 'Series.cat.' + gju__wzfup
        overload_attribute(SeriesCatMethodType, gju__wzfup)(
            create_unsupported_overload(hcnjw__arzl))
    for ltrh__yyeh in unsupported_cat_methods:
        hcnjw__arzl = 'Series.cat.' + ltrh__yyeh
        overload_method(SeriesCatMethodType, ltrh__yyeh)(
            create_unsupported_overload(hcnjw__arzl))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'cat', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for ltrh__yyeh in unsupported_str_methods:
        hcnjw__arzl = 'Series.str.' + ltrh__yyeh
        overload_method(SeriesStrMethodType, ltrh__yyeh)(
            create_unsupported_overload(hcnjw__arzl))


_install_strseries_unsupported()
