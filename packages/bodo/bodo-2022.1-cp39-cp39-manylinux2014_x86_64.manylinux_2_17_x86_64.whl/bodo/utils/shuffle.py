"""
helper data structures and functions for shuffle (alltoall).
"""
import os
from collections import namedtuple
import numba
import numpy as np
from numba import generated_jit
from numba.core import types
from numba.extending import overload
import bodo
from bodo.libs.array_item_arr_ext import offset_type
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import convert_len_arr_to_offset, convert_len_arr_to_offset32, get_bit_bitmap, get_data_ptr, get_null_bitmap_ptr, get_offset_ptr, get_str_arr_item_length, num_total_chars, print_str_arr, set_bit_to, string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.timsort import getitem_arr_tup, setitem_arr_tup
from bodo.utils.utils import alloc_arr_tup, get_ctypes_ptr, numba_to_c_type
PreShuffleMeta = namedtuple('PreShuffleMeta',
    'send_counts, send_counts_char_tup, send_arr_lens_tup, send_arr_nulls_tup')
ShuffleMeta = namedtuple('ShuffleMeta',
    'send_counts, recv_counts, n_send, n_out, send_disp, recv_disp, send_disp_nulls, recv_disp_nulls, tmp_offset, send_buff_tup, out_arr_tup, send_counts_char_tup, recv_counts_char_tup, send_arr_lens_tup, send_arr_nulls_tup, send_arr_chars_tup, send_disp_char_tup, recv_disp_char_tup, tmp_offset_char_tup, send_arr_chars_arr_tup'
    )


def alloc_pre_shuffle_metadata(arr, data, n_pes, is_contig):
    return PreShuffleMeta(np.zeros(n_pes, np.int32), ())


@overload(alloc_pre_shuffle_metadata, no_unliteral=True)
def alloc_pre_shuffle_metadata_overload(key_arrs, data, n_pes, is_contig):
    fbxom__uqhw = 'def f(key_arrs, data, n_pes, is_contig):\n'
    fbxom__uqhw += '  send_counts = np.zeros(n_pes, np.int32)\n'
    ldn__jhrh = len(key_arrs.types)
    ttp__yypm = ldn__jhrh + len(data.types)
    for i, oky__dqc in enumerate(key_arrs.types + data.types):
        fbxom__uqhw += '  arr = key_arrs[{}]\n'.format(i
            ) if i < ldn__jhrh else """  arr = data[{}]
""".format(i -
            ldn__jhrh)
        if oky__dqc in [string_array_type, binary_array_type]:
            fbxom__uqhw += (
                '  send_counts_char_{} = np.zeros(n_pes, np.int32)\n'.format(i)
                )
            fbxom__uqhw += ('  send_arr_lens_{} = np.empty(0, np.uint32)\n'
                .format(i))
            fbxom__uqhw += '  if is_contig:\n'
            fbxom__uqhw += (
                '    send_arr_lens_{} = np.empty(len(arr), np.uint32)\n'.
                format(i))
        else:
            fbxom__uqhw += '  send_counts_char_{} = None\n'.format(i)
            fbxom__uqhw += '  send_arr_lens_{} = None\n'.format(i)
        if is_null_masked_type(oky__dqc):
            fbxom__uqhw += ('  send_arr_nulls_{} = np.empty(0, np.uint8)\n'
                .format(i))
            fbxom__uqhw += '  if is_contig:\n'
            fbxom__uqhw += '    n_bytes = (len(arr) + 7) >> 3\n'
            fbxom__uqhw += (
                '    send_arr_nulls_{} = np.full(n_bytes + 2 * n_pes, 255, np.uint8)\n'
                .format(i))
        else:
            fbxom__uqhw += '  send_arr_nulls_{} = None\n'.format(i)
    loi__ugh = ', '.join('send_counts_char_{}'.format(i) for i in range(
        ttp__yypm))
    dnbtc__pifif = ', '.join('send_arr_lens_{}'.format(i) for i in range(
        ttp__yypm))
    ddds__uzra = ', '.join('send_arr_nulls_{}'.format(i) for i in range(
        ttp__yypm))
    iahf__mpwg = ',' if ttp__yypm == 1 else ''
    fbxom__uqhw += (
        '  return PreShuffleMeta(send_counts, ({}{}), ({}{}), ({}{}))\n'.
        format(loi__ugh, iahf__mpwg, dnbtc__pifif, iahf__mpwg, ddds__uzra,
        iahf__mpwg))
    jyefz__moi = {}
    exec(fbxom__uqhw, {'np': np, 'PreShuffleMeta': PreShuffleMeta}, jyefz__moi)
    szoy__paxp = jyefz__moi['f']
    return szoy__paxp


