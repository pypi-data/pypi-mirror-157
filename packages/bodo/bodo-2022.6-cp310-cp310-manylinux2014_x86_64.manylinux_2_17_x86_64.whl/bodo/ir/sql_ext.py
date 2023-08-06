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
    ern__dfgs = urlparse(con_str)
    db_type = ern__dfgs.scheme
    ueag__mks = ern__dfgs.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', ueag__mks
    if db_type == 'mysql+pymysql':
        return 'mysql', ueag__mks
    if con_str == 'iceberg+glue' or ern__dfgs.scheme in ('iceberg',
        'iceberg+file', 'iceberg+thrift', 'iceberg+http', 'iceberg+https'):
        return 'iceberg', ueag__mks
    return db_type, ueag__mks


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
    zho__pbx = sql_node.out_vars[0].name
    awtnu__esh = sql_node.out_vars[1].name
    if zho__pbx not in lives and awtnu__esh not in lives:
        return None
    elif zho__pbx not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif awtnu__esh not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        vkq__eqwhg = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        lhwt__sit = []
        egnn__vgzr = []
        for umoyw__tncer in sql_node.out_used_cols:
            mlc__flcwj = sql_node.df_colnames[umoyw__tncer]
            lhwt__sit.append(mlc__flcwj)
            if isinstance(sql_node.out_types[umoyw__tncer], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                egnn__vgzr.append(mlc__flcwj)
        if sql_node.index_column_name:
            lhwt__sit.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                egnn__vgzr.append(sql_node.index_column_name)
        xjjt__huvcg = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', vkq__eqwhg,
            xjjt__huvcg, lhwt__sit)
        if egnn__vgzr:
            efxv__rlvky = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                efxv__rlvky, xjjt__huvcg, egnn__vgzr)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        nbn__oznw = set(sql_node.unsupported_columns)
        ayra__cmmd = set(sql_node.out_used_cols)
        nrr__bid = ayra__cmmd & nbn__oznw
        if nrr__bid:
            tqz__blglt = sorted(nrr__bid)
            iovek__umlb = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            mdao__zwzc = 0
            for vpjug__woxx in tqz__blglt:
                while sql_node.unsupported_columns[mdao__zwzc] != vpjug__woxx:
                    mdao__zwzc += 1
                iovek__umlb.append(
                    f"Column '{sql_node.original_df_colnames[vpjug__woxx]}' with unsupported arrow type {sql_node.unsupported_arrow_types[mdao__zwzc]}"
                    )
                mdao__zwzc += 1
            rrtq__mvx = '\n'.join(iovek__umlb)
            raise BodoError(rrtq__mvx, loc=sql_node.loc)
    duz__rio, ozooq__dffbj = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    hgjx__gxlyn = ', '.join(duz__rio.values())
    dvoh__nrcxk = (
        f'def sql_impl(sql_request, conn, database_schema, {hgjx__gxlyn}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        atkhj__yqbd = []
        for pearq__kqyi in sql_node.filters:
            wrza__ehwgp = [' '.join(['(', kakjk__upp[0], kakjk__upp[1], '{' +
                duz__rio[kakjk__upp[2].name] + '}' if isinstance(kakjk__upp
                [2], ir.Var) else kakjk__upp[2], ')']) for kakjk__upp in
                pearq__kqyi]
            atkhj__yqbd.append(' ( ' + ' AND '.join(wrza__ehwgp) + ' ) ')
        bhk__sbehi = ' WHERE ' + ' OR '.join(atkhj__yqbd)
        for umoyw__tncer, ulne__pso in enumerate(duz__rio.values()):
            dvoh__nrcxk += f'    {ulne__pso} = get_sql_literal({ulne__pso})\n'
        dvoh__nrcxk += f'    sql_request = f"{{sql_request}} {bhk__sbehi}"\n'
    rcziv__ydd = ''
    if sql_node.db_type == 'iceberg':
        rcziv__ydd = hgjx__gxlyn
    dvoh__nrcxk += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {rcziv__ydd})
