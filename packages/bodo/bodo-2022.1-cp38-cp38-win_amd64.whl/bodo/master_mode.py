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
        cwj__his = state
        sfzi__znpxe = inspect.getsourcelines(cwj__his)[0][0]
        assert sfzi__znpxe.startswith('@bodo.jit') or sfzi__znpxe.startswith(
            '@jit')
        peime__row = eval(sfzi__znpxe[1:])
        self.dispatcher = peime__row(cwj__his)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    yss__esxf = MPI.COMM_WORLD
    while True:
        mpkoj__volx = yss__esxf.bcast(None, root=MASTER_RANK)
        if mpkoj__volx[0] == 'exec':
            cwj__his = pickle.loads(mpkoj__volx[1])
            for qyk__hchse, ynooh__frz in list(cwj__his.__globals__.items()):
                if isinstance(ynooh__frz, MasterModeDispatcher):
                    cwj__his.__globals__[qyk__hchse] = ynooh__frz.dispatcher
            if cwj__his.__module__ not in sys.modules:
                sys.modules[cwj__his.__module__] = pytypes.ModuleType(cwj__his
                    .__module__)
            sfzi__znpxe = inspect.getsourcelines(cwj__his)[0][0]
            assert sfzi__znpxe.startswith('@bodo.jit'
                ) or sfzi__znpxe.startswith('@jit')
            peime__row = eval(sfzi__znpxe[1:])
            func = peime__row(cwj__his)
            iqfx__txu = mpkoj__volx[2]
            mhfe__qtjl = mpkoj__volx[3]
            nwd__vwq = []
            for butda__ldvvm in iqfx__txu:
                if butda__ldvvm == 'scatter':
                    nwd__vwq.append(bodo.scatterv(None))
                elif butda__ldvvm == 'bcast':
                    nwd__vwq.append(yss__esxf.bcast(None, root=MASTER_RANK))
            nlrer__ljxgh = {}
            for argname, butda__ldvvm in mhfe__qtjl.items():
                if butda__ldvvm == 'scatter':
                    nlrer__ljxgh[argname] = bodo.scatterv(None)
                elif butda__ldvvm == 'bcast':
                    nlrer__ljxgh[argname] = yss__esxf.bcast(None, root=
                        MASTER_RANK)
            idhh__gmow = func(*nwd__vwq, **nlrer__ljxgh)
            if idhh__gmow is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(idhh__gmow)
            del (mpkoj__volx, cwj__his, func, peime__row, iqfx__txu,
                mhfe__qtjl, nwd__vwq, nlrer__ljxgh, idhh__gmow)
            gc.collect()
        elif mpkoj__volx[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    yss__esxf = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        iqfx__txu = ['scatter' for dlie__syez in range(len(args))]
        mhfe__qtjl = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        mplw__fdm = func.py_func.__code__.co_varnames
        avgza__rpxo = func.targetoptions

        def get_distribution(argname):
            if argname in avgza__rpxo.get('distributed', []
                ) or argname in avgza__rpxo.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        iqfx__txu = [get_distribution(argname) for argname in mplw__fdm[:
            len(args)]]
        mhfe__qtjl = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    ijxc__pdssz = pickle.dumps(func.py_func)
    yss__esxf.bcast(['exec', ijxc__pdssz, iqfx__txu, mhfe__qtjl])
    nwd__vwq = []
    for leg__nnb, butda__ldvvm in zip(args, iqfx__txu):
        if butda__ldvvm == 'scatter':
            nwd__vwq.append(bodo.scatterv(leg__nnb))
        elif butda__ldvvm == 'bcast':
            yss__esxf.bcast(leg__nnb)
            nwd__vwq.append(leg__nnb)
    nlrer__ljxgh = {}
    for argname, leg__nnb in kwargs.items():
        butda__ldvvm = mhfe__qtjl[argname]
        if butda__ldvvm == 'scatter':
            nlrer__ljxgh[argname] = bodo.scatterv(leg__nnb)
        elif butda__ldvvm == 'bcast':
            yss__esxf.bcast(leg__nnb)
            nlrer__ljxgh[argname] = leg__nnb
    jkc__svcmk = []
    for qyk__hchse, ynooh__frz in list(func.py_func.__globals__.items()):
        if isinstance(ynooh__frz, MasterModeDispatcher):
            jkc__svcmk.append((func.py_func.__globals__, qyk__hchse, func.
                py_func.__globals__[qyk__hchse]))
            func.py_func.__globals__[qyk__hchse] = ynooh__frz.dispatcher
    idhh__gmow = func(*nwd__vwq, **nlrer__ljxgh)
    for rsc__gmm, qyk__hchse, ynooh__frz in jkc__svcmk:
        rsc__gmm[qyk__hchse] = ynooh__frz
    if idhh__gmow is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        idhh__gmow = bodo.gatherv(idhh__gmow)
    return idhh__gmow


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
