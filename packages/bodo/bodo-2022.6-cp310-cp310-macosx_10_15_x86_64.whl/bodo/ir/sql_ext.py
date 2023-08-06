"""
Implementation of pd.read_sql in BODO.
We piggyback on the pandas implementation. Future plan is to have a faster
version for this task.
"""
from typing import List
from urllib.parse import urlparse
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.table import Table, TableType
from bodo.io.helpers import PyArrowTableSchemaType, is_nullable
from bodo.io.parquet_pio import ParquetPredicateType
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.distributed_api import bcast, bcast_scalar
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_and_propagate_cpp_exception
MPI_ROOT = 0


class SqlReader(ir.Stmt):

    def __init__(self, sql_request, connection, df_out, df_colnames,
        out_vars, out_types, converted_colnames, db_type, loc,
        unsupported_columns, unsupported_arrow_types, is_select_query,
        index_column_name, index_column_type, database_schema,
        pyarrow_table_schema=None):
        self.connector_typ = 'sql'
        self.sql_request = sql_request
        self.connection = connection
        self.df_out = df_out
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.converted_colnames = converted_colnames
        self.loc = loc
        self.limit = req_limit(sql_request)
        self.db_type = db_type
        self.filters = None
        self.unsupported_columns = unsupported_columns
        self.unsupported_arrow_types = unsupported_arrow_types
        self.is_select_query = is_select_query
        self.index_column_name = index_column_name
        self.index_column_type = index_column_type
        self.out_used_cols = list(range(len(df_colnames)))
        self.database_schema = database_schema
        self.pyarrow_table_schema = pyarrow_table_schema

    def __repr__(self):
        return (
            f'{self.df_out} = ReadSql(sql_request={self.sql_request}, connection={self.connection}, col_names={self.df_colnames}, types={self.out_types}, vars={self.out_vars}, limit={self.limit}, unsupported_columns={self.unsupported_columns}, unsupported_arrow_types={self.unsupported_arrow_types}, is_select_query={self.is_select_query}, index_column_name={self.index_column_name}, index_column_type={self.index_column_type}, out_used_cols={self.out_used_cols}, database_schema={self.database_schema}, pyarrow_table_schema={self.pyarrow_table_schema})'
            )


def parse_dbtype(con_str):
    bvd__xdee = urlparse(con_str)
    db_type = bvd__xdee.scheme
    pmai__fjc = bvd__xdee.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', pmai__fjc
    if db_type == 'mysql+pymysql':
        return 'mysql', pmai__fjc
    if con_str == 'iceberg+glue' or bvd__xdee.scheme in ('iceberg',
        'iceberg+file', 'iceberg+thrift', 'iceberg+http', 'iceberg+https'):
        return 'iceberg', pmai__fjc
    return db_type, pmai__fjc


def remove_iceberg_prefix(con):
    import sys
    if sys.version_info.minor < 9:
        if con.startswith('iceberg+'):
            con = con[len('iceberg+'):]
        if con.startswith('iceberg://'):
            con = con[len('iceberg://'):]
    else:
        con = con.removeprefix('iceberg+').removeprefix('iceberg://')
    return con