"""
    yhbi__wum = {}
    exec(dvoh__nrcxk, {}, yhbi__wum)
    jde__lyy = yhbi__wum['sql_impl']
    jvrdn__cvpm = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, sql_node.index_column_name, sql_node.index_column_type,
        sql_node.out_used_cols, typingctx, targetctx, sql_node.db_type,
        sql_node.limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    kalx__wtpc = (types.none if sql_node.database_schema is None else
        string_type)
    zvv__vzkt = compile_to_numba_ir(jde__lyy, {'_sql_reader_py':
        jvrdn__cvpm, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type, kalx__wtpc
        ) + tuple(typemap[yfvph__zinz.name] for yfvph__zinz in ozooq__dffbj
        ), typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        hhqhy__fxzxr = [sql_node.df_colnames[umoyw__tncer] for umoyw__tncer in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            hhqhy__fxzxr.append(sql_node.index_column_name)
        bpmkk__mwp = escape_column_names(hhqhy__fxzxr, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            wugfu__gdtic = ('SELECT ' + bpmkk__mwp + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            wugfu__gdtic = ('SELECT ' + bpmkk__mwp + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        wugfu__gdtic = sql_node.sql_request
    replace_arg_nodes(zvv__vzkt, [ir.Const(wugfu__gdtic, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + ozooq__dffbj)
    tut__cju = zvv__vzkt.body[:-3]
    tut__cju[-2].target = sql_node.out_vars[0]
    tut__cju[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        tut__cju.pop(-1)
    elif not sql_node.out_used_cols:
        tut__cju.pop(-2)
    return tut__cju


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        hhqhy__fxzxr = [(rhzy__xuur.upper() if rhzy__xuur in
            converted_colnames else rhzy__xuur) for rhzy__xuur in col_names]
        bpmkk__mwp = ', '.join([f'"{rhzy__xuur}"' for rhzy__xuur in
            hhqhy__fxzxr])
    elif db_type == 'mysql':
        bpmkk__mwp = ', '.join([f'`{rhzy__xuur}`' for rhzy__xuur in col_names])
    else:
        bpmkk__mwp = ', '.join([f'"{rhzy__xuur}"' for rhzy__xuur in col_names])
    return bpmkk__mwp


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    zog__xnx = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(zog__xnx,
        'Filter pushdown')
    if zog__xnx == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(zog__xnx, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif zog__xnx == bodo.pd_timestamp_type:

        def impl(filter_value):
            yuwg__laebx = filter_value.nanosecond
            pxrko__zmbbu = ''
            if yuwg__laebx < 10:
                pxrko__zmbbu = '00'
            elif yuwg__laebx < 100:
                pxrko__zmbbu = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{pxrko__zmbbu}{yuwg__laebx}'"
                )
        return impl
    elif zog__xnx == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {zog__xnx} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    cfnr__trwjm = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    zog__xnx = types.unliteral(filter_value)
    if isinstance(zog__xnx, types.List) and (isinstance(zog__xnx.dtype,
        scalar_isinstance) or zog__xnx.dtype in cfnr__trwjm):

        def impl(filter_value):
            bqus__ozw = ', '.join([_get_snowflake_sql_literal_scalar(
                rhzy__xuur) for rhzy__xuur in filter_value])
            return f'({bqus__ozw})'
        return impl
    elif isinstance(zog__xnx, scalar_isinstance) or zog__xnx in cfnr__trwjm:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {zog__xnx} used in filter pushdown.'
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
    except ImportError as lkdq__udtc:
        tplww__cuqf = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(tplww__cuqf)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as lkdq__udtc:
        tplww__cuqf = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(tplww__cuqf)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as lkdq__udtc:
        tplww__cuqf = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(tplww__cuqf)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as lkdq__udtc:
        tplww__cuqf = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(tplww__cuqf)


def req_limit(sql_request):
    import re
    zcg__xdrtn = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    xqqv__gbduc = zcg__xdrtn.search(sql_request)
    if xqqv__gbduc:
        return int(xqqv__gbduc.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type, limit, parallel, typemap, filters, pyarrow_table_schema:
    'Optional[pyarrow.Schema]'):
    ogofh__oor = next_label()
    hhqhy__fxzxr = [col_names[umoyw__tncer] for umoyw__tncer in out_used_cols]
    pmcry__huava = [col_typs[umoyw__tncer] for umoyw__tncer in out_used_cols]
    if index_column_name:
        hhqhy__fxzxr.append(index_column_name)
        pmcry__huava.append(index_column_type)
    tlqpc__hhax = None
    ffllr__tgqg = None
    ruj__rulu = TableType(tuple(col_typs)) if out_used_cols else types.none
    rcziv__ydd = ''
    duz__rio = {}
    ozooq__dffbj = []
    if filters and db_type == 'iceberg':
        duz__rio, ozooq__dffbj = bodo.ir.connector.generate_filter_map(filters)
        rcziv__ydd = ', '.join(duz__rio.values())
    dvoh__nrcxk = (
        f'def sql_reader_py(sql_request, conn, database_schema, {rcziv__ydd}):\n'
        )
    if db_type == 'iceberg':
        xzah__npwyz, orqj__cdek = bodo.ir.connector.generate_arrow_filters(
            filters, duz__rio, ozooq__dffbj, col_names, col_names, col_typs,
            typemap, 'iceberg')
        agpvx__gkrro: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[umoyw__tncer]) for umoyw__tncer in out_used_cols]
        ympm__uxxh = {ntzgj__wza: umoyw__tncer for umoyw__tncer, ntzgj__wza in
            enumerate(agpvx__gkrro)}
        vqoai__dbnwo = [int(is_nullable(col_typs[umoyw__tncer])) for
            umoyw__tncer in agpvx__gkrro]
        llbo__ess = ',' if rcziv__ydd else ''
        dvoh__nrcxk += (
            f"  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})\n")
        dvoh__nrcxk += f"""  dnf_filters, expr_filters = get_filters_pyobject("{xzah__npwyz}", "{orqj__cdek}", ({rcziv__ydd}{llbo__ess}))
