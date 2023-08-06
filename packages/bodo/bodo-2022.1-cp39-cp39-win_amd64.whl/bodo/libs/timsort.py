import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    rch__aava = hi - lo
    if rch__aava < 2:
        return
    if rch__aava < MIN_MERGE:
        bsz__djnc = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + bsz__djnc, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    tdelf__voe = minRunLength(rch__aava)
    while True:
        fzho__tdm = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if fzho__tdm < tdelf__voe:
            bebmp__yzdmt = rch__aava if rch__aava <= tdelf__voe else tdelf__voe
            binarySort(key_arrs, lo, lo + bebmp__yzdmt, lo + fzho__tdm, data)
            fzho__tdm = bebmp__yzdmt
        stackSize = pushRun(stackSize, runBase, runLen, lo, fzho__tdm)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += fzho__tdm
        rch__aava -= fzho__tdm
        if rch__aava == 0:
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
        jfuio__ykexm = getitem_arr_tup(key_arrs, start)
        jkw__pfbpt = getitem_arr_tup(data, start)
        jwuyv__zpalj = lo
        uuj__cmtw = start
        assert jwuyv__zpalj <= uuj__cmtw
        while jwuyv__zpalj < uuj__cmtw:
            vtu__qytzj = jwuyv__zpalj + uuj__cmtw >> 1
            if jfuio__ykexm < getitem_arr_tup(key_arrs, vtu__qytzj):
                uuj__cmtw = vtu__qytzj
            else:
                jwuyv__zpalj = vtu__qytzj + 1
        assert jwuyv__zpalj == uuj__cmtw
        n = start - jwuyv__zpalj
        copyRange_tup(key_arrs, jwuyv__zpalj, key_arrs, jwuyv__zpalj + 1, n)
        copyRange_tup(data, jwuyv__zpalj, data, jwuyv__zpalj + 1, n)
        setitem_arr_tup(key_arrs, jwuyv__zpalj, jfuio__ykexm)
        setitem_arr_tup(data, jwuyv__zpalj, jkw__pfbpt)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    keh__cbusa = lo + 1
    if keh__cbusa == hi:
        return 1
    if getitem_arr_tup(key_arrs, keh__cbusa) < getitem_arr_tup(key_arrs, lo):
        keh__cbusa += 1
        while keh__cbusa < hi and getitem_arr_tup(key_arrs, keh__cbusa
            ) < getitem_arr_tup(key_arrs, keh__cbusa - 1):
            keh__cbusa += 1
        reverseRange(key_arrs, lo, keh__cbusa, data)
    else:
        keh__cbusa += 1
        while keh__cbusa < hi and getitem_arr_tup(key_arrs, keh__cbusa
            ) >= getitem_arr_tup(key_arrs, keh__cbusa - 1):
            keh__cbusa += 1
    return keh__cbusa - lo


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
    lpwb__tym = 0
    while n >= MIN_MERGE:
        lpwb__tym |= n & 1
        n >>= 1
    return n + lpwb__tym


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    wiylx__hgds = len(key_arrs[0])
    tmpLength = (wiylx__hgds >> 1 if wiylx__hgds < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    ntn__tccvw = (5 if wiylx__hgds < 120 else 10 if wiylx__hgds < 1542 else
        19 if wiylx__hgds < 119151 else 40)
    runBase = np.empty(ntn__tccvw, np.int64)
    runLen = np.empty(ntn__tccvw, np.int64)
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
    pzu__fnv = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert pzu__fnv >= 0
    base1 += pzu__fnv
    len1 -= pzu__fnv
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
    zrgps__zpll = 0
    symcy__kpiqz = 1
    if key > getitem_arr_tup(arr, base + hint):
        xqykr__mwrn = _len - hint
        while symcy__kpiqz < xqykr__mwrn and key > getitem_arr_tup(arr, 
            base + hint + symcy__kpiqz):
            zrgps__zpll = symcy__kpiqz
            symcy__kpiqz = (symcy__kpiqz << 1) + 1
            if symcy__kpiqz <= 0:
                symcy__kpiqz = xqykr__mwrn
        if symcy__kpiqz > xqykr__mwrn:
            symcy__kpiqz = xqykr__mwrn
        zrgps__zpll += hint
        symcy__kpiqz += hint
    else:
        xqykr__mwrn = hint + 1
        while symcy__kpiqz < xqykr__mwrn and key <= getitem_arr_tup(arr, 
            base + hint - symcy__kpiqz):
            zrgps__zpll = symcy__kpiqz
            symcy__kpiqz = (symcy__kpiqz << 1) + 1
            if symcy__kpiqz <= 0:
                symcy__kpiqz = xqykr__mwrn
        if symcy__kpiqz > xqykr__mwrn:
            symcy__kpiqz = xqykr__mwrn
        tmp = zrgps__zpll
        zrgps__zpll = hint - symcy__kpiqz
        symcy__kpiqz = hint - tmp
    assert -1 <= zrgps__zpll and zrgps__zpll < symcy__kpiqz and symcy__kpiqz <= _len
    zrgps__zpll += 1
    while zrgps__zpll < symcy__kpiqz:
        bhn__ntw = zrgps__zpll + (symcy__kpiqz - zrgps__zpll >> 1)
        if key > getitem_arr_tup(arr, base + bhn__ntw):
            zrgps__zpll = bhn__ntw + 1
        else:
            symcy__kpiqz = bhn__ntw
    assert zrgps__zpll == symcy__kpiqz
    return symcy__kpiqz


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    symcy__kpiqz = 1
    zrgps__zpll = 0
    if key < getitem_arr_tup(arr, base + hint):
        xqykr__mwrn = hint + 1
        while symcy__kpiqz < xqykr__mwrn and key < getitem_arr_tup(arr, 
            base + hint - symcy__kpiqz):
            zrgps__zpll = symcy__kpiqz
            symcy__kpiqz = (symcy__kpiqz << 1) + 1
            if symcy__kpiqz <= 0:
                symcy__kpiqz = xqykr__mwrn
        if symcy__kpiqz > xqykr__mwrn:
            symcy__kpiqz = xqykr__mwrn
        tmp = zrgps__zpll
        zrgps__zpll = hint - symcy__kpiqz
        symcy__kpiqz = hint - tmp
    else:
        xqykr__mwrn = _len - hint
        while symcy__kpiqz < xqykr__mwrn and key >= getitem_arr_tup(arr, 
            base + hint + symcy__kpiqz):
            zrgps__zpll = symcy__kpiqz
            symcy__kpiqz = (symcy__kpiqz << 1) + 1
            if symcy__kpiqz <= 0:
                symcy__kpiqz = xqykr__mwrn
        if symcy__kpiqz > xqykr__mwrn:
            symcy__kpiqz = xqykr__mwrn
        zrgps__zpll += hint
        symcy__kpiqz += hint
    assert -1 <= zrgps__zpll and zrgps__zpll < symcy__kpiqz and symcy__kpiqz <= _len
    zrgps__zpll += 1
    while zrgps__zpll < symcy__kpiqz:
        bhn__ntw = zrgps__zpll + (symcy__kpiqz - zrgps__zpll >> 1)
        if key < getitem_arr_tup(arr, base + bhn__ntw):
            symcy__kpiqz = bhn__ntw
        else:
            zrgps__zpll = bhn__ntw + 1
    assert zrgps__zpll == symcy__kpiqz
    return symcy__kpiqz


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
        hit__tie = 0
        foqy__xngke = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                foqy__xngke += 1
                hit__tie = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                hit__tie += 1
                foqy__xngke = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not hit__tie | foqy__xngke < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            hit__tie = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if hit__tie != 0:
                copyRange_tup(tmp, cursor1, arr, dest, hit__tie)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, hit__tie)
                dest += hit__tie
                cursor1 += hit__tie
                len1 -= hit__tie
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            foqy__xngke = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if foqy__xngke != 0:
                copyRange_tup(arr, cursor2, arr, dest, foqy__xngke)
                copyRange_tup(arr_data, cursor2, arr_data, dest, foqy__xngke)
                dest += foqy__xngke
                cursor2 += foqy__xngke
                len2 -= foqy__xngke
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
            if not hit__tie >= MIN_GALLOP | foqy__xngke >= MIN_GALLOP:
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
        hit__tie = 0
        foqy__xngke = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                hit__tie += 1
                foqy__xngke = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                foqy__xngke += 1
                hit__tie = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not hit__tie | foqy__xngke < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            hit__tie = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if hit__tie != 0:
                dest -= hit__tie
                cursor1 -= hit__tie
                len1 -= hit__tie
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, hit__tie)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    hit__tie)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            foqy__xngke = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if foqy__xngke != 0:
                dest -= foqy__xngke
                cursor2 -= foqy__xngke
                len2 -= foqy__xngke
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, foqy__xngke)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    foqy__xngke)
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
            if not hit__tie >= MIN_GALLOP | foqy__xngke >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    rmj__khjr = len(key_arrs[0])
    if tmpLength < minCapacity:
        rigux__ujkfw = minCapacity
        rigux__ujkfw |= rigux__ujkfw >> 1
        rigux__ujkfw |= rigux__ujkfw >> 2
        rigux__ujkfw |= rigux__ujkfw >> 4
        rigux__ujkfw |= rigux__ujkfw >> 8
        rigux__ujkfw |= rigux__ujkfw >> 16
        rigux__ujkfw += 1
        if rigux__ujkfw < 0:
            rigux__ujkfw = minCapacity
        else:
            rigux__ujkfw = min(rigux__ujkfw, rmj__khjr >> 1)
        tmp = alloc_arr_tup(rigux__ujkfw, key_arrs)
        tmp_data = alloc_arr_tup(rigux__ujkfw, data)
        tmpLength = rigux__ujkfw
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        iqrfe__jljf = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = iqrfe__jljf


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    cjrg__vaq = arr_tup.count
    hckjm__slmf = 'def f(arr_tup, lo, hi):\n'
    for i in range(cjrg__vaq):
        hckjm__slmf += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        hckjm__slmf += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        hckjm__slmf += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    hckjm__slmf += '  return\n'
    lsckx__uktx = {}
    exec(hckjm__slmf, {}, lsckx__uktx)
    sim__cxxmp = lsckx__uktx['f']
    return sim__cxxmp


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    cjrg__vaq = src_arr_tup.count
    assert cjrg__vaq == dst_arr_tup.count
    hckjm__slmf = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(cjrg__vaq):
        hckjm__slmf += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    hckjm__slmf += '  return\n'
    lsckx__uktx = {}
    exec(hckjm__slmf, {'copyRange': copyRange}, lsckx__uktx)
    dema__tdb = lsckx__uktx['f']
    return dema__tdb


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    cjrg__vaq = src_arr_tup.count
    assert cjrg__vaq == dst_arr_tup.count
    hckjm__slmf = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(cjrg__vaq):
        hckjm__slmf += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    hckjm__slmf += '  return\n'
    lsckx__uktx = {}
    exec(hckjm__slmf, {'copyElement': copyElement}, lsckx__uktx)
    dema__tdb = lsckx__uktx['f']
    return dema__tdb