def remove_dead_sql(sql_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    nlv__sgv = sql_node.out_vars[0].name
    wwlid__eko = sql_node.out_vars[1].name
    if nlv__sgv not in lives and wwlid__eko not in lives:
        return None
    elif nlv__sgv not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif wwlid__eko not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        xjop__pmn = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        vfyk__yrzb = []
        fxnep__lbeo = []
        for agv__abb in sql_node.out_used_cols:
            cll__unui = sql_node.df_colnames[agv__abb]
            vfyk__yrzb.append(cll__unui)
            if isinstance(sql_node.out_types[agv__abb], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                fxnep__lbeo.append(cll__unui)
        if sql_node.index_column_name:
            vfyk__yrzb.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                fxnep__lbeo.append(sql_node.index_column_name)
        ktbb__szxlb = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', xjop__pmn,
            ktbb__szxlb, vfyk__yrzb)
        if fxnep__lbeo:
            bbq__pkfuk = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', bbq__pkfuk,
                ktbb__szxlb, fxnep__lbeo)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        krh__huaxr = set(sql_node.unsupported_columns)
        ecb__ujj = set(sql_node.out_used_cols)
        drvm__exyth = ecb__ujj & krh__huaxr
        if drvm__exyth:
            nqgqc__xufsj = sorted(drvm__exyth)
            dzi__muxnx = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            czs__ijn = 0
            for qnoas__qmx in nqgqc__xufsj:
                while sql_node.unsupported_columns[czs__ijn] != qnoas__qmx:
                    czs__ijn += 1
                dzi__muxnx.append(
                    f"Column '{sql_node.original_df_colnames[qnoas__qmx]}' with unsupported arrow type {sql_node.unsupported_arrow_types[czs__ijn]}"
                    )
                czs__ijn += 1
            ywj__rlzq = '\n'.join(dzi__muxnx)
            raise BodoError(ywj__rlzq, loc=sql_node.loc)
    qpm__rik, mks__doc = bodo.ir.connector.generate_filter_map(sql_node.filters
        )
    dhjnd__wtio = ', '.join(qpm__rik.values())
    eqn__teboc = (
        f'def sql_impl(sql_request, conn, database_schema, {dhjnd__wtio}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        yuki__awlva = []
        for cxc__hrz in sql_node.filters:
            nqgau__xuet = [' '.join(['(', bhsw__qxvc[0], bhsw__qxvc[1], '{' +
                qpm__rik[bhsw__qxvc[2].name] + '}' if isinstance(bhsw__qxvc
                [2], ir.Var) else bhsw__qxvc[2], ')']) for bhsw__qxvc in
                cxc__hrz]
            yuki__awlva.append(' ( ' + ' AND '.join(nqgau__xuet) + ' ) ')
        krmg__rjkrb = ' WHERE ' + ' OR '.join(yuki__awlva)
        for agv__abb, xqht__kgznn in enumerate(qpm__rik.values()):
            eqn__teboc += (
                f'    {xqht__kgznn} = get_sql_literal({xqht__kgznn})\n')
        eqn__teboc += f'    sql_request = f"{{sql_request}} {krmg__rjkrb}"\n'
    dyvd__exn = ''
    if sql_node.db_type == 'iceberg':
        dyvd__exn = dhjnd__wtio
    eqn__teboc += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {dyvd__exn})
