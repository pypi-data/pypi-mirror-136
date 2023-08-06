"""implementations of rolling window functions (sequential and parallel)
"""
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.core.imputils import impl_ret_borrowed
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_builtin, overload, register_jitable
import bodo
from bodo.libs.distributed_api import Reduce_Type
from bodo.utils.typing import BodoError, get_overload_const_func, get_overload_const_str, is_const_func_type, is_overload_constant_bool, is_overload_constant_str, is_overload_none, is_overload_true
from bodo.utils.utils import unliteral_all
supported_rolling_funcs = ('sum', 'mean', 'var', 'std', 'count', 'median',
    'min', 'max', 'cov', 'corr', 'apply')
unsupported_rolling_methods = ['skew', 'kurt', 'aggregate', 'quantile', 'sem']


def rolling_fixed(arr, win):
    return arr


def rolling_variable(arr, on_arr, win):
    return arr


def rolling_cov(arr, arr2, win):
    return arr


def rolling_corr(arr, arr2, win):
    return arr


@infer_global(rolling_cov)
@infer_global(rolling_corr)
class RollingCovType(AbstractTemplate):

    def generic(self, args, kws):
        arr = args[0]
        yjl__sjjo = arr.copy(dtype=types.float64)
        return signature(yjl__sjjo, *unliteral_all(args))


@lower_builtin(rolling_corr, types.VarArg(types.Any))
@lower_builtin(rolling_cov, types.VarArg(types.Any))
def lower_rolling_corr_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


@overload(rolling_fixed, no_unliteral=True)
def overload_rolling_fixed(arr, index_arr, win, minp, center, fname, raw=
    True, parallel=False):
    assert is_overload_constant_bool(raw
        ), 'raw argument should be constant bool'
    if is_const_func_type(fname):
        func = _get_apply_func(fname)
        return (lambda arr, index_arr, win, minp, center, fname, raw=True,
            parallel=False: roll_fixed_apply(arr, index_arr, win, minp,
            center, parallel, func, raw))
    assert is_overload_constant_str(fname)
    dtgjo__rhvi = get_overload_const_str(fname)
    if dtgjo__rhvi not in ('sum', 'mean', 'var', 'std', 'count', 'median',
        'min', 'max'):
        raise BodoError('invalid rolling (fixed window) function {}'.format
            (dtgjo__rhvi))
    if dtgjo__rhvi in ('median', 'min', 'max'):
        mkh__vaf = 'def kernel_func(A):\n'
        mkh__vaf += '  if np.isnan(A).sum() != 0: return np.nan\n'
        mkh__vaf += '  return np.{}(A)\n'.format(dtgjo__rhvi)
        nau__zny = {}
        exec(mkh__vaf, {'np': np}, nau__zny)
        kernel_func = register_jitable(nau__zny['kernel_func'])
        return (lambda arr, index_arr, win, minp, center, fname, raw=True,
            parallel=False: roll_fixed_apply(arr, index_arr, win, minp,
            center, parallel, kernel_func))
    init_kernel, add_kernel, remove_kernel, calc_kernel = linear_kernels[
        dtgjo__rhvi]
    return (lambda arr, index_arr, win, minp, center, fname, raw=True,
        parallel=False: roll_fixed_linear_generic(arr, win, minp, center,
        parallel, init_kernel, add_kernel, remove_kernel, calc_kernel))


@overload(rolling_variable, no_unliteral=True)
def overload_rolling_variable(arr, on_arr, index_arr, win, minp, center,
    fname, raw=True, parallel=False):
    assert is_overload_constant_bool(raw)
    if is_const_func_type(fname):
        func = _get_apply_func(fname)
        return (lambda arr, on_arr, index_arr, win, minp, center, fname,
            raw=True, parallel=False: roll_variable_apply(arr, on_arr,
            index_arr, win, minp, center, parallel, func, raw))
    assert is_overload_constant_str(fname)
    dtgjo__rhvi = get_overload_const_str(fname)
    if dtgjo__rhvi not in ('sum', 'mean', 'var', 'std', 'count', 'median',
        'min', 'max'):
        raise BodoError('invalid rolling (variable window) function {}'.
            format(dtgjo__rhvi))
    if dtgjo__rhvi in ('median', 'min', 'max'):
        mkh__vaf = 'def kernel_func(A):\n'
        mkh__vaf += '  arr  = dropna(A)\n'
        mkh__vaf += '  if len(arr) == 0: return np.nan\n'
        mkh__vaf += '  return np.{}(arr)\n'.format(dtgjo__rhvi)
        nau__zny = {}
        exec(mkh__vaf, {'np': np, 'dropna': _dropna}, nau__zny)
        kernel_func = register_jitable(nau__zny['kernel_func'])
        return (lambda arr, on_arr, index_arr, win, minp, center, fname,
            raw=True, parallel=False: roll_variable_apply(arr, on_arr,
            index_arr, win, minp, center, parallel, kernel_func))
    init_kernel, add_kernel, remove_kernel, calc_kernel = linear_kernels[
        dtgjo__rhvi]
    return (lambda arr, on_arr, index_arr, win, minp, center, fname, raw=
        True, parallel=False: roll_var_linear_generic(arr, on_arr, win,
        minp, center, parallel, init_kernel, add_kernel, remove_kernel,
        calc_kernel))


def _get_apply_func(f_type):
    func = get_overload_const_func(f_type, None)
    return bodo.compiler.udf_jit(func)


comm_border_tag = 22


@register_jitable
def roll_fixed_linear_generic(in_arr, win, minp, center, parallel,
    init_data, add_obs, remove_obs, calc_out):
    _validate_roll_fixed_args(win, minp)
    in_arr = prep_values(in_arr)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    if parallel:
        halo_size = np.int32(win // 2) if center else np.int32(win - 1)
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data(in_arr, win, minp, center, rank,
                n_pes, init_data, add_obs, remove_obs, calc_out)
        ahmy__hkanc = _border_icomm(in_arr, rank, n_pes, halo_size, True,
            center)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            carbd__rzy) = ahmy__hkanc
    output, data = roll_fixed_linear_generic_seq(in_arr, win, minp, center,
        init_data, add_obs, remove_obs, calc_out)
    if parallel:
        _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, center)
        if center and rank != n_pes - 1:
            bodo.libs.distributed_api.wait(carbd__rzy, True)
            for wjtvf__jfin in range(0, halo_size):
                data = add_obs(r_recv_buff[wjtvf__jfin], *data)
                tipds__sdxav = in_arr[N + wjtvf__jfin - win]
                data = remove_obs(tipds__sdxav, *data)
                output[N + wjtvf__jfin - offset] = calc_out(minp, *data)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            data = init_data()
            for wjtvf__jfin in range(0, halo_size):
                data = add_obs(l_recv_buff[wjtvf__jfin], *data)
            for wjtvf__jfin in range(0, win - 1):
                data = add_obs(in_arr[wjtvf__jfin], *data)
                if wjtvf__jfin > offset:
                    tipds__sdxav = l_recv_buff[wjtvf__jfin - offset - 1]
                    data = remove_obs(tipds__sdxav, *data)
                if wjtvf__jfin >= offset:
                    output[wjtvf__jfin - offset] = calc_out(minp, *data)
    return output


