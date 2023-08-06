"""IR node for the join and merge"""
from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba import generated_jit
from numba.core import cgutils, ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes, replace_vars_inner, visit_vars_inner
from numba.extending import intrinsic, overload
import bodo
from bodo.libs.array import arr_info_list_to_table, array_to_info, compute_node_partition_by_hash, delete_table, delete_table_decref_arrays, hash_join_table, info_from_table, info_to_array
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import copy_str_arr_slice, cp_str_list_to_array, get_bit_bitmap, get_null_bitmap_ptr, get_str_arr_item_length, get_str_arr_item_ptr, get_utf8_size, getitem_str_offset, num_total_chars, pre_alloc_string_array, set_bit_to, str_copy_ptr, string_array_type, to_list_if_immutable_arr
from bodo.libs.str_ext import string_type
from bodo.libs.timsort import getitem_arr_tup, setitem_arr_tup
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.shuffle import _get_data_tup, _get_keys_tup, alloc_pre_shuffle_metadata, alltoallv_tup, finalize_shuffle_meta, getitem_arr_tup_single, update_shuffle_meta
from bodo.utils.typing import BodoError, dtype_to_array_type, find_common_np_dtype, is_dtype_nullable, is_nullable_type, to_nullable_type
from bodo.utils.utils import alloc_arr_tup, debug_prints, is_null_pointer
join_gen_cond_cfunc = {}
join_gen_cond_cfunc_addr = {}


