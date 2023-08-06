import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    cze__vfss = hi - lo
    if cze__vfss < 2:
        return
    if cze__vfss < MIN_MERGE:
        plre__ebk = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + plre__ebk, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    kvqq__esqt = minRunLength(cze__vfss)
    while True:
        rqxrv__wpk = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if rqxrv__wpk < kvqq__esqt:
            fidbs__qwyq = cze__vfss if cze__vfss <= kvqq__esqt else kvqq__esqt
            binarySort(key_arrs, lo, lo + fidbs__qwyq, lo + rqxrv__wpk, data)
            rqxrv__wpk = fidbs__qwyq
        stackSize = pushRun(stackSize, runBase, runLen, lo, rqxrv__wpk)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += rqxrv__wpk
        cze__vfss -= rqxrv__wpk
        if cze__vfss == 0:
            break
    assert lo == hi
    stackSize, tmpLength, tmp, tmp_data, minGallop = mergeForceCollapse(
        stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
        tmp_data, minGallop)
    assert stackSize == 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def binarySort(key_arrs, lo, hi, start, data):
    assert lo <= start and start <= hi
    if start == lo:
        start += 1
    while start < hi:
        dmm__pzs = getitem_arr_tup(key_arrs, start)
        geg__tjgyc = getitem_arr_tup(data, start)
        tlrx__cju = lo
        gewl__ssxk = start
        assert tlrx__cju <= gewl__ssxk
        while tlrx__cju < gewl__ssxk:
            opckw__khr = tlrx__cju + gewl__ssxk >> 1
            if dmm__pzs < getitem_arr_tup(key_arrs, opckw__khr):
                gewl__ssxk = opckw__khr
            else:
                tlrx__cju = opckw__khr + 1
        assert tlrx__cju == gewl__ssxk
        n = start - tlrx__cju
        copyRange_tup(key_arrs, tlrx__cju, key_arrs, tlrx__cju + 1, n)
        copyRange_tup(data, tlrx__cju, data, tlrx__cju + 1, n)
        setitem_arr_tup(key_arrs, tlrx__cju, dmm__pzs)
        setitem_arr_tup(data, tlrx__cju, geg__tjgyc)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    pli__dbael = lo + 1
    if pli__dbael == hi:
        return 1
    if getitem_arr_tup(key_arrs, pli__dbael) < getitem_arr_tup(key_arrs, lo):
        pli__dbael += 1
        while pli__dbael < hi and getitem_arr_tup(key_arrs, pli__dbael
            ) < getitem_arr_tup(key_arrs, pli__dbael - 1):
            pli__dbael += 1
        reverseRange(key_arrs, lo, pli__dbael, data)
    else:
        pli__dbael += 1
        while pli__dbael < hi and getitem_arr_tup(key_arrs, pli__dbael
            ) >= getitem_arr_tup(key_arrs, pli__dbael - 1):
            pli__dbael += 1
    return pli__dbael - lo