@register_jitable
def roll_fixed_linear_generic_seq(in_arr, win, minp, center, init_data,
    add_obs, remove_obs, calc_out):
    data = init_data()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    output = np.empty(N, dtype=np.float64)
    aoov__msj = max(minp, 1) - 1
    aoov__msj = min(aoov__msj, N)
    for wjtvf__jfin in range(0, aoov__msj):
        data = add_obs(in_arr[wjtvf__jfin], *data)
        if wjtvf__jfin >= offset:
            output[wjtvf__jfin - offset] = calc_out(minp, *data)
    for wjtvf__jfin in range(aoov__msj, N):
        val = in_arr[wjtvf__jfin]
        data = add_obs(val, *data)
        if wjtvf__jfin > win - 1:
            tipds__sdxav = in_arr[wjtvf__jfin - win]
            data = remove_obs(tipds__sdxav, *data)
        output[wjtvf__jfin - offset] = calc_out(minp, *data)
    qqlyp__cek = data
    for wjtvf__jfin in range(N, N + offset):
        if wjtvf__jfin > win - 1:
            tipds__sdxav = in_arr[wjtvf__jfin - win]
            data = remove_obs(tipds__sdxav, *data)
        output[wjtvf__jfin - offset] = calc_out(minp, *data)
    return output, qqlyp__cek


def roll_fixed_apply(in_arr, index_arr, win, minp, center, parallel,
    kernel_func, raw=True):
    pass


@overload(roll_fixed_apply, no_unliteral=True)
def overload_roll_fixed_apply(in_arr, index_arr, win, minp, center,
    parallel, kernel_func, raw=True):
    assert is_overload_constant_bool(raw)
    return roll_fixed_apply_impl


def roll_fixed_apply_impl(in_arr, index_arr, win, minp, center, parallel,
    kernel_func, raw=True):
    _validate_roll_fixed_args(win, minp)
    in_arr = prep_values(in_arr)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    index_arr = fix_index_arr(index_arr)
    if parallel:
        halo_size = np.int32(win // 2) if center else np.int32(win - 1)
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_apply(in_arr, index_arr, win, minp,
                center, rank, n_pes, kernel_func, raw)
        ahmy__hkanc = _border_icomm(in_arr, rank, n_pes, halo_size, True,
            center)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            carbd__rzy) = ahmy__hkanc
        if raw == False:
            beg__ubxqg = _border_icomm(index_arr, rank, n_pes, halo_size, 
                True, center)
            (l_recv_buff_idx, r_recv_buff_idx, ohppi__yocp, xhbft__sgxva,
                oevc__irszk, vei__qvu) = beg__ubxqg
    output = roll_fixed_apply_seq(in_arr, index_arr, win, minp, center,
        kernel_func, raw)
    if parallel:
        _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, center)
        if raw == False:
            _border_send_wait(xhbft__sgxva, ohppi__yocp, rank, n_pes, True,
                center)
        if center and rank != n_pes - 1:
            bodo.libs.distributed_api.wait(carbd__rzy, True)
            if raw == False:
                bodo.libs.distributed_api.wait(vei__qvu, True)
            recv_right_compute(output, in_arr, index_arr, N, win, minp,
                offset, r_recv_buff, r_recv_buff_idx, kernel_func, raw)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            if raw == False:
                bodo.libs.distributed_api.wait(oevc__irszk, True)
            recv_left_compute(output, in_arr, index_arr, win, minp, offset,
                l_recv_buff, l_recv_buff_idx, kernel_func, raw)
    return output


def recv_right_compute(output, in_arr, index_arr, N, win, minp, offset,
    r_recv_buff, r_recv_buff_idx, kernel_func, raw):
    pass


@overload(recv_right_compute, no_unliteral=True)
def overload_recv_right_compute(output, in_arr, index_arr, N, win, minp,
    offset, r_recv_buff, r_recv_buff_idx, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, N, win, minp, offset,
            r_recv_buff, r_recv_buff_idx, kernel_func, raw):
            qqlyp__cek = np.concatenate((in_arr[N - win + 1:], r_recv_buff))
            pecqh__sfs = 0
            for wjtvf__jfin in range(max(N - offset, 0), N):
                data = qqlyp__cek[pecqh__sfs:pecqh__sfs + win]
                if win - np.isnan(data).sum() < minp:
                    output[wjtvf__jfin] = np.nan
                else:
                    output[wjtvf__jfin] = kernel_func(data)
                pecqh__sfs += 1
        return impl

    def impl_series(output, in_arr, index_arr, N, win, minp, offset,
        r_recv_buff, r_recv_buff_idx, kernel_func, raw):
        qqlyp__cek = np.concatenate((in_arr[N - win + 1:], r_recv_buff))
        eme__ncse = np.concatenate((index_arr[N - win + 1:], r_recv_buff_idx))
        pecqh__sfs = 0
        for wjtvf__jfin in range(max(N - offset, 0), N):
            data = qqlyp__cek[pecqh__sfs:pecqh__sfs + win]
            if win - np.isnan(data).sum() < minp:
                output[wjtvf__jfin] = np.nan
            else:
                output[wjtvf__jfin] = kernel_func(pd.Series(data, eme__ncse
                    [pecqh__sfs:pecqh__sfs + win]))
            pecqh__sfs += 1
    return impl_series


def recv_left_compute(output, in_arr, index_arr, win, minp, offset,
    l_recv_buff, l_recv_buff_idx, kernel_func, raw):
    pass


