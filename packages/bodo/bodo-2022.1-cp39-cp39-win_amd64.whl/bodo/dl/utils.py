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
    dkq__lhm = MPI.COMM_WORLD
    rnqp__njqzr = dkq__lhm.Get_rank()
    cdan__wmnnr = get_host_ranks()
    hgoi__pug = get_nodes_first_ranks()
    if rnqp__njqzr in hgoi__pug:
        try:
            dat__kxv = get_num_gpus(framework)
        except Exception as ecs__bkx:
            dat__kxv = ecs__bkx
        ouh__naso = create_subcomm_mpi4py(hgoi__pug)
        ogoel__ysag = ouh__naso.gather(dat__kxv)
        if rnqp__njqzr == 0:
            gpu_ranks = []
            ssjg__ddhkc = None
            for xnf__qvchq, rzgl__rrakq in enumerate(cdan__wmnnr.values()):
                xon__kpo = ogoel__ysag[xnf__qvchq]
                if isinstance(xon__kpo, Exception):
                    ssjg__ddhkc = xon__kpo
                    break
                if xon__kpo == 0:
                    continue
                sqv__uyq = len(rzgl__rrakq) // xon__kpo
                for hnvp__ayhu, pfoko__qgjb in enumerate(rzgl__rrakq):
                    if hnvp__ayhu % sqv__uyq == 0:
                        lrmeg__kua = hnvp__ayhu / sqv__uyq
                        if lrmeg__kua < xon__kpo:
                            gpu_ranks.append(pfoko__qgjb)
            if ssjg__ddhkc:
                dkq__lhm.bcast(ssjg__ddhkc)
                raise ssjg__ddhkc
            else:
                dkq__lhm.bcast(gpu_ranks)
    if rnqp__njqzr != 0:
        gpu_ranks = dkq__lhm.bcast(None)
        if isinstance(gpu_ranks, Exception):
            ecs__bkx = gpu_ranks
            raise ecs__bkx
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
    hvpsf__dctgs = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        ouh__naso = MPI.COMM_WORLD.Split(color=0 if hvpsf__dctgs in
            gpu_ranks else MPI.UNDEFINED, key=hvpsf__dctgs)
        if ouh__naso != MPI.COMM_NULL:
            hvd.init(comm=ouh__naso)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                zjkw__icc = tf.config.experimental.list_physical_devices('GPU')
                for dyz__bidf in zjkw__icc:
                    tf.config.experimental.set_memory_growth(dyz__bidf, True)
                tf.config.experimental.set_visible_devices(zjkw__icc[hvd.
                    local_rank()], 'GPU')
    else:
        if hvpsf__dctgs == 0:
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
        liug__gnven = 17
        dkq__lhm = MPI.COMM_WORLD
        mtaf__ilu = MPI.Get_processor_name()
        ytq__ibiip = get_host_ranks()[mtaf__ilu]
        assert_dl_initialized()
        if bodo.get_rank() == ytq__ibiip[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for rnqp__njqzr in ytq__ibiip[1:]:
                dkq__lhm.isend(1, dest=rnqp__njqzr, tag=liug__gnven)
        else:
            while True:
                bgjo__jjr = MPI.Status()
                geq__tsuxn = dkq__lhm.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    bgjo__jjr)
                if geq__tsuxn:
                    assert bgjo__jjr.source == ytq__ibiip[0]
                    assert bgjo__jjr.tag == liug__gnven
                    dkq__lhm.recv(source=0, tag=liug__gnven)
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
