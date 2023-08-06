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
        sge__eiybp = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        sge__eiybp = False
    elif A == bodo.string_array_type:
        sge__eiybp = ''
    elif A == bodo.binary_array_type:
        sge__eiybp = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        hmxp__ykqz = 0
        for cefj__fsfk in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, cefj__fsfk):
                if A[cefj__fsfk] != sge__eiybp:
                    hmxp__ykqz += 1
        return hmxp__ykqz != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        sge__eiybp = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        sge__eiybp = False
    elif A == bodo.string_array_type:
        sge__eiybp = ''
    elif A == bodo.binary_array_type:
        sge__eiybp = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        hmxp__ykqz = 0
        for cefj__fsfk in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, cefj__fsfk):
                if A[cefj__fsfk] == sge__eiybp:
                    hmxp__ykqz += 1
        return hmxp__ykqz == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    laad__ituj = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(laad__ituj.ctypes,
        arr, parallel, skipna)
    return laad__ituj[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        tye__rog = len(arr)
        aujsb__uduwc = np.empty(tye__rog, np.bool_)
        for cefj__fsfk in numba.parfors.parfor.internal_prange(tye__rog):
            aujsb__uduwc[cefj__fsfk] = bodo.libs.array_kernels.isna(arr,
                cefj__fsfk)
        return aujsb__uduwc
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        hmxp__ykqz = 0
        for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
            pnit__ydp = 0
            if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                pnit__ydp = 1
            hmxp__ykqz += pnit__ydp
        laad__ituj = hmxp__ykqz
        return laad__ituj
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    laj__dwp = array_op_count(arr)
    wcct__jte = array_op_min(arr)
    yspg__rvhi = array_op_max(arr)
    vrei__vgw = array_op_mean(arr)
    jiofm__agraa = array_op_std(arr)
    dyg__gtsbc = array_op_quantile(arr, 0.25)
    snb__nra = array_op_quantile(arr, 0.5)
    nfxqi__niyo = array_op_quantile(arr, 0.75)
    return (laj__dwp, vrei__vgw, jiofm__agraa, wcct__jte, dyg__gtsbc,
        snb__nra, nfxqi__niyo, yspg__rvhi)


def array_op_describe_dt_impl(arr):
    laj__dwp = array_op_count(arr)
    wcct__jte = array_op_min(arr)
    yspg__rvhi = array_op_max(arr)
    vrei__vgw = array_op_mean(arr)
    dyg__gtsbc = array_op_quantile(arr, 0.25)
    snb__nra = array_op_quantile(arr, 0.5)
    nfxqi__niyo = array_op_quantile(arr, 0.75)
    return (laj__dwp, vrei__vgw, wcct__jte, dyg__gtsbc, snb__nra,
        nfxqi__niyo, yspg__rvhi)


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
            llj__kqxma = numba.cpython.builtins.get_type_max_value(np.int64)
            hmxp__ykqz = 0
            for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
                ujja__jxzeh = llj__kqxma
                pnit__ydp = 0
                if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                    ujja__jxzeh = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[cefj__fsfk]))
                    pnit__ydp = 1
                llj__kqxma = min(llj__kqxma, ujja__jxzeh)
                hmxp__ykqz += pnit__ydp
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(llj__kqxma,
                hmxp__ykqz)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            llj__kqxma = numba.cpython.builtins.get_type_max_value(np.int64)
            hmxp__ykqz = 0
            for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
                ujja__jxzeh = llj__kqxma
                pnit__ydp = 0
                if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                    ujja__jxzeh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[cefj__fsfk]))
                    pnit__ydp = 1
                llj__kqxma = min(llj__kqxma, ujja__jxzeh)
                hmxp__ykqz += pnit__ydp
            return bodo.hiframes.pd_index_ext._dti_val_finalize(llj__kqxma,
                hmxp__ykqz)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            gknx__rrnjf = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            llj__kqxma = numba.cpython.builtins.get_type_max_value(np.int64)
            hmxp__ykqz = 0
            for cefj__fsfk in numba.parfors.parfor.internal_prange(len(
                gknx__rrnjf)):
                zdkqt__nxo = gknx__rrnjf[cefj__fsfk]
                if zdkqt__nxo == -1:
                    continue
                llj__kqxma = min(llj__kqxma, zdkqt__nxo)
                hmxp__ykqz += 1
            laad__ituj = bodo.hiframes.series_kernels._box_cat_val(llj__kqxma,
                arr.dtype, hmxp__ykqz)
            return laad__ituj
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            llj__kqxma = bodo.hiframes.series_kernels._get_date_max_value()
            hmxp__ykqz = 0
            for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
                ujja__jxzeh = llj__kqxma
                pnit__ydp = 0
                if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                    ujja__jxzeh = arr[cefj__fsfk]
                    pnit__ydp = 1
                llj__kqxma = min(llj__kqxma, ujja__jxzeh)
                hmxp__ykqz += pnit__ydp
            laad__ituj = bodo.hiframes.series_kernels._sum_handle_nan(
                llj__kqxma, hmxp__ykqz)
            return laad__ituj
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        llj__kqxma = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype
            )
        hmxp__ykqz = 0
        for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
            ujja__jxzeh = llj__kqxma
            pnit__ydp = 0
            if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                ujja__jxzeh = arr[cefj__fsfk]
                pnit__ydp = 1
            llj__kqxma = min(llj__kqxma, ujja__jxzeh)
            hmxp__ykqz += pnit__ydp
        laad__ituj = bodo.hiframes.series_kernels._sum_handle_nan(llj__kqxma,
            hmxp__ykqz)
        return laad__ituj
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            llj__kqxma = numba.cpython.builtins.get_type_min_value(np.int64)
            hmxp__ykqz = 0
            for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
                ujja__jxzeh = llj__kqxma
                pnit__ydp = 0
                if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                    ujja__jxzeh = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[cefj__fsfk]))
                    pnit__ydp = 1
                llj__kqxma = max(llj__kqxma, ujja__jxzeh)
                hmxp__ykqz += pnit__ydp
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(llj__kqxma,
                hmxp__ykqz)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            llj__kqxma = numba.cpython.builtins.get_type_min_value(np.int64)
            hmxp__ykqz = 0
            for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
                ujja__jxzeh = llj__kqxma
                pnit__ydp = 0
                if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                    ujja__jxzeh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[cefj__fsfk]))
                    pnit__ydp = 1
                llj__kqxma = max(llj__kqxma, ujja__jxzeh)
                hmxp__ykqz += pnit__ydp
            return bodo.hiframes.pd_index_ext._dti_val_finalize(llj__kqxma,
                hmxp__ykqz)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            gknx__rrnjf = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            llj__kqxma = -1
            for cefj__fsfk in numba.parfors.parfor.internal_prange(len(
                gknx__rrnjf)):
                llj__kqxma = max(llj__kqxma, gknx__rrnjf[cefj__fsfk])
            laad__ituj = bodo.hiframes.series_kernels._box_cat_val(llj__kqxma,
                arr.dtype, 1)
            return laad__ituj
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            llj__kqxma = bodo.hiframes.series_kernels._get_date_min_value()
            hmxp__ykqz = 0
            for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
                ujja__jxzeh = llj__kqxma
                pnit__ydp = 0
                if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                    ujja__jxzeh = arr[cefj__fsfk]
                    pnit__ydp = 1
                llj__kqxma = max(llj__kqxma, ujja__jxzeh)
                hmxp__ykqz += pnit__ydp
            laad__ituj = bodo.hiframes.series_kernels._sum_handle_nan(
                llj__kqxma, hmxp__ykqz)
            return laad__ituj
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        llj__kqxma = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype
            )
        hmxp__ykqz = 0
        for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
            ujja__jxzeh = llj__kqxma
            pnit__ydp = 0
            if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                ujja__jxzeh = arr[cefj__fsfk]
                pnit__ydp = 1
            llj__kqxma = max(llj__kqxma, ujja__jxzeh)
            hmxp__ykqz += pnit__ydp
        laad__ituj = bodo.hiframes.series_kernels._sum_handle_nan(llj__kqxma,
            hmxp__ykqz)
        return laad__ituj
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
    zrkk__max = types.float64
    bwgr__yudjk = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        zrkk__max = types.float32
        bwgr__yudjk = types.float32
    kgjbw__ogwdr = zrkk__max(0)
    grwc__ztr = bwgr__yudjk(0)
    bohe__vavyv = bwgr__yudjk(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        llj__kqxma = kgjbw__ogwdr
        hmxp__ykqz = grwc__ztr
        for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
            ujja__jxzeh = kgjbw__ogwdr
            pnit__ydp = grwc__ztr
            if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                ujja__jxzeh = arr[cefj__fsfk]
                pnit__ydp = bohe__vavyv
            llj__kqxma += ujja__jxzeh
            hmxp__ykqz += pnit__ydp
        laad__ituj = bodo.hiframes.series_kernels._mean_handle_nan(llj__kqxma,
            hmxp__ykqz)
        return laad__ituj
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        khhfu__yqg = 0.0
        npsn__nybp = 0.0
        hmxp__ykqz = 0
        for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
            ujja__jxzeh = 0.0
            pnit__ydp = 0
            if not bodo.libs.array_kernels.isna(arr, cefj__fsfk) or not skipna:
                ujja__jxzeh = arr[cefj__fsfk]
                pnit__ydp = 1
            khhfu__yqg += ujja__jxzeh
            npsn__nybp += ujja__jxzeh * ujja__jxzeh
            hmxp__ykqz += pnit__ydp
        laad__ituj = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            khhfu__yqg, npsn__nybp, hmxp__ykqz, ddof)
        return laad__ituj
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
                aujsb__uduwc = np.empty(len(q), np.int64)
                for cefj__fsfk in range(len(q)):
                    lfty__lvh = np.float64(q[cefj__fsfk])
                    aujsb__uduwc[cefj__fsfk
                        ] = bodo.libs.array_kernels.quantile(arr.view(np.
                        int64), lfty__lvh)
                return aujsb__uduwc.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            aujsb__uduwc = np.empty(len(q), np.float64)
            for cefj__fsfk in range(len(q)):
                lfty__lvh = np.float64(q[cefj__fsfk])
                aujsb__uduwc[cefj__fsfk] = bodo.libs.array_kernels.quantile(arr
                    , lfty__lvh)
            return aujsb__uduwc
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
        yprx__mbsjo = types.intp
    elif arr.dtype == types.bool_:
        yprx__mbsjo = np.int64
    else:
        yprx__mbsjo = arr.dtype
    gkgzs__jpusf = yprx__mbsjo(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            llj__kqxma = gkgzs__jpusf
            tye__rog = len(arr)
            hmxp__ykqz = 0
            for cefj__fsfk in numba.parfors.parfor.internal_prange(tye__rog):
                ujja__jxzeh = gkgzs__jpusf
                pnit__ydp = 0
                if not bodo.libs.array_kernels.isna(arr, cefj__fsfk
                    ) or not skipna:
                    ujja__jxzeh = arr[cefj__fsfk]
                    pnit__ydp = 1
                llj__kqxma += ujja__jxzeh
                hmxp__ykqz += pnit__ydp
            laad__ituj = bodo.hiframes.series_kernels._var_handle_mincount(
                llj__kqxma, hmxp__ykqz, min_count)
            return laad__ituj
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            llj__kqxma = gkgzs__jpusf
            tye__rog = len(arr)
            for cefj__fsfk in numba.parfors.parfor.internal_prange(tye__rog):
                ujja__jxzeh = gkgzs__jpusf
                if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                    ujja__jxzeh = arr[cefj__fsfk]
                llj__kqxma += ujja__jxzeh
            return llj__kqxma
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    qmyhr__kgp = arr.dtype(1)
    if arr.dtype == types.bool_:
        qmyhr__kgp = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            llj__kqxma = qmyhr__kgp
            hmxp__ykqz = 0
            for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
                ujja__jxzeh = qmyhr__kgp
                pnit__ydp = 0
                if not bodo.libs.array_kernels.isna(arr, cefj__fsfk
                    ) or not skipna:
                    ujja__jxzeh = arr[cefj__fsfk]
                    pnit__ydp = 1
                hmxp__ykqz += pnit__ydp
                llj__kqxma *= ujja__jxzeh
            laad__ituj = bodo.hiframes.series_kernels._var_handle_mincount(
                llj__kqxma, hmxp__ykqz, min_count)
            return laad__ituj
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            llj__kqxma = qmyhr__kgp
            for cefj__fsfk in numba.parfors.parfor.internal_prange(len(arr)):
                ujja__jxzeh = qmyhr__kgp
                if not bodo.libs.array_kernels.isna(arr, cefj__fsfk):
                    ujja__jxzeh = arr[cefj__fsfk]
                llj__kqxma *= ujja__jxzeh
            return llj__kqxma
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        cefj__fsfk = bodo.libs.array_kernels._nan_argmax(arr)
        return index[cefj__fsfk]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        cefj__fsfk = bodo.libs.array_kernels._nan_argmin(arr)
        return index[cefj__fsfk]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            mozqa__bjvr = {}
            for tkb__pijo in values:
                mozqa__bjvr[bodo.utils.conversion.box_if_dt64(tkb__pijo)] = 0
            return mozqa__bjvr
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
        tye__rog = len(arr)
        aujsb__uduwc = np.empty(tye__rog, np.bool_)
        for cefj__fsfk in numba.parfors.parfor.internal_prange(tye__rog):
            aujsb__uduwc[cefj__fsfk] = bodo.utils.conversion.box_if_dt64(arr
                [cefj__fsfk]) in values
        return aujsb__uduwc
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    uzpa__koabr = len(in_arr_tup) != 1
    wavr__legb = list(in_arr_tup.types)
    jssql__htuix = 'def impl(in_arr_tup):\n'
    jssql__htuix += '  n = len(in_arr_tup[0])\n'
    if uzpa__koabr:
        trj__gfzb = ', '.join([f'in_arr_tup[{cefj__fsfk}][unused]' for
            cefj__fsfk in range(len(in_arr_tup))])
        owqgx__xsk = ', '.join(['False' for ozush__iooo in range(len(
            in_arr_tup))])
        jssql__htuix += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({trj__gfzb},), ({owqgx__xsk},)): 0 for unused in range(0)}}