@overload(recv_left_compute, no_unliteral=True)
def overload_recv_left_compute(output, in_arr, index_arr, win, minp, offset,
    l_recv_buff, l_recv_buff_idx, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, win, minp, offset, l_recv_buff,
            l_recv_buff_idx, kernel_func, raw):
            qqlyp__cek = np.concatenate((l_recv_buff, in_arr[:win - 1]))
            for wjtvf__jfin in range(0, win - offset - 1):
                data = qqlyp__cek[wjtvf__jfin:wjtvf__jfin + win]
                if win - np.isnan(data).sum() < minp:
                    output[wjtvf__jfin] = np.nan
                else:
                    output[wjtvf__jfin] = kernel_func(data)
        return impl

    def impl_series(output, in_arr, index_arr, win, minp, offset,
        l_recv_buff, l_recv_buff_idx, kernel_func, raw):
        qqlyp__cek = np.concatenate((l_recv_buff, in_arr[:win - 1]))
        eme__ncse = np.concatenate((l_recv_buff_idx, index_arr[:win - 1]))
        for wjtvf__jfin in range(0, win - offset - 1):
            data = qqlyp__cek[wjtvf__jfin:wjtvf__jfin + win]
            if win - np.isnan(data).sum() < minp:
                output[wjtvf__jfin] = np.nan
            else:
                output[wjtvf__jfin] = kernel_func(pd.Series(data, eme__ncse
                    [wjtvf__jfin:wjtvf__jfin + win]))
    return impl_series


def roll_fixed_apply_seq(in_arr, index_arr, win, minp, center, kernel_func,
    raw=True):
    pass


@overload(roll_fixed_apply_seq, no_unliteral=True)
def overload_roll_fixed_apply_seq(in_arr, index_arr, win, minp, center,
    kernel_func, raw=True):
    assert is_overload_constant_bool(raw), "'raw' should be constant bool"

    def roll_fixed_apply_seq_impl(in_arr, index_arr, win, minp, center,
        kernel_func, raw=True):
        N = len(in_arr)
        output = np.empty(N, dtype=np.float64)
        offset = (win - 1) // 2 if center else 0
        for wjtvf__jfin in range(0, N):
            start = max(wjtvf__jfin - win + 1 + offset, 0)
            end = min(wjtvf__jfin + 1 + offset, N)
            data = in_arr[start:end]
            if end - start - np.isnan(data).sum() < minp:
                output[wjtvf__jfin] = np.nan
            else:
                output[wjtvf__jfin] = apply_func(kernel_func, data,
                    index_arr, start, end, raw)
        return output
    return roll_fixed_apply_seq_impl


def apply_func(kernel_func, data, index_arr, start, end, raw):
    return kernel_func(data)


@overload(apply_func, no_unliteral=True)
def overload_apply_func(kernel_func, data, index_arr, start, end, raw):
    assert is_overload_constant_bool(raw), "'raw' should be constant bool"
    if is_overload_true(raw):
        return (lambda kernel_func, data, index_arr, start, end, raw:
            kernel_func(data))
    return lambda kernel_func, data, index_arr, start, end, raw: kernel_func(pd
        .Series(data, index_arr[start:end]))


def fix_index_arr(A):
    return A


@overload(fix_index_arr)
def overload_fix_index_arr(A):
    if is_overload_none(A):
        return lambda A: np.zeros(3)
    return lambda A: A


def get_offset_nanos(w):
    out = status = 0
    try:
        out = pd.tseries.frequencies.to_offset(w).nanos
    except:
        status = 1
    return out, status


def offset_to_nanos(w):
    return w


@overload(offset_to_nanos)
def overload_offset_to_nanos(w):
    if isinstance(w, types.Integer):
        return lambda w: w

    def impl(w):
        with numba.objmode(out='int64', status='int64'):
            out, status = get_offset_nanos(w)
        if status != 0:
            raise ValueError('Invalid offset value')
        return out
    return impl


@register_jitable
def roll_var_linear_generic(in_arr, on_arr_dt, win, minp, center, parallel,
    init_data, add_obs, remove_obs, calc_out):
    _validate_roll_var_args(minp, center)
    in_arr = prep_values(in_arr)
    win = offset_to_nanos(win)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    on_arr = cast_dt64_arr_to_int(on_arr_dt)
    N = len(in_arr)
    left_closed = False
    right_closed = True
    if parallel:
        if _is_small_for_parallel_variable(on_arr, win):
            return _handle_small_data_variable(in_arr, on_arr, win, minp,
                rank, n_pes, init_data, add_obs, remove_obs, calc_out)
        ahmy__hkanc = _border_icomm_var(in_arr, on_arr, rank, n_pes, win)
        (l_recv_buff, l_recv_t_buff, r_send_req, fjle__nnxhe, l_recv_req,
            exlwn__zop) = ahmy__hkanc
    start, end = _build_indexer(on_arr, N, win, left_closed, right_closed)
    output = roll_var_linear_generic_seq(in_arr, on_arr, win, minp, start,
        end, init_data, add_obs, remove_obs, calc_out)
    if parallel:
        _border_send_wait(r_send_req, r_send_req, rank, n_pes, True, False)
        _border_send_wait(fjle__nnxhe, fjle__nnxhe, rank, n_pes, True, False)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            bodo.libs.distributed_api.wait(exlwn__zop, True)
            num_zero_starts = 0
            for wjtvf__jfin in range(0, N):
                if start[wjtvf__jfin] != 0:
                    break
                num_zero_starts += 1
            if num_zero_starts == 0:
                return output
            recv_starts = _get_var_recv_starts(on_arr, l_recv_t_buff,
                num_zero_starts, win)
            data = init_data()
            for glnfg__ozlr in range(recv_starts[0], len(l_recv_t_buff)):
                data = add_obs(l_recv_buff[glnfg__ozlr], *data)
            if right_closed:
                data = add_obs(in_arr[0], *data)
            output[0] = calc_out(minp, *data)
            for wjtvf__jfin in range(1, num_zero_starts):
                s = recv_starts[wjtvf__jfin]
                gylvo__fdzrb = end[wjtvf__jfin]
                for glnfg__ozlr in range(recv_starts[wjtvf__jfin - 1], s):
                    data = remove_obs(l_recv_buff[glnfg__ozlr], *data)
                for glnfg__ozlr in range(end[wjtvf__jfin - 1], gylvo__fdzrb):
                    data = add_obs(in_arr[glnfg__ozlr], *data)
                output[wjtvf__jfin] = calc_out(minp, *data)
    return output


