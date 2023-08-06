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
    vwx__ska = []
    dyxv__ojb = []
    tcluz__fib = []
    for gdo__qvpb, jahgi__rmkq in enumerate(json_node.out_vars):
        if jahgi__rmkq.name in lives:
            vwx__ska.append(json_node.df_colnames[gdo__qvpb])
            dyxv__ojb.append(json_node.out_vars[gdo__qvpb])
            tcluz__fib.append(json_node.out_types[gdo__qvpb])
    json_node.df_colnames = vwx__ska
    json_node.out_vars = dyxv__ojb
    json_node.out_types = tcluz__fib
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for abey__lmzbh in json_node.out_vars:
            if array_dists[abey__lmzbh.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                abey__lmzbh.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    xrhq__eoq = len(json_node.out_vars)
    fuuk__xvbz = ', '.join('arr' + str(gdo__qvpb) for gdo__qvpb in range(
        xrhq__eoq))
    hrxw__qnhyo = 'def json_impl(fname):\n'
    hrxw__qnhyo += '    ({},) = _json_reader_py(fname)\n'.format(fuuk__xvbz)
    ffo__kmmy = {}
    exec(hrxw__qnhyo, {}, ffo__kmmy)
    nzera__zchcq = ffo__kmmy['json_impl']
    ldqoh__fgpt = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression)
    crssl__rvar = compile_to_numba_ir(nzera__zchcq, {'_json_reader_py':
        ldqoh__fgpt}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(crssl__rvar, [json_node.file_name])
    axsh__roui = crssl__rvar.body[:-3]
    for gdo__qvpb in range(len(json_node.out_vars)):
        axsh__roui[-len(json_node.out_vars) + gdo__qvpb
            ].target = json_node.out_vars[gdo__qvpb]
    return axsh__roui


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
    xhd__evsev = [sanitize_varname(zzz__wnwfl) for zzz__wnwfl in col_names]
    egd__qbvb = ', '.join(str(gdo__qvpb) for gdo__qvpb, vako__vlw in
        enumerate(col_typs) if vako__vlw.dtype == types.NPDatetime('ns'))
    qlzr__nhuwp = ', '.join(["{}='{}'".format(oyhb__vhke, bodo.ir.csv_ext.
        _get_dtype_str(vako__vlw)) for oyhb__vhke, vako__vlw in zip(
        xhd__evsev, col_typs)])
    vkko__gdjhb = ', '.join(["'{}':{}".format(pxtvl__tkl, bodo.ir.csv_ext.
        _get_pd_dtype_str(vako__vlw)) for pxtvl__tkl, vako__vlw in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    hrxw__qnhyo = 'def json_reader_py(fname):\n'
    hrxw__qnhyo += '  check_java_installation(fname)\n'
    hrxw__qnhyo += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    hrxw__qnhyo += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    hrxw__qnhyo += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region) )
"""
        .format(lines, parallel, compression))
    hrxw__qnhyo += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    hrxw__qnhyo += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    hrxw__qnhyo += "      raise FileNotFoundError('File does not exist')\n"
    hrxw__qnhyo += '  with objmode({}):\n'.format(qlzr__nhuwp)
    hrxw__qnhyo += "    df = pd.read_json(f_reader, orient='{}',\n".format(
        orient)
    hrxw__qnhyo += '       convert_dates = {}, \n'.format(convert_dates)
    hrxw__qnhyo += '       precise_float={}, \n'.format(precise_float)
    hrxw__qnhyo += '       lines={}, \n'.format(lines)
    hrxw__qnhyo += '       dtype={{{}}},\n'.format(vkko__gdjhb)
    hrxw__qnhyo += '       )\n'
    for oyhb__vhke, pxtvl__tkl in zip(xhd__evsev, col_names):
        hrxw__qnhyo += '    if len(df) > 0:\n'
        hrxw__qnhyo += "        {} = df['{}'].values\n".format(oyhb__vhke,
            pxtvl__tkl)
        hrxw__qnhyo += '    else:\n'
        hrxw__qnhyo += '        {} = np.array([])\n'.format(oyhb__vhke)
    hrxw__qnhyo += '  return ({},)\n'.format(', '.join(qnf__kpp for
        qnf__kpp in xhd__evsev))
    kvvsp__iwknr = globals()
    ffo__kmmy = {}
    exec(hrxw__qnhyo, kvvsp__iwknr, ffo__kmmy)
    ldqoh__fgpt = ffo__kmmy['json_reader_py']
    zxvy__xqa = numba.njit(ldqoh__fgpt)
    compiled_funcs.append(zxvy__xqa)
    return zxvy__xqa
