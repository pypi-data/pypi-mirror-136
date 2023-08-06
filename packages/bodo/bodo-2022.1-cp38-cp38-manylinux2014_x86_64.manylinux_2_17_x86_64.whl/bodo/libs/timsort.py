import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    xab__utg = hi - lo
    if xab__utg < 2:
        return
    if xab__utg < MIN_MERGE:
        jfyqv__hfmqd = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + jfyqv__hfmqd, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    hsf__fpe = minRunLength(xab__utg)
    while True:
        hmee__ijllj = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if hmee__ijllj < hsf__fpe:
            mrkh__ebqx = xab__utg if xab__utg <= hsf__fpe else hsf__fpe
            binarySort(key_arrs, lo, lo + mrkh__ebqx, lo + hmee__ijllj, data)
            hmee__ijllj = mrkh__ebqx
        stackSize = pushRun(stackSize, runBase, runLen, lo, hmee__ijllj)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += hmee__ijllj
        xab__utg -= hmee__ijllj
        if xab__utg == 0:
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
        qdmh__unesp = getitem_arr_tup(key_arrs, start)
        lwca__xpz = getitem_arr_tup(data, start)
        olso__dam = lo
        oacnb__jllt = start
        assert olso__dam <= oacnb__jllt
        while olso__dam < oacnb__jllt:
            wpfx__khu = olso__dam + oacnb__jllt >> 1
            if qdmh__unesp < getitem_arr_tup(key_arrs, wpfx__khu):
                oacnb__jllt = wpfx__khu
            else:
                olso__dam = wpfx__khu + 1
        assert olso__dam == oacnb__jllt
        n = start - olso__dam
        copyRange_tup(key_arrs, olso__dam, key_arrs, olso__dam + 1, n)
        copyRange_tup(data, olso__dam, data, olso__dam + 1, n)
        setitem_arr_tup(key_arrs, olso__dam, qdmh__unesp)
        setitem_arr_tup(data, olso__dam, lwca__xpz)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    zmmtx__bfyze = lo + 1
    if zmmtx__bfyze == hi:
        return 1
    if getitem_arr_tup(key_arrs, zmmtx__bfyze) < getitem_arr_tup(key_arrs, lo):
        zmmtx__bfyze += 1
        while zmmtx__bfyze < hi and getitem_arr_tup(key_arrs, zmmtx__bfyze
            ) < getitem_arr_tup(key_arrs, zmmtx__bfyze - 1):
            zmmtx__bfyze += 1
        reverseRange(key_arrs, lo, zmmtx__bfyze, data)
    else:
        zmmtx__bfyze += 1
        while zmmtx__bfyze < hi and getitem_arr_tup(key_arrs, zmmtx__bfyze
            ) >= getitem_arr_tup(key_arrs, zmmtx__bfyze - 1):
            zmmtx__bfyze += 1
    return zmmtx__bfyze - lo


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
    zpqd__cia = 0
    while n >= MIN_MERGE:
        zpqd__cia |= n & 1
        n >>= 1
    return n + zpqd__cia


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    qkxb__awu = len(key_arrs[0])
    tmpLength = (qkxb__awu >> 1 if qkxb__awu < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    ksfz__ckezt = (5 if qkxb__awu < 120 else 10 if qkxb__awu < 1542 else 19 if
        qkxb__awu < 119151 else 40)
    runBase = np.empty(ksfz__ckezt, np.int64)
    runLen = np.empty(ksfz__ckezt, np.int64)
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
    titz__zuob = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert titz__zuob >= 0
    base1 += titz__zuob
    len1 -= titz__zuob
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
    rnv__hipvb = 0
    fkbu__zxrgg = 1
    if key > getitem_arr_tup(arr, base + hint):
        jgbqu__txkni = _len - hint
        while fkbu__zxrgg < jgbqu__txkni and key > getitem_arr_tup(arr, 
            base + hint + fkbu__zxrgg):
            rnv__hipvb = fkbu__zxrgg
            fkbu__zxrgg = (fkbu__zxrgg << 1) + 1
            if fkbu__zxrgg <= 0:
                fkbu__zxrgg = jgbqu__txkni
        if fkbu__zxrgg > jgbqu__txkni:
            fkbu__zxrgg = jgbqu__txkni
        rnv__hipvb += hint
        fkbu__zxrgg += hint
    else:
        jgbqu__txkni = hint + 1
        while fkbu__zxrgg < jgbqu__txkni and key <= getitem_arr_tup(arr, 
            base + hint - fkbu__zxrgg):
            rnv__hipvb = fkbu__zxrgg
            fkbu__zxrgg = (fkbu__zxrgg << 1) + 1
            if fkbu__zxrgg <= 0:
                fkbu__zxrgg = jgbqu__txkni
        if fkbu__zxrgg > jgbqu__txkni:
            fkbu__zxrgg = jgbqu__txkni
        tmp = rnv__hipvb
        rnv__hipvb = hint - fkbu__zxrgg
        fkbu__zxrgg = hint - tmp
    assert -1 <= rnv__hipvb and rnv__hipvb < fkbu__zxrgg and fkbu__zxrgg <= _len
    rnv__hipvb += 1
    while rnv__hipvb < fkbu__zxrgg:
        rwze__qxa = rnv__hipvb + (fkbu__zxrgg - rnv__hipvb >> 1)
        if key > getitem_arr_tup(arr, base + rwze__qxa):
            rnv__hipvb = rwze__qxa + 1
        else:
            fkbu__zxrgg = rwze__qxa
    assert rnv__hipvb == fkbu__zxrgg
    return fkbu__zxrgg


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    fkbu__zxrgg = 1
    rnv__hipvb = 0
    if key < getitem_arr_tup(arr, base + hint):
        jgbqu__txkni = hint + 1
        while fkbu__zxrgg < jgbqu__txkni and key < getitem_arr_tup(arr, 
            base + hint - fkbu__zxrgg):
            rnv__hipvb = fkbu__zxrgg
            fkbu__zxrgg = (fkbu__zxrgg << 1) + 1
            if fkbu__zxrgg <= 0:
                fkbu__zxrgg = jgbqu__txkni
        if fkbu__zxrgg > jgbqu__txkni:
            fkbu__zxrgg = jgbqu__txkni
        tmp = rnv__hipvb
        rnv__hipvb = hint - fkbu__zxrgg
        fkbu__zxrgg = hint - tmp
    else:
        jgbqu__txkni = _len - hint
        while fkbu__zxrgg < jgbqu__txkni and key >= getitem_arr_tup(arr, 
            base + hint + fkbu__zxrgg):
            rnv__hipvb = fkbu__zxrgg
            fkbu__zxrgg = (fkbu__zxrgg << 1) + 1
            if fkbu__zxrgg <= 0:
                fkbu__zxrgg = jgbqu__txkni
        if fkbu__zxrgg > jgbqu__txkni:
            fkbu__zxrgg = jgbqu__txkni
        rnv__hipvb += hint
        fkbu__zxrgg += hint
    assert -1 <= rnv__hipvb and rnv__hipvb < fkbu__zxrgg and fkbu__zxrgg <= _len
    rnv__hipvb += 1
    while rnv__hipvb < fkbu__zxrgg:
        rwze__qxa = rnv__hipvb + (fkbu__zxrgg - rnv__hipvb >> 1)
        if key < getitem_arr_tup(arr, base + rwze__qxa):
            fkbu__zxrgg = rwze__qxa
        else:
            rnv__hipvb = rwze__qxa + 1
    assert rnv__hipvb == fkbu__zxrgg
    return fkbu__zxrgg


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
        vryre__hzb = 0
        oby__wlpzs = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                oby__wlpzs += 1
                vryre__hzb = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                vryre__hzb += 1
                oby__wlpzs = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not vryre__hzb | oby__wlpzs < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            vryre__hzb = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if vryre__hzb != 0:
                copyRange_tup(tmp, cursor1, arr, dest, vryre__hzb)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, vryre__hzb)
                dest += vryre__hzb
                cursor1 += vryre__hzb
                len1 -= vryre__hzb
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            oby__wlpzs = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if oby__wlpzs != 0:
                copyRange_tup(arr, cursor2, arr, dest, oby__wlpzs)
                copyRange_tup(arr_data, cursor2, arr_data, dest, oby__wlpzs)
                dest += oby__wlpzs
                cursor2 += oby__wlpzs
                len2 -= oby__wlpzs
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
            if not vryre__hzb >= MIN_GALLOP | oby__wlpzs >= MIN_GALLOP:
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
        vryre__hzb = 0
        oby__wlpzs = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                vryre__hzb += 1
                oby__wlpzs = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                oby__wlpzs += 1
                vryre__hzb = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not vryre__hzb | oby__wlpzs < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            vryre__hzb = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if vryre__hzb != 0:
                dest -= vryre__hzb
                cursor1 -= vryre__hzb
                len1 -= vryre__hzb
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, vryre__hzb)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    vryre__hzb)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            oby__wlpzs = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if oby__wlpzs != 0:
                dest -= oby__wlpzs
                cursor2 -= oby__wlpzs
                len2 -= oby__wlpzs
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, oby__wlpzs)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    oby__wlpzs)
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
            if not vryre__hzb >= MIN_GALLOP | oby__wlpzs >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    foi__ban = len(key_arrs[0])
    if tmpLength < minCapacity:
        rwlet__edj = minCapacity
        rwlet__edj |= rwlet__edj >> 1
        rwlet__edj |= rwlet__edj >> 2
        rwlet__edj |= rwlet__edj >> 4
        rwlet__edj |= rwlet__edj >> 8
        rwlet__edj |= rwlet__edj >> 16
        rwlet__edj += 1
        if rwlet__edj < 0:
            rwlet__edj = minCapacity
        else:
            rwlet__edj = min(rwlet__edj, foi__ban >> 1)
        tmp = alloc_arr_tup(rwlet__edj, key_arrs)
        tmp_data = alloc_arr_tup(rwlet__edj, data)
        tmpLength = rwlet__edj
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        pbotj__olhki = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = pbotj__olhki


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    nze__qtmy = arr_tup.count
    rur__icqc = 'def f(arr_tup, lo, hi):\n'
    for i in range(nze__qtmy):
        rur__icqc += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        rur__icqc += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        rur__icqc += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    rur__icqc += '  return\n'
    tmyrs__izsg = {}
    exec(rur__icqc, {}, tmyrs__izsg)
    fbpn__qkclk = tmyrs__izsg['f']
    return fbpn__qkclk


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    nze__qtmy = src_arr_tup.count
    assert nze__qtmy == dst_arr_tup.count
    rur__icqc = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(nze__qtmy):
        rur__icqc += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    rur__icqc += '  return\n'
    tmyrs__izsg = {}
    exec(rur__icqc, {'copyRange': copyRange}, tmyrs__izsg)
    eyiq__azzd = tmyrs__izsg['f']
    return eyiq__azzd


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    nze__qtmy = src_arr_tup.count
    assert nze__qtmy == dst_arr_tup.count
    rur__icqc = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(nze__qtmy):
        rur__icqc += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    rur__icqc += '  return\n'
    tmyrs__izsg = {}
    exec(rur__icqc, {'copyElement': copyElement}, tmyrs__izsg)
    eyiq__azzd = tmyrs__izsg['f']
    return eyiq__azzd