"""
        dvoh__nrcxk += f'  out_table = iceberg_read(\n'
        dvoh__nrcxk += (
            f'    unicode_to_utf8(conn), unicode_to_utf8(database_schema),\n')
        dvoh__nrcxk += (
            f'    unicode_to_utf8(sql_request), {parallel}, dnf_filters,\n')
        dvoh__nrcxk += (
            f'    expr_filters, selected_cols_arr_{ogofh__oor}.ctypes,\n')
        dvoh__nrcxk += (
            f'    {len(agpvx__gkrro)}, nullable_cols_arr_{ogofh__oor}.ctypes,\n'
            )
        dvoh__nrcxk += f'    pyarrow_table_schema_{ogofh__oor},\n'
        dvoh__nrcxk += f'  )\n'
        dvoh__nrcxk += f'  check_and_propagate_cpp_exception()\n'
        dud__gwp = not out_used_cols
        ruj__rulu = TableType(tuple(col_typs))
        if dud__gwp:
            ruj__rulu = types.none
        awtnu__esh = 'None'
        if index_column_name is not None:
            xdfjm__fzbou = len(out_used_cols) + 1 if not dud__gwp else 0
            awtnu__esh = (
                f'info_to_array(info_from_table(out_table, {xdfjm__fzbou}), index_col_typ)'
                )
        dvoh__nrcxk += f'  index_var = {awtnu__esh}\n'
        tlqpc__hhax = None
        if not dud__gwp:
            tlqpc__hhax = []
            rdwv__jmbk = 0
            for umoyw__tncer in range(len(col_names)):
                if rdwv__jmbk < len(out_used_cols
                    ) and umoyw__tncer == out_used_cols[rdwv__jmbk]:
                    tlqpc__hhax.append(ympm__uxxh[umoyw__tncer])
                    rdwv__jmbk += 1
                else:
                    tlqpc__hhax.append(-1)
            tlqpc__hhax = np.array(tlqpc__hhax, dtype=np.int64)
        if dud__gwp:
            dvoh__nrcxk += '  table_var = None\n'
        else:
            dvoh__nrcxk += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{ogofh__oor}, py_table_type_{ogofh__oor})
"""
        dvoh__nrcxk += f'  delete_table(out_table)\n'
        dvoh__nrcxk += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        dvoh__nrcxk += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        vqoai__dbnwo = [int(is_nullable(col_typs[umoyw__tncer])) for
            umoyw__tncer in out_used_cols]
        if index_column_name:
            vqoai__dbnwo.append(int(is_nullable(index_column_type)))
        dvoh__nrcxk += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(vqoai__dbnwo)}, np.array({vqoai__dbnwo}, dtype=np.int32).ctypes)