@register_jitable(cache=True)
def _get_var_recv_starts(on_arr, l_recv_t_buff, num_zero_starts, win):
    recv_starts = np.zeros(num_zero_starts, np.int64)
    halo_size = len(l_recv_t_buff)
    hxev__mhc = cast_dt64_arr_to_int(on_arr)
    left_closed = False
    ebdld__hhp = hxev__mhc[0] - win
    if left_closed:
        ebdld__hhp -= 1
    recv_starts[0] = halo_size
    for glnfg__ozlr in range(0, halo_size):
        if l_recv_t_buff[glnfg__ozlr] > ebdld__hhp:
            recv_starts[0] = glnfg__ozlr
            break
    for wjtvf__jfin in range(1, num_zero_starts):
        ebdld__hhp = hxev__mhc[wjtvf__jfin] - win
        if left_closed:
            ebdld__hhp -= 1
        recv_starts[wjtvf__jfin] = halo_size
        for glnfg__ozlr in range(recv_starts[wjtvf__jfin - 1], halo_size):
            if l_recv_t_buff[glnfg__ozlr] > ebdld__hhp:
                recv_starts[wjtvf__jfin] = glnfg__ozlr
                break
    return recv_starts


@register_jitable
def roll_var_linear_generic_seq(in_arr, on_arr, win, minp, start, end,
    init_data, add_obs, remove_obs, calc_out):
    N = len(in_arr)
    output = np.empty(N, np.float64)
    data = init_data()
    for glnfg__ozlr in range(start[0], end[0]):
        data = add_obs(in_arr[glnfg__ozlr], *data)
    output[0] = calc_out(minp, *data)
    for wjtvf__jfin in range(1, N):
        s = start[wjtvf__jfin]
        gylvo__fdzrb = end[wjtvf__jfin]
        for glnfg__ozlr in range(start[wjtvf__jfin - 1], s):
            data = remove_obs(in_arr[glnfg__ozlr], *data)
        for glnfg__ozlr in range(end[wjtvf__jfin - 1], gylvo__fdzrb):
            data = add_obs(in_arr[glnfg__ozlr], *data)
        output[wjtvf__jfin] = calc_out(minp, *data)
    return output


def roll_variable_apply(in_arr, on_arr_dt, index_arr, win, minp, center,
    parallel, kernel_func, raw=True):
    pass


@overload(roll_variable_apply, no_unliteral=True)
def overload_roll_variable_apply(in_arr, on_arr_dt, index_arr, win, minp,
    center, parallel, kernel_func, raw=True):
    assert is_overload_constant_bool(raw)
    return roll_variable_apply_impl


def roll_variable_apply_impl(in_arr, on_arr_dt, index_arr, win, minp,
    center, parallel, kernel_func, raw=True):
    _validate_roll_var_args(minp, center)
    in_arr = prep_values(in_arr)
    win = offset_to_nanos(win)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    on_arr = cast_dt64_arr_to_int(on_arr_dt)
    index_arr = fix_index_arr(index_arr)
    N = len(in_arr)
    left_closed = False
    right_closed = True
    if parallel:
        if _is_small_for_parallel_variable(on_arr, win):
            return _handle_small_data_variable_apply(in_arr, on_arr,
                index_arr, win, minp, rank, n_pes, kernel_func, raw)
        ahmy__hkanc = _border_icomm_var(in_arr, on_arr, rank, n_pes, win)
        (l_recv_buff, l_recv_t_buff, r_send_req, fjle__nnxhe, l_recv_req,
            exlwn__zop) = ahmy__hkanc
        if raw == False:
            beg__ubxqg = _border_icomm_var(index_arr, on_arr, rank, n_pes, win)
            (l_recv_buff_idx, ozynq__hzbss, xhbft__sgxva, wojt__kbrj,
                oevc__irszk, ueo__rlc) = beg__ubxqg
    start, end = _build_indexer(on_arr, N, win, left_closed, right_closed)
    output = roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp,
        start, end, kernel_func, raw)
    if parallel:
        _border_send_wait(r_send_req, r_send_req, rank, n_pes, True, False)
        _border_send_wait(fjle__nnxhe, fjle__nnxhe, rank, n_pes, True, False)
        if raw == False:
            _border_send_wait(xhbft__sgxva, xhbft__sgxva, rank, n_pes, True,
                False)
            _border_send_wait(wojt__kbrj, wojt__kbrj, rank, n_pes, True, False)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            bodo.libs.distributed_api.wait(exlwn__zop, True)
            if raw == False:
                bodo.libs.distributed_api.wait(oevc__irszk, True)
                bodo.libs.distributed_api.wait(ueo__rlc, True)
            num_zero_starts = 0
            for wjtvf__jfin in range(0, N):
                if start[wjtvf__jfin] != 0:
                    break
                num_zero_starts += 1
            if num_zero_starts == 0:
                return output
            recv_starts = _get_var_recv_starts(on_arr, l_recv_t_buff,
                num_zero_starts, win)
            recv_left_var_compute(output, in_arr, index_arr,
                num_zero_starts, recv_starts, l_recv_buff, l_recv_buff_idx,
                minp, kernel_func, raw)
    return output


