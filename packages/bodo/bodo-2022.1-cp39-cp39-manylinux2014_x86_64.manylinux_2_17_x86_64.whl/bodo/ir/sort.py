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
            self.na_position_b = tuple([(True if cqx__akxi == 'last' else 
                False) for cqx__akxi in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_arrs)
        self.ascending_list = ascending_list
        self.loc = loc

    def __repr__(self):
        drdg__fvdta = ''
        for nfxza__jxp, qsgyc__sae in self.df_in_vars.items():
            drdg__fvdta += "'{}':{}, ".format(nfxza__jxp, qsgyc__sae.name)
        vch__hhgml = '{}{{{}}}'.format(self.df_in, drdg__fvdta)
        mvz__bsu = ''
        for nfxza__jxp, qsgyc__sae in self.df_out_vars.items():
            mvz__bsu += "'{}':{}, ".format(nfxza__jxp, qsgyc__sae.name)
        vvx__wgns = '{}{{{}}}'.format(self.df_out, mvz__bsu)
        return 'sort: [key: {}] {} [key: {}] {}'.format(', '.join(
            qsgyc__sae.name for qsgyc__sae in self.key_arrs), vch__hhgml,
            ', '.join(qsgyc__sae.name for qsgyc__sae in self.out_key_arrs),
            vvx__wgns)


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    voeoh__oqifh = []
    atcej__nwau = sort_node.key_arrs + list(sort_node.df_in_vars.values())
    for gmpn__uofro in atcej__nwau:
        kfv__elvy = equiv_set.get_shape(gmpn__uofro)
        if kfv__elvy is not None:
            voeoh__oqifh.append(kfv__elvy[0])
    if len(voeoh__oqifh) > 1:
        equiv_set.insert_equiv(*voeoh__oqifh)
    zadek__mbu = []
    voeoh__oqifh = []
    pej__kexh = sort_node.out_key_arrs + list(sort_node.df_out_vars.values())
    for gmpn__uofro in pej__kexh:
        ftn__zkz = typemap[gmpn__uofro.name]
        ejgl__igosi = array_analysis._gen_shape_call(equiv_set, gmpn__uofro,
            ftn__zkz.ndim, None, zadek__mbu)
        equiv_set.insert_equiv(gmpn__uofro, ejgl__igosi)
        voeoh__oqifh.append(ejgl__igosi[0])
        equiv_set.define(gmpn__uofro, set())
    if len(voeoh__oqifh) > 1:
        equiv_set.insert_equiv(*voeoh__oqifh)
    return [], zadek__mbu


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    atcej__nwau = sort_node.key_arrs + list(sort_node.df_in_vars.values())
    act__ugw = sort_node.out_key_arrs + list(sort_node.df_out_vars.values())
    upsmo__tkky = Distribution.OneD
    for gmpn__uofro in atcej__nwau:
        upsmo__tkky = Distribution(min(upsmo__tkky.value, array_dists[
            gmpn__uofro.name].value))
    pewue__aoh = Distribution(min(upsmo__tkky.value, Distribution.OneD_Var.
        value))
    for gmpn__uofro in act__ugw:
        if gmpn__uofro.name in array_dists:
            pewue__aoh = Distribution(min(pewue__aoh.value, array_dists[
                gmpn__uofro.name].value))
    if pewue__aoh != Distribution.OneD_Var:
        upsmo__tkky = pewue__aoh
    for gmpn__uofro in atcej__nwau:
        array_dists[gmpn__uofro.name] = upsmo__tkky
    for gmpn__uofro in act__ugw:
        array_dists[gmpn__uofro.name] = pewue__aoh
    return


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for koei__ine, zim__rsehj in zip(sort_node.key_arrs, sort_node.out_key_arrs
        ):
        typeinferer.constraints.append(typeinfer.Propagate(dst=zim__rsehj.
            name, src=koei__ine.name, loc=sort_node.loc))
    for cmm__dqbv, gmpn__uofro in sort_node.df_in_vars.items():
        kxxd__rraqr = sort_node.df_out_vars[cmm__dqbv]
        typeinferer.constraints.append(typeinfer.Propagate(dst=kxxd__rraqr.
            name, src=gmpn__uofro.name, loc=sort_node.loc))
    return


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for gmpn__uofro in (sort_node.out_key_arrs + list(sort_node.
            df_out_vars.values())):
            definitions[gmpn__uofro.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    if debug_prints():
        print('visiting sort vars for:', sort_node)
        print('cbdata: ', sorted(cbdata.items()))
    for qkppx__nktxj in range(len(sort_node.key_arrs)):
        sort_node.key_arrs[qkppx__nktxj] = visit_vars_inner(sort_node.
            key_arrs[qkppx__nktxj], callback, cbdata)
        sort_node.out_key_arrs[qkppx__nktxj] = visit_vars_inner(sort_node.
            out_key_arrs[qkppx__nktxj], callback, cbdata)
    for cmm__dqbv in list(sort_node.df_in_vars.keys()):
        sort_node.df_in_vars[cmm__dqbv] = visit_vars_inner(sort_node.
            df_in_vars[cmm__dqbv], callback, cbdata)
    for cmm__dqbv in list(sort_node.df_out_vars.keys()):
        sort_node.df_out_vars[cmm__dqbv] = visit_vars_inner(sort_node.
            df_out_vars[cmm__dqbv], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    srk__zzed = []
    for cmm__dqbv, gmpn__uofro in sort_node.df_out_vars.items():
        if gmpn__uofro.name not in lives:
            srk__zzed.append(cmm__dqbv)
    for ohx__thc in srk__zzed:
        sort_node.df_in_vars.pop(ohx__thc)
        sort_node.df_out_vars.pop(ohx__thc)
    if len(sort_node.df_out_vars) == 0 and all(qsgyc__sae.name not in lives for
        qsgyc__sae in sort_node.out_key_arrs):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({qsgyc__sae.name for qsgyc__sae in sort_node.key_arrs})
    use_set.update({qsgyc__sae.name for qsgyc__sae in sort_node.df_in_vars.
        values()})
    if not sort_node.inplace:
        def_set.update({qsgyc__sae.name for qsgyc__sae in sort_node.
            out_key_arrs})
        def_set.update({qsgyc__sae.name for qsgyc__sae in sort_node.
            df_out_vars.values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    wzg__vakl = set()
    if not sort_node.inplace:
        wzg__vakl = set(qsgyc__sae.name for qsgyc__sae in sort_node.
            df_out_vars.values())
        wzg__vakl.update({qsgyc__sae.name for qsgyc__sae in sort_node.
            out_key_arrs})
    return set(), wzg__vakl


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for qkppx__nktxj in range(len(sort_node.key_arrs)):
        sort_node.key_arrs[qkppx__nktxj] = replace_vars_inner(sort_node.
            key_arrs[qkppx__nktxj], var_dict)
        sort_node.out_key_arrs[qkppx__nktxj] = replace_vars_inner(sort_node
            .out_key_arrs[qkppx__nktxj], var_dict)
    for cmm__dqbv in list(sort_node.df_in_vars.keys()):
        sort_node.df_in_vars[cmm__dqbv] = replace_vars_inner(sort_node.
            df_in_vars[cmm__dqbv], var_dict)
    for cmm__dqbv in list(sort_node.df_out_vars.keys()):
        sort_node.df_out_vars[cmm__dqbv] = replace_vars_inner(sort_node.
            df_out_vars[cmm__dqbv], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    jqqf__fnyta = False
    lqa__dnz = list(sort_node.df_in_vars.values())
    pej__kexh = list(sort_node.df_out_vars.values())
    if array_dists is not None:
        jqqf__fnyta = True
        for qsgyc__sae in (sort_node.key_arrs + sort_node.out_key_arrs +
            lqa__dnz + pej__kexh):
            if array_dists[qsgyc__sae.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                qsgyc__sae.name] != distributed_pass.Distribution.OneD_Var:
                jqqf__fnyta = False
    loc = sort_node.loc
    now__jvg = sort_node.key_arrs[0].scope
    nodes = []
    key_arrs = sort_node.key_arrs
    if not sort_node.inplace:
        szmar__nnlb = []
        for qsgyc__sae in key_arrs:
            wdlx__ucwa = _copy_array_nodes(qsgyc__sae, nodes, typingctx,
                targetctx, typemap, calltypes)
            szmar__nnlb.append(wdlx__ucwa)
        key_arrs = szmar__nnlb
        slthm__lmu = []
        for qsgyc__sae in lqa__dnz:
            muzof__rjwu = _copy_array_nodes(qsgyc__sae, nodes, typingctx,
                targetctx, typemap, calltypes)
            slthm__lmu.append(muzof__rjwu)
        lqa__dnz = slthm__lmu
    key_name_args = [('key' + str(qkppx__nktxj)) for qkppx__nktxj in range(
        len(key_arrs))]
    bki__ons = ', '.join(key_name_args)
    col_name_args = [('c' + str(qkppx__nktxj)) for qkppx__nktxj in range(
        len(lqa__dnz))]
    xbvp__omvrb = ', '.join(col_name_args)
    dnjgw__iuc = 'def f({}, {}):\n'.format(bki__ons, xbvp__omvrb)
    dnjgw__iuc += get_sort_cpp_section(key_name_args, col_name_args,
        sort_node.ascending_list, sort_node.na_position_b, jqqf__fnyta)
    dnjgw__iuc += '  return key_arrs, data\n'
    pctrd__hlmxl = {}
    exec(dnjgw__iuc, {}, pctrd__hlmxl)
    pfuy__rutyd = pctrd__hlmxl['f']
    dyxot__wyy = types.Tuple([typemap[qsgyc__sae.name] for qsgyc__sae in
        key_arrs])
    evj__tfbk = types.Tuple([typemap[qsgyc__sae.name] for qsgyc__sae in
        lqa__dnz])
    lncrk__sqczd = compile_to_numba_ir(pfuy__rutyd, {'bodo': bodo, 'np': np,
        'to_list_if_immutable_arr': to_list_if_immutable_arr,
        'cp_str_list_to_array': cp_str_list_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'sort_values_table':
        sort_values_table, 'arr_info_list_to_table': arr_info_list_to_table,
        'array_to_info': array_to_info}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=tuple(list(dyxot__wyy.types) + list(evj__tfbk.
        types)), typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(lncrk__sqczd, key_arrs + lqa__dnz)
    nodes += lncrk__sqczd.body[:-2]
    wqe__bczea = nodes[-1].target
    igynj__xfjvv = ir.Var(now__jvg, mk_unique_var('key_data'), loc)
    typemap[igynj__xfjvv.name] = dyxot__wyy
    gen_getitem(igynj__xfjvv, wqe__bczea, 0, calltypes, nodes)
    cela__jdh = ir.Var(now__jvg, mk_unique_var('sort_data'), loc)
    typemap[cela__jdh.name] = evj__tfbk
    gen_getitem(cela__jdh, wqe__bczea, 1, calltypes, nodes)
    for qkppx__nktxj, var in enumerate(sort_node.out_key_arrs):
        gen_getitem(var, igynj__xfjvv, qkppx__nktxj, calltypes, nodes)
    for qkppx__nktxj, var in enumerate(pej__kexh):
        gen_getitem(var, cela__jdh, qkppx__nktxj, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes):

    def _impl(arr):
        return arr.copy()
    lncrk__sqczd = compile_to_numba_ir(_impl, {}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(lncrk__sqczd, [var])
    nodes += lncrk__sqczd.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(key_name_args, col_name_args, ascending_list,
    na_position_b, parallel_b):
    ixbuh__ydxfa = len(key_name_args)
    nny__kvo = ['array_to_info({})'.format(btqm__tozod) for btqm__tozod in
        key_name_args] + ['array_to_info({})'.format(btqm__tozod) for
        btqm__tozod in col_name_args]
    dnjgw__iuc = '  info_list_total = [{}]\n'.format(','.join(nny__kvo))
    dnjgw__iuc += '  table_total = arr_info_list_to_table(info_list_total)\n'
    dnjgw__iuc += '  vect_ascending = np.array([{}])\n'.format(','.join('1' if
        hsdod__dir else '0' for hsdod__dir in ascending_list))
    dnjgw__iuc += '  na_position = np.array([{}])\n'.format(','.join('1' if
        hsdod__dir else '0' for hsdod__dir in na_position_b))
    dnjgw__iuc += (
        """  out_table = sort_values_table(table_total, {}, vect_ascending.ctypes, na_position.ctypes, {})
"""
        .format(ixbuh__ydxfa, parallel_b))
    oid__kuc = 0
    dsis__jzke = []
    for btqm__tozod in key_name_args:
        dsis__jzke.append('info_to_array(info_from_table(out_table, {}), {})'
            .format(oid__kuc, btqm__tozod))
        oid__kuc += 1
    dnjgw__iuc += '  key_arrs = ({},)\n'.format(','.join(dsis__jzke))
    omnbk__pko = []
    for btqm__tozod in col_name_args:
        omnbk__pko.append('info_to_array(info_from_table(out_table, {}), {})'
            .format(oid__kuc, btqm__tozod))
        oid__kuc += 1
    if len(omnbk__pko) > 0:
        dnjgw__iuc += '  data = ({},)\n'.format(','.join(omnbk__pko))
    else:
        dnjgw__iuc += '  data = ()\n'
    dnjgw__iuc += '  delete_table(out_table)\n'
    dnjgw__iuc += '  delete_table(table_total)\n'
    return dnjgw__iuc