@intrinsic
def add_join_gen_cond_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        djde__bmjs = func.signature
        ciusd__xrqs = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        zfx__udz = cgutils.get_or_insert_function(builder.module,
            ciusd__xrqs, sym._literal_value)
        builder.call(zfx__udz, [context.get_constant_null(djde__bmjs.args[0
            ]), context.get_constant_null(djde__bmjs.args[1]), context.
            get_constant_null(djde__bmjs.args[2]), context.
            get_constant_null(djde__bmjs.args[3]), context.
            get_constant_null(djde__bmjs.args[4]), context.
            get_constant_null(djde__bmjs.args[5]), context.get_constant(
            types.int64, 0), context.get_constant(types.int64, 0)])
        context.add_linking_libs([join_gen_cond_cfunc[sym._literal_value].
            _library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_join_cond_addr(name):
    with numba.objmode(addr='int64'):
        addr = join_gen_cond_cfunc_addr[name]
    return addr


class Join(ir.Stmt):

    def __init__(self, df_out, left_df, right_df, left_keys, right_keys,
        out_data_vars, left_vars, right_vars, how, suffix_x, suffix_y, loc,
        is_left, is_right, is_join, left_index, right_index, indicator,
        is_na_equal, gen_cond_expr):
        self.df_out = df_out
        self.left_df = left_df
        self.right_df = right_df
        self.left_keys = left_keys
        self.right_keys = right_keys
        self.out_data_vars = out_data_vars
        self.left_vars = left_vars
        self.right_vars = right_vars
        self.how = how
        self.suffix_x = suffix_x
        self.suffix_y = suffix_y
        self.loc = loc
        self.is_left = is_left
        self.is_right = is_right
        self.is_join = is_join
        self.left_index = left_index
        self.right_index = right_index
        self.indicator = indicator
        self.is_na_equal = is_na_equal
        self.gen_cond_expr = gen_cond_expr
        self.left_cond_cols = set(wji__zufes for wji__zufes in left_vars.
            keys() if f'(left.{wji__zufes})' in gen_cond_expr)
        self.right_cond_cols = set(wji__zufes for wji__zufes in right_vars.
            keys() if f'(right.{wji__zufes})' in gen_cond_expr)
        qrg__viky = set(left_keys) & set(right_keys)
        taxs__kunx = set(left_vars.keys()) & set(right_vars.keys())
        uqpei__emdgn = taxs__kunx - qrg__viky
        vect_same_key = []
        n_keys = len(left_keys)
        for nif__ltfcn in range(n_keys):
            yfy__uexua = left_keys[nif__ltfcn]
            ybk__msuk = right_keys[nif__ltfcn]
            vect_same_key.append(yfy__uexua == ybk__msuk)
        self.vect_same_key = vect_same_key
        self.column_origins = {(str(wji__zufes) + suffix_x if wji__zufes in
            uqpei__emdgn else wji__zufes): ('left', wji__zufes) for
            wji__zufes in left_vars.keys()}
        self.column_origins.update({(str(wji__zufes) + suffix_y if 
            wji__zufes in uqpei__emdgn else wji__zufes): ('right',
            wji__zufes) for wji__zufes in right_vars.keys()})
        if '$_bodo_index_' in uqpei__emdgn:
            uqpei__emdgn.remove('$_bodo_index_')
        self.add_suffix = uqpei__emdgn

    def __repr__(self):
        xxq__nfx = ''
        for wji__zufes, xsdwc__xpoe in self.out_data_vars.items():
            xxq__nfx += "'{}':{}, ".format(wji__zufes, xsdwc__xpoe.name)
        jcf__emi = '{}{{{}}}'.format(self.df_out, xxq__nfx)
        mhdzc__zgjq = ''
        for wji__zufes, xsdwc__xpoe in self.left_vars.items():
            mhdzc__zgjq += "'{}':{}, ".format(wji__zufes, xsdwc__xpoe.name)
        jmpm__zkdr = '{}{{{}}}'.format(self.left_df, mhdzc__zgjq)
        mhdzc__zgjq = ''
        for wji__zufes, xsdwc__xpoe in self.right_vars.items():
            mhdzc__zgjq += "'{}':{}, ".format(wji__zufes, xsdwc__xpoe.name)
        rnm__bci = '{}{{{}}}'.format(self.right_df, mhdzc__zgjq)
        return 'join [{}={}]: {} , {}, {}'.format(self.left_keys, self.
            right_keys, jcf__emi, jmpm__zkdr, rnm__bci)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    wtt__nzt = []
    assert len(join_node.out_data_vars) > 0, 'empty join in array analysis'
    pcg__tzv = []
    jvce__tjwhk = list(join_node.left_vars.values())
    for fwqu__kaqkh in jvce__tjwhk:
        nkwr__zmag = typemap[fwqu__kaqkh.name]
        zcbb__uzmku = equiv_set.get_shape(fwqu__kaqkh)
        if zcbb__uzmku:
            pcg__tzv.append(zcbb__uzmku[0])
    if len(pcg__tzv) > 1:
        equiv_set.insert_equiv(*pcg__tzv)
    pcg__tzv = []
    jvce__tjwhk = list(join_node.right_vars.values())
    for fwqu__kaqkh in jvce__tjwhk:
        nkwr__zmag = typemap[fwqu__kaqkh.name]
        zcbb__uzmku = equiv_set.get_shape(fwqu__kaqkh)
        if zcbb__uzmku:
            pcg__tzv.append(zcbb__uzmku[0])
    if len(pcg__tzv) > 1:
        equiv_set.insert_equiv(*pcg__tzv)
    pcg__tzv = []
    for fwqu__kaqkh in join_node.out_data_vars.values():
        nkwr__zmag = typemap[fwqu__kaqkh.name]
        squ__orkn = array_analysis._gen_shape_call(equiv_set, fwqu__kaqkh,
            nkwr__zmag.ndim, None, wtt__nzt)
        equiv_set.insert_equiv(fwqu__kaqkh, squ__orkn)
        pcg__tzv.append(squ__orkn[0])
        equiv_set.define(fwqu__kaqkh, set())
    if len(pcg__tzv) > 1:
        equiv_set.insert_equiv(*pcg__tzv)
    return [], wtt__nzt


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    msmm__ava = Distribution.OneD
    dxy__frn = Distribution.OneD
    for fwqu__kaqkh in join_node.left_vars.values():
        msmm__ava = Distribution(min(msmm__ava.value, array_dists[
            fwqu__kaqkh.name].value))
    for fwqu__kaqkh in join_node.right_vars.values():
        dxy__frn = Distribution(min(dxy__frn.value, array_dists[fwqu__kaqkh
            .name].value))
    efq__pxkcw = Distribution.OneD_Var
    for fwqu__kaqkh in join_node.out_data_vars.values():
        if fwqu__kaqkh.name in array_dists:
            efq__pxkcw = Distribution(min(efq__pxkcw.value, array_dists[
                fwqu__kaqkh.name].value))
    qbgwh__axtxk = Distribution(min(efq__pxkcw.value, msmm__ava.value))
    yptbd__nkku = Distribution(min(efq__pxkcw.value, dxy__frn.value))
    efq__pxkcw = Distribution(max(qbgwh__axtxk.value, yptbd__nkku.value))
    for fwqu__kaqkh in join_node.out_data_vars.values():
        array_dists[fwqu__kaqkh.name] = efq__pxkcw
    if efq__pxkcw != Distribution.OneD_Var:
        msmm__ava = efq__pxkcw
        dxy__frn = efq__pxkcw
    for fwqu__kaqkh in join_node.left_vars.values():
        array_dists[fwqu__kaqkh.name] = msmm__ava
    for fwqu__kaqkh in join_node.right_vars.values():
        array_dists[fwqu__kaqkh.name] = dxy__frn
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def join_typeinfer(join_node, typeinferer):
    qrg__viky = set(join_node.left_keys) & set(join_node.right_keys)
    taxs__kunx = set(join_node.left_vars.keys()) & set(join_node.right_vars
        .keys())
    uqpei__emdgn = taxs__kunx - qrg__viky
    for jyb__lorcl, twf__xsxrn in join_node.out_data_vars.items():
        if join_node.indicator and jyb__lorcl == '_merge':
            continue
        if not jyb__lorcl in join_node.column_origins:
            raise BodoError('join(): The variable ' + jyb__lorcl +
                ' is absent from the output')
        xdwrq__wgtl = join_node.column_origins[jyb__lorcl]
        if xdwrq__wgtl[0] == 'left':
            fwqu__kaqkh = join_node.left_vars[xdwrq__wgtl[1]]
        else:
            fwqu__kaqkh = join_node.right_vars[xdwrq__wgtl[1]]
        typeinferer.constraints.append(typeinfer.Propagate(dst=twf__xsxrn.
            name, src=fwqu__kaqkh.name, loc=join_node.loc))
    return


typeinfer.typeinfer_extensions[Join] = join_typeinfer


def visit_vars_join(join_node, callback, cbdata):
    if debug_prints():
        print('visiting join vars for:', join_node)
        print('cbdata: ', sorted(cbdata.items()))
    for quv__lgajl in list(join_node.left_vars.keys()):
        join_node.left_vars[quv__lgajl] = visit_vars_inner(join_node.
            left_vars[quv__lgajl], callback, cbdata)
    for quv__lgajl in list(join_node.right_vars.keys()):
        join_node.right_vars[quv__lgajl] = visit_vars_inner(join_node.
            right_vars[quv__lgajl], callback, cbdata)
    for quv__lgajl in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[quv__lgajl] = visit_vars_inner(join_node.
            out_data_vars[quv__lgajl], callback, cbdata)


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    lgbpn__ivh = []
    omfcz__cxfy = True
    for quv__lgajl, fwqu__kaqkh in join_node.out_data_vars.items():
        if fwqu__kaqkh.name in lives:
            omfcz__cxfy = False
            continue
        if quv__lgajl == '$_bodo_index_':
            continue
        if join_node.indicator and quv__lgajl == '_merge':
            lgbpn__ivh.append('_merge')
            join_node.indicator = False
            continue
        dajki__vdc, qfux__lltwk = join_node.column_origins[quv__lgajl]
        if (dajki__vdc == 'left' and qfux__lltwk not in join_node.left_keys and
            qfux__lltwk not in join_node.left_cond_cols):
            join_node.left_vars.pop(qfux__lltwk)
            lgbpn__ivh.append(quv__lgajl)
        if (dajki__vdc == 'right' and qfux__lltwk not in join_node.
            right_keys and qfux__lltwk not in join_node.right_cond_cols):
            join_node.right_vars.pop(qfux__lltwk)
            lgbpn__ivh.append(quv__lgajl)
    for cname in lgbpn__ivh:
        join_node.out_data_vars.pop(cname)
    if omfcz__cxfy:
        return None
    return join_node


ir_utils.remove_dead_extensions[Join] = remove_dead_join


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({xsdwc__xpoe.name for xsdwc__xpoe in join_node.left_vars
        .values()})
    use_set.update({xsdwc__xpoe.name for xsdwc__xpoe in join_node.
        right_vars.values()})
    def_set.update({xsdwc__xpoe.name for xsdwc__xpoe in join_node.
        out_data_vars.values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    uxvpc__gibnl = set(xsdwc__xpoe.name for xsdwc__xpoe in join_node.
        out_data_vars.values())
    return set(), uxvpc__gibnl


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for quv__lgajl in list(join_node.left_vars.keys()):
        join_node.left_vars[quv__lgajl] = replace_vars_inner(join_node.
            left_vars[quv__lgajl], var_dict)
    for quv__lgajl in list(join_node.right_vars.keys()):
        join_node.right_vars[quv__lgajl] = replace_vars_inner(join_node.
            right_vars[quv__lgajl], var_dict)
    for quv__lgajl in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[quv__lgajl] = replace_vars_inner(join_node.
            out_data_vars[quv__lgajl], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for fwqu__kaqkh in join_node.out_data_vars.values():
        definitions[fwqu__kaqkh.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    n_keys = len(join_node.left_keys)
    xfpkf__lbch = tuple(join_node.left_vars[wji__zufes] for wji__zufes in
        join_node.left_keys)
    zasdg__memy = tuple(join_node.right_vars[wji__zufes] for wji__zufes in
        join_node.right_keys)
    hezj__ciy = tuple(join_node.left_vars.keys())
    osliy__lta = tuple(join_node.right_vars.keys())
    rcvo__tqhb = ()
    jufor__pqg = ()
    optional_column = False
    if (join_node.left_index and not join_node.right_index and not
        join_node.is_join):
        lpog__vwbp = join_node.right_keys[0]
        if lpog__vwbp in hezj__ciy:
            jufor__pqg = lpog__vwbp,
            rcvo__tqhb = join_node.right_vars[lpog__vwbp],
            optional_column = True
    if (join_node.right_index and not join_node.left_index and not
        join_node.is_join):
        lpog__vwbp = join_node.left_keys[0]
        if lpog__vwbp in osliy__lta:
            jufor__pqg = lpog__vwbp,
            rcvo__tqhb = join_node.left_vars[lpog__vwbp],
            optional_column = True
    gea__yiwi = tuple(join_node.out_data_vars[cname] for cname in jufor__pqg)
    slk__zxbrv = tuple(xsdwc__xpoe for qijg__kfev, xsdwc__xpoe in sorted(
        join_node.left_vars.items(), key=lambda a: str(a[0])) if qijg__kfev
         not in join_node.left_keys)
    bxv__chde = tuple(xsdwc__xpoe for qijg__kfev, xsdwc__xpoe in sorted(
        join_node.right_vars.items(), key=lambda a: str(a[0])) if 
        qijg__kfev not in join_node.right_keys)
    wxay__gwqjt = (rcvo__tqhb + xfpkf__lbch + zasdg__memy + slk__zxbrv +
        bxv__chde)
    cjisu__jreb = tuple(typemap[xsdwc__xpoe.name] for xsdwc__xpoe in
        wxay__gwqjt)
    yzqx__lhtxx = tuple('opti_c' + str(i) for i in range(len(rcvo__tqhb)))
    left_other_names = tuple('t1_c' + str(i) for i in range(len(slk__zxbrv)))
    right_other_names = tuple('t2_c' + str(i) for i in range(len(bxv__chde)))
    left_other_types = tuple([typemap[wji__zufes.name] for wji__zufes in
        slk__zxbrv])
    right_other_types = tuple([typemap[wji__zufes.name] for wji__zufes in
        bxv__chde])
    left_key_names = tuple('t1_key' + str(i) for i in range(n_keys))
    right_key_names = tuple('t2_key' + str(i) for i in range(n_keys))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}{}, {},{}{}{}):\n'.format('{},'.format(yzqx__lhtxx
        [0]) if len(yzqx__lhtxx) == 1 else '', ','.join(left_key_names),
        ','.join(right_key_names), ','.join(left_other_names), ',' if len(
        left_other_names) != 0 else '', ','.join(right_other_names))
    left_key_types = tuple(typemap[xsdwc__xpoe.name] for xsdwc__xpoe in
        xfpkf__lbch)
    right_key_types = tuple(typemap[xsdwc__xpoe.name] for xsdwc__xpoe in
        zasdg__memy)
    for i in range(n_keys):
        glbs[f'key_type_{i}'] = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
    func_text += '    t1_keys = ({},)\n'.format(', '.join(
        f'bodo.utils.utils.astype({left_key_names[i]}, key_type_{i})' for i in
        range(n_keys)))
    func_text += '    t2_keys = ({},)\n'.format(', '.join(
        f'bodo.utils.utils.astype({right_key_names[i]}, key_type_{i})' for
        i in range(n_keys)))
    func_text += '    data_left = ({}{})\n'.format(','.join(
        left_other_names), ',' if len(left_other_names) != 0 else '')
    func_text += '    data_right = ({}{})\n'.format(','.join(
        right_other_names), ',' if len(right_other_names) != 0 else '')
    yscwa__loll = []
    for cname in join_node.left_keys:
        if cname in join_node.add_suffix:
            gwhjm__ywfdr = str(cname) + join_node.suffix_x
        else:
            gwhjm__ywfdr = cname
        assert gwhjm__ywfdr in join_node.out_data_vars
        yscwa__loll.append(join_node.out_data_vars[gwhjm__ywfdr])
    for i, cname in enumerate(join_node.right_keys):
        if not join_node.vect_same_key[i] and not join_node.is_join:
            if cname in join_node.add_suffix:
                gwhjm__ywfdr = str(cname) + join_node.suffix_y
            else:
                gwhjm__ywfdr = cname
            assert gwhjm__ywfdr in join_node.out_data_vars
            yscwa__loll.append(join_node.out_data_vars[gwhjm__ywfdr])

    def _get_out_col_var(cname, is_left):
        if cname in join_node.add_suffix:
            if is_left:
                gwhjm__ywfdr = str(cname) + join_node.suffix_x
            else:
                gwhjm__ywfdr = str(cname) + join_node.suffix_y
        else:
            gwhjm__ywfdr = cname
        return join_node.out_data_vars[gwhjm__ywfdr]
    bex__smlrc = gea__yiwi + tuple(yscwa__loll)
    bex__smlrc += tuple(_get_out_col_var(qijg__kfev, True) for qijg__kfev,
        xsdwc__xpoe in sorted(join_node.left_vars.items(), key=lambda a:
        str(a[0])) if qijg__kfev not in join_node.left_keys)
    bex__smlrc += tuple(_get_out_col_var(qijg__kfev, False) for qijg__kfev,
        xsdwc__xpoe in sorted(join_node.right_vars.items(), key=lambda a:
        str(a[0])) if qijg__kfev not in join_node.right_keys)
    if join_node.indicator:
        bex__smlrc += _get_out_col_var('_merge', False),
    fhb__cvxa = [('t3_c' + str(i)) for i in range(len(bex__smlrc))]
    general_cond_cfunc, left_col_nums, right_col_nums = (
        _gen_general_cond_cfunc(join_node, typemap))
    if join_node.how == 'asof':
        if left_parallel or right_parallel:
            assert left_parallel and right_parallel
            func_text += """    t2_keys, data_right = parallel_asof_comm(t1_keys, t2_keys, data_right)
"""
        func_text += """    out_t1_keys, out_t2_keys, out_data_left, out_data_right = bodo.ir.join.local_merge_asof(t1_keys, t2_keys, data_left, data_right)
"""
    else:
        func_text += _gen_local_hash_join(optional_column, left_key_names,
            right_key_names, left_key_types, right_key_types,
            left_other_names, right_other_names, left_other_types,
            right_other_types, join_node.vect_same_key, join_node.is_left,
            join_node.is_right, join_node.is_join, left_parallel,
            right_parallel, glbs, [typemap[xsdwc__xpoe.name] for
            xsdwc__xpoe in bex__smlrc], join_node.loc, join_node.indicator,
            join_node.is_na_equal, general_cond_cfunc, left_col_nums,
            right_col_nums)
    if join_node.how == 'asof':
        for i in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(i, i)
        for i in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(i, i)
        for i in range(n_keys):
            func_text += f'    t1_keys_{i} = out_t1_keys[{i}]\n'
        for i in range(n_keys):
            func_text += f'    t2_keys_{i} = out_t2_keys[{i}]\n'
    idx = 0
    if optional_column:
        func_text += f'    {fhb__cvxa[idx]} = opti_0\n'
        idx += 1
    for i in range(n_keys):
        func_text += f'    {fhb__cvxa[idx]} = t1_keys_{i}\n'
        idx += 1
    for i in range(n_keys):
        if not join_node.vect_same_key[i] and not join_node.is_join:
            func_text += f'    {fhb__cvxa[idx]} = t2_keys_{i}\n'
            idx += 1
    for i in range(len(left_other_names)):
        func_text += f'    {fhb__cvxa[idx]} = left_{i}\n'
        idx += 1
    for i in range(len(right_other_names)):
        func_text += f'    {fhb__cvxa[idx]} = right_{i}\n'
        idx += 1
    if join_node.indicator:
        func_text += f'    {fhb__cvxa[idx]} = indicator_col\n'
        idx += 1
    bxrzc__vxn = {}
    exec(func_text, {}, bxrzc__vxn)
    cmlbr__ydnjo = bxrzc__vxn['f']
    glbs.update({'bodo': bodo, 'np': np, 'pd': pd,
        'to_list_if_immutable_arr': to_list_if_immutable_arr,
        'cp_str_list_to_array': cp_str_list_to_array, 'parallel_asof_comm':
        parallel_asof_comm, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'hash_join_table':
        hash_join_table, 'info_from_table': info_from_table,
        'info_to_array': info_to_array, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'add_join_gen_cond_cfunc_sym': add_join_gen_cond_cfunc_sym,
        'get_join_cond_addr': get_join_cond_addr})
    if general_cond_cfunc:
        glbs.update({'general_cond_cfunc': general_cond_cfunc})
    rgrp__ttse = compile_to_numba_ir(cmlbr__ydnjo, glbs, typingctx=
        typingctx, targetctx=targetctx, arg_typs=cjisu__jreb, typemap=
        typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(rgrp__ttse, wxay__gwqjt)
    wulj__cwlfx = rgrp__ttse.body[:-3]
    for i in range(len(bex__smlrc)):
        wulj__cwlfx[-len(bex__smlrc) + i].target = bex__smlrc[i]
    return wulj__cwlfx


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    gcl__jqi = next_label()
    vwyog__wvmu = _get_col_to_ind(join_node.left_keys, join_node.left_vars)
    vfac__ehrw = _get_col_to_ind(join_node.right_keys, join_node.right_vars)
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{gcl__jqi}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
"""
    func_text += '  if is_null_pointer(left_table):\n'
    func_text += '    return False\n'
    expr, func_text, left_col_nums = _replace_column_accesses(expr,
        vwyog__wvmu, typemap, join_node.left_vars, table_getitem_funcs,
        func_text, 'left', len(join_node.left_keys), na_check_name)
    expr, func_text, right_col_nums = _replace_column_accesses(expr,
        vfac__ehrw, typemap, join_node.right_vars, table_getitem_funcs,
        func_text, 'right', len(join_node.right_keys), na_check_name)
    func_text += f'  return {expr}'
    bxrzc__vxn = {}
    exec(func_text, table_getitem_funcs, bxrzc__vxn)
    gpku__zpm = bxrzc__vxn[f'bodo_join_gen_cond{gcl__jqi}']
    dyxn__rgoog = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    vyfq__xbdfo = numba.cfunc(dyxn__rgoog, nopython=True)(gpku__zpm)
    join_gen_cond_cfunc[vyfq__xbdfo.native_name] = vyfq__xbdfo
    join_gen_cond_cfunc_addr[vyfq__xbdfo.native_name] = vyfq__xbdfo.address
    return vyfq__xbdfo, left_col_nums, right_col_nums


def _replace_column_accesses(expr, col_to_ind, typemap, col_vars,
    table_getitem_funcs, func_text, table_name, n_keys, na_check_name):
    fghrj__wvx = []
    for wji__zufes, btzgr__mxj in col_to_ind.items():
        cname = f'({table_name}.{wji__zufes})'
        if cname not in expr:
            continue
        rtvp__noc = f'getitem_{table_name}_val_{btzgr__mxj}'
        nbds__xiia = f'_bodo_{table_name}_val_{btzgr__mxj}'
        bjraq__xzv = typemap[col_vars[wji__zufes].name].dtype
        if bjraq__xzv == types.unicode_type:
            func_text += f"""  {nbds__xiia}, {nbds__xiia}_size = {rtvp__noc}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {nbds__xiia} = bodo.libs.str_arr_ext.decode_utf8({nbds__xiia}, {nbds__xiia}_size)
"""
        else:
            func_text += (
                f'  {nbds__xiia} = {rtvp__noc}({table_name}_data1, {table_name}_ind)\n'
                )
        table_getitem_funcs[rtvp__noc
            ] = bodo.libs.array._gen_row_access_intrinsic(bjraq__xzv,
            btzgr__mxj)
        expr = expr.replace(cname, nbds__xiia)
        wndc__vgajt = f'({na_check_name}.{table_name}.{wji__zufes})'
        if wndc__vgajt in expr:
            czobz__ovao = typemap[col_vars[wji__zufes].name]
            tml__zzx = f'nacheck_{table_name}_val_{btzgr__mxj}'
            vwes__godxx = f'_bodo_isna_{table_name}_val_{btzgr__mxj}'
            if isinstance(czobz__ovao, bodo.libs.int_arr_ext.IntegerArrayType
                ) or czobz__ovao in [bodo.libs.bool_arr_ext.boolean_array,
                bodo.libs.str_arr_ext.string_array_type]:
                func_text += f"""  {vwes__godxx} = {tml__zzx}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += (
                    f'  {vwes__godxx} = {tml__zzx}({table_name}_data1, {table_name}_ind)\n'
                    )
            table_getitem_funcs[tml__zzx
                ] = bodo.libs.array._gen_row_na_check_intrinsic(czobz__ovao,
                btzgr__mxj)
            expr = expr.replace(wndc__vgajt, vwes__godxx)
        if btzgr__mxj >= n_keys:
            fghrj__wvx.append(btzgr__mxj)
    return expr, func_text, fghrj__wvx


def _get_col_to_ind(key_names, col_vars):
    n_keys = len(key_names)
    col_to_ind = {wji__zufes: i for i, wji__zufes in enumerate(key_names)}
    i = n_keys
    for wji__zufes in sorted(col_vars, key=lambda a: str(a)):
        if wji__zufes in key_names:
            continue
        col_to_ind[wji__zufes] = i
        i += 1
    return col_to_ind


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    lws__povn = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[xsdwc__xpoe.name] in lws__povn for
        xsdwc__xpoe in join_node.left_vars.values())
    right_parallel = all(array_dists[xsdwc__xpoe.name] in lws__povn for
        xsdwc__xpoe in join_node.right_vars.values())
    if not left_parallel:
        assert not any(array_dists[xsdwc__xpoe.name] in lws__povn for
            xsdwc__xpoe in join_node.left_vars.values())
    if not right_parallel:
        assert not any(array_dists[xsdwc__xpoe.name] in lws__povn for
            xsdwc__xpoe in join_node.right_vars.values())
    if left_parallel or right_parallel:
        assert all(array_dists[xsdwc__xpoe.name] in lws__povn for
            xsdwc__xpoe in join_node.out_data_vars.values())
    return left_parallel, right_parallel


def _gen_local_hash_join(optional_column, left_key_names, right_key_names,
    left_key_types, right_key_types, left_other_names, right_other_names,
    left_other_types, right_other_types, vect_same_key, is_left, is_right,
    is_join, left_parallel, right_parallel, glbs, out_types, loc, indicator,
    is_na_equal, general_cond_cfunc, left_col_nums, right_col_nums):

    def needs_typechange(in_type, need_nullable, is_same_key):
        return isinstance(in_type, types.Array) and not is_dtype_nullable(
            in_type.dtype) and need_nullable and not is_same_key
    pawol__gucqq = []
    for i in range(len(left_key_names)):
        hgmy__qzly = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
        pawol__gucqq.append(needs_typechange(hgmy__qzly, is_right,
            vect_same_key[i]))
    for i in range(len(left_other_names)):
        pawol__gucqq.append(needs_typechange(left_other_types[i], is_right,
            False))
    for i in range(len(right_key_names)):
        if not vect_same_key[i] and not is_join:
            hgmy__qzly = _match_join_key_types(left_key_types[i],
                right_key_types[i], loc)
            pawol__gucqq.append(needs_typechange(hgmy__qzly, is_left, False))
    for i in range(len(right_other_names)):
        pawol__gucqq.append(needs_typechange(right_other_types[i], is_left,
            False))

    def get_out_type(idx, in_type, in_name, need_nullable, is_same_key):
        if isinstance(in_type, types.Array) and not is_dtype_nullable(in_type
            .dtype) and need_nullable and not is_same_key:
            if isinstance(in_type.dtype, types.Integer):
                iaijs__tfrfo = IntDtype(in_type.dtype).name
                assert iaijs__tfrfo.endswith('Dtype()')
                iaijs__tfrfo = iaijs__tfrfo[:-7]
                alg__ayhqt = f"""    typ_{idx} = bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype="{iaijs__tfrfo}"))
"""
                dzq__dgcmg = f'typ_{idx}'
            else:
                assert in_type.dtype == types.bool_, 'unexpected non-nullable type in join'
                alg__ayhqt = (
                    f'    typ_{idx} = bodo.libs.bool_arr_ext.alloc_bool_array(1)\n'
                    )
                dzq__dgcmg = f'typ_{idx}'
        else:
            alg__ayhqt = ''
            dzq__dgcmg = in_name
        return alg__ayhqt, dzq__dgcmg
    n_keys = len(left_key_names)
    func_text = '    # beginning of _gen_local_hash_join\n'
    qcrde__gaxu = []
    for i in range(n_keys):
        qcrde__gaxu.append('t1_keys[{}]'.format(i))
    for i in range(len(left_other_names)):
        qcrde__gaxu.append('data_left[{}]'.format(i))
    func_text += '    info_list_total_l = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in qcrde__gaxu))
    func_text += '    table_left = arr_info_list_to_table(info_list_total_l)\n'
    zlx__pfxcr = []
    for i in range(n_keys):
        zlx__pfxcr.append('t2_keys[{}]'.format(i))
    for i in range(len(right_other_names)):
        zlx__pfxcr.append('data_right[{}]'.format(i))
    func_text += '    info_list_total_r = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in zlx__pfxcr))
    func_text += (
        '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    func_text += '    vect_same_key = np.array([{}])\n'.format(','.join('1' if
        ajna__aua else '0' for ajna__aua in vect_same_key))
    func_text += '    vect_need_typechange = np.array([{}])\n'.format(','.
        join('1' if ajna__aua else '0' for ajna__aua in pawol__gucqq))
    func_text += f"""    left_table_cond_columns = np.array({left_col_nums if len(left_col_nums) > 0 else [-1]}, dtype=np.int64)
"""
    func_text += f"""    right_table_cond_columns = np.array({right_col_nums if len(right_col_nums) > 0 else [-1]}, dtype=np.int64)
"""
    if general_cond_cfunc:
        func_text += f"""    cfunc_cond = add_join_gen_cond_cfunc_sym(general_cond_cfunc, '{general_cond_cfunc.native_name}')
"""
        func_text += (
            f"    cfunc_cond = get_join_cond_addr('{general_cond_cfunc.native_name}')\n"
            )
    else:
        func_text += '    cfunc_cond = 0\n'
    func_text += (
        """    out_table = hash_join_table(table_left, table_right, {}, {}, {}, {}, {}, vect_same_key.ctypes, vect_need_typechange.ctypes, {}, {}, {}, {}, {}, {}, cfunc_cond, left_table_cond_columns.ctypes, {}, right_table_cond_columns.ctypes, {})
"""
        .format(left_parallel, right_parallel, n_keys, len(left_other_names
        ), len(right_other_names), is_left, is_right, is_join,
        optional_column, indicator, is_na_equal, len(left_col_nums), len(
        right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    idx = 0
    if optional_column:
        func_text += (
            f'    opti_0 = info_to_array(info_from_table(out_table, {idx}), opti_c0)\n'
            )
        idx += 1
    for i, pqptz__ewjx in enumerate(left_key_names):
        hgmy__qzly = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
        zgu__mha = get_out_type(idx, hgmy__qzly, f't1_keys[{i}]', is_right,
            vect_same_key[i])
        func_text += zgu__mha[0]
        glbs[f'out_type_{idx}'] = out_types[idx]
        if hgmy__qzly != left_key_types[i]:
            func_text += f"""    t1_keys_{i} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {zgu__mha[1]}), out_type_{idx})
"""
        else:
            func_text += f"""    t1_keys_{i} = info_to_array(info_from_table(out_table, {idx}), {zgu__mha[1]})
"""
        idx += 1
    for i, pqptz__ewjx in enumerate(left_other_names):
        zgu__mha = get_out_type(idx, left_other_types[i], pqptz__ewjx,
            is_right, False)
        func_text += zgu__mha[0]
        func_text += (
            '    left_{} = info_to_array(info_from_table(out_table, {}), {})\n'
            .format(i, idx, zgu__mha[1]))
        idx += 1
    for i, pqptz__ewjx in enumerate(right_key_names):
        if not vect_same_key[i] and not is_join:
            hgmy__qzly = _match_join_key_types(left_key_types[i],
                right_key_types[i], loc)
            zgu__mha = get_out_type(idx, hgmy__qzly, f't2_keys[{i}]',
                is_left, False)
            func_text += zgu__mha[0]
            glbs[f'out_type_{idx}'] = out_types[idx - len(left_other_names)]
            if hgmy__qzly != right_key_types[i]:
                func_text += f"""    t2_keys_{i} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {zgu__mha[1]}), out_type_{idx})
"""
            else:
                func_text += f"""    t2_keys_{i} = info_to_array(info_from_table(out_table, {idx}), {zgu__mha[1]})
"""
            idx += 1
    for i, pqptz__ewjx in enumerate(right_other_names):
        zgu__mha = get_out_type(idx, right_other_types[i], pqptz__ewjx,
            is_left, False)
        func_text += zgu__mha[0]
        func_text += (
            '    right_{} = info_to_array(info_from_table(out_table, {}), {})\n'
            .format(i, idx, zgu__mha[1]))
        idx += 1
    if indicator:
        func_text += f"""    typ_{idx} = pd.Categorical(values=['both'], categories=('left_only', 'right_only', 'both'))
"""
        func_text += f"""    indicator_col = info_to_array(info_from_table(out_table, {idx}), typ_{idx})
"""
        idx += 1
    func_text += '    delete_table(out_table)\n'
    return func_text


def parallel_join_impl(key_arrs, data):
    zgd__cwo = bodo.libs.distributed_api.get_size()
    gmuue__hjfxe = alloc_pre_shuffle_metadata(key_arrs, data, zgd__cwo, False)
    qijg__kfev = len(key_arrs[0])
    mnbuf__ibli = np.empty(qijg__kfev, np.int32)
    iiqe__blc = arr_info_list_to_table([array_to_info(key_arrs[0])])
    iqq__fytt = 1
    jjcx__hlldk = compute_node_partition_by_hash(iiqe__blc, iqq__fytt, zgd__cwo
        )
    anr__qibq = np.empty(1, np.int32)
    ooj__zta = info_to_array(info_from_table(jjcx__hlldk, 0), anr__qibq)
    delete_table(jjcx__hlldk)
    delete_table(iiqe__blc)
    for i in range(qijg__kfev):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = ooj__zta[i]
        mnbuf__ibli[i] = node_id
        update_shuffle_meta(gmuue__hjfxe, node_id, i, key_arrs, data, False)
    shuffle_meta = finalize_shuffle_meta(key_arrs, data, gmuue__hjfxe,
        zgd__cwo, False)
    for i in range(qijg__kfev):
        node_id = mnbuf__ibli[i]
        write_send_buff(shuffle_meta, node_id, i, key_arrs, data)
        shuffle_meta.tmp_offset[node_id] += 1
    vxpqh__cwyfq = alltoallv_tup(key_arrs + data, shuffle_meta, key_arrs)
    yscwa__loll = _get_keys_tup(vxpqh__cwyfq, key_arrs)
    dkhl__zloh = _get_data_tup(vxpqh__cwyfq, key_arrs)
    return yscwa__loll, dkhl__zloh


@generated_jit(nopython=True, cache=True)
def parallel_shuffle(key_arrs, data):
    return parallel_join_impl


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    zgd__cwo = bodo.libs.distributed_api.get_size()
    nhwv__pogb = np.empty(zgd__cwo, left_key_arrs[0].dtype)
    hcpa__lkh = np.empty(zgd__cwo, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(nhwv__pogb, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(hcpa__lkh, left_key_arrs[0][-1])
    aotr__apdz = np.zeros(zgd__cwo, np.int32)
    uehn__wkznt = np.zeros(zgd__cwo, np.int32)
    ywu__ldjl = np.zeros(zgd__cwo, np.int32)
    svtm__ytz = right_key_arrs[0][0]
    sgy__ktdhf = right_key_arrs[0][-1]
    fqqix__ggdm = -1
    i = 0
    while i < zgd__cwo - 1 and hcpa__lkh[i] < svtm__ytz:
        i += 1
    while i < zgd__cwo and nhwv__pogb[i] <= sgy__ktdhf:
        fqqix__ggdm, trp__jss = _count_overlap(right_key_arrs[0],
            nhwv__pogb[i], hcpa__lkh[i])
        if fqqix__ggdm != 0:
            fqqix__ggdm -= 1
            trp__jss += 1
        aotr__apdz[i] = trp__jss
        uehn__wkznt[i] = fqqix__ggdm
        i += 1
    while i < zgd__cwo:
        aotr__apdz[i] = 1
        uehn__wkznt[i] = len(right_key_arrs[0]) - 1
        i += 1
    bodo.libs.distributed_api.alltoall(aotr__apdz, ywu__ldjl, 1)
    xhzs__opel = ywu__ldjl.sum()
    oyo__eskk = np.empty(xhzs__opel, right_key_arrs[0].dtype)
    zple__rih = alloc_arr_tup(xhzs__opel, right_data)
    suxxy__mlgkc = bodo.ir.join.calc_disp(ywu__ldjl)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], oyo__eskk,
        aotr__apdz, ywu__ldjl, uehn__wkznt, suxxy__mlgkc)
    bodo.libs.distributed_api.alltoallv_tup(right_data, zple__rih,
        aotr__apdz, ywu__ldjl, uehn__wkznt, suxxy__mlgkc)
    return (oyo__eskk,), zple__rih


@numba.njit
def _count_overlap(r_key_arr, start, end):
    trp__jss = 0
    fqqix__ggdm = 0
    lerb__nmgsd = 0
    while lerb__nmgsd < len(r_key_arr) and r_key_arr[lerb__nmgsd] < start:
        fqqix__ggdm += 1
        lerb__nmgsd += 1
    while lerb__nmgsd < len(r_key_arr) and start <= r_key_arr[lerb__nmgsd
        ] <= end:
        lerb__nmgsd += 1
        trp__jss += 1
    return fqqix__ggdm, trp__jss


def write_send_buff(shuffle_meta, node_id, i, key_arrs, data):
    return i


@overload(write_send_buff, no_unliteral=True)
def write_data_buff_overload(meta, node_id, i, key_arrs, data):
    func_text = 'def f(meta, node_id, i, key_arrs, data):\n'
    func_text += (
        '  w_ind = meta.send_disp[node_id] + meta.tmp_offset[node_id]\n')
    n_keys = len(key_arrs.types)
    for i, nkwr__zmag in enumerate(key_arrs.types + data.types):
        arr = 'key_arrs[{}]'.format(i) if i < n_keys else 'data[{}]'.format(
            i - n_keys)
        if not nkwr__zmag in (string_type, string_array_type,
            binary_array_type, bytes_type):
            func_text += '  meta.send_buff_tup[{}][w_ind] = {}[i]\n'.format(i,
                arr)
        else:
            func_text += ('  n_chars_{} = get_str_arr_item_length({}, i)\n'
                .format(i, arr))
            func_text += ('  meta.send_arr_lens_tup[{}][w_ind] = n_chars_{}\n'
                .format(i, i))
            if i >= n_keys:
                func_text += (
                    """  out_bitmap = meta.send_arr_nulls_tup[{}][meta.send_disp_nulls[node_id]:].ctypes
"""
                    .format(i))
                func_text += (
                    '  bit_val = get_bit_bitmap(get_null_bitmap_ptr(data[{}]), i)\n'
                    .format(i - n_keys))
                func_text += (
                    '  set_bit_to(out_bitmap, meta.tmp_offset[node_id], bit_val)\n'
                    )
            func_text += (
                """  indc_{} = meta.send_disp_char_tup[{}][node_id] + meta.tmp_offset_char_tup[{}][node_id]
"""
                .format(i, i, i))
            func_text += ('  item_ptr_{} = get_str_arr_item_ptr({}, i)\n'.
                format(i, arr))
            func_text += (
                """  str_copy_ptr(meta.send_arr_chars_tup[{}], indc_{}, item_ptr_{}, n_chars_{})
"""
                .format(i, i, i, i))
            func_text += (
                '  meta.tmp_offset_char_tup[{}][node_id] += n_chars_{}\n'.
                format(i, i))
    func_text += '  return w_ind\n'
    bxrzc__vxn = {}
    exec(func_text, {'str_copy_ptr': str_copy_ptr, 'get_null_bitmap_ptr':
        get_null_bitmap_ptr, 'get_bit_bitmap': get_bit_bitmap, 'set_bit_to':
        set_bit_to, 'get_str_arr_item_length': get_str_arr_item_length,
        'get_str_arr_item_ptr': get_str_arr_item_ptr}, bxrzc__vxn)
    neq__qufvc = bxrzc__vxn['f']
    return neq__qufvc


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    pbmlo__azxvw = np.empty_like(arr)
    pbmlo__azxvw[0] = 0
    for i in range(1, len(arr)):
        pbmlo__azxvw[i] = pbmlo__azxvw[i - 1] + arr[i - 1]
    return pbmlo__azxvw


def ensure_capacity(arr, new_size):
    dopw__mmx = arr
    zqn__niivr = len(arr)
    if zqn__niivr < new_size:
        ejebb__jcpkb = 2 * zqn__niivr
        dopw__mmx = bodo.utils.utils.alloc_type(ejebb__jcpkb, arr)
        dopw__mmx[:zqn__niivr] = arr
    return dopw__mmx


@overload(ensure_capacity, no_unliteral=True)
def ensure_capacity_overload(arr, new_size):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return ensure_capacity
    assert isinstance(arr, types.BaseTuple)
    trp__jss = arr.count
    func_text = 'def f(arr, new_size):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'ensure_capacity(arr[{}], new_size)'.format(i) for i in range(
        trp__jss)]), ',' if trp__jss == 1 else '')
    bxrzc__vxn = {}
    exec(func_text, {'ensure_capacity': ensure_capacity}, bxrzc__vxn)
    geo__psma = bxrzc__vxn['f']
    return geo__psma