def recv_left_var_compute(output, in_arr, index_arr, num_zero_starts,
    recv_starts, l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
    pass


@overload(recv_left_var_compute)
def overload_recv_left_var_compute(output, in_arr, index_arr,
    num_zero_starts, recv_starts, l_recv_buff, l_recv_buff_idx, minp,
    kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, num_zero_starts, recv_starts,
            l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
            for wjtvf__jfin in range(0, num_zero_starts):
                dwvmq__marou = recv_starts[wjtvf__jfin]
                mhk__mprw = np.concatenate((l_recv_buff[dwvmq__marou:],
                    in_arr[:wjtvf__jfin + 1]))
                if len(mhk__mprw) - np.isnan(mhk__mprw).sum() >= minp:
                    output[wjtvf__jfin] = kernel_func(mhk__mprw)
                else:
                    output[wjtvf__jfin] = np.nan
        return impl

    def impl_series(output, in_arr, index_arr, num_zero_starts, recv_starts,
        l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
        for wjtvf__jfin in range(0, num_zero_starts):
            dwvmq__marou = recv_starts[wjtvf__jfin]
            mhk__mprw = np.concatenate((l_recv_buff[dwvmq__marou:], in_arr[
                :wjtvf__jfin + 1]))
            nvt__yaoxo = np.concatenate((l_recv_buff_idx[dwvmq__marou:],
                index_arr[:wjtvf__jfin + 1]))
            if len(mhk__mprw) - np.isnan(mhk__mprw).sum() >= minp:
                output[wjtvf__jfin] = kernel_func(pd.Series(mhk__mprw,
                    nvt__yaoxo))
            else:
                output[wjtvf__jfin] = np.nan
    return impl_series


def roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp, start,
    end, kernel_func, raw):
    pass


@overload(roll_variable_apply_seq)
def overload_roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp,
    start, end, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):
        return roll_variable_apply_seq_impl
    return roll_variable_apply_seq_impl_series


def roll_variable_apply_seq_impl(in_arr, on_arr, index_arr, win, minp,
    start, end, kernel_func, raw):
    N = len(in_arr)
    output = np.empty(N, dtype=np.float64)
    for wjtvf__jfin in range(0, N):
        s = start[wjtvf__jfin]
        gylvo__fdzrb = end[wjtvf__jfin]
        data = in_arr[s:gylvo__fdzrb]
        if gylvo__fdzrb - s - np.isnan(data).sum() >= minp:
            output[wjtvf__jfin] = kernel_func(data)
        else:
            output[wjtvf__jfin] = np.nan
    return output


def roll_variable_apply_seq_impl_series(in_arr, on_arr, index_arr, win,
    minp, start, end, kernel_func, raw):
    N = len(in_arr)
    output = np.empty(N, dtype=np.float64)
    for wjtvf__jfin in range(0, N):
        s = start[wjtvf__jfin]
        gylvo__fdzrb = end[wjtvf__jfin]
        data = in_arr[s:gylvo__fdzrb]
        if gylvo__fdzrb - s - np.isnan(data).sum() >= minp:
            output[wjtvf__jfin] = kernel_func(pd.Series(data, index_arr[s:
                gylvo__fdzrb]))
        else:
            output[wjtvf__jfin] = np.nan
    return output


@register_jitable(cache=True)
def _build_indexer(on_arr, N, win, left_closed, right_closed):
    hxev__mhc = cast_dt64_arr_to_int(on_arr)
    start = np.empty(N, np.int64)
    end = np.empty(N, np.int64)
    start[0] = 0
    if right_closed:
        end[0] = 1
    else:
        end[0] = 0
    for wjtvf__jfin in range(1, N):
        sbfw__xuzvv = hxev__mhc[wjtvf__jfin]
        ebdld__hhp = hxev__mhc[wjtvf__jfin] - win
        if left_closed:
            ebdld__hhp -= 1
        start[wjtvf__jfin] = wjtvf__jfin
        for glnfg__ozlr in range(start[wjtvf__jfin - 1], wjtvf__jfin):
            if hxev__mhc[glnfg__ozlr] > ebdld__hhp:
                start[wjtvf__jfin] = glnfg__ozlr
                break
        if hxev__mhc[end[wjtvf__jfin - 1]] <= sbfw__xuzvv:
            end[wjtvf__jfin] = wjtvf__jfin + 1
        else:
            end[wjtvf__jfin] = end[wjtvf__jfin - 1]
        if not right_closed:
            end[wjtvf__jfin] -= 1
    return start, end


@register_jitable
def init_data_sum():
    return 0, 0.0


@register_jitable
def add_sum(val, nobs, sum_x):
    if not np.isnan(val):
        nobs += 1
        sum_x += val
    return nobs, sum_x


@register_jitable
def remove_sum(val, nobs, sum_x):
    if not np.isnan(val):
        nobs -= 1
        sum_x -= val
    return nobs, sum_x


@register_jitable
def calc_sum(minp, nobs, sum_x):
    return sum_x if nobs >= minp else np.nan


@register_jitable
def init_data_mean():
    return 0, 0.0, 0


@register_jitable
def add_mean(val, nobs, sum_x, neg_ct):
    if not np.isnan(val):
        nobs += 1
        sum_x += val
        if val < 0:
            neg_ct += 1
    return nobs, sum_x, neg_ct


@register_jitable
def remove_mean(val, nobs, sum_x, neg_ct):
    if not np.isnan(val):
        nobs -= 1
        sum_x -= val
        if val < 0:
            neg_ct -= 1
    return nobs, sum_x, neg_ct


@register_jitable
def calc_mean(minp, nobs, sum_x, neg_ct):
    if nobs >= minp:
        vlnbf__jzz = sum_x / nobs
        if neg_ct == 0 and vlnbf__jzz < 0.0:
            vlnbf__jzz = 0
        elif neg_ct == nobs and vlnbf__jzz > 0.0:
            vlnbf__jzz = 0
    else:
        vlnbf__jzz = np.nan
    return vlnbf__jzz


@register_jitable
def init_data_var():
    return 0, 0.0, 0.0


@register_jitable
def add_var(val, nobs, mean_x, ssqdm_x):
    if not np.isnan(val):
        nobs += 1
        lcl__xvld = val - mean_x
        mean_x += lcl__xvld / nobs
        ssqdm_x += (nobs - 1) * lcl__xvld ** 2 / nobs
    return nobs, mean_x, ssqdm_x


@register_jitable
def remove_var(val, nobs, mean_x, ssqdm_x):
    if not np.isnan(val):
        nobs -= 1
        if nobs != 0:
            lcl__xvld = val - mean_x
            mean_x -= lcl__xvld / nobs
            ssqdm_x -= (nobs + 1) * lcl__xvld ** 2 / nobs
        else:
            mean_x = 0.0
            ssqdm_x = 0.0
    return nobs, mean_x, ssqdm_x


@register_jitable
def calc_var(minp, nobs, mean_x, ssqdm_x):
    jiqke__orj = 1.0
    vlnbf__jzz = np.nan
    if nobs >= minp and nobs > jiqke__orj:
        if nobs == 1:
            vlnbf__jzz = 0.0
        else:
            vlnbf__jzz = ssqdm_x / (nobs - jiqke__orj)
            if vlnbf__jzz < 0.0:
                vlnbf__jzz = 0.0
    return vlnbf__jzz


@register_jitable
def calc_std(minp, nobs, mean_x, ssqdm_x):
    mmow__pzwue = calc_var(minp, nobs, mean_x, ssqdm_x)
    return np.sqrt(mmow__pzwue)


@register_jitable
def init_data_count():
    return 0.0,


@register_jitable
def add_count(val, count_x):
    if not np.isnan(val):
        count_x += 1.0
    return count_x,


@register_jitable
def remove_count(val, count_x):
    if not np.isnan(val):
        count_x -= 1.0
    return count_x,


@register_jitable
def calc_count(minp, count_x):
    return count_x


@register_jitable
def calc_count_var(minp, count_x):
    return count_x if count_x >= minp else np.nan


linear_kernels = {'sum': (init_data_sum, add_sum, remove_sum, calc_sum),
    'mean': (init_data_mean, add_mean, remove_mean, calc_mean), 'var': (
    init_data_var, add_var, remove_var, calc_var), 'std': (init_data_var,
    add_var, remove_var, calc_std), 'count': (init_data_count, add_count,
    remove_count, calc_count)}


def shift():
    return


@overload(shift, jit_options={'cache': True})
def shift_overload(in_arr, shift, parallel):
    if not isinstance(parallel, types.Literal):
        return shift_impl


def shift_impl(in_arr, shift, parallel):
    N = len(in_arr)
    output = alloc_shift(N, in_arr, (-1,))
    send_right = shift > 0
    send_left = shift <= 0
    is_parallel_str = False
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        halo_size = np.int32(abs(shift))
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_shift(in_arr, shift, rank, n_pes)
        ahmy__hkanc = _border_icomm(in_arr, rank, n_pes, halo_size,
            send_right, send_left)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            carbd__rzy) = ahmy__hkanc
        if send_right and is_str_binary_array(in_arr):
            is_parallel_str = True
            shift_left_recv(r_send_req, l_send_req, rank, n_pes, halo_size,
                l_recv_req, l_recv_buff, output)
    shift_seq(in_arr, shift, output, is_parallel_str)
    if parallel:
        if send_right:
            if not is_str_binary_array(in_arr):
                shift_left_recv(r_send_req, l_send_req, rank, n_pes,
                    halo_size, l_recv_req, l_recv_buff, output)
        else:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, False, True)
            if rank != n_pes - 1:
                bodo.libs.distributed_api.wait(carbd__rzy, True)
                for wjtvf__jfin in range(0, halo_size):
                    if bodo.libs.array_kernels.isna(r_recv_buff, wjtvf__jfin):
                        bodo.libs.array_kernels.setna(output, N - halo_size +
                            wjtvf__jfin)
                        continue
                    output[N - halo_size + wjtvf__jfin] = r_recv_buff[
                        wjtvf__jfin]
    return output


