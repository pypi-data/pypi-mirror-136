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
        ranhr__dalxu = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, ranhr__dalxu)


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
        nvg__altof, wgrl__xsl, cze__mip, oqzd__slrfh = args
        fzfbq__xnbn = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        fzfbq__xnbn.data = nvg__altof
        fzfbq__xnbn.indices = wgrl__xsl
        fzfbq__xnbn.indptr = cze__mip
        fzfbq__xnbn.shape = oqzd__slrfh
        context.nrt.incref(builder, signature.args[0], nvg__altof)
        context.nrt.incref(builder, signature.args[1], wgrl__xsl)
        context.nrt.incref(builder, signature.args[2], cze__mip)
        return fzfbq__xnbn._getvalue()
    fra__zridy = CSRMatrixType(data_t.dtype, indices_t.dtype)
    rrnad__wgpa = fra__zridy(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return rrnad__wgpa, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    fzfbq__xnbn = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nuqnh__dfly = c.pyapi.object_getattr_string(val, 'data')
    vpzac__kus = c.pyapi.object_getattr_string(val, 'indices')
    vog__ncymf = c.pyapi.object_getattr_string(val, 'indptr')
    ysr__ixogu = c.pyapi.object_getattr_string(val, 'shape')
    fzfbq__xnbn.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1,
        'C'), nuqnh__dfly).value
    fzfbq__xnbn.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), vpzac__kus).value
    fzfbq__xnbn.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), vog__ncymf).value
    fzfbq__xnbn.shape = c.pyapi.to_native_value(types.UniTuple(types.int64,
        2), ysr__ixogu).value
    c.pyapi.decref(nuqnh__dfly)
    c.pyapi.decref(vpzac__kus)
    c.pyapi.decref(vog__ncymf)
    c.pyapi.decref(ysr__ixogu)
    nmyk__mjvyj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(fzfbq__xnbn._getvalue(), is_error=nmyk__mjvyj)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    aktbp__sjodi = c.context.insert_const_string(c.builder.module,
        'scipy.sparse')
    abpbp__ymws = c.pyapi.import_module_noblock(aktbp__sjodi)
    fzfbq__xnbn = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        fzfbq__xnbn.data)
    nuqnh__dfly = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        fzfbq__xnbn.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        fzfbq__xnbn.indices)
    vpzac__kus = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), fzfbq__xnbn.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        fzfbq__xnbn.indptr)
    vog__ncymf = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), fzfbq__xnbn.indptr, c.env_manager)
    ysr__ixogu = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        fzfbq__xnbn.shape, c.env_manager)
    jwwwt__ism = c.pyapi.tuple_pack([nuqnh__dfly, vpzac__kus, vog__ncymf])
    ijz__qgifh = c.pyapi.call_method(abpbp__ymws, 'csr_matrix', (jwwwt__ism,
        ysr__ixogu))
    c.pyapi.decref(jwwwt__ism)
    c.pyapi.decref(nuqnh__dfly)
    c.pyapi.decref(vpzac__kus)
    c.pyapi.decref(vog__ncymf)
    c.pyapi.decref(ysr__ixogu)
    c.pyapi.decref(abpbp__ymws)
    c.context.nrt.decref(c.builder, typ, val)
    return ijz__qgifh


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
    rmdv__dryy = A.dtype
    dorgk__yzdpb = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            qnt__mbr, lbf__qsn = A.shape
            afgvn__mqtb = numba.cpython.unicode._normalize_slice(idx[0],
                qnt__mbr)
            pzb__oog = numba.cpython.unicode._normalize_slice(idx[1], lbf__qsn)
            if afgvn__mqtb.step != 1 or pzb__oog.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            uirbi__fltk = afgvn__mqtb.start
            xibi__zreri = afgvn__mqtb.stop
            ojvuo__stxwu = pzb__oog.start
            rtav__fzv = pzb__oog.stop
            kss__kznx = A.indptr
            rokn__vkccy = A.indices
            yqggb__cwln = A.data
            fjqvs__aze = xibi__zreri - uirbi__fltk
            qokg__xrks = rtav__fzv - ojvuo__stxwu
            mezd__tkupn = 0
            uljnc__asj = 0
            for ovfi__dhujg in range(fjqvs__aze):
                lgr__cqx = kss__kznx[uirbi__fltk + ovfi__dhujg]
                xbu__zihw = kss__kznx[uirbi__fltk + ovfi__dhujg + 1]
                for xvbbf__oiu in range(lgr__cqx, xbu__zihw):
                    if rokn__vkccy[xvbbf__oiu] >= ojvuo__stxwu and rokn__vkccy[
                        xvbbf__oiu] < rtav__fzv:
                        mezd__tkupn += 1
            hnrj__amqq = np.empty(fjqvs__aze + 1, dorgk__yzdpb)
            qpw__ggr = np.empty(mezd__tkupn, dorgk__yzdpb)
            cyvh__kdrz = np.empty(mezd__tkupn, rmdv__dryy)
            hnrj__amqq[0] = 0
            for ovfi__dhujg in range(fjqvs__aze):
                lgr__cqx = kss__kznx[uirbi__fltk + ovfi__dhujg]
                xbu__zihw = kss__kznx[uirbi__fltk + ovfi__dhujg + 1]
                for xvbbf__oiu in range(lgr__cqx, xbu__zihw):
                    if rokn__vkccy[xvbbf__oiu] >= ojvuo__stxwu and rokn__vkccy[
                        xvbbf__oiu] < rtav__fzv:
                        qpw__ggr[uljnc__asj] = rokn__vkccy[xvbbf__oiu
                            ] - ojvuo__stxwu
                        cyvh__kdrz[uljnc__asj] = yqggb__cwln[xvbbf__oiu]
                        uljnc__asj += 1
                hnrj__amqq[ovfi__dhujg + 1] = uljnc__asj
            return init_csr_matrix(cyvh__kdrz, qpw__ggr, hnrj__amqq, (
                fjqvs__aze, qokg__xrks))
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
