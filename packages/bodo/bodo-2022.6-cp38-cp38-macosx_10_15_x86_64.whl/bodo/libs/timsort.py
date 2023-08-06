import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    vgy__hfq = hi - lo
    if vgy__hfq < 2:
        return
    if vgy__hfq < MIN_MERGE:
        cruqc__qyv = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + cruqc__qyv, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    umy__hvhr = minRunLength(vgy__hfq)
    while True:
        nwib__xff = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if nwib__xff < umy__hvhr:
            zou__cwjyu = vgy__hfq if vgy__hfq <= umy__hvhr else umy__hvhr
            binarySort(key_arrs, lo, lo + zou__cwjyu, lo + nwib__xff, data)
            nwib__xff = zou__cwjyu
        stackSize = pushRun(stackSize, runBase, runLen, lo, nwib__xff)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += nwib__xff
        vgy__hfq -= nwib__xff
        if vgy__hfq == 0:
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
        jeto__fhfp = getitem_arr_tup(key_arrs, start)
        qitmi__hprpe = getitem_arr_tup(data, start)
        vadcl__aku = lo
        rwqeh__lzzki = start
        assert vadcl__aku <= rwqeh__lzzki
        while vadcl__aku < rwqeh__lzzki:
            moxnz__hscsk = vadcl__aku + rwqeh__lzzki >> 1
            if jeto__fhfp < getitem_arr_tup(key_arrs, moxnz__hscsk):
                rwqeh__lzzki = moxnz__hscsk
            else:
                vadcl__aku = moxnz__hscsk + 1
        assert vadcl__aku == rwqeh__lzzki
        n = start - vadcl__aku
        copyRange_tup(key_arrs, vadcl__aku, key_arrs, vadcl__aku + 1, n)
        copyRange_tup(data, vadcl__aku, data, vadcl__aku + 1, n)
        setitem_arr_tup(key_arrs, vadcl__aku, jeto__fhfp)
        setitem_arr_tup(data, vadcl__aku, qitmi__hprpe)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    gzzgt__covre = lo + 1
    if gzzgt__covre == hi:
        return 1
    if getitem_arr_tup(key_arrs, gzzgt__covre) < getitem_arr_tup(key_arrs, lo):
        gzzgt__covre += 1
        while gzzgt__covre < hi and getitem_arr_tup(key_arrs, gzzgt__covre
            ) < getitem_arr_tup(key_arrs, gzzgt__covre - 1):
            gzzgt__covre += 1
        reverseRange(key_arrs, lo, gzzgt__covre, data)
    else:
        gzzgt__covre += 1
        while gzzgt__covre < hi and getitem_arr_tup(key_arrs, gzzgt__covre
            ) >= getitem_arr_tup(key_arrs, gzzgt__covre - 1):
            gzzgt__covre += 1
    return gzzgt__covre - lo


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
    xnro__egjls = 0
    while n >= MIN_MERGE:
        xnro__egjls |= n & 1
        n >>= 1
    return n + xnro__egjls


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    euqy__bam = len(key_arrs[0])
    tmpLength = (euqy__bam >> 1 if euqy__bam < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    vndwr__ckkxa = (5 if euqy__bam < 120 else 10 if euqy__bam < 1542 else 
        19 if euqy__bam < 119151 else 40)
    runBase = np.empty(vndwr__ckkxa, np.int64)
    runLen = np.empty(vndwr__ckkxa, np.int64)
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
    hob__xcno = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert hob__xcno >= 0
    base1 += hob__xcno
    len1 -= hob__xcno
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
    qwl__vrdpl = 0
    wsh__ixycu = 1
    if key > getitem_arr_tup(arr, base + hint):
        qnlxx__mpvs = _len - hint
        while wsh__ixycu < qnlxx__mpvs and key > getitem_arr_tup(arr, base +
            hint + wsh__ixycu):
            qwl__vrdpl = wsh__ixycu
            wsh__ixycu = (wsh__ixycu << 1) + 1
            if wsh__ixycu <= 0:
                wsh__ixycu = qnlxx__mpvs
        if wsh__ixycu > qnlxx__mpvs:
            wsh__ixycu = qnlxx__mpvs
        qwl__vrdpl += hint
        wsh__ixycu += hint
    else:
        qnlxx__mpvs = hint + 1
        while wsh__ixycu < qnlxx__mpvs and key <= getitem_arr_tup(arr, base +
            hint - wsh__ixycu):
            qwl__vrdpl = wsh__ixycu
            wsh__ixycu = (wsh__ixycu << 1) + 1
            if wsh__ixycu <= 0:
                wsh__ixycu = qnlxx__mpvs
        if wsh__ixycu > qnlxx__mpvs:
            wsh__ixycu = qnlxx__mpvs
        tmp = qwl__vrdpl
        qwl__vrdpl = hint - wsh__ixycu
        wsh__ixycu = hint - tmp
    assert -1 <= qwl__vrdpl and qwl__vrdpl < wsh__ixycu and wsh__ixycu <= _len
    qwl__vrdpl += 1
    while qwl__vrdpl < wsh__ixycu:
        bqga__lvd = qwl__vrdpl + (wsh__ixycu - qwl__vrdpl >> 1)
        if key > getitem_arr_tup(arr, base + bqga__lvd):
            qwl__vrdpl = bqga__lvd + 1
        else:
            wsh__ixycu = bqga__lvd
    assert qwl__vrdpl == wsh__ixycu
    return wsh__ixycu


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    wsh__ixycu = 1
    qwl__vrdpl = 0
    if key < getitem_arr_tup(arr, base + hint):
        qnlxx__mpvs = hint + 1
        while wsh__ixycu < qnlxx__mpvs and key < getitem_arr_tup(arr, base +
            hint - wsh__ixycu):
            qwl__vrdpl = wsh__ixycu
            wsh__ixycu = (wsh__ixycu << 1) + 1
            if wsh__ixycu <= 0:
                wsh__ixycu = qnlxx__mpvs
        if wsh__ixycu > qnlxx__mpvs:
            wsh__ixycu = qnlxx__mpvs
        tmp = qwl__vrdpl
        qwl__vrdpl = hint - wsh__ixycu
        wsh__ixycu = hint - tmp
    else:
        qnlxx__mpvs = _len - hint
        while wsh__ixycu < qnlxx__mpvs and key >= getitem_arr_tup(arr, base +
            hint + wsh__ixycu):
            qwl__vrdpl = wsh__ixycu
            wsh__ixycu = (wsh__ixycu << 1) + 1
            if wsh__ixycu <= 0:
                wsh__ixycu = qnlxx__mpvs
        if wsh__ixycu > qnlxx__mpvs:
            wsh__ixycu = qnlxx__mpvs
        qwl__vrdpl += hint
        wsh__ixycu += hint
    assert -1 <= qwl__vrdpl and qwl__vrdpl < wsh__ixycu and wsh__ixycu <= _len
    qwl__vrdpl += 1
    while qwl__vrdpl < wsh__ixycu:
        bqga__lvd = qwl__vrdpl + (wsh__ixycu - qwl__vrdpl >> 1)
        if key < getitem_arr_tup(arr, base + bqga__lvd):
            wsh__ixycu = bqga__lvd
        else:
            qwl__vrdpl = bqga__lvd + 1
    assert qwl__vrdpl == wsh__ixycu
    return wsh__ixycu


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
        pjfn__rffe = 0
        pjrn__glzob = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                pjrn__glzob += 1
                pjfn__rffe = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                pjfn__rffe += 1
                pjrn__glzob = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not pjfn__rffe | pjrn__glzob < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            pjfn__rffe = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if pjfn__rffe != 0:
                copyRange_tup(tmp, cursor1, arr, dest, pjfn__rffe)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, pjfn__rffe)
                dest += pjfn__rffe
                cursor1 += pjfn__rffe
                len1 -= pjfn__rffe
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            pjrn__glzob = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if pjrn__glzob != 0:
                copyRange_tup(arr, cursor2, arr, dest, pjrn__glzob)
                copyRange_tup(arr_data, cursor2, arr_data, dest, pjrn__glzob)
                dest += pjrn__glzob
                cursor2 += pjrn__glzob
                len2 -= pjrn__glzob
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
            if not pjfn__rffe >= MIN_GALLOP | pjrn__glzob >= MIN_GALLOP:
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
        pjfn__rffe = 0
        pjrn__glzob = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                pjfn__rffe += 1
                pjrn__glzob = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                pjrn__glzob += 1
                pjfn__rffe = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not pjfn__rffe | pjrn__glzob < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            pjfn__rffe = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if pjfn__rffe != 0:
                dest -= pjfn__rffe
                cursor1 -= pjfn__rffe
                len1 -= pjfn__rffe
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, pjfn__rffe)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    pjfn__rffe)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            pjrn__glzob = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if pjrn__glzob != 0:
                dest -= pjrn__glzob
                cursor2 -= pjrn__glzob
                len2 -= pjrn__glzob
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, pjrn__glzob)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    pjrn__glzob)
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
            if not pjfn__rffe >= MIN_GALLOP | pjrn__glzob >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    fuo__rdlp = len(key_arrs[0])
    if tmpLength < minCapacity:
        stjr__tcoru = minCapacity
        stjr__tcoru |= stjr__tcoru >> 1
        stjr__tcoru |= stjr__tcoru >> 2
        stjr__tcoru |= stjr__tcoru >> 4
        stjr__tcoru |= stjr__tcoru >> 8
        stjr__tcoru |= stjr__tcoru >> 16
        stjr__tcoru += 1
        if stjr__tcoru < 0:
            stjr__tcoru = minCapacity
        else:
            stjr__tcoru = min(stjr__tcoru, fuo__rdlp >> 1)
        tmp = alloc_arr_tup(stjr__tcoru, key_arrs)
        tmp_data = alloc_arr_tup(stjr__tcoru, data)
        tmpLength = stjr__tcoru
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        skzj__pisrv = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = skzj__pisrv


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    lfkde__impp = arr_tup.count
    bznod__nnee = 'def f(arr_tup, lo, hi):\n'
    for i in range(lfkde__impp):
        bznod__nnee += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        bznod__nnee += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        bznod__nnee += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    bznod__nnee += '  return\n'
    tprad__reo = {}
    exec(bznod__nnee, {}, tprad__reo)
    uss__wua = tprad__reo['f']
    return uss__wua


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    lfkde__impp = src_arr_tup.count
    assert lfkde__impp == dst_arr_tup.count
    bznod__nnee = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(lfkde__impp):
        bznod__nnee += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    bznod__nnee += '  return\n'
    tprad__reo = {}
    exec(bznod__nnee, {'copyRange': copyRange}, tprad__reo)
    vzxkn__mkfu = tprad__reo['f']
    return vzxkn__mkfu


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    lfkde__impp = src_arr_tup.count
    assert lfkde__impp == dst_arr_tup.count
    bznod__nnee = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(lfkde__impp):
        bznod__nnee += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    bznod__nnee += '  return\n'
    tprad__reo = {}
    exec(bznod__nnee, {'copyElement': copyElement}, tprad__reo)
    vzxkn__mkfu = tprad__reo['f']
    return vzxkn__mkfu


