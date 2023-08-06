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
        cyd__qhhe = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(cyd__qhhe)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ixh__xhv = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, ixh__xhv)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        rcum__sjywe, = args
        sjnar__kqe = signature.return_type
        mukiw__zte = cgutils.create_struct_proxy(sjnar__kqe)(context, builder)
        mukiw__zte.obj = rcum__sjywe
        context.nrt.incref(builder, signature.args[0], rcum__sjywe)
        return mukiw__zte._getvalue()
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
        gcny__tswnr = 'def impl(S_dt):\n'
        gcny__tswnr += '    S = S_dt._obj\n'
        gcny__tswnr += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        gcny__tswnr += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        gcny__tswnr += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        gcny__tswnr += '    numba.parfors.parfor.init_prange()\n'
        gcny__tswnr += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            gcny__tswnr += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            gcny__tswnr += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        gcny__tswnr += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        gcny__tswnr += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        gcny__tswnr += (
            '            bodo.libs.array_kernels.setna(out_arr, i)\n')
        gcny__tswnr += '            continue\n'
        gcny__tswnr += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            gcny__tswnr += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                gcny__tswnr += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            gcny__tswnr += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            vgisr__kzjqk = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            gcny__tswnr += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            gcny__tswnr += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            gcny__tswnr += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(vgisr__kzjqk[field]))
        elif field == 'is_leap_year':
            gcny__tswnr += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            gcny__tswnr += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            vgisr__kzjqk = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            gcny__tswnr += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            gcny__tswnr += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            gcny__tswnr += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(vgisr__kzjqk[field]))
        else:
            gcny__tswnr += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            gcny__tswnr += '        out_arr[i] = ts.' + field + '\n'
        gcny__tswnr += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        nbcxp__tjaio = {}
        exec(gcny__tswnr, {'bodo': bodo, 'numba': numba, 'np': np},
            nbcxp__tjaio)
        impl = nbcxp__tjaio['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        newj__lru = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(newj__lru)


_install_date_fields()


def create_date_method_overload(method):
    hhtu__hhcos = method in ['day_name', 'month_name']
    if hhtu__hhcos:
        gcny__tswnr = 'def overload_method(S_dt, locale=None):\n'
        gcny__tswnr += '    unsupported_args = dict(locale=locale)\n'
        gcny__tswnr += '    arg_defaults = dict(locale=None)\n'
        gcny__tswnr += '    bodo.utils.typing.check_unsupported_args(\n'
        gcny__tswnr += f"        'Series.dt.{method}',\n"
        gcny__tswnr += '        unsupported_args,\n'
        gcny__tswnr += '        arg_defaults,\n'
        gcny__tswnr += "        package_name='pandas',\n"
        gcny__tswnr += "        module_name='Series',\n"
        gcny__tswnr += '    )\n'
    else:
        gcny__tswnr = 'def overload_method(S_dt):\n'
        gcny__tswnr += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    gcny__tswnr += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    gcny__tswnr += '        return\n'
    if hhtu__hhcos:
        gcny__tswnr += '    def impl(S_dt, locale=None):\n'
    else:
        gcny__tswnr += '    def impl(S_dt):\n'
    gcny__tswnr += '        S = S_dt._obj\n'
    gcny__tswnr += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    gcny__tswnr += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    gcny__tswnr += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    gcny__tswnr += '        numba.parfors.parfor.init_prange()\n'
    gcny__tswnr += '        n = len(arr)\n'
    if hhtu__hhcos:
        gcny__tswnr += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        gcny__tswnr += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    gcny__tswnr += (
        '        for i in numba.parfors.parfor.internal_prange(n):\n')
    gcny__tswnr += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    gcny__tswnr += (
        '                bodo.libs.array_kernels.setna(out_arr, i)\n')
    gcny__tswnr += '                continue\n'
    gcny__tswnr += (
        '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n')
    gcny__tswnr += f'            method_val = ts.{method}()\n'
    if hhtu__hhcos:
        gcny__tswnr += '            out_arr[i] = method_val\n'
    else:
        gcny__tswnr += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    gcny__tswnr += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    gcny__tswnr += '    return impl\n'
    nbcxp__tjaio = {}
    exec(gcny__tswnr, {'bodo': bodo, 'numba': numba, 'np': np}, nbcxp__tjaio)
    overload_method = nbcxp__tjaio['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        newj__lru = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            newj__lru)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        feuo__wba = S_dt._obj
        dedql__vyy = bodo.hiframes.pd_series_ext.get_series_data(feuo__wba)
        pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(feuo__wba)
        cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(feuo__wba)
        numba.parfors.parfor.init_prange()
        aigsk__uegxv = len(dedql__vyy)
        qbnrg__qpkhh = (bodo.hiframes.datetime_date_ext.
            alloc_datetime_date_array(aigsk__uegxv))
        for vko__uxocf in numba.parfors.parfor.internal_prange(aigsk__uegxv):
            shr__elv = dedql__vyy[vko__uxocf]
            lbc__jcdvc = bodo.utils.conversion.box_if_dt64(shr__elv)
            qbnrg__qpkhh[vko__uxocf] = datetime.date(lbc__jcdvc.year,
                lbc__jcdvc.month, lbc__jcdvc.day)
        return bodo.hiframes.pd_series_ext.init_series(qbnrg__qpkhh,
            pbqs__oiu, cyd__qhhe)
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
            zhtu__kmj = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            ybw__tzylj = 'convert_numpy_timedelta64_to_pd_timedelta'
            ppn__obhm = 'np.empty(n, np.int64)'
            ypmvr__ztt = attr
        elif attr == 'isocalendar':
            zhtu__kmj = ['year', 'week', 'day']
            ybw__tzylj = 'convert_datetime64_to_timestamp'
            ppn__obhm = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            ypmvr__ztt = attr + '()'
        gcny__tswnr = 'def impl(S_dt):\n'
        gcny__tswnr += '    S = S_dt._obj\n'
        gcny__tswnr += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        gcny__tswnr += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        gcny__tswnr += '    numba.parfors.parfor.init_prange()\n'
        gcny__tswnr += '    n = len(arr)\n'
        for field in zhtu__kmj:
            gcny__tswnr += '    {} = {}\n'.format(field, ppn__obhm)
        gcny__tswnr += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        gcny__tswnr += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in zhtu__kmj:
            gcny__tswnr += (
                '            bodo.libs.array_kernels.setna({}, i)\n'.format
                (field))
        gcny__tswnr += '            continue\n'
        rho__hled = '(' + '[i], '.join(zhtu__kmj) + '[i])'
        gcny__tswnr += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(rho__hled, ybw__tzylj, ypmvr__ztt))
        bkc__oskn = '(' + ', '.join(zhtu__kmj) + ')'
        gcny__tswnr += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(bkc__oskn))
        nbcxp__tjaio = {}
        exec(gcny__tswnr, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(zhtu__kmj))}, nbcxp__tjaio)
        impl = nbcxp__tjaio['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    aplxd__yxb = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, xwy__hsayw in aplxd__yxb:
        newj__lru = create_series_dt_df_output_overload(attr)
        xwy__hsayw(SeriesDatetimePropertiesType, attr, inline='always')(
            newj__lru)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        gcny__tswnr = 'def impl(S_dt):\n'
        gcny__tswnr += '    S = S_dt._obj\n'
        gcny__tswnr += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        gcny__tswnr += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        gcny__tswnr += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        gcny__tswnr += '    numba.parfors.parfor.init_prange()\n'
        gcny__tswnr += '    n = len(A)\n'
        gcny__tswnr += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        gcny__tswnr += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        gcny__tswnr += '        if bodo.libs.array_kernels.isna(A, i):\n'
        gcny__tswnr += '            bodo.libs.array_kernels.setna(B, i)\n'
        gcny__tswnr += '            continue\n'
        gcny__tswnr += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            gcny__tswnr += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            gcny__tswnr += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            gcny__tswnr += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            gcny__tswnr += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        gcny__tswnr += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        nbcxp__tjaio = {}
        exec(gcny__tswnr, {'numba': numba, 'np': np, 'bodo': bodo},
            nbcxp__tjaio)
        impl = nbcxp__tjaio['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        gcny__tswnr = 'def impl(S_dt):\n'
        gcny__tswnr += '    S = S_dt._obj\n'
        gcny__tswnr += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        gcny__tswnr += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        gcny__tswnr += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        gcny__tswnr += '    numba.parfors.parfor.init_prange()\n'
        gcny__tswnr += '    n = len(A)\n'
        if method == 'total_seconds':
            gcny__tswnr += '    B = np.empty(n, np.float64)\n'
        else:
            gcny__tswnr += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        gcny__tswnr += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        gcny__tswnr += '        if bodo.libs.array_kernels.isna(A, i):\n'
        gcny__tswnr += '            bodo.libs.array_kernels.setna(B, i)\n'
        gcny__tswnr += '            continue\n'
        gcny__tswnr += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            gcny__tswnr += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            gcny__tswnr += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            gcny__tswnr += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            gcny__tswnr += '    return B\n'
        nbcxp__tjaio = {}
        exec(gcny__tswnr, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, nbcxp__tjaio)
        impl = nbcxp__tjaio['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        newj__lru = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(newj__lru)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        newj__lru = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            newj__lru)


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
        feuo__wba = S_dt._obj
        untez__gli = bodo.hiframes.pd_series_ext.get_series_data(feuo__wba)
        pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(feuo__wba)
        cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(feuo__wba)
        numba.parfors.parfor.init_prange()
        aigsk__uegxv = len(untez__gli)
        lcdl__xing = bodo.libs.str_arr_ext.pre_alloc_string_array(aigsk__uegxv,
            -1)
        for fctn__qpx in numba.parfors.parfor.internal_prange(aigsk__uegxv):
            if bodo.libs.array_kernels.isna(untez__gli, fctn__qpx):
                bodo.libs.array_kernels.setna(lcdl__xing, fctn__qpx)
                continue
            lcdl__xing[fctn__qpx] = bodo.utils.conversion.box_if_dt64(
                untez__gli[fctn__qpx]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(lcdl__xing,
            pbqs__oiu, cyd__qhhe)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        feuo__wba = S_dt._obj
        hcgiw__sbpq = get_series_data(feuo__wba).tz_convert(tz)
        pbqs__oiu = get_series_index(feuo__wba)
        cyd__qhhe = get_series_name(feuo__wba)
        return init_series(hcgiw__sbpq, pbqs__oiu, cyd__qhhe)
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
        rloff__skuw = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        gdt__xgo = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', rloff__skuw, gdt__xgo,
            package_name='pandas', module_name='Series')
        gcny__tswnr = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        gcny__tswnr += '    S = S_dt._obj\n'
        gcny__tswnr += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        gcny__tswnr += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        gcny__tswnr += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        gcny__tswnr += '    numba.parfors.parfor.init_prange()\n'
        gcny__tswnr += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            gcny__tswnr += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            gcny__tswnr += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        gcny__tswnr += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        gcny__tswnr += '        if bodo.libs.array_kernels.isna(A, i):\n'
        gcny__tswnr += '            bodo.libs.array_kernels.setna(B, i)\n'
        gcny__tswnr += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            qzcl__dvre = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            fyas__qorxl = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            qzcl__dvre = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            fyas__qorxl = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        gcny__tswnr += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            fyas__qorxl, qzcl__dvre, method)
        gcny__tswnr += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        nbcxp__tjaio = {}
        exec(gcny__tswnr, {'numba': numba, 'np': np, 'bodo': bodo},
            nbcxp__tjaio)
        impl = nbcxp__tjaio['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    blerx__ecr = ['ceil', 'floor', 'round']
    for method in blerx__ecr:
        newj__lru = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            newj__lru)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ten__sblp = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                acfu__ebe = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ten__sblp)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ismsi__rvy = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                tbk__trt = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ismsi__rvy)
                aigsk__uegxv = len(acfu__ebe)
                feuo__wba = np.empty(aigsk__uegxv, timedelta64_dtype)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    gdzt__adq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        acfu__ebe[vko__uxocf])
                    kdsy__cgpnz = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(tbk__trt[vko__uxocf]))
                    if gdzt__adq == xxxq__ykmt or kdsy__cgpnz == xxxq__ykmt:
                        eosz__syml = xxxq__ykmt
                    else:
                        eosz__syml = op(gdzt__adq, kdsy__cgpnz)
                    feuo__wba[vko__uxocf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        eosz__syml)
                return bodo.hiframes.pd_series_ext.init_series(feuo__wba,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                tbk__trt = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                aigsk__uegxv = len(dedql__vyy)
                feuo__wba = np.empty(aigsk__uegxv, dt64_dtype)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    dai__izk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dedql__vyy[vko__uxocf])
                    kitn__wnvz = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(tbk__trt[vko__uxocf]))
                    if dai__izk == xxxq__ykmt or kitn__wnvz == xxxq__ykmt:
                        eosz__syml = xxxq__ykmt
                    else:
                        eosz__syml = op(dai__izk, kitn__wnvz)
                    feuo__wba[vko__uxocf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        eosz__syml)
                return bodo.hiframes.pd_series_ext.init_series(feuo__wba,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                tbk__trt = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                aigsk__uegxv = len(dedql__vyy)
                feuo__wba = np.empty(aigsk__uegxv, dt64_dtype)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    dai__izk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dedql__vyy[vko__uxocf])
                    kitn__wnvz = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(tbk__trt[vko__uxocf]))
                    if dai__izk == xxxq__ykmt or kitn__wnvz == xxxq__ykmt:
                        eosz__syml = xxxq__ykmt
                    else:
                        eosz__syml = op(dai__izk, kitn__wnvz)
                    feuo__wba[vko__uxocf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        eosz__syml)
                return bodo.hiframes.pd_series_ext.init_series(feuo__wba,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                aigsk__uegxv = len(dedql__vyy)
                feuo__wba = np.empty(aigsk__uegxv, timedelta64_dtype)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                hfchr__qwtky = rhs.value
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    dai__izk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dedql__vyy[vko__uxocf])
                    if dai__izk == xxxq__ykmt or hfchr__qwtky == xxxq__ykmt:
                        eosz__syml = xxxq__ykmt
                    else:
                        eosz__syml = op(dai__izk, hfchr__qwtky)
                    feuo__wba[vko__uxocf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        eosz__syml)
                return bodo.hiframes.pd_series_ext.init_series(feuo__wba,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                aigsk__uegxv = len(dedql__vyy)
                feuo__wba = np.empty(aigsk__uegxv, timedelta64_dtype)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                hfchr__qwtky = lhs.value
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    dai__izk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dedql__vyy[vko__uxocf])
                    if hfchr__qwtky == xxxq__ykmt or dai__izk == xxxq__ykmt:
                        eosz__syml = xxxq__ykmt
                    else:
                        eosz__syml = op(hfchr__qwtky, dai__izk)
                    feuo__wba[vko__uxocf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        eosz__syml)
                return bodo.hiframes.pd_series_ext.init_series(feuo__wba,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                aigsk__uegxv = len(dedql__vyy)
                feuo__wba = np.empty(aigsk__uegxv, dt64_dtype)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                ldaj__fzca = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                kitn__wnvz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ldaj__fzca))
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    dai__izk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dedql__vyy[vko__uxocf])
                    if dai__izk == xxxq__ykmt or kitn__wnvz == xxxq__ykmt:
                        eosz__syml = xxxq__ykmt
                    else:
                        eosz__syml = op(dai__izk, kitn__wnvz)
                    feuo__wba[vko__uxocf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        eosz__syml)
                return bodo.hiframes.pd_series_ext.init_series(feuo__wba,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                aigsk__uegxv = len(dedql__vyy)
                feuo__wba = np.empty(aigsk__uegxv, dt64_dtype)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                ldaj__fzca = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                kitn__wnvz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ldaj__fzca))
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    dai__izk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dedql__vyy[vko__uxocf])
                    if dai__izk == xxxq__ykmt or kitn__wnvz == xxxq__ykmt:
                        eosz__syml = xxxq__ykmt
                    else:
                        eosz__syml = op(dai__izk, kitn__wnvz)
                    feuo__wba[vko__uxocf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        eosz__syml)
                return bodo.hiframes.pd_series_ext.init_series(feuo__wba,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                aigsk__uegxv = len(dedql__vyy)
                feuo__wba = np.empty(aigsk__uegxv, timedelta64_dtype)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                iwexy__mnon = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                dai__izk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iwexy__mnon)
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    xmvy__bnkp = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dedql__vyy[vko__uxocf]))
                    if xmvy__bnkp == xxxq__ykmt or dai__izk == xxxq__ykmt:
                        eosz__syml = xxxq__ykmt
                    else:
                        eosz__syml = op(xmvy__bnkp, dai__izk)
                    feuo__wba[vko__uxocf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        eosz__syml)
                return bodo.hiframes.pd_series_ext.init_series(feuo__wba,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                aigsk__uegxv = len(dedql__vyy)
                feuo__wba = np.empty(aigsk__uegxv, timedelta64_dtype)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                iwexy__mnon = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                dai__izk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iwexy__mnon)
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    xmvy__bnkp = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dedql__vyy[vko__uxocf]))
                    if dai__izk == xxxq__ykmt or xmvy__bnkp == xxxq__ykmt:
                        eosz__syml = xxxq__ykmt
                    else:
                        eosz__syml = op(dai__izk, xmvy__bnkp)
                    feuo__wba[vko__uxocf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        eosz__syml)
                return bodo.hiframes.pd_series_ext.init_series(feuo__wba,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            izite__lul = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dedql__vyy = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                aigsk__uegxv = len(dedql__vyy)
                feuo__wba = np.empty(aigsk__uegxv, timedelta64_dtype)
                xxxq__ykmt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(izite__lul))
                ldaj__fzca = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                kitn__wnvz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ldaj__fzca))
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    vtl__cdtpo = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(dedql__vyy[vko__uxocf]))
                    if kitn__wnvz == xxxq__ykmt or vtl__cdtpo == xxxq__ykmt:
                        eosz__syml = xxxq__ykmt
                    else:
                        eosz__syml = op(vtl__cdtpo, kitn__wnvz)
                    feuo__wba[vko__uxocf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        eosz__syml)
                return bodo.hiframes.pd_series_ext.init_series(feuo__wba,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            izite__lul = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dedql__vyy = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                aigsk__uegxv = len(dedql__vyy)
                feuo__wba = np.empty(aigsk__uegxv, timedelta64_dtype)
                xxxq__ykmt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(izite__lul))
                ldaj__fzca = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                kitn__wnvz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ldaj__fzca))
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    vtl__cdtpo = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(dedql__vyy[vko__uxocf]))
                    if kitn__wnvz == xxxq__ykmt or vtl__cdtpo == xxxq__ykmt:
                        eosz__syml = xxxq__ykmt
                    else:
                        eosz__syml = op(kitn__wnvz, vtl__cdtpo)
                    feuo__wba[vko__uxocf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        eosz__syml)
                return bodo.hiframes.pd_series_ext.init_series(feuo__wba,
                    pbqs__oiu, cyd__qhhe)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            jdae__daxcr = True
        else:
            jdae__daxcr = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            izite__lul = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dedql__vyy = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                aigsk__uegxv = len(dedql__vyy)
                qbnrg__qpkhh = bodo.libs.bool_arr_ext.alloc_bool_array(
                    aigsk__uegxv)
                xxxq__ykmt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(izite__lul))
                rul__iphv = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                agjy__xwa = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(rul__iphv))
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    vharm__hwjqd = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(dedql__vyy[vko__uxocf]))
                    if vharm__hwjqd == xxxq__ykmt or agjy__xwa == xxxq__ykmt:
                        eosz__syml = jdae__daxcr
                    else:
                        eosz__syml = op(vharm__hwjqd, agjy__xwa)
                    qbnrg__qpkhh[vko__uxocf] = eosz__syml
                return bodo.hiframes.pd_series_ext.init_series(qbnrg__qpkhh,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            izite__lul = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dedql__vyy = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                aigsk__uegxv = len(dedql__vyy)
                qbnrg__qpkhh = bodo.libs.bool_arr_ext.alloc_bool_array(
                    aigsk__uegxv)
                xxxq__ykmt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(izite__lul))
                moqy__mffnr = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                vharm__hwjqd = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(moqy__mffnr))
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    agjy__xwa = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(dedql__vyy[vko__uxocf]))
                    if vharm__hwjqd == xxxq__ykmt or agjy__xwa == xxxq__ykmt:
                        eosz__syml = jdae__daxcr
                    else:
                        eosz__syml = op(vharm__hwjqd, agjy__xwa)
                    qbnrg__qpkhh[vko__uxocf] = eosz__syml
                return bodo.hiframes.pd_series_ext.init_series(qbnrg__qpkhh,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                aigsk__uegxv = len(dedql__vyy)
                qbnrg__qpkhh = bodo.libs.bool_arr_ext.alloc_bool_array(
                    aigsk__uegxv)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    vharm__hwjqd = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dedql__vyy[vko__uxocf]))
                    if vharm__hwjqd == xxxq__ykmt or rhs.value == xxxq__ykmt:
                        eosz__syml = jdae__daxcr
                    else:
                        eosz__syml = op(vharm__hwjqd, rhs.value)
                    qbnrg__qpkhh[vko__uxocf] = eosz__syml
                return bodo.hiframes.pd_series_ext.init_series(qbnrg__qpkhh,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                aigsk__uegxv = len(dedql__vyy)
                qbnrg__qpkhh = bodo.libs.bool_arr_ext.alloc_bool_array(
                    aigsk__uegxv)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    agjy__xwa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dedql__vyy[vko__uxocf])
                    if agjy__xwa == xxxq__ykmt or lhs.value == xxxq__ykmt:
                        eosz__syml = jdae__daxcr
                    else:
                        eosz__syml = op(lhs.value, agjy__xwa)
                    qbnrg__qpkhh[vko__uxocf] = eosz__syml
                return bodo.hiframes.pd_series_ext.init_series(qbnrg__qpkhh,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                aigsk__uegxv = len(dedql__vyy)
                qbnrg__qpkhh = bodo.libs.bool_arr_ext.alloc_bool_array(
                    aigsk__uegxv)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                hxrgv__gbxo = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(rhs))
                xlpso__abv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    hxrgv__gbxo)
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    vharm__hwjqd = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dedql__vyy[vko__uxocf]))
                    if vharm__hwjqd == xxxq__ykmt or xlpso__abv == xxxq__ykmt:
                        eosz__syml = jdae__daxcr
                    else:
                        eosz__syml = op(vharm__hwjqd, xlpso__abv)
                    qbnrg__qpkhh[vko__uxocf] = eosz__syml
                return bodo.hiframes.pd_series_ext.init_series(qbnrg__qpkhh,
                    pbqs__oiu, cyd__qhhe)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            izite__lul = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                sksh__ddjz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                dedql__vyy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    sksh__ddjz)
                pbqs__oiu = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                cyd__qhhe = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                aigsk__uegxv = len(dedql__vyy)
                qbnrg__qpkhh = bodo.libs.bool_arr_ext.alloc_bool_array(
                    aigsk__uegxv)
                xxxq__ykmt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    izite__lul)
                hxrgv__gbxo = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(lhs))
                xlpso__abv = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    hxrgv__gbxo)
                for vko__uxocf in numba.parfors.parfor.internal_prange(
                    aigsk__uegxv):
                    iwexy__mnon = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dedql__vyy[vko__uxocf]))
                    if iwexy__mnon == xxxq__ykmt or xlpso__abv == xxxq__ykmt:
                        eosz__syml = jdae__daxcr
                    else:
                        eosz__syml = op(xlpso__abv, iwexy__mnon)
                    qbnrg__qpkhh[vko__uxocf] = eosz__syml
                return bodo.hiframes.pd_series_ext.init_series(qbnrg__qpkhh,
                    pbqs__oiu, cyd__qhhe)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for fvbs__lnotl in series_dt_unsupported_attrs:
        ikgmx__mikca = 'Series.dt.' + fvbs__lnotl
        overload_attribute(SeriesDatetimePropertiesType, fvbs__lnotl)(
            create_unsupported_overload(ikgmx__mikca))
    for oegr__owcn in series_dt_unsupported_methods:
        ikgmx__mikca = 'Series.dt.' + oegr__owcn
        overload_method(SeriesDatetimePropertiesType, oegr__owcn,
            no_unliteral=True)(create_unsupported_overload(ikgmx__mikca))


_install_series_dt_unsupported()
