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
    xxuv__ksgp = []
    vzpv__uzugw = []
    kthfk__uvedz = []
    for dsia__jytxc, yej__pggg in enumerate(sql_node.out_vars):
        if yej__pggg.name in lives:
            xxuv__ksgp.append(sql_node.df_colnames[dsia__jytxc])
            vzpv__uzugw.append(sql_node.out_vars[dsia__jytxc])
            kthfk__uvedz.append(sql_node.out_types[dsia__jytxc])
    sql_node.df_colnames = xxuv__ksgp
    sql_node.out_vars = vzpv__uzugw
    sql_node.out_types = kthfk__uvedz
    if len(sql_node.out_vars) == 0:
        return None
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for nri__hzgk in sql_node.out_vars:
            if array_dists[nri__hzgk.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                nri__hzgk.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    jsv__jotpf = len(sql_node.out_vars)
    tgjyk__ezzc = ', '.join('arr' + str(dsia__jytxc) for dsia__jytxc in
        range(jsv__jotpf))
    jrlf__lepik, sbm__wtwj = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    opro__ueuw = ', '.join(jrlf__lepik.values())
    ouw__gjhqs = f'def sql_impl(sql_request, conn, {opro__ueuw}):\n'
    if sql_node.filters:
        yzfyf__kvfuh = []
        for bpwim__blo in sql_node.filters:
            nwq__nxuxf = [' '.join(['(', ronn__aghq[0], ronn__aghq[1], '{' +
                jrlf__lepik[ronn__aghq[2].name] + '}' if isinstance(
                ronn__aghq[2], ir.Var) else ronn__aghq[2], ')']) for
                ronn__aghq in bpwim__blo]
            yzfyf__kvfuh.append(' ( ' + ' AND '.join(nwq__nxuxf) + ' ) ')
        eacn__npidt = ' WHERE ' + ' OR '.join(yzfyf__kvfuh)
        for dsia__jytxc, unboz__fpst in enumerate(jrlf__lepik.values()):
            ouw__gjhqs += (
                f'    {unboz__fpst} = get_sql_literal({unboz__fpst})\n')
        ouw__gjhqs += f'    sql_request = f"{{sql_request}} {eacn__npidt}"\n'
    ouw__gjhqs += '    ({},) = _sql_reader_py(sql_request, conn)\n'.format(
        tgjyk__ezzc)
    erg__vlr = {}
    exec(ouw__gjhqs, {}, erg__vlr)
    jawkp__rmavj = erg__vlr['sql_impl']
    hii__ggc = _gen_sql_reader_py(sql_node.df_colnames, sql_node.out_types,
        typingctx, targetctx, sql_node.db_type, sql_node.limit, parallel)
    eltn__npty = compile_to_numba_ir(jawkp__rmavj, {'_sql_reader_py':
        hii__ggc, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type) + tuple(
        typemap[nri__hzgk.name] for nri__hzgk in sbm__wtwj), typemap=
        typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.db_type == 'snowflake':
        nzjxq__htide = [(uvyyg__busf.upper() if uvyyg__busf in sql_node.
            converted_colnames else uvyyg__busf) for uvyyg__busf in
            sql_node.df_colnames]
        pcu__kaofr = ', '.join([f'"{uvyyg__busf}"' for uvyyg__busf in
            nzjxq__htide])
    else:
        pcu__kaofr = ', '.join(sql_node.df_colnames)
    uvjpp__xdqy = ('SELECT ' + pcu__kaofr + ' FROM (' + sql_node.
        sql_request + ') as TEMP')
    replace_arg_nodes(eltn__npty, [ir.Const(uvjpp__xdqy, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc)] + sbm__wtwj)
    ydgqu__okize = eltn__npty.body[:-3]
    for dsia__jytxc in range(len(sql_node.out_vars)):
        ydgqu__okize[-len(sql_node.out_vars) + dsia__jytxc
            ].target = sql_node.out_vars[dsia__jytxc]
    return ydgqu__okize


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    tff__aaap = types.unliteral(filter_value)
    if tff__aaap == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(tff__aaap, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif tff__aaap == bodo.pd_timestamp_type:

        def impl(filter_value):
            tit__ihez = filter_value.nanosecond
            btxyg__xrrxy = ''
            if tit__ihez < 10:
                btxyg__xrrxy = '00'
            elif tit__ihez < 100:
                btxyg__xrrxy = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{btxyg__xrrxy}{tit__ihez}'"
                )
        return impl
    elif tff__aaap == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {tff__aaap} used in filter pushdown.'
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
    except ImportError as umu__wpssb:
        rsdnl__rrwd = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(rsdnl__rrwd)


def req_limit(sql_request):
    import re
    iyuol__twj = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    yba__pszys = iyuol__twj.search(sql_request)
    if yba__pszys:
        return int(yba__pszys.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names, col_typs, typingctx, targetctx, db_type,
    limit, parallel):
    vcv__gltl = [sanitize_varname(qpwon__kuzuh) for qpwon__kuzuh in col_names]
    awu__ggv = ["{}='{}'".format(yeu__flg, _get_dtype_str(ogkm__wvoge)) for
        yeu__flg, ogkm__wvoge in zip(vcv__gltl, col_typs)]
    if bodo.sql_access_method == 'multiple_access_by_block':
        ouw__gjhqs = 'def sql_reader_py(sql_request,conn):\n'
        ouw__gjhqs += '  sqlalchemy_check()\n'
        ouw__gjhqs += '  rank = bodo.libs.distributed_api.get_rank()\n'
        ouw__gjhqs += '  n_pes = bodo.libs.distributed_api.get_size()\n'
        ouw__gjhqs += '  with objmode({}):\n'.format(', '.join(awu__ggv))
        ouw__gjhqs += '    list_df_block = []\n'
        ouw__gjhqs += '    block_size = 50000\n'
        ouw__gjhqs += '    iter = 0\n'
        ouw__gjhqs += '    while(True):\n'
        ouw__gjhqs += '      offset = (iter * n_pes + rank) * block_size\n'
        ouw__gjhqs += """      sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(block_size) + ' OFFSET ' + str(offset)
"""
        ouw__gjhqs += '      df_block = pd.read_sql(sql_cons, conn)\n'
        ouw__gjhqs += '      if df_block.size == 0:\n'
        ouw__gjhqs += '        break\n'
        ouw__gjhqs += '      list_df_block.append(df_block)\n'
        ouw__gjhqs += '      iter += 1\n'
        ouw__gjhqs += '    df_ret = pd.concat(list_df_block)\n'
        for yeu__flg, gwz__hxt in zip(vcv__gltl, col_names):
            ouw__gjhqs += "    {} = df_ret['{}'].values\n".format(yeu__flg,
                gwz__hxt)
        ouw__gjhqs += '  return ({},)\n'.format(', '.join(nupcw__doym for
            nupcw__doym in vcv__gltl))
    if bodo.sql_access_method == 'multiple_access_nb_row_first':
        ouw__gjhqs = 'def sql_reader_py(sql_request, conn):\n'
        if db_type == 'snowflake':
            qpewi__rrkxf = {}
            for dsia__jytxc, ffhuq__jzz in enumerate(col_typs):
                qpewi__rrkxf[f'col_{dsia__jytxc}_type'] = ffhuq__jzz
            ouw__gjhqs += (
                f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n"
                )

            def is_nullable(typ):
                return bodo.utils.utils.is_array_typ(typ, False
                    ) and not isinstance(typ, types.Array)
            heu__noz = [int(is_nullable(ffhuq__jzz)) for ffhuq__jzz in col_typs
                ]
            ouw__gjhqs += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(col_names)}, np.array({heu__noz}, dtype=np.int32).ctypes)