@register_jitable(cache=True)
def shift_seq(in_arr, shift, output, is_parallel_str=False):
    N = len(in_arr)
    zag__ngx = 1 if shift > 0 else -1
    shift = zag__ngx * min(abs(shift), N)
    if shift > 0 and (not is_parallel_str or bodo.get_rank() == 0):
        bodo.libs.array_kernels.setna_slice(output, slice(None, shift))
    start = max(shift, 0)
    end = min(N, N + shift)
    for wjtvf__jfin in range(start, end):
        if bodo.libs.array_kernels.isna(in_arr, wjtvf__jfin - shift):
            bodo.libs.array_kernels.setna(output, wjtvf__jfin)
            continue
        output[wjtvf__jfin] = in_arr[wjtvf__jfin - shift]
    if shift < 0:
        bodo.libs.array_kernels.setna_slice(output, slice(shift, None))
    return output


@register_jitable
def shift_left_recv(r_send_req, l_send_req, rank, n_pes, halo_size,
    l_recv_req, l_recv_buff, output):
    _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, False)
    if rank != 0:
        bodo.libs.distributed_api.wait(l_recv_req, True)
        for wjtvf__jfin in range(0, halo_size):
            if bodo.libs.array_kernels.isna(l_recv_buff, wjtvf__jfin):
                bodo.libs.array_kernels.setna(output, wjtvf__jfin)
                continue
            output[wjtvf__jfin] = l_recv_buff[wjtvf__jfin]


def is_str_binary_array(arr):
    return False


@overload(is_str_binary_array)
def overload_is_str_binary_array(arr):
    if arr in [bodo.string_array_type, bodo.binary_array_type]:
        return lambda arr: True
    return lambda arr: False


def is_supported_shift_array_type(arr_type):
    return isinstance(arr_type, types.Array) and (isinstance(arr_type.dtype,
        types.Number) or arr_type.dtype in [bodo.datetime64ns, bodo.
        timedelta64ns]) or isinstance(arr_type, (bodo.IntegerArrayType,
        bodo.DecimalArrayType)) or arr_type in (bodo.boolean_array, bodo.
        datetime_date_array_type, bodo.string_array_type, bodo.
        binary_array_type)


def pct_change():
    return


@overload(pct_change, jit_options={'cache': True})
def pct_change_overload(in_arr, shift, parallel):
    if not isinstance(parallel, types.Literal):
        return pct_change_impl


def pct_change_impl(in_arr, shift, parallel):
    N = len(in_arr)
    send_right = shift > 0
    send_left = shift <= 0
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        halo_size = np.int32(abs(shift))
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_pct_change(in_arr, shift, rank, n_pes)
        ahmy__hkanc = _border_icomm(in_arr, rank, n_pes, halo_size,
            send_right, send_left)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            carbd__rzy) = ahmy__hkanc
    output = pct_change_seq(in_arr, shift)
    if parallel:
        if send_right:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, False)
            if rank != 0:
                bodo.libs.distributed_api.wait(l_recv_req, True)
                for wjtvf__jfin in range(0, halo_size):
                    gvyjm__wzy = l_recv_buff[wjtvf__jfin]
                    output[wjtvf__jfin] = (in_arr[wjtvf__jfin] - gvyjm__wzy
                        ) / gvyjm__wzy
        else:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, False, True)
            if rank != n_pes - 1:
                bodo.libs.distributed_api.wait(carbd__rzy, True)
                for wjtvf__jfin in range(0, halo_size):
                    gvyjm__wzy = r_recv_buff[wjtvf__jfin]
                    output[N - halo_size + wjtvf__jfin] = (in_arr[N -
                        halo_size + wjtvf__jfin] - gvyjm__wzy) / gvyjm__wzy
    return output


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_first_non_na(arr):
    if isinstance(arr.dtype, (types.Integer, types.Boolean)):
        zero = arr.dtype(0)
        return lambda arr: zero if len(arr) == 0 else arr[0]
    assert isinstance(arr.dtype, types.Float)
    viicw__jxs = np.nan
    if arr.dtype == types.float32:
        viicw__jxs = np.float32('nan')

    def impl(arr):
        for wjtvf__jfin in range(len(arr)):
            if not bodo.libs.array_kernels.isna(arr, wjtvf__jfin):
                return arr[wjtvf__jfin]
        return viicw__jxs
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_last_non_na(arr):
    if isinstance(arr.dtype, (types.Integer, types.Boolean)):
        zero = arr.dtype(0)
        return lambda arr: zero if len(arr) == 0 else arr[-1]
    assert isinstance(arr.dtype, types.Float)
    viicw__jxs = np.nan
    if arr.dtype == types.float32:
        viicw__jxs = np.float32('nan')

    def impl(arr):
        gethy__ctvhj = len(arr)
        for wjtvf__jfin in range(len(arr)):
            pecqh__sfs = gethy__ctvhj - wjtvf__jfin - 1
            if not bodo.libs.array_kernels.isna(arr, pecqh__sfs):
                return arr[pecqh__sfs]
        return viicw__jxs
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_one_from_arr_dtype(arr):
    one = arr.dtype(1)
    return lambda arr: one


