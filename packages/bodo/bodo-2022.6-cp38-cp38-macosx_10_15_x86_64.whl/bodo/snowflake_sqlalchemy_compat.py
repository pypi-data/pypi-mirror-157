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
    rycdb__tep = {}
    pqrw__hkht, bnazk__lcraq = self._current_database_schema(connection, **kw)
    rds__bsr = self._denormalize_quote_join(pqrw__hkht, schema)
    try:
        xoz__eqr = self._get_schema_primary_keys(connection, rds__bsr, **kw)
        rfp__pnk = connection.execute(text(
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
    except sa_exc.ProgrammingError as sfsxz__mdh:
        if sfsxz__mdh.orig.errno == 90030:
            return None
        raise
    for table_name, jdp__xbltz, qpr__mgp, avao__rrlr, pythv__ozyp, nhxr__liesx, rvooq__phf, pqdrn__yfgg, mqfr__ttpli, pqj__qot in rfp__pnk:
        table_name = self.normalize_name(table_name)
        jdp__xbltz = self.normalize_name(jdp__xbltz)
        if table_name not in rycdb__tep:
            rycdb__tep[table_name] = list()
        if jdp__xbltz.startswith('sys_clustering_column'):
            continue
        rlo__bcv = self.ischema_names.get(qpr__mgp, None)
        qfpe__fxy = {}
        if rlo__bcv is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(qpr__mgp, jdp__xbltz))
            rlo__bcv = sqltypes.NULLTYPE
        elif issubclass(rlo__bcv, sqltypes.FLOAT):
            qfpe__fxy['precision'] = pythv__ozyp
            qfpe__fxy['decimal_return_scale'] = nhxr__liesx
        elif issubclass(rlo__bcv, sqltypes.Numeric):
            qfpe__fxy['precision'] = pythv__ozyp
            qfpe__fxy['scale'] = nhxr__liesx
        elif issubclass(rlo__bcv, (sqltypes.String, sqltypes.BINARY)):
            qfpe__fxy['length'] = avao__rrlr
        gur__ifd = rlo__bcv if isinstance(rlo__bcv, sqltypes.NullType
            ) else rlo__bcv(**qfpe__fxy)
        nzlit__iqf = xoz__eqr.get(table_name)
        rycdb__tep[table_name].append({'name': jdp__xbltz, 'type': gur__ifd,
            'nullable': rvooq__phf == 'YES', 'default': pqdrn__yfgg,
            'autoincrement': mqfr__ttpli == 'YES', 'comment': pqj__qot,
            'primary_key': jdp__xbltz in xoz__eqr[table_name][
            'constrained_columns'] if nzlit__iqf else False})
    return rycdb__tep


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
    rycdb__tep = []
    pqrw__hkht, bnazk__lcraq = self._current_database_schema(connection, **kw)
    rds__bsr = self._denormalize_quote_join(pqrw__hkht, schema)
    xoz__eqr = self._get_schema_primary_keys(connection, rds__bsr, **kw)
    rfp__pnk = connection.execute(text(
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
    for table_name, jdp__xbltz, qpr__mgp, avao__rrlr, pythv__ozyp, nhxr__liesx, rvooq__phf, pqdrn__yfgg, mqfr__ttpli, pqj__qot in rfp__pnk:
        table_name = self.normalize_name(table_name)
        jdp__xbltz = self.normalize_name(jdp__xbltz)
        if jdp__xbltz.startswith('sys_clustering_column'):
            continue
        rlo__bcv = self.ischema_names.get(qpr__mgp, None)
        qfpe__fxy = {}
        if rlo__bcv is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(qpr__mgp, jdp__xbltz))
            rlo__bcv = sqltypes.NULLTYPE
        elif issubclass(rlo__bcv, sqltypes.FLOAT):
            qfpe__fxy['precision'] = pythv__ozyp
            qfpe__fxy['decimal_return_scale'] = nhxr__liesx
        elif issubclass(rlo__bcv, sqltypes.Numeric):
            qfpe__fxy['precision'] = pythv__ozyp
            qfpe__fxy['scale'] = nhxr__liesx
        elif issubclass(rlo__bcv, (sqltypes.String, sqltypes.BINARY)):
            qfpe__fxy['length'] = avao__rrlr
        gur__ifd = rlo__bcv if isinstance(rlo__bcv, sqltypes.NullType
            ) else rlo__bcv(**qfpe__fxy)
        nzlit__iqf = xoz__eqr.get(table_name)
        rycdb__tep.append({'name': jdp__xbltz, 'type': gur__ifd, 'nullable':
            rvooq__phf == 'YES', 'default': pqdrn__yfgg, 'autoincrement': 
            mqfr__ttpli == 'YES', 'comment': pqj__qot if pqj__qot != '' else
            None, 'primary_key': jdp__xbltz in xoz__eqr[table_name][
            'constrained_columns'] if nzlit__iqf else False})
    return rycdb__tep


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
