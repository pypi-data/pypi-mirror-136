from urllib.parse import parse_qsl, urlparse
import snowflake.connector
import bodo
from bodo.utils import tracing


def get_connection_params(conn_str):
    import json
    mycd__liyf = urlparse(conn_str)
    glsf__boe = {}
    if mycd__liyf.username:
        glsf__boe['user'] = mycd__liyf.username
    if mycd__liyf.password:
        glsf__boe['password'] = mycd__liyf.password
    if mycd__liyf.hostname:
        glsf__boe['account'] = mycd__liyf.hostname
    if mycd__liyf.port:
        glsf__boe['port'] = mycd__liyf.port
    if mycd__liyf.path:
        nxumb__oyfqy = mycd__liyf.path
        if nxumb__oyfqy.startswith('/'):
            nxumb__oyfqy = nxumb__oyfqy[1:]
        bvvjs__prlz, schema = nxumb__oyfqy.split('/')
        glsf__boe['database'] = bvvjs__prlz
        if schema:
            glsf__boe['schema'] = schema
    if mycd__liyf.query:
        for buckw__dynj, tjnct__rxnyy in parse_qsl(mycd__liyf.query):
            glsf__boe[buckw__dynj] = tjnct__rxnyy
            if buckw__dynj == 'session_parameters':
                glsf__boe[buckw__dynj] = json.loads(tjnct__rxnyy)
    glsf__boe['application'] = 'bodo'
    return glsf__boe


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for sbvqm__uxpbe in batches:
            sbvqm__uxpbe._bodo_num_rows = sbvqm__uxpbe.rowcount
            self._bodo_total_rows += sbvqm__uxpbe._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    mwy__starb = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    upwkt__agej = MPI.COMM_WORLD
    jjz__gxj = tracing.Event('snowflake_connect', is_parallel=False)
    eiiw__dgojp = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**eiiw__dgojp)
    jjz__gxj.finalize()
    if bodo.get_rank() == 0:
        gsmwu__wray = conn.cursor()
        rsdp__zpyao = tracing.Event('get_schema', is_parallel=False)
        tqsm__ldrg = f'select * from ({query}) x LIMIT {100}'
        schema = gsmwu__wray.execute(tqsm__ldrg).fetch_arrow_all().schema
        rsdp__zpyao.finalize()
        ksn__jsavr = tracing.Event('execute_query', is_parallel=False)
        gsmwu__wray.execute(query)
        ksn__jsavr.finalize()
        batches = gsmwu__wray.get_result_batches()
        upwkt__agej.bcast((batches, schema))
    else:
        batches, schema = upwkt__agej.bcast(None)
    qmkhg__lyfj = SnowflakeDataset(batches, schema, conn)
    mwy__starb.finalize()
    return qmkhg__lyfj
