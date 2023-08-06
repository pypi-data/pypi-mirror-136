"""
Common IR extension functions for connectors such as CSV, Parquet and JSON readers.
"""
from collections import defaultdict
import numba
from numba.core import ir, types
from numba.core.ir_utils import replace_vars_inner, visit_vars_inner
from numba.extending import box, models, register_model
from bodo.hiframes.table import TableType
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.utils import debug_prints


def connector_array_analysis(node, equiv_set, typemap, array_analysis):
    pagsq__dhtr = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    hlroa__dwi = []
    for cnjud__wsxf in node.out_vars:
        typ = typemap[cnjud__wsxf.name]
        if typ == types.none:
            continue
        oewpz__hmb = array_analysis._gen_shape_call(equiv_set, cnjud__wsxf,
            typ.ndim, None, pagsq__dhtr)
        equiv_set.insert_equiv(cnjud__wsxf, oewpz__hmb)
        hlroa__dwi.append(oewpz__hmb[0])
        equiv_set.define(cnjud__wsxf, set())
    if len(hlroa__dwi) > 1:
        equiv_set.insert_equiv(*hlroa__dwi)
    return [], pagsq__dhtr


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and node.limit is not None:
        qkiu__lvr = Distribution.OneD_Var
    else:
        qkiu__lvr = Distribution.OneD
    for bbtz__gxf in node.out_vars:
        if bbtz__gxf.name in array_dists:
            qkiu__lvr = Distribution(min(qkiu__lvr.value, array_dists[
                bbtz__gxf.name].value))
    for bbtz__gxf in node.out_vars:
        array_dists[bbtz__gxf.name] = qkiu__lvr


def connector_typeinfer(node, typeinferer):
    if node.connector_typ == 'csv':
        if node.chunksize is not None:
            typeinferer.lock_type(node.out_vars[0].name, node.out_types[0],
                loc=node.loc)
        else:
            typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(
                node.out_types)), loc=node.loc)
            typeinferer.lock_type(node.out_vars[1].name, node.
                index_column_typ, loc=node.loc)
        return
    if node.connector_typ == 'parquet':
        typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(node.
            out_types)), loc=node.loc)
        typeinferer.lock_type(node.out_vars[1].name, node.index_column_type,
            loc=node.loc)
        return
    for cnjud__wsxf, typ in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(cnjud__wsxf.name, typ, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    vdim__hotsv = []
    for cnjud__wsxf in node.out_vars:
        hyrkn__mfp = visit_vars_inner(cnjud__wsxf, callback, cbdata)
        vdim__hotsv.append(hyrkn__mfp)
    node.out_vars = vdim__hotsv
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for dglcq__dlh in node.filters:
            for sju__ndp in range(len(dglcq__dlh)):
                val = dglcq__dlh[sju__ndp]
                dglcq__dlh[sju__ndp] = val[0], val[1], visit_vars_inner(val
                    [2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({bbtz__gxf.name for bbtz__gxf in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for fduqz__bqvlx in node.filters:
            for bbtz__gxf in fduqz__bqvlx:
                if isinstance(bbtz__gxf[2], ir.Var):
                    use_set.add(bbtz__gxf[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    rlzz__afef = set(bbtz__gxf.name for bbtz__gxf in node.out_vars)
    return set(), rlzz__afef


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    vdim__hotsv = []
    for cnjud__wsxf in node.out_vars:
        hyrkn__mfp = replace_vars_inner(cnjud__wsxf, var_dict)
        vdim__hotsv.append(hyrkn__mfp)
    node.out_vars = vdim__hotsv
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for dglcq__dlh in node.filters:
            for sju__ndp in range(len(dglcq__dlh)):
                val = dglcq__dlh[sju__ndp]
                dglcq__dlh[sju__ndp] = val[0], val[1], replace_vars_inner(val
                    [2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for cnjud__wsxf in node.out_vars:
        embz__fmpds = definitions[cnjud__wsxf.name]
        if node not in embz__fmpds:
            embz__fmpds.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        mps__obbi = []
        kczrl__iogts = [bbtz__gxf[2] for fduqz__bqvlx in filters for
            bbtz__gxf in fduqz__bqvlx]
        omd__tzs = set()
        for goy__yor in kczrl__iogts:
            if isinstance(goy__yor, ir.Var):
                if goy__yor.name not in omd__tzs:
                    mps__obbi.append(goy__yor)
                omd__tzs.add(goy__yor.name)
        return {bbtz__gxf.name: f'f{sju__ndp}' for sju__ndp, bbtz__gxf in
            enumerate(mps__obbi)}, mps__obbi
    else:
        return {}, []


class StreamReaderType(types.Opaque):

    def __init__(self):
        super(StreamReaderType, self).__init__(name='StreamReaderType')


stream_reader_type = StreamReaderType()
register_model(StreamReaderType)(models.OpaqueModel)


@box(StreamReaderType)
def box_stream_reader(typ, val, c):
    c.pyapi.incref(val)
    return val


def trim_extra_used_columns(used_columns, num_columns):
    jesx__jrw = len(used_columns)
    for sju__ndp in range(len(used_columns) - 1, -1, -1):
        if used_columns[sju__ndp] < num_columns:
            break
        jesx__jrw = sju__ndp
    return used_columns[:jesx__jrw]
