"""Support distributed deep learning with Horovod
"""
import time
import numba
import numpy as np
from mpi4py import MPI
import bodo
from bodo.libs.distributed_api import create_subcomm_mpi4py, get_host_ranks, get_nodes_first_ranks
dl_status = None


def assert_dl_initialized():
    assert dl_status is not None, 'Horovod has not been initialized. Call bodo.dl.start() first'


class DLStatus(object):

    def __init__(self, framework, gpu_ranks):
        self.framework = framework
        self.gpu_ranks = gpu_ranks


def get_num_gpus(framework):
    if framework == 'torch':
        import torch
        return torch.cuda.device_count()
    elif framework == 'tensorflow':
        import tensorflow as tf
        return len(tf.config.experimental.list_physical_devices('GPU'))
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))


def get_gpu_ranks(framework):
    aron__zqokw = MPI.COMM_WORLD
    zxd__gjpri = aron__zqokw.Get_rank()
    jnm__nyu = get_host_ranks()
    rvqh__cnvmk = get_nodes_first_ranks()
    if zxd__gjpri in rvqh__cnvmk:
        try:
            mful__uortc = get_num_gpus(framework)
        except Exception as nzoag__uvdg:
            mful__uortc = nzoag__uvdg
        pvrh__gzkq = create_subcomm_mpi4py(rvqh__cnvmk)
        vccm__ukai = pvrh__gzkq.gather(mful__uortc)
        if zxd__gjpri == 0:
            gpu_ranks = []
            alm__tvbyk = None
            for jzc__nuwh, awrcs__oadbb in enumerate(jnm__nyu.values()):
                byssi__eea = vccm__ukai[jzc__nuwh]
                if isinstance(byssi__eea, Exception):
                    alm__tvbyk = byssi__eea
                    break
                if byssi__eea == 0:
                    continue
                iyyiw__sjwo = len(awrcs__oadbb) // byssi__eea
                for dab__jesb, jfgh__qot in enumerate(awrcs__oadbb):
                    if dab__jesb % iyyiw__sjwo == 0:
                        rvmce__iro = dab__jesb / iyyiw__sjwo
                        if rvmce__iro < byssi__eea:
                            gpu_ranks.append(jfgh__qot)
            if alm__tvbyk:
                aron__zqokw.bcast(alm__tvbyk)
                raise alm__tvbyk
            else:
                aron__zqokw.bcast(gpu_ranks)
    if zxd__gjpri != 0:
        gpu_ranks = aron__zqokw.bcast(None)
        if isinstance(gpu_ranks, Exception):
            nzoag__uvdg = gpu_ranks
            raise nzoag__uvdg
    return gpu_ranks


def is_cuda_available():
    assert_dl_initialized()
    return len(dl_status.gpu_ranks) > 0


def initialize_horovod(framework):
    global dl_status
    if dl_status is not None:
        assert dl_status.framework == framework, 'Attempted to initialize Horovod with different DL frameworks'
        return np.array(dl_status.gpu_ranks, dtype=np.int32)
    gpu_ranks = get_gpu_ranks(framework)
    if framework == 'torch':
        import horovod.torch as hvd
        import torch
        torch.set_num_threads(1)
    elif framework == 'tensorflow':
        import horovod.tensorflow as hvd
        import tensorflow as tf
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))
    ccyj__fkqm = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        pvrh__gzkq = MPI.COMM_WORLD.Split(color=0 if ccyj__fkqm in
            gpu_ranks else MPI.UNDEFINED, key=ccyj__fkqm)
        if pvrh__gzkq != MPI.COMM_NULL:
            hvd.init(comm=pvrh__gzkq)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                rrq__ctu = tf.config.experimental.list_physical_devices('GPU')
                for ildl__kuf in rrq__ctu:
                    tf.config.experimental.set_memory_growth(ildl__kuf, True)
                tf.config.experimental.set_visible_devices(rrq__ctu[hvd.
                    local_rank()], 'GPU')
    else:
        if ccyj__fkqm == 0:
            print('[BODO-DL]: No GPUs found in cluster. Using CPUs')
        hvd.init()
    dl_status = DLStatus(framework, np.array(gpu_ranks, dtype=np.int32))


@numba.njit
def start(framework):
    with numba.objmode:
        initialize_horovod(framework)


@numba.njit
def end():
    with numba.objmode:
        end_py()


def end_py():
    if is_cuda_available():
        nhc__rknyi = 17
        aron__zqokw = MPI.COMM_WORLD
        npwhg__lkejo = MPI.Get_processor_name()
        gnu__kxlx = get_host_ranks()[npwhg__lkejo]
        assert_dl_initialized()
        if bodo.get_rank() == gnu__kxlx[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for zxd__gjpri in gnu__kxlx[1:]:
                aron__zqokw.isend(1, dest=zxd__gjpri, tag=nhc__rknyi)
        else:
            while True:
                rqmgo__qbdf = MPI.Status()
                udkh__kdlnl = aron__zqokw.Iprobe(MPI.ANY_SOURCE, MPI.
                    ANY_TAG, rqmgo__qbdf)
                if udkh__kdlnl:
                    assert rqmgo__qbdf.source == gnu__kxlx[0]
                    assert rqmgo__qbdf.tag == nhc__rknyi
                    aron__zqokw.recv(source=0, tag=nhc__rknyi)
                    break
                time.sleep(1.0)
    else:
        bodo.barrier()


def _prepare_data_get_gpu_ranks():
    assert_dl_initialized()
    return dl_status.gpu_ranks


@numba.njit
def prepare_data(data):
    with numba.objmode(gpu_ranks='int32[:]'):
        gpu_ranks = _prepare_data_get_gpu_ranks()
    if len(gpu_ranks) > 0:
        data = bodo.rebalance(data, dests=list(gpu_ranks), parallel=True)
    else:
        data = bodo.rebalance(data, parallel=True)
    return data
