"""IR node for the data sorting"""
from collections import defaultdict
import numba
import numpy as np
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, mk_unique_var, replace_arg_nodes, replace_vars_inner, visit_vars_inner
import bodo
import bodo.libs.timsort
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, sort_values_table
from bodo.libs.str_arr_ext import cp_str_list_to_array, to_list_if_immutable_arr
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.utils import debug_prints, gen_getitem
MIN_SAMPLES = 1000000
samplePointsPerPartitionHint = 20
MPI_ROOT = 0


class Sort(ir.Stmt):

    def __init__(self, df_in, df_out, key_arrs, out_key_arrs, df_in_vars,
        df_out_vars, inplace, loc, ascending_list=True, na_position='last'):
        self.df_in = df_in
        self.df_out = df_out
        self.key_arrs = key_arrs
        self.out_key_arrs = out_key_arrs
        self.df_in_vars = df_in_vars
        self.df_out_vars = df_out_vars
        self.inplace = inplace
        if isinstance(na_position, str):
            if na_position == 'last':
                self.na_position_b = (True,) * len(key_arrs)
            else:
                self.na_position_b = (False,) * len(key_arrs)
        else:
            self.na_position_b = tuple([(True if btv__pfh == 'last' else 
                False) for btv__pfh in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_arrs)
        self.ascending_list = ascending_list
        self.loc = loc

    def __repr__(self):
        fsi__xmny = ''
        for owstp__vqd, vmbcx__akyut in self.df_in_vars.items():
            fsi__xmny += "'{}':{}, ".format(owstp__vqd, vmbcx__akyut.name)
        uqd__snxdn = '{}{{{}}}'.format(self.df_in, fsi__xmny)
        fwn__yzqz = ''
        for owstp__vqd, vmbcx__akyut in self.df_out_vars.items():
            fwn__yzqz += "'{}':{}, ".format(owstp__vqd, vmbcx__akyut.name)
        jtt__yzscd = '{}{{{}}}'.format(self.df_out, fwn__yzqz)
        return 'sort: [key: {}] {} [key: {}] {}'.format(', '.join(
            vmbcx__akyut.name for vmbcx__akyut in self.key_arrs),
            uqd__snxdn, ', '.join(vmbcx__akyut.name for vmbcx__akyut in
            self.out_key_arrs), jtt__yzscd)


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    cla__rwflg = []
    nhdd__fgad = sort_node.key_arrs + list(sort_node.df_in_vars.values())
    for lxtoo__hkl in nhdd__fgad:
        ksm__pkemi = equiv_set.get_shape(lxtoo__hkl)
        if ksm__pkemi is not None:
            cla__rwflg.append(ksm__pkemi[0])
    if len(cla__rwflg) > 1:
        equiv_set.insert_equiv(*cla__rwflg)
    pujel__nzzod = []
    cla__rwflg = []
    tzsmd__egsm = sort_node.out_key_arrs + list(sort_node.df_out_vars.values())
    for lxtoo__hkl in tzsmd__egsm:
        wtc__rlsr = typemap[lxtoo__hkl.name]
        quklc__gnlg = array_analysis._gen_shape_call(equiv_set, lxtoo__hkl,
            wtc__rlsr.ndim, None, pujel__nzzod)
        equiv_set.insert_equiv(lxtoo__hkl, quklc__gnlg)
        cla__rwflg.append(quklc__gnlg[0])
        equiv_set.define(lxtoo__hkl, set())
    if len(cla__rwflg) > 1:
        equiv_set.insert_equiv(*cla__rwflg)
    return [], pujel__nzzod


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    nhdd__fgad = sort_node.key_arrs + list(sort_node.df_in_vars.values())
    ifmb__vcv = sort_node.out_key_arrs + list(sort_node.df_out_vars.values())
    lzst__gpdl = Distribution.OneD
    for lxtoo__hkl in nhdd__fgad:
        lzst__gpdl = Distribution(min(lzst__gpdl.value, array_dists[
            lxtoo__hkl.name].value))
    vpygc__zgg = Distribution(min(lzst__gpdl.value, Distribution.OneD_Var.
        value))
    for lxtoo__hkl in ifmb__vcv:
        if lxtoo__hkl.name in array_dists:
            vpygc__zgg = Distribution(min(vpygc__zgg.value, array_dists[
                lxtoo__hkl.name].value))
    if vpygc__zgg != Distribution.OneD_Var:
        lzst__gpdl = vpygc__zgg
    for lxtoo__hkl in nhdd__fgad:
        array_dists[lxtoo__hkl.name] = lzst__gpdl
    for lxtoo__hkl in ifmb__vcv:
        array_dists[lxtoo__hkl.name] = vpygc__zgg
    return


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for lukx__yfkf, zdkyt__tmiky in zip(sort_node.key_arrs, sort_node.
        out_key_arrs):
        typeinferer.constraints.append(typeinfer.Propagate(dst=zdkyt__tmiky
            .name, src=lukx__yfkf.name, loc=sort_node.loc))
    for ymzp__jesn, lxtoo__hkl in sort_node.df_in_vars.items():
        sor__ccoib = sort_node.df_out_vars[ymzp__jesn]
        typeinferer.constraints.append(typeinfer.Propagate(dst=sor__ccoib.
            name, src=lxtoo__hkl.name, loc=sort_node.loc))
    return


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for lxtoo__hkl in (sort_node.out_key_arrs + list(sort_node.
            df_out_vars.values())):
            definitions[lxtoo__hkl.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    if debug_prints():
        print('visiting sort vars for:', sort_node)
        print('cbdata: ', sorted(cbdata.items()))
    for dwwm__yfk in range(len(sort_node.key_arrs)):
        sort_node.key_arrs[dwwm__yfk] = visit_vars_inner(sort_node.key_arrs
            [dwwm__yfk], callback, cbdata)
        sort_node.out_key_arrs[dwwm__yfk] = visit_vars_inner(sort_node.
            out_key_arrs[dwwm__yfk], callback, cbdata)
    for ymzp__jesn in list(sort_node.df_in_vars.keys()):
        sort_node.df_in_vars[ymzp__jesn] = visit_vars_inner(sort_node.
            df_in_vars[ymzp__jesn], callback, cbdata)
    for ymzp__jesn in list(sort_node.df_out_vars.keys()):
        sort_node.df_out_vars[ymzp__jesn] = visit_vars_inner(sort_node.
            df_out_vars[ymzp__jesn], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    kaj__exuu = []
    for ymzp__jesn, lxtoo__hkl in sort_node.df_out_vars.items():
        if lxtoo__hkl.name not in lives:
            kaj__exuu.append(ymzp__jesn)
    for btjji__vrj in kaj__exuu:
        sort_node.df_in_vars.pop(btjji__vrj)
        sort_node.df_out_vars.pop(btjji__vrj)
    if len(sort_node.df_out_vars) == 0 and all(vmbcx__akyut.name not in
        lives for vmbcx__akyut in sort_node.out_key_arrs):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({vmbcx__akyut.name for vmbcx__akyut in sort_node.key_arrs})
    use_set.update({vmbcx__akyut.name for vmbcx__akyut in sort_node.
        df_in_vars.values()})
    if not sort_node.inplace:
        def_set.update({vmbcx__akyut.name for vmbcx__akyut in sort_node.
            out_key_arrs})
        def_set.update({vmbcx__akyut.name for vmbcx__akyut in sort_node.
            df_out_vars.values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    zkw__lpsl = set()
    if not sort_node.inplace:
        zkw__lpsl = set(vmbcx__akyut.name for vmbcx__akyut in sort_node.
            df_out_vars.values())
        zkw__lpsl.update({vmbcx__akyut.name for vmbcx__akyut in sort_node.
            out_key_arrs})
    return set(), zkw__lpsl


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for dwwm__yfk in range(len(sort_node.key_arrs)):
        sort_node.key_arrs[dwwm__yfk] = replace_vars_inner(sort_node.
            key_arrs[dwwm__yfk], var_dict)
        sort_node.out_key_arrs[dwwm__yfk] = replace_vars_inner(sort_node.
            out_key_arrs[dwwm__yfk], var_dict)
    for ymzp__jesn in list(sort_node.df_in_vars.keys()):
        sort_node.df_in_vars[ymzp__jesn] = replace_vars_inner(sort_node.
            df_in_vars[ymzp__jesn], var_dict)
    for ymzp__jesn in list(sort_node.df_out_vars.keys()):
        sort_node.df_out_vars[ymzp__jesn] = replace_vars_inner(sort_node.
            df_out_vars[ymzp__jesn], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    krpx__yssj = False
    kreb__bleee = list(sort_node.df_in_vars.values())
    tzsmd__egsm = list(sort_node.df_out_vars.values())
    if array_dists is not None:
        krpx__yssj = True
        for vmbcx__akyut in (sort_node.key_arrs + sort_node.out_key_arrs +
            kreb__bleee + tzsmd__egsm):
            if array_dists[vmbcx__akyut.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                vmbcx__akyut.name] != distributed_pass.Distribution.OneD_Var:
                krpx__yssj = False
    loc = sort_node.loc
    zmsk__gziqp = sort_node.key_arrs[0].scope
    nodes = []
    key_arrs = sort_node.key_arrs
    if not sort_node.inplace:
        mmjnv__eye = []
        for vmbcx__akyut in key_arrs:
            nuix__psjxq = _copy_array_nodes(vmbcx__akyut, nodes, typingctx,
                targetctx, typemap, calltypes)
            mmjnv__eye.append(nuix__psjxq)
        key_arrs = mmjnv__eye
        wphm__oro = []
        for vmbcx__akyut in kreb__bleee:
            vwpd__zuzit = _copy_array_nodes(vmbcx__akyut, nodes, typingctx,
                targetctx, typemap, calltypes)
            wphm__oro.append(vwpd__zuzit)
        kreb__bleee = wphm__oro
    key_name_args = [('key' + str(dwwm__yfk)) for dwwm__yfk in range(len(
        key_arrs))]
    zfoq__for = ', '.join(key_name_args)
    col_name_args = [('c' + str(dwwm__yfk)) for dwwm__yfk in range(len(
        kreb__bleee))]
    avfnl__gubjv = ', '.join(col_name_args)
    ciyl__wnpz = 'def f({}, {}):\n'.format(zfoq__for, avfnl__gubjv)
    ciyl__wnpz += get_sort_cpp_section(key_name_args, col_name_args,
        sort_node.ascending_list, sort_node.na_position_b, krpx__yssj)
    ciyl__wnpz += '  return key_arrs, data\n'
    eovmz__dyf = {}
    exec(ciyl__wnpz, {}, eovmz__dyf)
    dfr__nqp = eovmz__dyf['f']
    xlsh__tptwf = types.Tuple([typemap[vmbcx__akyut.name] for vmbcx__akyut in
        key_arrs])
    qcnh__xiplw = types.Tuple([typemap[vmbcx__akyut.name] for vmbcx__akyut in
        kreb__bleee])
    rggl__kzj = compile_to_numba_ir(dfr__nqp, {'bodo': bodo, 'np': np,
        'to_list_if_immutable_arr': to_list_if_immutable_arr,
        'cp_str_list_to_array': cp_str_list_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'sort_values_table':
        sort_values_table, 'arr_info_list_to_table': arr_info_list_to_table,
        'array_to_info': array_to_info}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=tuple(list(xlsh__tptwf.types) + list(
        qcnh__xiplw.types)), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(rggl__kzj, key_arrs + kreb__bleee)
    nodes += rggl__kzj.body[:-2]
    lhsgb__berh = nodes[-1].target
    qgy__ywyfb = ir.Var(zmsk__gziqp, mk_unique_var('key_data'), loc)
    typemap[qgy__ywyfb.name] = xlsh__tptwf
    gen_getitem(qgy__ywyfb, lhsgb__berh, 0, calltypes, nodes)
    fqrf__hnobk = ir.Var(zmsk__gziqp, mk_unique_var('sort_data'), loc)
    typemap[fqrf__hnobk.name] = qcnh__xiplw
    gen_getitem(fqrf__hnobk, lhsgb__berh, 1, calltypes, nodes)
    for dwwm__yfk, var in enumerate(sort_node.out_key_arrs):
        gen_getitem(var, qgy__ywyfb, dwwm__yfk, calltypes, nodes)
    for dwwm__yfk, var in enumerate(tzsmd__egsm):
        gen_getitem(var, fqrf__hnobk, dwwm__yfk, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes):

    def _impl(arr):
        return arr.copy()
    rggl__kzj = compile_to_numba_ir(_impl, {}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(rggl__kzj, [var])
    nodes += rggl__kzj.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(key_name_args, col_name_args, ascending_list,
    na_position_b, parallel_b):
    xmqho__tqpby = len(key_name_args)
    sdzn__vjx = ['array_to_info({})'.format(ghmo__wkmz) for ghmo__wkmz in
        key_name_args] + ['array_to_info({})'.format(ghmo__wkmz) for
        ghmo__wkmz in col_name_args]
    ciyl__wnpz = '  info_list_total = [{}]\n'.format(','.join(sdzn__vjx))
    ciyl__wnpz += '  table_total = arr_info_list_to_table(info_list_total)\n'
    ciyl__wnpz += '  vect_ascending = np.array([{}])\n'.format(','.join('1' if
        ipq__vmx else '0' for ipq__vmx in ascending_list))
    ciyl__wnpz += '  na_position = np.array([{}])\n'.format(','.join('1' if
        ipq__vmx else '0' for ipq__vmx in na_position_b))
    ciyl__wnpz += (
        """  out_table = sort_values_table(table_total, {}, vect_ascending.ctypes, na_position.ctypes, {})
"""
        .format(xmqho__tqpby, parallel_b))
    bvat__byy = 0
    blsr__wmj = []
    for ghmo__wkmz in key_name_args:
        blsr__wmj.append('info_to_array(info_from_table(out_table, {}), {})'
            .format(bvat__byy, ghmo__wkmz))
        bvat__byy += 1
    ciyl__wnpz += '  key_arrs = ({},)\n'.format(','.join(blsr__wmj))
    gnoou__tnuq = []
    for ghmo__wkmz in col_name_args:
        gnoou__tnuq.append('info_to_array(info_from_table(out_table, {}), {})'
            .format(bvat__byy, ghmo__wkmz))
        bvat__byy += 1
    if len(gnoou__tnuq) > 0:
        ciyl__wnpz += '  data = ({},)\n'.format(','.join(gnoou__tnuq))
    else:
        ciyl__wnpz += '  data = ()\n'
    ciyl__wnpz += '  delete_table(out_table)\n'
    ciyl__wnpz += '  delete_table(table_total)\n'
    return ciyl__wnpz
