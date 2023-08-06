"""
Implementation of pd.read_sql in BODO.
We piggyback on the pandas implementation. Future plan is to have a faster
version for this task.
"""
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.ir.csv_ext import _get_dtype_str
from bodo.libs.array import delete_table, info_from_table, info_to_array, table_type
from bodo.libs.distributed_api import bcast, bcast_scalar
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_and_propagate_cpp_exception, sanitize_varname
MPI_ROOT = 0


class SqlReader(ir.Stmt):

    def __init__(self, sql_request, connection, df_out, df_colnames,
        out_vars, out_types, converted_colnames, db_type, loc):
        self.connector_typ = 'sql'
        self.sql_request = sql_request
        self.connection = connection
        self.df_out = df_out
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.converted_colnames = converted_colnames
        self.loc = loc
        self.limit = req_limit(sql_request)
        self.db_type = db_type
        self.filters = None

    def __repr__(self):
        return (
            '{} = ReadSql(sql_request={}, connection={}, col_names={}, types={}, vars={}, limit={})'
            .format(self.df_out, self.sql_request, self.connection, self.
            df_colnames, self.out_types, self.out_vars, self.limit))


def remove_dead_sql(sql_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    erh__jxsze = []
    mybzl__ksjxm = []
    sgl__vgft = []
    for ovx__bfvy, hsmnr__koy in enumerate(sql_node.out_vars):
        if hsmnr__koy.name in lives:
            erh__jxsze.append(sql_node.df_colnames[ovx__bfvy])
            mybzl__ksjxm.append(sql_node.out_vars[ovx__bfvy])
            sgl__vgft.append(sql_node.out_types[ovx__bfvy])
    sql_node.df_colnames = erh__jxsze
    sql_node.out_vars = mybzl__ksjxm
    sql_node.out_types = sgl__vgft
    if len(sql_node.out_vars) == 0:
        return None
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for ypagk__wifa in sql_node.out_vars:
            if array_dists[ypagk__wifa.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                ypagk__wifa.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    brbx__yxasy = len(sql_node.out_vars)
    nqjdc__rerzf = ', '.join('arr' + str(ovx__bfvy) for ovx__bfvy in range(
        brbx__yxasy))
    bfeo__ebla, vneo__znju = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    cpqci__jalon = ', '.join(bfeo__ebla.values())
    euvz__ywfr = f'def sql_impl(sql_request, conn, {cpqci__jalon}):\n'
    if sql_node.filters:
        vpwea__oyep = []
        for sypvz__eer in sql_node.filters:
            erf__uoly = [' '.join(['(', ifo__enyzd[0], ifo__enyzd[1], '{' +
                bfeo__ebla[ifo__enyzd[2].name] + '}' if isinstance(
                ifo__enyzd[2], ir.Var) else ifo__enyzd[2], ')']) for
                ifo__enyzd in sypvz__eer]
            vpwea__oyep.append(' ( ' + ' AND '.join(erf__uoly) + ' ) ')
        wetak__mgu = ' WHERE ' + ' OR '.join(vpwea__oyep)
        for ovx__bfvy, vwoqh__yaufs in enumerate(bfeo__ebla.values()):
            euvz__ywfr += (
                f'    {vwoqh__yaufs} = get_sql_literal({vwoqh__yaufs})\n')
        euvz__ywfr += f'    sql_request = f"{{sql_request}} {wetak__mgu}"\n'
    euvz__ywfr += '    ({},) = _sql_reader_py(sql_request, conn)\n'.format(
        nqjdc__rerzf)
    kror__nmgrj = {}
    exec(euvz__ywfr, {}, kror__nmgrj)
    rqa__jxm = kror__nmgrj['sql_impl']
    wlqz__oklw = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, typingctx, targetctx, sql_node.db_type, sql_node.limit,
        parallel)
    eehuq__flaa = compile_to_numba_ir(rqa__jxm, {'_sql_reader_py':
        wlqz__oklw, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type) + tuple(
        typemap[ypagk__wifa.name] for ypagk__wifa in vneo__znju), typemap=
        typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.db_type == 'snowflake':
        xshz__vkp = [(azey__tpsix.upper() if azey__tpsix in sql_node.
            converted_colnames else azey__tpsix) for azey__tpsix in
            sql_node.df_colnames]
        pyckl__ipb = ', '.join([f'"{azey__tpsix}"' for azey__tpsix in
            xshz__vkp])
    else:
        pyckl__ipb = ', '.join(sql_node.df_colnames)
    bydyx__cizal = ('SELECT ' + pyckl__ipb + ' FROM (' + sql_node.
        sql_request + ') as TEMP')
    replace_arg_nodes(eehuq__flaa, [ir.Const(bydyx__cizal, sql_node.loc),
        ir.Const(sql_node.connection, sql_node.loc)] + vneo__znju)
    llzlp__lmf = eehuq__flaa.body[:-3]
    for ovx__bfvy in range(len(sql_node.out_vars)):
        llzlp__lmf[-len(sql_node.out_vars) + ovx__bfvy
            ].target = sql_node.out_vars[ovx__bfvy]
    return llzlp__lmf


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    nzhe__ksqun = types.unliteral(filter_value)
    if nzhe__ksqun == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(nzhe__ksqun, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif nzhe__ksqun == bodo.pd_timestamp_type:

        def impl(filter_value):
            aifg__rjjsq = filter_value.nanosecond
            cfufa__bsbu = ''
            if aifg__rjjsq < 10:
                cfufa__bsbu = '00'
            elif aifg__rjjsq < 100:
                cfufa__bsbu = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{cfufa__bsbu}{aifg__rjjsq}'"
                )
        return impl
    elif nzhe__ksqun == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {nzhe__ksqun} used in filter pushdown.'
            )


numba.parfors.array_analysis.array_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[SqlReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[SqlReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[SqlReader] = remove_dead_sql
numba.core.analysis.ir_extension_usedefs[SqlReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[SqlReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[SqlReader] = sql_distributed_run
compiled_funcs = []


@numba.njit
def sqlalchemy_check():
    with numba.objmode():
        sqlalchemy_check_()


def sqlalchemy_check_():
    try:
        import sqlalchemy
    except ImportError as pck__sjys:
        epdad__perd = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(epdad__perd)


def req_limit(sql_request):
    import re
    engi__hgr = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    yeses__rug = engi__hgr.search(sql_request)
    if yeses__rug:
        return int(yeses__rug.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names, col_typs, typingctx, targetctx, db_type,
    limit, parallel):
    knug__njtdo = [sanitize_varname(bxma__ojtwl) for bxma__ojtwl in col_names]
    sla__ecp = ["{}='{}'".format(impho__dtkhj, _get_dtype_str(nxuyf__klkx)) for
        impho__dtkhj, nxuyf__klkx in zip(knug__njtdo, col_typs)]
    if bodo.sql_access_method == 'multiple_access_by_block':
        euvz__ywfr = 'def sql_reader_py(sql_request,conn):\n'
        euvz__ywfr += '  sqlalchemy_check()\n'
        euvz__ywfr += '  rank = bodo.libs.distributed_api.get_rank()\n'
        euvz__ywfr += '  n_pes = bodo.libs.distributed_api.get_size()\n'
        euvz__ywfr += '  with objmode({}):\n'.format(', '.join(sla__ecp))
        euvz__ywfr += '    list_df_block = []\n'
        euvz__ywfr += '    block_size = 50000\n'
        euvz__ywfr += '    iter = 0\n'
        euvz__ywfr += '    while(True):\n'
        euvz__ywfr += '      offset = (iter * n_pes + rank) * block_size\n'
        euvz__ywfr += """      sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(block_size) + ' OFFSET ' + str(offset)
"""
        euvz__ywfr += '      df_block = pd.read_sql(sql_cons, conn)\n'
        euvz__ywfr += '      if df_block.size == 0:\n'
        euvz__ywfr += '        break\n'
        euvz__ywfr += '      list_df_block.append(df_block)\n'
        euvz__ywfr += '      iter += 1\n'
        euvz__ywfr += '    df_ret = pd.concat(list_df_block)\n'
        for impho__dtkhj, mhqb__fvuyy in zip(knug__njtdo, col_names):
            euvz__ywfr += "    {} = df_ret['{}'].values\n".format(impho__dtkhj,
                mhqb__fvuyy)
        euvz__ywfr += '  return ({},)\n'.format(', '.join(taac__xbkdn for
            taac__xbkdn in knug__njtdo))
    if bodo.sql_access_method == 'multiple_access_nb_row_first':
        euvz__ywfr = 'def sql_reader_py(sql_request, conn):\n'
        if db_type == 'snowflake':
            zisuz__sfb = {}
            for ovx__bfvy, uqusi__urjb in enumerate(col_typs):
                zisuz__sfb[f'col_{ovx__bfvy}_type'] = uqusi__urjb
            euvz__ywfr += (
                f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n"
                )

            def is_nullable(typ):
                return bodo.utils.utils.is_array_typ(typ, False
                    ) and not isinstance(typ, types.Array)
            zzmiy__motv = [int(is_nullable(uqusi__urjb)) for uqusi__urjb in
                col_typs]
            euvz__ywfr += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(col_names)}, np.array({zzmiy__motv}, dtype=np.int32).ctypes)
"""
            euvz__ywfr += '  check_and_propagate_cpp_exception()\n'
            for ovx__bfvy, dlueh__zajr in enumerate(knug__njtdo):
                euvz__ywfr += f"""  {dlueh__zajr} = info_to_array(info_from_table(out_table, {ovx__bfvy}), col_{ovx__bfvy}_type)
"""
            euvz__ywfr += '  delete_table(out_table)\n'
            euvz__ywfr += f'  ev.finalize()\n'
        else:
            euvz__ywfr += '  sqlalchemy_check()\n'
            if parallel:
                euvz__ywfr += '  rank = bodo.libs.distributed_api.get_rank()\n'
                if limit is not None:
                    euvz__ywfr += f'  nb_row = {limit}\n'
                else:
                    euvz__ywfr += '  with objmode(nb_row="int64"):\n'
                    euvz__ywfr += f'     if rank == {MPI_ROOT}:\n'
                    euvz__ywfr += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                    euvz__ywfr += (
                        '         frame = pd.read_sql(sql_cons, conn)\n')
                    euvz__ywfr += '         nb_row = frame.iat[0,0]\n'
                    euvz__ywfr += '     else:\n'
                    euvz__ywfr += '         nb_row = 0\n'
                    euvz__ywfr += '  nb_row = bcast_scalar(nb_row)\n'
                euvz__ywfr += '  with objmode({}):\n'.format(', '.join(
                    sla__ecp))
                euvz__ywfr += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
                euvz__ywfr += f"""    sql_cons = 'select {', '.join(col_names)} from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
                euvz__ywfr += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            else:
                euvz__ywfr += '  with objmode({}):\n'.format(', '.join(
                    sla__ecp))
                euvz__ywfr += '    df_ret = pd.read_sql(sql_request, conn)\n'
            for impho__dtkhj, mhqb__fvuyy in zip(knug__njtdo, col_names):
                euvz__ywfr += "    {} = df_ret['{}'].values\n".format(
                    impho__dtkhj, mhqb__fvuyy)
        euvz__ywfr += '  return ({},)\n'.format(', '.join(taac__xbkdn for
            taac__xbkdn in knug__njtdo))
    gewvy__lrk = {'bodo': bodo}
    if db_type == 'snowflake':
        gewvy__lrk.update(zisuz__sfb)
        gewvy__lrk.update({'np': np, 'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'snowflake_read':
            _snowflake_read, 'info_to_array': info_to_array,
            'info_from_table': info_from_table, 'delete_table': delete_table})
    else:
        gewvy__lrk.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar})
    kror__nmgrj = {}
    exec(euvz__ywfr, gewvy__lrk, kror__nmgrj)
    wlqz__oklw = kror__nmgrj['sql_reader_py']
    jub__ieis = numba.njit(wlqz__oklw)
    compiled_funcs.append(jub__ieis)
    return jub__ieis


_snowflake_read = types.ExternalFunction('snowflake_read', table_type(types
    .voidptr, types.voidptr, types.boolean, types.int64, types.voidptr))
import llvmlite.binding as ll
from bodo.io import arrow_cpp
ll.add_symbol('snowflake_read', arrow_cpp.snowflake_read)
