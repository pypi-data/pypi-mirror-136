from urllib.parse import parse_qsl, urlparse
import snowflake.connector
import bodo
from bodo.utils import tracing


def get_connection_params(conn_str):
    import json
    ffxlb__ebtl = urlparse(conn_str)
    jiuw__mesd = {}
    if ffxlb__ebtl.username:
        jiuw__mesd['user'] = ffxlb__ebtl.username
    if ffxlb__ebtl.password:
        jiuw__mesd['password'] = ffxlb__ebtl.password
    if ffxlb__ebtl.hostname:
        jiuw__mesd['account'] = ffxlb__ebtl.hostname
    if ffxlb__ebtl.port:
        jiuw__mesd['port'] = ffxlb__ebtl.port
    if ffxlb__ebtl.path:
        bkrn__hpk = ffxlb__ebtl.path
        if bkrn__hpk.startswith('/'):
            bkrn__hpk = bkrn__hpk[1:]
        avqbv__ssz, schema = bkrn__hpk.split('/')
        jiuw__mesd['database'] = avqbv__ssz
        if schema:
            jiuw__mesd['schema'] = schema
    if ffxlb__ebtl.query:
        for uekdz__qmpe, hmkwc__lyrqw in parse_qsl(ffxlb__ebtl.query):
            jiuw__mesd[uekdz__qmpe] = hmkwc__lyrqw
            if uekdz__qmpe == 'session_parameters':
                jiuw__mesd[uekdz__qmpe] = json.loads(hmkwc__lyrqw)
    jiuw__mesd['application'] = 'bodo'
    return jiuw__mesd


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for hgw__oag in batches:
            hgw__oag._bodo_num_rows = hgw__oag.rowcount
            self._bodo_total_rows += hgw__oag._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    oox__dsv = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    vdl__frkej = MPI.COMM_WORLD
    washs__lbji = tracing.Event('snowflake_connect', is_parallel=False)
    keds__hnlp = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**keds__hnlp)
    washs__lbji.finalize()
    if bodo.get_rank() == 0:
        hghi__fux = conn.cursor()
        ypz__lvw = tracing.Event('get_schema', is_parallel=False)
        qdi__syoe = f'select * from ({query}) x LIMIT {100}'
        schema = hghi__fux.execute(qdi__syoe).fetch_arrow_all().schema
        ypz__lvw.finalize()
        yjhjz__cfbza = tracing.Event('execute_query', is_parallel=False)
        hghi__fux.execute(query)
        yjhjz__cfbza.finalize()
        batches = hghi__fux.get_result_batches()
        vdl__frkej.bcast((batches, schema))
    else:
        batches, schema = vdl__frkej.bcast(None)
    iqs__dmunm = SnowflakeDataset(batches, schema, conn)
    oox__dsv.finalize()
    return iqs__dmunm