@numba.njit
def ensure_capacity_str(arr, new_size, n_chars):
    dopw__mmx = arr
    zqn__niivr = len(arr)
    ogpn__wrx = num_total_chars(arr)
    rpj__qgorn = getitem_str_offset(arr, new_size - 1) + n_chars
    if zqn__niivr < new_size or rpj__qgorn > ogpn__wrx:
        ejebb__jcpkb = int(2 * zqn__niivr if zqn__niivr < new_size else
            zqn__niivr)
        yskd__wwgk = int(2 * ogpn__wrx + n_chars if rpj__qgorn > ogpn__wrx else
            ogpn__wrx)
        dopw__mmx = pre_alloc_string_array(ejebb__jcpkb, yskd__wwgk)
        copy_str_arr_slice(dopw__mmx, arr, new_size - 1)
    return dopw__mmx


def trim_arr_tup(data, new_size):
    return data


@overload(trim_arr_tup, no_unliteral=True)
def trim_arr_tup_overload(data, new_size):
    assert isinstance(data, types.BaseTuple)
    trp__jss = data.count
    func_text = 'def f(data, new_size):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'trim_arr(data[{}], new_size)'.format(i) for i in range(trp__jss)]),
        ',' if trp__jss == 1 else '')
    bxrzc__vxn = {}
    exec(func_text, {'trim_arr': trim_arr}, bxrzc__vxn)
    geo__psma = bxrzc__vxn['f']
    return geo__psma


