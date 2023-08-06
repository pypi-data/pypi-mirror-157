"""
Implements array operations for usage by DataFrames and Series
such as count and max.
"""
import numba
import numpy as np
import pandas as pd
from numba import generated_jit
from numba.core import types
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.utils.typing import element_type, is_hashable_type, is_iterable_type, is_overload_true, is_overload_zero, is_str_arr_type


def array_op_any(arr, skipna=True):
    pass


@overload(array_op_any)
def overload_array_op_any(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        owwr__gkdek = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        owwr__gkdek = False
    elif A == bodo.string_array_type:
        owwr__gkdek = ''
    elif A == bodo.binary_array_type:
        owwr__gkdek = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        bkhf__ooi = 0
        for qye__yprga in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, qye__yprga):
                if A[qye__yprga] != owwr__gkdek:
                    bkhf__ooi += 1
        return bkhf__ooi != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        owwr__gkdek = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        owwr__gkdek = False
    elif A == bodo.string_array_type:
        owwr__gkdek = ''
    elif A == bodo.binary_array_type:
        owwr__gkdek = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        bkhf__ooi = 0
        for qye__yprga in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, qye__yprga):
                if A[qye__yprga] == owwr__gkdek:
                    bkhf__ooi += 1
        return bkhf__ooi == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    phh__nzv = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(phh__nzv.ctypes, arr,
        parallel, skipna)
    return phh__nzv[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        qzrfe__xumrn = len(arr)
        wwqvv__wbb = np.empty(qzrfe__xumrn, np.bool_)
        for qye__yprga in numba.parfors.parfor.internal_prange(qzrfe__xumrn):
            wwqvv__wbb[qye__yprga] = bodo.libs.array_kernels.isna(arr,
                qye__yprga)
        return wwqvv__wbb
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        bkhf__ooi = 0
        for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
            oltk__eto = 0
            if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                oltk__eto = 1
            bkhf__ooi += oltk__eto
        phh__nzv = bkhf__ooi
        return phh__nzv
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    lfxwd__yssx = array_op_count(arr)
    bsu__pzfcs = array_op_min(arr)
    bmh__tdfnn = array_op_max(arr)
    zhort__vqy = array_op_mean(arr)
    rufl__uncol = array_op_std(arr)
    urn__tfoit = array_op_quantile(arr, 0.25)
    isl__ysb = array_op_quantile(arr, 0.5)
    sri__odaz = array_op_quantile(arr, 0.75)
    return (lfxwd__yssx, zhort__vqy, rufl__uncol, bsu__pzfcs, urn__tfoit,
        isl__ysb, sri__odaz, bmh__tdfnn)


def array_op_describe_dt_impl(arr):
    lfxwd__yssx = array_op_count(arr)
    bsu__pzfcs = array_op_min(arr)
    bmh__tdfnn = array_op_max(arr)
    zhort__vqy = array_op_mean(arr)
    urn__tfoit = array_op_quantile(arr, 0.25)
    isl__ysb = array_op_quantile(arr, 0.5)
    sri__odaz = array_op_quantile(arr, 0.75)
    return (lfxwd__yssx, zhort__vqy, bsu__pzfcs, urn__tfoit, isl__ysb,
        sri__odaz, bmh__tdfnn)


@overload(array_op_describe)
def overload_array_op_describe(arr):
    if arr.dtype == bodo.datetime64ns:
        return array_op_describe_dt_impl
    return array_op_describe_impl


@generated_jit(nopython=True)
def array_op_nbytes(arr):
    return array_op_nbytes_impl


def array_op_nbytes_impl(arr):
    return arr.nbytes


def array_op_min(arr):
    pass


@overload(array_op_min)
def overload_array_op_min(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = numba.cpython.builtins.get_type_max_value(np.int64)
            bkhf__ooi = 0
            for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
                czdc__bmc = ifbby__cdeb
                oltk__eto = 0
                if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                    czdc__bmc = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[qye__yprga]))
                    oltk__eto = 1
                ifbby__cdeb = min(ifbby__cdeb, czdc__bmc)
                bkhf__ooi += oltk__eto
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(ifbby__cdeb,
                bkhf__ooi)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = numba.cpython.builtins.get_type_max_value(np.int64)
            bkhf__ooi = 0
            for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
                czdc__bmc = ifbby__cdeb
                oltk__eto = 0
                if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                    czdc__bmc = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[qye__yprga])
                    oltk__eto = 1
                ifbby__cdeb = min(ifbby__cdeb, czdc__bmc)
                bkhf__ooi += oltk__eto
            return bodo.hiframes.pd_index_ext._dti_val_finalize(ifbby__cdeb,
                bkhf__ooi)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            qbtq__qmwq = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = numba.cpython.builtins.get_type_max_value(np.int64)
            bkhf__ooi = 0
            for qye__yprga in numba.parfors.parfor.internal_prange(len(
                qbtq__qmwq)):
                mhr__aziz = qbtq__qmwq[qye__yprga]
                if mhr__aziz == -1:
                    continue
                ifbby__cdeb = min(ifbby__cdeb, mhr__aziz)
                bkhf__ooi += 1
            phh__nzv = bodo.hiframes.series_kernels._box_cat_val(ifbby__cdeb,
                arr.dtype, bkhf__ooi)
            return phh__nzv
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = bodo.hiframes.series_kernels._get_date_max_value()
            bkhf__ooi = 0
            for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
                czdc__bmc = ifbby__cdeb
                oltk__eto = 0
                if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                    czdc__bmc = arr[qye__yprga]
                    oltk__eto = 1
                ifbby__cdeb = min(ifbby__cdeb, czdc__bmc)
                bkhf__ooi += oltk__eto
            phh__nzv = bodo.hiframes.series_kernels._sum_handle_nan(ifbby__cdeb
                , bkhf__ooi)
            return phh__nzv
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        ifbby__cdeb = bodo.hiframes.series_kernels._get_type_max_value(arr.
            dtype)
        bkhf__ooi = 0
        for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
            czdc__bmc = ifbby__cdeb
            oltk__eto = 0
            if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                czdc__bmc = arr[qye__yprga]
                oltk__eto = 1
            ifbby__cdeb = min(ifbby__cdeb, czdc__bmc)
            bkhf__ooi += oltk__eto
        phh__nzv = bodo.hiframes.series_kernels._sum_handle_nan(ifbby__cdeb,
            bkhf__ooi)
        return phh__nzv
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = numba.cpython.builtins.get_type_min_value(np.int64)
            bkhf__ooi = 0
            for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
                czdc__bmc = ifbby__cdeb
                oltk__eto = 0
                if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                    czdc__bmc = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[qye__yprga]))
                    oltk__eto = 1
                ifbby__cdeb = max(ifbby__cdeb, czdc__bmc)
                bkhf__ooi += oltk__eto
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(ifbby__cdeb,
                bkhf__ooi)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = numba.cpython.builtins.get_type_min_value(np.int64)
            bkhf__ooi = 0
            for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
                czdc__bmc = ifbby__cdeb
                oltk__eto = 0
                if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                    czdc__bmc = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[qye__yprga])
                    oltk__eto = 1
                ifbby__cdeb = max(ifbby__cdeb, czdc__bmc)
                bkhf__ooi += oltk__eto
            return bodo.hiframes.pd_index_ext._dti_val_finalize(ifbby__cdeb,
                bkhf__ooi)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            qbtq__qmwq = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = -1
            for qye__yprga in numba.parfors.parfor.internal_prange(len(
                qbtq__qmwq)):
                ifbby__cdeb = max(ifbby__cdeb, qbtq__qmwq[qye__yprga])
            phh__nzv = bodo.hiframes.series_kernels._box_cat_val(ifbby__cdeb,
                arr.dtype, 1)
            return phh__nzv
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = bodo.hiframes.series_kernels._get_date_min_value()
            bkhf__ooi = 0
            for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
                czdc__bmc = ifbby__cdeb
                oltk__eto = 0
                if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                    czdc__bmc = arr[qye__yprga]
                    oltk__eto = 1
                ifbby__cdeb = max(ifbby__cdeb, czdc__bmc)
                bkhf__ooi += oltk__eto
            phh__nzv = bodo.hiframes.series_kernels._sum_handle_nan(ifbby__cdeb
                , bkhf__ooi)
            return phh__nzv
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        ifbby__cdeb = bodo.hiframes.series_kernels._get_type_min_value(arr.
            dtype)
        bkhf__ooi = 0
        for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
            czdc__bmc = ifbby__cdeb
            oltk__eto = 0
            if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                czdc__bmc = arr[qye__yprga]
                oltk__eto = 1
            ifbby__cdeb = max(ifbby__cdeb, czdc__bmc)
            bkhf__ooi += oltk__eto
        phh__nzv = bodo.hiframes.series_kernels._sum_handle_nan(ifbby__cdeb,
            bkhf__ooi)
        return phh__nzv
    return impl