"""
            ouw__gjhqs += '  check_and_propagate_cpp_exception()\n'
            for dsia__jytxc, jdbl__tgoeu in enumerate(vcv__gltl):
                ouw__gjhqs += f"""  {jdbl__tgoeu} = info_to_array(info_from_table(out_table, {dsia__jytxc}), col_{dsia__jytxc}_type)
"""
            ouw__gjhqs += '  delete_table(out_table)\n'
            ouw__gjhqs += f'  ev.finalize()\n'
        else:
            ouw__gjhqs += '  sqlalchemy_check()\n'
            if parallel:
                ouw__gjhqs += '  rank = bodo.libs.distributed_api.get_rank()\n'
                if limit is not None:
                    ouw__gjhqs += f'  nb_row = {limit}\n'
                else:
                    ouw__gjhqs += '  with objmode(nb_row="int64"):\n'
                    ouw__gjhqs += f'     if rank == {MPI_ROOT}:\n'
                    ouw__gjhqs += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                    ouw__gjhqs += (
                        '         frame = pd.read_sql(sql_cons, conn)\n')
                    ouw__gjhqs += '         nb_row = frame.iat[0,0]\n'
                    ouw__gjhqs += '     else:\n'
                    ouw__gjhqs += '         nb_row = 0\n'
                    ouw__gjhqs += '  nb_row = bcast_scalar(nb_row)\n'
                ouw__gjhqs += '  with objmode({}):\n'.format(', '.join(
                    awu__ggv))
                ouw__gjhqs += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
                ouw__gjhqs += f"""    sql_cons = 'select {', '.join(col_names)} from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
                ouw__gjhqs += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            else:
                ouw__gjhqs += '  with objmode({}):\n'.format(', '.join(
                    awu__ggv))
                ouw__gjhqs += '    df_ret = pd.read_sql(sql_request, conn)\n'
            for yeu__flg, gwz__hxt in zip(vcv__gltl, col_names):
                ouw__gjhqs += "    {} = df_ret['{}'].values\n".format(yeu__flg,
                    gwz__hxt)
        ouw__gjhqs += '  return ({},)\n'.format(', '.join(nupcw__doym for
            nupcw__doym in vcv__gltl))
    rcq__pizlt = {'bodo': bodo}
    if db_type == 'snowflake':
        rcq__pizlt.update(qpewi__rrkxf)
        rcq__pizlt.update({'np': np, 'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'snowflake_read':
            _snowflake_read, 'info_to_array': info_to_array,
            'info_from_table': info_from_table, 'delete_table': delete_table})
    else:
        rcq__pizlt.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar})
    erg__vlr = {}
    exec(ouw__gjhqs, rcq__pizlt, erg__vlr)
    hii__ggc = erg__vlr['sql_reader_py']
    uqrll__uacbp = numba.njit(hii__ggc)
    compiled_funcs.append(uqrll__uacbp)
    return uqrll__uacbp


_snowflake_read = types.ExternalFunction('snowflake_read', table_type(types
    .voidptr, types.voidptr, types.boolean, types.int64, types.voidptr))
import llvmlite.binding as ll
from bodo.io import arrow_cpp
ll.add_symbol('snowflake_read', arrow_cpp.snowflake_read)