def copy_elem_buff(arr, ind, val):
    dopw__mmx = ensure_capacity(arr, ind + 1)
    dopw__mmx[ind] = val
    return dopw__mmx


@overload(copy_elem_buff, no_unliteral=True)
def copy_elem_buff_overload(arr, ind, val):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return copy_elem_buff
    assert arr == string_array_type

    def copy_elem_buff_str(arr, ind, val):
        dopw__mmx = ensure_capacity_str(arr, ind + 1, get_utf8_size(val))
        dopw__mmx[ind] = val
        return dopw__mmx
    return copy_elem_buff_str


def copy_elem_buff_tup(arr, ind, val):
    return arr


@overload(copy_elem_buff_tup, no_unliteral=True)
def copy_elem_buff_tup_overload(data, ind, val):
    assert isinstance(data, types.BaseTuple)
    trp__jss = data.count
    func_text = 'def f(data, ind, val):\n'
    for i in range(trp__jss):
        func_text += ('  arr_{} = copy_elem_buff(data[{}], ind, val[{}])\n'
            .format(i, i, i))
    func_text += '  return ({}{})\n'.format(','.join(['arr_{}'.format(i) for
        i in range(trp__jss)]), ',' if trp__jss == 1 else '')
    bxrzc__vxn = {}
    exec(func_text, {'copy_elem_buff': copy_elem_buff}, bxrzc__vxn)
    fdur__dwvs = bxrzc__vxn['f']
    return fdur__dwvs