"""
        dvoh__nrcxk += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            dvoh__nrcxk += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            dvoh__nrcxk += '  index_var = None\n'
        if out_used_cols:
            mdao__zwzc = []
            rdwv__jmbk = 0
            for umoyw__tncer in range(len(col_names)):
                if rdwv__jmbk < len(out_used_cols
                    ) and umoyw__tncer == out_used_cols[rdwv__jmbk]:
                    mdao__zwzc.append(rdwv__jmbk)
                    rdwv__jmbk += 1
                else:
                    mdao__zwzc.append(-1)
            tlqpc__hhax = np.array(mdao__zwzc, dtype=np.int64)
            dvoh__nrcxk += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{ogofh__oor}, py_table_type_{ogofh__oor})
"""
        else:
            dvoh__nrcxk += '  table_var = None\n'
        dvoh__nrcxk += '  delete_table(out_table)\n'
        dvoh__nrcxk += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            dvoh__nrcxk += f"""  type_usecols_offsets_arr_{ogofh__oor}_2 = type_usecols_offsets_arr_{ogofh__oor}
"""
            ffllr__tgqg = np.array(out_used_cols, dtype=np.int64)
        dvoh__nrcxk += '  df_typeref_2 = df_typeref\n'
        dvoh__nrcxk += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            dvoh__nrcxk += '  pymysql_check()\n'
        elif db_type == 'oracle':
            dvoh__nrcxk += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            dvoh__nrcxk += '  psycopg2_check()\n'
        if parallel:
            dvoh__nrcxk += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                dvoh__nrcxk += f'  nb_row = {limit}\n'
            else:
                dvoh__nrcxk += '  with objmode(nb_row="int64"):\n'
                dvoh__nrcxk += f'     if rank == {MPI_ROOT}:\n'
                dvoh__nrcxk += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                dvoh__nrcxk += '         frame = pd.read_sql(sql_cons, conn)\n'
                dvoh__nrcxk += '         nb_row = frame.iat[0,0]\n'
                dvoh__nrcxk += '     else:\n'
                dvoh__nrcxk += '         nb_row = 0\n'
                dvoh__nrcxk += '  nb_row = bcast_scalar(nb_row)\n'
            dvoh__nrcxk += f"""  with objmode(table_var=py_table_type_{ogofh__oor}, index_var=index_col_typ):
"""
            dvoh__nrcxk += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
            if db_type == 'oracle':
                dvoh__nrcxk += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                dvoh__nrcxk += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            dvoh__nrcxk += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            dvoh__nrcxk += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            dvoh__nrcxk += f"""  with objmode(table_var=py_table_type_{ogofh__oor}, index_var=index_col_typ):
"""
            dvoh__nrcxk += '    df_ret = pd.read_sql(sql_request, conn)\n'
            dvoh__nrcxk += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            dvoh__nrcxk += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            dvoh__nrcxk += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            dvoh__nrcxk += '    index_var = None\n'
        if out_used_cols:
            dvoh__nrcxk += f'    arrs = []\n'
            dvoh__nrcxk += f'    for i in range(df_ret.shape[1]):\n'
            dvoh__nrcxk += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            dvoh__nrcxk += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{ogofh__oor}_2, {len(col_names)})
"""
        else:
            dvoh__nrcxk += '    table_var = None\n'
    dvoh__nrcxk += '  return (table_var, index_var)\n'
    bsuej__qjqt = globals()
    bsuej__qjqt.update({'bodo': bodo, f'py_table_type_{ogofh__oor}':
        ruj__rulu, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        bsuej__qjqt.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{ogofh__oor}': tlqpc__hhax})
    if db_type == 'iceberg':
        bsuej__qjqt.update({f'selected_cols_arr_{ogofh__oor}': np.array(
            agpvx__gkrro, np.int32), f'nullable_cols_arr_{ogofh__oor}': np.
            array(vqoai__dbnwo, np.int32), f'py_table_type_{ogofh__oor}':
            ruj__rulu, f'pyarrow_table_schema_{ogofh__oor}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        bsuej__qjqt.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        bsuej__qjqt.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(pmcry__huava), bodo.RangeIndexType(
            None), tuple(hhqhy__fxzxr)), 'Table': Table,
            f'type_usecols_offsets_arr_{ogofh__oor}': ffllr__tgqg})
    yhbi__wum = {}
    exec(dvoh__nrcxk, bsuej__qjqt, yhbi__wum)
    jvrdn__cvpm = yhbi__wum['sql_reader_py']
    eot__ktjyb = numba.njit(jvrdn__cvpm)
    compiled_funcs.append(eot__ktjyb)
    return eot__ktjyb


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