@numba.njit(no_cpython_wrapper=True, cache=True)
def reverseRange(key_arrs, lo, hi, data):
    hi -= 1
    while lo < hi:
        swap_arrs(key_arrs, lo, hi)
        swap_arrs(data, lo, hi)
        lo += 1
        hi -= 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def minRunLength(n):
    assert n >= 0
    lgchh__dmsbs = 0
    while n >= MIN_MERGE:
        lgchh__dmsbs |= n & 1
        n >>= 1
    return n + lgchh__dmsbs


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    xklxa__kzu = len(key_arrs[0])
    tmpLength = (xklxa__kzu >> 1 if xklxa__kzu < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    kwjw__javb = (5 if xklxa__kzu < 120 else 10 if xklxa__kzu < 1542 else 
        19 if xklxa__kzu < 119151 else 40)
    runBase = np.empty(kwjw__javb, np.int64)
    runLen = np.empty(kwjw__javb, np.int64)
    return stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def pushRun(stackSize, runBase, runLen, runBase_val, runLen_val):
    runBase[stackSize] = runBase_val
    runLen[stackSize] = runLen_val
    stackSize += 1
    return stackSize


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeCollapse(stackSize, runBase, runLen, key_arrs, data, tmpLength,
    tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n >= 1 and runLen[n - 1] <= runLen[n] + runLen[n + 1
            ] or n >= 2 and runLen[n - 2] <= runLen[n] + runLen[n - 1]:
            if runLen[n - 1] < runLen[n + 1]:
                n -= 1
        elif runLen[n] > runLen[n + 1]:
            break
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeForceCollapse(stackSize, runBase, runLen, key_arrs, data,
    tmpLength, tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n > 0 and runLen[n - 1] < runLen[n + 1]:
            n -= 1
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeAt(stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
    tmp_data, minGallop, i):
    assert stackSize >= 2
    assert i >= 0
    assert i == stackSize - 2 or i == stackSize - 3
    base1 = runBase[i]
    len1 = runLen[i]
    base2 = runBase[i + 1]
    len2 = runLen[i + 1]
    assert len1 > 0 and len2 > 0
    assert base1 + len1 == base2
    runLen[i] = len1 + len2
    if i == stackSize - 3:
        runBase[i + 1] = runBase[i + 2]
        runLen[i + 1] = runLen[i + 2]
    stackSize -= 1
    bufn__onc = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert bufn__onc >= 0
    base1 += bufn__onc
    len1 -= bufn__onc
    if len1 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    len2 = gallopLeft(getitem_arr_tup(key_arrs, base1 + len1 - 1), key_arrs,
        base2, len2, len2 - 1)
    assert len2 >= 0
    if len2 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    if len1 <= len2:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len1)
        minGallop = mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    else:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len2)
        minGallop = mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopLeft(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    rgpp__nbcb = 0
    kdj__uorf = 1
    if key > getitem_arr_tup(arr, base + hint):
        hkuu__hhnef = _len - hint
        while kdj__uorf < hkuu__hhnef and key > getitem_arr_tup(arr, base +
            hint + kdj__uorf):
            rgpp__nbcb = kdj__uorf
            kdj__uorf = (kdj__uorf << 1) + 1
            if kdj__uorf <= 0:
                kdj__uorf = hkuu__hhnef
        if kdj__uorf > hkuu__hhnef:
            kdj__uorf = hkuu__hhnef
        rgpp__nbcb += hint
        kdj__uorf += hint
    else:
        hkuu__hhnef = hint + 1
        while kdj__uorf < hkuu__hhnef and key <= getitem_arr_tup(arr, base +
            hint - kdj__uorf):
            rgpp__nbcb = kdj__uorf
            kdj__uorf = (kdj__uorf << 1) + 1
            if kdj__uorf <= 0:
                kdj__uorf = hkuu__hhnef
        if kdj__uorf > hkuu__hhnef:
            kdj__uorf = hkuu__hhnef
        tmp = rgpp__nbcb
        rgpp__nbcb = hint - kdj__uorf
        kdj__uorf = hint - tmp
    assert -1 <= rgpp__nbcb and rgpp__nbcb < kdj__uorf and kdj__uorf <= _len
    rgpp__nbcb += 1
    while rgpp__nbcb < kdj__uorf:
        smfz__iarnp = rgpp__nbcb + (kdj__uorf - rgpp__nbcb >> 1)
        if key > getitem_arr_tup(arr, base + smfz__iarnp):
            rgpp__nbcb = smfz__iarnp + 1
        else:
            kdj__uorf = smfz__iarnp
    assert rgpp__nbcb == kdj__uorf
    return kdj__uorf


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    kdj__uorf = 1
    rgpp__nbcb = 0
    if key < getitem_arr_tup(arr, base + hint):
        hkuu__hhnef = hint + 1
        while kdj__uorf < hkuu__hhnef and key < getitem_arr_tup(arr, base +
            hint - kdj__uorf):
            rgpp__nbcb = kdj__uorf
            kdj__uorf = (kdj__uorf << 1) + 1
            if kdj__uorf <= 0:
                kdj__uorf = hkuu__hhnef
        if kdj__uorf > hkuu__hhnef:
            kdj__uorf = hkuu__hhnef
        tmp = rgpp__nbcb
        rgpp__nbcb = hint - kdj__uorf
        kdj__uorf = hint - tmp
    else:
        hkuu__hhnef = _len - hint
        while kdj__uorf < hkuu__hhnef and key >= getitem_arr_tup(arr, base +
            hint + kdj__uorf):
            rgpp__nbcb = kdj__uorf
            kdj__uorf = (kdj__uorf << 1) + 1
            if kdj__uorf <= 0:
                kdj__uorf = hkuu__hhnef
        if kdj__uorf > hkuu__hhnef:
            kdj__uorf = hkuu__hhnef
        rgpp__nbcb += hint
        kdj__uorf += hint
    assert -1 <= rgpp__nbcb and rgpp__nbcb < kdj__uorf and kdj__uorf <= _len
    rgpp__nbcb += 1
    while rgpp__nbcb < kdj__uorf:
        smfz__iarnp = rgpp__nbcb + (kdj__uorf - rgpp__nbcb >> 1)
        if key < getitem_arr_tup(arr, base + smfz__iarnp):
            kdj__uorf = smfz__iarnp
        else:
            rgpp__nbcb = smfz__iarnp + 1
    assert rgpp__nbcb == kdj__uorf
    return kdj__uorf


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base1, tmp, 0, len1)
    copyRange_tup(arr_data, base1, tmp_data, 0, len1)
    cursor1 = 0
    cursor2 = base2
    dest = base1
    setitem_arr_tup(arr, dest, getitem_arr_tup(arr, cursor2))
    copyElement_tup(arr_data, cursor2, arr_data, dest)
    cursor2 += 1
    dest += 1
    len2 -= 1
    if len2 == 0:
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
        return minGallop
    if len1 == 1:
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
        return minGallop
    len1, len2, cursor1, cursor2, dest, minGallop = mergeLo_inner(key_arrs,
        data, tmp_data, len1, len2, tmp, cursor1, cursor2, dest, minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len1 == 1:
        assert len2 > 0
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
    elif len1 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len2 == 0
        assert len1 > 1
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo_inner(arr, arr_data, tmp_data, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        vdsyl__hnt = 0
        njho__fanf = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                njho__fanf += 1
                vdsyl__hnt = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                vdsyl__hnt += 1
                njho__fanf = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not vdsyl__hnt | njho__fanf < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            vdsyl__hnt = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if vdsyl__hnt != 0:
                copyRange_tup(tmp, cursor1, arr, dest, vdsyl__hnt)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, vdsyl__hnt)
                dest += vdsyl__hnt
                cursor1 += vdsyl__hnt
                len1 -= vdsyl__hnt
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            njho__fanf = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if njho__fanf != 0:
                copyRange_tup(arr, cursor2, arr, dest, njho__fanf)
                copyRange_tup(arr_data, cursor2, arr_data, dest, njho__fanf)
                dest += njho__fanf
                cursor2 += njho__fanf
                len2 -= njho__fanf
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor1, arr, dest)
            copyElement_tup(tmp_data, cursor1, arr_data, dest)
            cursor1 += 1
            dest += 1
            len1 -= 1
            if len1 == 1:
                return len1, len2, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not vdsyl__hnt >= MIN_GALLOP | njho__fanf >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base2, tmp, 0, len2)
    copyRange_tup(arr_data, base2, tmp_data, 0, len2)
    cursor1 = base1 + len1 - 1
    cursor2 = len2 - 1
    dest = base2 + len2 - 1
    copyElement_tup(arr, cursor1, arr, dest)
    copyElement_tup(arr_data, cursor1, arr_data, dest)
    cursor1 -= 1
    dest -= 1
    len1 -= 1
    if len1 == 0:
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
        return minGallop
    if len2 == 1:
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
        return minGallop
    len1, len2, tmp, cursor1, cursor2, dest, minGallop = mergeHi_inner(key_arrs
        , data, tmp_data, base1, len1, len2, tmp, cursor1, cursor2, dest,
        minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len2 == 1:
        assert len1 > 0
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
    elif len2 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len1 == 0
        assert len2 > 0
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi_inner(arr, arr_data, tmp_data, base1, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        vdsyl__hnt = 0
        njho__fanf = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                vdsyl__hnt += 1
                njho__fanf = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                njho__fanf += 1
                vdsyl__hnt = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not vdsyl__hnt | njho__fanf < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            vdsyl__hnt = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if vdsyl__hnt != 0:
                dest -= vdsyl__hnt
                cursor1 -= vdsyl__hnt
                len1 -= vdsyl__hnt
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, vdsyl__hnt)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    vdsyl__hnt)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            njho__fanf = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if njho__fanf != 0:
                dest -= njho__fanf
                cursor2 -= njho__fanf
                len2 -= njho__fanf
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, njho__fanf)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    njho__fanf)
                if len2 <= 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor1, arr, dest)
            copyElement_tup(arr_data, cursor1, arr_data, dest)
            cursor1 -= 1
            dest -= 1
            len1 -= 1
            if len1 == 0:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not vdsyl__hnt >= MIN_GALLOP | njho__fanf >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    grxva__ypg = len(key_arrs[0])
    if tmpLength < minCapacity:
        sjdey__ghrka = minCapacity
        sjdey__ghrka |= sjdey__ghrka >> 1
        sjdey__ghrka |= sjdey__ghrka >> 2
        sjdey__ghrka |= sjdey__ghrka >> 4
        sjdey__ghrka |= sjdey__ghrka >> 8
        sjdey__ghrka |= sjdey__ghrka >> 16
        sjdey__ghrka += 1
        if sjdey__ghrka < 0:
            sjdey__ghrka = minCapacity
        else:
            sjdey__ghrka = min(sjdey__ghrka, grxva__ypg >> 1)
        tmp = alloc_arr_tup(sjdey__ghrka, key_arrs)
        tmp_data = alloc_arr_tup(sjdey__ghrka, data)
        tmpLength = sjdey__ghrka
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        jpz__pong = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = jpz__pong


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    wgplq__kpzso = arr_tup.count
    aoey__ftoq = 'def f(arr_tup, lo, hi):\n'
    for i in range(wgplq__kpzso):
        aoey__ftoq += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        aoey__ftoq += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        aoey__ftoq += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    aoey__ftoq += '  return\n'
    vpay__pvwgq = {}
    exec(aoey__ftoq, {}, vpay__pvwgq)
    htcmi__huv = vpay__pvwgq['f']
    return htcmi__huv


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    wgplq__kpzso = src_arr_tup.count
    assert wgplq__kpzso == dst_arr_tup.count
    aoey__ftoq = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(wgplq__kpzso):
        aoey__ftoq += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    aoey__ftoq += '  return\n'
    vpay__pvwgq = {}
    exec(aoey__ftoq, {'copyRange': copyRange}, vpay__pvwgq)
    sef__laspm = vpay__pvwgq['f']
    return sef__laspm


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    wgplq__kpzso = src_arr_tup.count
    assert wgplq__kpzso == dst_arr_tup.count
    aoey__ftoq = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(wgplq__kpzso):
        aoey__ftoq += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    aoey__ftoq += '  return\n'
    vpay__pvwgq = {}
    exec(aoey__ftoq, {'copyElement': copyElement}, vpay__pvwgq)
    sef__laspm = vpay__pvwgq['f']
    return sef__laspm


