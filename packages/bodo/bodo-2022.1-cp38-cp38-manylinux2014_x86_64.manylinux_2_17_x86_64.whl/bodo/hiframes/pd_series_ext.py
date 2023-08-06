"""
Implement pd.Series typing and data model handling.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import bound_function, signature
from numba.extending import infer_getattr, intrinsic, lower_builtin, lower_cast, models, overload, overload_attribute, overload_method, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.io import csv_cpp
from bodo.libs.int_arr_ext import IntDtype
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_overload_const_str, get_overload_const_tuple, get_udf_error_msg, get_udf_out_arr_type, is_heterogeneous_tuple_type, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_int, is_overload_none, raise_bodo_error
_csv_output_is_dir = types.ExternalFunction('csv_output_is_dir', types.int8
    (types.voidptr))
ll.add_symbol('csv_output_is_dir', csv_cpp.csv_output_is_dir)


class SeriesType(types.IterableType, types.ArrayCompatible):
    ndim = 1

    def __init__(self, dtype, data=None, index=None, name_typ=None, dist=None):
        from bodo.hiframes.pd_index_ext import RangeIndexType
        from bodo.transforms.distributed_analysis import Distribution
        data = dtype_to_array_type(dtype) if data is None else data
        dtype = dtype.dtype if isinstance(dtype, IntDtype) else dtype
        self.dtype = dtype
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        index = RangeIndexType(types.none) if index is None else index
        self.index = index
        self.name_typ = name_typ
        dist = Distribution.OneD_Var if dist is None else dist
        self.dist = dist
        super(SeriesType, self).__init__(name=
            f'series({dtype}, {data}, {index}, {name_typ}, {dist})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self, dtype=None, index=None, dist=None):
        if index is None:
            index = self.index
        if dist is None:
            dist = self.dist
        if dtype is None:
            dtype = self.dtype
            data = self.data
        else:
            data = dtype_to_array_type(dtype)
        return SeriesType(dtype, data, index, self.name_typ, dist)

    @property
    def key(self):
        return self.dtype, self.data, self.index, self.name_typ, self.dist

    def unify(self, typingctx, other):
        from bodo.transforms.distributed_analysis import Distribution
        if isinstance(other, SeriesType):
            xdyb__tfdox = (self.index if self.index == other.index else
                self.index.unify(typingctx, other.index))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if other.dtype == self.dtype or not other.dtype.is_precise():
                return SeriesType(self.dtype, self.data.unify(typingctx,
                    other.data), xdyb__tfdox, dist=dist)
        return super(SeriesType, self).unify(typingctx, other)

    def can_convert_to(self, typingctx, other):
        from numba.core.typeconv import Conversion
        if (isinstance(other, SeriesType) and self.dtype == other.dtype and
            self.data == other.data and self.index == other.index and self.
            name_typ == other.name_typ and self.dist != other.dist):
            return Conversion.safe

    def is_precise(self):
        return self.dtype.is_precise()

    @property
    def iterator_type(self):
        return self.data.iterator_type

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class HeterogeneousSeriesType(types.Type):
    ndim = 1

    def __init__(self, data=None, index=None, name_typ=None):
        from bodo.hiframes.pd_index_ext import RangeIndexType
        from bodo.transforms.distributed_analysis import Distribution
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        index = RangeIndexType(types.none) if index is None else index
        self.index = index
        self.name_typ = name_typ
        self.dist = Distribution.REP
        super(HeterogeneousSeriesType, self).__init__(name=
            f'heter_series({data}, {index}, {name_typ})')

    def copy(self, index=None, dist=None):
        from bodo.transforms.distributed_analysis import Distribution
        assert dist == Distribution.REP, 'invalid distribution for HeterogeneousSeriesType'
        if index is None:
            index = self.index.copy()
        return HeterogeneousSeriesType(self.data, index, self.name_typ)

    @property
    def key(self):
        return self.data, self.index, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@lower_builtin('getiter', SeriesType)
def series_getiter(context, builder, sig, args):
    gny__mdjxz = get_series_payload(context, builder, sig.args[0], args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].data))
    return impl(builder, (gny__mdjxz.data,))


@infer_getattr
class HeterSeriesAttribute(OverloadedKeyAttributeTemplate):
    key = HeterogeneousSeriesType

    def generic_resolve(self, S, attr):
        from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
        if self._is_existing_attr(attr):
            return
        if isinstance(S.index, HeterogeneousIndexType
            ) and is_overload_constant_tuple(S.index.data):
            sfml__hwiiw = get_overload_const_tuple(S.index.data)
            if attr in sfml__hwiiw:
                bkri__reyld = sfml__hwiiw.index(attr)
                return S.data[bkri__reyld]


def is_str_series_typ(t):
    return isinstance(t, SeriesType) and t.dtype == string_type


def is_dt64_series_typ(t):
    return isinstance(t, SeriesType) and t.dtype == types.NPDatetime('ns')


def is_timedelta64_series_typ(t):
    return isinstance(t, SeriesType) and t.dtype == types.NPTimedelta('ns')


def is_datetime_date_series_typ(t):
    return isinstance(t, SeriesType) and t.dtype == datetime_date_type


class SeriesPayloadType(types.Type):

    def __init__(self, series_type):
        self.series_type = series_type
        super(SeriesPayloadType, self).__init__(name=
            f'SeriesPayloadType({series_type})')

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesPayloadType)
class SeriesPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        jxn__iwuv = [('data', fe_type.series_type.data), ('index', fe_type.
            series_type.index), ('name', fe_type.series_type.name_typ)]
        super(SeriesPayloadModel, self).__init__(dmm, fe_type, jxn__iwuv)


@register_model(HeterogeneousSeriesType)
@register_model(SeriesType)
class SeriesModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = SeriesPayloadType(fe_type)
        jxn__iwuv = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(SeriesModel, self).__init__(dmm, fe_type, jxn__iwuv)


def define_series_dtor(context, builder, series_type, payload_type):
    azxs__quc = builder.module
    tbe__kxqf = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    yclk__ucizg = cgutils.get_or_insert_function(azxs__quc, tbe__kxqf, name
        ='.dtor.series.{}'.format(series_type))
    if not yclk__ucizg.is_declaration:
        return yclk__ucizg
    yclk__ucizg.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(yclk__ucizg.append_basic_block())
    scfsx__nqe = yclk__ucizg.args[0]
    mzd__xdkyv = context.get_value_type(payload_type).as_pointer()
    kvjdw__ywnkb = builder.bitcast(scfsx__nqe, mzd__xdkyv)
    fmtk__tqzdj = context.make_helper(builder, payload_type, ref=kvjdw__ywnkb)
    context.nrt.decref(builder, series_type.data, fmtk__tqzdj.data)
    context.nrt.decref(builder, series_type.index, fmtk__tqzdj.index)
    context.nrt.decref(builder, series_type.name_typ, fmtk__tqzdj.name)
    builder.ret_void()
    return yclk__ucizg


def construct_series(context, builder, series_type, data_val, index_val,
    name_val):
    payload_type = SeriesPayloadType(series_type)
    gny__mdjxz = cgutils.create_struct_proxy(payload_type)(context, builder)
    gny__mdjxz.data = data_val
    gny__mdjxz.index = index_val
    gny__mdjxz.name = name_val
    phh__rhgvj = context.get_value_type(payload_type)
    tisw__fovz = context.get_abi_sizeof(phh__rhgvj)
    byzx__yfcxh = define_series_dtor(context, builder, series_type,
        payload_type)
    glgiq__qvwrc = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tisw__fovz), byzx__yfcxh)
    xdq__ufcz = context.nrt.meminfo_data(builder, glgiq__qvwrc)
    iuf__nof = builder.bitcast(xdq__ufcz, phh__rhgvj.as_pointer())
    builder.store(gny__mdjxz._getvalue(), iuf__nof)
    series = cgutils.create_struct_proxy(series_type)(context, builder)
    series.meminfo = glgiq__qvwrc
    series.parent = cgutils.get_null_value(series.parent.type)
    return series._getvalue()


@intrinsic
def init_series(typingctx, data, index, name=None):
    from bodo.hiframes.pd_index_ext import is_pd_index_type
    from bodo.hiframes.pd_multi_index_ext import MultiIndexType
    assert is_pd_index_type(index) or isinstance(index, MultiIndexType)
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        data_val, index_val, name_val = args
        series_type = signature.return_type
        pnq__gghxv = construct_series(context, builder, series_type,
            data_val, index_val, name_val)
        context.nrt.incref(builder, signature.args[0], data_val)
        context.nrt.incref(builder, signature.args[1], index_val)
        context.nrt.incref(builder, signature.args[2], name_val)
        return pnq__gghxv
    if is_heterogeneous_tuple_type(data):
        fvl__spfh = HeterogeneousSeriesType(data, index, name)
    else:
        dtype = data.dtype
        data = if_series_to_array_type(data)
        fvl__spfh = SeriesType(dtype, data, index, name)
    sig = signature(fvl__spfh, data, index, name)
    return sig, codegen


def init_series_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) >= 2 and not kws
    data = args[0]
    index = args[1]
    cwur__ghc = self.typemap[data.name]
    if is_heterogeneous_tuple_type(cwur__ghc) or isinstance(cwur__ghc,
        types.BaseTuple):
        return None
    hum__acoak = self.typemap[index.name]
    if not isinstance(hum__acoak, HeterogeneousIndexType
        ) and equiv_set.has_shape(data) and equiv_set.has_shape(index):
        equiv_set.insert_equiv(data, index)
    if equiv_set.has_shape(data):
        return ArrayAnalysis.AnalyzeResult(shape=data, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_init_series = (
    init_series_equiv)


def get_series_payload(context, builder, series_type, value):
    glgiq__qvwrc = cgutils.create_struct_proxy(series_type)(context,
        builder, value).meminfo
    payload_type = SeriesPayloadType(series_type)
    fmtk__tqzdj = context.nrt.meminfo_data(builder, glgiq__qvwrc)
    mzd__xdkyv = context.get_value_type(payload_type).as_pointer()
    fmtk__tqzdj = builder.bitcast(fmtk__tqzdj, mzd__xdkyv)
    return context.make_helper(builder, payload_type, ref=fmtk__tqzdj)


@intrinsic
def get_series_data(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        gny__mdjxz = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, series_typ.data,
            gny__mdjxz.data)
    fvl__spfh = series_typ.data
    sig = signature(fvl__spfh, series_typ)
    return sig, codegen


@intrinsic
def get_series_index(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        gny__mdjxz = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, series_typ.index,
            gny__mdjxz.index)
    fvl__spfh = series_typ.index
    sig = signature(fvl__spfh, series_typ)
    return sig, codegen


@intrinsic
def get_series_name(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        gny__mdjxz = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            gny__mdjxz.name)
    sig = signature(series_typ.name_typ, series_typ)
    return sig, codegen


def get_series_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    nxle__jtqy = args[0]
    cwur__ghc = self.typemap[nxle__jtqy.name].data
    if is_heterogeneous_tuple_type(cwur__ghc) or isinstance(cwur__ghc,
        types.BaseTuple):
        return None
    if equiv_set.has_shape(nxle__jtqy):
        return ArrayAnalysis.AnalyzeResult(shape=nxle__jtqy, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_get_series_data
    ) = get_series_data_equiv


def get_series_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    nxle__jtqy = args[0]
    hum__acoak = self.typemap[nxle__jtqy.name].index
    if isinstance(hum__acoak, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(nxle__jtqy):
        return ArrayAnalysis.AnalyzeResult(shape=nxle__jtqy, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_get_series_index
    ) = get_series_index_equiv


def alias_ext_init_series(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    if len(args) > 1:
        numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
            arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_series',
    'bodo.hiframes.pd_series_ext'] = alias_ext_init_series


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_series_data',
    'bodo.hiframes.pd_series_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_series_index',
    'bodo.hiframes.pd_series_ext'] = alias_ext_dummy_func


def is_series_type(typ):
    return isinstance(typ, SeriesType)


def if_series_to_array_type(typ):
    if isinstance(typ, SeriesType):
        return typ.data
    return typ


@lower_cast(SeriesType, SeriesType)
def cast_series(context, builder, fromty, toty, val):
    if fromty.copy(index=toty.index) == toty and isinstance(fromty.index,
        bodo.hiframes.pd_index_ext.RangeIndexType) and isinstance(toty.
        index, bodo.hiframes.pd_index_ext.NumericIndexType):
        gny__mdjxz = get_series_payload(context, builder, fromty, val)
        xdyb__tfdox = context.cast(builder, gny__mdjxz.index, fromty.index,
            toty.index)
        context.nrt.incref(builder, fromty.data, gny__mdjxz.data)
        context.nrt.incref(builder, fromty.name_typ, gny__mdjxz.name)
        return construct_series(context, builder, toty, gny__mdjxz.data,
            xdyb__tfdox, gny__mdjxz.name)
    if (fromty.dtype == toty.dtype and fromty.data == toty.data and fromty.
        index == toty.index and fromty.name_typ == toty.name_typ and fromty
        .dist != toty.dist):
        return val
    return val


@infer_getattr
class SeriesAttribute(OverloadedKeyAttributeTemplate):
    key = SeriesType

    @bound_function('series.head')
    def resolve_head(self, ary, args, kws):
        zwsun__xqgtf = 'Series.head'
        lnyn__cwi = 'n',
        rox__mgqlm = {'n': 5}
        pysig, rjdwi__kmzat = bodo.utils.typing.fold_typing_args(zwsun__xqgtf,
            args, kws, lnyn__cwi, rox__mgqlm)
        dhmkt__hnzhf = rjdwi__kmzat[0]
        if not is_overload_int(dhmkt__hnzhf):
            raise BodoError(f"{zwsun__xqgtf}(): 'n' must be an Integer")
        rmiga__swa = ary
        return rmiga__swa(*rjdwi__kmzat).replace(pysig=pysig)

    def _resolve_map_func(self, ary, func, pysig, fname, f_args=None, kws=None
        ):
        dtype = ary.dtype
        if dtype == types.NPDatetime('ns'):
            dtype = pd_timestamp_type
        if dtype == types.NPTimedelta('ns'):
            dtype = pd_timedelta_type
        kwhf__coee = dtype,
        if f_args is not None:
            kwhf__coee += tuple(f_args.types)
        if kws is None:
            kws = {}
        ylzzs__dlfuc = False
        eaw__noqok = True
        if fname == 'map' and isinstance(func, types.DictType):
            efet__fpy = func.value_type
            ylzzs__dlfuc = True
        else:
            try:
                if types.unliteral(func) == types.unicode_type:
                    if not is_overload_constant_str(func):
                        raise BodoError(
                            f'Series.apply(): string argument (for builtins) must be a compile time constant'
                            )
                    efet__fpy = bodo.utils.transform.get_udf_str_return_type(
                        ary, get_overload_const_str(func), self.context,
                        'Series.apply')
                    eaw__noqok = False
                elif bodo.utils.typing.is_numpy_ufunc(func):
                    efet__fpy = func.get_call_type(self.context, (ary,), {}
                        ).return_type
                    eaw__noqok = False
                else:
                    efet__fpy = get_const_func_output_type(func, kwhf__coee,
                        kws, self.context, numba.core.registry.cpu_target.
                        target_context)
            except Exception as krlu__tjdnx:
                raise BodoError(get_udf_error_msg(f'Series.{fname}()',
                    krlu__tjdnx))
        if eaw__noqok:
            if isinstance(efet__fpy, (SeriesType, HeterogeneousSeriesType)
                ) and efet__fpy.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(efet__fpy, HeterogeneousSeriesType):
                sth__cgkag, ichj__rpr = efet__fpy.const_info
                fgxda__ldm = tuple(dtype_to_array_type(t) for t in
                    efet__fpy.data.types)
                vzx__igghg = bodo.DataFrameType(fgxda__ldm, ary.index,
                    ichj__rpr)
            elif isinstance(efet__fpy, SeriesType):
                gsbq__wicue, ichj__rpr = efet__fpy.const_info
                fgxda__ldm = tuple(dtype_to_array_type(efet__fpy.dtype) for
                    sth__cgkag in range(gsbq__wicue))
                vzx__igghg = bodo.DataFrameType(fgxda__ldm, ary.index,
                    ichj__rpr)
            else:
                umype__zln = get_udf_out_arr_type(efet__fpy, ylzzs__dlfuc)
                vzx__igghg = SeriesType(umype__zln.dtype, umype__zln, ary.
                    index, ary.name_typ)
        else:
            vzx__igghg = efet__fpy
        return signature(vzx__igghg, (func,)).replace(pysig=pysig)

    @bound_function('series.map', no_unliteral=True)
    def resolve_map(self, ary, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws['arg']
        kws.pop('arg', None)
        na_action = args[1] if len(args) > 1 else kws.pop('na_action',
            types.none)
        lmhv__hdmr = dict(na_action=na_action)
        oyk__ehaq = dict(na_action=None)
        check_unsupported_args('Series.map', lmhv__hdmr, oyk__ehaq,
            package_name='pandas', module_name='Series')

        def map_stub(arg, na_action=None):
            pass
        pysig = numba.core.utils.pysignature(map_stub)
        return self._resolve_map_func(ary, func, pysig, 'map')

    @bound_function('series.apply', no_unliteral=True)
    def resolve_apply(self, ary, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws['func']
        kws.pop('func', None)
        bvbba__uhgea = args[1] if len(args) > 1 else kws.pop('convert_dtype',
            types.literal(True))
        f_args = args[2] if len(args) > 2 else kws.pop('args', None)
        lmhv__hdmr = dict(convert_dtype=bvbba__uhgea)
        kajxj__quf = dict(convert_dtype=True)
        check_unsupported_args('Series.apply', lmhv__hdmr, kajxj__quf,
            package_name='pandas', module_name='Series')
        erh__iep = ', '.join("{} = ''".format(viro__gts) for viro__gts in
            kws.keys())
        mlows__hrmo = (
            f'def apply_stub(func, convert_dtype=True, args=(), {erh__iep}):\n'
            )
        mlows__hrmo += '    pass\n'
        qkh__jtkh = {}
        exec(mlows__hrmo, {}, qkh__jtkh)
        iyw__qvgx = qkh__jtkh['apply_stub']
        pysig = numba.core.utils.pysignature(iyw__qvgx)
        return self._resolve_map_func(ary, func, pysig, 'apply', f_args, kws)

    def _resolve_combine_func(self, ary, args, kws):
        kwargs = dict(kws)
        other = args[0] if len(args) > 0 else types.unliteral(kwargs['other'])
        func = args[1] if len(args) > 1 else kwargs['func']
        fill_value = args[2] if len(args) > 2 else types.unliteral(kwargs.
            get('fill_value', types.none))

        def combine_stub(other, func, fill_value=None):
            pass
        pysig = numba.core.utils.pysignature(combine_stub)
        vbh__znxc = ary.dtype
        if vbh__znxc == types.NPDatetime('ns'):
            vbh__znxc = pd_timestamp_type
        tdq__bgxtr = other.dtype
        if tdq__bgxtr == types.NPDatetime('ns'):
            tdq__bgxtr = pd_timestamp_type
        efet__fpy = get_const_func_output_type(func, (vbh__znxc, tdq__bgxtr
            ), {}, self.context, numba.core.registry.cpu_target.target_context)
        sig = signature(SeriesType(efet__fpy, index=ary.index, name_typ=
            types.none), (other, func, fill_value))
        return sig.replace(pysig=pysig)

    @bound_function('series.combine', no_unliteral=True)
    def resolve_combine(self, ary, args, kws):
        return self._resolve_combine_func(ary, args, kws)

    @bound_function('series.pipe', no_unliteral=True)
    def resolve_pipe(self, ary, args, kws):
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, ary,
            args, kws, 'Series')

    def generic_resolve(self, S, attr):
        from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
        if self._is_existing_attr(attr):
            return
        if isinstance(S.index, HeterogeneousIndexType
            ) and is_overload_constant_tuple(S.index.data):
            sfml__hwiiw = get_overload_const_tuple(S.index.data)
            if attr in sfml__hwiiw:
                bkri__reyld = sfml__hwiiw.index(attr)
                return S.data[bkri__reyld]


series_binary_ops = tuple(op for op in numba.core.typing.npydecl.
    NumpyRulesArrayOperator._op_map.keys() if op not in (operator.lshift,
    operator.rshift))
series_inplace_binary_ops = tuple(op for op in numba.core.typing.npydecl.
    NumpyRulesInplaceArrayOperator._op_map.keys() if op not in (operator.
    ilshift, operator.irshift, operator.itruediv))
inplace_binop_to_imm = {operator.iadd: operator.add, operator.isub:
    operator.sub, operator.imul: operator.mul, operator.ifloordiv: operator
    .floordiv, operator.imod: operator.mod, operator.ipow: operator.pow,
    operator.iand: operator.and_, operator.ior: operator.or_, operator.ixor:
    operator.xor}
series_unary_ops = operator.neg, operator.invert, operator.pos
str2str_methods = ('capitalize', 'lower', 'lstrip', 'rstrip', 'strip',
    'swapcase', 'title', 'upper')
str2bool_methods = ('isalnum', 'isalpha', 'isdigit', 'isspace', 'islower',
    'isupper', 'istitle', 'isnumeric', 'isdecimal')


@overload(pd.Series, no_unliteral=True)
def pd_series_overload(data=None, index=None, dtype=None, name=None, copy=
    False, fastpath=False):
    if not is_overload_false(fastpath):
        raise BodoError("pd.Series(): 'fastpath' argument not supported.")
    cku__ael = is_overload_none(data)
    iivt__rodrq = is_overload_none(index)
    rgf__pomj = is_overload_none(dtype)
    if cku__ael and iivt__rodrq and rgf__pomj:
        raise BodoError(
            'pd.Series() requires at least 1 of data, index, and dtype to not be none'
            )
    if is_series_type(data) and not iivt__rodrq:
        raise BodoError(
            'pd.Series() does not support index value when input data is a Series'
            )
    if isinstance(data, types.DictType):
        raise_bodo_error(
            'pd.Series(): When intializing series with a dictionary, it is required that the dict has constant keys'
            )
    if is_heterogeneous_tuple_type(data) and is_overload_none(dtype):

        def impl_heter(data=None, index=None, dtype=None, name=None, copy=
            False, fastpath=False):
            wkqb__qksh = bodo.utils.conversion.extract_index_if_none(data,
                index)
            uwz__dnogf = bodo.utils.conversion.to_tuple(data)
            return bodo.hiframes.pd_series_ext.init_series(uwz__dnogf, bodo
                .utils.conversion.convert_to_index(wkqb__qksh), name)
        return impl_heter
    if cku__ael:
        if rgf__pomj:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                xjcs__jmr = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                wkqb__qksh = bodo.utils.conversion.extract_index_if_none(data,
                    index)
                numba.parfors.parfor.init_prange()
                nwp__yqpx = len(wkqb__qksh)
                uwz__dnogf = np.empty(nwp__yqpx, np.float64)
                for jsec__uhl in numba.parfors.parfor.internal_prange(nwp__yqpx
                    ):
                    bodo.libs.array_kernels.setna(uwz__dnogf, jsec__uhl)
                return bodo.hiframes.pd_series_ext.init_series(uwz__dnogf,
                    bodo.utils.conversion.convert_to_index(wkqb__qksh),
                    xjcs__jmr)
            return impl
        if bodo.utils.conversion._is_str_dtype(dtype):
            gluq__iuqu = bodo.string_array_type
        else:
            hbm__oxq = bodo.utils.typing.parse_dtype(dtype, 'pandas.Series')
            if isinstance(hbm__oxq, bodo.libs.int_arr_ext.IntDtype):
                gluq__iuqu = bodo.IntegerArrayType(hbm__oxq.dtype)
            elif hbm__oxq == bodo.libs.bool_arr_ext.boolean_dtype:
                gluq__iuqu = bodo.boolean_array
            elif isinstance(hbm__oxq, types.Number) or hbm__oxq in [bodo.
                datetime64ns, bodo.timedelta64ns]:
                gluq__iuqu = types.Array(hbm__oxq, 1, 'C')
            else:
                raise BodoError(
                    'pd.Series with dtype: {dtype} not currently supported')
        if iivt__rodrq:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                xjcs__jmr = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                wkqb__qksh = bodo.hiframes.pd_index_ext.init_range_index(0,
                    0, 1, None)
                numba.parfors.parfor.init_prange()
                nwp__yqpx = len(wkqb__qksh)
                uwz__dnogf = bodo.utils.utils.alloc_type(nwp__yqpx,
                    gluq__iuqu, (-1,))
                return bodo.hiframes.pd_series_ext.init_series(uwz__dnogf,
                    wkqb__qksh, xjcs__jmr)
            return impl
        else:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                xjcs__jmr = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                wkqb__qksh = bodo.utils.conversion.extract_index_if_none(data,
                    index)
                numba.parfors.parfor.init_prange()
                nwp__yqpx = len(wkqb__qksh)
                uwz__dnogf = bodo.utils.utils.alloc_type(nwp__yqpx,
                    gluq__iuqu, (-1,))
                for jsec__uhl in numba.parfors.parfor.internal_prange(nwp__yqpx
                    ):
                    bodo.libs.array_kernels.setna(uwz__dnogf, jsec__uhl)
                return bodo.hiframes.pd_series_ext.init_series(uwz__dnogf,
                    bodo.utils.conversion.convert_to_index(wkqb__qksh),
                    xjcs__jmr)
            return impl

    def impl(data=None, index=None, dtype=None, name=None, copy=False,
        fastpath=False):
        xjcs__jmr = bodo.utils.conversion.extract_name_if_none(data, name)
        wkqb__qksh = bodo.utils.conversion.extract_index_if_none(data, index)
        poxm__tct = bodo.utils.conversion.coerce_to_array(data, True,
            scalar_to_arr_len=len(wkqb__qksh))
        nxg__wof = bodo.utils.conversion.fix_arr_dtype(poxm__tct, dtype,
            None, False)
        return bodo.hiframes.pd_series_ext.init_series(nxg__wof, bodo.utils
            .conversion.convert_to_index(wkqb__qksh), xjcs__jmr)
    return impl


@overload_method(SeriesType, 'to_csv', no_unliteral=True)
def to_csv_overload(series, path_or_buf=None, sep=',', na_rep='',
    float_format=None, columns=None, header=True, index=True, index_label=
    None, mode='w', encoding=None, compression='infer', quoting=None,
    quotechar='"', line_terminator=None, chunksize=None, date_format=None,
    doublequote=True, escapechar=None, decimal='.', errors='strict',
    _is_parallel=False):
    if not (is_overload_none(path_or_buf) or is_overload_constant_str(
        path_or_buf) or path_or_buf == string_type):
        raise BodoError(
            "Series.to_csv(): 'path_or_buf' argument should be None or string")
    if is_overload_none(path_or_buf):

        def _impl(series, path_or_buf=None, sep=',', na_rep='',
            float_format=None, columns=None, header=True, index=True,
            index_label=None, mode='w', encoding=None, compression='infer',
            quoting=None, quotechar='"', line_terminator=None, chunksize=
            None, date_format=None, doublequote=True, escapechar=None,
            decimal='.', errors='strict', _is_parallel=False):
            with numba.objmode(D='unicode_type'):
                D = series.to_csv(None, sep, na_rep, float_format, columns,
                    header, index, index_label, mode, encoding, compression,
                    quoting, quotechar, line_terminator, chunksize,
                    date_format, doublequote, escapechar, decimal, errors)
            return D
        return _impl

    def _impl(series, path_or_buf=None, sep=',', na_rep='', float_format=
        None, columns=None, header=True, index=True, index_label=None, mode
        ='w', encoding=None, compression='infer', quoting=None, quotechar=
        '"', line_terminator=None, chunksize=None, date_format=None,
        doublequote=True, escapechar=None, decimal='.', errors='strict',
        _is_parallel=False):
        if _is_parallel:
            header &= (bodo.libs.distributed_api.get_rank() == 0
                ) | _csv_output_is_dir(unicode_to_utf8(path_or_buf))
        with numba.objmode(D='unicode_type'):
            D = series.to_csv(None, sep, na_rep, float_format, columns,
                header, index, index_label, mode, encoding, compression,
                quoting, quotechar, line_terminator, chunksize, date_format,
                doublequote, escapechar, decimal, errors)
        bodo.io.fs_io.csv_write(path_or_buf, D, _is_parallel)
    return _impl


@lower_constant(SeriesType)
def lower_constant_series(context, builder, series_type, pyval):
    data_val = context.get_constant_generic(builder, series_type.data,
        pyval.values)
    index_val = context.get_constant_generic(builder, series_type.index,
        pyval.index)
    name_val = context.get_constant_generic(builder, series_type.name_typ,
        pyval.name)
    fmtk__tqzdj = lir.Constant.literal_struct([data_val, index_val, name_val])
    fmtk__tqzdj = cgutils.global_constant(builder, '.const.payload',
        fmtk__tqzdj).bitcast(cgutils.voidptr_t)
    havt__vqnd = context.get_constant(types.int64, -1)
    jehx__sqg = context.get_constant_null(types.voidptr)
    glgiq__qvwrc = lir.Constant.literal_struct([havt__vqnd, jehx__sqg,
        jehx__sqg, fmtk__tqzdj, havt__vqnd])
    glgiq__qvwrc = cgutils.global_constant(builder, '.const.meminfo',
        glgiq__qvwrc).bitcast(cgutils.voidptr_t)
    pnq__gghxv = lir.Constant.literal_struct([glgiq__qvwrc, jehx__sqg])
    return pnq__gghxv


series_unsupported_attrs = {'axes', 'array', 'flags', 'at', 'is_unique',
    'sparse', 'attrs'}
series_unsupported_methods = ('set_flags', 'convert_dtypes', 'bool',
    'to_period', 'to_timestamp', '__array__', 'get', 'at', '__iter__',
    'items', 'iteritems', 'pop', 'item', 'xs', 'combine_first', 'agg',
    'aggregate', 'transform', 'expanding', 'ewm', 'clip', 'factorize',
    'mode', 'rank', 'align', 'drop', 'droplevel', 'duplicated', 'reindex',
    'reindex_like', 'rename_axis', 'sample', 'set_axis', 'truncate',
    'add_prefix', 'add_suffix', 'filter', 'interpolate', 'argmin', 'argmax',
    'reorder_levels', 'swaplevel', 'unstack', 'searchsorted', 'ravel',
    'squeeze', 'view', 'compare', 'update', 'asfreq', 'asof',
    'first_valid_index', 'last_valid_index', 'resample', 'tz_convert',
    'tz_localize', 'at_time', 'between_time', 'tshift', 'slice_shift',
    'plot', 'hist', 'to_pickle', 'to_excel', 'to_xarray', 'to_hdf',
    'to_sql', 'to_json', 'to_string', 'to_clipboard', 'to_latex', 'to_markdown'
    )


def _install_series_unsupported():
    for isj__kwf in series_unsupported_attrs:
        yfd__eii = 'Series.' + isj__kwf
        overload_attribute(SeriesType, isj__kwf)(create_unsupported_overload
            (yfd__eii))
    for fname in series_unsupported_methods:
        yfd__eii = 'Series.' + fname
        overload_method(SeriesType, fname, no_unliteral=True)(
            create_unsupported_overload(yfd__eii))


_install_series_unsupported()
heter_series_unsupported_attrs = {'axes', 'array', 'dtype', 'nbytes',
    'memory_usage', 'hasnans', 'dtypes', 'flags', 'at', 'is_unique',
    'is_monotonic', 'is_monotonic_increasing', 'is_monotonic_decreasing',
    'dt', 'str', 'cat', 'sparse', 'attrs'}
heter_series_unsupported_methods = {'set_flags', 'astype', 'convert_dtypes',
    'infer_objects', 'copy', 'bool', 'to_numpy', 'to_period',
    'to_timestamp', 'to_list', 'tolist', '__array__', 'get', 'at', 'iat',
    'iloc', 'loc', '__iter__', 'items', 'iteritems', 'keys', 'pop', 'item',
    'xs', 'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'pow',
    'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv', 'rfloordiv', 'rmod', 'rpow',
    'combine', 'combine_first', 'round', 'lt', 'gt', 'le', 'ge', 'ne', 'eq',
    'product', 'dot', 'apply', 'agg', 'aggregate', 'transform', 'map',
    'groupby', 'rolling', 'expanding', 'ewm', 'pipe', 'abs', 'all', 'any',
    'autocorr', 'between', 'clip', 'corr', 'count', 'cov', 'cummax',
    'cummin', 'cumprod', 'cumsum', 'describe', 'diff', 'factorize', 'kurt',
    'mad', 'max', 'mean', 'median', 'min', 'mode', 'nlargest', 'nsmallest',
    'pct_change', 'prod', 'quantile', 'rank', 'sem', 'skew', 'std', 'sum',
    'var', 'kurtosis', 'unique', 'nunique', 'value_counts', 'align', 'drop',
    'droplevel', 'drop_duplicates', 'duplicated', 'equals', 'first', 'head',
    'idxmax', 'idxmin', 'isin', 'last', 'reindex', 'reindex_like', 'rename',
    'rename_axis', 'reset_index', 'sample', 'set_axis', 'take', 'tail',
    'truncate', 'where', 'mask', 'add_prefix', 'add_suffix', 'filter',
    'backfill', 'bfill', 'dropna', 'ffill', 'fillna', 'interpolate', 'isna',
    'isnull', 'notna', 'notnull', 'pad', 'replace', 'argsort', 'argmin',
    'argmax', 'reorder_levels', 'sort_values', 'sort_index', 'swaplevel',
    'unstack', 'explode', 'searchsorted', 'ravel', 'repeat', 'squeeze',
    'view', 'append', 'compare', 'update', 'asfreq', 'asof', 'shift',
    'first_valid_index', 'last_valid_index', 'resample', 'tz_convert',
    'tz_localize', 'at_time', 'between_time', 'tshift', 'slice_shift',
    'plot', 'hist', 'to_pickle', 'to_csv', 'to_dict', 'to_excel',
    'to_frame', 'to_xarray', 'to_hdf', 'to_sql', 'to_json', 'to_string',
    'to_clipboard', 'to_latex', 'to_markdown'}


def _install_heter_series_unsupported():
    for isj__kwf in heter_series_unsupported_attrs:
        yfd__eii = 'HeterogeneousSeries.' + isj__kwf
        overload_attribute(HeterogeneousSeriesType, isj__kwf)(
            create_unsupported_overload(yfd__eii))
    for fname in heter_series_unsupported_methods:
        yfd__eii = 'HeterogeneousSeries.' + fname
        overload_method(HeterogeneousSeriesType, fname, no_unliteral=True)(
            create_unsupported_overload(yfd__eii))


_install_heter_series_unsupported()
