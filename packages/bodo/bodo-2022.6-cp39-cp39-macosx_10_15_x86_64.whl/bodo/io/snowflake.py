from urllib.parse import parse_qsl, urlparse
import pyarrow as pa
import snowflake.connector
import bodo
from bodo.utils import tracing
FIELD_TYPE_TO_PA_TYPE = [pa.int64(), pa.float64(), pa.string(), pa.date32(),
    pa.timestamp('ns'), pa.string(), pa.timestamp('ns'), pa.timestamp('ns'),
    pa.timestamp('ns'), pa.string(), pa.string(), pa.binary(), pa.time64(
    'ns'), pa.bool_()]


def get_connection_params(conn_str):
    import json
    jsjm__siow = urlparse(conn_str)
    hfgqd__nbf = {}
    if jsjm__siow.username:
        hfgqd__nbf['user'] = jsjm__siow.username
    if jsjm__siow.password:
        hfgqd__nbf['password'] = jsjm__siow.password
    if jsjm__siow.hostname:
        hfgqd__nbf['account'] = jsjm__siow.hostname
    if jsjm__siow.port:
        hfgqd__nbf['port'] = jsjm__siow.port
    if jsjm__siow.path:
        tysp__upja = jsjm__siow.path
        if tysp__upja.startswith('/'):
            tysp__upja = tysp__upja[1:]
        rezud__egu, schema = tysp__upja.split('/')
        hfgqd__nbf['database'] = rezud__egu
        if schema:
            hfgqd__nbf['schema'] = schema
    if jsjm__siow.query:
        for gliv__oomiw, nzoo__gni in parse_qsl(jsjm__siow.query):
            hfgqd__nbf[gliv__oomiw] = nzoo__gni
            if gliv__oomiw == 'session_parameters':
                hfgqd__nbf[gliv__oomiw] = json.loads(nzoo__gni)
    hfgqd__nbf['application'] = 'bodo'
    return hfgqd__nbf


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for izapi__uwcr in batches:
            izapi__uwcr._bodo_num_rows = izapi__uwcr.rowcount
            self._bodo_total_rows += izapi__uwcr._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    dot__ahb = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    kqbm__bwyyd = MPI.COMM_WORLD
    mvx__zecui = tracing.Event('snowflake_connect', is_parallel=False)
    gfjj__rzgr = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**gfjj__rzgr)
    mvx__zecui.finalize()
    if bodo.get_rank() == 0:
        hyk__aezfo = conn.cursor()
        oafk__ubs = tracing.Event('get_schema', is_parallel=False)
        ddvm__vhwg = f'select * from ({query}) x LIMIT {100}'
        kzsi__guhe = hyk__aezfo.execute(ddvm__vhwg).fetch_arrow_all()
        if kzsi__guhe is None:
            vdyu__yynu = hyk__aezfo.describe(query)
            zps__owm = [pa.field(znqq__vgtsu.name, FIELD_TYPE_TO_PA_TYPE[
                znqq__vgtsu.type_code]) for znqq__vgtsu in vdyu__yynu]
            schema = pa.schema(zps__owm)
        else:
            schema = kzsi__guhe.schema
        oafk__ubs.finalize()
        uczq__wxubl = tracing.Event('execute_query', is_parallel=False)
        hyk__aezfo.execute(query)
        uczq__wxubl.finalize()
        batches = hyk__aezfo.get_result_batches()
        kqbm__bwyyd.bcast((batches, schema))
    else:
        batches, schema = kqbm__bwyyd.bcast(None)
    pqpo__lmtaa = SnowflakeDataset(batches, schema, conn)
    dot__ahb.finalize()
    return pqpo__lmtaa
