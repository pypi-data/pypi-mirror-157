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
    hnin__gcigz = None
    zucuv__porbp = None
    wsb__msuk = None
    if bodo.get_rank() == 0:
        try:
            hnin__gcigz, zucuv__porbp, wsb__msuk = (bodo_iceberg_connector.
                get_iceberg_typing_schema(con, database_schema, table_name))
        except bodo_iceberg_connector.IcebergError as vtg__yba:
            if isinstance(vtg__yba, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                hnin__gcigz = BodoError(
                    f'{vtg__yba.message}:\n {str(vtg__yba.java_error)}')
            else:
                hnin__gcigz = BodoError(vtg__yba.message)
    krve__aavh = MPI.COMM_WORLD
    hnin__gcigz = krve__aavh.bcast(hnin__gcigz)
    if isinstance(hnin__gcigz, Exception):
        raise hnin__gcigz
    jaxo__ybog = hnin__gcigz
    zucuv__porbp = krve__aavh.bcast(zucuv__porbp)
    wsb__msuk = krve__aavh.bcast(wsb__msuk)
    mid__idvwv = [_get_numba_typ_from_pa_typ(idlpa__jhtm, False, True, None
        )[0] for idlpa__jhtm in zucuv__porbp]
    return jaxo__ybog, mid__idvwv, wsb__msuk


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        xal__atn = bodo_iceberg_connector.bodo_connector_get_parquet_file_list(
            conn, database_schema, table_name, filters)
    except bodo_iceberg_connector.IcebergError as vtg__yba:
        if isinstance(vtg__yba, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(f'{vtg__yba.message}:\n {str(vtg__yba.java_error)}'
                )
        else:
            raise BodoError(vtg__yba.message)
    return xal__atn


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
    ulpa__qjelb = tracing.Event('get_iceberg_pq_dataset')
    krve__aavh = MPI.COMM_WORLD
    qwcbk__nfq = []
    if bodo.get_rank() == 0:
        xuzlh__aty = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            qwcbk__nfq = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                agzi__zfpat = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                xuzlh__aty.add_attribute('num_files', len(qwcbk__nfq))
                xuzlh__aty.add_attribute(f'first_{agzi__zfpat}_files', ', '
                    .join(qwcbk__nfq[:agzi__zfpat]))
        except Exception as vtg__yba:
            qwcbk__nfq = vtg__yba
        xuzlh__aty.finalize()
    qwcbk__nfq = krve__aavh.bcast(qwcbk__nfq)
    if isinstance(qwcbk__nfq, Exception):
        brzdj__xtacn = qwcbk__nfq
        raise BodoError(
            f"""Error reading Iceberg Table: {type(brzdj__xtacn).__name__}: {str(brzdj__xtacn)}
"""
            )
    crt__rwz: List[str] = qwcbk__nfq
    if len(crt__rwz) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(crt__rwz,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as vtg__yba:
            if re.search('Schema .* was different', str(vtg__yba), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{vtg__yba}"""
                    )
            else:
                raise
    yvhg__hwz = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    ulpa__qjelb.finalize()
    return yvhg__hwz
