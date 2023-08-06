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
        ftjvr__qjb = func.signature
        pnonn__tyjb = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        efhyq__tiayx = cgutils.get_or_insert_function(builder.module,
            pnonn__tyjb, sym._literal_value)
        builder.call(efhyq__tiayx, [context.get_constant_null(ftjvr__qjb.
            args[0]), context.get_constant_null(ftjvr__qjb.args[1]),
            context.get_constant_null(ftjvr__qjb.args[2]), context.
            get_constant_null(ftjvr__qjb.args[3]), context.
            get_constant_null(ftjvr__qjb.args[4]), context.
            get_constant_null(ftjvr__qjb.args[5]), context.get_constant(
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
        self.left_cond_cols = set(akwf__jbdwe for akwf__jbdwe in left_vars.
            keys() if f'(left.{akwf__jbdwe})' in gen_cond_expr)
        self.right_cond_cols = set(akwf__jbdwe for akwf__jbdwe in
            right_vars.keys() if f'(right.{akwf__jbdwe})' in gen_cond_expr)
        vxclb__qgp = set(left_keys) & set(right_keys)
        fjb__pgn = set(left_vars.keys()) & set(right_vars.keys())
        xllm__tkf = fjb__pgn - vxclb__qgp
        vect_same_key = []
        n_keys = len(left_keys)
        for afzpv__hryko in range(n_keys):
            mgvtv__zlwc = left_keys[afzpv__hryko]
            rssnn__rdcx = right_keys[afzpv__hryko]
            vect_same_key.append(mgvtv__zlwc == rssnn__rdcx)
        self.vect_same_key = vect_same_key
        self.column_origins = {(str(akwf__jbdwe) + suffix_x if akwf__jbdwe in
            xllm__tkf else akwf__jbdwe): ('left', akwf__jbdwe) for
            akwf__jbdwe in left_vars.keys()}
        self.column_origins.update({(str(akwf__jbdwe) + suffix_y if 
            akwf__jbdwe in xllm__tkf else akwf__jbdwe): ('right',
            akwf__jbdwe) for akwf__jbdwe in right_vars.keys()})
        if '$_bodo_index_' in xllm__tkf:
            xllm__tkf.remove('$_bodo_index_')
        self.add_suffix = xllm__tkf

    def __repr__(self):
        mcx__cewv = ''
        for akwf__jbdwe, vlcs__oblps in self.out_data_vars.items():
            mcx__cewv += "'{}':{}, ".format(akwf__jbdwe, vlcs__oblps.name)
        cmjp__lnrl = '{}{{{}}}'.format(self.df_out, mcx__cewv)
        sha__nxe = ''
        for akwf__jbdwe, vlcs__oblps in self.left_vars.items():
            sha__nxe += "'{}':{}, ".format(akwf__jbdwe, vlcs__oblps.name)
        ohrbq__wxojv = '{}{{{}}}'.format(self.left_df, sha__nxe)
        sha__nxe = ''
        for akwf__jbdwe, vlcs__oblps in self.right_vars.items():
            sha__nxe += "'{}':{}, ".format(akwf__jbdwe, vlcs__oblps.name)
        tnm__vkbvl = '{}{{{}}}'.format(self.right_df, sha__nxe)
        return 'join [{}={}]: {} , {}, {}'.format(self.left_keys, self.
            right_keys, cmjp__lnrl, ohrbq__wxojv, tnm__vkbvl)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    ruysv__nvsb = []
    assert len(join_node.out_data_vars) > 0, 'empty join in array analysis'
    ort__lll = []
    wqz__ztcrs = list(join_node.left_vars.values())
    for hmxvj__gymdv in wqz__ztcrs:
        ufgkx__quysg = typemap[hmxvj__gymdv.name]
        krse__vjkj = equiv_set.get_shape(hmxvj__gymdv)
        if krse__vjkj:
            ort__lll.append(krse__vjkj[0])
    if len(ort__lll) > 1:
        equiv_set.insert_equiv(*ort__lll)
    ort__lll = []
    wqz__ztcrs = list(join_node.right_vars.values())
    for hmxvj__gymdv in wqz__ztcrs:
        ufgkx__quysg = typemap[hmxvj__gymdv.name]
        krse__vjkj = equiv_set.get_shape(hmxvj__gymdv)
        if krse__vjkj:
            ort__lll.append(krse__vjkj[0])
    if len(ort__lll) > 1:
        equiv_set.insert_equiv(*ort__lll)
    ort__lll = []
    for hmxvj__gymdv in join_node.out_data_vars.values():
        ufgkx__quysg = typemap[hmxvj__gymdv.name]
        mql__utfug = array_analysis._gen_shape_call(equiv_set, hmxvj__gymdv,
            ufgkx__quysg.ndim, None, ruysv__nvsb)
        equiv_set.insert_equiv(hmxvj__gymdv, mql__utfug)
        ort__lll.append(mql__utfug[0])
        equiv_set.define(hmxvj__gymdv, set())
    if len(ort__lll) > 1:
        equiv_set.insert_equiv(*ort__lll)
    return [], ruysv__nvsb


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    thg__kkv = Distribution.OneD
    egyy__fqmm = Distribution.OneD
    for hmxvj__gymdv in join_node.left_vars.values():
        thg__kkv = Distribution(min(thg__kkv.value, array_dists[
            hmxvj__gymdv.name].value))
    for hmxvj__gymdv in join_node.right_vars.values():
        egyy__fqmm = Distribution(min(egyy__fqmm.value, array_dists[
            hmxvj__gymdv.name].value))
    wtngu__fgzc = Distribution.OneD_Var
    for hmxvj__gymdv in join_node.out_data_vars.values():
        if hmxvj__gymdv.name in array_dists:
            wtngu__fgzc = Distribution(min(wtngu__fgzc.value, array_dists[
                hmxvj__gymdv.name].value))
    hgck__oavy = Distribution(min(wtngu__fgzc.value, thg__kkv.value))
    waum__xnu = Distribution(min(wtngu__fgzc.value, egyy__fqmm.value))
    wtngu__fgzc = Distribution(max(hgck__oavy.value, waum__xnu.value))
    for hmxvj__gymdv in join_node.out_data_vars.values():
        array_dists[hmxvj__gymdv.name] = wtngu__fgzc
    if wtngu__fgzc != Distribution.OneD_Var:
        thg__kkv = wtngu__fgzc
        egyy__fqmm = wtngu__fgzc
    for hmxvj__gymdv in join_node.left_vars.values():
        array_dists[hmxvj__gymdv.name] = thg__kkv
    for hmxvj__gymdv in join_node.right_vars.values():
        array_dists[hmxvj__gymdv.name] = egyy__fqmm
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def join_typeinfer(join_node, typeinferer):
    vxclb__qgp = set(join_node.left_keys) & set(join_node.right_keys)
    fjb__pgn = set(join_node.left_vars.keys()) & set(join_node.right_vars.
        keys())
    xllm__tkf = fjb__pgn - vxclb__qgp
    for phkhc__rrjj, fuu__ifona in join_node.out_data_vars.items():
        if join_node.indicator and phkhc__rrjj == '_merge':
            continue
        if not phkhc__rrjj in join_node.column_origins:
            raise BodoError('join(): The variable ' + phkhc__rrjj +
                ' is absent from the output')
        rbkrf__tpfry = join_node.column_origins[phkhc__rrjj]
        if rbkrf__tpfry[0] == 'left':
            hmxvj__gymdv = join_node.left_vars[rbkrf__tpfry[1]]
        else:
            hmxvj__gymdv = join_node.right_vars[rbkrf__tpfry[1]]
        typeinferer.constraints.append(typeinfer.Propagate(dst=fuu__ifona.
            name, src=hmxvj__gymdv.name, loc=join_node.loc))
    return


typeinfer.typeinfer_extensions[Join] = join_typeinfer


def visit_vars_join(join_node, callback, cbdata):
    if debug_prints():
        print('visiting join vars for:', join_node)
        print('cbdata: ', sorted(cbdata.items()))
    for wnpu__wgc in list(join_node.left_vars.keys()):
        join_node.left_vars[wnpu__wgc] = visit_vars_inner(join_node.
            left_vars[wnpu__wgc], callback, cbdata)
    for wnpu__wgc in list(join_node.right_vars.keys()):
        join_node.right_vars[wnpu__wgc] = visit_vars_inner(join_node.
            right_vars[wnpu__wgc], callback, cbdata)
    for wnpu__wgc in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[wnpu__wgc] = visit_vars_inner(join_node.
            out_data_vars[wnpu__wgc], callback, cbdata)


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    fda__yuv = []
    bhiqe__ajc = True
    for wnpu__wgc, hmxvj__gymdv in join_node.out_data_vars.items():
        if hmxvj__gymdv.name in lives:
            bhiqe__ajc = False
            continue
        if wnpu__wgc == '$_bodo_index_':
            continue
        if join_node.indicator and wnpu__wgc == '_merge':
            fda__yuv.append('_merge')
            join_node.indicator = False
            continue
        hik__qbn, bpg__monz = join_node.column_origins[wnpu__wgc]
        if (hik__qbn == 'left' and bpg__monz not in join_node.left_keys and
            bpg__monz not in join_node.left_cond_cols):
            join_node.left_vars.pop(bpg__monz)
            fda__yuv.append(wnpu__wgc)
        if (hik__qbn == 'right' and bpg__monz not in join_node.right_keys and
            bpg__monz not in join_node.right_cond_cols):
            join_node.right_vars.pop(bpg__monz)
            fda__yuv.append(wnpu__wgc)
    for cname in fda__yuv:
        join_node.out_data_vars.pop(cname)
    if bhiqe__ajc:
        return None
    return join_node


ir_utils.remove_dead_extensions[Join] = remove_dead_join


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({vlcs__oblps.name for vlcs__oblps in join_node.left_vars
        .values()})
    use_set.update({vlcs__oblps.name for vlcs__oblps in join_node.
        right_vars.values()})
    def_set.update({vlcs__oblps.name for vlcs__oblps in join_node.
        out_data_vars.values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    fzgw__bmpr = set(vlcs__oblps.name for vlcs__oblps in join_node.
        out_data_vars.values())
    return set(), fzgw__bmpr


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for wnpu__wgc in list(join_node.left_vars.keys()):
        join_node.left_vars[wnpu__wgc] = replace_vars_inner(join_node.
            left_vars[wnpu__wgc], var_dict)
    for wnpu__wgc in list(join_node.right_vars.keys()):
        join_node.right_vars[wnpu__wgc] = replace_vars_inner(join_node.
            right_vars[wnpu__wgc], var_dict)
    for wnpu__wgc in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[wnpu__wgc] = replace_vars_inner(join_node.
            out_data_vars[wnpu__wgc], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for hmxvj__gymdv in join_node.out_data_vars.values():
        definitions[hmxvj__gymdv.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    n_keys = len(join_node.left_keys)
    jif__cfhgo = tuple(join_node.left_vars[akwf__jbdwe] for akwf__jbdwe in
        join_node.left_keys)
    jrolf__foto = tuple(join_node.right_vars[akwf__jbdwe] for akwf__jbdwe in
        join_node.right_keys)
    gnp__jpnlu = tuple(join_node.left_vars.keys())
    rmr__xucuo = tuple(join_node.right_vars.keys())
    brt__dnvui = ()
    nfj__kovth = ()
    optional_column = False
    if (join_node.left_index and not join_node.right_index and not
        join_node.is_join):
        qnc__str = join_node.right_keys[0]
        if qnc__str in gnp__jpnlu:
            nfj__kovth = qnc__str,
            brt__dnvui = join_node.right_vars[qnc__str],
            optional_column = True
    if (join_node.right_index and not join_node.left_index and not
        join_node.is_join):
        qnc__str = join_node.left_keys[0]
        if qnc__str in rmr__xucuo:
            nfj__kovth = qnc__str,
            brt__dnvui = join_node.left_vars[qnc__str],
            optional_column = True
    oool__lrozp = tuple(join_node.out_data_vars[cname] for cname in nfj__kovth)
    fcy__dqajz = tuple(vlcs__oblps for fymze__mnyw, vlcs__oblps in sorted(
        join_node.left_vars.items(), key=lambda a: str(a[0])) if 
        fymze__mnyw not in join_node.left_keys)
    mrew__pjbu = tuple(vlcs__oblps for fymze__mnyw, vlcs__oblps in sorted(
        join_node.right_vars.items(), key=lambda a: str(a[0])) if 
        fymze__mnyw not in join_node.right_keys)
    pxfs__veb = brt__dnvui + jif__cfhgo + jrolf__foto + fcy__dqajz + mrew__pjbu
    nvuji__pxrxl = tuple(typemap[vlcs__oblps.name] for vlcs__oblps in pxfs__veb
        )
    jnlvs__chili = tuple('opti_c' + str(i) for i in range(len(brt__dnvui)))
    left_other_names = tuple('t1_c' + str(i) for i in range(len(fcy__dqajz)))
    right_other_names = tuple('t2_c' + str(i) for i in range(len(mrew__pjbu)))
    left_other_types = tuple([typemap[akwf__jbdwe.name] for akwf__jbdwe in
        fcy__dqajz])
    right_other_types = tuple([typemap[akwf__jbdwe.name] for akwf__jbdwe in
        mrew__pjbu])
    left_key_names = tuple('t1_key' + str(i) for i in range(n_keys))
    right_key_names = tuple('t2_key' + str(i) for i in range(n_keys))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}{}, {},{}{}{}):\n'.format('{},'.format(
        jnlvs__chili[0]) if len(jnlvs__chili) == 1 else '', ','.join(
        left_key_names), ','.join(right_key_names), ','.join(
        left_other_names), ',' if len(left_other_names) != 0 else '', ','.
        join(right_other_names))
    left_key_types = tuple(typemap[vlcs__oblps.name] for vlcs__oblps in
        jif__cfhgo)
    right_key_types = tuple(typemap[vlcs__oblps.name] for vlcs__oblps in
        jrolf__foto)
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
    bqg__wzf = []
    for cname in join_node.left_keys:
        if cname in join_node.add_suffix:
            brqv__ppo = str(cname) + join_node.suffix_x
        else:
            brqv__ppo = cname
        assert brqv__ppo in join_node.out_data_vars
        bqg__wzf.append(join_node.out_data_vars[brqv__ppo])
    for i, cname in enumerate(join_node.right_keys):
        if not join_node.vect_same_key[i] and not join_node.is_join:
            if cname in join_node.add_suffix:
                brqv__ppo = str(cname) + join_node.suffix_y
            else:
                brqv__ppo = cname
            assert brqv__ppo in join_node.out_data_vars
            bqg__wzf.append(join_node.out_data_vars[brqv__ppo])

    def _get_out_col_var(cname, is_left):
        if cname in join_node.add_suffix:
            if is_left:
                brqv__ppo = str(cname) + join_node.suffix_x
            else:
                brqv__ppo = str(cname) + join_node.suffix_y
        else:
            brqv__ppo = cname
        return join_node.out_data_vars[brqv__ppo]
    enis__dfi = oool__lrozp + tuple(bqg__wzf)
    enis__dfi += tuple(_get_out_col_var(fymze__mnyw, True) for fymze__mnyw,
        vlcs__oblps in sorted(join_node.left_vars.items(), key=lambda a:
        str(a[0])) if fymze__mnyw not in join_node.left_keys)
    enis__dfi += tuple(_get_out_col_var(fymze__mnyw, False) for fymze__mnyw,
        vlcs__oblps in sorted(join_node.right_vars.items(), key=lambda a:
        str(a[0])) if fymze__mnyw not in join_node.right_keys)
    if join_node.indicator:
        enis__dfi += _get_out_col_var('_merge', False),
    isdb__craau = [('t3_c' + str(i)) for i in range(len(enis__dfi))]
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
            right_parallel, glbs, [typemap[vlcs__oblps.name] for
            vlcs__oblps in enis__dfi], join_node.loc, join_node.indicator,
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
        func_text += f'    {isdb__craau[idx]} = opti_0\n'
        idx += 1
    for i in range(n_keys):
        func_text += f'    {isdb__craau[idx]} = t1_keys_{i}\n'
        idx += 1
    for i in range(n_keys):
        if not join_node.vect_same_key[i] and not join_node.is_join:
            func_text += f'    {isdb__craau[idx]} = t2_keys_{i}\n'
            idx += 1
    for i in range(len(left_other_names)):
        func_text += f'    {isdb__craau[idx]} = left_{i}\n'
        idx += 1
    for i in range(len(right_other_names)):
        func_text += f'    {isdb__craau[idx]} = right_{i}\n'
        idx += 1
    if join_node.indicator:
        func_text += f'    {isdb__craau[idx]} = indicator_col\n'
        idx += 1
    owq__tkzps = {}
    exec(func_text, {}, owq__tkzps)
    nkr__yvr = owq__tkzps['f']
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
    lphku__lemmb = compile_to_numba_ir(nkr__yvr, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=nvuji__pxrxl, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(lphku__lemmb, pxfs__veb)
    mrjfx__kkyg = lphku__lemmb.body[:-3]
    for i in range(len(enis__dfi)):
        mrjfx__kkyg[-len(enis__dfi) + i].target = enis__dfi[i]
    return mrjfx__kkyg


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    etrf__gqopj = next_label()
    tce__fojvb = _get_col_to_ind(join_node.left_keys, join_node.left_vars)
    hhec__dgx = _get_col_to_ind(join_node.right_keys, join_node.right_vars)
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{etrf__gqopj}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
"""
    func_text += '  if is_null_pointer(left_table):\n'
    func_text += '    return False\n'
    expr, func_text, left_col_nums = _replace_column_accesses(expr,
        tce__fojvb, typemap, join_node.left_vars, table_getitem_funcs,
        func_text, 'left', len(join_node.left_keys), na_check_name)
    expr, func_text, right_col_nums = _replace_column_accesses(expr,
        hhec__dgx, typemap, join_node.right_vars, table_getitem_funcs,
        func_text, 'right', len(join_node.right_keys), na_check_name)
    func_text += f'  return {expr}'
    owq__tkzps = {}
    exec(func_text, table_getitem_funcs, owq__tkzps)
    bem__bybr = owq__tkzps[f'bodo_join_gen_cond{etrf__gqopj}']
    afhf__tjnc = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    emn__oivzv = numba.cfunc(afhf__tjnc, nopython=True)(bem__bybr)
    join_gen_cond_cfunc[emn__oivzv.native_name] = emn__oivzv
    join_gen_cond_cfunc_addr[emn__oivzv.native_name] = emn__oivzv.address
    return emn__oivzv, left_col_nums, right_col_nums


def _replace_column_accesses(expr, col_to_ind, typemap, col_vars,
    table_getitem_funcs, func_text, table_name, n_keys, na_check_name):
    xnbo__jzzos = []
    for akwf__jbdwe, kwp__okre in col_to_ind.items():
        cname = f'({table_name}.{akwf__jbdwe})'
        if cname not in expr:
            continue
        dty__lpfkr = f'getitem_{table_name}_val_{kwp__okre}'
        wwswj__nnzlc = f'_bodo_{table_name}_val_{kwp__okre}'
        fsxof__cqz = typemap[col_vars[akwf__jbdwe].name].dtype
        if fsxof__cqz == types.unicode_type:
            func_text += f"""  {wwswj__nnzlc}, {wwswj__nnzlc}_size = {dty__lpfkr}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {wwswj__nnzlc} = bodo.libs.str_arr_ext.decode_utf8({wwswj__nnzlc}, {wwswj__nnzlc}_size)
"""
        else:
            func_text += (
                f'  {wwswj__nnzlc} = {dty__lpfkr}({table_name}_data1, {table_name}_ind)\n'
                )
        table_getitem_funcs[dty__lpfkr
            ] = bodo.libs.array._gen_row_access_intrinsic(fsxof__cqz, kwp__okre
            )
        expr = expr.replace(cname, wwswj__nnzlc)
        xprar__xhlbv = f'({na_check_name}.{table_name}.{akwf__jbdwe})'
        if xprar__xhlbv in expr:
            hoy__dsczg = typemap[col_vars[akwf__jbdwe].name]
            fhnfc__plnps = f'nacheck_{table_name}_val_{kwp__okre}'
            scgl__qybcf = f'_bodo_isna_{table_name}_val_{kwp__okre}'
            if isinstance(hoy__dsczg, bodo.libs.int_arr_ext.IntegerArrayType
                ) or hoy__dsczg in [bodo.libs.bool_arr_ext.boolean_array,
                bodo.libs.str_arr_ext.string_array_type]:
                func_text += f"""  {scgl__qybcf} = {fhnfc__plnps}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += f"""  {scgl__qybcf} = {fhnfc__plnps}({table_name}_data1, {table_name}_ind)
"""
            table_getitem_funcs[fhnfc__plnps
                ] = bodo.libs.array._gen_row_na_check_intrinsic(hoy__dsczg,
                kwp__okre)
            expr = expr.replace(xprar__xhlbv, scgl__qybcf)
        if kwp__okre >= n_keys:
            xnbo__jzzos.append(kwp__okre)
    return expr, func_text, xnbo__jzzos


def _get_col_to_ind(key_names, col_vars):
    n_keys = len(key_names)
    col_to_ind = {akwf__jbdwe: i for i, akwf__jbdwe in enumerate(key_names)}
    i = n_keys
    for akwf__jbdwe in sorted(col_vars, key=lambda a: str(a)):
        if akwf__jbdwe in key_names:
            continue
        col_to_ind[akwf__jbdwe] = i
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
    ryfn__zduv = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[vlcs__oblps.name] in ryfn__zduv for
        vlcs__oblps in join_node.left_vars.values())
    right_parallel = all(array_dists[vlcs__oblps.name] in ryfn__zduv for
        vlcs__oblps in join_node.right_vars.values())
    if not left_parallel:
        assert not any(array_dists[vlcs__oblps.name] in ryfn__zduv for
            vlcs__oblps in join_node.left_vars.values())
    if not right_parallel:
        assert not any(array_dists[vlcs__oblps.name] in ryfn__zduv for
            vlcs__oblps in join_node.right_vars.values())
    if left_parallel or right_parallel:
        assert all(array_dists[vlcs__oblps.name] in ryfn__zduv for
            vlcs__oblps in join_node.out_data_vars.values())
    return left_parallel, right_parallel


def _gen_local_hash_join(optional_column, left_key_names, right_key_names,
    left_key_types, right_key_types, left_other_names, right_other_names,
    left_other_types, right_other_types, vect_same_key, is_left, is_right,
    is_join, left_parallel, right_parallel, glbs, out_types, loc, indicator,
    is_na_equal, general_cond_cfunc, left_col_nums, right_col_nums):

    def needs_typechange(in_type, need_nullable, is_same_key):
        return isinstance(in_type, types.Array) and not is_dtype_nullable(
            in_type.dtype) and need_nullable and not is_same_key
    ywci__duz = []
    for i in range(len(left_key_names)):
        dfw__whasg = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
        ywci__duz.append(needs_typechange(dfw__whasg, is_right,
            vect_same_key[i]))
    for i in range(len(left_other_names)):
        ywci__duz.append(needs_typechange(left_other_types[i], is_right, False)
            )
    for i in range(len(right_key_names)):
        if not vect_same_key[i] and not is_join:
            dfw__whasg = _match_join_key_types(left_key_types[i],
                right_key_types[i], loc)
            ywci__duz.append(needs_typechange(dfw__whasg, is_left, False))
    for i in range(len(right_other_names)):
        ywci__duz.append(needs_typechange(right_other_types[i], is_left, False)
            )

    def get_out_type(idx, in_type, in_name, need_nullable, is_same_key):
        if isinstance(in_type, types.Array) and not is_dtype_nullable(in_type
            .dtype) and need_nullable and not is_same_key:
            if isinstance(in_type.dtype, types.Integer):
                xbzr__wvnme = IntDtype(in_type.dtype).name
                assert xbzr__wvnme.endswith('Dtype()')
                xbzr__wvnme = xbzr__wvnme[:-7]
                ssi__tbjks = f"""    typ_{idx} = bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype="{xbzr__wvnme}"))
"""
                dlwl__jfqbp = f'typ_{idx}'
            else:
                assert in_type.dtype == types.bool_, 'unexpected non-nullable type in join'
                ssi__tbjks = (
                    f'    typ_{idx} = bodo.libs.bool_arr_ext.alloc_bool_array(1)\n'
                    )
                dlwl__jfqbp = f'typ_{idx}'
        else:
            ssi__tbjks = ''
            dlwl__jfqbp = in_name
        return ssi__tbjks, dlwl__jfqbp
    n_keys = len(left_key_names)
    func_text = '    # beginning of _gen_local_hash_join\n'
    bfren__baf = []
    for i in range(n_keys):
        bfren__baf.append('t1_keys[{}]'.format(i))
    for i in range(len(left_other_names)):
        bfren__baf.append('data_left[{}]'.format(i))
    func_text += '    info_list_total_l = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in bfren__baf))
    func_text += '    table_left = arr_info_list_to_table(info_list_total_l)\n'
    inw__ugon = []
    for i in range(n_keys):
        inw__ugon.append('t2_keys[{}]'.format(i))
    for i in range(len(right_other_names)):
        inw__ugon.append('data_right[{}]'.format(i))
    func_text += '    info_list_total_r = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in inw__ugon))
    func_text += (
        '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    func_text += '    vect_same_key = np.array([{}])\n'.format(','.join('1' if
        vpyd__ihsb else '0' for vpyd__ihsb in vect_same_key))
    func_text += '    vect_need_typechange = np.array([{}])\n'.format(','.
        join('1' if vpyd__ihsb else '0' for vpyd__ihsb in ywci__duz))
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
    for i, rhi__hjpny in enumerate(left_key_names):
        dfw__whasg = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
        jhzuq__zqmog = get_out_type(idx, dfw__whasg, f't1_keys[{i}]',
            is_right, vect_same_key[i])
        func_text += jhzuq__zqmog[0]
        glbs[f'out_type_{idx}'] = out_types[idx]
        if dfw__whasg != left_key_types[i]:
            func_text += f"""    t1_keys_{i} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {jhzuq__zqmog[1]}), out_type_{idx})
"""
        else:
            func_text += f"""    t1_keys_{i} = info_to_array(info_from_table(out_table, {idx}), {jhzuq__zqmog[1]})
"""
        idx += 1
    for i, rhi__hjpny in enumerate(left_other_names):
        jhzuq__zqmog = get_out_type(idx, left_other_types[i], rhi__hjpny,
            is_right, False)
        func_text += jhzuq__zqmog[0]
        func_text += (
            '    left_{} = info_to_array(info_from_table(out_table, {}), {})\n'
            .format(i, idx, jhzuq__zqmog[1]))
        idx += 1
    for i, rhi__hjpny in enumerate(right_key_names):
        if not vect_same_key[i] and not is_join:
            dfw__whasg = _match_join_key_types(left_key_types[i],
                right_key_types[i], loc)
            jhzuq__zqmog = get_out_type(idx, dfw__whasg, f't2_keys[{i}]',
                is_left, False)
            func_text += jhzuq__zqmog[0]
            glbs[f'out_type_{idx}'] = out_types[idx - len(left_other_names)]
            if dfw__whasg != right_key_types[i]:
                func_text += f"""    t2_keys_{i} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {jhzuq__zqmog[1]}), out_type_{idx})
"""
            else:
                func_text += f"""    t2_keys_{i} = info_to_array(info_from_table(out_table, {idx}), {jhzuq__zqmog[1]})
"""
            idx += 1
    for i, rhi__hjpny in enumerate(right_other_names):
        jhzuq__zqmog = get_out_type(idx, right_other_types[i], rhi__hjpny,
            is_left, False)
        func_text += jhzuq__zqmog[0]
        func_text += (
            '    right_{} = info_to_array(info_from_table(out_table, {}), {})\n'
            .format(i, idx, jhzuq__zqmog[1]))
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
    ucz__hqii = bodo.libs.distributed_api.get_size()
    xej__hqmj = alloc_pre_shuffle_metadata(key_arrs, data, ucz__hqii, False)
    fymze__mnyw = len(key_arrs[0])
    wkmcv__gpxf = np.empty(fymze__mnyw, np.int32)
    mysfl__wwef = arr_info_list_to_table([array_to_info(key_arrs[0])])
    vpnd__wrdp = 1
    bjl__onn = compute_node_partition_by_hash(mysfl__wwef, vpnd__wrdp,
        ucz__hqii)
    dretr__cky = np.empty(1, np.int32)
    rpsjh__kdwwd = info_to_array(info_from_table(bjl__onn, 0), dretr__cky)
    delete_table(bjl__onn)
    delete_table(mysfl__wwef)
    for i in range(fymze__mnyw):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = rpsjh__kdwwd[i]
        wkmcv__gpxf[i] = node_id
        update_shuffle_meta(xej__hqmj, node_id, i, key_arrs, data, False)
    shuffle_meta = finalize_shuffle_meta(key_arrs, data, xej__hqmj,
        ucz__hqii, False)
    for i in range(fymze__mnyw):
        node_id = wkmcv__gpxf[i]
        write_send_buff(shuffle_meta, node_id, i, key_arrs, data)
        shuffle_meta.tmp_offset[node_id] += 1
    ttox__uvqb = alltoallv_tup(key_arrs + data, shuffle_meta, key_arrs)
    bqg__wzf = _get_keys_tup(ttox__uvqb, key_arrs)
    yarej__xix = _get_data_tup(ttox__uvqb, key_arrs)
    return bqg__wzf, yarej__xix


@generated_jit(nopython=True, cache=True)
def parallel_shuffle(key_arrs, data):
    return parallel_join_impl


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    ucz__hqii = bodo.libs.distributed_api.get_size()
    tic__jkvx = np.empty(ucz__hqii, left_key_arrs[0].dtype)
    nptr__bge = np.empty(ucz__hqii, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(tic__jkvx, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(nptr__bge, left_key_arrs[0][-1])
    zvxzr__rfsh = np.zeros(ucz__hqii, np.int32)
    pagkl__qqi = np.zeros(ucz__hqii, np.int32)
    yljl__vsdk = np.zeros(ucz__hqii, np.int32)
    ntc__cgk = right_key_arrs[0][0]
    qrpu__zwo = right_key_arrs[0][-1]
    jnbt__esw = -1
    i = 0
    while i < ucz__hqii - 1 and nptr__bge[i] < ntc__cgk:
        i += 1
    while i < ucz__hqii and tic__jkvx[i] <= qrpu__zwo:
        jnbt__esw, zqql__vwvy = _count_overlap(right_key_arrs[0], tic__jkvx
            [i], nptr__bge[i])
        if jnbt__esw != 0:
            jnbt__esw -= 1
            zqql__vwvy += 1
        zvxzr__rfsh[i] = zqql__vwvy
        pagkl__qqi[i] = jnbt__esw
        i += 1
    while i < ucz__hqii:
        zvxzr__rfsh[i] = 1
        pagkl__qqi[i] = len(right_key_arrs[0]) - 1
        i += 1
    bodo.libs.distributed_api.alltoall(zvxzr__rfsh, yljl__vsdk, 1)
    nsllt__obusf = yljl__vsdk.sum()
    ahs__vzgcb = np.empty(nsllt__obusf, right_key_arrs[0].dtype)
    lqkf__ieuxe = alloc_arr_tup(nsllt__obusf, right_data)
    pbg__jflc = bodo.ir.join.calc_disp(yljl__vsdk)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], ahs__vzgcb,
        zvxzr__rfsh, yljl__vsdk, pagkl__qqi, pbg__jflc)
    bodo.libs.distributed_api.alltoallv_tup(right_data, lqkf__ieuxe,
        zvxzr__rfsh, yljl__vsdk, pagkl__qqi, pbg__jflc)
    return (ahs__vzgcb,), lqkf__ieuxe


@numba.njit
def _count_overlap(r_key_arr, start, end):
    zqql__vwvy = 0
    jnbt__esw = 0
    mnuq__gnj = 0
    while mnuq__gnj < len(r_key_arr) and r_key_arr[mnuq__gnj] < start:
        jnbt__esw += 1
        mnuq__gnj += 1
    while mnuq__gnj < len(r_key_arr) and start <= r_key_arr[mnuq__gnj] <= end:
        mnuq__gnj += 1
        zqql__vwvy += 1
    return jnbt__esw, zqql__vwvy


def write_send_buff(shuffle_meta, node_id, i, key_arrs, data):
    return i


@overload(write_send_buff, no_unliteral=True)
def write_data_buff_overload(meta, node_id, i, key_arrs, data):
    func_text = 'def f(meta, node_id, i, key_arrs, data):\n'
    func_text += (
        '  w_ind = meta.send_disp[node_id] + meta.tmp_offset[node_id]\n')
    n_keys = len(key_arrs.types)
    for i, ufgkx__quysg in enumerate(key_arrs.types + data.types):
        arr = 'key_arrs[{}]'.format(i) if i < n_keys else 'data[{}]'.format(
            i - n_keys)
        if not ufgkx__quysg in (string_type, string_array_type,
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
    owq__tkzps = {}
    exec(func_text, {'str_copy_ptr': str_copy_ptr, 'get_null_bitmap_ptr':
        get_null_bitmap_ptr, 'get_bit_bitmap': get_bit_bitmap, 'set_bit_to':
        set_bit_to, 'get_str_arr_item_length': get_str_arr_item_length,
        'get_str_arr_item_ptr': get_str_arr_item_ptr}, owq__tkzps)
    sqqf__pzbbu = owq__tkzps['f']
    return sqqf__pzbbu


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    fbx__xpzty = np.empty_like(arr)
    fbx__xpzty[0] = 0
    for i in range(1, len(arr)):
        fbx__xpzty[i] = fbx__xpzty[i - 1] + arr[i - 1]
    return fbx__xpzty


def ensure_capacity(arr, new_size):
    qxy__ppopa = arr
    xezh__javyi = len(arr)
    if xezh__javyi < new_size:
        hrxe__gwq = 2 * xezh__javyi
        qxy__ppopa = bodo.utils.utils.alloc_type(hrxe__gwq, arr)
        qxy__ppopa[:xezh__javyi] = arr
    return qxy__ppopa


@overload(ensure_capacity, no_unliteral=True)
def ensure_capacity_overload(arr, new_size):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return ensure_capacity
    assert isinstance(arr, types.BaseTuple)
    zqql__vwvy = arr.count
    func_text = 'def f(arr, new_size):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'ensure_capacity(arr[{}], new_size)'.format(i) for i in range(
        zqql__vwvy)]), ',' if zqql__vwvy == 1 else '')
    owq__tkzps = {}
    exec(func_text, {'ensure_capacity': ensure_capacity}, owq__tkzps)
    hnfw__sfugs = owq__tkzps['f']
    return hnfw__sfugs