def trim_arr(arr, size):
    return arr[:size]


@overload(trim_arr, no_unliteral=True)
def trim_arr_overload(arr, size):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return trim_arr
    assert arr == string_array_type

    def trim_arr_str(arr, size):
        dopw__mmx = pre_alloc_string_array(size, np.int64(
            getitem_str_offset(arr, size)))
        copy_str_arr_slice(dopw__mmx, arr, size)
        return dopw__mmx
    return trim_arr_str


def setnan_elem_buff(arr, ind):
    dopw__mmx = ensure_capacity(arr, ind + 1)
    bodo.libs.array_kernels.setna(dopw__mmx, ind)
    return dopw__mmx


@overload(setnan_elem_buff, no_unliteral=True)
def setnan_elem_buff_overload(arr, ind):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return setnan_elem_buff
    assert arr == string_array_type

    def setnan_elem_buff_str(arr, ind):
        dopw__mmx = ensure_capacity_str(arr, ind + 1, 0)
        dopw__mmx[ind] = ''
        bodo.libs.array_kernels.setna(dopw__mmx, ind)
        return dopw__mmx
    return setnan_elem_buff_str


def setnan_elem_buff_tup(arr, ind):
    return arr


@overload(setnan_elem_buff_tup, no_unliteral=True)
def setnan_elem_buff_tup_overload(data, ind):
    assert isinstance(data, types.BaseTuple)
    trp__jss = data.count
    func_text = 'def f(data, ind):\n'
    for i in range(trp__jss):
        func_text += '  arr_{} = setnan_elem_buff(data[{}], ind)\n'.format(i, i
            )
    func_text += '  return ({}{})\n'.format(','.join(['arr_{}'.format(i) for
        i in range(trp__jss)]), ',' if trp__jss == 1 else '')
    bxrzc__vxn = {}
    exec(func_text, {'setnan_elem_buff': setnan_elem_buff}, bxrzc__vxn)
    fdur__dwvs = bxrzc__vxn['f']
    return fdur__dwvs


