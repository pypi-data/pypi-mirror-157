"""
File that contains the main functionality for the Iceberg
integration within the Bodo repo. This does not contain the
main IR transformation.
"""
import os
import re
from typing import List
from mpi4py import MPI
import bodo
from bodo.utils import tracing
from bodo.utils.typing import BodoError


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    hbf__ahy = None
    geb__fhtbt = None
    kmhqa__oiu = None
    if bodo.get_rank() == 0:
        try:
            hbf__ahy, geb__fhtbt, kmhqa__oiu = (bodo_iceberg_connector.
                get_iceberg_typing_schema(con, database_schema, table_name))
        except bodo_iceberg_connector.IcebergError as uxr__mhj:
            if isinstance(uxr__mhj, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                hbf__ahy = BodoError(
                    f'{uxr__mhj.message}:\n {str(uxr__mhj.java_error)}')
            else:
                hbf__ahy = BodoError(uxr__mhj.message)
    nywf__gmbvc = MPI.COMM_WORLD
    hbf__ahy = nywf__gmbvc.bcast(hbf__ahy)
    if isinstance(hbf__ahy, Exception):
        raise hbf__ahy
    vkf__smtyb = hbf__ahy
    geb__fhtbt = nywf__gmbvc.bcast(geb__fhtbt)
    kmhqa__oiu = nywf__gmbvc.bcast(kmhqa__oiu)
    gbg__nrzh = [_get_numba_typ_from_pa_typ(vncm__uql, False, True, None)[0
        ] for vncm__uql in geb__fhtbt]
    return vkf__smtyb, gbg__nrzh, kmhqa__oiu


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        zag__zudxx = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as uxr__mhj:
        if isinstance(uxr__mhj, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(f'{uxr__mhj.message}:\n {str(uxr__mhj.java_error)}'
                )
        else:
            raise BodoError(uxr__mhj.message)
    return zag__zudxx


class IcebergParquetDataset(object):

    def __init__(self, conn, database_schema, table_name, pa_table_schema,
        pq_dataset=None):
        self.pq_dataset = pq_dataset
        self.conn = conn
        self.database_schema = database_schema
        self.table_name = table_name
        self.schema = pa_table_schema
        self.pieces = []
        self._bodo_total_rows = 0
        self._prefix = ''
        self.filesystem = None
        if pq_dataset is not None:
            self.pieces = pq_dataset.pieces
            self._bodo_total_rows = pq_dataset._bodo_total_rows
            self._prefix = pq_dataset._prefix
            self.filesystem = pq_dataset.filesystem


def get_iceberg_pq_dataset(conn, database_schema, table_name,
    typing_pa_table_schema, dnf_filters=None, expr_filters=None,
    is_parallel=False):
    fsx__iagg = tracing.Event('get_iceberg_pq_dataset')
    nywf__gmbvc = MPI.COMM_WORLD
    cfgvi__pyv = []
    if bodo.get_rank() == 0:
        rktmu__wnh = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            cfgvi__pyv = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                ovygo__zvk = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                rktmu__wnh.add_attribute('num_files', len(cfgvi__pyv))
                rktmu__wnh.add_attribute(f'first_{ovygo__zvk}_files', ', '.
                    join(cfgvi__pyv[:ovygo__zvk]))
        except Exception as uxr__mhj:
            cfgvi__pyv = uxr__mhj
        rktmu__wnh.finalize()
    cfgvi__pyv = nywf__gmbvc.bcast(cfgvi__pyv)
    if isinstance(cfgvi__pyv, Exception):
        yjy__ewk = cfgvi__pyv
        raise BodoError(
            f'Error reading Iceberg Table: {type(yjy__ewk).__name__}: {str(yjy__ewk)}\n'
            )
    cota__uiidm: List[str] = cfgvi__pyv
    if len(cota__uiidm) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(cota__uiidm,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as uxr__mhj:
            if re.search('Schema .* was different', str(uxr__mhj), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{uxr__mhj}"""
                    )
            else:
                raise
    bjp__ofnt = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    fsx__iagg.finalize()
    return bjp__ofnt
