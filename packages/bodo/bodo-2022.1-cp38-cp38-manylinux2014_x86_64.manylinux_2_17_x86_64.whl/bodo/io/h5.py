"""
Analysis and transformation for HDF5 support.
"""
import types as pytypes
import numba
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, find_callname, find_const, get_definition, guard, replace_arg_nodes, require
import bodo
import bodo.io
from bodo.utils.transform import get_const_value_inner


class H5_IO:

    def __init__(self, func_ir, _locals, flags, arg_types):
        self.func_ir = func_ir
        self.locals = _locals
        self.flags = flags
        self.arg_types = arg_types

    def handle_possible_h5_read(self, assign, lhs, rhs):
        kqn__fais = self._get_h5_type(lhs, rhs)
        if kqn__fais is not None:
            bkuo__rdx = str(kqn__fais.dtype)
            gkgp__sgzm = 'def _h5_read_impl(dset, index):\n'
            gkgp__sgzm += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(kqn__fais.ndim, bkuo__rdx))
            dab__vktr = {}
            exec(gkgp__sgzm, {}, dab__vktr)
            uns__yvol = dab__vktr['_h5_read_impl']
            vhbce__lfhv = compile_to_numba_ir(uns__yvol, {'bodo': bodo}
                ).blocks.popitem()[1]
            ewgqk__amp = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(vhbce__lfhv, [rhs.value, ewgqk__amp])
            isbg__xnt = vhbce__lfhv.body[:-3]
            isbg__xnt[-1].target = assign.target
            return isbg__xnt
        return None

    def _get_h5_type(self, lhs, rhs):
        kqn__fais = self._get_h5_type_locals(lhs)
        if kqn__fais is not None:
            return kqn__fais
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        ewgqk__amp = rhs.index if rhs.op == 'getitem' else rhs.index_var
        jdds__jzq = guard(find_const, self.func_ir, ewgqk__amp)
        require(not isinstance(jdds__jzq, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            rebe__rjay = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            ike__dty = get_const_value_inner(self.func_ir, rebe__rjay,
                arg_types=self.arg_types)
            obj_name_list.append(ike__dty)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        edmy__dpf = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        pbna__bbxk = h5py.File(edmy__dpf, 'r')
        lvkjt__wzsja = pbna__bbxk
        for ike__dty in obj_name_list:
            lvkjt__wzsja = lvkjt__wzsja[ike__dty]
        require(isinstance(lvkjt__wzsja, h5py.Dataset))
        mhsk__hfjb = len(lvkjt__wzsja.shape)
        dsxb__gfvc = numba.np.numpy_support.from_dtype(lvkjt__wzsja.dtype)
        pbna__bbxk.close()
        return types.Array(dsxb__gfvc, mhsk__hfjb, 'C')

    def _get_h5_type_locals(self, varname):
        pwr__lsv = self.locals.pop(varname, None)
        if pwr__lsv is None and varname is not None:
            pwr__lsv = self.flags.h5_types.get(varname, None)
        return pwr__lsv