"""
    hmzb__zrbh = {}
    exec(eqn__teboc, {}, hmzb__zrbh)
    ptqea__qhjf = hmzb__zrbh['sql_impl']
    gub__ygei = _gen_sql_reader_py(sql_node.df_colnames, sql_node.out_types,
        sql_node.index_column_name, sql_node.index_column_type, sql_node.
        out_used_cols, typingctx, targetctx, sql_node.db_type, sql_node.
        limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    hkkm__gdu = types.none if sql_node.database_schema is None else string_type
    belbx__hjkx = compile_to_numba_ir(ptqea__qhjf, {'_sql_reader_py':
        gub__ygei, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type, hkkm__gdu) +
        tuple(typemap[vemre__hfv.name] for vemre__hfv in mks__doc), typemap
        =typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        wdg__hynpw = [sql_node.df_colnames[agv__abb] for agv__abb in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            wdg__hynpw.append(sql_node.index_column_name)
        bhd__kybvr = escape_column_names(wdg__hynpw, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            fnqxv__vqir = ('SELECT ' + bhd__kybvr + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            fnqxv__vqir = ('SELECT ' + bhd__kybvr + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        fnqxv__vqir = sql_node.sql_request
    replace_arg_nodes(belbx__hjkx, [ir.Const(fnqxv__vqir, sql_node.loc), ir
        .Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + mks__doc)
    ambmx__evr = belbx__hjkx.body[:-3]
    ambmx__evr[-2].target = sql_node.out_vars[0]
    ambmx__evr[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        ambmx__evr.pop(-1)
    elif not sql_node.out_used_cols:
        ambmx__evr.pop(-2)
    return ambmx__evr


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        wdg__hynpw = [(xhexp__rnaa.upper() if xhexp__rnaa in
            converted_colnames else xhexp__rnaa) for xhexp__rnaa in col_names]
        bhd__kybvr = ', '.join([f'"{xhexp__rnaa}"' for xhexp__rnaa in
            wdg__hynpw])
    elif db_type == 'mysql':
        bhd__kybvr = ', '.join([f'`{xhexp__rnaa}`' for xhexp__rnaa in
            col_names])
    else:
        bhd__kybvr = ', '.join([f'"{xhexp__rnaa}"' for xhexp__rnaa in
            col_names])
    return bhd__kybvr


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    ibxk__miwzu = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ibxk__miwzu,
        'Filter pushdown')
    if ibxk__miwzu == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(ibxk__miwzu, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif ibxk__miwzu == bodo.pd_timestamp_type:

        def impl(filter_value):
            deh__shymr = filter_value.nanosecond
            lwqe__kilr = ''
            if deh__shymr < 10:
                lwqe__kilr = '00'
            elif deh__shymr < 100:
                lwqe__kilr = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{lwqe__kilr}{deh__shymr}'"
                )
        return impl
    elif ibxk__miwzu == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {ibxk__miwzu} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    pjsp__guy = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    ibxk__miwzu = types.unliteral(filter_value)
    if isinstance(ibxk__miwzu, types.List) and (isinstance(ibxk__miwzu.
        dtype, scalar_isinstance) or ibxk__miwzu.dtype in pjsp__guy):

        def impl(filter_value):
            fuc__ofpjs = ', '.join([_get_snowflake_sql_literal_scalar(
                xhexp__rnaa) for xhexp__rnaa in filter_value])
            return f'({fuc__ofpjs})'
        return impl
    elif isinstance(ibxk__miwzu, scalar_isinstance
        ) or ibxk__miwzu in pjsp__guy:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {ibxk__miwzu} used in filter pushdown.'
            )


def sql_remove_dead_column(sql_node, column_live_map, equiv_vars, typemap):
    return bodo.ir.connector.base_connector_remove_dead_columns(sql_node,
        column_live_map, equiv_vars, typemap, 'SQLReader', sql_node.df_colnames
        )


numba.parfors.array_analysis.array_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[SqlReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[SqlReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[SqlReader] = remove_dead_sql
numba.core.analysis.ir_extension_usedefs[SqlReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[SqlReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[SqlReader] = sql_distributed_run
remove_dead_column_extensions[SqlReader] = sql_remove_dead_column
ir_extension_table_column_use[SqlReader
    ] = bodo.ir.connector.connector_table_column_use
compiled_funcs = []


@numba.njit
def sqlalchemy_check():
    with numba.objmode():
        sqlalchemy_check_()


def sqlalchemy_check_():
    try:
        import sqlalchemy
    except ImportError as mzhue__jjdb:
        osghg__dsbdb = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(osghg__dsbdb)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as mzhue__jjdb:
        osghg__dsbdb = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(osghg__dsbdb)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as mzhue__jjdb:
        osghg__dsbdb = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(osghg__dsbdb)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as mzhue__jjdb:
        osghg__dsbdb = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(osghg__dsbdb)


def req_limit(sql_request):
    import re
    zhast__slot = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    ybp__zmrbl = zhast__slot.search(sql_request)
    if ybp__zmrbl:
        return int(ybp__zmrbl.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type, limit, parallel, typemap, filters, pyarrow_table_schema:
    'Optional[pyarrow.Schema]'):
    icokx__tggv = next_label()
    wdg__hynpw = [col_names[agv__abb] for agv__abb in out_used_cols]
    nqr__lbty = [col_typs[agv__abb] for agv__abb in out_used_cols]
    if index_column_name:
        wdg__hynpw.append(index_column_name)
        nqr__lbty.append(index_column_type)
    aod__jbcc = None
    bva__fcl = None
    oss__lchwz = TableType(tuple(col_typs)) if out_used_cols else types.none
    dyvd__exn = ''
    qpm__rik = {}
    mks__doc = []
    if filters and db_type == 'iceberg':
        qpm__rik, mks__doc = bodo.ir.connector.generate_filter_map(filters)
        dyvd__exn = ', '.join(qpm__rik.values())
    eqn__teboc = (
        f'def sql_reader_py(sql_request, conn, database_schema, {dyvd__exn}):\n'
        )
    if db_type == 'iceberg':
        dujiz__ldnb, heskx__tbnd = bodo.ir.connector.generate_arrow_filters(
            filters, qpm__rik, mks__doc, col_names, col_names, col_typs,
            typemap, 'iceberg')
        bbj__vqg: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[agv__abb]) for agv__abb in out_used_cols]
        bccm__eeu = {wrkd__rhec: agv__abb for agv__abb, wrkd__rhec in
            enumerate(bbj__vqg)}
        brc__zhy = [int(is_nullable(col_typs[agv__abb])) for agv__abb in
            bbj__vqg]
        chbh__lkoj = ',' if dyvd__exn else ''
        eqn__teboc += (
            f"  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})\n")
        eqn__teboc += f"""  dnf_filters, expr_filters = get_filters_pyobject("{dujiz__ldnb}", "{heskx__tbnd}", ({dyvd__exn}{chbh__lkoj}))
