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
        modk__xjn = self._get_h5_type(lhs, rhs)
        if modk__xjn is not None:
            lhd__zyir = str(modk__xjn.dtype)
            ghyqc__yrfrq = 'def _h5_read_impl(dset, index):\n'
            ghyqc__yrfrq += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(modk__xjn.ndim, lhd__zyir))
            mjv__scb = {}
            exec(ghyqc__yrfrq, {}, mjv__scb)
            lwv__trm = mjv__scb['_h5_read_impl']
            jpc__qmr = compile_to_numba_ir(lwv__trm, {'bodo': bodo}
                ).blocks.popitem()[1]
            inxdo__nzyf = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(jpc__qmr, [rhs.value, inxdo__nzyf])
            dwwct__vkv = jpc__qmr.body[:-3]
            dwwct__vkv[-1].target = assign.target
            return dwwct__vkv
        return None

    def _get_h5_type(self, lhs, rhs):
        modk__xjn = self._get_h5_type_locals(lhs)
        if modk__xjn is not None:
            return modk__xjn
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        inxdo__nzyf = rhs.index if rhs.op == 'getitem' else rhs.index_var
        wbbq__fawg = guard(find_const, self.func_ir, inxdo__nzyf)
        require(not isinstance(wbbq__fawg, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            mhgbt__vpqy = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            pyoa__qvko = get_const_value_inner(self.func_ir, mhgbt__vpqy,
                arg_types=self.arg_types)
            obj_name_list.append(pyoa__qvko)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        pqikq__olkf = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        axm__rtrm = h5py.File(pqikq__olkf, 'r')
        rcf__tqd = axm__rtrm
        for pyoa__qvko in obj_name_list:
            rcf__tqd = rcf__tqd[pyoa__qvko]
        require(isinstance(rcf__tqd, h5py.Dataset))
        akpp__gjq = len(rcf__tqd.shape)
        ilwlj__lzus = numba.np.numpy_support.from_dtype(rcf__tqd.dtype)
        axm__rtrm.close()
        return types.Array(ilwlj__lzus, akpp__gjq, 'C')

    def _get_h5_type_locals(self, varname):
        vkteo__otd = self.locals.pop(varname, None)
        if vkteo__otd is None and varname is not None:
            vkteo__otd = self.flags.h5_types.get(varname, None)
        return vkteo__otd