def update_shuffle_meta(pre_shuffle_meta, node_id, ind, key_arrs, data,
    is_contig=True, padded_bits=0):
    pre_shuffle_meta.send_counts[node_id] += 1


@overload(update_shuffle_meta, no_unliteral=True)
def update_shuffle_meta_overload(pre_shuffle_meta, node_id, ind, key_arrs,
    data, is_contig=True, padded_bits=0):
    qksk__htc = 'BODO_DEBUG_LEVEL'
    uowqe__rhccc = 0
    try:
        uowqe__rhccc = int(os.environ[qksk__htc])
    except:
        pass
    fbxom__uqhw = """def f(pre_shuffle_meta, node_id, ind, key_arrs, data, is_contig=True, padded_bits=0):
"""
    fbxom__uqhw += '  pre_shuffle_meta.send_counts[node_id] += 1\n'
    if uowqe__rhccc > 0:
        fbxom__uqhw += ('  if pre_shuffle_meta.send_counts[node_id] >= {}:\n'
            .format(bodo.libs.distributed_api.INT_MAX))
        fbxom__uqhw += "    print('large shuffle error')\n"
    ldn__jhrh = len(key_arrs.types)
    for i, oky__dqc in enumerate(key_arrs.types + data.types):
        if oky__dqc in (string_type, string_array_type, bytes_type,
            binary_array_type):
            arr = 'key_arrs[{}]'.format(i
                ) if i < ldn__jhrh else 'data[{}]'.format(i - ldn__jhrh)
            fbxom__uqhw += ('  n_chars = get_str_arr_item_length({}, ind)\n'
                .format(arr))
            fbxom__uqhw += (
                '  pre_shuffle_meta.send_counts_char_tup[{}][node_id] += n_chars\n'
                .format(i))
            if uowqe__rhccc > 0:
                fbxom__uqhw += (
                    '  if pre_shuffle_meta.send_counts_char_tup[{}][node_id] >= {}:\n'
                    .format(i, bodo.libs.distributed_api.INT_MAX))
                fbxom__uqhw += "    print('large shuffle error')\n"
            fbxom__uqhw += '  if is_contig:\n'
            fbxom__uqhw += (
                '    pre_shuffle_meta.send_arr_lens_tup[{}][ind] = n_chars\n'
                .format(i))
        if is_null_masked_type(oky__dqc):
            fbxom__uqhw += '  if is_contig:\n'
            fbxom__uqhw += (
                '    out_bitmap = pre_shuffle_meta.send_arr_nulls_tup[{}].ctypes\n'
                .format(i))
            if i < ldn__jhrh:
                fbxom__uqhw += (
                    '    bit_val = get_mask_bit(key_arrs[{}], ind)\n'.format(i)
                    )
            else:
                fbxom__uqhw += ('    bit_val = get_mask_bit(data[{}], ind)\n'
                    .format(i - ldn__jhrh))
            fbxom__uqhw += (
                '    set_bit_to(out_bitmap, padded_bits + ind, bit_val)\n')
    jyefz__moi = {}
    exec(fbxom__uqhw, {'set_bit_to': set_bit_to, 'get_bit_bitmap':
        get_bit_bitmap, 'get_null_bitmap_ptr': get_null_bitmap_ptr,
        'getitem_arr_tup': getitem_arr_tup, 'get_mask_bit': get_mask_bit,
        'get_str_arr_item_length': get_str_arr_item_length}, jyefz__moi)
    xtyoz__woz = jyefz__moi['f']
    return xtyoz__woz