"""
        eqn__teboc += f'  out_table = iceberg_read(\n'
        eqn__teboc += (
            f'    unicode_to_utf8(conn), unicode_to_utf8(database_schema),\n')
        eqn__teboc += (
            f'    unicode_to_utf8(sql_request), {parallel}, dnf_filters,\n')
        eqn__teboc += (
            f'    expr_filters, selected_cols_arr_{icokx__tggv}.ctypes,\n')
        eqn__teboc += (
            f'    {len(bbj__vqg)}, nullable_cols_arr_{icokx__tggv}.ctypes,\n')
        eqn__teboc += f'    pyarrow_table_schema_{icokx__tggv},\n'
        eqn__teboc += f'  )\n'
        eqn__teboc += f'  check_and_propagate_cpp_exception()\n'
        tvy__zia = not out_used_cols
        oss__lchwz = TableType(tuple(col_typs))
        if tvy__zia:
            oss__lchwz = types.none
        wwlid__eko = 'None'
        if index_column_name is not None:
            dcxhm__zvwa = len(out_used_cols) + 1 if not tvy__zia else 0
            wwlid__eko = (
                f'info_to_array(info_from_table(out_table, {dcxhm__zvwa}), index_col_typ)'
                )
        eqn__teboc += f'  index_var = {wwlid__eko}\n'
        aod__jbcc = None
        if not tvy__zia:
            aod__jbcc = []
            tfib__emzjv = 0
            for agv__abb in range(len(col_names)):
                if tfib__emzjv < len(out_used_cols
                    ) and agv__abb == out_used_cols[tfib__emzjv]:
                    aod__jbcc.append(bccm__eeu[agv__abb])
                    tfib__emzjv += 1
                else:
                    aod__jbcc.append(-1)
            aod__jbcc = np.array(aod__jbcc, dtype=np.int64)
        if tvy__zia:
            eqn__teboc += '  table_var = None\n'
        else:
            eqn__teboc += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{icokx__tggv}, py_table_type_{icokx__tggv})
"""
        eqn__teboc += f'  delete_table(out_table)\n'
        eqn__teboc += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        eqn__teboc += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        brc__zhy = [int(is_nullable(col_typs[agv__abb])) for agv__abb in
            out_used_cols]
        if index_column_name:
            brc__zhy.append(int(is_nullable(index_column_type)))
        eqn__teboc += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(brc__zhy)}, np.array({brc__zhy}, dtype=np.int32).ctypes)