def array_op_mean(arr):
    pass


@overload(array_op_mean)
def overload_array_op_mean(arr):
    if arr.dtype == bodo.datetime64ns:

        def impl(arr):
            return pd.Timestamp(types.int64(bodo.libs.array_ops.
                array_op_mean(arr.view(np.int64))))
        return impl
    agnm__gqspy = types.float64
    bgdex__pkmre = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        agnm__gqspy = types.float32
        bgdex__pkmre = types.float32
    vfwt__vhdpc = agnm__gqspy(0)
    qzxfo__eehv = bgdex__pkmre(0)
    jqj__igu = bgdex__pkmre(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        ifbby__cdeb = vfwt__vhdpc
        bkhf__ooi = qzxfo__eehv
        for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
            czdc__bmc = vfwt__vhdpc
            oltk__eto = qzxfo__eehv
            if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                czdc__bmc = arr[qye__yprga]
                oltk__eto = jqj__igu
            ifbby__cdeb += czdc__bmc
            bkhf__ooi += oltk__eto
        phh__nzv = bodo.hiframes.series_kernels._mean_handle_nan(ifbby__cdeb,
            bkhf__ooi)
        return phh__nzv
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        sbrqq__aiwht = 0.0
        rxnx__vdp = 0.0
        bkhf__ooi = 0
        for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
            czdc__bmc = 0.0
            oltk__eto = 0
            if not bodo.libs.array_kernels.isna(arr, qye__yprga) or not skipna:
                czdc__bmc = arr[qye__yprga]
                oltk__eto = 1
            sbrqq__aiwht += czdc__bmc
            rxnx__vdp += czdc__bmc * czdc__bmc
            bkhf__ooi += oltk__eto
        phh__nzv = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            sbrqq__aiwht, rxnx__vdp, bkhf__ooi, ddof)
        return phh__nzv
    return impl