@numba.njit
def calc_disp_nulls(arr):
    lnwtg__vps = np.empty_like(arr)
    lnwtg__vps[0] = 0
    for i in range(1, len(arr)):
        lrv__wbuky = arr[i - 1] + 7 >> 3
        lnwtg__vps[i] = lnwtg__vps[i - 1] + lrv__wbuky
    return lnwtg__vps


def finalize_shuffle_meta(arrs, data, pre_shuffle_meta, n_pes, is_contig,
    init_vals=()):
    return ShuffleMeta()


@overload(finalize_shuffle_meta, no_unliteral=True)
def finalize_shuffle_meta_overload(key_arrs, data, pre_shuffle_meta, n_pes,
    is_contig, init_vals=()):
    fbxom__uqhw = (
        'def f(key_arrs, data, pre_shuffle_meta, n_pes, is_contig, init_vals=()):\n'
        )
    fbxom__uqhw += '  send_counts = pre_shuffle_meta.send_counts\n'
    fbxom__uqhw += '  recv_counts = np.empty(n_pes, np.int32)\n'
    fbxom__uqhw += '  tmp_offset = np.zeros(n_pes, np.int32)\n'
    fbxom__uqhw += (
        '  bodo.libs.distributed_api.alltoall(send_counts, recv_counts, 1)\n')
    fbxom__uqhw += '  n_out = recv_counts.sum()\n'
    fbxom__uqhw += '  n_send = send_counts.sum()\n'
    fbxom__uqhw += '  send_disp = bodo.ir.join.calc_disp(send_counts)\n'
    fbxom__uqhw += '  recv_disp = bodo.ir.join.calc_disp(recv_counts)\n'
    fbxom__uqhw += '  send_disp_nulls = calc_disp_nulls(send_counts)\n'
    fbxom__uqhw += '  recv_disp_nulls = calc_disp_nulls(recv_counts)\n'
    ldn__jhrh = len(key_arrs.types)
    ttp__yypm = len(key_arrs.types + data.types)
    for i, oky__dqc in enumerate(key_arrs.types + data.types):
        fbxom__uqhw += '  arr = key_arrs[{}]\n'.format(i
            ) if i < ldn__jhrh else """  arr = data[{}]
""".format(i -
            ldn__jhrh)
        if oky__dqc in [string_array_type, binary_array_type]:
            if oky__dqc == string_array_type:
                ttug__ykj = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
            else:
                ttug__ykj = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
            fbxom__uqhw += '  send_buff_{} = None\n'.format(i)
            fbxom__uqhw += (
                '  send_counts_char_{} = pre_shuffle_meta.send_counts_char_tup[{}]\n'
                .format(i, i))
            fbxom__uqhw += (
                '  recv_counts_char_{} = np.empty(n_pes, np.int32)\n'.format(i)
                )
            fbxom__uqhw += (
                """  bodo.libs.distributed_api.alltoall(send_counts_char_{}, recv_counts_char_{}, 1)
"""
                .format(i, i))
            fbxom__uqhw += ('  n_all_chars = recv_counts_char_{}.sum()\n'.
                format(i))
            fbxom__uqhw += '  out_arr_{} = {}(n_out, n_all_chars)\n'.format(i,
                ttug__ykj)
            fbxom__uqhw += (
                '  send_disp_char_{} = bodo.ir.join.calc_disp(send_counts_char_{})\n'
                .format(i, i))
            fbxom__uqhw += (
                '  recv_disp_char_{} = bodo.ir.join.calc_disp(recv_counts_char_{})\n'
                .format(i, i))
            fbxom__uqhw += (
                '  tmp_offset_char_{} = np.zeros(n_pes, np.int32)\n'.format(i))
            fbxom__uqhw += (
                '  send_arr_lens_{} = pre_shuffle_meta.send_arr_lens_tup[{}]\n'
                .format(i, i))
            fbxom__uqhw += ('  send_arr_chars_arr_{} = np.empty(0, np.uint8)\n'
                .format(i))
            fbxom__uqhw += (
                '  send_arr_chars_{} = get_ctypes_ptr(get_data_ptr(arr))\n'
                .format(i))
            fbxom__uqhw += '  if not is_contig:\n'
            fbxom__uqhw += (
                '    send_arr_lens_{} = np.empty(n_send, np.uint32)\n'.
                format(i))
            fbxom__uqhw += ('    s_n_all_chars = send_counts_char_{}.sum()\n'
                .format(i))
            fbxom__uqhw += (
                '    send_arr_chars_arr_{} = np.empty(s_n_all_chars, np.uint8)\n'
                .format(i))
            fbxom__uqhw += (
                '    send_arr_chars_{} = get_ctypes_ptr(send_arr_chars_arr_{}.ctypes)\n'
                .format(i, i))
        else:
            assert isinstance(oky__dqc, (types.Array, IntegerArrayType,
                BooleanArrayType, bodo.CategoricalArrayType))
            fbxom__uqhw += (
                '  out_arr_{} = bodo.utils.utils.alloc_type(n_out, arr)\n'.
                format(i))
            fbxom__uqhw += '  send_buff_{} = arr\n'.format(i)
            fbxom__uqhw += '  if not is_contig:\n'
            if i >= ldn__jhrh and init_vals != ():
                fbxom__uqhw += (
                    """    send_buff_{} = bodo.utils.utils.full_type(n_send, init_vals[{}], arr)
"""
                    .format(i, i - ldn__jhrh))
            else:
                fbxom__uqhw += (
                    '    send_buff_{} = bodo.utils.utils.alloc_type(n_send, arr)\n'
                    .format(i))
            fbxom__uqhw += '  send_counts_char_{} = None\n'.format(i)
            fbxom__uqhw += '  recv_counts_char_{} = None\n'.format(i)
            fbxom__uqhw += '  send_arr_lens_{} = None\n'.format(i)
            fbxom__uqhw += '  send_arr_chars_{} = None\n'.format(i)
            fbxom__uqhw += '  send_disp_char_{} = None\n'.format(i)
            fbxom__uqhw += '  recv_disp_char_{} = None\n'.format(i)
            fbxom__uqhw += '  tmp_offset_char_{} = None\n'.format(i)
            fbxom__uqhw += '  send_arr_chars_arr_{} = None\n'.format(i)
        if is_null_masked_type(oky__dqc):
            fbxom__uqhw += (
                '  send_arr_nulls_{} = pre_shuffle_meta.send_arr_nulls_tup[{}]\n'
                .format(i, i))
            fbxom__uqhw += '  if not is_contig:\n'
            fbxom__uqhw += '    n_bytes = (n_send + 7) >> 3\n'
            fbxom__uqhw += (
                '    send_arr_nulls_{} = np.full(n_bytes + 2 * n_pes, 255, np.uint8)\n'
                .format(i))
        else:
            fbxom__uqhw += '  send_arr_nulls_{} = None\n'.format(i)
    eev__kifx = ', '.join('send_buff_{}'.format(i) for i in range(ttp__yypm))
    pfffd__bqgci = ', '.join('out_arr_{}'.format(i) for i in range(ttp__yypm))
    hra__rgwc = ',' if ttp__yypm == 1 else ''
    fkqv__kvxxq = ', '.join('send_counts_char_{}'.format(i) for i in range(
        ttp__yypm))
    bbksi__bey = ', '.join('recv_counts_char_{}'.format(i) for i in range(
        ttp__yypm))
    gdzq__fle = ', '.join('send_arr_lens_{}'.format(i) for i in range(
        ttp__yypm))
    cgfwu__fexel = ', '.join('send_arr_nulls_{}'.format(i) for i in range(
        ttp__yypm))
    iubso__pyp = ', '.join('send_arr_chars_{}'.format(i) for i in range(
        ttp__yypm))
    tipw__qhiko = ', '.join('send_disp_char_{}'.format(i) for i in range(
        ttp__yypm))
    fog__yci = ', '.join('recv_disp_char_{}'.format(i) for i in range(
        ttp__yypm))
    hcc__xzuw = ', '.join('tmp_offset_char_{}'.format(i) for i in range(
        ttp__yypm))
    gsaq__orjwo = ', '.join('send_arr_chars_arr_{}'.format(i) for i in
        range(ttp__yypm))
    fbxom__uqhw += (
        """  return ShuffleMeta(send_counts, recv_counts, n_send, n_out, send_disp, recv_disp, send_disp_nulls, recv_disp_nulls, tmp_offset, ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), )
"""
        .format(eev__kifx, hra__rgwc, pfffd__bqgci, hra__rgwc, fkqv__kvxxq,
        hra__rgwc, bbksi__bey, hra__rgwc, gdzq__fle, hra__rgwc,
        cgfwu__fexel, hra__rgwc, iubso__pyp, hra__rgwc, tipw__qhiko,
        hra__rgwc, fog__yci, hra__rgwc, hcc__xzuw, hra__rgwc, gsaq__orjwo,
        hra__rgwc))
    jyefz__moi = {}
    exec(fbxom__uqhw, {'np': np, 'bodo': bodo, 'num_total_chars':
        num_total_chars, 'get_data_ptr': get_data_ptr, 'ShuffleMeta':
        ShuffleMeta, 'get_ctypes_ptr': get_ctypes_ptr, 'calc_disp_nulls':
        calc_disp_nulls}, jyefz__moi)
    xttx__euf = jyefz__moi['f']
    return xttx__euf