@numba.njit
def ensure_capacity_str(arr, new_size, n_chars):
    qxy__ppopa = arr
    xezh__javyi = len(arr)
    qhb__pkm = num_total_chars(arr)
    ymdpk__mskgp = getitem_str_offset(arr, new_size - 1) + n_chars
    if xezh__javyi < new_size or ymdpk__mskgp > qhb__pkm:
        hrxe__gwq = int(2 * xezh__javyi if xezh__javyi < new_size else
            xezh__javyi)
        lcg__hbiog = int(2 * qhb__pkm + n_chars if ymdpk__mskgp > qhb__pkm else
            qhb__pkm)
        qxy__ppopa = pre_alloc_string_array(hrxe__gwq, lcg__hbiog)
        copy_str_arr_slice(qxy__ppopa, arr, new_size - 1)
    return qxy__ppopa


def trim_arr_tup(data, new_size):
    return data


@overload(trim_arr_tup, no_unliteral=True)
def trim_arr_tup_overload(data, new_size):
    assert isinstance(data, types.BaseTuple)
    zqql__vwvy = data.count
    func_text = 'def f(data, new_size):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'trim_arr(data[{}], new_size)'.format(i) for i in range(zqql__vwvy)
        ]), ',' if zqql__vwvy == 1 else '')
    owq__tkzps = {}
    exec(func_text, {'trim_arr': trim_arr}, owq__tkzps)
    hnfw__sfugs = owq__tkzps['f']
    return hnfw__sfugs


