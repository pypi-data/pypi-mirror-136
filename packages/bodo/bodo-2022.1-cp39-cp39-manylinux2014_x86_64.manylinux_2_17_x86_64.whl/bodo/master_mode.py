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
        usxko__konwq = state
        ccp__qhfh = inspect.getsourcelines(usxko__konwq)[0][0]
        assert ccp__qhfh.startswith('@bodo.jit') or ccp__qhfh.startswith('@jit'
            )
        dmgpe__mplt = eval(ccp__qhfh[1:])
        self.dispatcher = dmgpe__mplt(usxko__konwq)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    xez__gks = MPI.COMM_WORLD
    while True:
        mppk__rhnbr = xez__gks.bcast(None, root=MASTER_RANK)
        if mppk__rhnbr[0] == 'exec':
            usxko__konwq = pickle.loads(mppk__rhnbr[1])
            for excup__scuwm, qhkf__wue in list(usxko__konwq.__globals__.
                items()):
                if isinstance(qhkf__wue, MasterModeDispatcher):
                    usxko__konwq.__globals__[excup__scuwm
                        ] = qhkf__wue.dispatcher
            if usxko__konwq.__module__ not in sys.modules:
                sys.modules[usxko__konwq.__module__] = pytypes.ModuleType(
                    usxko__konwq.__module__)
            ccp__qhfh = inspect.getsourcelines(usxko__konwq)[0][0]
            assert ccp__qhfh.startswith('@bodo.jit') or ccp__qhfh.startswith(
                '@jit')
            dmgpe__mplt = eval(ccp__qhfh[1:])
            func = dmgpe__mplt(usxko__konwq)
            coo__ptr = mppk__rhnbr[2]
            dxzk__gva = mppk__rhnbr[3]
            bkeh__bbkt = []
            for hlla__nkh in coo__ptr:
                if hlla__nkh == 'scatter':
                    bkeh__bbkt.append(bodo.scatterv(None))
                elif hlla__nkh == 'bcast':
                    bkeh__bbkt.append(xez__gks.bcast(None, root=MASTER_RANK))
            hjtpk__qlxtx = {}
            for argname, hlla__nkh in dxzk__gva.items():
                if hlla__nkh == 'scatter':
                    hjtpk__qlxtx[argname] = bodo.scatterv(None)
                elif hlla__nkh == 'bcast':
                    hjtpk__qlxtx[argname] = xez__gks.bcast(None, root=
                        MASTER_RANK)
            byba__wtgdg = func(*bkeh__bbkt, **hjtpk__qlxtx)
            if byba__wtgdg is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(byba__wtgdg)
            del (mppk__rhnbr, usxko__konwq, func, dmgpe__mplt, coo__ptr,
                dxzk__gva, bkeh__bbkt, hjtpk__qlxtx, byba__wtgdg)
            gc.collect()
        elif mppk__rhnbr[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    xez__gks = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        coo__ptr = ['scatter' for bsnwn__znio in range(len(args))]
        dxzk__gva = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        qzcl__dbdiz = func.py_func.__code__.co_varnames
        dkt__cmwrj = func.targetoptions

        def get_distribution(argname):
            if argname in dkt__cmwrj.get('distributed', []
                ) or argname in dkt__cmwrj.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        coo__ptr = [get_distribution(argname) for argname in qzcl__dbdiz[:
            len(args)]]
        dxzk__gva = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    qpp__smw = pickle.dumps(func.py_func)
    xez__gks.bcast(['exec', qpp__smw, coo__ptr, dxzk__gva])
    bkeh__bbkt = []
    for xnuwg__degl, hlla__nkh in zip(args, coo__ptr):
        if hlla__nkh == 'scatter':
            bkeh__bbkt.append(bodo.scatterv(xnuwg__degl))
        elif hlla__nkh == 'bcast':
            xez__gks.bcast(xnuwg__degl)
            bkeh__bbkt.append(xnuwg__degl)
    hjtpk__qlxtx = {}
    for argname, xnuwg__degl in kwargs.items():
        hlla__nkh = dxzk__gva[argname]
        if hlla__nkh == 'scatter':
            hjtpk__qlxtx[argname] = bodo.scatterv(xnuwg__degl)
        elif hlla__nkh == 'bcast':
            xez__gks.bcast(xnuwg__degl)
            hjtpk__qlxtx[argname] = xnuwg__degl
    ppuzi__zdhlu = []
    for excup__scuwm, qhkf__wue in list(func.py_func.__globals__.items()):
        if isinstance(qhkf__wue, MasterModeDispatcher):
            ppuzi__zdhlu.append((func.py_func.__globals__, excup__scuwm,
                func.py_func.__globals__[excup__scuwm]))
            func.py_func.__globals__[excup__scuwm] = qhkf__wue.dispatcher
    byba__wtgdg = func(*bkeh__bbkt, **hjtpk__qlxtx)
    for mun__fwh, excup__scuwm, qhkf__wue in ppuzi__zdhlu:
        mun__fwh[excup__scuwm] = qhkf__wue
    if byba__wtgdg is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        byba__wtgdg = bodo.gatherv(byba__wtgdg)
    return byba__wtgdg


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
