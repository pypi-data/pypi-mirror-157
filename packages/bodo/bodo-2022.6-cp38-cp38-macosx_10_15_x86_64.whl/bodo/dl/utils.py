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
    wevx__btme = MPI.COMM_WORLD
    thdff__werxd = wevx__btme.Get_rank()
    ugmf__bbh = get_host_ranks()
    qvyb__tceg = get_nodes_first_ranks()
    if thdff__werxd in qvyb__tceg:
        try:
            hzac__kfxun = get_num_gpus(framework)
        except Exception as mtaqy__djpno:
            hzac__kfxun = mtaqy__djpno
        pxwge__yqd = create_subcomm_mpi4py(qvyb__tceg)
        oibb__bdv = pxwge__yqd.gather(hzac__kfxun)
        if thdff__werxd == 0:
            gpu_ranks = []
            zbxg__zas = None
            for gcu__mpr, spakl__dfja in enumerate(ugmf__bbh.values()):
                zfz__vio = oibb__bdv[gcu__mpr]
                if isinstance(zfz__vio, Exception):
                    zbxg__zas = zfz__vio
                    break
                if zfz__vio == 0:
                    continue
                poeyw__lhi = len(spakl__dfja) // zfz__vio
                for occmq__nlhk, rxi__akrhb in enumerate(spakl__dfja):
                    if occmq__nlhk % poeyw__lhi == 0:
                        udzq__snyvf = occmq__nlhk / poeyw__lhi
                        if udzq__snyvf < zfz__vio:
                            gpu_ranks.append(rxi__akrhb)
            if zbxg__zas:
                wevx__btme.bcast(zbxg__zas)
                raise zbxg__zas
            else:
                wevx__btme.bcast(gpu_ranks)
    if thdff__werxd != 0:
        gpu_ranks = wevx__btme.bcast(None)
        if isinstance(gpu_ranks, Exception):
            mtaqy__djpno = gpu_ranks
            raise mtaqy__djpno
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
    vgcjk__rddzk = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        pxwge__yqd = MPI.COMM_WORLD.Split(color=0 if vgcjk__rddzk in
            gpu_ranks else MPI.UNDEFINED, key=vgcjk__rddzk)
        if pxwge__yqd != MPI.COMM_NULL:
            hvd.init(comm=pxwge__yqd)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                fwbvg__apjfa = tf.config.experimental.list_physical_devices(
                    'GPU')
                for jddg__dzsti in fwbvg__apjfa:
                    tf.config.experimental.set_memory_growth(jddg__dzsti, True)
                tf.config.experimental.set_visible_devices(fwbvg__apjfa[hvd
                    .local_rank()], 'GPU')
    else:
        if vgcjk__rddzk == 0:
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
        ltrp__vlkti = 17
        wevx__btme = MPI.COMM_WORLD
        qtgqc__afhsa = MPI.Get_processor_name()
        quy__tqg = get_host_ranks()[qtgqc__afhsa]
        assert_dl_initialized()
        if bodo.get_rank() == quy__tqg[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for thdff__werxd in quy__tqg[1:]:
                wevx__btme.isend(1, dest=thdff__werxd, tag=ltrp__vlkti)
        else:
            while True:
                xcqfv__gyx = MPI.Status()
                hqmly__dints = wevx__btme.Iprobe(MPI.ANY_SOURCE, MPI.
                    ANY_TAG, xcqfv__gyx)
                if hqmly__dints:
                    assert xcqfv__gyx.source == quy__tqg[0]
                    assert xcqfv__gyx.tag == ltrp__vlkti
                    wevx__btme.recv(source=0, tag=ltrp__vlkti)
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