@generated_jit(nopython=True, cache=True)
def _check_ind_if_hashed(right_keys, r_ind, l_key):
    if right_keys == types.Tuple((types.intp[::1],)):
        return lambda right_keys, r_ind, l_key: r_ind

    def _impl(right_keys, r_ind, l_key):
        ydo__fgwca = getitem_arr_tup(right_keys, r_ind)
        if ydo__fgwca != l_key:
            return -1
        return r_ind
    return _impl


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    xbpq__ythte = len(left_keys[0])
    yjywq__nnzei = len(right_keys[0])
    zyw__nfce = alloc_arr_tup(xbpq__ythte, left_keys)
    sbfg__dfo = alloc_arr_tup(xbpq__ythte, right_keys)
    iif__hoflc = alloc_arr_tup(xbpq__ythte, data_left)
    vdiak__akn = alloc_arr_tup(xbpq__ythte, data_right)
    vguup__hjps = 0
    ssz__cdlr = 0
    for vguup__hjps in range(xbpq__ythte):
        if ssz__cdlr < 0:
            ssz__cdlr = 0
        while ssz__cdlr < yjywq__nnzei and getitem_arr_tup(right_keys,
            ssz__cdlr) <= getitem_arr_tup(left_keys, vguup__hjps):
            ssz__cdlr += 1
        ssz__cdlr -= 1
        setitem_arr_tup(zyw__nfce, vguup__hjps, getitem_arr_tup(left_keys,
            vguup__hjps))
        setitem_arr_tup(iif__hoflc, vguup__hjps, getitem_arr_tup(data_left,
            vguup__hjps))
        if ssz__cdlr >= 0:
            setitem_arr_tup(sbfg__dfo, vguup__hjps, getitem_arr_tup(
                right_keys, ssz__cdlr))
            setitem_arr_tup(vdiak__akn, vguup__hjps, getitem_arr_tup(
                data_right, ssz__cdlr))
        else:
            bodo.libs.array_kernels.setna_tup(sbfg__dfo, vguup__hjps)
            bodo.libs.array_kernels.setna_tup(vdiak__akn, vguup__hjps)
    return zyw__nfce, sbfg__dfo, iif__hoflc, vdiak__akn


