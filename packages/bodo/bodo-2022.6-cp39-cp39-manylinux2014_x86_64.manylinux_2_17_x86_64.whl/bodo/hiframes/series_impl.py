"""
Implementation of Series attributes and methods using overload.
"""
import operator
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_builtin, overload, overload_attribute, overload_method, register_jitable
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.datetime_timedelta_ext import PDTimeDeltaType, datetime_timedelta_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.pd_offsets_ext import is_offsets_type
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType, if_series_to_array_type, is_series_type
from bodo.hiframes.pd_timestamp_ext import PandasTimestampType, pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType
from bodo.libs.str_ext import string_type
from bodo.utils.transform import is_var_size_item_array_type
from bodo.utils.typing import BodoError, ColNamesMetaType, can_replace, check_unsupported_args, dtype_to_array_type, element_type, get_common_scalar_dtype, get_index_names, get_literal_value, get_overload_const_bytes, get_overload_const_int, get_overload_const_str, is_common_scalar_dtype, is_iterable_type, is_literal_type, is_nullable_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_bytes, is_overload_constant_int, is_overload_constant_nan, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, is_str_arr_type, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array


@overload_attribute(HeterogeneousSeriesType, 'index', inline='always')
@overload_attribute(SeriesType, 'index', inline='always')
def overload_series_index(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_index(s)


@overload_attribute(HeterogeneousSeriesType, 'values', inline='always')
@overload_attribute(SeriesType, 'values', inline='always')
def overload_series_values(s):
    if isinstance(s.data, bodo.DatetimeArrayType):

        def impl(s):
            ccjvm__osjj = bodo.hiframes.pd_series_ext.get_series_data(s)
            giisc__emq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                ccjvm__osjj)
            return giisc__emq
        return impl
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s)


@overload_attribute(SeriesType, 'dtype', inline='always')
def overload_series_dtype(s):
    if s.dtype == bodo.string_type:
        raise BodoError('Series.dtype not supported for string Series yet')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(s, 'Series.dtype'
        )
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s).dtype


@overload_attribute(HeterogeneousSeriesType, 'shape')
@overload_attribute(SeriesType, 'shape')
def overload_series_shape(s):
    return lambda s: (len(bodo.hiframes.pd_series_ext.get_series_data(s)),)


@overload_attribute(HeterogeneousSeriesType, 'ndim', inline='always')
@overload_attribute(SeriesType, 'ndim', inline='always')
def overload_series_ndim(s):
    return lambda s: 1


@overload_attribute(HeterogeneousSeriesType, 'size')
@overload_attribute(SeriesType, 'size')
def overload_series_size(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s))


@overload_attribute(HeterogeneousSeriesType, 'T', inline='always')
@overload_attribute(SeriesType, 'T', inline='always')
def overload_series_T(s):
    return lambda s: s


@overload_attribute(SeriesType, 'hasnans', inline='always')
def overload_series_hasnans(s):
    return lambda s: s.isna().sum() != 0


@overload_attribute(HeterogeneousSeriesType, 'empty')
@overload_attribute(SeriesType, 'empty')
def overload_series_empty(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s)) == 0


@overload_attribute(SeriesType, 'dtypes', inline='always')
def overload_series_dtypes(s):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(s,
        'Series.dtypes')
    return lambda s: s.dtype