def copy_elem_buff(arr, ind, val):
    qxy__ppopa = ensure_capacity(arr, ind + 1)
    qxy__ppopa[ind] = val
    return qxy__ppopa


@overload(copy_elem_buff, no_unliteral=True)
def copy_elem_buff_overload(arr, ind, val):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return copy_elem_buff
    assert arr == string_array_type

    def copy_elem_buff_str(arr, ind, val):
        qxy__ppopa = ensure_capacity_str(arr, ind + 1, get_utf8_size(val))
        qxy__ppopa[ind] = val
        return qxy__ppopa
    return copy_elem_buff_str


def copy_elem_buff_tup(arr, ind, val):
    return arr


@overload(copy_elem_buff_tup, no_unliteral=True)
def copy_elem_buff_tup_overload(data, ind, val):
    assert isinstance(data, types.BaseTuple)
    zqql__vwvy = data.count
    func_text = 'def f(data, ind, val):\n'
    for i in range(zqql__vwvy):
        func_text += ('  arr_{} = copy_elem_buff(data[{}], ind, val[{}])\n'
            .format(i, i, i))
    func_text += '  return ({}{})\n'.format(','.join(['arr_{}'.format(i) for
        i in range(zqql__vwvy)]), ',' if zqql__vwvy == 1 else '')
    owq__tkzps = {}
    exec(func_text, {'copy_elem_buff': copy_elem_buff}, owq__tkzps)
    qaujm__wczs = owq__tkzps['f']
    return qaujm__wczs


