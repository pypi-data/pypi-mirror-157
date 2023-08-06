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
        dyxq__hfe = state
        ucc__dxkw = inspect.getsourcelines(dyxq__hfe)[0][0]
        assert ucc__dxkw.startswith('@bodo.jit') or ucc__dxkw.startswith('@jit'
            )
        ghz__soyn = eval(ucc__dxkw[1:])
        self.dispatcher = ghz__soyn(dyxq__hfe)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    azh__vdn = MPI.COMM_WORLD
    while True:
        bnqsr__syitz = azh__vdn.bcast(None, root=MASTER_RANK)
        if bnqsr__syitz[0] == 'exec':
            dyxq__hfe = pickle.loads(bnqsr__syitz[1])
            for okxv__wefdw, nbf__rhwjp in list(dyxq__hfe.__globals__.items()):
                if isinstance(nbf__rhwjp, MasterModeDispatcher):
                    dyxq__hfe.__globals__[okxv__wefdw] = nbf__rhwjp.dispatcher
            if dyxq__hfe.__module__ not in sys.modules:
                sys.modules[dyxq__hfe.__module__] = pytypes.ModuleType(
                    dyxq__hfe.__module__)
            ucc__dxkw = inspect.getsourcelines(dyxq__hfe)[0][0]
            assert ucc__dxkw.startswith('@bodo.jit') or ucc__dxkw.startswith(
                '@jit')
            ghz__soyn = eval(ucc__dxkw[1:])
            func = ghz__soyn(dyxq__hfe)
            bjtx__poa = bnqsr__syitz[2]
            ssx__hsev = bnqsr__syitz[3]
            kyx__lkd = []
            for zit__olts in bjtx__poa:
                if zit__olts == 'scatter':
                    kyx__lkd.append(bodo.scatterv(None))
                elif zit__olts == 'bcast':
                    kyx__lkd.append(azh__vdn.bcast(None, root=MASTER_RANK))
            hohc__kqi = {}
            for argname, zit__olts in ssx__hsev.items():
                if zit__olts == 'scatter':
                    hohc__kqi[argname] = bodo.scatterv(None)
                elif zit__olts == 'bcast':
                    hohc__kqi[argname] = azh__vdn.bcast(None, root=MASTER_RANK)
            icfw__vfa = func(*kyx__lkd, **hohc__kqi)
            if icfw__vfa is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(icfw__vfa)
            del (bnqsr__syitz, dyxq__hfe, func, ghz__soyn, bjtx__poa,
                ssx__hsev, kyx__lkd, hohc__kqi, icfw__vfa)
            gc.collect()
        elif bnqsr__syitz[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    azh__vdn = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        bjtx__poa = ['scatter' for skr__ooeot in range(len(args))]
        ssx__hsev = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        izohc__oldwd = func.py_func.__code__.co_varnames
        jjq__bss = func.targetoptions

        def get_distribution(argname):
            if argname in jjq__bss.get('distributed', []
                ) or argname in jjq__bss.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        bjtx__poa = [get_distribution(argname) for argname in izohc__oldwd[
            :len(args)]]
        ssx__hsev = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    rmf__mdgom = pickle.dumps(func.py_func)
    azh__vdn.bcast(['exec', rmf__mdgom, bjtx__poa, ssx__hsev])
    kyx__lkd = []
    for zsm__cgxcb, zit__olts in zip(args, bjtx__poa):
        if zit__olts == 'scatter':
            kyx__lkd.append(bodo.scatterv(zsm__cgxcb))
        elif zit__olts == 'bcast':
            azh__vdn.bcast(zsm__cgxcb)
            kyx__lkd.append(zsm__cgxcb)
    hohc__kqi = {}
    for argname, zsm__cgxcb in kwargs.items():
        zit__olts = ssx__hsev[argname]
        if zit__olts == 'scatter':
            hohc__kqi[argname] = bodo.scatterv(zsm__cgxcb)
        elif zit__olts == 'bcast':
            azh__vdn.bcast(zsm__cgxcb)
            hohc__kqi[argname] = zsm__cgxcb
    vre__kqui = []
    for okxv__wefdw, nbf__rhwjp in list(func.py_func.__globals__.items()):
        if isinstance(nbf__rhwjp, MasterModeDispatcher):
            vre__kqui.append((func.py_func.__globals__, okxv__wefdw, func.
                py_func.__globals__[okxv__wefdw]))
            func.py_func.__globals__[okxv__wefdw] = nbf__rhwjp.dispatcher
    icfw__vfa = func(*kyx__lkd, **hohc__kqi)
    for ief__bsaw, okxv__wefdw, nbf__rhwjp in vre__kqui:
        ief__bsaw[okxv__wefdw] = nbf__rhwjp
    if icfw__vfa is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        icfw__vfa = bodo.gatherv(icfw__vfa)
    return icfw__vfa


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
