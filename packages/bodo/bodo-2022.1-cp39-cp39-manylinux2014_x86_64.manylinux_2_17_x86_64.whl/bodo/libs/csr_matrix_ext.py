"""CSR Matrix data type implementation for scipy.sparse.csr_matrix
"""
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
import bodo
from bodo.utils.typing import BodoError


class CSRMatrixType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, dtype, idx_dtype):
        self.dtype = dtype
        self.idx_dtype = idx_dtype
        super(CSRMatrixType, self).__init__(name=
            f'CSRMatrixType({dtype}, {idx_dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    def copy(self):
        return CSRMatrixType(self.dtype, self.idx_dtype)


@register_model(CSRMatrixType)
class CSRMatrixModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ueznn__baii = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, ueznn__baii)


make_attribute_wrapper(CSRMatrixType, 'data', 'data')
make_attribute_wrapper(CSRMatrixType, 'indices', 'indices')
make_attribute_wrapper(CSRMatrixType, 'indptr', 'indptr')
make_attribute_wrapper(CSRMatrixType, 'shape', 'shape')


@intrinsic
def init_csr_matrix(typingctx, data_t, indices_t, indptr_t, shape_t=None):
    assert isinstance(data_t, types.Array)
    assert isinstance(indices_t, types.Array) and isinstance(indices_t.
        dtype, types.Integer)
    assert indices_t == indptr_t

    def codegen(context, builder, signature, args):
        cretk__hknwk, mpwne__kego, uzg__nmjx, rclj__bozc = args
        ess__tfqy = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        ess__tfqy.data = cretk__hknwk
        ess__tfqy.indices = mpwne__kego
        ess__tfqy.indptr = uzg__nmjx
        ess__tfqy.shape = rclj__bozc
        context.nrt.incref(builder, signature.args[0], cretk__hknwk)
        context.nrt.incref(builder, signature.args[1], mpwne__kego)
        context.nrt.incref(builder, signature.args[2], uzg__nmjx)
        return ess__tfqy._getvalue()
    ilpuf__wvd = CSRMatrixType(data_t.dtype, indices_t.dtype)
    qztld__lbe = ilpuf__wvd(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return qztld__lbe, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    ess__tfqy = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    waby__ingbw = c.pyapi.object_getattr_string(val, 'data')
    xdgg__czpv = c.pyapi.object_getattr_string(val, 'indices')
    imjxx__gop = c.pyapi.object_getattr_string(val, 'indptr')
    gvck__eqxv = c.pyapi.object_getattr_string(val, 'shape')
    ess__tfqy.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'),
        waby__ingbw).value
    ess__tfqy.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 
        1, 'C'), xdgg__czpv).value
    ess__tfqy.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), imjxx__gop).value
    ess__tfqy.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 2
        ), gvck__eqxv).value
    c.pyapi.decref(waby__ingbw)
    c.pyapi.decref(xdgg__czpv)
    c.pyapi.decref(imjxx__gop)
    c.pyapi.decref(gvck__eqxv)
    cqczh__qwupn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ess__tfqy._getvalue(), is_error=cqczh__qwupn)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    vqqwi__gmi = c.context.insert_const_string(c.builder.module, 'scipy.sparse'
        )
    cbpar__fyb = c.pyapi.import_module_noblock(vqqwi__gmi)
    ess__tfqy = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        ess__tfqy.data)
    waby__ingbw = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        ess__tfqy.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        ess__tfqy.indices)
    xdgg__czpv = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), ess__tfqy.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        ess__tfqy.indptr)
    imjxx__gop = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), ess__tfqy.indptr, c.env_manager)
    gvck__eqxv = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        ess__tfqy.shape, c.env_manager)
    ncyft__socc = c.pyapi.tuple_pack([waby__ingbw, xdgg__czpv, imjxx__gop])
    xseve__rrcoh = c.pyapi.call_method(cbpar__fyb, 'csr_matrix', (
        ncyft__socc, gvck__eqxv))
    c.pyapi.decref(ncyft__socc)
    c.pyapi.decref(waby__ingbw)
    c.pyapi.decref(xdgg__czpv)
    c.pyapi.decref(imjxx__gop)
    c.pyapi.decref(gvck__eqxv)
    c.pyapi.decref(cbpar__fyb)
    c.context.nrt.decref(c.builder, typ, val)
    return xseve__rrcoh