def alltoallv_tup(arrs, shuffle_meta, key_arrs):
    return arrs


@overload(alltoallv_tup, no_unliteral=True)
def alltoallv_tup_overload(arrs, meta, key_arrs):
    ldn__jhrh = len(key_arrs.types)
    fbxom__uqhw = 'def f(arrs, meta, key_arrs):\n'
    if any(is_null_masked_type(t) for t in arrs.types):
        fbxom__uqhw += (
            '  send_counts_nulls = np.empty(len(meta.send_counts), np.int32)\n'
            )
        fbxom__uqhw += '  for i in range(len(meta.send_counts)):\n'
        fbxom__uqhw += (
            '    send_counts_nulls[i] = (meta.send_counts[i] + 7) >> 3\n')
        fbxom__uqhw += (
            '  recv_counts_nulls = np.empty(len(meta.recv_counts), np.int32)\n'
            )
        fbxom__uqhw += '  for i in range(len(meta.recv_counts)):\n'
        fbxom__uqhw += (
            '    recv_counts_nulls[i] = (meta.recv_counts[i] + 7) >> 3\n')
        fbxom__uqhw += (
            '  tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)\n')
    fbxom__uqhw += '  lens = np.empty(meta.n_out, np.uint32)\n'
    for i, oky__dqc in enumerate(arrs.types):
        if isinstance(oky__dqc, (types.Array, IntegerArrayType,
            BooleanArrayType, bodo.CategoricalArrayType)):
            fbxom__uqhw += (
                """  bodo.libs.distributed_api.alltoallv(meta.send_buff_tup[{}], meta.out_arr_tup[{}], meta.send_counts,meta.recv_counts, meta.send_disp, meta.recv_disp)
"""
                .format(i, i))
        else:
            assert oky__dqc in [string_array_type, binary_array_type]
            fbxom__uqhw += (
                '  offset_ptr_{} = get_offset_ptr(meta.out_arr_tup[{}])\n'.
                format(i, i))
            if offset_type.bitwidth == 32:
                fbxom__uqhw += (
                    """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_lens_tup[{}].ctypes, offset_ptr_{}, meta.send_counts.ctypes, meta.recv_counts.ctypes, meta.send_disp.ctypes, meta.recv_disp.ctypes, int32_typ_enum)
"""
                    .format(i, i))
            else:
                fbxom__uqhw += (
                    """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_lens_tup[{}].ctypes, lens.ctypes, meta.send_counts.ctypes, meta.recv_counts.ctypes, meta.send_disp.ctypes, meta.recv_disp.ctypes, int32_typ_enum)
"""
                    .format(i))
            fbxom__uqhw += (
                """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_chars_tup[{}], get_data_ptr(meta.out_arr_tup[{}]), meta.send_counts_char_tup[{}].ctypes,meta.recv_counts_char_tup[{}].ctypes, meta.send_disp_char_tup[{}].ctypes,meta.recv_disp_char_tup[{}].ctypes, char_typ_enum)
"""
                .format(i, i, i, i, i, i))
            if offset_type.bitwidth == 32:
                fbxom__uqhw += (
                    '  convert_len_arr_to_offset32(offset_ptr_{}, meta.n_out)\n'
                    .format(i))
            else:
                fbxom__uqhw += (
                    """  convert_len_arr_to_offset(lens.ctypes, offset_ptr_{}, meta.n_out)
"""
                    .format(i))
        if is_null_masked_type(oky__dqc):
            fbxom__uqhw += (
                '  null_bitmap_ptr_{} = get_arr_null_ptr(meta.out_arr_tup[{}])\n'
                .format(i, i))
            fbxom__uqhw += (
                """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_nulls_tup[{}].ctypes, tmp_null_bytes.ctypes, send_counts_nulls.ctypes, recv_counts_nulls.ctypes, meta.send_disp_nulls.ctypes, meta.recv_disp_nulls.ctypes, char_typ_enum)
"""
                .format(i))
            fbxom__uqhw += (
                """  copy_gathered_null_bytes(null_bitmap_ptr_{}, tmp_null_bytes, recv_counts_nulls, meta.recv_counts)
"""
                .format(i))
    fbxom__uqhw += '  return ({}{})\n'.format(','.join([
        'meta.out_arr_tup[{}]'.format(i) for i in range(arrs.count)]), ',' if
        arrs.count == 1 else '')
    sscz__jubjt = np.int32(numba_to_c_type(types.int32))
    wvuw__bjhbj = np.int32(numba_to_c_type(types.uint8))
    jyefz__moi = {}
    exec(fbxom__uqhw, {'np': np, 'bodo': bodo, 'get_offset_ptr':
        get_offset_ptr, 'get_data_ptr': get_data_ptr, 'int32_typ_enum':
        sscz__jubjt, 'char_typ_enum': wvuw__bjhbj,
        'convert_len_arr_to_offset': convert_len_arr_to_offset,
        'convert_len_arr_to_offset32': convert_len_arr_to_offset32,
        'copy_gathered_null_bytes': bodo.libs.distributed_api.
        copy_gathered_null_bytes, 'get_arr_null_ptr': get_arr_null_ptr,
        'print_str_arr': print_str_arr}, jyefz__moi)
    rdt__okgs = jyefz__moi['f']
    return rdt__okgs