def array_op_std(arr, skipna=True, ddof=1):
    pass


@overload(array_op_std)
def overload_array_op_std(arr, skipna=True, ddof=1):
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr, skipna=True, ddof=1):
            return pd.Timedelta(types.int64(array_op_var(arr.view(np.int64),
                skipna, ddof) ** 0.5))
        return impl_dt64
    return lambda arr, skipna=True, ddof=1: array_op_var(arr, skipna, ddof
        ) ** 0.5


def array_op_quantile(arr, q):
    pass


@overload(array_op_quantile)
def overload_array_op_quantile(arr, q):
    if is_iterable_type(q):
        if arr.dtype == bodo.datetime64ns:

            def _impl_list_dt(arr, q):
                wwqvv__wbb = np.empty(len(q), np.int64)
                for qye__yprga in range(len(q)):
                    wixk__tvm = np.float64(q[qye__yprga])
                    wwqvv__wbb[qye__yprga] = bodo.libs.array_kernels.quantile(
                        arr.view(np.int64), wixk__tvm)
                return wwqvv__wbb.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            wwqvv__wbb = np.empty(len(q), np.float64)
            for qye__yprga in range(len(q)):
                wixk__tvm = np.float64(q[qye__yprga])
                wwqvv__wbb[qye__yprga] = bodo.libs.array_kernels.quantile(arr,
                    wixk__tvm)
            return wwqvv__wbb
        return impl_list
    if arr.dtype == bodo.datetime64ns:

        def _impl_dt(arr, q):
            return pd.Timestamp(bodo.libs.array_kernels.quantile(arr.view(
                np.int64), np.float64(q)))
        return _impl_dt

    def impl(arr, q):
        return bodo.libs.array_kernels.quantile(arr, np.float64(q))
    return impl


def array_op_sum(arr, skipna, min_count):
    pass