"""
        eqn__teboc += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            eqn__teboc += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            eqn__teboc += '  index_var = None\n'
        if out_used_cols:
            czs__ijn = []
            tfib__emzjv = 0
            for agv__abb in range(len(col_names)):
                if tfib__emzjv < len(out_used_cols
                    ) and agv__abb == out_used_cols[tfib__emzjv]:
                    czs__ijn.append(tfib__emzjv)
                    tfib__emzjv += 1
                else:
                    czs__ijn.append(-1)
            aod__jbcc = np.array(czs__ijn, dtype=np.int64)
            eqn__teboc += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{icokx__tggv}, py_table_type_{icokx__tggv})
"""
        else:
            eqn__teboc += '  table_var = None\n'
        eqn__teboc += '  delete_table(out_table)\n'
        eqn__teboc += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            eqn__teboc += f"""  type_usecols_offsets_arr_{icokx__tggv}_2 = type_usecols_offsets_arr_{icokx__tggv}
"""
            bva__fcl = np.array(out_used_cols, dtype=np.int64)
        eqn__teboc += '  df_typeref_2 = df_typeref\n'
        eqn__teboc += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            eqn__teboc += '  pymysql_check()\n'
        elif db_type == 'oracle':
            eqn__teboc += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            eqn__teboc += '  psycopg2_check()\n'
        if parallel:
            eqn__teboc += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                eqn__teboc += f'  nb_row = {limit}\n'
            else:
                eqn__teboc += '  with objmode(nb_row="int64"):\n'
                eqn__teboc += f'     if rank == {MPI_ROOT}:\n'
                eqn__teboc += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                eqn__teboc += '         frame = pd.read_sql(sql_cons, conn)\n'
                eqn__teboc += '         nb_row = frame.iat[0,0]\n'
                eqn__teboc += '     else:\n'
                eqn__teboc += '         nb_row = 0\n'
                eqn__teboc += '  nb_row = bcast_scalar(nb_row)\n'
            eqn__teboc += f"""  with objmode(table_var=py_table_type_{icokx__tggv}, index_var=index_col_typ):
"""
            eqn__teboc += (
                '    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)\n'
                )
            if db_type == 'oracle':
                eqn__teboc += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                eqn__teboc += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            eqn__teboc += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            eqn__teboc += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            eqn__teboc += f"""  with objmode(table_var=py_table_type_{icokx__tggv}, index_var=index_col_typ):
"""
            eqn__teboc += '    df_ret = pd.read_sql(sql_request, conn)\n'
            eqn__teboc += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            eqn__teboc += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            eqn__teboc += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            eqn__teboc += '    index_var = None\n'
        if out_used_cols:
            eqn__teboc += f'    arrs = []\n'
            eqn__teboc += f'    for i in range(df_ret.shape[1]):\n'
            eqn__teboc += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            eqn__teboc += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{icokx__tggv}_2, {len(col_names)})
"""
        else:
            eqn__teboc += '    table_var = None\n'
    eqn__teboc += '  return (table_var, index_var)\n'
    uyl__vhvki = globals()
    uyl__vhvki.update({'bodo': bodo, f'py_table_type_{icokx__tggv}':
        oss__lchwz, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        uyl__vhvki.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{icokx__tggv}': aod__jbcc})
    if db_type == 'iceberg':
        uyl__vhvki.update({f'selected_cols_arr_{icokx__tggv}': np.array(
            bbj__vqg, np.int32), f'nullable_cols_arr_{icokx__tggv}': np.
            array(brc__zhy, np.int32), f'py_table_type_{icokx__tggv}':
            oss__lchwz, f'pyarrow_table_schema_{icokx__tggv}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        uyl__vhvki.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        uyl__vhvki.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(nqr__lbty), bodo.RangeIndexType(None),
            tuple(wdg__hynpw)), 'Table': Table,
            f'type_usecols_offsets_arr_{icokx__tggv}': bva__fcl})
    hmzb__zrbh = {}
    exec(eqn__teboc, uyl__vhvki, hmzb__zrbh)
    gub__ygei = hmzb__zrbh['sql_reader_py']
    mfde__ohuo = numba.njit(gub__ygei)
    compiled_funcs.append(mfde__ohuo)
    return mfde__ohuo


_snowflake_read = types.ExternalFunction('snowflake_read', table_type(types
    .voidptr, types.voidptr, types.boolean, types.int64, types.voidptr))
parquet_predicate_type = ParquetPredicateType()
pyarrow_table_schema_type = PyArrowTableSchemaType()
_iceberg_read = types.ExternalFunction('iceberg_pq_read', table_type(types.
    voidptr, types.voidptr, types.voidptr, types.boolean,
    parquet_predicate_type, parquet_predicate_type, types.voidptr, types.
    int32, types.voidptr, pyarrow_table_schema_type))
import llvmlite.binding as ll
from bodo.io import arrow_cpp
ll.add_symbol('snowflake_read', arrow_cpp.snowflake_read)
ll.add_symbol('iceberg_pq_read', arrow_cpp.iceberg_pq_read)