def shuffle_with_index_impl(key_arrs, node_arr, data):
    n_pes = bodo.libs.distributed_api.get_size()
    pre_shuffle_meta = alloc_pre_shuffle_metadata(key_arrs, data, n_pes, False)
    kvgi__myh = len(key_arrs[0])
    orig_indices = np.arange(kvgi__myh)
    sgai__yobu = np.empty(kvgi__myh, np.int32)
    for i in range(kvgi__myh):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = node_arr[i]
        sgai__yobu[i] = node_id
        update_shuffle_meta(pre_shuffle_meta, node_id, i, key_arrs, data, False
            )
    shuffle_meta = finalize_shuffle_meta(key_arrs, data, pre_shuffle_meta,
        n_pes, False)
    for i in range(kvgi__myh):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = sgai__yobu[i]
        kqn__blbj = bodo.ir.join.write_send_buff(shuffle_meta, node_id, i,
            key_arrs, data)
        orig_indices[kqn__blbj] = i
        shuffle_meta.tmp_offset[node_id] += 1
    recvs = alltoallv_tup(key_arrs + data, shuffle_meta, key_arrs)
    iusuo__puq = _get_keys_tup(recvs, key_arrs)
    giitb__zefce = _get_data_tup(recvs, key_arrs)
    return iusuo__puq, giitb__zefce, orig_indices, shuffle_meta


