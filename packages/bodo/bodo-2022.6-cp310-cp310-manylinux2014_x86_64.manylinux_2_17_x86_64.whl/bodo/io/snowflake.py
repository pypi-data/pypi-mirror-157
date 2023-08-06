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
    safq__ulr = urlparse(conn_str)
    togn__uctri = {}
    if safq__ulr.username:
        togn__uctri['user'] = safq__ulr.username
    if safq__ulr.password:
        togn__uctri['password'] = safq__ulr.password
    if safq__ulr.hostname:
        togn__uctri['account'] = safq__ulr.hostname
    if safq__ulr.port:
        togn__uctri['port'] = safq__ulr.port
    if safq__ulr.path:
        xwa__vjxtw = safq__ulr.path
        if xwa__vjxtw.startswith('/'):
            xwa__vjxtw = xwa__vjxtw[1:]
        zsr__fbaw, schema = xwa__vjxtw.split('/')
        togn__uctri['database'] = zsr__fbaw
        if schema:
            togn__uctri['schema'] = schema
    if safq__ulr.query:
        for jbn__iybw, gbef__gekjq in parse_qsl(safq__ulr.query):
            togn__uctri[jbn__iybw] = gbef__gekjq
            if jbn__iybw == 'session_parameters':
                togn__uctri[jbn__iybw] = json.loads(gbef__gekjq)
    togn__uctri['application'] = 'bodo'
    return togn__uctri


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for gmq__gac in batches:
            gmq__gac._bodo_num_rows = gmq__gac.rowcount
            self._bodo_total_rows += gmq__gac._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    qse__fmc = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    bcg__voif = MPI.COMM_WORLD
    rtah__qexo = tracing.Event('snowflake_connect', is_parallel=False)
    ynxe__vyo = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**ynxe__vyo)
    rtah__qexo.finalize()
    if bodo.get_rank() == 0:
        zoxsp__tyux = conn.cursor()
        skk__glvd = tracing.Event('get_schema', is_parallel=False)
        ooebv__xvaom = f'select * from ({query}) x LIMIT {100}'
        ovnqz__oxq = zoxsp__tyux.execute(ooebv__xvaom).fetch_arrow_all()
        if ovnqz__oxq is None:
            srboq__jrjfa = zoxsp__tyux.describe(query)
            lhpp__erd = [pa.field(yae__nieq.name, FIELD_TYPE_TO_PA_TYPE[
                yae__nieq.type_code]) for yae__nieq in srboq__jrjfa]
            schema = pa.schema(lhpp__erd)
        else:
            schema = ovnqz__oxq.schema
        skk__glvd.finalize()
        qjdn__gjqa = tracing.Event('execute_query', is_parallel=False)
        zoxsp__tyux.execute(query)
        qjdn__gjqa.finalize()
        batches = zoxsp__tyux.get_result_batches()
        bcg__voif.bcast((batches, schema))
    else:
        batches, schema = bcg__voif.bcast(None)
    vdwy__vxql = SnowflakeDataset(batches, schema, conn)
    qse__fmc.finalize()
    return vdwy__vxql