def getitem_arr_tup(arr_tup, ind):
    xrxt__zuz = [arr[ind] for arr in arr_tup]
    return tuple(xrxt__zuz)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    lfkde__impp = arr_tup.count
    bznod__nnee = 'def f(arr_tup, ind):\n'
    bznod__nnee += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(lfkde__impp)]), ',' if lfkde__impp == 1 else
        '')
    tprad__reo = {}
    exec(bznod__nnee, {}, tprad__reo)
    yeo__ozbn = tprad__reo['f']
    return yeo__ozbn


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, obht__qlrn in zip(arr_tup, val_tup):
        arr[ind] = obht__qlrn


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    lfkde__impp = arr_tup.count
    bznod__nnee = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(lfkde__impp):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            bznod__nnee += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            bznod__nnee += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    bznod__nnee += '  return\n'
    tprad__reo = {}
    exec(bznod__nnee, {}, tprad__reo)
    yeo__ozbn = tprad__reo['f']
    return yeo__ozbn


def test():
    import time
    dwg__vnxm = time.time()
    zqvtc__vwkn = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((zqvtc__vwkn,), 0, 3, data)
    print('compile time', time.time() - dwg__vnxm)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    tvni__ukfox = np.random.ranf(n)
    yucw__omsry = pd.DataFrame({'A': tvni__ukfox, 'B': data[0], 'C': data[1]})
    dwg__vnxm = time.time()
    gsa__hvggo = yucw__omsry.sort_values('A', inplace=False)
    abn__vhazu = time.time()
    sort((tvni__ukfox,), 0, n, data)
    print('Bodo', time.time() - abn__vhazu, 'Numpy', abn__vhazu - dwg__vnxm)
    np.testing.assert_almost_equal(data[0], gsa__hvggo.B.values)
    np.testing.assert_almost_equal(data[1], gsa__hvggo.C.values)


if __name__ == '__main__':
    test()