@generated_jit(nopython=True, cache=True)
def shuffle_with_index(key_arrs, node_arr, data):
    return shuffle_with_index_impl


@numba.njit(cache=True)
def reverse_shuffle(data, orig_indices, shuffle_meta):
    pfffd__bqgci = alloc_arr_tup(shuffle_meta.n_send, data)
    jjs__kyzzg = ShuffleMeta(shuffle_meta.recv_counts, shuffle_meta.
        send_counts, shuffle_meta.n_out, shuffle_meta.n_send, shuffle_meta.
        recv_disp, shuffle_meta.send_disp, shuffle_meta.recv_disp_nulls,
        shuffle_meta.send_disp_nulls, shuffle_meta.tmp_offset, data,
        pfffd__bqgci, shuffle_meta.recv_counts_char_tup, shuffle_meta.
        send_counts_char_tup, shuffle_meta.send_arr_lens_tup, shuffle_meta.
        send_arr_nulls_tup, shuffle_meta.send_arr_chars_tup, shuffle_meta.
        recv_disp_char_tup, shuffle_meta.send_disp_char_tup, shuffle_meta.
        tmp_offset_char_tup, shuffle_meta.send_arr_chars_arr_tup)
    pfffd__bqgci = alltoallv_tup(data, jjs__kyzzg, ())
    wjzjs__nqb = alloc_arr_tup(shuffle_meta.n_send, data)
    for i in range(len(orig_indices)):
        setitem_arr_tup(wjzjs__nqb, orig_indices[i], getitem_arr_tup(
            pfffd__bqgci, i))
    return wjzjs__nqb