def trim_arr(arr, size):
    return arr[:size]


@overload(trim_arr, no_unliteral=True)
def trim_arr_overload(arr, size):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return trim_arr
    assert arr == string_array_type

    def trim_arr_str(arr, size):
        qxy__ppopa = pre_alloc_string_array(size, np.int64(
            getitem_str_offset(arr, size)))
        copy_str_arr_slice(qxy__ppopa, arr, size)
        return qxy__ppopa
    return trim_arr_str


def setnan_elem_buff(arr, ind):
    qxy__ppopa = ensure_capacity(arr, ind + 1)
    bodo.libs.array_kernels.setna(qxy__ppopa, ind)
    return qxy__ppopa


@overload(setnan_elem_buff, no_unliteral=True)
def setnan_elem_buff_overload(arr, ind):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return setnan_elem_buff
    assert arr == string_array_type

    def setnan_elem_buff_str(arr, ind):
        qxy__ppopa = ensure_capacity_str(arr, ind + 1, 0)
        qxy__ppopa[ind] = ''
        bodo.libs.array_kernels.setna(qxy__ppopa, ind)
        return qxy__ppopa
    return setnan_elem_buff_str


def setnan_elem_buff_tup(arr, ind):
    return arr


@overload(setnan_elem_buff_tup, no_unliteral=True)
def setnan_elem_buff_tup_overload(data, ind):
    assert isinstance(data, types.BaseTuple)
    zqql__vwvy = data.count
    func_text = 'def f(data, ind):\n'
    for i in range(zqql__vwvy):
        func_text += '  arr_{} = setnan_elem_buff(data[{}], ind)\n'.format(i, i
            )
    func_text += '  return ({}{})\n'.format(','.join(['arr_{}'.format(i) for
        i in range(zqql__vwvy)]), ',' if zqql__vwvy == 1 else '')
    owq__tkzps = {}
    exec(func_text, {'setnan_elem_buff': setnan_elem_buff}, owq__tkzps)
    qaujm__wczs = owq__tkzps['f']
    return qaujm__wczs