def getitem_arr_tup(arr_tup, ind):
    fvkrf__dte = [arr[ind] for arr in arr_tup]
    return tuple(fvkrf__dte)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    nze__qtmy = arr_tup.count
    rur__icqc = 'def f(arr_tup, ind):\n'
    rur__icqc += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(nze__qtmy)]), ',' if nze__qtmy == 1 else '')
    tmyrs__izsg = {}
    exec(rur__icqc, {}, tmyrs__izsg)
    ljp__rjdwt = tmyrs__izsg['f']
    return ljp__rjdwt


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, ygv__itr in zip(arr_tup, val_tup):
        arr[ind] = ygv__itr


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    nze__qtmy = arr_tup.count
    rur__icqc = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(nze__qtmy):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            rur__icqc += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            rur__icqc += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    rur__icqc += '  return\n'
    tmyrs__izsg = {}
    exec(rur__icqc, {}, tmyrs__izsg)
    ljp__rjdwt = tmyrs__izsg['f']
    return ljp__rjdwt


def test():
    import time
    jrgsi__nkrsh = time.time()
    zadti__auw = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((zadti__auw,), 0, 3, data)
    print('compile time', time.time() - jrgsi__nkrsh)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    nkyt__vlfk = np.random.ranf(n)
    aui__hdi = pd.DataFrame({'A': nkyt__vlfk, 'B': data[0], 'C': data[1]})
    jrgsi__nkrsh = time.time()
    qsxg__mzf = aui__hdi.sort_values('A', inplace=False)
    xewf__quf = time.time()
    sort((nkyt__vlfk,), 0, n, data)
    print('Bodo', time.time() - xewf__quf, 'Numpy', xewf__quf - jrgsi__nkrsh)
    np.testing.assert_almost_equal(data[0], qsxg__mzf.B.values)
    np.testing.assert_almost_equal(data[1], qsxg__mzf.C.values)


if __name__ == '__main__':
    test()
