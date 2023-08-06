import gc
import inspect
import sys
import types as pytypes
import bodo
master_mode_on = False
MASTER_RANK = 0


class MasterModeDispatcher(object):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def __call__(self, *args, **kwargs):
        assert bodo.get_rank() == MASTER_RANK
        return master_wrapper(self.dispatcher, *args, **kwargs)

    def __getstate__(self):
        assert bodo.get_rank() == MASTER_RANK
        return self.dispatcher.py_func

    def __setstate__(self, state):
        assert bodo.get_rank() != MASTER_RANK
        mzh__bbb = state
        mhfq__vyoat = inspect.getsourcelines(mzh__bbb)[0][0]
        assert mhfq__vyoat.startswith('@bodo.jit') or mhfq__vyoat.startswith(
            '@jit')
        krev__zjym = eval(mhfq__vyoat[1:])
        self.dispatcher = krev__zjym(mzh__bbb)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    afrmb__ljzde = MPI.COMM_WORLD
    while True:
        kjli__wgwbc = afrmb__ljzde.bcast(None, root=MASTER_RANK)
        if kjli__wgwbc[0] == 'exec':
            mzh__bbb = pickle.loads(kjli__wgwbc[1])
            for yrufq__pse, dij__qzp in list(mzh__bbb.__globals__.items()):
                if isinstance(dij__qzp, MasterModeDispatcher):
                    mzh__bbb.__globals__[yrufq__pse] = dij__qzp.dispatcher
            if mzh__bbb.__module__ not in sys.modules:
                sys.modules[mzh__bbb.__module__] = pytypes.ModuleType(mzh__bbb
                    .__module__)
            mhfq__vyoat = inspect.getsourcelines(mzh__bbb)[0][0]
            assert mhfq__vyoat.startswith('@bodo.jit'
                ) or mhfq__vyoat.startswith('@jit')
            krev__zjym = eval(mhfq__vyoat[1:])
            func = krev__zjym(mzh__bbb)
            buxsf__nazx = kjli__wgwbc[2]
            ebq__chmqx = kjli__wgwbc[3]
            ouxrg__kyybf = []
            for cng__smdx in buxsf__nazx:
                if cng__smdx == 'scatter':
                    ouxrg__kyybf.append(bodo.scatterv(None))
                elif cng__smdx == 'bcast':
                    ouxrg__kyybf.append(afrmb__ljzde.bcast(None, root=
                        MASTER_RANK))
            aiz__hbt = {}
            for argname, cng__smdx in ebq__chmqx.items():
                if cng__smdx == 'scatter':
                    aiz__hbt[argname] = bodo.scatterv(None)
                elif cng__smdx == 'bcast':
                    aiz__hbt[argname] = afrmb__ljzde.bcast(None, root=
                        MASTER_RANK)
            gsmxn__gnfd = func(*ouxrg__kyybf, **aiz__hbt)
            if gsmxn__gnfd is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(gsmxn__gnfd)
            del (kjli__wgwbc, mzh__bbb, func, krev__zjym, buxsf__nazx,
                ebq__chmqx, ouxrg__kyybf, aiz__hbt, gsmxn__gnfd)
            gc.collect()
        elif kjli__wgwbc[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    afrmb__ljzde = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        buxsf__nazx = ['scatter' for hopj__nsjkt in range(len(args))]
        ebq__chmqx = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        agej__clgbn = func.py_func.__code__.co_varnames
        cbiga__xhom = func.targetoptions

        def get_distribution(argname):
            if argname in cbiga__xhom.get('distributed', []
                ) or argname in cbiga__xhom.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        buxsf__nazx = [get_distribution(argname) for argname in agej__clgbn
            [:len(args)]]
        ebq__chmqx = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    vtbq__xszs = pickle.dumps(func.py_func)
    afrmb__ljzde.bcast(['exec', vtbq__xszs, buxsf__nazx, ebq__chmqx])
    ouxrg__kyybf = []
    for pcp__ywrpo, cng__smdx in zip(args, buxsf__nazx):
        if cng__smdx == 'scatter':
            ouxrg__kyybf.append(bodo.scatterv(pcp__ywrpo))
        elif cng__smdx == 'bcast':
            afrmb__ljzde.bcast(pcp__ywrpo)
            ouxrg__kyybf.append(pcp__ywrpo)
    aiz__hbt = {}
    for argname, pcp__ywrpo in kwargs.items():
        cng__smdx = ebq__chmqx[argname]
        if cng__smdx == 'scatter':
            aiz__hbt[argname] = bodo.scatterv(pcp__ywrpo)
        elif cng__smdx == 'bcast':
            afrmb__ljzde.bcast(pcp__ywrpo)
            aiz__hbt[argname] = pcp__ywrpo
    qrb__ftn = []
    for yrufq__pse, dij__qzp in list(func.py_func.__globals__.items()):
        if isinstance(dij__qzp, MasterModeDispatcher):
            qrb__ftn.append((func.py_func.__globals__, yrufq__pse, func.
                py_func.__globals__[yrufq__pse]))
            func.py_func.__globals__[yrufq__pse] = dij__qzp.dispatcher
    gsmxn__gnfd = func(*ouxrg__kyybf, **aiz__hbt)
    for qmo__wrjd, yrufq__pse, dij__qzp in qrb__ftn:
        qmo__wrjd[yrufq__pse] = dij__qzp
    if gsmxn__gnfd is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        gsmxn__gnfd = bodo.gatherv(gsmxn__gnfd)
    return gsmxn__gnfd


def init_master_mode():
    if bodo.get_size() == 1:
        return
    global master_mode_on
    assert master_mode_on is False, 'init_master_mode can only be called once on each process'
    master_mode_on = True
    assert sys.version_info[:2] >= (3, 8
        ), 'Python 3.8+ required for master mode'
    from bodo import jit
    globals()['jit'] = jit
    import cloudpickle
    from mpi4py import MPI
    globals()['pickle'] = cloudpickle
    globals()['MPI'] = MPI

    def master_exit():
        MPI.COMM_WORLD.bcast(['exit'])
    if bodo.get_rank() == MASTER_RANK:
        import atexit
        atexit.register(master_exit)
    else:
        worker_loop()