@overload(array_op_sum, no_unliteral=True)
def overload_array_op_sum(arr, skipna, min_count):
    if isinstance(arr.dtype, types.Integer):
        jjfg__ldd = types.intp
    elif arr.dtype == types.bool_:
        jjfg__ldd = np.int64
    else:
        jjfg__ldd = arr.dtype
    xvlmf__kha = jjfg__ldd(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = xvlmf__kha
            qzrfe__xumrn = len(arr)
            bkhf__ooi = 0
            for qye__yprga in numba.parfors.parfor.internal_prange(qzrfe__xumrn
                ):
                czdc__bmc = xvlmf__kha
                oltk__eto = 0
                if not bodo.libs.array_kernels.isna(arr, qye__yprga
                    ) or not skipna:
                    czdc__bmc = arr[qye__yprga]
                    oltk__eto = 1
                ifbby__cdeb += czdc__bmc
                bkhf__ooi += oltk__eto
            phh__nzv = bodo.hiframes.series_kernels._var_handle_mincount(
                ifbby__cdeb, bkhf__ooi, min_count)
            return phh__nzv
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = xvlmf__kha
            qzrfe__xumrn = len(arr)
            for qye__yprga in numba.parfors.parfor.internal_prange(qzrfe__xumrn
                ):
                czdc__bmc = xvlmf__kha
                if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                    czdc__bmc = arr[qye__yprga]
                ifbby__cdeb += czdc__bmc
            return ifbby__cdeb
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    gcd__iihms = arr.dtype(1)
    if arr.dtype == types.bool_:
        gcd__iihms = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = gcd__iihms
            bkhf__ooi = 0
            for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
                czdc__bmc = gcd__iihms
                oltk__eto = 0
                if not bodo.libs.array_kernels.isna(arr, qye__yprga
                    ) or not skipna:
                    czdc__bmc = arr[qye__yprga]
                    oltk__eto = 1
                bkhf__ooi += oltk__eto
                ifbby__cdeb *= czdc__bmc
            phh__nzv = bodo.hiframes.series_kernels._var_handle_mincount(
                ifbby__cdeb, bkhf__ooi, min_count)
            return phh__nzv
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            ifbby__cdeb = gcd__iihms
            for qye__yprga in numba.parfors.parfor.internal_prange(len(arr)):
                czdc__bmc = gcd__iihms
                if not bodo.libs.array_kernels.isna(arr, qye__yprga):
                    czdc__bmc = arr[qye__yprga]
                ifbby__cdeb *= czdc__bmc
            return ifbby__cdeb
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        qye__yprga = bodo.libs.array_kernels._nan_argmax(arr)
        return index[qye__yprga]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        qye__yprga = bodo.libs.array_kernels._nan_argmin(arr)
        return index[qye__yprga]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            pqh__hlxsp = {}
            for igiog__nsz in values:
                pqh__hlxsp[bodo.utils.conversion.box_if_dt64(igiog__nsz)] = 0
            return pqh__hlxsp
        return impl
    else:

        def impl(values, use_hash_impl):
            return values
        return impl


def array_op_isin(arr, values):
    pass


@overload(array_op_isin, inline='always')
def overload_array_op_isin(arr, values):
    use_hash_impl = element_type(values) == element_type(arr
        ) and is_hashable_type(element_type(values))

    def impl(arr, values):
        values = bodo.libs.array_ops._convert_isin_values(values, use_hash_impl
            )
        numba.parfors.parfor.init_prange()
        qzrfe__xumrn = len(arr)
        wwqvv__wbb = np.empty(qzrfe__xumrn, np.bool_)
        for qye__yprga in numba.parfors.parfor.internal_prange(qzrfe__xumrn):
            wwqvv__wbb[qye__yprga] = bodo.utils.conversion.box_if_dt64(arr[
                qye__yprga]) in values
        return wwqvv__wbb
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    aidr__byt = len(in_arr_tup) != 1
    odwc__vrec = list(in_arr_tup.types)
    uxcwi__xlwr = 'def impl(in_arr_tup):\n'
    uxcwi__xlwr += '  n = len(in_arr_tup[0])\n'
    if aidr__byt:
        fmtp__qnr = ', '.join([f'in_arr_tup[{qye__yprga}][unused]' for
            qye__yprga in range(len(in_arr_tup))])
        njo__bzrpt = ', '.join(['False' for movy__gmg in range(len(
            in_arr_tup))])
        uxcwi__xlwr += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({fmtp__qnr},), ({njo__bzrpt},)): 0 for unused in range(0)}}
