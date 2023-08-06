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
    hmhct__vrg = MPI.COMM_WORLD
    fxywf__akbm = hmhct__vrg.Get_rank()
    hkgxj__kbjy = get_host_ranks()
    exea__xcnx = get_nodes_first_ranks()
    if fxywf__akbm in exea__xcnx:
        try:
            mfr__aoxgt = get_num_gpus(framework)
        except Exception as ddn__dti:
            mfr__aoxgt = ddn__dti
        hvz__wjrpb = create_subcomm_mpi4py(exea__xcnx)
        uatw__eqt = hvz__wjrpb.gather(mfr__aoxgt)
        if fxywf__akbm == 0:
            gpu_ranks = []
            gxab__xlyyf = None
            for tzgyx__xgn, pbxhu__zrq in enumerate(hkgxj__kbjy.values()):
                psh__samho = uatw__eqt[tzgyx__xgn]
                if isinstance(psh__samho, Exception):
                    gxab__xlyyf = psh__samho
                    break
                if psh__samho == 0:
                    continue
                grl__poay = len(pbxhu__zrq) // psh__samho
                for lksel__iyig, wlhv__vybd in enumerate(pbxhu__zrq):
                    if lksel__iyig % grl__poay == 0:
                        toz__gxsg = lksel__iyig / grl__poay
                        if toz__gxsg < psh__samho:
                            gpu_ranks.append(wlhv__vybd)
            if gxab__xlyyf:
                hmhct__vrg.bcast(gxab__xlyyf)
                raise gxab__xlyyf
            else:
                hmhct__vrg.bcast(gpu_ranks)
    if fxywf__akbm != 0:
        gpu_ranks = hmhct__vrg.bcast(None)
        if isinstance(gpu_ranks, Exception):
            ddn__dti = gpu_ranks
            raise ddn__dti
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
    slogu__kmwqo = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        hvz__wjrpb = MPI.COMM_WORLD.Split(color=0 if slogu__kmwqo in
            gpu_ranks else MPI.UNDEFINED, key=slogu__kmwqo)
        if hvz__wjrpb != MPI.COMM_NULL:
            hvd.init(comm=hvz__wjrpb)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                gpgw__ekccj = tf.config.experimental.list_physical_devices(
                    'GPU')
                for rlv__ziu in gpgw__ekccj:
                    tf.config.experimental.set_memory_growth(rlv__ziu, True)
                tf.config.experimental.set_visible_devices(gpgw__ekccj[hvd.
                    local_rank()], 'GPU')
    else:
        if slogu__kmwqo == 0:
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
        mam__ont = 17
        hmhct__vrg = MPI.COMM_WORLD
        ddta__mwuns = MPI.Get_processor_name()
        pwld__djcis = get_host_ranks()[ddta__mwuns]
        assert_dl_initialized()
        if bodo.get_rank() == pwld__djcis[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for fxywf__akbm in pwld__djcis[1:]:
                hmhct__vrg.isend(1, dest=fxywf__akbm, tag=mam__ont)
        else:
            while True:
                zdnti__rscby = MPI.Status()
                oqudb__okvzl = hmhct__vrg.Iprobe(MPI.ANY_SOURCE, MPI.
                    ANY_TAG, zdnti__rscby)
                if oqudb__okvzl:
                    assert zdnti__rscby.source == pwld__djcis[0]
                    assert zdnti__rscby.tag == mam__ont
                    hmhct__vrg.recv(source=0, tag=mam__ont)
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
