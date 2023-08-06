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
            sol__fyzq = bodo.hiframes.pd_series_ext.get_series_data(s)
            yedg__qcvd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                sol__fyzq)
            return yedg__qcvd
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
            yvdkj__qhncf = list()
            for chdp__htsvm in range(len(S)):
                yvdkj__qhncf.append(S.iat[chdp__htsvm])
            return yvdkj__qhncf
        return impl_float

    def impl(S):
        yvdkj__qhncf = list()
        for chdp__htsvm in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, chdp__htsvm):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            yvdkj__qhncf.append(S.iat[chdp__htsvm])
        return yvdkj__qhncf
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    qgyxy__ulcif = dict(dtype=dtype, copy=copy, na_value=na_value)
    zdov__fjtbx = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    qgyxy__ulcif = dict(name=name, inplace=inplace)
    zdov__fjtbx = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', qgyxy__ulcif, zdov__fjtbx,
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
        vfjq__wctk = ', '.join(['index_arrs[{}]'.format(chdp__htsvm) for
            chdp__htsvm in range(S.index.nlevels)])
    else:
        vfjq__wctk = '    bodo.utils.conversion.index_to_array(index)\n'
    aqhjn__qmzzm = 'index' if 'index' != series_name else 'level_0'
    krvi__rpxme = get_index_names(S.index, 'Series.reset_index()', aqhjn__qmzzm
        )
    columns = [name for name in krvi__rpxme]
    columns.append(series_name)
    ydlwu__zqqho = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    ydlwu__zqqho += (
        '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ydlwu__zqqho += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        ydlwu__zqqho += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    ydlwu__zqqho += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    ydlwu__zqqho += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({vfjq__wctk}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    opu__rfm = {}
    exec(ydlwu__zqqho, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, opu__rfm)
    nvg__okjpa = opu__rfm['_impl']
    return nvg__okjpa


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nef__wtwj = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
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
        nef__wtwj = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[chdp__htsvm]):
                bodo.libs.array_kernels.setna(nef__wtwj, chdp__htsvm)
            else:
                nef__wtwj[chdp__htsvm] = np.round(arr[chdp__htsvm], decimals)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    qgyxy__ulcif = dict(level=level, numeric_only=numeric_only)
    zdov__fjtbx = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(level=level, numeric_only=numeric_only)
    zdov__fjtbx = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(axis=axis, bool_only=bool_only, skipna=skipna,
        level=level)
    zdov__fjtbx = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', qgyxy__ulcif, zdov__fjtbx,
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
        isotd__ucm = bodo.hiframes.pd_series_ext.get_series_data(S)
        jluw__wmy = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        uafb__vvp = 0
        for chdp__htsvm in numba.parfors.parfor.internal_prange(len(isotd__ucm)
            ):
            mwioj__dkuw = 0
            awy__nnpf = bodo.libs.array_kernels.isna(isotd__ucm, chdp__htsvm)
            zwau__jqywf = bodo.libs.array_kernels.isna(jluw__wmy, chdp__htsvm)
            if awy__nnpf and not zwau__jqywf or not awy__nnpf and zwau__jqywf:
                mwioj__dkuw = 1
            elif not awy__nnpf:
                if isotd__ucm[chdp__htsvm] != jluw__wmy[chdp__htsvm]:
                    mwioj__dkuw = 1
            uafb__vvp += mwioj__dkuw
        return uafb__vvp == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    qgyxy__ulcif = dict(axis=axis, bool_only=bool_only, skipna=skipna,
        level=level)
    zdov__fjtbx = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    qgyxy__ulcif = dict(level=level)
    zdov__fjtbx = dict(level=None)
    check_unsupported_args('Series.mad', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    dah__hbng = types.float64
    mnx__sseym = types.float64
    if S.dtype == types.float32:
        dah__hbng = types.float32
        mnx__sseym = types.float32
    ofn__ifq = dah__hbng(0)
    tzii__lkdds = mnx__sseym(0)
    owz__fbxoj = mnx__sseym(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        kmn__rtfk = ofn__ifq
        uafb__vvp = tzii__lkdds
        for chdp__htsvm in numba.parfors.parfor.internal_prange(len(A)):
            mwioj__dkuw = ofn__ifq
            ynis__zhq = tzii__lkdds
            if not bodo.libs.array_kernels.isna(A, chdp__htsvm) or not skipna:
                mwioj__dkuw = A[chdp__htsvm]
                ynis__zhq = owz__fbxoj
            kmn__rtfk += mwioj__dkuw
            uafb__vvp += ynis__zhq
        uiu__zhx = bodo.hiframes.series_kernels._mean_handle_nan(kmn__rtfk,
            uafb__vvp)
        ido__gem = ofn__ifq
        for chdp__htsvm in numba.parfors.parfor.internal_prange(len(A)):
            mwioj__dkuw = ofn__ifq
            if not bodo.libs.array_kernels.isna(A, chdp__htsvm) or not skipna:
                mwioj__dkuw = abs(A[chdp__htsvm] - uiu__zhx)
            ido__gem += mwioj__dkuw
        hfi__apkae = bodo.hiframes.series_kernels._mean_handle_nan(ido__gem,
            uafb__vvp)
        return hfi__apkae
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    qgyxy__ulcif = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    zdov__fjtbx = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(level=level, numeric_only=numeric_only)
    zdov__fjtbx = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', qgyxy__ulcif, zdov__fjtbx,
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
        cuwcm__yqwf = 0
        jpmz__dym = 0
        uafb__vvp = 0
        for chdp__htsvm in numba.parfors.parfor.internal_prange(len(A)):
            mwioj__dkuw = 0
            ynis__zhq = 0
            if not bodo.libs.array_kernels.isna(A, chdp__htsvm) or not skipna:
                mwioj__dkuw = A[chdp__htsvm]
                ynis__zhq = 1
            cuwcm__yqwf += mwioj__dkuw
            jpmz__dym += mwioj__dkuw * mwioj__dkuw
            uafb__vvp += ynis__zhq
        kndno__mwjzj = (bodo.hiframes.series_kernels.
            _compute_var_nan_count_ddof(cuwcm__yqwf, jpmz__dym, uafb__vvp,
            ddof))
        ndb__euihf = bodo.hiframes.series_kernels._sem_handle_nan(kndno__mwjzj,
            uafb__vvp)
        return ndb__euihf
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    qgyxy__ulcif = dict(level=level, numeric_only=numeric_only)
    zdov__fjtbx = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', qgyxy__ulcif, zdov__fjtbx,
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
        cuwcm__yqwf = 0.0
        jpmz__dym = 0.0
        qrof__fumfk = 0.0
        rraye__pbyd = 0.0
        uafb__vvp = 0
        for chdp__htsvm in numba.parfors.parfor.internal_prange(len(A)):
            mwioj__dkuw = 0.0
            ynis__zhq = 0
            if not bodo.libs.array_kernels.isna(A, chdp__htsvm) or not skipna:
                mwioj__dkuw = np.float64(A[chdp__htsvm])
                ynis__zhq = 1
            cuwcm__yqwf += mwioj__dkuw
            jpmz__dym += mwioj__dkuw ** 2
            qrof__fumfk += mwioj__dkuw ** 3
            rraye__pbyd += mwioj__dkuw ** 4
            uafb__vvp += ynis__zhq
        kndno__mwjzj = bodo.hiframes.series_kernels.compute_kurt(cuwcm__yqwf,
            jpmz__dym, qrof__fumfk, rraye__pbyd, uafb__vvp)
        return kndno__mwjzj
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    qgyxy__ulcif = dict(level=level, numeric_only=numeric_only)
    zdov__fjtbx = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', qgyxy__ulcif, zdov__fjtbx,
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
        cuwcm__yqwf = 0.0
        jpmz__dym = 0.0
        qrof__fumfk = 0.0
        uafb__vvp = 0
        for chdp__htsvm in numba.parfors.parfor.internal_prange(len(A)):
            mwioj__dkuw = 0.0
            ynis__zhq = 0
            if not bodo.libs.array_kernels.isna(A, chdp__htsvm) or not skipna:
                mwioj__dkuw = np.float64(A[chdp__htsvm])
                ynis__zhq = 1
            cuwcm__yqwf += mwioj__dkuw
            jpmz__dym += mwioj__dkuw ** 2
            qrof__fumfk += mwioj__dkuw ** 3
            uafb__vvp += ynis__zhq
        kndno__mwjzj = bodo.hiframes.series_kernels.compute_skew(cuwcm__yqwf,
            jpmz__dym, qrof__fumfk, uafb__vvp)
        return kndno__mwjzj
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    qgyxy__ulcif = dict(level=level, numeric_only=numeric_only)
    zdov__fjtbx = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(level=level, numeric_only=numeric_only)
    zdov__fjtbx = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', qgyxy__ulcif, zdov__fjtbx,
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
        isotd__ucm = bodo.hiframes.pd_series_ext.get_series_data(S)
        jluw__wmy = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        lgoq__gkg = 0
        for chdp__htsvm in numba.parfors.parfor.internal_prange(len(isotd__ucm)
            ):
            shyz__gkbef = isotd__ucm[chdp__htsvm]
            dtw__glwf = jluw__wmy[chdp__htsvm]
            lgoq__gkg += shyz__gkbef * dtw__glwf
        return lgoq__gkg
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    qgyxy__ulcif = dict(skipna=skipna)
    zdov__fjtbx = dict(skipna=True)
    check_unsupported_args('Series.cumsum', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(skipna=skipna)
    zdov__fjtbx = dict(skipna=True)
    check_unsupported_args('Series.cumprod', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(skipna=skipna)
    zdov__fjtbx = dict(skipna=True)
    check_unsupported_args('Series.cummin', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(skipna=skipna)
    zdov__fjtbx = dict(skipna=True)
    check_unsupported_args('Series.cummax', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    zdov__fjtbx = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        aoo__dgs = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, aoo__dgs, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    qgyxy__ulcif = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    zdov__fjtbx = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(level=level)
    zdov__fjtbx = dict(level=None)
    check_unsupported_args('Series.count', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    qgyxy__ulcif = dict(method=method, min_periods=min_periods)
    zdov__fjtbx = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        kpcr__cqf = S.sum()
        ppf__aps = other.sum()
        a = n * (S * other).sum() - kpcr__cqf * ppf__aps
        svg__csvb = n * (S ** 2).sum() - kpcr__cqf ** 2
        voq__sun = n * (other ** 2).sum() - ppf__aps ** 2
        return a / np.sqrt(svg__csvb * voq__sun)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    qgyxy__ulcif = dict(min_periods=min_periods)
    zdov__fjtbx = dict(min_periods=None)
    check_unsupported_args('Series.cov', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        kpcr__cqf = S.mean()
        ppf__aps = other.mean()
        dct__ehbto = ((S - kpcr__cqf) * (other - ppf__aps)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(dct__ehbto, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            pygwf__btbu = np.sign(sum_val)
            return np.inf * pygwf__btbu
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    qgyxy__ulcif = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    zdov__fjtbx = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    zdov__fjtbx = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(axis=axis, skipna=skipna)
    zdov__fjtbx = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(axis=axis, skipna=skipna)
    zdov__fjtbx = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', qgyxy__ulcif, zdov__fjtbx,
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
    qgyxy__ulcif = dict(level=level, numeric_only=numeric_only)
    zdov__fjtbx = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', qgyxy__ulcif, zdov__fjtbx,
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
        znfm__cbt = arr[:n]
        ket__tdjpk = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(znfm__cbt,
            ket__tdjpk, name)
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
        uwrjy__yhpey = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        znfm__cbt = arr[uwrjy__yhpey:]
        ket__tdjpk = index[uwrjy__yhpey:]
        return bodo.hiframes.pd_series_ext.init_series(znfm__cbt,
            ket__tdjpk, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    jdg__lpapb = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in jdg__lpapb:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            jrd__petr = index[0]
            aie__cwzft = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, jrd__petr,
                False))
        else:
            aie__cwzft = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        znfm__cbt = arr[:aie__cwzft]
        ket__tdjpk = index[:aie__cwzft]
        return bodo.hiframes.pd_series_ext.init_series(znfm__cbt,
            ket__tdjpk, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    jdg__lpapb = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in jdg__lpapb:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            cqm__ueaaf = index[-1]
            aie__cwzft = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                cqm__ueaaf, True))
        else:
            aie__cwzft = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        znfm__cbt = arr[len(arr) - aie__cwzft:]
        ket__tdjpk = index[len(arr) - aie__cwzft:]
        return bodo.hiframes.pd_series_ext.init_series(znfm__cbt,
            ket__tdjpk, name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        bxoh__aasmj = bodo.utils.conversion.index_to_array(index)
        ess__ljt, cxq__ccy = bodo.libs.array_kernels.first_last_valid_index(arr
            , bxoh__aasmj)
        return cxq__ccy if ess__ljt else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        bxoh__aasmj = bodo.utils.conversion.index_to_array(index)
        ess__ljt, cxq__ccy = bodo.libs.array_kernels.first_last_valid_index(arr
            , bxoh__aasmj, False)
        return cxq__ccy if ess__ljt else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    qgyxy__ulcif = dict(keep=keep)
    zdov__fjtbx = dict(keep='first')
    check_unsupported_args('Series.nlargest', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        bxoh__aasmj = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nef__wtwj, dpab__sdjzp = bodo.libs.array_kernels.nlargest(arr,
            bxoh__aasmj, n, True, bodo.hiframes.series_kernels.gt_f)
        amst__eyayn = bodo.utils.conversion.convert_to_index(dpab__sdjzp)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
            amst__eyayn, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    qgyxy__ulcif = dict(keep=keep)
    zdov__fjtbx = dict(keep='first')
    check_unsupported_args('Series.nsmallest', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        bxoh__aasmj = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nef__wtwj, dpab__sdjzp = bodo.libs.array_kernels.nlargest(arr,
            bxoh__aasmj, n, False, bodo.hiframes.series_kernels.lt_f)
        amst__eyayn = bodo.utils.conversion.convert_to_index(dpab__sdjzp)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
            amst__eyayn, name)
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
    qgyxy__ulcif = dict(errors=errors)
    zdov__fjtbx = dict(errors='raise')
    check_unsupported_args('Series.astype', qgyxy__ulcif, zdov__fjtbx,
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
        nef__wtwj = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    qgyxy__ulcif = dict(axis=axis, is_copy=is_copy)
    zdov__fjtbx = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        dvv__nkiz = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[dvv__nkiz],
            index[dvv__nkiz], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    qgyxy__ulcif = dict(axis=axis, kind=kind, order=order)
    zdov__fjtbx = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        dbyx__rcx = S.notna().values
        if not dbyx__rcx.all():
            nef__wtwj = np.full(n, -1, np.int64)
            nef__wtwj[dbyx__rcx] = argsort(arr[dbyx__rcx])
        else:
            nef__wtwj = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    qgyxy__ulcif = dict(axis=axis, numeric_only=numeric_only)
    zdov__fjtbx = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', qgyxy__ulcif, zdov__fjtbx,
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
        nef__wtwj = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    qgyxy__ulcif = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    zdov__fjtbx = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    ipwm__art = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        cwqc__yxlxf = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ipwm__art)
        waz__qguug = cwqc__yxlxf.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        nef__wtwj = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            waz__qguug, 0)
        amst__eyayn = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            waz__qguug)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
            amst__eyayn, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    qgyxy__ulcif = dict(axis=axis, inplace=inplace, kind=kind, ignore_index
        =ignore_index, key=key)
    zdov__fjtbx = dict(axis=0, inplace=False, kind='quicksort',
        ignore_index=False, key=None)
    check_unsupported_args('Series.sort_values', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    snqk__mxdxw = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        cwqc__yxlxf = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, snqk__mxdxw)
        waz__qguug = cwqc__yxlxf.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        nef__wtwj = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            waz__qguug, 0)
        amst__eyayn = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            waz__qguug)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
            amst__eyayn, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    txj__nhmm = is_overload_true(is_nullable)
    ydlwu__zqqho = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    ydlwu__zqqho += '  numba.parfors.parfor.init_prange()\n'
    ydlwu__zqqho += '  n = len(arr)\n'
    if txj__nhmm:
        ydlwu__zqqho += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        ydlwu__zqqho += '  out_arr = np.empty(n, np.int64)\n'
    ydlwu__zqqho += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ydlwu__zqqho += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if txj__nhmm:
        ydlwu__zqqho += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        ydlwu__zqqho += '      out_arr[i] = -1\n'
    ydlwu__zqqho += '      continue\n'
    ydlwu__zqqho += '    val = arr[i]\n'
    ydlwu__zqqho += '    if include_lowest and val == bins[0]:\n'
    ydlwu__zqqho += '      ind = 1\n'
    ydlwu__zqqho += '    else:\n'
    ydlwu__zqqho += '      ind = np.searchsorted(bins, val)\n'
    ydlwu__zqqho += '    if ind == 0 or ind == len(bins):\n'
    if txj__nhmm:
        ydlwu__zqqho += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        ydlwu__zqqho += '      out_arr[i] = -1\n'
    ydlwu__zqqho += '    else:\n'
    ydlwu__zqqho += '      out_arr[i] = ind - 1\n'
    ydlwu__zqqho += '  return out_arr\n'
    opu__rfm = {}
    exec(ydlwu__zqqho, {'bodo': bodo, 'np': np, 'numba': numba}, opu__rfm)
    impl = opu__rfm['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        szz__wru, jbfn__agdqb = np.divmod(x, 1)
        if szz__wru == 0:
            hoo__ojog = -int(np.floor(np.log10(abs(jbfn__agdqb)))
                ) - 1 + precision
        else:
            hoo__ojog = precision
        return np.around(x, hoo__ojog)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        kqzxp__ato = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(kqzxp__ato)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        ckonm__rtlo = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            wwi__shrvm = bins.copy()
            if right and include_lowest:
                wwi__shrvm[0] = wwi__shrvm[0] - ckonm__rtlo
            vissc__ixex = bodo.libs.interval_arr_ext.init_interval_array(
                wwi__shrvm[:-1], wwi__shrvm[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(vissc__ixex,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        wwi__shrvm = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            wwi__shrvm[0] = wwi__shrvm[0] - 10.0 ** -precision
        vissc__ixex = bodo.libs.interval_arr_ext.init_interval_array(wwi__shrvm
            [:-1], wwi__shrvm[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(vissc__ixex, None
            )
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        lslj__xcet = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        mdkvf__faf = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        nef__wtwj = np.zeros(nbins, np.int64)
        for chdp__htsvm in range(len(lslj__xcet)):
            nef__wtwj[mdkvf__faf[chdp__htsvm]] = lslj__xcet[chdp__htsvm]
        return nef__wtwj
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
            ziwyy__yaqtk = (max_val - min_val) * 0.001
            if right:
                bins[0] -= ziwyy__yaqtk
            else:
                bins[-1] += ziwyy__yaqtk
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    qgyxy__ulcif = dict(dropna=dropna)
    zdov__fjtbx = dict(dropna=True)
    check_unsupported_args('Series.value_counts', qgyxy__ulcif, zdov__fjtbx,
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
    zhg__plwhn = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    ydlwu__zqqho = 'def impl(\n'
    ydlwu__zqqho += '    S,\n'
    ydlwu__zqqho += '    normalize=False,\n'
    ydlwu__zqqho += '    sort=True,\n'
    ydlwu__zqqho += '    ascending=False,\n'
    ydlwu__zqqho += '    bins=None,\n'
    ydlwu__zqqho += '    dropna=True,\n'
    ydlwu__zqqho += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    ydlwu__zqqho += '):\n'
    ydlwu__zqqho += (
        '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ydlwu__zqqho += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ydlwu__zqqho += (
        '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if zhg__plwhn:
        ydlwu__zqqho += '    right = True\n'
        ydlwu__zqqho += _gen_bins_handling(bins, S.dtype)
        ydlwu__zqqho += '    arr = get_bin_inds(bins, arr)\n'
    ydlwu__zqqho += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    ydlwu__zqqho += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    ydlwu__zqqho += '    )\n'
    ydlwu__zqqho += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if zhg__plwhn:
        ydlwu__zqqho += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        ydlwu__zqqho += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        ydlwu__zqqho += '    index = get_bin_labels(bins)\n'
    else:
        ydlwu__zqqho += """    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)
"""
        ydlwu__zqqho += (
            '    ind_arr = bodo.utils.conversion.coerce_to_array(\n')
        ydlwu__zqqho += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        ydlwu__zqqho += '    )\n'
        ydlwu__zqqho += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    ydlwu__zqqho += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        ydlwu__zqqho += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        ccfzv__ysjd = 'len(S)' if zhg__plwhn else 'count_arr.sum()'
        ydlwu__zqqho += f'    res = res / float({ccfzv__ysjd})\n'
    ydlwu__zqqho += '    return res\n'
    opu__rfm = {}
    exec(ydlwu__zqqho, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, opu__rfm)
    impl = opu__rfm['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    ydlwu__zqqho = ''
    if isinstance(bins, types.Integer):
        ydlwu__zqqho += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        ydlwu__zqqho += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            ydlwu__zqqho += '    min_val = min_val.value\n'
            ydlwu__zqqho += '    max_val = max_val.value\n'
        ydlwu__zqqho += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            ydlwu__zqqho += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        ydlwu__zqqho += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return ydlwu__zqqho


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    qgyxy__ulcif = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    zdov__fjtbx = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    ydlwu__zqqho = 'def impl(\n'
    ydlwu__zqqho += '    x,\n'
    ydlwu__zqqho += '    bins,\n'
    ydlwu__zqqho += '    right=True,\n'
    ydlwu__zqqho += '    labels=None,\n'
    ydlwu__zqqho += '    retbins=False,\n'
    ydlwu__zqqho += '    precision=3,\n'
    ydlwu__zqqho += '    include_lowest=False,\n'
    ydlwu__zqqho += "    duplicates='raise',\n"
    ydlwu__zqqho += '    ordered=True\n'
    ydlwu__zqqho += '):\n'
    if isinstance(x, SeriesType):
        ydlwu__zqqho += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        ydlwu__zqqho += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        ydlwu__zqqho += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        ydlwu__zqqho += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    ydlwu__zqqho += _gen_bins_handling(bins, x.dtype)
    ydlwu__zqqho += (
        '    arr = get_bin_inds(bins, arr, False, include_lowest)\n')
    ydlwu__zqqho += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    ydlwu__zqqho += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    ydlwu__zqqho += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        ydlwu__zqqho += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        ydlwu__zqqho += '    return res\n'
    else:
        ydlwu__zqqho += '    return out_arr\n'
    opu__rfm = {}
    exec(ydlwu__zqqho, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, opu__rfm)
    impl = opu__rfm['impl']
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
    qgyxy__ulcif = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    zdov__fjtbx = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        fcng__kvlm = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, fcng__kvlm)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    qgyxy__ulcif = dict(axis=axis, sort=sort, group_keys=group_keys,
        squeeze=squeeze, observed=observed, dropna=dropna)
    zdov__fjtbx = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', qgyxy__ulcif, zdov__fjtbx,
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
        pzywu__nng = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            fat__qod = bodo.utils.conversion.coerce_to_array(index)
            cwqc__yxlxf = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                fat__qod, arr), index, pzywu__nng)
            return cwqc__yxlxf.groupby(' ')['']
        return impl_index
    gvjo__sezw = by
    if isinstance(by, SeriesType):
        gvjo__sezw = by.data
    if isinstance(gvjo__sezw, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    bfqa__pztf = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        fat__qod = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        cwqc__yxlxf = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            fat__qod, arr), index, bfqa__pztf)
        return cwqc__yxlxf.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    qgyxy__ulcif = dict(verify_integrity=verify_integrity)
    zdov__fjtbx = dict(verify_integrity=False)
    check_unsupported_args('Series.append', qgyxy__ulcif, zdov__fjtbx,
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
            sasyc__xrcxl = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            nef__wtwj = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(nef__wtwj, A, sasyc__xrcxl, False)
            return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index,
                name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nef__wtwj = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    qgyxy__ulcif = dict(interpolation=interpolation)
    zdov__fjtbx = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            nef__wtwj = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index,
                name)
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
        yto__sam = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(yto__sam, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    qgyxy__ulcif = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    zdov__fjtbx = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', qgyxy__ulcif, zdov__fjtbx,
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
        fokud__ybaqk = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        fokud__ybaqk = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    ydlwu__zqqho = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {fokud__ybaqk}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    qahg__vupcf = dict()
    exec(ydlwu__zqqho, {'bodo': bodo, 'numba': numba}, qahg__vupcf)
    myey__xer = qahg__vupcf['impl']
    return myey__xer


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        fokud__ybaqk = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        fokud__ybaqk = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    ydlwu__zqqho = 'def impl(S,\n'
    ydlwu__zqqho += '     value=None,\n'
    ydlwu__zqqho += '    method=None,\n'
    ydlwu__zqqho += '    axis=None,\n'
    ydlwu__zqqho += '    inplace=False,\n'
    ydlwu__zqqho += '    limit=None,\n'
    ydlwu__zqqho += '   downcast=None,\n'
    ydlwu__zqqho += '):\n'
    ydlwu__zqqho += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ydlwu__zqqho += '    n = len(in_arr)\n'
    ydlwu__zqqho += f'    out_arr = {fokud__ybaqk}(n, -1)\n'
    ydlwu__zqqho += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    ydlwu__zqqho += '        s = in_arr[j]\n'
    ydlwu__zqqho += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    ydlwu__zqqho += '            s = value\n'
    ydlwu__zqqho += '        out_arr[j] = s\n'
    ydlwu__zqqho += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    qahg__vupcf = dict()
    exec(ydlwu__zqqho, {'bodo': bodo, 'numba': numba}, qahg__vupcf)
    myey__xer = qahg__vupcf['impl']
    return myey__xer


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
    xzne__ghcmw = bodo.hiframes.pd_series_ext.get_series_data(value)
    for chdp__htsvm in numba.parfors.parfor.internal_prange(len(yibac__usb)):
        s = yibac__usb[chdp__htsvm]
        if bodo.libs.array_kernels.isna(yibac__usb, chdp__htsvm
            ) and not bodo.libs.array_kernels.isna(xzne__ghcmw, chdp__htsvm):
            s = xzne__ghcmw[chdp__htsvm]
        yibac__usb[chdp__htsvm] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
    for chdp__htsvm in numba.parfors.parfor.internal_prange(len(yibac__usb)):
        s = yibac__usb[chdp__htsvm]
        if bodo.libs.array_kernels.isna(yibac__usb, chdp__htsvm):
            s = value
        yibac__usb[chdp__htsvm] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    xzne__ghcmw = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(yibac__usb)
    nef__wtwj = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for uad__nvmgd in numba.parfors.parfor.internal_prange(n):
        s = yibac__usb[uad__nvmgd]
        if bodo.libs.array_kernels.isna(yibac__usb, uad__nvmgd
            ) and not bodo.libs.array_kernels.isna(xzne__ghcmw, uad__nvmgd):
            s = xzne__ghcmw[uad__nvmgd]
        nef__wtwj[uad__nvmgd] = s
        if bodo.libs.array_kernels.isna(yibac__usb, uad__nvmgd
            ) and bodo.libs.array_kernels.isna(xzne__ghcmw, uad__nvmgd):
            bodo.libs.array_kernels.setna(nef__wtwj, uad__nvmgd)
    return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    xzne__ghcmw = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(yibac__usb)
    nef__wtwj = bodo.utils.utils.alloc_type(n, yibac__usb.dtype, (-1,))
    for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
        s = yibac__usb[chdp__htsvm]
        if bodo.libs.array_kernels.isna(yibac__usb, chdp__htsvm
            ) and not bodo.libs.array_kernels.isna(xzne__ghcmw, chdp__htsvm):
            s = xzne__ghcmw[chdp__htsvm]
        nef__wtwj[chdp__htsvm] = s
    return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    qgyxy__ulcif = dict(limit=limit, downcast=downcast)
    zdov__fjtbx = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', qgyxy__ulcif, zdov__fjtbx,
        package_name='pandas', module_name='Series')
    gcae__uwp = not is_overload_none(value)
    tln__rwrh = not is_overload_none(method)
    if gcae__uwp and tln__rwrh:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not gcae__uwp and not tln__rwrh:
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
    if tln__rwrh:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        paae__vohm = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(paae__vohm)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(paae__vohm)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    obzn__ubman = element_type(S.data)
    roe__fhzo = None
    if gcae__uwp:
        roe__fhzo = element_type(types.unliteral(value))
    if roe__fhzo and not can_replace(obzn__ubman, roe__fhzo):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {roe__fhzo} with series type {obzn__ubman}'
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
        pko__thd = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                xzne__ghcmw = bodo.hiframes.pd_series_ext.get_series_data(value
                    )
                n = len(yibac__usb)
                nef__wtwj = bodo.utils.utils.alloc_type(n, pko__thd, (-1,))
                for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(yibac__usb, chdp__htsvm
                        ) and bodo.libs.array_kernels.isna(xzne__ghcmw,
                        chdp__htsvm):
                        bodo.libs.array_kernels.setna(nef__wtwj, chdp__htsvm)
                        continue
                    if bodo.libs.array_kernels.isna(yibac__usb, chdp__htsvm):
                        nef__wtwj[chdp__htsvm
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            xzne__ghcmw[chdp__htsvm])
                        continue
                    nef__wtwj[chdp__htsvm
                        ] = bodo.utils.conversion.unbox_if_timestamp(yibac__usb
                        [chdp__htsvm])
                return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                    index, name)
            return fillna_series_impl
        if tln__rwrh:
            ehvbm__xqnv = (types.unicode_type, types.bool_, bodo.
                datetime64ns, bodo.timedelta64ns)
            if not isinstance(obzn__ubman, (types.Integer, types.Float)
                ) and obzn__ubman not in ehvbm__xqnv:
                raise BodoError(
                    f"Series.fillna(): series of type {obzn__ubman} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                nef__wtwj = bodo.libs.array_kernels.ffill_bfill_arr(yibac__usb,
                    method)
                return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(yibac__usb)
            nef__wtwj = bodo.utils.utils.alloc_type(n, pko__thd, (-1,))
            for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(yibac__usb[
                    chdp__htsvm])
                if bodo.libs.array_kernels.isna(yibac__usb, chdp__htsvm):
                    s = value
                nef__wtwj[chdp__htsvm] = s
            return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index,
                name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        lhadk__uwu = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        qgyxy__ulcif = dict(limit=limit, downcast=downcast)
        zdov__fjtbx = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', qgyxy__ulcif,
            zdov__fjtbx, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        obzn__ubman = element_type(S.data)
        ehvbm__xqnv = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(obzn__ubman, (types.Integer, types.Float)
            ) and obzn__ubman not in ehvbm__xqnv:
            raise BodoError(
                f'Series.{overload_name}(): series of type {obzn__ubman} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            nef__wtwj = bodo.libs.array_kernels.ffill_bfill_arr(yibac__usb,
                lhadk__uwu)
            return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index,
                name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        tec__nxk = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(tec__nxk)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        bxu__ocx = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(bxu__ocx)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        bxu__ocx = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(bxu__ocx)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        bxu__ocx = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(bxu__ocx)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    qgyxy__ulcif = dict(inplace=inplace, limit=limit, regex=regex, method=
        method)
    jnhzj__eyxy = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', qgyxy__ulcif, jnhzj__eyxy,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    obzn__ubman = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        agwm__txo = element_type(to_replace.key_type)
        roe__fhzo = element_type(to_replace.value_type)
    else:
        agwm__txo = element_type(to_replace)
        roe__fhzo = element_type(value)
    igqv__zhzq = None
    if obzn__ubman != types.unliteral(agwm__txo):
        if bodo.utils.typing.equality_always_false(obzn__ubman, types.
            unliteral(agwm__txo)
            ) or not bodo.utils.typing.types_equality_exists(obzn__ubman,
            agwm__txo):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(obzn__ubman, (types.Float, types.Integer)
            ) or obzn__ubman == np.bool_:
            igqv__zhzq = obzn__ubman
    if not can_replace(obzn__ubman, types.unliteral(roe__fhzo)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    rat__gaqbw = to_str_arr_if_dict_array(S.data)
    if isinstance(rat__gaqbw, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(yibac__usb.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(yibac__usb)
        nef__wtwj = bodo.utils.utils.alloc_type(n, rat__gaqbw, (-1,))
        zqis__nljj = build_replace_dict(to_replace, value, igqv__zhzq)
        for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(yibac__usb, chdp__htsvm):
                bodo.libs.array_kernels.setna(nef__wtwj, chdp__htsvm)
                continue
            s = yibac__usb[chdp__htsvm]
            if s in zqis__nljj:
                s = zqis__nljj[s]
            nef__wtwj[chdp__htsvm] = s
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    uuxe__jre = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    cxqz__iitdb = is_iterable_type(to_replace)
    bafc__ekhpa = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    eow__wcmk = is_iterable_type(value)
    if uuxe__jre and bafc__ekhpa:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                zqis__nljj = {}
                zqis__nljj[key_dtype_conv(to_replace)] = value
                return zqis__nljj
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            zqis__nljj = {}
            zqis__nljj[to_replace] = value
            return zqis__nljj
        return impl
    if cxqz__iitdb and bafc__ekhpa:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                zqis__nljj = {}
                for wdjeq__flue in to_replace:
                    zqis__nljj[key_dtype_conv(wdjeq__flue)] = value
                return zqis__nljj
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            zqis__nljj = {}
            for wdjeq__flue in to_replace:
                zqis__nljj[wdjeq__flue] = value
            return zqis__nljj
        return impl
    if cxqz__iitdb and eow__wcmk:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                zqis__nljj = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for chdp__htsvm in range(len(to_replace)):
                    zqis__nljj[key_dtype_conv(to_replace[chdp__htsvm])
                        ] = value[chdp__htsvm]
                return zqis__nljj
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            zqis__nljj = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for chdp__htsvm in range(len(to_replace)):
                zqis__nljj[to_replace[chdp__htsvm]] = value[chdp__htsvm]
            return zqis__nljj
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
            nef__wtwj = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index,
                name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nef__wtwj = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    qgyxy__ulcif = dict(ignore_index=ignore_index)
    buja__bhs = dict(ignore_index=False)
    check_unsupported_args('Series.explode', qgyxy__ulcif, buja__bhs,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        bxoh__aasmj = bodo.utils.conversion.index_to_array(index)
        nef__wtwj, inlea__rlkoo = bodo.libs.array_kernels.explode(arr,
            bxoh__aasmj)
        amst__eyayn = bodo.utils.conversion.index_from_array(inlea__rlkoo)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
            amst__eyayn, name)
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
            dehhp__gwin = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
                dehhp__gwin[chdp__htsvm] = np.argmax(a[chdp__htsvm])
            return dehhp__gwin
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            hayvb__rjt = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
                hayvb__rjt[chdp__htsvm] = np.argmin(a[chdp__htsvm])
            return hayvb__rjt
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
    qgyxy__ulcif = dict(axis=axis, inplace=inplace, how=how)
    jyxg__wai = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', qgyxy__ulcif, jyxg__wai,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            dbyx__rcx = S.notna().values
            bxoh__aasmj = bodo.utils.conversion.extract_index_array(S)
            amst__eyayn = bodo.utils.conversion.convert_to_index(bxoh__aasmj
                [dbyx__rcx])
            nef__wtwj = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(yibac__usb))
            return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                amst__eyayn, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            bxoh__aasmj = bodo.utils.conversion.extract_index_array(S)
            dbyx__rcx = S.notna().values
            amst__eyayn = bodo.utils.conversion.convert_to_index(bxoh__aasmj
                [dbyx__rcx])
            nef__wtwj = yibac__usb[dbyx__rcx]
            return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                amst__eyayn, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    qgyxy__ulcif = dict(freq=freq, axis=axis, fill_value=fill_value)
    zdov__fjtbx = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', qgyxy__ulcif, zdov__fjtbx,
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
        nef__wtwj = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    qgyxy__ulcif = dict(fill_method=fill_method, limit=limit, freq=freq)
    zdov__fjtbx = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', qgyxy__ulcif, zdov__fjtbx,
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
        nef__wtwj = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
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
            aax__szb = 'None'
        else:
            aax__szb = 'other'
        ydlwu__zqqho = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            ydlwu__zqqho += '  cond = ~cond\n'
        ydlwu__zqqho += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ydlwu__zqqho += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ydlwu__zqqho += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ydlwu__zqqho += (
            f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {aax__szb})\n'
            )
        ydlwu__zqqho += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        opu__rfm = {}
        exec(ydlwu__zqqho, {'bodo': bodo, 'np': np}, opu__rfm)
        impl = opu__rfm['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        tec__nxk = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(tec__nxk)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    qgyxy__ulcif = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    zdov__fjtbx = dict(inplace=False, level=None, errors='raise', try_cast=
        False)
    check_unsupported_args(f'{func_name}', qgyxy__ulcif, zdov__fjtbx,
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
    jcde__qxwib = is_overload_constant_nan(other)
    if not (is_default or jcde__qxwib or is_scalar_type(other) or 
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
            bnxf__dvzez = arr.dtype.elem_type
        else:
            bnxf__dvzez = arr.dtype
        if is_iterable_type(other):
            tpdq__zoyoy = other.dtype
        elif jcde__qxwib:
            tpdq__zoyoy = types.float64
        else:
            tpdq__zoyoy = types.unliteral(other)
        if not jcde__qxwib and not is_common_scalar_dtype([bnxf__dvzez,
            tpdq__zoyoy]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        qgyxy__ulcif = dict(level=level, axis=axis)
        zdov__fjtbx = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__),
            qgyxy__ulcif, zdov__fjtbx, package_name='pandas', module_name=
            'Series')
        qlz__tno = other == string_type or is_overload_constant_str(other)
        wse__vhyyq = is_iterable_type(other) and other.dtype == string_type
        kldm__revx = S.dtype == string_type and (op == operator.add and (
            qlz__tno or wse__vhyyq) or op == operator.mul and isinstance(
            other, types.Integer))
        oyhh__zdsf = S.dtype == bodo.timedelta64ns
        giqq__iofxa = S.dtype == bodo.datetime64ns
        htwj__ajcv = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        yxt__ndj = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        gkx__bbg = oyhh__zdsf and (htwj__ajcv or yxt__ndj
            ) or giqq__iofxa and htwj__ajcv
        gkx__bbg = gkx__bbg and op == operator.add
        if not (isinstance(S.dtype, types.Number) or kldm__revx or gkx__bbg):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        fwjxp__vco = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            rat__gaqbw = fwjxp__vco.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and rat__gaqbw == types.Array(types.bool_, 1, 'C'):
                rat__gaqbw = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                nef__wtwj = bodo.utils.utils.alloc_type(n, rat__gaqbw, (-1,))
                for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
                    cfoga__ifgmn = bodo.libs.array_kernels.isna(arr,
                        chdp__htsvm)
                    if cfoga__ifgmn:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(nef__wtwj,
                                chdp__htsvm)
                        else:
                            nef__wtwj[chdp__htsvm] = op(fill_value, other)
                    else:
                        nef__wtwj[chdp__htsvm] = op(arr[chdp__htsvm], other)
                return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        rat__gaqbw = fwjxp__vco.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and rat__gaqbw == types.Array(
            types.bool_, 1, 'C'):
            rat__gaqbw = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            ojb__xbacy = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            nef__wtwj = bodo.utils.utils.alloc_type(n, rat__gaqbw, (-1,))
            for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
                cfoga__ifgmn = bodo.libs.array_kernels.isna(arr, chdp__htsvm)
                yuzs__huk = bodo.libs.array_kernels.isna(ojb__xbacy,
                    chdp__htsvm)
                if cfoga__ifgmn and yuzs__huk:
                    bodo.libs.array_kernels.setna(nef__wtwj, chdp__htsvm)
                elif cfoga__ifgmn:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nef__wtwj, chdp__htsvm)
                    else:
                        nef__wtwj[chdp__htsvm] = op(fill_value, ojb__xbacy[
                            chdp__htsvm])
                elif yuzs__huk:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nef__wtwj, chdp__htsvm)
                    else:
                        nef__wtwj[chdp__htsvm] = op(arr[chdp__htsvm],
                            fill_value)
                else:
                    nef__wtwj[chdp__htsvm] = op(arr[chdp__htsvm],
                        ojb__xbacy[chdp__htsvm])
            return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index,
                name)
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
        fwjxp__vco = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            rat__gaqbw = fwjxp__vco.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and rat__gaqbw == types.Array(types.bool_, 1, 'C'):
                rat__gaqbw = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                nef__wtwj = bodo.utils.utils.alloc_type(n, rat__gaqbw, None)
                for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
                    cfoga__ifgmn = bodo.libs.array_kernels.isna(arr,
                        chdp__htsvm)
                    if cfoga__ifgmn:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(nef__wtwj,
                                chdp__htsvm)
                        else:
                            nef__wtwj[chdp__htsvm] = op(other, fill_value)
                    else:
                        nef__wtwj[chdp__htsvm] = op(other, arr[chdp__htsvm])
                return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        rat__gaqbw = fwjxp__vco.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and rat__gaqbw == types.Array(
            types.bool_, 1, 'C'):
            rat__gaqbw = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            ojb__xbacy = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            nef__wtwj = bodo.utils.utils.alloc_type(n, rat__gaqbw, None)
            for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
                cfoga__ifgmn = bodo.libs.array_kernels.isna(arr, chdp__htsvm)
                yuzs__huk = bodo.libs.array_kernels.isna(ojb__xbacy,
                    chdp__htsvm)
                nef__wtwj[chdp__htsvm] = op(ojb__xbacy[chdp__htsvm], arr[
                    chdp__htsvm])
                if cfoga__ifgmn and yuzs__huk:
                    bodo.libs.array_kernels.setna(nef__wtwj, chdp__htsvm)
                elif cfoga__ifgmn:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nef__wtwj, chdp__htsvm)
                    else:
                        nef__wtwj[chdp__htsvm] = op(ojb__xbacy[chdp__htsvm],
                            fill_value)
                elif yuzs__huk:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nef__wtwj, chdp__htsvm)
                    else:
                        nef__wtwj[chdp__htsvm] = op(fill_value, arr[
                            chdp__htsvm])
                else:
                    nef__wtwj[chdp__htsvm] = op(ojb__xbacy[chdp__htsvm],
                        arr[chdp__htsvm])
            return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index,
                name)
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
    for op, iignd__mjyh in explicit_binop_funcs_two_ways.items():
        for name in iignd__mjyh:
            tec__nxk = create_explicit_binary_op_overload(op)
            bej__sjy = create_explicit_binary_reverse_op_overload(op)
            lomi__bvuph = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(tec__nxk)
            overload_method(SeriesType, lomi__bvuph, no_unliteral=True)(
                bej__sjy)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        tec__nxk = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(tec__nxk)
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
                oijs__pfd = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                nef__wtwj = dt64_arr_sub(arr, oijs__pfd)
                return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
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
                nef__wtwj = np.empty(n, np.dtype('datetime64[ns]'))
                for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, chdp__htsvm):
                        bodo.libs.array_kernels.setna(nef__wtwj, chdp__htsvm)
                        continue
                    ioz__itgr = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[chdp__htsvm]))
                    sdom__xujhe = op(ioz__itgr, rhs)
                    nef__wtwj[chdp__htsvm
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        sdom__xujhe.value)
                return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
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
                    oijs__pfd = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    nef__wtwj = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(oijs__pfd))
                    return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                oijs__pfd = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                nef__wtwj = op(arr, oijs__pfd)
                return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    hpqao__gpmqq = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    nef__wtwj = op(bodo.utils.conversion.unbox_if_timestamp
                        (hpqao__gpmqq), arr)
                    return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                hpqao__gpmqq = (bodo.utils.conversion.
                    get_array_if_series_or_index(lhs))
                nef__wtwj = op(hpqao__gpmqq, arr)
                return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        tec__nxk = create_binary_op_overload(op)
        overload(op)(tec__nxk)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    fmqyy__nty = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, fmqyy__nty)
        for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, chdp__htsvm
                ) or bodo.libs.array_kernels.isna(arg2, chdp__htsvm):
                bodo.libs.array_kernels.setna(S, chdp__htsvm)
                continue
            S[chdp__htsvm
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                chdp__htsvm]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[chdp__htsvm]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                ojb__xbacy = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, ojb__xbacy)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        tec__nxk = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(tec__nxk)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                nef__wtwj = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        tec__nxk = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(tec__nxk)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    nef__wtwj = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
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
                    ojb__xbacy = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    nef__wtwj = ufunc(arr, ojb__xbacy)
                    return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    ojb__xbacy = bodo.hiframes.pd_series_ext.get_series_data(S2
                        )
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    nef__wtwj = ufunc(arr, ojb__xbacy)
                    return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        tec__nxk = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(tec__nxk)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        oyy__mxsw = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),))
        sol__fyzq = np.arange(n),
        bodo.libs.timsort.sort(oyy__mxsw, 0, n, sol__fyzq)
        return sol__fyzq[0]
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
        gqril__rmwes = get_overload_const_str(downcast)
        if gqril__rmwes in ('integer', 'signed'):
            out_dtype = types.int64
        elif gqril__rmwes == 'unsigned':
            out_dtype = types.uint64
        else:
            assert gqril__rmwes == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            yibac__usb = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            nef__wtwj = pd.to_numeric(yibac__usb, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index,
                name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            dzg__psxxy = np.empty(n, np.float64)
            for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, chdp__htsvm):
                    bodo.libs.array_kernels.setna(dzg__psxxy, chdp__htsvm)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(dzg__psxxy,
                        chdp__htsvm, arg_a, chdp__htsvm)
            return dzg__psxxy
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            dzg__psxxy = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, chdp__htsvm):
                    bodo.libs.array_kernels.setna(dzg__psxxy, chdp__htsvm)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(dzg__psxxy,
                        chdp__htsvm, arg_a, chdp__htsvm)
            return dzg__psxxy
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        ebj__jjeb = if_series_to_array_type(args[0])
        if isinstance(ebj__jjeb, types.Array) and isinstance(ebj__jjeb.
            dtype, types.Integer):
            ebj__jjeb = types.Array(types.float64, 1, 'C')
        return ebj__jjeb(*args)


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
    zehs__gfkvr = bodo.utils.utils.is_array_typ(x, True)
    qoq__flk = bodo.utils.utils.is_array_typ(y, True)
    ydlwu__zqqho = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        ydlwu__zqqho += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if zehs__gfkvr and not bodo.utils.utils.is_array_typ(x, False):
        ydlwu__zqqho += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if qoq__flk and not bodo.utils.utils.is_array_typ(y, False):
        ydlwu__zqqho += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    ydlwu__zqqho += '  n = len(condition)\n'
    igfmy__yisor = x.dtype if zehs__gfkvr else types.unliteral(x)
    wnsbn__xyaip = y.dtype if qoq__flk else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        igfmy__yisor = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        wnsbn__xyaip = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    rvho__okn = get_data(x)
    cawt__kcul = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(sol__fyzq) for
        sol__fyzq in [rvho__okn, cawt__kcul])
    if cawt__kcul == types.none:
        if isinstance(igfmy__yisor, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif rvho__okn == cawt__kcul and not is_nullable:
        out_dtype = dtype_to_array_type(igfmy__yisor)
    elif igfmy__yisor == string_type or wnsbn__xyaip == string_type:
        out_dtype = bodo.string_array_type
    elif rvho__okn == bytes_type or (zehs__gfkvr and igfmy__yisor == bytes_type
        ) and (cawt__kcul == bytes_type or qoq__flk and wnsbn__xyaip ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(igfmy__yisor, bodo.PDCategoricalDtype):
        out_dtype = None
    elif igfmy__yisor in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(igfmy__yisor, 1, 'C')
    elif wnsbn__xyaip in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(wnsbn__xyaip, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(igfmy__yisor), numba.np.numpy_support.
            as_dtype(wnsbn__xyaip)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(igfmy__yisor, bodo.PDCategoricalDtype):
        jjx__yhyo = 'x'
    else:
        jjx__yhyo = 'out_dtype'
    ydlwu__zqqho += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {jjx__yhyo}, (-1,))\n')
    if isinstance(igfmy__yisor, bodo.PDCategoricalDtype):
        ydlwu__zqqho += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        ydlwu__zqqho += """  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)
"""
    ydlwu__zqqho += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    ydlwu__zqqho += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if zehs__gfkvr:
        ydlwu__zqqho += '      if bodo.libs.array_kernels.isna(x, j):\n'
        ydlwu__zqqho += '        setna(out_arr, j)\n'
        ydlwu__zqqho += '        continue\n'
    if isinstance(igfmy__yisor, bodo.PDCategoricalDtype):
        ydlwu__zqqho += '      out_codes[j] = x_codes[j]\n'
    else:
        ydlwu__zqqho += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if zehs__gfkvr else 'x'))
    ydlwu__zqqho += '    else:\n'
    if qoq__flk:
        ydlwu__zqqho += '      if bodo.libs.array_kernels.isna(y, j):\n'
        ydlwu__zqqho += '        setna(out_arr, j)\n'
        ydlwu__zqqho += '        continue\n'
    if cawt__kcul == types.none:
        if isinstance(igfmy__yisor, bodo.PDCategoricalDtype):
            ydlwu__zqqho += '      out_codes[j] = -1\n'
        else:
            ydlwu__zqqho += '      setna(out_arr, j)\n'
    else:
        ydlwu__zqqho += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if qoq__flk else 'y'))
    ydlwu__zqqho += '  return out_arr\n'
    opu__rfm = {}
    exec(ydlwu__zqqho, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, opu__rfm)
    nvg__okjpa = opu__rfm['_impl']
    return nvg__okjpa


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
        leu__jjl = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(leu__jjl, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(leu__jjl):
            iagn__qla = leu__jjl.data.dtype
        else:
            iagn__qla = leu__jjl.dtype
        if isinstance(iagn__qla, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        qqf__tkwur = leu__jjl
    else:
        qpe__unrku = []
        for leu__jjl in choicelist:
            if not bodo.utils.utils.is_array_typ(leu__jjl, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(leu__jjl):
                iagn__qla = leu__jjl.data.dtype
            else:
                iagn__qla = leu__jjl.dtype
            if isinstance(iagn__qla, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            qpe__unrku.append(iagn__qla)
        if not is_common_scalar_dtype(qpe__unrku):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        qqf__tkwur = choicelist[0]
    if is_series_type(qqf__tkwur):
        qqf__tkwur = qqf__tkwur.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, qqf__tkwur.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(qqf__tkwur, types.Array) or isinstance(qqf__tkwur,
        BooleanArrayType) or isinstance(qqf__tkwur, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(qqf__tkwur, False) and qqf__tkwur.
        dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {qqf__tkwur} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    bzbw__erxn = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        mcsuk__vnmh = choicelist.dtype
    else:
        jqcky__ifcbh = False
        qpe__unrku = []
        for leu__jjl in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(leu__jjl,
                'numpy.select()')
            if is_nullable_type(leu__jjl):
                jqcky__ifcbh = True
            if is_series_type(leu__jjl):
                iagn__qla = leu__jjl.data.dtype
            else:
                iagn__qla = leu__jjl.dtype
            if isinstance(iagn__qla, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            qpe__unrku.append(iagn__qla)
        buwya__klg, edfh__pis = get_common_scalar_dtype(qpe__unrku)
        if not edfh__pis:
            raise BodoError('Internal error in overload_np_select')
        czto__utre = dtype_to_array_type(buwya__klg)
        if jqcky__ifcbh:
            czto__utre = to_nullable_type(czto__utre)
        mcsuk__vnmh = czto__utre
    if isinstance(mcsuk__vnmh, SeriesType):
        mcsuk__vnmh = mcsuk__vnmh.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        phvpc__affc = True
    else:
        phvpc__affc = False
    yoi__gil = False
    nmpf__wcsj = False
    if phvpc__affc:
        if isinstance(mcsuk__vnmh.dtype, types.Number):
            pass
        elif mcsuk__vnmh.dtype == types.bool_:
            nmpf__wcsj = True
        else:
            yoi__gil = True
            mcsuk__vnmh = to_nullable_type(mcsuk__vnmh)
    elif default == types.none or is_overload_constant_nan(default):
        yoi__gil = True
        mcsuk__vnmh = to_nullable_type(mcsuk__vnmh)
    ydlwu__zqqho = 'def np_select_impl(condlist, choicelist, default=0):\n'
    ydlwu__zqqho += '  if len(condlist) != len(choicelist):\n'
    ydlwu__zqqho += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    ydlwu__zqqho += '  output_len = len(choicelist[0])\n'
    ydlwu__zqqho += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    ydlwu__zqqho += '  for i in range(output_len):\n'
    if yoi__gil:
        ydlwu__zqqho += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif nmpf__wcsj:
        ydlwu__zqqho += '    out[i] = False\n'
    else:
        ydlwu__zqqho += '    out[i] = default\n'
    if bzbw__erxn:
        ydlwu__zqqho += '  for i in range(len(condlist) - 1, -1, -1):\n'
        ydlwu__zqqho += '    cond = condlist[i]\n'
        ydlwu__zqqho += '    choice = choicelist[i]\n'
        ydlwu__zqqho += '    out = np.where(cond, choice, out)\n'
    else:
        for chdp__htsvm in range(len(choicelist) - 1, -1, -1):
            ydlwu__zqqho += f'  cond = condlist[{chdp__htsvm}]\n'
            ydlwu__zqqho += f'  choice = choicelist[{chdp__htsvm}]\n'
            ydlwu__zqqho += f'  out = np.where(cond, choice, out)\n'
    ydlwu__zqqho += '  return out'
    opu__rfm = dict()
    exec(ydlwu__zqqho, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': mcsuk__vnmh}, opu__rfm)
    impl = opu__rfm['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nef__wtwj = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    qgyxy__ulcif = dict(subset=subset, keep=keep, inplace=inplace)
    zdov__fjtbx = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', qgyxy__ulcif,
        zdov__fjtbx, package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        awf__xzdwm = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (awf__xzdwm,), bxoh__aasmj = bodo.libs.array_kernels.drop_duplicates((
            awf__xzdwm,), index, 1)
        index = bodo.utils.conversion.index_from_array(bxoh__aasmj)
        return bodo.hiframes.pd_series_ext.init_series(awf__xzdwm, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    kraa__acopl = element_type(S.data)
    if not is_common_scalar_dtype([kraa__acopl, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([kraa__acopl, right]):
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
        nef__wtwj = np.empty(n, np.bool_)
        for chdp__htsvm in numba.parfors.parfor.internal_prange(n):
            mwioj__dkuw = bodo.utils.conversion.box_if_dt64(arr[chdp__htsvm])
            if inclusive == 'both':
                nef__wtwj[chdp__htsvm
                    ] = mwioj__dkuw <= right and mwioj__dkuw >= left
            else:
                nef__wtwj[chdp__htsvm
                    ] = mwioj__dkuw < right and mwioj__dkuw > left
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    qgyxy__ulcif = dict(axis=axis)
    zdov__fjtbx = dict(axis=None)
    check_unsupported_args('Series.repeat', qgyxy__ulcif, zdov__fjtbx,
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
            bxoh__aasmj = bodo.utils.conversion.index_to_array(index)
            nef__wtwj = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            inlea__rlkoo = bodo.libs.array_kernels.repeat_kernel(bxoh__aasmj,
                repeats)
            amst__eyayn = bodo.utils.conversion.index_from_array(inlea__rlkoo)
            return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
                amst__eyayn, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        bxoh__aasmj = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        nef__wtwj = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        inlea__rlkoo = bodo.libs.array_kernels.repeat_kernel(bxoh__aasmj,
            repeats)
        amst__eyayn = bodo.utils.conversion.index_from_array(inlea__rlkoo)
        return bodo.hiframes.pd_series_ext.init_series(nef__wtwj,
            amst__eyayn, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        sol__fyzq = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(sol__fyzq)
        gjzdy__txja = {}
        for chdp__htsvm in range(n):
            mwioj__dkuw = bodo.utils.conversion.box_if_dt64(sol__fyzq[
                chdp__htsvm])
            gjzdy__txja[index[chdp__htsvm]] = mwioj__dkuw
        return gjzdy__txja
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    paae__vohm = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            eaz__qzdqx = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(paae__vohm)
    elif is_literal_type(name):
        eaz__qzdqx = get_literal_value(name)
    else:
        raise_bodo_error(paae__vohm)
    eaz__qzdqx = 0 if eaz__qzdqx is None else eaz__qzdqx
    pgwax__ctjm = ColNamesMetaType((eaz__qzdqx,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            pgwax__ctjm)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
