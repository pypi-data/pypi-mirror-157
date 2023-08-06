import hashlib
import inspect
import warnings
import snowflake.sqlalchemy
import sqlalchemy.types as sqltypes
from sqlalchemy import exc as sa_exc
from sqlalchemy import util as sa_util
from sqlalchemy.sql import text
_check_snowflake_sqlalchemy_change = True


def _get_schema_columns(self, connection, schema, **kw):
    oxcl__hngeb = {}
    vjlz__eokal, mvq__ggxwp = self._current_database_schema(connection, **kw)
    yvx__twmi = self._denormalize_quote_join(vjlz__eokal, schema)
    try:
        kesjw__moe = self._get_schema_primary_keys(connection, yvx__twmi, **kw)
        fbf__cddro = connection.execute(text(
            """
        SELECT /* sqlalchemy:_get_schema_columns */
                ic.table_name,
                ic.column_name,
                ic.data_type,
                ic.character_maximum_length,
                ic.numeric_precision,
                ic.numeric_scale,
                ic.is_nullable,
                ic.column_default,
                ic.is_identity,
                ic.comment
            FROM information_schema.columns ic
            WHERE ic.table_schema=:table_schema
            ORDER BY ic.ordinal_position"""
            ), {'table_schema': self.denormalize_name(schema)})
    except sa_exc.ProgrammingError as bql__rygti:
        if bql__rygti.orig.errno == 90030:
            return None
        raise
    for table_name, lyyn__uhmnz, zhxbj__dyjpe, epx__mlw, qrgq__qlk, hlr__xpa, ycddi__ufuz, zixh__rkfhv, cifqj__hoif, iet__bwnyt in fbf__cddro:
        table_name = self.normalize_name(table_name)
        lyyn__uhmnz = self.normalize_name(lyyn__uhmnz)
        if table_name not in oxcl__hngeb:
            oxcl__hngeb[table_name] = list()
        if lyyn__uhmnz.startswith('sys_clustering_column'):
            continue
        syfe__dtgyo = self.ischema_names.get(zhxbj__dyjpe, None)
        uums__yrdt = {}
        if syfe__dtgyo is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(zhxbj__dyjpe, lyyn__uhmnz))
            syfe__dtgyo = sqltypes.NULLTYPE
        elif issubclass(syfe__dtgyo, sqltypes.FLOAT):
            uums__yrdt['precision'] = qrgq__qlk
            uums__yrdt['decimal_return_scale'] = hlr__xpa
        elif issubclass(syfe__dtgyo, sqltypes.Numeric):
            uums__yrdt['precision'] = qrgq__qlk
            uums__yrdt['scale'] = hlr__xpa
        elif issubclass(syfe__dtgyo, (sqltypes.String, sqltypes.BINARY)):
            uums__yrdt['length'] = epx__mlw
        lzqnx__ypy = syfe__dtgyo if isinstance(syfe__dtgyo, sqltypes.NullType
            ) else syfe__dtgyo(**uums__yrdt)
        plifg__qcg = kesjw__moe.get(table_name)
        oxcl__hngeb[table_name].append({'name': lyyn__uhmnz, 'type':
            lzqnx__ypy, 'nullable': ycddi__ufuz == 'YES', 'default':
            zixh__rkfhv, 'autoincrement': cifqj__hoif == 'YES', 'comment':
            iet__bwnyt, 'primary_key': lyyn__uhmnz in kesjw__moe[table_name
            ]['constrained_columns'] if plifg__qcg else False})
    return oxcl__hngeb


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_schema_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdf39af1ac165319d3b6074e8cf9296a090a21f0e2c05b644ff8ec0e56e2d769':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns = (
    _get_schema_columns)


def _get_table_columns(self, connection, table_name, schema=None, **kw):
    oxcl__hngeb = []
    vjlz__eokal, mvq__ggxwp = self._current_database_schema(connection, **kw)
    yvx__twmi = self._denormalize_quote_join(vjlz__eokal, schema)
    kesjw__moe = self._get_schema_primary_keys(connection, yvx__twmi, **kw)
    fbf__cddro = connection.execute(text(
        """
    SELECT /* sqlalchemy:get_table_columns */
            ic.table_name,
            ic.column_name,
            ic.data_type,
            ic.character_maximum_length,
            ic.numeric_precision,
            ic.numeric_scale,
            ic.is_nullable,
            ic.column_default,
            ic.is_identity,
            ic.comment
        FROM information_schema.columns ic
        WHERE ic.table_schema=:table_schema
        AND ic.table_name=:table_name
        ORDER BY ic.ordinal_position"""
        ), {'table_schema': self.denormalize_name(schema), 'table_name':
        self.denormalize_name(table_name)})
    for table_name, lyyn__uhmnz, zhxbj__dyjpe, epx__mlw, qrgq__qlk, hlr__xpa, ycddi__ufuz, zixh__rkfhv, cifqj__hoif, iet__bwnyt in fbf__cddro:
        table_name = self.normalize_name(table_name)
        lyyn__uhmnz = self.normalize_name(lyyn__uhmnz)
        if lyyn__uhmnz.startswith('sys_clustering_column'):
            continue
        syfe__dtgyo = self.ischema_names.get(zhxbj__dyjpe, None)
        uums__yrdt = {}
        if syfe__dtgyo is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(zhxbj__dyjpe, lyyn__uhmnz))
            syfe__dtgyo = sqltypes.NULLTYPE
        elif issubclass(syfe__dtgyo, sqltypes.FLOAT):
            uums__yrdt['precision'] = qrgq__qlk
            uums__yrdt['decimal_return_scale'] = hlr__xpa
        elif issubclass(syfe__dtgyo, sqltypes.Numeric):
            uums__yrdt['precision'] = qrgq__qlk
            uums__yrdt['scale'] = hlr__xpa
        elif issubclass(syfe__dtgyo, (sqltypes.String, sqltypes.BINARY)):
            uums__yrdt['length'] = epx__mlw
        lzqnx__ypy = syfe__dtgyo if isinstance(syfe__dtgyo, sqltypes.NullType
            ) else syfe__dtgyo(**uums__yrdt)
        plifg__qcg = kesjw__moe.get(table_name)
        oxcl__hngeb.append({'name': lyyn__uhmnz, 'type': lzqnx__ypy,
            'nullable': ycddi__ufuz == 'YES', 'default': zixh__rkfhv,
            'autoincrement': cifqj__hoif == 'YES', 'comment': iet__bwnyt if
            iet__bwnyt != '' else None, 'primary_key': lyyn__uhmnz in
            kesjw__moe[table_name]['constrained_columns'] if plifg__qcg else
            False})
    return oxcl__hngeb


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_table_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9ecc8a2425c655836ade4008b1b98a8fd1819f3be43ba77b0fbbfc1f8740e2be':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns = (
    _get_table_columns)
