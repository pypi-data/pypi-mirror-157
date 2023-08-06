"""
Support for Series.dt attributes and methods
"""
import datetime
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_series_ext import SeriesType, get_series_data, get_series_index, get_series_name, init_series
from bodo.libs.pd_datetime_arr_ext import PandasDatetimeTZDtype
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, raise_bodo_error
dt64_dtype = np.dtype('datetime64[ns]')
timedelta64_dtype = np.dtype('timedelta64[ns]')


class SeriesDatetimePropertiesType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        fqva__zeil = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(fqva__zeil)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ouqdh__lvu = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, ouqdh__lvu)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        mqtuk__fywyk, = args
        bqm__ouo = signature.return_type
        tftmj__joaq = cgutils.create_struct_proxy(bqm__ouo)(context, builder)
        tftmj__joaq.obj = mqtuk__fywyk
        context.nrt.incref(builder, signature.args[0], mqtuk__fywyk)
        return tftmj__joaq._getvalue()
    return SeriesDatetimePropertiesType(obj)(obj), codegen


@overload_attribute(SeriesType, 'dt')
def overload_series_dt(s):
    if not (bodo.hiframes.pd_series_ext.is_dt64_series_typ(s) or bodo.
        hiframes.pd_series_ext.is_timedelta64_series_typ(s)):
        raise_bodo_error('Can only use .dt accessor with datetimelike values.')
    return lambda s: bodo.hiframes.series_dt_impl.init_series_dt_properties(s)