@generated_jit(nopython=True, cache=True)
def _check_ind_if_hashed(right_keys, r_ind, l_key):
    if right_keys == types.Tuple((types.intp[::1],)):
        return lambda right_keys, r_ind, l_key: r_ind

    def _impl(right_keys, r_ind, l_key):
        cvip__rbvcm = getitem_arr_tup(right_keys, r_ind)
        if cvip__rbvcm != l_key:
            return -1
        return r_ind
    return _impl


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    jdeov__awb = len(left_keys[0])
    wtzjz__sdhb = len(right_keys[0])
    kxeir__qczwc = alloc_arr_tup(jdeov__awb, left_keys)
    equaa__ycrj = alloc_arr_tup(jdeov__awb, right_keys)
    enrg__uzq = alloc_arr_tup(jdeov__awb, data_left)
    eide__fgkyu = alloc_arr_tup(jdeov__awb, data_right)
    kunl__dbsjn = 0
    tqhf__zhswj = 0
    for kunl__dbsjn in range(jdeov__awb):
        if tqhf__zhswj < 0:
            tqhf__zhswj = 0
        while tqhf__zhswj < wtzjz__sdhb and getitem_arr_tup(right_keys,
            tqhf__zhswj) <= getitem_arr_tup(left_keys, kunl__dbsjn):
            tqhf__zhswj += 1
        tqhf__zhswj -= 1
        setitem_arr_tup(kxeir__qczwc, kunl__dbsjn, getitem_arr_tup(
            left_keys, kunl__dbsjn))
        setitem_arr_tup(enrg__uzq, kunl__dbsjn, getitem_arr_tup(data_left,
            kunl__dbsjn))
        if tqhf__zhswj >= 0:
            setitem_arr_tup(equaa__ycrj, kunl__dbsjn, getitem_arr_tup(
                right_keys, tqhf__zhswj))
            setitem_arr_tup(eide__fgkyu, kunl__dbsjn, getitem_arr_tup(
                data_right, tqhf__zhswj))
        else:
            bodo.libs.array_kernels.setna_tup(equaa__ycrj, kunl__dbsjn)
            bodo.libs.array_kernels.setna_tup(eide__fgkyu, kunl__dbsjn)
    return kxeir__qczwc, equaa__ycrj, enrg__uzq, eide__fgkyu