def getitem_arr_tup(arr_tup, ind):
    cwk__jseqg = [arr[ind] for arr in arr_tup]
    return tuple(cwk__jseqg)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    cjrg__vaq = arr_tup.count
    hckjm__slmf = 'def f(arr_tup, ind):\n'
    hckjm__slmf += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(cjrg__vaq)]), ',' if cjrg__vaq == 1 else '')
    lsckx__uktx = {}
    exec(hckjm__slmf, {}, lsckx__uktx)
    clgb__whxew = lsckx__uktx['f']
    return clgb__whxew


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, qkukj__yyo in zip(arr_tup, val_tup):
        arr[ind] = qkukj__yyo


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    cjrg__vaq = arr_tup.count
    hckjm__slmf = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(cjrg__vaq):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            hckjm__slmf += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            hckjm__slmf += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    hckjm__slmf += '  return\n'
    lsckx__uktx = {}
    exec(hckjm__slmf, {}, lsckx__uktx)
    clgb__whxew = lsckx__uktx['f']
    return clgb__whxew


def test():
    import time
    mvq__irceh = time.time()
    zjh__ojety = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((zjh__ojety,), 0, 3, data)
    print('compile time', time.time() - mvq__irceh)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    nnm__ysv = np.random.ranf(n)
    njd__epj = pd.DataFrame({'A': nnm__ysv, 'B': data[0], 'C': data[1]})
    mvq__irceh = time.time()
    gjtsj__ffibq = njd__epj.sort_values('A', inplace=False)
    mbdd__smijt = time.time()
    sort((nnm__ysv,), 0, n, data)
    print('Bodo', time.time() - mbdd__smijt, 'Numpy', mbdd__smijt - mvq__irceh)
    np.testing.assert_almost_equal(data[0], gjtsj__ffibq.B.values)
    np.testing.assert_almost_equal(data[1], gjtsj__ffibq.C.values)


if __name__ == '__main__':
    test()