def create_date_field_overload(field):

    def overload_field(S_dt):
        if S_dt.stype.dtype != types.NPDatetime('ns') and not isinstance(S_dt
            .stype.dtype, PandasDatetimeTZDtype):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{field}')
        spav__vnbl = 'def impl(S_dt):\n'
        spav__vnbl += '    S = S_dt._obj\n'
        spav__vnbl += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        spav__vnbl += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        spav__vnbl += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        spav__vnbl += '    numba.parfors.parfor.init_prange()\n'
        spav__vnbl += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            spav__vnbl += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            spav__vnbl += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        spav__vnbl += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        spav__vnbl += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        spav__vnbl += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        spav__vnbl += '            continue\n'
        spav__vnbl += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            spav__vnbl += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                spav__vnbl += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            spav__vnbl += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            tueb__vybnm = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            spav__vnbl += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            spav__vnbl += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            spav__vnbl += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(tueb__vybnm[field]))
        elif field == 'is_leap_year':
            spav__vnbl += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            spav__vnbl += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            tueb__vybnm = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            spav__vnbl += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            spav__vnbl += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            spav__vnbl += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(tueb__vybnm[field]))
        else:
            spav__vnbl += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            spav__vnbl += '        out_arr[i] = ts.' + field + '\n'
        spav__vnbl += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        oxthp__kpee = {}
        exec(spav__vnbl, {'bodo': bodo, 'numba': numba, 'np': np}, oxthp__kpee)
        impl = oxthp__kpee['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        olr__zxjld = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(olr__zxjld)


_install_date_fields()


def create_date_method_overload(method):
    nxbgl__gfg = method in ['day_name', 'month_name']
    if nxbgl__gfg:
        spav__vnbl = 'def overload_method(S_dt, locale=None):\n'
        spav__vnbl += '    unsupported_args = dict(locale=locale)\n'
        spav__vnbl += '    arg_defaults = dict(locale=None)\n'
        spav__vnbl += '    bodo.utils.typing.check_unsupported_args(\n'
        spav__vnbl += f"        'Series.dt.{method}',\n"
        spav__vnbl += '        unsupported_args,\n'
        spav__vnbl += '        arg_defaults,\n'
        spav__vnbl += "        package_name='pandas',\n"
        spav__vnbl += "        module_name='Series',\n"
        spav__vnbl += '    )\n'
    else:
        spav__vnbl = 'def overload_method(S_dt):\n'
        spav__vnbl += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    spav__vnbl += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    spav__vnbl += '        return\n'
    if nxbgl__gfg:
        spav__vnbl += '    def impl(S_dt, locale=None):\n'
    else:
        spav__vnbl += '    def impl(S_dt):\n'
    spav__vnbl += '        S = S_dt._obj\n'
    spav__vnbl += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    spav__vnbl += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    spav__vnbl += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    spav__vnbl += '        numba.parfors.parfor.init_prange()\n'
    spav__vnbl += '        n = len(arr)\n'
    if nxbgl__gfg:
        spav__vnbl += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        spav__vnbl += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    spav__vnbl += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    spav__vnbl += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    spav__vnbl += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    spav__vnbl += '                continue\n'
    spav__vnbl += (
        '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n')
    spav__vnbl += f'            method_val = ts.{method}()\n'
    if nxbgl__gfg:
        spav__vnbl += '            out_arr[i] = method_val\n'
    else:
        spav__vnbl += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    spav__vnbl += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    spav__vnbl += '    return impl\n'
    oxthp__kpee = {}
    exec(spav__vnbl, {'bodo': bodo, 'numba': numba, 'np': np}, oxthp__kpee)
    overload_method = oxthp__kpee['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        olr__zxjld = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            olr__zxjld)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        bajri__civk = S_dt._obj
        qnwel__rlioa = bodo.hiframes.pd_series_ext.get_series_data(bajri__civk)
        lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(bajri__civk)
        fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(bajri__civk)
        numba.parfors.parfor.init_prange()
        clzta__apsrw = len(qnwel__rlioa)
        mzobo__ammme = (bodo.hiframes.datetime_date_ext.
            alloc_datetime_date_array(clzta__apsrw))
        for fbk__zgu in numba.parfors.parfor.internal_prange(clzta__apsrw):
            yzsjr__nvd = qnwel__rlioa[fbk__zgu]
            grw__mvwnv = bodo.utils.conversion.box_if_dt64(yzsjr__nvd)
            mzobo__ammme[fbk__zgu] = datetime.date(grw__mvwnv.year,
                grw__mvwnv.month, grw__mvwnv.day)
        return bodo.hiframes.pd_series_ext.init_series(mzobo__ammme,
            lstm__ptm, fqva__zeil)
    return impl


def create_series_dt_df_output_overload(attr):

    def series_dt_df_output_overload(S_dt):
        if not (attr == 'components' and S_dt.stype.dtype == types.
            NPTimedelta('ns') or attr == 'isocalendar' and (S_dt.stype.
            dtype == types.NPDatetime('ns') or isinstance(S_dt.stype.dtype,
            PandasDatetimeTZDtype))):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{attr}')
        if attr == 'components':
            fflz__wsosn = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            dmxsp__muxf = 'convert_numpy_timedelta64_to_pd_timedelta'
            zxj__osh = 'np.empty(n, np.int64)'
            vtf__kejhk = attr
        elif attr == 'isocalendar':
            fflz__wsosn = ['year', 'week', 'day']
            dmxsp__muxf = 'convert_datetime64_to_timestamp'
            zxj__osh = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            vtf__kejhk = attr + '()'
        spav__vnbl = 'def impl(S_dt):\n'
        spav__vnbl += '    S = S_dt._obj\n'
        spav__vnbl += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        spav__vnbl += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        spav__vnbl += '    numba.parfors.parfor.init_prange()\n'
        spav__vnbl += '    n = len(arr)\n'
        for field in fflz__wsosn:
            spav__vnbl += '    {} = {}\n'.format(field, zxj__osh)
        spav__vnbl += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        spav__vnbl += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in fflz__wsosn:
            spav__vnbl += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        spav__vnbl += '            continue\n'
        xcwm__rqlh = '(' + '[i], '.join(fflz__wsosn) + '[i])'
        spav__vnbl += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(xcwm__rqlh, dmxsp__muxf, vtf__kejhk))
        jmq__jelz = '(' + ', '.join(fflz__wsosn) + ')'
        spav__vnbl += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(jmq__jelz))
        oxthp__kpee = {}
        exec(spav__vnbl, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(fflz__wsosn))}, oxthp__kpee)
        impl = oxthp__kpee['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    ztvw__opxi = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, ywsl__czz in ztvw__opxi:
        olr__zxjld = create_series_dt_df_output_overload(attr)
        ywsl__czz(SeriesDatetimePropertiesType, attr, inline='always')(
            olr__zxjld)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        spav__vnbl = 'def impl(S_dt):\n'
        spav__vnbl += '    S = S_dt._obj\n'
        spav__vnbl += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        spav__vnbl += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        spav__vnbl += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        spav__vnbl += '    numba.parfors.parfor.init_prange()\n'
        spav__vnbl += '    n = len(A)\n'
        spav__vnbl += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        spav__vnbl += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        spav__vnbl += '        if bodo.libs.array_kernels.isna(A, i):\n'
        spav__vnbl += '            bodo.libs.array_kernels.setna(B, i)\n'
        spav__vnbl += '            continue\n'
        spav__vnbl += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            spav__vnbl += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            spav__vnbl += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            spav__vnbl += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            spav__vnbl += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        spav__vnbl += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        oxthp__kpee = {}
        exec(spav__vnbl, {'numba': numba, 'np': np, 'bodo': bodo}, oxthp__kpee)
        impl = oxthp__kpee['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        spav__vnbl = 'def impl(S_dt):\n'
        spav__vnbl += '    S = S_dt._obj\n'
        spav__vnbl += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        spav__vnbl += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        spav__vnbl += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        spav__vnbl += '    numba.parfors.parfor.init_prange()\n'
        spav__vnbl += '    n = len(A)\n'
        if method == 'total_seconds':
            spav__vnbl += '    B = np.empty(n, np.float64)\n'
        else:
            spav__vnbl += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        spav__vnbl += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        spav__vnbl += '        if bodo.libs.array_kernels.isna(A, i):\n'
        spav__vnbl += '            bodo.libs.array_kernels.setna(B, i)\n'
        spav__vnbl += '            continue\n'
        spav__vnbl += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            spav__vnbl += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            spav__vnbl += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            spav__vnbl += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            spav__vnbl += '    return B\n'
        oxthp__kpee = {}
        exec(spav__vnbl, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, oxthp__kpee)
        impl = oxthp__kpee['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        olr__zxjld = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(olr__zxjld)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        olr__zxjld = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            olr__zxjld)


_install_S_dt_timedelta_methods()


@overload_method(SeriesDatetimePropertiesType, 'strftime', inline='always',
    no_unliteral=True)
def dt_strftime(S_dt, date_format):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return
    if types.unliteral(date_format) != types.unicode_type:
        raise BodoError(
            "Series.str.strftime(): 'date_format' argument must be a string")

    def impl(S_dt, date_format):
        bajri__civk = S_dt._obj
        rii__dlb = bodo.hiframes.pd_series_ext.get_series_data(bajri__civk)
        lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(bajri__civk)
        fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(bajri__civk)
        numba.parfors.parfor.init_prange()
        clzta__apsrw = len(rii__dlb)
        ccrf__nagr = bodo.libs.str_arr_ext.pre_alloc_string_array(clzta__apsrw,
            -1)
        for ujy__brp in numba.parfors.parfor.internal_prange(clzta__apsrw):
            if bodo.libs.array_kernels.isna(rii__dlb, ujy__brp):
                bodo.libs.array_kernels.setna(ccrf__nagr, ujy__brp)
                continue
            ccrf__nagr[ujy__brp] = bodo.utils.conversion.box_if_dt64(rii__dlb
                [ujy__brp]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(ccrf__nagr,
            lstm__ptm, fqva__zeil)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        bajri__civk = S_dt._obj
        gpu__mdrs = get_series_data(bajri__civk).tz_convert(tz)
        lstm__ptm = get_series_index(bajri__civk)
        fqva__zeil = get_series_name(bajri__civk)
        return init_series(gpu__mdrs, lstm__ptm, fqva__zeil)
    return impl


def create_timedelta_freq_overload(method):

    def freq_overload(S_dt, freq, ambiguous='raise', nonexistent='raise'):
        if S_dt.stype.dtype != types.NPTimedelta('ns'
            ) and S_dt.stype.dtype != types.NPDatetime('ns'
            ) and not isinstance(S_dt.stype.dtype, bodo.libs.
            pd_datetime_arr_ext.PandasDatetimeTZDtype):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{method}()')
        zbose__iynl = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        bwrr__oaghb = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', zbose__iynl,
            bwrr__oaghb, package_name='pandas', module_name='Series')
        spav__vnbl = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        spav__vnbl += '    S = S_dt._obj\n'
        spav__vnbl += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        spav__vnbl += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        spav__vnbl += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        spav__vnbl += '    numba.parfors.parfor.init_prange()\n'
        spav__vnbl += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            spav__vnbl += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            spav__vnbl += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        spav__vnbl += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        spav__vnbl += '        if bodo.libs.array_kernels.isna(A, i):\n'
        spav__vnbl += '            bodo.libs.array_kernels.setna(B, i)\n'
        spav__vnbl += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            dadx__eazjg = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            ays__nuiy = 'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64'
        else:
            dadx__eazjg = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            ays__nuiy = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        spav__vnbl += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            ays__nuiy, dadx__eazjg, method)
        spav__vnbl += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        oxthp__kpee = {}
        exec(spav__vnbl, {'numba': numba, 'np': np, 'bodo': bodo}, oxthp__kpee)
        impl = oxthp__kpee['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    ehh__lagg = ['ceil', 'floor', 'round']
    for method in ehh__lagg:
        olr__zxjld = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            olr__zxjld)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                vcqho__nsmoh = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                wtd__qwma = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    vcqho__nsmoh)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                xbzoj__sqai = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                aslm__bojrg = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    xbzoj__sqai)
                clzta__apsrw = len(wtd__qwma)
                bajri__civk = np.empty(clzta__apsrw, timedelta64_dtype)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    yfeyj__evln = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(wtd__qwma[fbk__zgu]))
                    fpn__urzm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        aslm__bojrg[fbk__zgu])
                    if (yfeyj__evln == iehtt__ldchj or fpn__urzm ==
                        iehtt__ldchj):
                        ustqy__mutv = iehtt__ldchj
                    else:
                        ustqy__mutv = op(yfeyj__evln, fpn__urzm)
                    bajri__civk[fbk__zgu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ustqy__mutv)
                return bodo.hiframes.pd_series_ext.init_series(bajri__civk,
                    lstm__ptm, fqva__zeil)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                aslm__bojrg = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                clzta__apsrw = len(qnwel__rlioa)
                bajri__civk = np.empty(clzta__apsrw, dt64_dtype)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    cfff__ctf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qnwel__rlioa[fbk__zgu])
                    rin__mrt = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(aslm__bojrg[fbk__zgu]))
                    if cfff__ctf == iehtt__ldchj or rin__mrt == iehtt__ldchj:
                        ustqy__mutv = iehtt__ldchj
                    else:
                        ustqy__mutv = op(cfff__ctf, rin__mrt)
                    bajri__civk[fbk__zgu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        ustqy__mutv)
                return bodo.hiframes.pd_series_ext.init_series(bajri__civk,
                    lstm__ptm, fqva__zeil)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                aslm__bojrg = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                clzta__apsrw = len(qnwel__rlioa)
                bajri__civk = np.empty(clzta__apsrw, dt64_dtype)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    cfff__ctf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qnwel__rlioa[fbk__zgu])
                    rin__mrt = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(aslm__bojrg[fbk__zgu]))
                    if cfff__ctf == iehtt__ldchj or rin__mrt == iehtt__ldchj:
                        ustqy__mutv = iehtt__ldchj
                    else:
                        ustqy__mutv = op(cfff__ctf, rin__mrt)
                    bajri__civk[fbk__zgu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        ustqy__mutv)
                return bodo.hiframes.pd_series_ext.init_series(bajri__civk,
                    lstm__ptm, fqva__zeil)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                clzta__apsrw = len(qnwel__rlioa)
                bajri__civk = np.empty(clzta__apsrw, timedelta64_dtype)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                bvho__dmqj = rhs.value
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    cfff__ctf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qnwel__rlioa[fbk__zgu])
                    if cfff__ctf == iehtt__ldchj or bvho__dmqj == iehtt__ldchj:
                        ustqy__mutv = iehtt__ldchj
                    else:
                        ustqy__mutv = op(cfff__ctf, bvho__dmqj)
                    bajri__civk[fbk__zgu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ustqy__mutv)
                return bodo.hiframes.pd_series_ext.init_series(bajri__civk,
                    lstm__ptm, fqva__zeil)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                clzta__apsrw = len(qnwel__rlioa)
                bajri__civk = np.empty(clzta__apsrw, timedelta64_dtype)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                bvho__dmqj = lhs.value
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    cfff__ctf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qnwel__rlioa[fbk__zgu])
                    if bvho__dmqj == iehtt__ldchj or cfff__ctf == iehtt__ldchj:
                        ustqy__mutv = iehtt__ldchj
                    else:
                        ustqy__mutv = op(bvho__dmqj, cfff__ctf)
                    bajri__civk[fbk__zgu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ustqy__mutv)
                return bodo.hiframes.pd_series_ext.init_series(bajri__civk,
                    lstm__ptm, fqva__zeil)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                clzta__apsrw = len(qnwel__rlioa)
                bajri__civk = np.empty(clzta__apsrw, dt64_dtype)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                dxiev__ioei = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                rin__mrt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(dxiev__ioei))
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    cfff__ctf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qnwel__rlioa[fbk__zgu])
                    if cfff__ctf == iehtt__ldchj or rin__mrt == iehtt__ldchj:
                        ustqy__mutv = iehtt__ldchj
                    else:
                        ustqy__mutv = op(cfff__ctf, rin__mrt)
                    bajri__civk[fbk__zgu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        ustqy__mutv)
                return bodo.hiframes.pd_series_ext.init_series(bajri__civk,
                    lstm__ptm, fqva__zeil)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                clzta__apsrw = len(qnwel__rlioa)
                bajri__civk = np.empty(clzta__apsrw, dt64_dtype)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                dxiev__ioei = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                rin__mrt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(dxiev__ioei))
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    cfff__ctf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qnwel__rlioa[fbk__zgu])
                    if cfff__ctf == iehtt__ldchj or rin__mrt == iehtt__ldchj:
                        ustqy__mutv = iehtt__ldchj
                    else:
                        ustqy__mutv = op(cfff__ctf, rin__mrt)
                    bajri__civk[fbk__zgu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        ustqy__mutv)
                return bodo.hiframes.pd_series_ext.init_series(bajri__civk,
                    lstm__ptm, fqva__zeil)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                clzta__apsrw = len(qnwel__rlioa)
                bajri__civk = np.empty(clzta__apsrw, timedelta64_dtype)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                amw__ahr = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                cfff__ctf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    amw__ahr)
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    poqw__jirn = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(qnwel__rlioa[fbk__zgu]))
                    if poqw__jirn == iehtt__ldchj or cfff__ctf == iehtt__ldchj:
                        ustqy__mutv = iehtt__ldchj
                    else:
                        ustqy__mutv = op(poqw__jirn, cfff__ctf)
                    bajri__civk[fbk__zgu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ustqy__mutv)
                return bodo.hiframes.pd_series_ext.init_series(bajri__civk,
                    lstm__ptm, fqva__zeil)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                clzta__apsrw = len(qnwel__rlioa)
                bajri__civk = np.empty(clzta__apsrw, timedelta64_dtype)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                amw__ahr = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                cfff__ctf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    amw__ahr)
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    poqw__jirn = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(qnwel__rlioa[fbk__zgu]))
                    if cfff__ctf == iehtt__ldchj or poqw__jirn == iehtt__ldchj:
                        ustqy__mutv = iehtt__ldchj
                    else:
                        ustqy__mutv = op(cfff__ctf, poqw__jirn)
                    bajri__civk[fbk__zgu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ustqy__mutv)
                return bodo.hiframes.pd_series_ext.init_series(bajri__civk,
                    lstm__ptm, fqva__zeil)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            jxcko__rvl = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                qnwel__rlioa = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                clzta__apsrw = len(qnwel__rlioa)
                bajri__civk = np.empty(clzta__apsrw, timedelta64_dtype)
                iehtt__ldchj = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jxcko__rvl))
                dxiev__ioei = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                rin__mrt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(dxiev__ioei))
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    qzoq__ievnn = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(qnwel__rlioa[fbk__zgu]))
                    if rin__mrt == iehtt__ldchj or qzoq__ievnn == iehtt__ldchj:
                        ustqy__mutv = iehtt__ldchj
                    else:
                        ustqy__mutv = op(qzoq__ievnn, rin__mrt)
                    bajri__civk[fbk__zgu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ustqy__mutv)
                return bodo.hiframes.pd_series_ext.init_series(bajri__civk,
                    lstm__ptm, fqva__zeil)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            jxcko__rvl = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                qnwel__rlioa = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                clzta__apsrw = len(qnwel__rlioa)
                bajri__civk = np.empty(clzta__apsrw, timedelta64_dtype)
                iehtt__ldchj = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jxcko__rvl))
                dxiev__ioei = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                rin__mrt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(dxiev__ioei))
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    qzoq__ievnn = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(qnwel__rlioa[fbk__zgu]))
                    if rin__mrt == iehtt__ldchj or qzoq__ievnn == iehtt__ldchj:
                        ustqy__mutv = iehtt__ldchj
                    else:
                        ustqy__mutv = op(rin__mrt, qzoq__ievnn)
                    bajri__civk[fbk__zgu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ustqy__mutv)
                return bodo.hiframes.pd_series_ext.init_series(bajri__civk,
                    lstm__ptm, fqva__zeil)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            nrs__pslps = True
        else:
            nrs__pslps = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            jxcko__rvl = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                qnwel__rlioa = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                clzta__apsrw = len(qnwel__rlioa)
                mzobo__ammme = bodo.libs.bool_arr_ext.alloc_bool_array(
                    clzta__apsrw)
                iehtt__ldchj = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jxcko__rvl))
                atru__ssfc = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                shdz__mgf = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(atru__ssfc))
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    luoa__xwewj = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(qnwel__rlioa[fbk__zgu]))
                    if (luoa__xwewj == iehtt__ldchj or shdz__mgf ==
                        iehtt__ldchj):
                        ustqy__mutv = nrs__pslps
                    else:
                        ustqy__mutv = op(luoa__xwewj, shdz__mgf)
                    mzobo__ammme[fbk__zgu] = ustqy__mutv
                return bodo.hiframes.pd_series_ext.init_series(mzobo__ammme,
                    lstm__ptm, fqva__zeil)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            jxcko__rvl = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                qnwel__rlioa = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                clzta__apsrw = len(qnwel__rlioa)
                mzobo__ammme = bodo.libs.bool_arr_ext.alloc_bool_array(
                    clzta__apsrw)
                iehtt__ldchj = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jxcko__rvl))
                bzwy__hxj = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                luoa__xwewj = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(bzwy__hxj))
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    shdz__mgf = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(qnwel__rlioa[fbk__zgu]))
                    if (luoa__xwewj == iehtt__ldchj or shdz__mgf ==
                        iehtt__ldchj):
                        ustqy__mutv = nrs__pslps
                    else:
                        ustqy__mutv = op(luoa__xwewj, shdz__mgf)
                    mzobo__ammme[fbk__zgu] = ustqy__mutv
                return bodo.hiframes.pd_series_ext.init_series(mzobo__ammme,
                    lstm__ptm, fqva__zeil)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                clzta__apsrw = len(qnwel__rlioa)
                mzobo__ammme = bodo.libs.bool_arr_ext.alloc_bool_array(
                    clzta__apsrw)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    luoa__xwewj = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(qnwel__rlioa[fbk__zgu]))
                    if (luoa__xwewj == iehtt__ldchj or rhs.value ==
                        iehtt__ldchj):
                        ustqy__mutv = nrs__pslps
                    else:
                        ustqy__mutv = op(luoa__xwewj, rhs.value)
                    mzobo__ammme[fbk__zgu] = ustqy__mutv
                return bodo.hiframes.pd_series_ext.init_series(mzobo__ammme,
                    lstm__ptm, fqva__zeil)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                clzta__apsrw = len(qnwel__rlioa)
                mzobo__ammme = bodo.libs.bool_arr_ext.alloc_bool_array(
                    clzta__apsrw)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    shdz__mgf = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qnwel__rlioa[fbk__zgu])
                    if shdz__mgf == iehtt__ldchj or lhs.value == iehtt__ldchj:
                        ustqy__mutv = nrs__pslps
                    else:
                        ustqy__mutv = op(lhs.value, shdz__mgf)
                    mzobo__ammme[fbk__zgu] = ustqy__mutv
                return bodo.hiframes.pd_series_ext.init_series(mzobo__ammme,
                    lstm__ptm, fqva__zeil)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                clzta__apsrw = len(qnwel__rlioa)
                mzobo__ammme = bodo.libs.bool_arr_ext.alloc_bool_array(
                    clzta__apsrw)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                dyf__wwbxq = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                bfeez__plm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    dyf__wwbxq)
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    luoa__xwewj = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(qnwel__rlioa[fbk__zgu]))
                    if (luoa__xwewj == iehtt__ldchj or bfeez__plm ==
                        iehtt__ldchj):
                        ustqy__mutv = nrs__pslps
                    else:
                        ustqy__mutv = op(luoa__xwewj, bfeez__plm)
                    mzobo__ammme[fbk__zgu] = ustqy__mutv
                return bodo.hiframes.pd_series_ext.init_series(mzobo__ammme,
                    lstm__ptm, fqva__zeil)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            jxcko__rvl = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                lmh__qaawb = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qnwel__rlioa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lmh__qaawb)
                lstm__ptm = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                fqva__zeil = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                clzta__apsrw = len(qnwel__rlioa)
                mzobo__ammme = bodo.libs.bool_arr_ext.alloc_bool_array(
                    clzta__apsrw)
                iehtt__ldchj = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    jxcko__rvl)
                dyf__wwbxq = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                bfeez__plm = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    dyf__wwbxq)
                for fbk__zgu in numba.parfors.parfor.internal_prange(
                    clzta__apsrw):
                    amw__ahr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qnwel__rlioa[fbk__zgu])
                    if amw__ahr == iehtt__ldchj or bfeez__plm == iehtt__ldchj:
                        ustqy__mutv = nrs__pslps
                    else:
                        ustqy__mutv = op(bfeez__plm, amw__ahr)
                    mzobo__ammme[fbk__zgu] = ustqy__mutv
                return bodo.hiframes.pd_series_ext.init_series(mzobo__ammme,
                    lstm__ptm, fqva__zeil)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for hzbp__pudot in series_dt_unsupported_attrs:
        mhp__vic = 'Series.dt.' + hzbp__pudot
        overload_attribute(SeriesDatetimePropertiesType, hzbp__pudot)(
            create_unsupported_overload(mhp__vic))
    for chu__qjrg in series_dt_unsupported_methods:
        mhp__vic = 'Series.dt.' + chu__qjrg
        overload_method(SeriesDatetimePropertiesType, chu__qjrg,
            no_unliteral=True)(create_unsupported_overload(mhp__vic))


_install_series_dt_unsupported()
