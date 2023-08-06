import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname


class JsonReader(ir.Stmt):

    def __init__(self, df_out, loc, out_vars, out_types, file_name,
        df_colnames, orient, convert_dates, precise_float, lines, compression):
        self.connector_typ = 'json'
        self.df_out = df_out
        self.loc = loc
        self.out_vars = out_vars
        self.out_types = out_types
        self.file_name = file_name
        self.df_colnames = df_colnames
        self.orient = orient
        self.convert_dates = convert_dates
        self.precise_float = precise_float
        self.lines = lines
        self.compression = compression

    def __repr__(self):
        return ('{} = ReadJson(file={}, col_names={}, types={}, vars={})'.
            format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars))


import llvmlite.binding as ll
from bodo.io import json_cpp
ll.add_symbol('json_file_chunk_reader', json_cpp.json_file_chunk_reader)
json_file_chunk_reader = types.ExternalFunction('json_file_chunk_reader',
    bodo.ir.connector.stream_reader_type(types.voidptr, types.bool_, types.
    bool_, types.int64, types.voidptr, types.voidptr))


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    yhukq__xtme = []
    jovvi__xmy = []
    sxcc__yjgy = []
    for uzcp__bowpw, tzc__mtq in enumerate(json_node.out_vars):
        if tzc__mtq.name in lives:
            yhukq__xtme.append(json_node.df_colnames[uzcp__bowpw])
            jovvi__xmy.append(json_node.out_vars[uzcp__bowpw])
            sxcc__yjgy.append(json_node.out_types[uzcp__bowpw])
    json_node.df_colnames = yhukq__xtme
    json_node.out_vars = jovvi__xmy
    json_node.out_types = sxcc__yjgy
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for nagc__tnaz in json_node.out_vars:
            if array_dists[nagc__tnaz.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                nagc__tnaz.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nkqph__biwm = len(json_node.out_vars)
    ngy__jru = ', '.join('arr' + str(uzcp__bowpw) for uzcp__bowpw in range(
        nkqph__biwm))
    uio__qbc = 'def json_impl(fname):\n'
    uio__qbc += '    ({},) = _json_reader_py(fname)\n'.format(ngy__jru)
    ohnfd__snxs = {}
    exec(uio__qbc, {}, ohnfd__snxs)
    dzt__mzaw = ohnfd__snxs['json_impl']
    ucr__varh = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression)
    ulup__vuo = compile_to_numba_ir(dzt__mzaw, {'_json_reader_py':
        ucr__varh}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(ulup__vuo, [json_node.file_name])
    mfed__wcnsz = ulup__vuo.body[:-3]
    for uzcp__bowpw in range(len(json_node.out_vars)):
        mfed__wcnsz[-len(json_node.out_vars) + uzcp__bowpw
            ].target = json_node.out_vars[uzcp__bowpw]
    return mfed__wcnsz


numba.parfors.array_analysis.array_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[JsonReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[JsonReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[JsonReader] = remove_dead_json
numba.core.analysis.ir_extension_usedefs[JsonReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[JsonReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[JsonReader] = json_distributed_run
compiled_funcs = []


def _gen_json_reader_py(col_names, col_typs, typingctx, targetctx, parallel,
    orient, convert_dates, precise_float, lines, compression):
    uau__tlvfr = [sanitize_varname(zyu__kpsh) for zyu__kpsh in col_names]
    hwviq__jjtl = ', '.join(str(uzcp__bowpw) for uzcp__bowpw, kcfs__rdsni in
        enumerate(col_typs) if kcfs__rdsni.dtype == types.NPDatetime('ns'))
    igtt__npw = ', '.join(["{}='{}'".format(ffazm__iuqcl, bodo.ir.csv_ext.
        _get_dtype_str(kcfs__rdsni)) for ffazm__iuqcl, kcfs__rdsni in zip(
        uau__tlvfr, col_typs)])
    brdfn__llbw = ', '.join(["'{}':{}".format(ufdo__hdqit, bodo.ir.csv_ext.
        _get_pd_dtype_str(kcfs__rdsni)) for ufdo__hdqit, kcfs__rdsni in zip
        (col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    uio__qbc = 'def json_reader_py(fname):\n'
    uio__qbc += '  check_java_installation(fname)\n'
    uio__qbc += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    uio__qbc += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    uio__qbc += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region) )
"""
        .format(lines, parallel, compression))
    uio__qbc += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    uio__qbc += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    uio__qbc += "      raise FileNotFoundError('File does not exist')\n"
    uio__qbc += '  with objmode({}):\n'.format(igtt__npw)
    uio__qbc += "    df = pd.read_json(f_reader, orient='{}',\n".format(orient)
    uio__qbc += '       convert_dates = {}, \n'.format(convert_dates)
    uio__qbc += '       precise_float={}, \n'.format(precise_float)
    uio__qbc += '       lines={}, \n'.format(lines)
    uio__qbc += '       dtype={{{}}},\n'.format(brdfn__llbw)
    uio__qbc += '       )\n'
    for ffazm__iuqcl, ufdo__hdqit in zip(uau__tlvfr, col_names):
        uio__qbc += '    if len(df) > 0:\n'
        uio__qbc += "        {} = df['{}'].values\n".format(ffazm__iuqcl,
            ufdo__hdqit)
        uio__qbc += '    else:\n'
        uio__qbc += '        {} = np.array([])\n'.format(ffazm__iuqcl)
    uio__qbc += '  return ({},)\n'.format(', '.join(tvan__ngbb for
        tvan__ngbb in uau__tlvfr))
    ertsc__nkdg = globals()
    ohnfd__snxs = {}
    exec(uio__qbc, ertsc__nkdg, ohnfd__snxs)
    ucr__varh = ohnfd__snxs['json_reader_py']
    kulkt__nwfsc = numba.njit(ucr__varh)
    compiled_funcs.append(kulkt__nwfsc)
    return kulkt__nwfsc