def copy_arr_tup(arrs):
    return tuple(a.copy() for a in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    trp__jss = arrs.count
    func_text = 'def f(arrs):\n'
    func_text += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(trp__jss)))
    bxrzc__vxn = {}
    exec(func_text, {}, bxrzc__vxn)
    impl = bxrzc__vxn['f']
    return impl


def get_nan_bits(arr, ind):
    return 0


@overload(get_nan_bits, no_unliteral=True)
def overload_get_nan_bits(arr, ind):
    if arr == string_array_type:

        def impl_str(arr, ind):
            htydf__cdaei = get_null_bitmap_ptr(arr)
            return get_bit_bitmap(htydf__cdaei, ind)
        return impl_str
    if isinstance(arr, IntegerArrayType) or arr == boolean_array:

        def impl(arr, ind):
            return bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr.
                _null_bitmap, ind)
        return impl
    return lambda arr, ind: False


def get_nan_bits_tup(arr_tup, ind):
    return tuple(get_nan_bits(arr, ind) for arr in arr_tup)


@overload(get_nan_bits_tup, no_unliteral=True)
def overload_get_nan_bits_tup(arr_tup, ind):
    trp__jss = arr_tup.count
    func_text = 'def f(arr_tup, ind):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'get_nan_bits(arr_tup[{}], ind)'.format(i) for i in range(trp__jss)
        ]), ',' if trp__jss == 1 else '')
    bxrzc__vxn = {}
    exec(func_text, {'get_nan_bits': get_nan_bits}, bxrzc__vxn)
    impl = bxrzc__vxn['f']
    return impl