@overload_attribute(HeterogeneousSeriesType, 'name', inline='always')
@overload_attribute(SeriesType, 'name', inline='always')
def overload_series_name(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_name(s)


@overload(len, no_unliteral=True)
def overload_series_len(S):
    if isinstance(S, (SeriesType, HeterogeneousSeriesType)):
        return lambda S: len(bodo.hiframes.pd_series_ext.get_series_data(S))


@overload_method(SeriesType, 'copy', inline='always', no_unliteral=True)
def overload_series_copy(S, deep=True):
    if is_overload_true(deep):

        def impl1(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr.copy(),
                index, name)
        return impl1
    if is_overload_false(deep):

        def impl2(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl2

    def impl(S, deep=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        if deep:
            arr = arr.copy()
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'to_list', no_unliteral=True)
@overload_method(SeriesType, 'tolist', no_unliteral=True)
def overload_series_to_list(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.tolist()')
    if isinstance(S.dtype, types.Float):

        def impl_float(S):
            zpvrp__iwr = list()
            for epsx__nqlia in range(len(S)):
                zpvrp__iwr.append(S.iat[epsx__nqlia])
            return zpvrp__iwr
        return impl_float

    def impl(S):
        zpvrp__iwr = list()
        for epsx__nqlia in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, epsx__nqlia):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            zpvrp__iwr.append(S.iat[epsx__nqlia])
        return zpvrp__iwr
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    dez__zieuq = dict(dtype=dtype, copy=copy, na_value=na_value)
    vcpmw__vaq = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    dez__zieuq = dict(name=name, inplace=inplace)
    vcpmw__vaq = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not bodo.hiframes.dataframe_impl._is_all_levels(S, level):
        raise_bodo_error(
            'Series.reset_index(): only dropping all index levels supported')
    if not is_overload_constant_bool(drop):
        raise_bodo_error(
            "Series.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if is_overload_true(drop):

        def impl_drop(S, level=None, drop=False, name=None, inplace=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_index_ext.init_range_index(0, len(arr),
                1, None)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl_drop

    def get_name_literal(name_typ, is_index=False, series_name=None):
        if is_overload_none(name_typ):
            if is_index:
                return 'index' if series_name != 'index' else 'level_0'
            return 0
        if is_literal_type(name_typ):
            return get_literal_value(name_typ)
        else:
            raise BodoError(
                'Series.reset_index() not supported for non-literal series names'
                )
    series_name = get_name_literal(S.name_typ)
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        zdgx__papml = ', '.join(['index_arrs[{}]'.format(epsx__nqlia) for
            epsx__nqlia in range(S.index.nlevels)])
    else:
        zdgx__papml = '    bodo.utils.conversion.index_to_array(index)\n'
    thz__gxye = 'index' if 'index' != series_name else 'level_0'
    lzdq__afj = get_index_names(S.index, 'Series.reset_index()', thz__gxye)
    columns = [name for name in lzdq__afj]
    columns.append(series_name)
    olhtg__izt = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    olhtg__izt += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    olhtg__izt += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        olhtg__izt += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    olhtg__izt += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    olhtg__izt += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({zdgx__papml}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    siim__hlnfv = {}
    exec(olhtg__izt, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, siim__hlnfv)
    roz__ejq = siim__hlnfv['_impl']
    return roz__ejq


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnux__byyp = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


@overload_method(SeriesType, 'round', inline='always', no_unliteral=True)
def overload_series_round(S, decimals=0):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.round()')

    def impl(S, decimals=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        hnux__byyp = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[epsx__nqlia]):
                bodo.libs.array_kernels.setna(hnux__byyp, epsx__nqlia)
            else:
                hnux__byyp[epsx__nqlia] = np.round(arr[epsx__nqlia], decimals)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    dez__zieuq = dict(level=level, numeric_only=numeric_only)
    vcpmw__vaq = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sum(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sum(): skipna argument must be a boolean')
    if not is_overload_int(min_count):
        raise BodoError('Series.sum(): min_count argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.sum()'
        )

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_sum(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'prod', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'product', inline='always', no_unliteral=True)
def overload_series_prod(S, axis=None, skipna=True, level=None,
    numeric_only=None, min_count=0):
    dez__zieuq = dict(level=level, numeric_only=numeric_only)
    vcpmw__vaq = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.product(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.product(): skipna argument must be a boolean')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.product()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_prod(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'any', inline='always', no_unliteral=True)
def overload_series_any(S, axis=0, bool_only=None, skipna=True, level=None):
    dez__zieuq = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=
        level)
    vcpmw__vaq = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.any()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_any(A)
    return impl


@overload_method(SeriesType, 'equals', inline='always', no_unliteral=True)
def overload_series_equals(S, other):
    if not isinstance(other, SeriesType):
        raise BodoError("Series.equals() 'other' must be a Series")
    if isinstance(S.data, bodo.ArrayItemArrayType):
        raise BodoError(
            'Series.equals() not supported for Series where each element is an array or list'
            )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.equals()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.equals()')
    if S.data != other.data:
        return lambda S, other: False

    def impl(S, other):
        wcy__qbud = bodo.hiframes.pd_series_ext.get_series_data(S)
        urkad__barll = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        rbqs__hddj = 0
        for epsx__nqlia in numba.parfors.parfor.internal_prange(len(wcy__qbud)
            ):
            frjfz__kltg = 0
            nwh__bnl = bodo.libs.array_kernels.isna(wcy__qbud, epsx__nqlia)
            dxmzw__cpyvl = bodo.libs.array_kernels.isna(urkad__barll,
                epsx__nqlia)
            if nwh__bnl and not dxmzw__cpyvl or not nwh__bnl and dxmzw__cpyvl:
                frjfz__kltg = 1
            elif not nwh__bnl:
                if wcy__qbud[epsx__nqlia] != urkad__barll[epsx__nqlia]:
                    frjfz__kltg = 1
            rbqs__hddj += frjfz__kltg
        return rbqs__hddj == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    dez__zieuq = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=
        level)
    vcpmw__vaq = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    dez__zieuq = dict(level=level)
    vcpmw__vaq = dict(level=None)
    check_unsupported_args('Series.mad', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    zkf__mcvaj = types.float64
    hlwz__mzdn = types.float64
    if S.dtype == types.float32:
        zkf__mcvaj = types.float32
        hlwz__mzdn = types.float32
    yjr__kanmp = zkf__mcvaj(0)
    hvbza__fgynt = hlwz__mzdn(0)
    bzah__krba = hlwz__mzdn(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        omds__ahqg = yjr__kanmp
        rbqs__hddj = hvbza__fgynt
        for epsx__nqlia in numba.parfors.parfor.internal_prange(len(A)):
            frjfz__kltg = yjr__kanmp
            vcx__wwie = hvbza__fgynt
            if not bodo.libs.array_kernels.isna(A, epsx__nqlia) or not skipna:
                frjfz__kltg = A[epsx__nqlia]
                vcx__wwie = bzah__krba
            omds__ahqg += frjfz__kltg
            rbqs__hddj += vcx__wwie
        aol__wqo = bodo.hiframes.series_kernels._mean_handle_nan(omds__ahqg,
            rbqs__hddj)
        eryda__csc = yjr__kanmp
        for epsx__nqlia in numba.parfors.parfor.internal_prange(len(A)):
            frjfz__kltg = yjr__kanmp
            if not bodo.libs.array_kernels.isna(A, epsx__nqlia) or not skipna:
                frjfz__kltg = abs(A[epsx__nqlia] - aol__wqo)
            eryda__csc += frjfz__kltg
        urvx__xhdm = bodo.hiframes.series_kernels._mean_handle_nan(eryda__csc,
            rbqs__hddj)
        return urvx__xhdm
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    dez__zieuq = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    vcpmw__vaq = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mean(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.mean()')

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_mean(arr)
    return impl


@overload_method(SeriesType, 'sem', inline='always', no_unliteral=True)
def overload_series_sem(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    dez__zieuq = dict(level=level, numeric_only=numeric_only)
    vcpmw__vaq = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sem(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sem(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.sem(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.sem()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        kdddr__bcra = 0
        cny__vzhcg = 0
        rbqs__hddj = 0
        for epsx__nqlia in numba.parfors.parfor.internal_prange(len(A)):
            frjfz__kltg = 0
            vcx__wwie = 0
            if not bodo.libs.array_kernels.isna(A, epsx__nqlia) or not skipna:
                frjfz__kltg = A[epsx__nqlia]
                vcx__wwie = 1
            kdddr__bcra += frjfz__kltg
            cny__vzhcg += frjfz__kltg * frjfz__kltg
            rbqs__hddj += vcx__wwie
        uraqf__hhv = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            kdddr__bcra, cny__vzhcg, rbqs__hddj, ddof)
        weu__btbq = bodo.hiframes.series_kernels._sem_handle_nan(uraqf__hhv,
            rbqs__hddj)
        return weu__btbq
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    dez__zieuq = dict(level=level, numeric_only=numeric_only)
    vcpmw__vaq = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.kurtosis(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError(
            "Series.kurtosis(): 'skipna' argument must be a boolean")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.kurtosis()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        kdddr__bcra = 0.0
        cny__vzhcg = 0.0
        aeji__msz = 0.0
        fbs__msac = 0.0
        rbqs__hddj = 0
        for epsx__nqlia in numba.parfors.parfor.internal_prange(len(A)):
            frjfz__kltg = 0.0
            vcx__wwie = 0
            if not bodo.libs.array_kernels.isna(A, epsx__nqlia) or not skipna:
                frjfz__kltg = np.float64(A[epsx__nqlia])
                vcx__wwie = 1
            kdddr__bcra += frjfz__kltg
            cny__vzhcg += frjfz__kltg ** 2
            aeji__msz += frjfz__kltg ** 3
            fbs__msac += frjfz__kltg ** 4
            rbqs__hddj += vcx__wwie
        uraqf__hhv = bodo.hiframes.series_kernels.compute_kurt(kdddr__bcra,
            cny__vzhcg, aeji__msz, fbs__msac, rbqs__hddj)
        return uraqf__hhv
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    dez__zieuq = dict(level=level, numeric_only=numeric_only)
    vcpmw__vaq = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.skew(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.skew(): skipna argument must be a boolean')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.skew()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        kdddr__bcra = 0.0
        cny__vzhcg = 0.0
        aeji__msz = 0.0
        rbqs__hddj = 0
        for epsx__nqlia in numba.parfors.parfor.internal_prange(len(A)):
            frjfz__kltg = 0.0
            vcx__wwie = 0
            if not bodo.libs.array_kernels.isna(A, epsx__nqlia) or not skipna:
                frjfz__kltg = np.float64(A[epsx__nqlia])
                vcx__wwie = 1
            kdddr__bcra += frjfz__kltg
            cny__vzhcg += frjfz__kltg ** 2
            aeji__msz += frjfz__kltg ** 3
            rbqs__hddj += vcx__wwie
        uraqf__hhv = bodo.hiframes.series_kernels.compute_skew(kdddr__bcra,
            cny__vzhcg, aeji__msz, rbqs__hddj)
        return uraqf__hhv
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    dez__zieuq = dict(level=level, numeric_only=numeric_only)
    vcpmw__vaq = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.var(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.var(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.var(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.var()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_var(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'std', inline='always', no_unliteral=True)
def overload_series_std(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    dez__zieuq = dict(level=level, numeric_only=numeric_only)
    vcpmw__vaq = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.std(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.std(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.std(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.std()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_std(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'dot', inline='always', no_unliteral=True)
def overload_series_dot(S, other):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.dot()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.dot()')

    def impl(S, other):
        wcy__qbud = bodo.hiframes.pd_series_ext.get_series_data(S)
        urkad__barll = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        sgyw__ddhhu = 0
        for epsx__nqlia in numba.parfors.parfor.internal_prange(len(wcy__qbud)
            ):
            tcyf__frqfn = wcy__qbud[epsx__nqlia]
            jcdrt__uwzlu = urkad__barll[epsx__nqlia]
            sgyw__ddhhu += tcyf__frqfn * jcdrt__uwzlu
        return sgyw__ddhhu
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    dez__zieuq = dict(skipna=skipna)
    vcpmw__vaq = dict(skipna=True)
    check_unsupported_args('Series.cumsum', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumsum(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cumsum()')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumsum(), index, name)
    return impl


@overload_method(SeriesType, 'cumprod', inline='always', no_unliteral=True)
def overload_series_cumprod(S, axis=None, skipna=True):
    dez__zieuq = dict(skipna=skipna)
    vcpmw__vaq = dict(skipna=True)
    check_unsupported_args('Series.cumprod', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumprod(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cumprod()')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumprod(), index, name
            )
    return impl


@overload_method(SeriesType, 'cummin', inline='always', no_unliteral=True)
def overload_series_cummin(S, axis=None, skipna=True):
    dez__zieuq = dict(skipna=skipna)
    vcpmw__vaq = dict(skipna=True)
    check_unsupported_args('Series.cummin', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummin(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cummin()')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummin(arr), index, name)
    return impl


@overload_method(SeriesType, 'cummax', inline='always', no_unliteral=True)
def overload_series_cummax(S, axis=None, skipna=True):
    dez__zieuq = dict(skipna=skipna)
    vcpmw__vaq = dict(skipna=True)
    check_unsupported_args('Series.cummax', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummax(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cummax()')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummax(arr), index, name)
    return impl


@overload_method(SeriesType, 'rename', inline='always', no_unliteral=True)
def overload_series_rename(S, index=None, axis=None, copy=True, inplace=
    False, level=None, errors='ignore'):
    if not (index == bodo.string_type or isinstance(index, types.StringLiteral)
        ):
        raise BodoError("Series.rename() 'index' can only be a string")
    dez__zieuq = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    vcpmw__vaq = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        rff__lfjw = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, rff__lfjw, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    dez__zieuq = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    vcpmw__vaq = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if is_overload_none(mapper) or not is_scalar_type(mapper):
        raise BodoError(
            "Series.rename_axis(): 'mapper' is required and must be a scalar type."
            )

    def impl(S, mapper=None, index=None, columns=None, axis=None, copy=True,
        inplace=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        index = index.rename(mapper)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'abs', inline='always', no_unliteral=True)
def overload_series_abs(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.abs()'
        )

    def impl(S):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(np.abs(A), index, name)
    return impl


@overload_method(SeriesType, 'count', no_unliteral=True)
def overload_series_count(S, level=None):
    dez__zieuq = dict(level=level)
    vcpmw__vaq = dict(level=None)
    check_unsupported_args('Series.count', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    dez__zieuq = dict(method=method, min_periods=min_periods)
    vcpmw__vaq = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        ttfs__dutx = S.sum()
        hewp__vwhdg = other.sum()
        a = n * (S * other).sum() - ttfs__dutx * hewp__vwhdg
        qnio__dkf = n * (S ** 2).sum() - ttfs__dutx ** 2
        obxkp__aygxl = n * (other ** 2).sum() - hewp__vwhdg ** 2
        return a / np.sqrt(qnio__dkf * obxkp__aygxl)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    dez__zieuq = dict(min_periods=min_periods)
    vcpmw__vaq = dict(min_periods=None)
    check_unsupported_args('Series.cov', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        ttfs__dutx = S.mean()
        hewp__vwhdg = other.mean()
        pntx__gdzeu = ((S - ttfs__dutx) * (other - hewp__vwhdg)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(pntx__gdzeu, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            bqvps__vyon = np.sign(sum_val)
            return np.inf * bqvps__vyon
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    dez__zieuq = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    vcpmw__vaq = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.min(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.min(): only ordered categoricals are possible')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.min()'
        )

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_min(arr)
    return impl


@overload(max, no_unliteral=True)
def overload_series_builtins_max(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.max()
        return impl


@overload(min, no_unliteral=True)
def overload_series_builtins_min(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.min()
        return impl


@overload(sum, no_unliteral=True)
def overload_series_builtins_sum(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.sum()
        return impl


@overload(np.prod, inline='always', no_unliteral=True)
def overload_series_np_prod(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.prod()
        return impl


@overload_method(SeriesType, 'max', inline='always', no_unliteral=True)
def overload_series_max(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    dez__zieuq = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    vcpmw__vaq = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.max(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.max(): only ordered categoricals are possible')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.max()'
        )

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_max(arr)
    return impl


@overload_method(SeriesType, 'idxmin', inline='always', no_unliteral=True)
def overload_series_idxmin(S, axis=0, skipna=True):
    dez__zieuq = dict(axis=axis, skipna=skipna)
    vcpmw__vaq = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.idxmin()')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmin() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmin(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmin(arr, index)
    return impl


@overload_method(SeriesType, 'idxmax', inline='always', no_unliteral=True)
def overload_series_idxmax(S, axis=0, skipna=True):
    dez__zieuq = dict(axis=axis, skipna=skipna)
    vcpmw__vaq = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.idxmax()')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmax() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmax(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmax(arr, index)
    return impl


@overload_method(SeriesType, 'infer_objects', inline='always')
def overload_series_infer_objects(S):
    return lambda S: S.copy()


@overload_attribute(SeriesType, 'is_monotonic', inline='always')
@overload_attribute(SeriesType, 'is_monotonic_increasing', inline='always')
def overload_series_is_monotonic_increasing(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.is_monotonic_increasing')
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 1)


@overload_attribute(SeriesType, 'is_monotonic_decreasing', inline='always')
def overload_series_is_monotonic_decreasing(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.is_monotonic_decreasing')
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 2)


@overload_attribute(SeriesType, 'nbytes', inline='always')
def overload_series_nbytes(S):
    return lambda S: bodo.hiframes.pd_series_ext.get_series_data(S).nbytes


@overload_method(SeriesType, 'autocorr', inline='always', no_unliteral=True)
def overload_series_autocorr(S, lag=1):
    return lambda S, lag=1: bodo.libs.array_kernels.autocorr(bodo.hiframes.
        pd_series_ext.get_series_data(S), lag)


@overload_method(SeriesType, 'median', inline='always', no_unliteral=True)
def overload_series_median(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    dez__zieuq = dict(level=level, numeric_only=numeric_only)
    vcpmw__vaq = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.median(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.median(): skipna argument must be a boolean')
    return (lambda S, axis=None, skipna=True, level=None, numeric_only=None:
        bodo.libs.array_ops.array_op_median(bodo.hiframes.pd_series_ext.
        get_series_data(S), skipna))


def overload_series_head(S, n=5):

    def impl(S, n=5):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        pkb__zlfz = arr[:n]
        quf__xohj = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(pkb__zlfz, quf__xohj,
            name)
    return impl


@lower_builtin('series.head', SeriesType, types.Integer)
@lower_builtin('series.head', SeriesType, types.Omitted)
def series_head_lower(context, builder, sig, args):
    impl = overload_series_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@numba.extending.register_jitable
def tail_slice(k, n):
    if n == 0:
        return k
    return -n


@overload_method(SeriesType, 'tail', inline='always', no_unliteral=True)
def overload_series_tail(S, n=5):
    if not is_overload_int(n):
        raise BodoError("Series.tail(): 'n' must be an Integer")

    def impl(S, n=5):
        kjvaw__tifc = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        pkb__zlfz = arr[kjvaw__tifc:]
        quf__xohj = index[kjvaw__tifc:]
        return bodo.hiframes.pd_series_ext.init_series(pkb__zlfz, quf__xohj,
            name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    ufqk__todd = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in ufqk__todd:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            bmf__nfjom = index[0]
            vkkn__pjlir = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                bmf__nfjom, False))
        else:
            vkkn__pjlir = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        pkb__zlfz = arr[:vkkn__pjlir]
        quf__xohj = index[:vkkn__pjlir]
        return bodo.hiframes.pd_series_ext.init_series(pkb__zlfz, quf__xohj,
            name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    ufqk__todd = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in ufqk__todd:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            hqid__ryxvq = index[-1]
            vkkn__pjlir = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                hqid__ryxvq, True))
        else:
            vkkn__pjlir = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        pkb__zlfz = arr[len(arr) - vkkn__pjlir:]
        quf__xohj = index[len(arr) - vkkn__pjlir:]
        return bodo.hiframes.pd_series_ext.init_series(pkb__zlfz, quf__xohj,
            name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        sxm__wafx = bodo.utils.conversion.index_to_array(index)
        fppb__rdzqb, novg__dveu = (bodo.libs.array_kernels.
            first_last_valid_index(arr, sxm__wafx))
        return novg__dveu if fppb__rdzqb else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        sxm__wafx = bodo.utils.conversion.index_to_array(index)
        fppb__rdzqb, novg__dveu = (bodo.libs.array_kernels.
            first_last_valid_index(arr, sxm__wafx, False))
        return novg__dveu if fppb__rdzqb else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    dez__zieuq = dict(keep=keep)
    vcpmw__vaq = dict(keep='first')
    check_unsupported_args('Series.nlargest', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        sxm__wafx = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnux__byyp, hzwf__nio = bodo.libs.array_kernels.nlargest(arr,
            sxm__wafx, n, True, bodo.hiframes.series_kernels.gt_f)
        lme__lmzyh = bodo.utils.conversion.convert_to_index(hzwf__nio)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
            lme__lmzyh, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    dez__zieuq = dict(keep=keep)
    vcpmw__vaq = dict(keep='first')
    check_unsupported_args('Series.nsmallest', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        sxm__wafx = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnux__byyp, hzwf__nio = bodo.libs.array_kernels.nlargest(arr,
            sxm__wafx, n, False, bodo.hiframes.series_kernels.lt_f)
        lme__lmzyh = bodo.utils.conversion.convert_to_index(hzwf__nio)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
            lme__lmzyh, name)
    return impl


@overload_method(SeriesType, 'notnull', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'notna', inline='always', no_unliteral=True)
def overload_series_notna(S):
    return lambda S: S.isna() == False


@overload_method(SeriesType, 'astype', inline='always', no_unliteral=True)
@overload_method(HeterogeneousSeriesType, 'astype', inline='always',
    no_unliteral=True)
def overload_series_astype(S, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True):
    dez__zieuq = dict(errors=errors)
    vcpmw__vaq = dict(errors='raise')
    check_unsupported_args('Series.astype', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "Series.astype(): 'dtype' when passed as string must be a constant value"
            )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.astype()')

    def impl(S, dtype, copy=True, errors='raise', _bodo_nan_to_str=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnux__byyp = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    dez__zieuq = dict(axis=axis, is_copy=is_copy)
    vcpmw__vaq = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        wxfu__his = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[wxfu__his],
            index[wxfu__his], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    dez__zieuq = dict(axis=axis, kind=kind, order=order)
    vcpmw__vaq = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        txaxo__enlya = S.notna().values
        if not txaxo__enlya.all():
            hnux__byyp = np.full(n, -1, np.int64)
            hnux__byyp[txaxo__enlya] = argsort(arr[txaxo__enlya])
        else:
            hnux__byyp = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    dez__zieuq = dict(axis=axis, numeric_only=numeric_only)
    vcpmw__vaq = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_str(method):
        raise BodoError(
            "Series.rank(): 'method' argument must be a constant string")
    if not is_overload_constant_str(na_option):
        raise BodoError(
            "Series.rank(): 'na_option' argument must be a constant string")

    def impl(S, axis=0, method='average', numeric_only=None, na_option=
        'keep', ascending=True, pct=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnux__byyp = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    dez__zieuq = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    vcpmw__vaq = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    wlg__jcpb = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        aairp__obcc = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, wlg__jcpb)
        ooc__kqy = aairp__obcc.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        hnux__byyp = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(ooc__kqy
            , 0)
        lme__lmzyh = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            ooc__kqy)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
            lme__lmzyh, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    dez__zieuq = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    vcpmw__vaq = dict(axis=0, inplace=False, kind='quicksort', ignore_index
        =False, key=None)
    check_unsupported_args('Series.sort_values', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    kpwif__smtb = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        aairp__obcc = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, kpwif__smtb)
        ooc__kqy = aairp__obcc.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        hnux__byyp = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(ooc__kqy
            , 0)
        lme__lmzyh = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            ooc__kqy)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
            lme__lmzyh, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    jlzb__vob = is_overload_true(is_nullable)
    olhtg__izt = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    olhtg__izt += '  numba.parfors.parfor.init_prange()\n'
    olhtg__izt += '  n = len(arr)\n'
    if jlzb__vob:
        olhtg__izt += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        olhtg__izt += '  out_arr = np.empty(n, np.int64)\n'
    olhtg__izt += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    olhtg__izt += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if jlzb__vob:
        olhtg__izt += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        olhtg__izt += '      out_arr[i] = -1\n'
    olhtg__izt += '      continue\n'
    olhtg__izt += '    val = arr[i]\n'
    olhtg__izt += '    if include_lowest and val == bins[0]:\n'
    olhtg__izt += '      ind = 1\n'
    olhtg__izt += '    else:\n'
    olhtg__izt += '      ind = np.searchsorted(bins, val)\n'
    olhtg__izt += '    if ind == 0 or ind == len(bins):\n'
    if jlzb__vob:
        olhtg__izt += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        olhtg__izt += '      out_arr[i] = -1\n'
    olhtg__izt += '    else:\n'
    olhtg__izt += '      out_arr[i] = ind - 1\n'
    olhtg__izt += '  return out_arr\n'
    siim__hlnfv = {}
    exec(olhtg__izt, {'bodo': bodo, 'np': np, 'numba': numba}, siim__hlnfv)
    impl = siim__hlnfv['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        vudgl__orj, gocts__loqq = np.divmod(x, 1)
        if vudgl__orj == 0:
            qbzcb__tsog = -int(np.floor(np.log10(abs(gocts__loqq)))
                ) - 1 + precision
        else:
            qbzcb__tsog = precision
        return np.around(x, qbzcb__tsog)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        kodyb__nyjrn = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(kodyb__nyjrn)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        dthc__urm = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            hgm__xobm = bins.copy()
            if right and include_lowest:
                hgm__xobm[0] = hgm__xobm[0] - dthc__urm
            xym__qhc = bodo.libs.interval_arr_ext.init_interval_array(hgm__xobm
                [:-1], hgm__xobm[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(xym__qhc,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        hgm__xobm = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            hgm__xobm[0] = hgm__xobm[0] - 10.0 ** -precision
        xym__qhc = bodo.libs.interval_arr_ext.init_interval_array(hgm__xobm
            [:-1], hgm__xobm[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(xym__qhc, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        xnvi__scv = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        qzbe__tdoj = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        hnux__byyp = np.zeros(nbins, np.int64)
        for epsx__nqlia in range(len(xnvi__scv)):
            hnux__byyp[qzbe__tdoj[epsx__nqlia]] = xnvi__scv[epsx__nqlia]
        return hnux__byyp
    return impl


def compute_bins(nbins, min_val, max_val):
    pass


@overload(compute_bins, no_unliteral=True)
def overload_compute_bins(nbins, min_val, max_val, right=True):

    def impl(nbins, min_val, max_val, right=True):
        if nbins < 1:
            raise ValueError('`bins` should be a positive integer.')
        min_val = min_val + 0.0
        max_val = max_val + 0.0
        if np.isinf(min_val) or np.isinf(max_val):
            raise ValueError(
                'cannot specify integer `bins` when input data contains infinity'
                )
        elif min_val == max_val:
            min_val -= 0.001 * abs(min_val) if min_val != 0 else 0.001
            max_val += 0.001 * abs(max_val) if max_val != 0 else 0.001
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
        else:
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
            vyys__zssl = (max_val - min_val) * 0.001
            if right:
                bins[0] -= vyys__zssl
            else:
                bins[-1] += vyys__zssl
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    dez__zieuq = dict(dropna=dropna)
    vcpmw__vaq = dict(dropna=True)
    check_unsupported_args('Series.value_counts', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_bool(normalize):
        raise_bodo_error(
            'Series.value_counts(): normalize argument must be a constant boolean'
            )
    if not is_overload_constant_bool(sort):
        raise_bodo_error(
            'Series.value_counts(): sort argument must be a constant boolean')
    if not is_overload_bool(ascending):
        raise_bodo_error(
            'Series.value_counts(): ascending argument must be a constant boolean'
            )
    nygw__zvap = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    olhtg__izt = 'def impl(\n'
    olhtg__izt += '    S,\n'
    olhtg__izt += '    normalize=False,\n'
    olhtg__izt += '    sort=True,\n'
    olhtg__izt += '    ascending=False,\n'
    olhtg__izt += '    bins=None,\n'
    olhtg__izt += '    dropna=True,\n'
    olhtg__izt += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    olhtg__izt += '):\n'
    olhtg__izt += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    olhtg__izt += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    olhtg__izt += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if nygw__zvap:
        olhtg__izt += '    right = True\n'
        olhtg__izt += _gen_bins_handling(bins, S.dtype)
        olhtg__izt += '    arr = get_bin_inds(bins, arr)\n'
    olhtg__izt += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    olhtg__izt += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    olhtg__izt += '    )\n'
    olhtg__izt += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if nygw__zvap:
        olhtg__izt += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        olhtg__izt += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        olhtg__izt += '    index = get_bin_labels(bins)\n'
    else:
        olhtg__izt += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        olhtg__izt += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        olhtg__izt += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        olhtg__izt += '    )\n'
        olhtg__izt += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    olhtg__izt += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        olhtg__izt += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        qzyx__hrqlu = 'len(S)' if nygw__zvap else 'count_arr.sum()'
        olhtg__izt += f'    res = res / float({qzyx__hrqlu})\n'
    olhtg__izt += '    return res\n'
    siim__hlnfv = {}
    exec(olhtg__izt, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, siim__hlnfv)
    impl = siim__hlnfv['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    olhtg__izt = ''
    if isinstance(bins, types.Integer):
        olhtg__izt += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        olhtg__izt += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            olhtg__izt += '    min_val = min_val.value\n'
            olhtg__izt += '    max_val = max_val.value\n'
        olhtg__izt += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            olhtg__izt += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        olhtg__izt += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return olhtg__izt


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    dez__zieuq = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    vcpmw__vaq = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    olhtg__izt = 'def impl(\n'
    olhtg__izt += '    x,\n'
    olhtg__izt += '    bins,\n'
    olhtg__izt += '    right=True,\n'
    olhtg__izt += '    labels=None,\n'
    olhtg__izt += '    retbins=False,\n'
    olhtg__izt += '    precision=3,\n'
    olhtg__izt += '    include_lowest=False,\n'
    olhtg__izt += "    duplicates='raise',\n"
    olhtg__izt += '    ordered=True\n'
    olhtg__izt += '):\n'
    if isinstance(x, SeriesType):
        olhtg__izt += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        olhtg__izt += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        olhtg__izt += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        olhtg__izt += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    olhtg__izt += _gen_bins_handling(bins, x.dtype)
    olhtg__izt += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    olhtg__izt += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    olhtg__izt += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    olhtg__izt += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        olhtg__izt += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        olhtg__izt += '    return res\n'
    else:
        olhtg__izt += '    return out_arr\n'
    siim__hlnfv = {}
    exec(olhtg__izt, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, siim__hlnfv)
    impl = siim__hlnfv['impl']
    return impl


def _get_q_list(q):
    return q


@overload(_get_q_list, no_unliteral=True)
def get_q_list_overload(q):
    if is_overload_int(q):
        return lambda q: np.linspace(0, 1, q + 1)
    return lambda q: q


@overload(pd.unique, inline='always', no_unliteral=True)
def overload_unique(values):
    if not is_series_type(values) and not (bodo.utils.utils.is_array_typ(
        values, False) and values.ndim == 1):
        raise BodoError(
            "pd.unique(): 'values' must be either a Series or a 1-d array")
    if is_series_type(values):

        def impl(values):
            arr = bodo.hiframes.pd_series_ext.get_series_data(values)
            return bodo.allgatherv(bodo.libs.array_kernels.unique(arr), False)
        return impl
    else:
        return lambda values: bodo.allgatherv(bodo.libs.array_kernels.
            unique(values), False)


@overload(pd.qcut, inline='always', no_unliteral=True)
def overload_qcut(x, q, labels=None, retbins=False, precision=3, duplicates
    ='raise'):
    dez__zieuq = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    vcpmw__vaq = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        vom__pyr = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, vom__pyr)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    dez__zieuq = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze=
        squeeze, observed=observed, dropna=dropna)
    vcpmw__vaq = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='GroupBy')
    if not is_overload_true(as_index):
        raise BodoError('as_index=False only valid with DataFrame')
    if is_overload_none(by) and is_overload_none(level):
        raise BodoError("You have to supply one of 'by' and 'level'")
    if not is_overload_none(by) and not is_overload_none(level):
        raise BodoError(
            "Series.groupby(): 'level' argument should be None if 'by' is not None"
            )
    if not is_overload_none(level):
        if not (is_overload_constant_int(level) and get_overload_const_int(
            level) == 0) or isinstance(S.index, bodo.hiframes.
            pd_multi_index_ext.MultiIndexType):
            raise BodoError(
                "Series.groupby(): MultiIndex case or 'level' other than 0 not supported yet"
                )
        ioaxu__gfoq = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            lbie__nua = bodo.utils.conversion.coerce_to_array(index)
            aairp__obcc = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                lbie__nua, arr), index, ioaxu__gfoq)
            return aairp__obcc.groupby(' ')['']
        return impl_index
    zyhvt__lekd = by
    if isinstance(by, SeriesType):
        zyhvt__lekd = by.data
    if isinstance(zyhvt__lekd, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    pufjv__rot = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        lbie__nua = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        aairp__obcc = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            lbie__nua, arr), index, pufjv__rot)
        return aairp__obcc.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    dez__zieuq = dict(verify_integrity=verify_integrity)
    vcpmw__vaq = dict(verify_integrity=False)
    check_unsupported_args('Series.append', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(to_append,
        'Series.append()')
    if isinstance(to_append, SeriesType):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S, to_append), ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    if isinstance(to_append, types.BaseTuple):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S,) + to_append, ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    return (lambda S, to_append, ignore_index=False, verify_integrity=False:
        pd.concat([S] + to_append, ignore_index=ignore_index,
        verify_integrity=verify_integrity))


@overload_method(SeriesType, 'isin', inline='always', no_unliteral=True)
def overload_series_isin(S, values):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.isin()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(values,
        'Series.isin()')
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(S, values):
            uzk__njblh = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            hnux__byyp = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(hnux__byyp, A, uzk__njblh, False)
            return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnux__byyp = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    dez__zieuq = dict(interpolation=interpolation)
    vcpmw__vaq = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnux__byyp = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                index, name)
        return impl_list
    elif isinstance(q, (float, types.Number)) or is_overload_constant_int(q):

        def impl(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return bodo.libs.array_ops.array_op_quantile(arr, q)
        return impl
    else:
        raise BodoError(
            f'Series.quantile() q type must be float or iterable of floats only.'
            )


@overload_method(SeriesType, 'nunique', inline='always', no_unliteral=True)
def overload_series_nunique(S, dropna=True):
    if not is_overload_bool(dropna):
        raise BodoError('Series.nunique: dropna must be a boolean value')

    def impl(S, dropna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_kernels.nunique(arr, dropna)
    return impl


@overload_method(SeriesType, 'unique', inline='always', no_unliteral=True)
def overload_series_unique(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        ksdjs__vqmk = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(ksdjs__vqmk, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    dez__zieuq = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    vcpmw__vaq = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.describe()')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)
        ) and not isinstance(S.data, IntegerArrayType):
        raise BodoError(f'describe() column input type {S.data} not supported.'
            )
    if S.data.dtype == bodo.datetime64ns:

        def impl_dt(S, percentiles=None, include=None, exclude=None,
            datetime_is_numeric=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
                array_ops.array_op_describe(arr), bodo.utils.conversion.
                convert_to_index(['count', 'mean', 'min', '25%', '50%',
                '75%', 'max']), name)
        return impl_dt

    def impl(S, percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.array_ops.
            array_op_describe(arr), bodo.utils.conversion.convert_to_index(
            ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']), name)
    return impl


@overload_method(SeriesType, 'memory_usage', inline='always', no_unliteral=True
    )
def overload_series_memory_usage(S, index=True, deep=False):
    if is_overload_true(index):

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            return arr.nbytes + index.nbytes
        return impl
    else:

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return arr.nbytes
        return impl


def binary_str_fillna_inplace_series_impl(is_binary=False):
    if is_binary:
        xizl__mmh = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        xizl__mmh = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    olhtg__izt = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {xizl__mmh}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    itast__vjf = dict()
    exec(olhtg__izt, {'bodo': bodo, 'numba': numba}, itast__vjf)
    bivez__hivsx = itast__vjf['impl']
    return bivez__hivsx


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        xizl__mmh = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        xizl__mmh = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    olhtg__izt = 'def impl(S,\n'
    olhtg__izt += '     value=None,\n'
    olhtg__izt += '    method=None,\n'
    olhtg__izt += '    axis=None,\n'
    olhtg__izt += '    inplace=False,\n'
    olhtg__izt += '    limit=None,\n'
    olhtg__izt += '   downcast=None,\n'
    olhtg__izt += '):\n'
    olhtg__izt += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    olhtg__izt += '    n = len(in_arr)\n'
    olhtg__izt += f'    out_arr = {xizl__mmh}(n, -1)\n'
    olhtg__izt += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    olhtg__izt += '        s = in_arr[j]\n'
    olhtg__izt += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    olhtg__izt += '            s = value\n'
    olhtg__izt += '        out_arr[j] = s\n'
    olhtg__izt += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    itast__vjf = dict()
    exec(olhtg__izt, {'bodo': bodo, 'numba': numba}, itast__vjf)
    bivez__hivsx = itast__vjf['impl']
    return bivez__hivsx


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
    pfyta__hptvw = bodo.hiframes.pd_series_ext.get_series_data(value)
    for epsx__nqlia in numba.parfors.parfor.internal_prange(len(kpcf__yite)):
        s = kpcf__yite[epsx__nqlia]
        if bodo.libs.array_kernels.isna(kpcf__yite, epsx__nqlia
            ) and not bodo.libs.array_kernels.isna(pfyta__hptvw, epsx__nqlia):
            s = pfyta__hptvw[epsx__nqlia]
        kpcf__yite[epsx__nqlia] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
    for epsx__nqlia in numba.parfors.parfor.internal_prange(len(kpcf__yite)):
        s = kpcf__yite[epsx__nqlia]
        if bodo.libs.array_kernels.isna(kpcf__yite, epsx__nqlia):
            s = value
        kpcf__yite[epsx__nqlia] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    pfyta__hptvw = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(kpcf__yite)
    hnux__byyp = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for remk__yjz in numba.parfors.parfor.internal_prange(n):
        s = kpcf__yite[remk__yjz]
        if bodo.libs.array_kernels.isna(kpcf__yite, remk__yjz
            ) and not bodo.libs.array_kernels.isna(pfyta__hptvw, remk__yjz):
            s = pfyta__hptvw[remk__yjz]
        hnux__byyp[remk__yjz] = s
        if bodo.libs.array_kernels.isna(kpcf__yite, remk__yjz
            ) and bodo.libs.array_kernels.isna(pfyta__hptvw, remk__yjz):
            bodo.libs.array_kernels.setna(hnux__byyp, remk__yjz)
    return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    pfyta__hptvw = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(kpcf__yite)
    hnux__byyp = bodo.utils.utils.alloc_type(n, kpcf__yite.dtype, (-1,))
    for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
        s = kpcf__yite[epsx__nqlia]
        if bodo.libs.array_kernels.isna(kpcf__yite, epsx__nqlia
            ) and not bodo.libs.array_kernels.isna(pfyta__hptvw, epsx__nqlia):
            s = pfyta__hptvw[epsx__nqlia]
        hnux__byyp[epsx__nqlia] = s
    return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    dez__zieuq = dict(limit=limit, downcast=downcast)
    vcpmw__vaq = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    muql__ldun = not is_overload_none(value)
    leb__jcuy = not is_overload_none(method)
    if muql__ldun and leb__jcuy:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not muql__ldun and not leb__jcuy:
        raise BodoError(
            "Series.fillna(): Must specify one of 'value' and 'method'.")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.fillna(): axis argument not supported')
    elif is_iterable_type(value) and not isinstance(value, SeriesType):
        raise BodoError('Series.fillna(): "value" parameter cannot be a list')
    elif is_var_size_item_array_type(S.data
        ) and not S.dtype == bodo.string_type:
        raise BodoError(
            f'Series.fillna() with inplace=True not supported for {S.dtype} values yet.'
            )
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "Series.fillna(): 'inplace' argument must be a constant boolean")
    if leb__jcuy:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        gncqb__zhpsj = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(gncqb__zhpsj)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(gncqb__zhpsj)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    cmy__szgt = element_type(S.data)
    tnlbj__fqj = None
    if muql__ldun:
        tnlbj__fqj = element_type(types.unliteral(value))
    if tnlbj__fqj and not can_replace(cmy__szgt, tnlbj__fqj):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {tnlbj__fqj} with series type {cmy__szgt}'
            )
    if is_overload_true(inplace):
        if S.dtype == bodo.string_type:
            if S.data == bodo.dict_str_arr_type:
                raise_bodo_error(
                    "Series.fillna(): 'inplace' not supported for dictionary-encoded string arrays yet."
                    )
            if is_overload_constant_str(value) and get_overload_const_str(value
                ) == '':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=False)
            return binary_str_fillna_inplace_impl(is_binary=False)
        if S.dtype == bodo.bytes_type:
            if is_overload_constant_bytes(value) and get_overload_const_bytes(
                value) == b'':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=True)
            return binary_str_fillna_inplace_impl(is_binary=True)
        else:
            if isinstance(value, SeriesType):
                return fillna_inplace_series_impl
            return fillna_inplace_impl
    else:
        tder__uyrs = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                pfyta__hptvw = bodo.hiframes.pd_series_ext.get_series_data(
                    value)
                n = len(kpcf__yite)
                hnux__byyp = bodo.utils.utils.alloc_type(n, tder__uyrs, (-1,))
                for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(kpcf__yite, epsx__nqlia
                        ) and bodo.libs.array_kernels.isna(pfyta__hptvw,
                        epsx__nqlia):
                        bodo.libs.array_kernels.setna(hnux__byyp, epsx__nqlia)
                        continue
                    if bodo.libs.array_kernels.isna(kpcf__yite, epsx__nqlia):
                        hnux__byyp[epsx__nqlia
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            pfyta__hptvw[epsx__nqlia])
                        continue
                    hnux__byyp[epsx__nqlia
                        ] = bodo.utils.conversion.unbox_if_timestamp(kpcf__yite
                        [epsx__nqlia])
                return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                    index, name)
            return fillna_series_impl
        if leb__jcuy:
            pnr__leyxc = (types.unicode_type, types.bool_, bodo.
                datetime64ns, bodo.timedelta64ns)
            if not isinstance(cmy__szgt, (types.Integer, types.Float)
                ) and cmy__szgt not in pnr__leyxc:
                raise BodoError(
                    f"Series.fillna(): series of type {cmy__szgt} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                hnux__byyp = bodo.libs.array_kernels.ffill_bfill_arr(kpcf__yite
                    , method)
                return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(kpcf__yite)
            hnux__byyp = bodo.utils.utils.alloc_type(n, tder__uyrs, (-1,))
            for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(kpcf__yite[
                    epsx__nqlia])
                if bodo.libs.array_kernels.isna(kpcf__yite, epsx__nqlia):
                    s = value
                hnux__byyp[epsx__nqlia] = s
            return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        ywna__jnzz = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        dez__zieuq = dict(limit=limit, downcast=downcast)
        vcpmw__vaq = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', dez__zieuq,
            vcpmw__vaq, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        cmy__szgt = element_type(S.data)
        pnr__leyxc = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(cmy__szgt, (types.Integer, types.Float)
            ) and cmy__szgt not in pnr__leyxc:
            raise BodoError(
                f'Series.{overload_name}(): series of type {cmy__szgt} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            hnux__byyp = bodo.libs.array_kernels.ffill_bfill_arr(kpcf__yite,
                ywna__jnzz)
            return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        rgots__jsuz = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            rgots__jsuz)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        ujimt__sbl = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(ujimt__sbl)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        ujimt__sbl = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(ujimt__sbl)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        ujimt__sbl = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(ujimt__sbl)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    dez__zieuq = dict(inplace=inplace, limit=limit, regex=regex, method=method)
    ikm__dvrpp = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', dez__zieuq, ikm__dvrpp,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    cmy__szgt = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        lat__ielzx = element_type(to_replace.key_type)
        tnlbj__fqj = element_type(to_replace.value_type)
    else:
        lat__ielzx = element_type(to_replace)
        tnlbj__fqj = element_type(value)
    jyf__eoahz = None
    if cmy__szgt != types.unliteral(lat__ielzx):
        if bodo.utils.typing.equality_always_false(cmy__szgt, types.
            unliteral(lat__ielzx)
            ) or not bodo.utils.typing.types_equality_exists(cmy__szgt,
            lat__ielzx):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(cmy__szgt, (types.Float, types.Integer)
            ) or cmy__szgt == np.bool_:
            jyf__eoahz = cmy__szgt
    if not can_replace(cmy__szgt, types.unliteral(tnlbj__fqj)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    ogf__gke = to_str_arr_if_dict_array(S.data)
    if isinstance(ogf__gke, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(kpcf__yite.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(kpcf__yite)
        hnux__byyp = bodo.utils.utils.alloc_type(n, ogf__gke, (-1,))
        wfim__ozn = build_replace_dict(to_replace, value, jyf__eoahz)
        for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(kpcf__yite, epsx__nqlia):
                bodo.libs.array_kernels.setna(hnux__byyp, epsx__nqlia)
                continue
            s = kpcf__yite[epsx__nqlia]
            if s in wfim__ozn:
                s = wfim__ozn[s]
            hnux__byyp[epsx__nqlia] = s
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    fov__fgi = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    ziru__bchwc = is_iterable_type(to_replace)
    pmkw__etewv = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    vpjze__onkma = is_iterable_type(value)
    if fov__fgi and pmkw__etewv:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                wfim__ozn = {}
                wfim__ozn[key_dtype_conv(to_replace)] = value
                return wfim__ozn
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            wfim__ozn = {}
            wfim__ozn[to_replace] = value
            return wfim__ozn
        return impl
    if ziru__bchwc and pmkw__etewv:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                wfim__ozn = {}
                for qkx__vsuf in to_replace:
                    wfim__ozn[key_dtype_conv(qkx__vsuf)] = value
                return wfim__ozn
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            wfim__ozn = {}
            for qkx__vsuf in to_replace:
                wfim__ozn[qkx__vsuf] = value
            return wfim__ozn
        return impl
    if ziru__bchwc and vpjze__onkma:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                wfim__ozn = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for epsx__nqlia in range(len(to_replace)):
                    wfim__ozn[key_dtype_conv(to_replace[epsx__nqlia])] = value[
                        epsx__nqlia]
                return wfim__ozn
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            wfim__ozn = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for epsx__nqlia in range(len(to_replace)):
                wfim__ozn[to_replace[epsx__nqlia]] = value[epsx__nqlia]
            return wfim__ozn
        return impl
    if isinstance(to_replace, numba.types.DictType) and is_overload_none(value
        ):
        return lambda to_replace, value, key_dtype_conv: to_replace
    raise BodoError(
        'Series.replace(): Not supported for types to_replace={} and value={}'
        .format(to_replace, value))


@overload_method(SeriesType, 'diff', inline='always', no_unliteral=True)
def overload_series_diff(S, periods=1):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.diff()')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)):
        raise BodoError(
            f'Series.diff() column input type {S.data} not supported.')
    if not is_overload_int(periods):
        raise BodoError("Series.diff(): 'periods' input must be an integer.")
    if S.data == types.Array(bodo.datetime64ns, 1, 'C'):

        def impl_datetime(S, periods=1):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            hnux__byyp = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnux__byyp = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    dez__zieuq = dict(ignore_index=ignore_index)
    txm__ank = dict(ignore_index=False)
    check_unsupported_args('Series.explode', dez__zieuq, txm__ank,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        sxm__wafx = bodo.utils.conversion.index_to_array(index)
        hnux__byyp, bwg__wrg = bodo.libs.array_kernels.explode(arr, sxm__wafx)
        lme__lmzyh = bodo.utils.conversion.index_from_array(bwg__wrg)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
            lme__lmzyh, name)
    return impl


@overload(np.digitize, inline='always', no_unliteral=True)
def overload_series_np_digitize(x, bins, right=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'numpy.digitize()')
    if isinstance(x, SeriesType):

        def impl(x, bins, right=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(x)
            return np.digitize(arr, bins, right)
        return impl


@overload(np.argmax, inline='always', no_unliteral=True)
def argmax_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            cklj__tutl = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
                cklj__tutl[epsx__nqlia] = np.argmax(a[epsx__nqlia])
            return cklj__tutl
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            jtrzr__xqzfg = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
                jtrzr__xqzfg[epsx__nqlia] = np.argmin(a[epsx__nqlia])
            return jtrzr__xqzfg
        return impl


def overload_series_np_dot(a, b, out=None):
    if (isinstance(a, SeriesType) or isinstance(b, SeriesType)
        ) and not is_overload_none(out):
        raise BodoError("np.dot(): 'out' parameter not supported yet")
    if isinstance(a, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(a)
            return np.dot(arr, b)
        return impl
    if isinstance(b, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(b)
            return np.dot(a, arr)
        return impl


overload(np.dot, inline='always', no_unliteral=True)(overload_series_np_dot)
overload(operator.matmul, inline='always', no_unliteral=True)(
    overload_series_np_dot)


@overload_method(SeriesType, 'dropna', inline='always', no_unliteral=True)
def overload_series_dropna(S, axis=0, inplace=False, how=None):
    dez__zieuq = dict(axis=axis, inplace=inplace, how=how)
    saw__bxc = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', dez__zieuq, saw__bxc,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            txaxo__enlya = S.notna().values
            sxm__wafx = bodo.utils.conversion.extract_index_array(S)
            lme__lmzyh = bodo.utils.conversion.convert_to_index(sxm__wafx[
                txaxo__enlya])
            hnux__byyp = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(kpcf__yite))
            return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                lme__lmzyh, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            sxm__wafx = bodo.utils.conversion.extract_index_array(S)
            txaxo__enlya = S.notna().values
            lme__lmzyh = bodo.utils.conversion.convert_to_index(sxm__wafx[
                txaxo__enlya])
            hnux__byyp = kpcf__yite[txaxo__enlya]
            return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                lme__lmzyh, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    dez__zieuq = dict(freq=freq, axis=axis, fill_value=fill_value)
    vcpmw__vaq = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.shift()')
    if not is_supported_shift_array_type(S.data):
        raise BodoError(
            f"Series.shift(): Series input type '{S.data.dtype}' not supported yet."
            )
    if not is_overload_int(periods):
        raise BodoError("Series.shift(): 'periods' input must be an integer.")

    def impl(S, periods=1, freq=None, axis=0, fill_value=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnux__byyp = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    dez__zieuq = dict(fill_method=fill_method, limit=limit, freq=freq)
    vcpmw__vaq = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    if not is_overload_int(periods):
        raise BodoError(
            'Series.pct_change(): periods argument must be an Integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.pct_change()')

    def impl(S, periods=1, fill_method='pad', limit=None, freq=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnux__byyp = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


def create_series_mask_where_overload(func_name):

    def overload_series_mask_where(S, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
            f'Series.{func_name}()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
            f'Series.{func_name}()')
        _validate_arguments_mask_where(f'Series.{func_name}', 'Series', S,
            cond, other, inplace, axis, level, errors, try_cast)
        if is_overload_constant_nan(other):
            hma__uzya = 'None'
        else:
            hma__uzya = 'other'
        olhtg__izt = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            olhtg__izt += '  cond = ~cond\n'
        olhtg__izt += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        olhtg__izt += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        olhtg__izt += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        olhtg__izt += (
            f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {hma__uzya})\n'
            )
        olhtg__izt += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        siim__hlnfv = {}
        exec(olhtg__izt, {'bodo': bodo, 'np': np}, siim__hlnfv)
        impl = siim__hlnfv['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        rgots__jsuz = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(rgots__jsuz)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    dez__zieuq = dict(inplace=inplace, level=level, errors=errors, try_cast
        =try_cast)
    vcpmw__vaq = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name=module_name)
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if isinstance(S, bodo.hiframes.pd_index_ext.RangeIndexType):
        arr = types.Array(types.int64, 1, 'C')
    else:
        arr = S.data
    if isinstance(other, SeriesType):
        _validate_self_other_mask_where(func_name, module_name, arr, other.data
            )
    else:
        _validate_self_other_mask_where(func_name, module_name, arr, other)
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        cond.ndim == 1 and cond.dtype == types.bool_):
        raise BodoError(
            f"{func_name}() 'cond' argument must be a Series or 1-dim array of booleans"
            )


def _validate_self_other_mask_where(func_name, module_name, arr, other,
    max_ndim=1, is_default=False):
    if not (isinstance(arr, types.Array) or isinstance(arr,
        BooleanArrayType) or isinstance(arr, IntegerArrayType) or bodo.
        utils.utils.is_array_typ(arr, False) and arr.dtype in [bodo.
        string_type, bodo.bytes_type] or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type not in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.pd_timestamp_type, bodo.
        pd_timedelta_type]):
        raise BodoError(
            f'{func_name}() {module_name} data with type {arr} not yet supported'
            )
    kizwf__xhrsl = is_overload_constant_nan(other)
    if not (is_default or kizwf__xhrsl or is_scalar_type(other) or 
        isinstance(other, types.Array) and other.ndim >= 1 and other.ndim <=
        max_ndim or isinstance(other, SeriesType) and (isinstance(arr,
        types.Array) or arr.dtype in [bodo.string_type, bodo.bytes_type]) or
        is_str_arr_type(other) and (arr.dtype == bodo.string_type or 
        isinstance(arr, bodo.CategoricalArrayType) and arr.dtype.elem_type ==
        bodo.string_type) or isinstance(other, BinaryArrayType) and (arr.
        dtype == bodo.bytes_type or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type == bodo.bytes_type) or
        (not (isinstance(other, (StringArrayType, BinaryArrayType)) or 
        other == bodo.dict_str_arr_type) and (isinstance(arr.dtype, types.
        Integer) and (bodo.utils.utils.is_array_typ(other) and isinstance(
        other.dtype, types.Integer) or is_series_type(other) and isinstance
        (other.dtype, types.Integer))) or (bodo.utils.utils.is_array_typ(
        other) and arr.dtype == other.dtype or is_series_type(other) and 
        arr.dtype == other.dtype)) and (isinstance(arr, BooleanArrayType) or
        isinstance(arr, IntegerArrayType))):
        raise BodoError(
            f"{func_name}() 'other' must be a scalar, non-categorical series, 1-dim numpy array or StringArray with a matching type for {module_name}."
            )
    if not is_default:
        if isinstance(arr.dtype, bodo.PDCategoricalDtype):
            nawj__ujvnb = arr.dtype.elem_type
        else:
            nawj__ujvnb = arr.dtype
        if is_iterable_type(other):
            laml__hknt = other.dtype
        elif kizwf__xhrsl:
            laml__hknt = types.float64
        else:
            laml__hknt = types.unliteral(other)
        if not kizwf__xhrsl and not is_common_scalar_dtype([nawj__ujvnb,
            laml__hknt]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        dez__zieuq = dict(level=level, axis=axis)
        vcpmw__vaq = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), dez__zieuq,
            vcpmw__vaq, package_name='pandas', module_name='Series')
        ekdga__ktgzz = other == string_type or is_overload_constant_str(other)
        mous__hzt = is_iterable_type(other) and other.dtype == string_type
        jkgz__fxus = S.dtype == string_type and (op == operator.add and (
            ekdga__ktgzz or mous__hzt) or op == operator.mul and isinstance
            (other, types.Integer))
        rll__obgqt = S.dtype == bodo.timedelta64ns
        wvc__zde = S.dtype == bodo.datetime64ns
        vpswe__caqw = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        tnrd__jbnwq = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        bzbp__lywvv = rll__obgqt and (vpswe__caqw or tnrd__jbnwq
            ) or wvc__zde and vpswe__caqw
        bzbp__lywvv = bzbp__lywvv and op == operator.add
        if not (isinstance(S.dtype, types.Number) or jkgz__fxus or bzbp__lywvv
            ):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        jvgb__gfaa = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            ogf__gke = jvgb__gfaa.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and ogf__gke == types.Array(types.bool_, 1, 'C'):
                ogf__gke = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                hnux__byyp = bodo.utils.utils.alloc_type(n, ogf__gke, (-1,))
                for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
                    ugcdf__xkdmf = bodo.libs.array_kernels.isna(arr,
                        epsx__nqlia)
                    if ugcdf__xkdmf:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(hnux__byyp,
                                epsx__nqlia)
                        else:
                            hnux__byyp[epsx__nqlia] = op(fill_value, other)
                    else:
                        hnux__byyp[epsx__nqlia] = op(arr[epsx__nqlia], other)
                return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        ogf__gke = jvgb__gfaa.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and ogf__gke == types.Array(
            types.bool_, 1, 'C'):
            ogf__gke = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            tuc__ettbe = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            hnux__byyp = bodo.utils.utils.alloc_type(n, ogf__gke, (-1,))
            for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
                ugcdf__xkdmf = bodo.libs.array_kernels.isna(arr, epsx__nqlia)
                ubzwm__frz = bodo.libs.array_kernels.isna(tuc__ettbe,
                    epsx__nqlia)
                if ugcdf__xkdmf and ubzwm__frz:
                    bodo.libs.array_kernels.setna(hnux__byyp, epsx__nqlia)
                elif ugcdf__xkdmf:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(hnux__byyp, epsx__nqlia)
                    else:
                        hnux__byyp[epsx__nqlia] = op(fill_value, tuc__ettbe
                            [epsx__nqlia])
                elif ubzwm__frz:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(hnux__byyp, epsx__nqlia)
                    else:
                        hnux__byyp[epsx__nqlia] = op(arr[epsx__nqlia],
                            fill_value)
                else:
                    hnux__byyp[epsx__nqlia] = op(arr[epsx__nqlia],
                        tuc__ettbe[epsx__nqlia])
            return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                index, name)
        return impl
    return overload_series_explicit_binary_op


def create_explicit_binary_reverse_op_overload(op):

    def overload_series_explicit_binary_reverse_op(S, other, level=None,
        fill_value=None, axis=0):
        if not is_overload_none(level):
            raise BodoError('level argument not supported')
        if not is_overload_zero(axis):
            raise BodoError('axis argument not supported')
        if not isinstance(S.dtype, types.Number):
            raise BodoError('only numeric values supported')
        jvgb__gfaa = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            ogf__gke = jvgb__gfaa.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and ogf__gke == types.Array(types.bool_, 1, 'C'):
                ogf__gke = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                hnux__byyp = bodo.utils.utils.alloc_type(n, ogf__gke, None)
                for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
                    ugcdf__xkdmf = bodo.libs.array_kernels.isna(arr,
                        epsx__nqlia)
                    if ugcdf__xkdmf:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(hnux__byyp,
                                epsx__nqlia)
                        else:
                            hnux__byyp[epsx__nqlia] = op(other, fill_value)
                    else:
                        hnux__byyp[epsx__nqlia] = op(other, arr[epsx__nqlia])
                return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        ogf__gke = jvgb__gfaa.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and ogf__gke == types.Array(
            types.bool_, 1, 'C'):
            ogf__gke = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            tuc__ettbe = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            hnux__byyp = bodo.utils.utils.alloc_type(n, ogf__gke, None)
            for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
                ugcdf__xkdmf = bodo.libs.array_kernels.isna(arr, epsx__nqlia)
                ubzwm__frz = bodo.libs.array_kernels.isna(tuc__ettbe,
                    epsx__nqlia)
                hnux__byyp[epsx__nqlia] = op(tuc__ettbe[epsx__nqlia], arr[
                    epsx__nqlia])
                if ugcdf__xkdmf and ubzwm__frz:
                    bodo.libs.array_kernels.setna(hnux__byyp, epsx__nqlia)
                elif ugcdf__xkdmf:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(hnux__byyp, epsx__nqlia)
                    else:
                        hnux__byyp[epsx__nqlia] = op(tuc__ettbe[epsx__nqlia
                            ], fill_value)
                elif ubzwm__frz:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(hnux__byyp, epsx__nqlia)
                    else:
                        hnux__byyp[epsx__nqlia] = op(fill_value, arr[
                            epsx__nqlia])
                else:
                    hnux__byyp[epsx__nqlia] = op(tuc__ettbe[epsx__nqlia],
                        arr[epsx__nqlia])
            return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                index, name)
        return impl
    return overload_series_explicit_binary_reverse_op


explicit_binop_funcs_two_ways = {operator.add: {'add'}, operator.sub: {
    'sub'}, operator.mul: {'mul'}, operator.truediv: {'div', 'truediv'},
    operator.floordiv: {'floordiv'}, operator.mod: {'mod'}, operator.pow: {
    'pow'}}
explicit_binop_funcs_single = {operator.lt: 'lt', operator.gt: 'gt',
    operator.le: 'le', operator.ge: 'ge', operator.ne: 'ne', operator.eq: 'eq'}
explicit_binop_funcs = set()
split_logical_binops_funcs = [operator.or_, operator.and_]


def _install_explicit_binary_ops():
    for op, enltf__pucyw in explicit_binop_funcs_two_ways.items():
        for name in enltf__pucyw:
            rgots__jsuz = create_explicit_binary_op_overload(op)
            wef__rhr = create_explicit_binary_reverse_op_overload(op)
            qogxa__zkt = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(rgots__jsuz)
            overload_method(SeriesType, qogxa__zkt, no_unliteral=True)(wef__rhr
                )
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        rgots__jsuz = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(rgots__jsuz)
        explicit_binop_funcs.add(name)


_install_explicit_binary_ops()


def create_binary_op_overload(op):

    def overload_series_binary_op(lhs, rhs):
        if (isinstance(lhs, SeriesType) and isinstance(rhs, SeriesType) and
            lhs.dtype == bodo.datetime64ns and rhs.dtype == bodo.
            datetime64ns and op == operator.sub):

            def impl_dt64(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                jezb__vbm = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                hnux__byyp = dt64_arr_sub(arr, jezb__vbm)
                return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                    index, name)
            return impl_dt64
        if op in [operator.add, operator.sub] and isinstance(lhs, SeriesType
            ) and lhs.dtype == bodo.datetime64ns and is_offsets_type(rhs):

            def impl_offsets(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                hnux__byyp = np.empty(n, np.dtype('datetime64[ns]'))
                for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, epsx__nqlia):
                        bodo.libs.array_kernels.setna(hnux__byyp, epsx__nqlia)
                        continue
                    yuay__yxiqo = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[epsx__nqlia]))
                    mbgps__gvpvw = op(yuay__yxiqo, rhs)
                    hnux__byyp[epsx__nqlia
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        mbgps__gvpvw.value)
                return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                    index, name)
            return impl_offsets
        if op == operator.add and is_offsets_type(lhs) and isinstance(rhs,
            SeriesType) and rhs.dtype == bodo.datetime64ns:

            def impl(lhs, rhs):
                return op(rhs, lhs)
            return impl
        if isinstance(lhs, SeriesType):
            if lhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                    jezb__vbm = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    hnux__byyp = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(jezb__vbm))
                    return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                jezb__vbm = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                hnux__byyp = op(arr, jezb__vbm)
                return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    asv__azxj = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    hnux__byyp = op(bodo.utils.conversion.
                        unbox_if_timestamp(asv__azxj), arr)
                    return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                asv__azxj = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                hnux__byyp = op(asv__azxj, arr)
                return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        rgots__jsuz = create_binary_op_overload(op)
        overload(op)(rgots__jsuz)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    znygz__wgk = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, znygz__wgk)
        for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, epsx__nqlia
                ) or bodo.libs.array_kernels.isna(arg2, epsx__nqlia):
                bodo.libs.array_kernels.setna(S, epsx__nqlia)
                continue
            S[epsx__nqlia
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                epsx__nqlia]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[epsx__nqlia]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                tuc__ettbe = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, tuc__ettbe)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        rgots__jsuz = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(rgots__jsuz)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                hnux__byyp = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        rgots__jsuz = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(rgots__jsuz)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    hnux__byyp = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                        index, name)
                return impl
        return overload_series_ufunc_nin_1
    elif ufunc.nin == 2:

        def overload_series_ufunc_nin_2(S1, S2):
            if isinstance(S1, SeriesType):

                def impl(S1, S2):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S1)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S1)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S1)
                    tuc__ettbe = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    hnux__byyp = ufunc(arr, tuc__ettbe)
                    return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    tuc__ettbe = bodo.hiframes.pd_series_ext.get_series_data(S2
                        )
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    hnux__byyp = ufunc(arr, tuc__ettbe)
                    return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        rgots__jsuz = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(rgots__jsuz)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        lbze__frxw = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),)
            )
        ccjvm__osjj = np.arange(n),
        bodo.libs.timsort.sort(lbze__frxw, 0, n, ccjvm__osjj)
        return ccjvm__osjj[0]
    return impl


@overload(pd.to_numeric, inline='always', no_unliteral=True)
def overload_to_numeric(arg_a, errors='raise', downcast=None):
    if not is_overload_none(downcast) and not (is_overload_constant_str(
        downcast) and get_overload_const_str(downcast) in ('integer',
        'signed', 'unsigned', 'float')):
        raise BodoError(
            'pd.to_numeric(): invalid downcasting method provided {}'.
            format(downcast))
    out_dtype = types.float64
    if not is_overload_none(downcast):
        ynam__dlb = get_overload_const_str(downcast)
        if ynam__dlb in ('integer', 'signed'):
            out_dtype = types.int64
        elif ynam__dlb == 'unsigned':
            out_dtype = types.uint64
        else:
            assert ynam__dlb == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            kpcf__yite = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            hnux__byyp = pd.to_numeric(kpcf__yite, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            fhlfv__dwyp = np.empty(n, np.float64)
            for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, epsx__nqlia):
                    bodo.libs.array_kernels.setna(fhlfv__dwyp, epsx__nqlia)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(fhlfv__dwyp,
                        epsx__nqlia, arg_a, epsx__nqlia)
            return fhlfv__dwyp
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            fhlfv__dwyp = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, epsx__nqlia):
                    bodo.libs.array_kernels.setna(fhlfv__dwyp, epsx__nqlia)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(fhlfv__dwyp,
                        epsx__nqlia, arg_a, epsx__nqlia)
            return fhlfv__dwyp
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        jhmop__tfa = if_series_to_array_type(args[0])
        if isinstance(jhmop__tfa, types.Array) and isinstance(jhmop__tfa.
            dtype, types.Integer):
            jhmop__tfa = types.Array(types.float64, 1, 'C')
        return jhmop__tfa(*args)


def where_impl_one_arg(c):
    return np.where(c)


@overload(where_impl_one_arg, no_unliteral=True)
def overload_where_unsupported_one_arg(condition):
    if isinstance(condition, SeriesType) or bodo.utils.utils.is_array_typ(
        condition, False):
        return lambda condition: np.where(condition)


def overload_np_where_one_arg(condition):
    if isinstance(condition, SeriesType):

        def impl_series(condition):
            condition = bodo.hiframes.pd_series_ext.get_series_data(condition)
            return bodo.libs.array_kernels.nonzero(condition)
        return impl_series
    elif bodo.utils.utils.is_array_typ(condition, False):

        def impl(condition):
            return bodo.libs.array_kernels.nonzero(condition)
        return impl


overload(np.where, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)
overload(where_impl_one_arg, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)


def where_impl(c, x, y):
    return np.where(c, x, y)


@overload(where_impl, no_unliteral=True)
def overload_where_unsupported(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return lambda condition, x, y: np.where(condition, x, y)


@overload(where_impl, no_unliteral=True)
@overload(np.where, no_unliteral=True)
def overload_np_where(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return
    assert condition.dtype == types.bool_, 'invalid condition dtype'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'numpy.where()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(y,
        'numpy.where()')
    xif__khoot = bodo.utils.utils.is_array_typ(x, True)
    wvzpa__fxt = bodo.utils.utils.is_array_typ(y, True)
    olhtg__izt = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        olhtg__izt += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if xif__khoot and not bodo.utils.utils.is_array_typ(x, False):
        olhtg__izt += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if wvzpa__fxt and not bodo.utils.utils.is_array_typ(y, False):
        olhtg__izt += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    olhtg__izt += '  n = len(condition)\n'
    iahdl__zkr = x.dtype if xif__khoot else types.unliteral(x)
    jmgrp__hlno = y.dtype if wvzpa__fxt else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        iahdl__zkr = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        jmgrp__hlno = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    bueas__siwm = get_data(x)
    neie__llp = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(ccjvm__osjj) for
        ccjvm__osjj in [bueas__siwm, neie__llp])
    if neie__llp == types.none:
        if isinstance(iahdl__zkr, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif bueas__siwm == neie__llp and not is_nullable:
        out_dtype = dtype_to_array_type(iahdl__zkr)
    elif iahdl__zkr == string_type or jmgrp__hlno == string_type:
        out_dtype = bodo.string_array_type
    elif bueas__siwm == bytes_type or (xif__khoot and iahdl__zkr == bytes_type
        ) and (neie__llp == bytes_type or wvzpa__fxt and jmgrp__hlno ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(iahdl__zkr, bodo.PDCategoricalDtype):
        out_dtype = None
    elif iahdl__zkr in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(iahdl__zkr, 1, 'C')
    elif jmgrp__hlno in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(jmgrp__hlno, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(iahdl__zkr), numba.np.numpy_support.
            as_dtype(jmgrp__hlno)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(iahdl__zkr, bodo.PDCategoricalDtype):
        fyjm__nar = 'x'
    else:
        fyjm__nar = 'out_dtype'
    olhtg__izt += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {fyjm__nar}, (-1,))\n')
    if isinstance(iahdl__zkr, bodo.PDCategoricalDtype):
        olhtg__izt += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        olhtg__izt += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    olhtg__izt += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    olhtg__izt += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if xif__khoot:
        olhtg__izt += '      if bodo.libs.array_kernels.isna(x, j):\n'
        olhtg__izt += '        setna(out_arr, j)\n'
        olhtg__izt += '        continue\n'
    if isinstance(iahdl__zkr, bodo.PDCategoricalDtype):
        olhtg__izt += '      out_codes[j] = x_codes[j]\n'
    else:
        olhtg__izt += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if xif__khoot else 'x'))
    olhtg__izt += '    else:\n'
    if wvzpa__fxt:
        olhtg__izt += '      if bodo.libs.array_kernels.isna(y, j):\n'
        olhtg__izt += '        setna(out_arr, j)\n'
        olhtg__izt += '        continue\n'
    if neie__llp == types.none:
        if isinstance(iahdl__zkr, bodo.PDCategoricalDtype):
            olhtg__izt += '      out_codes[j] = -1\n'
        else:
            olhtg__izt += '      setna(out_arr, j)\n'
    else:
        olhtg__izt += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if wvzpa__fxt else 'y'))
    olhtg__izt += '  return out_arr\n'
    siim__hlnfv = {}
    exec(olhtg__izt, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, siim__hlnfv)
    roz__ejq = siim__hlnfv['_impl']
    return roz__ejq


def _verify_np_select_arg_typs(condlist, choicelist, default):
    if isinstance(condlist, (types.List, types.UniTuple)):
        if not (bodo.utils.utils.is_np_array_typ(condlist.dtype) and 
            condlist.dtype.dtype == types.bool_):
            raise BodoError(
                "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
                )
    else:
        raise BodoError(
            "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
            )
    if not isinstance(choicelist, (types.List, types.UniTuple, types.BaseTuple)
        ):
        raise BodoError(
            "np.select(): 'choicelist' argument must be list or tuple type")
    if isinstance(choicelist, (types.List, types.UniTuple)):
        dnl__bek = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(dnl__bek, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(dnl__bek):
            nafm__ega = dnl__bek.data.dtype
        else:
            nafm__ega = dnl__bek.dtype
        if isinstance(nafm__ega, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        tae__bwurw = dnl__bek
    else:
        gxbb__uoz = []
        for dnl__bek in choicelist:
            if not bodo.utils.utils.is_array_typ(dnl__bek, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(dnl__bek):
                nafm__ega = dnl__bek.data.dtype
            else:
                nafm__ega = dnl__bek.dtype
            if isinstance(nafm__ega, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            gxbb__uoz.append(nafm__ega)
        if not is_common_scalar_dtype(gxbb__uoz):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        tae__bwurw = choicelist[0]
    if is_series_type(tae__bwurw):
        tae__bwurw = tae__bwurw.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, tae__bwurw.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(tae__bwurw, types.Array) or isinstance(tae__bwurw,
        BooleanArrayType) or isinstance(tae__bwurw, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(tae__bwurw, False) and tae__bwurw.
        dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {tae__bwurw} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    nvli__jbqav = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        fzfs__lko = choicelist.dtype
    else:
        kwwk__ckgq = False
        gxbb__uoz = []
        for dnl__bek in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dnl__bek,
                'numpy.select()')
            if is_nullable_type(dnl__bek):
                kwwk__ckgq = True
            if is_series_type(dnl__bek):
                nafm__ega = dnl__bek.data.dtype
            else:
                nafm__ega = dnl__bek.dtype
            if isinstance(nafm__ega, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            gxbb__uoz.append(nafm__ega)
        kywvo__sfu, pdz__anvz = get_common_scalar_dtype(gxbb__uoz)
        if not pdz__anvz:
            raise BodoError('Internal error in overload_np_select')
        yjnlj__wnpy = dtype_to_array_type(kywvo__sfu)
        if kwwk__ckgq:
            yjnlj__wnpy = to_nullable_type(yjnlj__wnpy)
        fzfs__lko = yjnlj__wnpy
    if isinstance(fzfs__lko, SeriesType):
        fzfs__lko = fzfs__lko.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        avhqu__hggt = True
    else:
        avhqu__hggt = False
    jzzd__dxtto = False
    hye__yrsbh = False
    if avhqu__hggt:
        if isinstance(fzfs__lko.dtype, types.Number):
            pass
        elif fzfs__lko.dtype == types.bool_:
            hye__yrsbh = True
        else:
            jzzd__dxtto = True
            fzfs__lko = to_nullable_type(fzfs__lko)
    elif default == types.none or is_overload_constant_nan(default):
        jzzd__dxtto = True
        fzfs__lko = to_nullable_type(fzfs__lko)
    olhtg__izt = 'def np_select_impl(condlist, choicelist, default=0):\n'
    olhtg__izt += '  if len(condlist) != len(choicelist):\n'
    olhtg__izt += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    olhtg__izt += '  output_len = len(choicelist[0])\n'
    olhtg__izt += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    olhtg__izt += '  for i in range(output_len):\n'
    if jzzd__dxtto:
        olhtg__izt += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif hye__yrsbh:
        olhtg__izt += '    out[i] = False\n'
    else:
        olhtg__izt += '    out[i] = default\n'
    if nvli__jbqav:
        olhtg__izt += '  for i in range(len(condlist) - 1, -1, -1):\n'
        olhtg__izt += '    cond = condlist[i]\n'
        olhtg__izt += '    choice = choicelist[i]\n'
        olhtg__izt += '    out = np.where(cond, choice, out)\n'
    else:
        for epsx__nqlia in range(len(choicelist) - 1, -1, -1):
            olhtg__izt += f'  cond = condlist[{epsx__nqlia}]\n'
            olhtg__izt += f'  choice = choicelist[{epsx__nqlia}]\n'
            olhtg__izt += f'  out = np.where(cond, choice, out)\n'
    olhtg__izt += '  return out'
    siim__hlnfv = dict()
    exec(olhtg__izt, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': fzfs__lko}, siim__hlnfv)
    impl = siim__hlnfv['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnux__byyp = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    dez__zieuq = dict(subset=subset, keep=keep, inplace=inplace)
    vcpmw__vaq = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        zwka__jpvv = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (zwka__jpvv,), sxm__wafx = bodo.libs.array_kernels.drop_duplicates((
            zwka__jpvv,), index, 1)
        index = bodo.utils.conversion.index_from_array(sxm__wafx)
        return bodo.hiframes.pd_series_ext.init_series(zwka__jpvv, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    ahk__kra = element_type(S.data)
    if not is_common_scalar_dtype([ahk__kra, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([ahk__kra, right]):
        raise_bodo_error(
            "Series.between(): 'right' must be compariable with the Series data"
            )
    if not is_overload_constant_str(inclusive) or get_overload_const_str(
        inclusive) not in ('both', 'neither'):
        raise_bodo_error(
            "Series.between(): 'inclusive' must be a constant string and one of ('both', 'neither')"
            )

    def impl(S, left, right, inclusive='both'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        hnux__byyp = np.empty(n, np.bool_)
        for epsx__nqlia in numba.parfors.parfor.internal_prange(n):
            frjfz__kltg = bodo.utils.conversion.box_if_dt64(arr[epsx__nqlia])
            if inclusive == 'both':
                hnux__byyp[epsx__nqlia
                    ] = frjfz__kltg <= right and frjfz__kltg >= left
            else:
                hnux__byyp[epsx__nqlia
                    ] = frjfz__kltg < right and frjfz__kltg > left
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    dez__zieuq = dict(axis=axis)
    vcpmw__vaq = dict(axis=None)
    check_unsupported_args('Series.repeat', dez__zieuq, vcpmw__vaq,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Series.repeat(): 'repeats' should be an integer or array of integers"
            )
    if isinstance(repeats, types.Integer):

        def impl_int(S, repeats, axis=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            sxm__wafx = bodo.utils.conversion.index_to_array(index)
            hnux__byyp = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            bwg__wrg = bodo.libs.array_kernels.repeat_kernel(sxm__wafx, repeats
                )
            lme__lmzyh = bodo.utils.conversion.index_from_array(bwg__wrg)
            return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
                lme__lmzyh, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        sxm__wafx = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        hnux__byyp = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        bwg__wrg = bodo.libs.array_kernels.repeat_kernel(sxm__wafx, repeats)
        lme__lmzyh = bodo.utils.conversion.index_from_array(bwg__wrg)
        return bodo.hiframes.pd_series_ext.init_series(hnux__byyp,
            lme__lmzyh, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        ccjvm__osjj = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(ccjvm__osjj)
        kdg__hcz = {}
        for epsx__nqlia in range(n):
            frjfz__kltg = bodo.utils.conversion.box_if_dt64(ccjvm__osjj[
                epsx__nqlia])
            kdg__hcz[index[epsx__nqlia]] = frjfz__kltg
        return kdg__hcz
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    gncqb__zhpsj = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            rdulg__cfdo = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(gncqb__zhpsj)
    elif is_literal_type(name):
        rdulg__cfdo = get_literal_value(name)
    else:
        raise_bodo_error(gncqb__zhpsj)
    rdulg__cfdo = 0 if rdulg__cfdo is None else rdulg__cfdo
    qjbkm__pgf = ColNamesMetaType((rdulg__cfdo,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            qjbkm__pgf)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