"""
        uxcwi__xlwr += '  map_vector = np.empty(n, np.int64)\n'
        for qye__yprga, elncw__trwma in enumerate(odwc__vrec):
            uxcwi__xlwr += f'  in_lst_{qye__yprga} = []\n'
            if is_str_arr_type(elncw__trwma):
                uxcwi__xlwr += f'  total_len_{qye__yprga} = 0\n'
            uxcwi__xlwr += f'  null_in_lst_{qye__yprga} = []\n'
        uxcwi__xlwr += '  for i in range(n):\n'
        xbo__dhkb = ', '.join([f'in_arr_tup[{qye__yprga}][i]' for
            qye__yprga in range(len(odwc__vrec))])
        uhh__jfhwa = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{qye__yprga}], i)' for
            qye__yprga in range(len(odwc__vrec))])
        uxcwi__xlwr += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({xbo__dhkb},), ({uhh__jfhwa},))
"""
        uxcwi__xlwr += '    if data_val not in arr_map:\n'
        uxcwi__xlwr += '      set_val = len(arr_map)\n'
        uxcwi__xlwr += '      values_tup = data_val._data\n'
        uxcwi__xlwr += '      nulls_tup = data_val._null_values\n'
        for qye__yprga, elncw__trwma in enumerate(odwc__vrec):
            uxcwi__xlwr += (
                f'      in_lst_{qye__yprga}.append(values_tup[{qye__yprga}])\n'
                )
            uxcwi__xlwr += (
                f'      null_in_lst_{qye__yprga}.append(nulls_tup[{qye__yprga}])\n'
                )
            if is_str_arr_type(elncw__trwma):
                uxcwi__xlwr += f"""      total_len_{qye__yprga}  += nulls_tup[{qye__yprga}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{qye__yprga}], i)
"""
        uxcwi__xlwr += '      arr_map[data_val] = len(arr_map)\n'
        uxcwi__xlwr += '    else:\n'
        uxcwi__xlwr += '      set_val = arr_map[data_val]\n'
        uxcwi__xlwr += '    map_vector[i] = set_val\n'
        uxcwi__xlwr += '  n_rows = len(arr_map)\n'
        for qye__yprga, elncw__trwma in enumerate(odwc__vrec):
            if is_str_arr_type(elncw__trwma):
                uxcwi__xlwr += f"""  out_arr_{qye__yprga} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{qye__yprga})
"""
            else:
                uxcwi__xlwr += f"""  out_arr_{qye__yprga} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{qye__yprga}], (-1,))
"""
        uxcwi__xlwr += '  for j in range(len(arr_map)):\n'
        for qye__yprga in range(len(odwc__vrec)):
            uxcwi__xlwr += f'    if null_in_lst_{qye__yprga}[j]:\n'
            uxcwi__xlwr += (
                f'      bodo.libs.array_kernels.setna(out_arr_{qye__yprga}, j)\n'
                )
            uxcwi__xlwr += '    else:\n'
            uxcwi__xlwr += (
                f'      out_arr_{qye__yprga}[j] = in_lst_{qye__yprga}[j]\n')
        cxc__gtjrl = ', '.join([f'out_arr_{qye__yprga}' for qye__yprga in
            range(len(odwc__vrec))])
        uxcwi__xlwr += f'  return ({cxc__gtjrl},), map_vector\n'
    else:
        uxcwi__xlwr += '  in_arr = in_arr_tup[0]\n'
        uxcwi__xlwr += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        uxcwi__xlwr += '  map_vector = np.empty(n, np.int64)\n'
        uxcwi__xlwr += '  is_na = 0\n'
        uxcwi__xlwr += '  in_lst = []\n'
        uxcwi__xlwr += '  na_idxs = []\n'
        if is_str_arr_type(odwc__vrec[0]):
            uxcwi__xlwr += '  total_len = 0\n'
        uxcwi__xlwr += '  for i in range(n):\n'
        uxcwi__xlwr += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        uxcwi__xlwr += '      is_na = 1\n'
        uxcwi__xlwr += '      # Always put NA in the last location.\n'
        uxcwi__xlwr += '      # We use -1 as a placeholder\n'
        uxcwi__xlwr += '      set_val = -1\n'
        uxcwi__xlwr += '      na_idxs.append(i)\n'
        uxcwi__xlwr += '    else:\n'
        uxcwi__xlwr += '      data_val = in_arr[i]\n'
        uxcwi__xlwr += '      if data_val not in arr_map:\n'
        uxcwi__xlwr += '        set_val = len(arr_map)\n'
        uxcwi__xlwr += '        in_lst.append(data_val)\n'
        if is_str_arr_type(odwc__vrec[0]):
            uxcwi__xlwr += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        uxcwi__xlwr += '        arr_map[data_val] = len(arr_map)\n'
        uxcwi__xlwr += '      else:\n'
        uxcwi__xlwr += '        set_val = arr_map[data_val]\n'
        uxcwi__xlwr += '    map_vector[i] = set_val\n'
        uxcwi__xlwr += '  map_vector[na_idxs] = len(arr_map)\n'
        uxcwi__xlwr += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(odwc__vrec[0]):
            uxcwi__xlwr += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            uxcwi__xlwr += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        uxcwi__xlwr += '  for j in range(len(arr_map)):\n'
        uxcwi__xlwr += '    out_arr[j] = in_lst[j]\n'
        uxcwi__xlwr += '  if is_na:\n'
        uxcwi__xlwr += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        uxcwi__xlwr += f'  return (out_arr,), map_vector\n'
    khs__rpa = {}
    exec(uxcwi__xlwr, {'bodo': bodo, 'np': np}, khs__rpa)
    impl = khs__rpa['impl']
    return impl