def getitem_arr_tup(arr_tup, ind):
    ndlvj__qpl = [arr[ind] for arr in arr_tup]
    return tuple(ndlvj__qpl)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    wgplq__kpzso = arr_tup.count
    aoey__ftoq = 'def f(arr_tup, ind):\n'
    aoey__ftoq += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(wgplq__kpzso)]), ',' if wgplq__kpzso == 1 else
        '')
    vpay__pvwgq = {}
    exec(aoey__ftoq, {}, vpay__pvwgq)
    ecrgx__gwwp = vpay__pvwgq['f']
    return ecrgx__gwwp


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, swyl__vhev in zip(arr_tup, val_tup):
        arr[ind] = swyl__vhev


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    wgplq__kpzso = arr_tup.count
    aoey__ftoq = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(wgplq__kpzso):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            aoey__ftoq += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            aoey__ftoq += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    aoey__ftoq += '  return\n'
    vpay__pvwgq = {}
    exec(aoey__ftoq, {}, vpay__pvwgq)
    ecrgx__gwwp = vpay__pvwgq['f']
    return ecrgx__gwwp


def test():
    import time
    tot__abxwo = time.time()
    ahyy__crhr = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((ahyy__crhr,), 0, 3, data)
    print('compile time', time.time() - tot__abxwo)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    prp__mdfc = np.random.ranf(n)
    mkmoy__wvf = pd.DataFrame({'A': prp__mdfc, 'B': data[0], 'C': data[1]})
    tot__abxwo = time.time()
    uju__ivo = mkmoy__wvf.sort_values('A', inplace=False)
    pfq__hqct = time.time()
    sort((prp__mdfc,), 0, n, data)
    print('Bodo', time.time() - pfq__hqct, 'Numpy', pfq__hqct - tot__abxwo)
    np.testing.assert_almost_equal(data[0], uju__ivo.B.values)
    np.testing.assert_almost_equal(data[1], uju__ivo.C.values)


if __name__ == '__main__':
    test()