def copy_arr_tup(arrs):
    return tuple(a.copy() for a in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    zqql__vwvy = arrs.count
    func_text = 'def f(arrs):\n'
    func_text += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(zqql__vwvy)))
    owq__tkzps = {}
    exec(func_text, {}, owq__tkzps)
    impl = owq__tkzps['f']
    return impl


def get_nan_bits(arr, ind):
    return 0


@overload(get_nan_bits, no_unliteral=True)
def overload_get_nan_bits(arr, ind):
    if arr == string_array_type:

        def impl_str(arr, ind):
            chxrb__jpj = get_null_bitmap_ptr(arr)
            return get_bit_bitmap(chxrb__jpj, ind)
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
    zqql__vwvy = arr_tup.count
    func_text = 'def f(arr_tup, ind):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'get_nan_bits(arr_tup[{}], ind)'.format(i) for i in range(
        zqql__vwvy)]), ',' if zqql__vwvy == 1 else '')
    owq__tkzps = {}
    exec(func_text, {'get_nan_bits': get_nan_bits}, owq__tkzps)
    impl = owq__tkzps['f']
    return impl


def set_nan_bits(arr, ind, na_val):
    return 0


@overload(set_nan_bits, no_unliteral=True)
def overload_set_nan_bits(arr, ind, na_val):
    if arr == string_array_type:

        def impl_str(arr, ind, na_val):
            chxrb__jpj = get_null_bitmap_ptr(arr)
            set_bit_to(chxrb__jpj, ind, na_val)
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
    zqql__vwvy = arr_tup.count
    func_text = 'def f(arr_tup, ind, na_val):\n'
    for i in range(zqql__vwvy):
        func_text += '  set_nan_bits(arr_tup[{}], ind, na_val[{}])\n'.format(i,
            i)
    func_text += '  return\n'
    owq__tkzps = {}
    exec(func_text, {'set_nan_bits': set_nan_bits}, owq__tkzps)
    impl = owq__tkzps['f']
    return impl