def _get_keys_tup(recvs, key_arrs):
    return recvs[:len(key_arrs)]


@overload(_get_keys_tup, no_unliteral=True)
def _get_keys_tup_overload(recvs, key_arrs):
    ldn__jhrh = len(key_arrs.types)
    fbxom__uqhw = 'def f(recvs, key_arrs):\n'
    emior__crdw = ','.join('recvs[{}]'.format(i) for i in range(ldn__jhrh))
    fbxom__uqhw += '  return ({}{})\n'.format(emior__crdw, ',' if ldn__jhrh ==
        1 else '')
    jyefz__moi = {}
    exec(fbxom__uqhw, {}, jyefz__moi)
    vsa__akmu = jyefz__moi['f']
    return vsa__akmu


def _get_data_tup(recvs, key_arrs):
    return recvs[len(key_arrs):]


@overload(_get_data_tup, no_unliteral=True)
def _get_data_tup_overload(recvs, key_arrs):
    ldn__jhrh = len(key_arrs.types)
    ttp__yypm = len(recvs.types)
    mwmfs__tof = ttp__yypm - ldn__jhrh
    fbxom__uqhw = 'def f(recvs, key_arrs):\n'
    emior__crdw = ','.join('recvs[{}]'.format(i) for i in range(ldn__jhrh,
        ttp__yypm))
    fbxom__uqhw += '  return ({}{})\n'.format(emior__crdw, ',' if 
        mwmfs__tof == 1 else '')
    jyefz__moi = {}
    exec(fbxom__uqhw, {}, jyefz__moi)
    vsa__akmu = jyefz__moi['f']
    return vsa__akmu


def getitem_arr_tup_single(arrs, i):
    return arrs[0][i]


@overload(getitem_arr_tup_single, no_unliteral=True)
def getitem_arr_tup_single_overload(arrs, i):
    if len(arrs.types) == 1:
        return lambda arrs, i: arrs[0][i]
    return lambda arrs, i: getitem_arr_tup(arrs, i)


def val_to_tup(val):
    return val,


@overload(val_to_tup, no_unliteral=True)
def val_to_tup_overload(val):
    if isinstance(val, types.BaseTuple):
        return lambda val: val
    return lambda val: (val,)


def is_null_masked_type(t):
    return t in (string_type, string_array_type, bytes_type,
        binary_array_type, boolean_array) or isinstance(t, IntegerArrayType)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_mask_bit(arr, i):
    if arr in [string_array_type, binary_array_type]:
        return lambda arr, i: get_bit_bitmap(get_null_bitmap_ptr(arr), i)
    assert isinstance(arr, IntegerArrayType) or arr == boolean_array
    return lambda arr, i: bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr.
        _null_bitmap, i)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_arr_null_ptr(arr):
    if arr in [string_array_type, binary_array_type]:
        return lambda arr: get_null_bitmap_ptr(arr)
    assert isinstance(arr, IntegerArrayType) or arr == boolean_array
    return lambda arr: arr._null_bitmap.ctypes
