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
    kvnci__fsuin = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    ujssy__rtqn = []
    for zdqt__rvx in node.out_vars:
        typ = typemap[zdqt__rvx.name]
        if typ == types.none:
            continue
        lvo__poe = array_analysis._gen_shape_call(equiv_set, zdqt__rvx, typ
            .ndim, None, kvnci__fsuin)
        equiv_set.insert_equiv(zdqt__rvx, lvo__poe)
        ujssy__rtqn.append(lvo__poe[0])
        equiv_set.define(zdqt__rvx, set())
    if len(ujssy__rtqn) > 1:
        equiv_set.insert_equiv(*ujssy__rtqn)
    return [], kvnci__fsuin


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and node.limit is not None:
        poki__fgjiu = Distribution.OneD_Var
    else:
        poki__fgjiu = Distribution.OneD
    for kabsz__plcss in node.out_vars:
        if kabsz__plcss.name in array_dists:
            poki__fgjiu = Distribution(min(poki__fgjiu.value, array_dists[
                kabsz__plcss.name].value))
    for kabsz__plcss in node.out_vars:
        array_dists[kabsz__plcss.name] = poki__fgjiu


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
    for zdqt__rvx, typ in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(zdqt__rvx.name, typ, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    tmmn__ocs = []
    for zdqt__rvx in node.out_vars:
        fle__jfml = visit_vars_inner(zdqt__rvx, callback, cbdata)
        tmmn__ocs.append(fle__jfml)
    node.out_vars = tmmn__ocs
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for jta__wnlz in node.filters:
            for szzu__tzwzu in range(len(jta__wnlz)):
                val = jta__wnlz[szzu__tzwzu]
                jta__wnlz[szzu__tzwzu] = val[0], val[1], visit_vars_inner(val
                    [2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({kabsz__plcss.name for kabsz__plcss in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for wre__iyba in node.filters:
            for kabsz__plcss in wre__iyba:
                if isinstance(kabsz__plcss[2], ir.Var):
                    use_set.add(kabsz__plcss[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    unzc__ttg = set(kabsz__plcss.name for kabsz__plcss in node.out_vars)
    return set(), unzc__ttg


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    tmmn__ocs = []
    for zdqt__rvx in node.out_vars:
        fle__jfml = replace_vars_inner(zdqt__rvx, var_dict)
        tmmn__ocs.append(fle__jfml)
    node.out_vars = tmmn__ocs
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for jta__wnlz in node.filters:
            for szzu__tzwzu in range(len(jta__wnlz)):
                val = jta__wnlz[szzu__tzwzu]
                jta__wnlz[szzu__tzwzu] = val[0], val[1], replace_vars_inner(val
                    [2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for zdqt__rvx in node.out_vars:
        bbsp__uotxk = definitions[zdqt__rvx.name]
        if node not in bbsp__uotxk:
            bbsp__uotxk.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        ham__jmmu = []
        fzvq__jcd = [kabsz__plcss[2] for wre__iyba in filters for
            kabsz__plcss in wre__iyba]
        baob__hogz = set()
        for wtvix__cwme in fzvq__jcd:
            if isinstance(wtvix__cwme, ir.Var):
                if wtvix__cwme.name not in baob__hogz:
                    ham__jmmu.append(wtvix__cwme)
                baob__hogz.add(wtvix__cwme.name)
        return {kabsz__plcss.name: f'f{szzu__tzwzu}' for szzu__tzwzu,
            kabsz__plcss in enumerate(ham__jmmu)}, ham__jmmu
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
    lvn__ttbs = len(used_columns)
    for szzu__tzwzu in range(len(used_columns) - 1, -1, -1):
        if used_columns[szzu__tzwzu] < num_columns:
            break
        lvn__ttbs = szzu__tzwzu
    return used_columns[:lvn__ttbs]