"""
        jssql__htuix += '  map_vector = np.empty(n, np.int64)\n'
        for cefj__fsfk, nyvvu__dgsp in enumerate(wavr__legb):
            jssql__htuix += f'  in_lst_{cefj__fsfk} = []\n'
            if is_str_arr_type(nyvvu__dgsp):
                jssql__htuix += f'  total_len_{cefj__fsfk} = 0\n'
            jssql__htuix += f'  null_in_lst_{cefj__fsfk} = []\n'
        jssql__htuix += '  for i in range(n):\n'
        bhuw__qac = ', '.join([f'in_arr_tup[{cefj__fsfk}][i]' for
            cefj__fsfk in range(len(wavr__legb))])
        jyr__ohzox = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{cefj__fsfk}], i)' for
            cefj__fsfk in range(len(wavr__legb))])
        jssql__htuix += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({bhuw__qac},), ({jyr__ohzox},))
"""
        jssql__htuix += '    if data_val not in arr_map:\n'
        jssql__htuix += '      set_val = len(arr_map)\n'
        jssql__htuix += '      values_tup = data_val._data\n'
        jssql__htuix += '      nulls_tup = data_val._null_values\n'
        for cefj__fsfk, nyvvu__dgsp in enumerate(wavr__legb):
            jssql__htuix += (
                f'      in_lst_{cefj__fsfk}.append(values_tup[{cefj__fsfk}])\n'
                )
            jssql__htuix += (
                f'      null_in_lst_{cefj__fsfk}.append(nulls_tup[{cefj__fsfk}])\n'
                )
            if is_str_arr_type(nyvvu__dgsp):
                jssql__htuix += f"""      total_len_{cefj__fsfk}  += nulls_tup[{cefj__fsfk}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{cefj__fsfk}], i)
"""
        jssql__htuix += '      arr_map[data_val] = len(arr_map)\n'
        jssql__htuix += '    else:\n'
        jssql__htuix += '      set_val = arr_map[data_val]\n'
        jssql__htuix += '    map_vector[i] = set_val\n'
        jssql__htuix += '  n_rows = len(arr_map)\n'
        for cefj__fsfk, nyvvu__dgsp in enumerate(wavr__legb):
            if is_str_arr_type(nyvvu__dgsp):
                jssql__htuix += f"""  out_arr_{cefj__fsfk} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{cefj__fsfk})
"""
            else:
                jssql__htuix += f"""  out_arr_{cefj__fsfk} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{cefj__fsfk}], (-1,))
"""
        jssql__htuix += '  for j in range(len(arr_map)):\n'
        for cefj__fsfk in range(len(wavr__legb)):
            jssql__htuix += f'    if null_in_lst_{cefj__fsfk}[j]:\n'
            jssql__htuix += (
                f'      bodo.libs.array_kernels.setna(out_arr_{cefj__fsfk}, j)\n'
                )
            jssql__htuix += '    else:\n'
            jssql__htuix += (
                f'      out_arr_{cefj__fsfk}[j] = in_lst_{cefj__fsfk}[j]\n')
        trev__xdw = ', '.join([f'out_arr_{cefj__fsfk}' for cefj__fsfk in
            range(len(wavr__legb))])
        jssql__htuix += f'  return ({trev__xdw},), map_vector\n'
    else:
        jssql__htuix += '  in_arr = in_arr_tup[0]\n'
        jssql__htuix += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        jssql__htuix += '  map_vector = np.empty(n, np.int64)\n'
        jssql__htuix += '  is_na = 0\n'
        jssql__htuix += '  in_lst = []\n'
        jssql__htuix += '  na_idxs = []\n'
        if is_str_arr_type(wavr__legb[0]):
            jssql__htuix += '  total_len = 0\n'
        jssql__htuix += '  for i in range(n):\n'
        jssql__htuix += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        jssql__htuix += '      is_na = 1\n'
        jssql__htuix += '      # Always put NA in the last location.\n'
        jssql__htuix += '      # We use -1 as a placeholder\n'
        jssql__htuix += '      set_val = -1\n'
        jssql__htuix += '      na_idxs.append(i)\n'
        jssql__htuix += '    else:\n'
        jssql__htuix += '      data_val = in_arr[i]\n'
        jssql__htuix += '      if data_val not in arr_map:\n'
        jssql__htuix += '        set_val = len(arr_map)\n'
        jssql__htuix += '        in_lst.append(data_val)\n'
        if is_str_arr_type(wavr__legb[0]):
            jssql__htuix += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        jssql__htuix += '        arr_map[data_val] = len(arr_map)\n'
        jssql__htuix += '      else:\n'
        jssql__htuix += '        set_val = arr_map[data_val]\n'
        jssql__htuix += '    map_vector[i] = set_val\n'
        jssql__htuix += '  map_vector[na_idxs] = len(arr_map)\n'
        jssql__htuix += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(wavr__legb[0]):
            jssql__htuix += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            jssql__htuix += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        jssql__htuix += '  for j in range(len(arr_map)):\n'
        jssql__htuix += '    out_arr[j] = in_lst[j]\n'
        jssql__htuix += '  if is_na:\n'
        jssql__htuix += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        jssql__htuix += f'  return (out_arr,), map_vector\n'
    dvzhd__eudb = {}
    exec(jssql__htuix, {'bodo': bodo, 'np': np}, dvzhd__eudb)
    impl = dvzhd__eudb['impl']
    return impl