@register_jitable(cache=True)
def pct_change_seq(in_arr, shift):
    N = len(in_arr)
    output = alloc_pct_change(N, in_arr)
    zag__ngx = 1 if shift > 0 else -1
    shift = zag__ngx * min(abs(shift), N)
    if shift > 0:
        bodo.libs.array_kernels.setna_slice(output, slice(None, shift))
    else:
        bodo.libs.array_kernels.setna_slice(output, slice(shift, None))
    if shift > 0:
        zveh__ftlnt = get_first_non_na(in_arr[:shift])
        obsw__qyh = get_last_non_na(in_arr[:shift])
    else:
        zveh__ftlnt = get_last_non_na(in_arr[:-shift])
        obsw__qyh = get_first_non_na(in_arr[:-shift])
    one = get_one_from_arr_dtype(output)
    start = max(shift, 0)
    end = min(N, N + shift)
    for wjtvf__jfin in range(start, end):
        gvyjm__wzy = in_arr[wjtvf__jfin - shift]
        if np.isnan(gvyjm__wzy):
            gvyjm__wzy = zveh__ftlnt
        else:
            zveh__ftlnt = gvyjm__wzy
        val = in_arr[wjtvf__jfin]
        if np.isnan(val):
            val = obsw__qyh
        else:
            obsw__qyh = val
        output[wjtvf__jfin] = val / gvyjm__wzy - one
    return output


@register_jitable(cache=True)
def _border_icomm(in_arr, rank, n_pes, halo_size, send_right=True,
    send_left=False):
    xcw__mew = np.int32(comm_border_tag)
    l_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr, (-1,))
    r_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr, (-1,))
    if send_right and rank != n_pes - 1:
        r_send_req = bodo.libs.distributed_api.isend(in_arr[-halo_size:],
            halo_size, np.int32(rank + 1), xcw__mew, True)
    if send_right and rank != 0:
        l_recv_req = bodo.libs.distributed_api.irecv(l_recv_buff, halo_size,
            np.int32(rank - 1), xcw__mew, True)
    if send_left and rank != 0:
        l_send_req = bodo.libs.distributed_api.isend(in_arr[:halo_size],
            halo_size, np.int32(rank - 1), xcw__mew, True)
    if send_left and rank != n_pes - 1:
        carbd__rzy = bodo.libs.distributed_api.irecv(r_recv_buff, halo_size,
            np.int32(rank + 1), xcw__mew, True)
    return (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
        carbd__rzy)


@register_jitable(cache=True)
def _border_icomm_var(in_arr, on_arr, rank, n_pes, win_size):
    xcw__mew = np.int32(comm_border_tag)
    N = len(on_arr)
    halo_size = N
    end = on_arr[-1]
    for glnfg__ozlr in range(-2, -N, -1):
        tndn__dgv = on_arr[glnfg__ozlr]
        if end - tndn__dgv >= win_size:
            halo_size = -glnfg__ozlr
            break
    if rank != n_pes - 1:
        bodo.libs.distributed_api.send(halo_size, np.int32(rank + 1), xcw__mew)
        r_send_req = bodo.libs.distributed_api.isend(in_arr[-halo_size:],
            np.int32(halo_size), np.int32(rank + 1), xcw__mew, True)
        fjle__nnxhe = bodo.libs.distributed_api.isend(on_arr[-halo_size:],
            np.int32(halo_size), np.int32(rank + 1), xcw__mew, True)
    if rank != 0:
        halo_size = bodo.libs.distributed_api.recv(np.int64, np.int32(rank -
            1), xcw__mew)
        l_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr)
        l_recv_req = bodo.libs.distributed_api.irecv(l_recv_buff, np.int32(
            halo_size), np.int32(rank - 1), xcw__mew, True)
        l_recv_t_buff = np.empty(halo_size, np.int64)
        exlwn__zop = bodo.libs.distributed_api.irecv(l_recv_t_buff, np.
            int32(halo_size), np.int32(rank - 1), xcw__mew, True)
    return (l_recv_buff, l_recv_t_buff, r_send_req, fjle__nnxhe, l_recv_req,
        exlwn__zop)


@register_jitable
def _border_send_wait(r_send_req, l_send_req, rank, n_pes, right, left):
    if right and rank != n_pes - 1:
        bodo.libs.distributed_api.wait(r_send_req, True)
    if left and rank != 0:
        bodo.libs.distributed_api.wait(l_send_req, True)


@register_jitable
def _is_small_for_parallel(N, halo_size):
    tdl__dcxpj = bodo.libs.distributed_api.dist_reduce(int(N <= 2 *
        halo_size + 1), np.int32(Reduce_Type.Sum.value))
    return tdl__dcxpj != 0


@register_jitable
def _handle_small_data(in_arr, win, minp, center, rank, n_pes, init_data,
    add_obs, remove_obs, calc_out):
    N = len(in_arr)
    ntq__jez = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32(
        Reduce_Type.Sum.value))
    xlowy__cojlt = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        qlzg__wisg, pkuq__odh = roll_fixed_linear_generic_seq(xlowy__cojlt,
            win, minp, center, init_data, add_obs, remove_obs, calc_out)
    else:
        qlzg__wisg = np.empty(ntq__jez, np.float64)
    bodo.libs.distributed_api.bcast(qlzg__wisg)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return qlzg__wisg[start:end]


@register_jitable
def _handle_small_data_apply(in_arr, index_arr, win, minp, center, rank,
    n_pes, kernel_func, raw=True):
    N = len(in_arr)
    ntq__jez = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32(
        Reduce_Type.Sum.value))
    xlowy__cojlt = bodo.libs.distributed_api.gatherv(in_arr)
    odgx__pvfi = bodo.libs.distributed_api.gatherv(index_arr)
    if rank == 0:
        qlzg__wisg = roll_fixed_apply_seq(xlowy__cojlt, odgx__pvfi, win,
            minp, center, kernel_func, raw)
    else:
        qlzg__wisg = np.empty(ntq__jez, np.float64)
    bodo.libs.distributed_api.bcast(qlzg__wisg)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return qlzg__wisg[start:end]


def bcast_n_chars_if_str_binary_arr(arr):
    pass