def set_nan_bits(arr, ind, na_val):
    return 0


@overload(set_nan_bits, no_unliteral=True)
def overload_set_nan_bits(arr, ind, na_val):
    if arr == string_array_type:

        def impl_str(arr, ind, na_val):
            htydf__cdaei = get_null_bitmap_ptr(arr)
            set_bit_to(htydf__cdaei, ind, na_val)
        return impl_str
    if isinstance(arr, IntegerArrayType) or arr == boolean_array:

        def impl(arr, ind, na_val):
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, na_val)
        return impl
    return lambda arr, ind, na_val: None


def set_nan_bits_tup(arr_tup, ind, na_val):
    return tuple(set_nan_bits(arr, ind, na_val) for arr in arr_tup)


@overload(set_nan_bits_tup, no_unliteral=True)
def overload_set_nan_bits_tup(arr_tup, ind, na_val):
    trp__jss = arr_tup.count
    func_text = 'def f(arr_tup, ind, na_val):\n'
    for i in range(trp__jss):
        func_text += '  set_nan_bits(arr_tup[{}], ind, na_val[{}])\n'.format(i,
            i)
    func_text += '  return\n'
    bxrzc__vxn = {}
    exec(func_text, {'set_nan_bits': set_nan_bits}, bxrzc__vxn)
    impl = bxrzc__vxn['f']
    return impl