@overload(len, no_unliteral=True)
def overload_csr_matrix_len(A):
    if isinstance(A, CSRMatrixType):
        return lambda A: A.shape[0]


@overload_attribute(CSRMatrixType, 'ndim')
def overload_csr_matrix_ndim(A):
    return lambda A: 2


@overload_method(CSRMatrixType, 'copy', no_unliteral=True)
def overload_csr_matrix_copy(A):

    def copy_impl(A):
        return init_csr_matrix(A.data.copy(), A.indices.copy(), A.indptr.
            copy(), A.shape)
    return copy_impl


@overload(operator.getitem, no_unliteral=True)
def csr_matrix_getitem(A, idx):
    if not isinstance(A, CSRMatrixType):
        return
    olp__jrz = A.dtype
    ogn__kys = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            ioabh__sajsa, kih__ibr = A.shape
            ecjs__cje = numba.cpython.unicode._normalize_slice(idx[0],
                ioabh__sajsa)
            pbtyb__yjne = numba.cpython.unicode._normalize_slice(idx[1],
                kih__ibr)
            if ecjs__cje.step != 1 or pbtyb__yjne.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            pzrk__nhmb = ecjs__cje.start
            rxz__ofgx = ecjs__cje.stop
            muppi__gezae = pbtyb__yjne.start
            usb__wzcrr = pbtyb__yjne.stop
            dzv__mra = A.indptr
            mgvd__mjg = A.indices
            cev__hpr = A.data
            anx__hspyc = rxz__ofgx - pzrk__nhmb
            wtcg__zggw = usb__wzcrr - muppi__gezae
            cahb__qhgg = 0
            shksa__vitjy = 0
            for mnn__gekcz in range(anx__hspyc):
                eair__kmwwn = dzv__mra[pzrk__nhmb + mnn__gekcz]
                plhi__ichq = dzv__mra[pzrk__nhmb + mnn__gekcz + 1]
                for zcbwz__dubai in range(eair__kmwwn, plhi__ichq):
                    if mgvd__mjg[zcbwz__dubai] >= muppi__gezae and mgvd__mjg[
                        zcbwz__dubai] < usb__wzcrr:
                        cahb__qhgg += 1
            ycjy__fqiuf = np.empty(anx__hspyc + 1, ogn__kys)
            jakdq__smies = np.empty(cahb__qhgg, ogn__kys)
            yczvp__lotnk = np.empty(cahb__qhgg, olp__jrz)
            ycjy__fqiuf[0] = 0
            for mnn__gekcz in range(anx__hspyc):
                eair__kmwwn = dzv__mra[pzrk__nhmb + mnn__gekcz]
                plhi__ichq = dzv__mra[pzrk__nhmb + mnn__gekcz + 1]
                for zcbwz__dubai in range(eair__kmwwn, plhi__ichq):
                    if mgvd__mjg[zcbwz__dubai] >= muppi__gezae and mgvd__mjg[
                        zcbwz__dubai] < usb__wzcrr:
                        jakdq__smies[shksa__vitjy] = mgvd__mjg[zcbwz__dubai
                            ] - muppi__gezae
                        yczvp__lotnk[shksa__vitjy] = cev__hpr[zcbwz__dubai]
                        shksa__vitjy += 1
                ycjy__fqiuf[mnn__gekcz + 1] = shksa__vitjy
            return init_csr_matrix(yczvp__lotnk, jakdq__smies, ycjy__fqiuf,
                (anx__hspyc, wtcg__zggw))
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