@overload(bcast_n_chars_if_str_binary_arr)
def overload_bcast_n_chars_if_str_binary_arr(arr):
    if arr in [bodo.binary_array_type, bodo.string_array_type]:

        def impl(arr):
            return bodo.libs.distributed_api.bcast_scalar(np.int64(bodo.
                libs.str_arr_ext.num_total_chars(arr)))
        return impl
    return lambda arr: -1


@register_jitable
def _handle_small_data_shift(in_arr, shift, rank, n_pes):
    N = len(in_arr)
    ntq__jez = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32(
        Reduce_Type.Sum.value))
    xlowy__cojlt = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        qlzg__wisg = alloc_shift(len(xlowy__cojlt), xlowy__cojlt, (-1,))
        shift_seq(xlowy__cojlt, shift, qlzg__wisg)
        lucl__qjdki = bcast_n_chars_if_str_binary_arr(qlzg__wisg)
    else:
        lucl__qjdki = bcast_n_chars_if_str_binary_arr(in_arr)
        qlzg__wisg = alloc_shift(ntq__jez, in_arr, (lucl__qjdki,))
    bodo.libs.distributed_api.bcast(qlzg__wisg)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return qlzg__wisg[start:end]


@register_jitable
def _handle_small_data_pct_change(in_arr, shift, rank, n_pes):
    N = len(in_arr)
    ntq__jez = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    xlowy__cojlt = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        qlzg__wisg = pct_change_seq(xlowy__cojlt, shift)
    else:
        qlzg__wisg = alloc_pct_change(ntq__jez, in_arr)
    bodo.libs.distributed_api.bcast(qlzg__wisg)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return qlzg__wisg[start:end]


def cast_dt64_arr_to_int(arr):
    return arr


@infer_global(cast_dt64_arr_to_int)
class DtArrToIntType(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        assert args[0] == types.Array(types.NPDatetime('ns'), 1, 'C') or args[0
            ] == types.Array(types.int64, 1, 'C')
        return signature(types.Array(types.int64, 1, 'C'), *args)


@lower_builtin(cast_dt64_arr_to_int, types.Array(types.NPDatetime('ns'), 1,
    'C'))
@lower_builtin(cast_dt64_arr_to_int, types.Array(types.int64, 1, 'C'))
def lower_cast_dt64_arr_to_int(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@register_jitable
def _is_small_for_parallel_variable(on_arr, win_size):
    if len(on_arr) < 2:
        mhw__htdjp = 1
    else:
        start = on_arr[0]
        end = on_arr[-1]
        cvl__jte = end - start
        mhw__htdjp = int(cvl__jte <= win_size)
    tdl__dcxpj = bodo.libs.distributed_api.dist_reduce(mhw__htdjp, np.int32
        (Reduce_Type.Sum.value))
    return tdl__dcxpj != 0


@register_jitable
def _handle_small_data_variable(in_arr, on_arr, win, minp, rank, n_pes,
    init_data, add_obs, remove_obs, calc_out):
    N = len(in_arr)
    ntq__jez = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    xlowy__cojlt = bodo.libs.distributed_api.gatherv(in_arr)
    hhfse__xmwx = bodo.libs.distributed_api.gatherv(on_arr)
    if rank == 0:
        start, end = _build_indexer(hhfse__xmwx, ntq__jez, win, False, True)
        qlzg__wisg = roll_var_linear_generic_seq(xlowy__cojlt, hhfse__xmwx,
            win, minp, start, end, init_data, add_obs, remove_obs, calc_out)
    else:
        qlzg__wisg = np.empty(ntq__jez, np.float64)
    bodo.libs.distributed_api.bcast(qlzg__wisg)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return qlzg__wisg[start:end]


@register_jitable
def _handle_small_data_variable_apply(in_arr, on_arr, index_arr, win, minp,
    rank, n_pes, kernel_func, raw):
    N = len(in_arr)
    ntq__jez = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    xlowy__cojlt = bodo.libs.distributed_api.gatherv(in_arr)
    hhfse__xmwx = bodo.libs.distributed_api.gatherv(on_arr)
    odgx__pvfi = bodo.libs.distributed_api.gatherv(index_arr)
    if rank == 0:
        start, end = _build_indexer(hhfse__xmwx, ntq__jez, win, False, True)
        qlzg__wisg = roll_variable_apply_seq(xlowy__cojlt, hhfse__xmwx,
            odgx__pvfi, win, minp, start, end, kernel_func, raw)
    else:
        qlzg__wisg = np.empty(ntq__jez, np.float64)
    bodo.libs.distributed_api.bcast(qlzg__wisg)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return qlzg__wisg[start:end]


@register_jitable(cache=True)
def _dropna(arr):
    dphhi__oepm = len(arr)
    rcns__mbu = dphhi__oepm - np.isnan(arr).sum()
    A = np.empty(rcns__mbu, arr.dtype)
    whi__ywlfe = 0
    for wjtvf__jfin in range(dphhi__oepm):
        val = arr[wjtvf__jfin]
        if not np.isnan(val):
            A[whi__ywlfe] = val
            whi__ywlfe += 1
    return A


def alloc_shift(n, A, s=None):
    return np.empty(n, A.dtype)


@overload(alloc_shift, no_unliteral=True)
def alloc_shift_overload(n, A, s=None):
    if not isinstance(A, types.Array):
        return lambda n, A, s=None: bodo.utils.utils.alloc_type(n, A, s)
    if isinstance(A.dtype, types.Integer):
        return lambda n, A, s=None: np.empty(n, np.float64)
    return lambda n, A, s=None: np.empty(n, A.dtype)


def alloc_pct_change(n, A):
    return np.empty(n, A.dtype)


@overload(alloc_pct_change, no_unliteral=True)
def alloc_pct_change_overload(n, A):
    if isinstance(A.dtype, types.Integer):
        return lambda n, A: np.empty(n, np.float64)
    return lambda n, A: np.empty(n, A.dtype)


def prep_values(A):
    return A.astype('float64')


@overload(prep_values, no_unliteral=True)
def prep_values_overload(A):
    if A == types.Array(types.float64, 1, 'C'):
        return lambda A: A
    return lambda A: A.astype(np.float64)


@register_jitable
def _validate_roll_fixed_args(win, minp):
    if win < 0:
        raise ValueError('window must be non-negative')
    if minp < 0:
        raise ValueError('min_periods must be >= 0')
    if minp > win:
        raise ValueError('min_periods must be <= window')


@register_jitable
def _validate_roll_var_args(minp, center):
    if minp < 0:
        raise ValueError('min_periods must be >= 0')
    if center:
        raise NotImplementedError(
            'rolling: center is not implemented for datetimelike and offset based windows'
            )
