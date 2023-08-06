"""Tools for handling bodo arrays, e.g. passing to C/C++ code
"""
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import signature
from numba.cpython.listobj import ListInstance
from numba.extending import intrinsic, models, register_model
from numba.np.arrayobj import _getitem_array_single_int
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, get_categories_int_type
from bodo.libs import array_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, define_array_item_dtor, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType, int128_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType, _get_map_arr_data_type, init_map_arr_codegen
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, char_arr_type, null_bitmap_arr_type, offset_arr_type, string_array_type
from bodo.libs.struct_arr_ext import StructArrayPayloadType, StructArrayType, StructType, _get_struct_arr_payload, define_struct_arr_dtor
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, MetaType
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, numba_to_c_type
ll.add_symbol('list_string_array_to_info', array_ext.list_string_array_to_info)
ll.add_symbol('nested_array_to_info', array_ext.nested_array_to_info)
ll.add_symbol('string_array_to_info', array_ext.string_array_to_info)
ll.add_symbol('numpy_array_to_info', array_ext.numpy_array_to_info)
ll.add_symbol('categorical_array_to_info', array_ext.categorical_array_to_info)
ll.add_symbol('nullable_array_to_info', array_ext.nullable_array_to_info)
ll.add_symbol('interval_array_to_info', array_ext.interval_array_to_info)
ll.add_symbol('decimal_array_to_info', array_ext.decimal_array_to_info)
ll.add_symbol('info_to_nested_array', array_ext.info_to_nested_array)
ll.add_symbol('info_to_list_string_array', array_ext.info_to_list_string_array)
ll.add_symbol('info_to_string_array', array_ext.info_to_string_array)
ll.add_symbol('info_to_numpy_array', array_ext.info_to_numpy_array)
ll.add_symbol('info_to_nullable_array', array_ext.info_to_nullable_array)
ll.add_symbol('info_to_interval_array', array_ext.info_to_interval_array)
ll.add_symbol('alloc_numpy', array_ext.alloc_numpy)
ll.add_symbol('alloc_string_array', array_ext.alloc_string_array)
ll.add_symbol('arr_info_list_to_table', array_ext.arr_info_list_to_table)
ll.add_symbol('info_from_table', array_ext.info_from_table)
ll.add_symbol('delete_info_decref_array', array_ext.delete_info_decref_array)
ll.add_symbol('delete_table_decref_arrays', array_ext.
    delete_table_decref_arrays)
ll.add_symbol('delete_table', array_ext.delete_table)
ll.add_symbol('shuffle_table', array_ext.shuffle_table)
ll.add_symbol('get_shuffle_info', array_ext.get_shuffle_info)
ll.add_symbol('delete_shuffle_info', array_ext.delete_shuffle_info)
ll.add_symbol('reverse_shuffle_table', array_ext.reverse_shuffle_table)
ll.add_symbol('hash_join_table', array_ext.hash_join_table)
ll.add_symbol('drop_duplicates_table', array_ext.drop_duplicates_table)
ll.add_symbol('sort_values_table', array_ext.sort_values_table)
ll.add_symbol('sample_table', array_ext.sample_table)
ll.add_symbol('shuffle_renormalization', array_ext.shuffle_renormalization)
ll.add_symbol('shuffle_renormalization_group', array_ext.
    shuffle_renormalization_group)
ll.add_symbol('groupby_and_aggregate', array_ext.groupby_and_aggregate)
ll.add_symbol('pivot_groupby_and_aggregate', array_ext.
    pivot_groupby_and_aggregate)
ll.add_symbol('get_groupby_labels', array_ext.get_groupby_labels)
ll.add_symbol('array_isin', array_ext.array_isin)
ll.add_symbol('get_search_regex', array_ext.get_search_regex)
ll.add_symbol('compute_node_partition_by_hash', array_ext.
    compute_node_partition_by_hash)
ll.add_symbol('array_info_getitem', array_ext.array_info_getitem)


class ArrayInfoType(types.Type):

    def __init__(self):
        super(ArrayInfoType, self).__init__(name='ArrayInfoType()')


array_info_type = ArrayInfoType()
register_model(ArrayInfoType)(models.OpaqueModel)


class TableTypeCPP(types.Type):

    def __init__(self):
        super(TableTypeCPP, self).__init__(name='TableTypeCPP()')


table_type = TableTypeCPP()
register_model(TableTypeCPP)(models.OpaqueModel)


@intrinsic
def array_to_info(typingctx, arr_type_t=None):
    return array_info_type(arr_type_t), array_to_info_codegen


def array_to_info_codegen(context, builder, sig, args):
    in_arr, = args
    arr_type = sig.args[0]
    if isinstance(arr_type, TupleArrayType):
        rxuh__wepbi = context.make_helper(builder, arr_type, in_arr)
        in_arr = rxuh__wepbi.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        xdxb__mckw = context.make_helper(builder, arr_type, in_arr)
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='list_string_array_to_info')
        return builder.call(qcksh__idgzh, [xdxb__mckw.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                pdic__stib = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for fsl__uxbe in arr_typ.data:
                    pdic__stib += get_types(fsl__uxbe)
                return pdic__stib
            elif isinstance(arr_typ, (types.Array, IntegerArrayType)
                ) or arr_typ == boolean_array:
                return get_types(arr_typ.dtype)
            elif arr_typ == string_array_type:
                return [CTypeEnum.STRING.value]
            elif arr_typ == binary_array_type:
                return [CTypeEnum.BINARY.value]
            elif isinstance(arr_typ, DecimalArrayType):
                return [CTypeEnum.Decimal.value, arr_typ.precision, arr_typ
                    .scale]
            else:
                return [numba_to_c_type(arr_typ)]

        def get_lengths(arr_typ, arr):
            offzx__sisnf = context.compile_internal(builder, lambda a: len(
                a), types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                drtg__brfi = context.make_helper(builder, arr_typ, value=arr)
                wedw__wwa = get_lengths(_get_map_arr_data_type(arr_typ),
                    drtg__brfi.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                crq__nsmr = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                wedw__wwa = get_lengths(arr_typ.dtype, crq__nsmr.data)
                wedw__wwa = cgutils.pack_array(builder, [crq__nsmr.n_arrays
                    ] + [builder.extract_value(wedw__wwa, tjlf__koda) for
                    tjlf__koda in range(wedw__wwa.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                crq__nsmr = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                wedw__wwa = []
                for tjlf__koda, fsl__uxbe in enumerate(arr_typ.data):
                    jel__cqoev = get_lengths(fsl__uxbe, builder.
                        extract_value(crq__nsmr.data, tjlf__koda))
                    wedw__wwa += [builder.extract_value(jel__cqoev,
                        ffibr__zbc) for ffibr__zbc in range(jel__cqoev.type
                        .count)]
                wedw__wwa = cgutils.pack_array(builder, [offzx__sisnf,
                    context.get_constant(types.int64, -1)] + wedw__wwa)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                wedw__wwa = cgutils.pack_array(builder, [offzx__sisnf])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray')
            return wedw__wwa

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                drtg__brfi = context.make_helper(builder, arr_typ, value=arr)
                ijcc__ghsu = get_buffers(_get_map_arr_data_type(arr_typ),
                    drtg__brfi.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                crq__nsmr = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                nwzgm__yrf = get_buffers(arr_typ.dtype, crq__nsmr.data)
                yduwt__kcgx = context.make_array(types.Array(offset_type, 1,
                    'C'))(context, builder, crq__nsmr.offsets)
                qwhbr__ywt = builder.bitcast(yduwt__kcgx.data, lir.IntType(
                    8).as_pointer())
                tpylh__whtra = context.make_array(types.Array(types.uint8, 
                    1, 'C'))(context, builder, crq__nsmr.null_bitmap)
                figqv__hdluf = builder.bitcast(tpylh__whtra.data, lir.
                    IntType(8).as_pointer())
                ijcc__ghsu = cgutils.pack_array(builder, [qwhbr__ywt,
                    figqv__hdluf] + [builder.extract_value(nwzgm__yrf,
                    tjlf__koda) for tjlf__koda in range(nwzgm__yrf.type.count)]
                    )
            elif isinstance(arr_typ, StructArrayType):
                crq__nsmr = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                nwzgm__yrf = []
                for tjlf__koda, fsl__uxbe in enumerate(arr_typ.data):
                    rvivb__nvvbk = get_buffers(fsl__uxbe, builder.
                        extract_value(crq__nsmr.data, tjlf__koda))
                    nwzgm__yrf += [builder.extract_value(rvivb__nvvbk,
                        ffibr__zbc) for ffibr__zbc in range(rvivb__nvvbk.
                        type.count)]
                tpylh__whtra = context.make_array(types.Array(types.uint8, 
                    1, 'C'))(context, builder, crq__nsmr.null_bitmap)
                figqv__hdluf = builder.bitcast(tpylh__whtra.data, lir.
                    IntType(8).as_pointer())
                ijcc__ghsu = cgutils.pack_array(builder, [figqv__hdluf] +
                    nwzgm__yrf)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                gryk__tmvv = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    gryk__tmvv = int128_type
                elif arr_typ == datetime_date_array_type:
                    gryk__tmvv = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                btyd__wbc = context.make_array(types.Array(gryk__tmvv, 1, 'C')
                    )(context, builder, arr.data)
                tpylh__whtra = context.make_array(types.Array(types.uint8, 
                    1, 'C'))(context, builder, arr.null_bitmap)
                dfjzi__hnpda = builder.bitcast(btyd__wbc.data, lir.IntType(
                    8).as_pointer())
                figqv__hdluf = builder.bitcast(tpylh__whtra.data, lir.
                    IntType(8).as_pointer())
                ijcc__ghsu = cgutils.pack_array(builder, [figqv__hdluf,
                    dfjzi__hnpda])
            elif arr_typ in (string_array_type, binary_array_type):
                crq__nsmr = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                hpt__deah = context.make_helper(builder, offset_arr_type,
                    crq__nsmr.offsets).data
                zezn__eeq = context.make_helper(builder, char_arr_type,
                    crq__nsmr.data).data
                bigwg__qwad = context.make_helper(builder,
                    null_bitmap_arr_type, crq__nsmr.null_bitmap).data
                ijcc__ghsu = cgutils.pack_array(builder, [builder.bitcast(
                    hpt__deah, lir.IntType(8).as_pointer()), builder.
                    bitcast(bigwg__qwad, lir.IntType(8).as_pointer()),
                    builder.bitcast(zezn__eeq, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                dfjzi__hnpda = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                vtlj__xrpjb = lir.Constant(lir.IntType(8).as_pointer(), None)
                ijcc__ghsu = cgutils.pack_array(builder, [vtlj__xrpjb,
                    dfjzi__hnpda])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return ijcc__ghsu

        def get_field_names(arr_typ):
            gyz__gdwd = []
            if isinstance(arr_typ, StructArrayType):
                for dgzl__olv, mgv__vpl in zip(arr_typ.dtype.names, arr_typ
                    .data):
                    gyz__gdwd.append(dgzl__olv)
                    gyz__gdwd += get_field_names(mgv__vpl)
            elif isinstance(arr_typ, ArrayItemArrayType):
                gyz__gdwd += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                gyz__gdwd += get_field_names(_get_map_arr_data_type(arr_typ))
            return gyz__gdwd
        pdic__stib = get_types(arr_type)
        ayt__juso = cgutils.pack_array(builder, [context.get_constant(types
            .int32, t) for t in pdic__stib])
        dhrq__zgz = cgutils.alloca_once_value(builder, ayt__juso)
        wedw__wwa = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, wedw__wwa)
        ijcc__ghsu = get_buffers(arr_type, in_arr)
        gvmt__wdj = cgutils.alloca_once_value(builder, ijcc__ghsu)
        gyz__gdwd = get_field_names(arr_type)
        if len(gyz__gdwd) == 0:
            gyz__gdwd = ['irrelevant']
        gchm__mycbc = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in gyz__gdwd])
        obzo__riraz = cgutils.alloca_once_value(builder, gchm__mycbc)
        if isinstance(arr_type, MapArrayType):
            asf__tjfv = _get_map_arr_data_type(arr_type)
            piy__ayhcj = context.make_helper(builder, arr_type, value=in_arr)
            vdlh__esp = piy__ayhcj.data
        else:
            asf__tjfv = arr_type
            vdlh__esp = in_arr
        rszaf__mwnhd = context.make_helper(builder, asf__tjfv, vdlh__esp)
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='nested_array_to_info')
        vfsvc__lyuch = builder.call(qcksh__idgzh, [builder.bitcast(
            dhrq__zgz, lir.IntType(32).as_pointer()), builder.bitcast(
            gvmt__wdj, lir.IntType(8).as_pointer().as_pointer()), builder.
            bitcast(lengths_ptr, lir.IntType(64).as_pointer()), builder.
            bitcast(obzo__riraz, lir.IntType(8).as_pointer()), rszaf__mwnhd
            .meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vfsvc__lyuch
    if arr_type in (string_array_type, binary_array_type):
        nrwog__mlu = context.make_helper(builder, arr_type, in_arr)
        wdpyj__xoxlp = ArrayItemArrayType(char_arr_type)
        xdxb__mckw = context.make_helper(builder, wdpyj__xoxlp, nrwog__mlu.data
            )
        crq__nsmr = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        hpt__deah = context.make_helper(builder, offset_arr_type, crq__nsmr
            .offsets).data
        zezn__eeq = context.make_helper(builder, char_arr_type, crq__nsmr.data
            ).data
        bigwg__qwad = context.make_helper(builder, null_bitmap_arr_type,
            crq__nsmr.null_bitmap).data
        ttmfe__qrclg = builder.zext(builder.load(builder.gep(hpt__deah, [
            crq__nsmr.n_arrays])), lir.IntType(64))
        wge__efs = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='string_array_to_info')
        return builder.call(qcksh__idgzh, [crq__nsmr.n_arrays, ttmfe__qrclg,
            zezn__eeq, hpt__deah, bigwg__qwad, xdxb__mckw.meminfo, wge__efs])
    wvla__azh = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        umlo__kykkj = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        lwgt__iabzn = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(lwgt__iabzn, 1, 'C')
        wvla__azh = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        offzx__sisnf = builder.extract_value(arr.shape, 0)
        nyf__cjzh = arr_type.dtype
        gboc__yypeg = numba_to_c_type(nyf__cjzh)
        wdgb__dhsmm = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), gboc__yypeg))
        if wvla__azh:
            exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
                exame__dgc, name='categorical_array_to_info')
            return builder.call(qcksh__idgzh, [offzx__sisnf, builder.
                bitcast(arr.data, lir.IntType(8).as_pointer()), builder.
                load(wdgb__dhsmm), umlo__kykkj, arr.meminfo])
        else:
            exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
                exame__dgc, name='numpy_array_to_info')
            return builder.call(qcksh__idgzh, [offzx__sisnf, builder.
                bitcast(arr.data, lir.IntType(8).as_pointer()), builder.
                load(wdgb__dhsmm), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        nyf__cjzh = arr_type.dtype
        gryk__tmvv = nyf__cjzh
        if isinstance(arr_type, DecimalArrayType):
            gryk__tmvv = int128_type
        if arr_type == datetime_date_array_type:
            gryk__tmvv = types.int64
        btyd__wbc = context.make_array(types.Array(gryk__tmvv, 1, 'C'))(context
            , builder, arr.data)
        offzx__sisnf = builder.extract_value(btyd__wbc.shape, 0)
        jxey__cixdc = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        gboc__yypeg = numba_to_c_type(nyf__cjzh)
        wdgb__dhsmm = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), gboc__yypeg))
        if isinstance(arr_type, DecimalArrayType):
            exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
                exame__dgc, name='decimal_array_to_info')
            return builder.call(qcksh__idgzh, [offzx__sisnf, builder.
                bitcast(btyd__wbc.data, lir.IntType(8).as_pointer()),
                builder.load(wdgb__dhsmm), builder.bitcast(jxey__cixdc.data,
                lir.IntType(8).as_pointer()), btyd__wbc.meminfo,
                jxey__cixdc.meminfo, context.get_constant(types.int32,
                arr_type.precision), context.get_constant(types.int32,
                arr_type.scale)])
        else:
            exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
                exame__dgc, name='nullable_array_to_info')
            return builder.call(qcksh__idgzh, [offzx__sisnf, builder.
                bitcast(btyd__wbc.data, lir.IntType(8).as_pointer()),
                builder.load(wdgb__dhsmm), builder.bitcast(jxey__cixdc.data,
                lir.IntType(8).as_pointer()), btyd__wbc.meminfo,
                jxey__cixdc.meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        wlsie__pwk = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        rqxk__hon = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        offzx__sisnf = builder.extract_value(wlsie__pwk.shape, 0)
        gboc__yypeg = numba_to_c_type(arr_type.arr_type.dtype)
        wdgb__dhsmm = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), gboc__yypeg))
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='interval_array_to_info')
        return builder.call(qcksh__idgzh, [offzx__sisnf, builder.bitcast(
            wlsie__pwk.data, lir.IntType(8).as_pointer()), builder.bitcast(
            rqxk__hon.data, lir.IntType(8).as_pointer()), builder.load(
            wdgb__dhsmm), wlsie__pwk.meminfo, rqxk__hon.meminfo])
    raise BodoError(f'array_to_info(): array type {arr_type} is not supported')


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    qlae__xnng = cgutils.alloca_once(builder, lir.IntType(64))
    dfjzi__hnpda = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    egrbb__wpy = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    exame__dgc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
        exame__dgc, name='info_to_numpy_array')
    builder.call(qcksh__idgzh, [in_info, qlae__xnng, dfjzi__hnpda, egrbb__wpy])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    opv__rnp = context.get_value_type(types.intp)
    dqmq__pcgw = cgutils.pack_array(builder, [builder.load(qlae__xnng)], ty
        =opv__rnp)
    qcyu__elohp = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    hqu__qpk = cgutils.pack_array(builder, [qcyu__elohp], ty=opv__rnp)
    zezn__eeq = builder.bitcast(builder.load(dfjzi__hnpda), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=zezn__eeq, shape=dqmq__pcgw,
        strides=hqu__qpk, itemsize=qcyu__elohp, meminfo=builder.load(
        egrbb__wpy))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    lgnq__ugb = context.make_helper(builder, arr_type)
    exame__dgc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
        exame__dgc, name='info_to_list_string_array')
    builder.call(qcksh__idgzh, [in_info, lgnq__ugb._get_ptr_by_name('meminfo')]
        )
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return lgnq__ugb._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    yfbkl__iehz = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        zuef__axc = lengths_pos
        zco__eektr = infos_pos
        jao__apyt, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        zpv__wzxw = ArrayItemArrayPayloadType(arr_typ)
        tbew__kyf = context.get_data_type(zpv__wzxw)
        mnyzo__lhmvg = context.get_abi_sizeof(tbew__kyf)
        gohew__qawr = define_array_item_dtor(context, builder, arr_typ,
            zpv__wzxw)
        btt__hgz = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, mnyzo__lhmvg), gohew__qawr)
        wucb__owfr = context.nrt.meminfo_data(builder, btt__hgz)
        zvtdt__oxh = builder.bitcast(wucb__owfr, tbew__kyf.as_pointer())
        crq__nsmr = cgutils.create_struct_proxy(zpv__wzxw)(context, builder)
        crq__nsmr.n_arrays = builder.extract_value(builder.load(lengths_ptr
            ), zuef__axc)
        crq__nsmr.data = jao__apyt
        qux__bxe = builder.load(array_infos_ptr)
        dpolw__tuij = builder.bitcast(builder.extract_value(qux__bxe,
            zco__eektr), yfbkl__iehz)
        crq__nsmr.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, dpolw__tuij)
        wunh__jfbry = builder.bitcast(builder.extract_value(qux__bxe, 
            zco__eektr + 1), yfbkl__iehz)
        crq__nsmr.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, wunh__jfbry)
        builder.store(crq__nsmr._getvalue(), zvtdt__oxh)
        xdxb__mckw = context.make_helper(builder, arr_typ)
        xdxb__mckw.meminfo = btt__hgz
        return xdxb__mckw._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        hqypf__xcw = []
        zco__eektr = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for xawdx__gzbga in arr_typ.data:
            jao__apyt, lengths_pos, infos_pos = nested_to_array(context,
                builder, xawdx__gzbga, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            hqypf__xcw.append(jao__apyt)
        zpv__wzxw = StructArrayPayloadType(arr_typ.data)
        tbew__kyf = context.get_value_type(zpv__wzxw)
        mnyzo__lhmvg = context.get_abi_sizeof(tbew__kyf)
        gohew__qawr = define_struct_arr_dtor(context, builder, arr_typ,
            zpv__wzxw)
        btt__hgz = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, mnyzo__lhmvg), gohew__qawr)
        wucb__owfr = context.nrt.meminfo_data(builder, btt__hgz)
        zvtdt__oxh = builder.bitcast(wucb__owfr, tbew__kyf.as_pointer())
        crq__nsmr = cgutils.create_struct_proxy(zpv__wzxw)(context, builder)
        crq__nsmr.data = cgutils.pack_array(builder, hqypf__xcw
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, hqypf__xcw)
        qux__bxe = builder.load(array_infos_ptr)
        wunh__jfbry = builder.bitcast(builder.extract_value(qux__bxe,
            zco__eektr), yfbkl__iehz)
        crq__nsmr.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, wunh__jfbry)
        builder.store(crq__nsmr._getvalue(), zvtdt__oxh)
        wqb__qlx = context.make_helper(builder, arr_typ)
        wqb__qlx.meminfo = btt__hgz
        return wqb__qlx._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        qux__bxe = builder.load(array_infos_ptr)
        bswdf__kzd = builder.bitcast(builder.extract_value(qux__bxe,
            infos_pos), yfbkl__iehz)
        nrwog__mlu = context.make_helper(builder, arr_typ)
        wdpyj__xoxlp = ArrayItemArrayType(char_arr_type)
        xdxb__mckw = context.make_helper(builder, wdpyj__xoxlp)
        exame__dgc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='info_to_string_array')
        builder.call(qcksh__idgzh, [bswdf__kzd, xdxb__mckw._get_ptr_by_name
            ('meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        nrwog__mlu.data = xdxb__mckw._getvalue()
        return nrwog__mlu._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        qux__bxe = builder.load(array_infos_ptr)
        odpa__kix = builder.bitcast(builder.extract_value(qux__bxe, 
            infos_pos + 1), yfbkl__iehz)
        return _lower_info_to_array_numpy(arr_typ, context, builder, odpa__kix
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        gryk__tmvv = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            gryk__tmvv = int128_type
        elif arr_typ == datetime_date_array_type:
            gryk__tmvv = types.int64
        qux__bxe = builder.load(array_infos_ptr)
        wunh__jfbry = builder.bitcast(builder.extract_value(qux__bxe,
            infos_pos), yfbkl__iehz)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, wunh__jfbry)
        odpa__kix = builder.bitcast(builder.extract_value(qux__bxe, 
            infos_pos + 1), yfbkl__iehz)
        arr.data = _lower_info_to_array_numpy(types.Array(gryk__tmvv, 1,
            'C'), context, builder, odpa__kix)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


@intrinsic
def info_to_array(typingctx, info_type, array_type):
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    assert info_type == array_info_type

    def codegen(context, builder, sig, args):
        in_info, asek__vtd = args
        if isinstance(arr_type, ArrayItemArrayType
            ) and arr_type.dtype == string_array_type:
            return _lower_info_to_array_list_string_array(arr_type, context,
                builder, in_info)
        if isinstance(arr_type, (MapArrayType, ArrayItemArrayType,
            StructArrayType, TupleArrayType)):

            def get_num_arrays(arr_typ):
                if isinstance(arr_typ, ArrayItemArrayType):
                    return 1 + get_num_arrays(arr_typ.dtype)
                elif isinstance(arr_typ, StructArrayType):
                    return 1 + sum([get_num_arrays(xawdx__gzbga) for
                        xawdx__gzbga in arr_typ.data])
                else:
                    return 1

            def get_num_infos(arr_typ):
                if isinstance(arr_typ, ArrayItemArrayType):
                    return 2 + get_num_infos(arr_typ.dtype)
                elif isinstance(arr_typ, StructArrayType):
                    return 1 + sum([get_num_infos(xawdx__gzbga) for
                        xawdx__gzbga in arr_typ.data])
                elif arr_typ in (string_array_type, binary_array_type):
                    return 1
                else:
                    return 2
            if isinstance(arr_type, TupleArrayType):
                vxr__jitjq = StructArrayType(arr_type.data, ('dummy',) *
                    len(arr_type.data))
            elif isinstance(arr_type, MapArrayType):
                vxr__jitjq = _get_map_arr_data_type(arr_type)
            else:
                vxr__jitjq = arr_type
            caz__olhj = get_num_arrays(vxr__jitjq)
            wedw__wwa = cgutils.pack_array(builder, [lir.Constant(lir.
                IntType(64), 0) for asek__vtd in range(caz__olhj)])
            lengths_ptr = cgutils.alloca_once_value(builder, wedw__wwa)
            vtlj__xrpjb = lir.Constant(lir.IntType(8).as_pointer(), None)
            nmljg__jsrt = cgutils.pack_array(builder, [vtlj__xrpjb for
                asek__vtd in range(get_num_infos(vxr__jitjq))])
            array_infos_ptr = cgutils.alloca_once_value(builder, nmljg__jsrt)
            exame__dgc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
                as_pointer().as_pointer()])
            qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
                exame__dgc, name='info_to_nested_array')
            builder.call(qcksh__idgzh, [in_info, builder.bitcast(
                lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast
                (array_infos_ptr, lir.IntType(8).as_pointer().as_pointer())])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            arr, asek__vtd, asek__vtd = nested_to_array(context, builder,
                vxr__jitjq, lengths_ptr, array_infos_ptr, 0, 0)
            if isinstance(arr_type, TupleArrayType):
                rxuh__wepbi = context.make_helper(builder, arr_type)
                rxuh__wepbi.data = arr
                context.nrt.incref(builder, vxr__jitjq, arr)
                arr = rxuh__wepbi._getvalue()
            elif isinstance(arr_type, MapArrayType):
                sig = signature(arr_type, vxr__jitjq)
                arr = init_map_arr_codegen(context, builder, sig, (arr,))
            return arr
        if arr_type in (string_array_type, binary_array_type):
            nrwog__mlu = context.make_helper(builder, arr_type)
            wdpyj__xoxlp = ArrayItemArrayType(char_arr_type)
            xdxb__mckw = context.make_helper(builder, wdpyj__xoxlp)
            exame__dgc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
            qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
                exame__dgc, name='info_to_string_array')
            builder.call(qcksh__idgzh, [in_info, xdxb__mckw.
                _get_ptr_by_name('meminfo')])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            nrwog__mlu.data = xdxb__mckw._getvalue()
            return nrwog__mlu._getvalue()
        if isinstance(arr_type, CategoricalArrayType):
            out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            lwgt__iabzn = get_categories_int_type(arr_type.dtype)
            nnv__nvgn = types.Array(lwgt__iabzn, 1, 'C')
            out_arr.codes = _lower_info_to_array_numpy(nnv__nvgn, context,
                builder, in_info)
            if isinstance(array_type, types.TypeRef):
                assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
                is_ordered = arr_type.dtype.ordered
                cjdpa__nrqc = pd.CategoricalDtype(arr_type.dtype.categories,
                    is_ordered).categories.values
                new_cats_tup = MetaType(tuple(cjdpa__nrqc))
                int_type = arr_type.dtype.int_type
                xjdn__ldw = bodo.typeof(cjdpa__nrqc)
                ijxup__uto = context.get_constant_generic(builder,
                    xjdn__ldw, cjdpa__nrqc)
                nyf__cjzh = context.compile_internal(builder, lambda c_arr:
                    bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.
                    utils.conversion.index_from_array(c_arr), is_ordered,
                    int_type, new_cats_tup), arr_type.dtype(xjdn__ldw), [
                    ijxup__uto])
            else:
                nyf__cjzh = cgutils.create_struct_proxy(arr_type)(context,
                    builder, args[1]).dtype
                context.nrt.incref(builder, arr_type.dtype, nyf__cjzh)
            out_arr.dtype = nyf__cjzh
            return out_arr._getvalue()
        if isinstance(arr_type, types.Array):
            return _lower_info_to_array_numpy(arr_type, context, builder,
                in_info)
        if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
            ) or arr_type in (boolean_array, datetime_date_array_type):
            arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            gryk__tmvv = arr_type.dtype
            if isinstance(arr_type, DecimalArrayType):
                gryk__tmvv = int128_type
            elif arr_type == datetime_date_array_type:
                gryk__tmvv = types.int64
            hqvsk__hvv = types.Array(gryk__tmvv, 1, 'C')
            btyd__wbc = context.make_array(hqvsk__hvv)(context, builder)
            wsol__vuyq = types.Array(types.uint8, 1, 'C')
            npdzd__drfb = context.make_array(wsol__vuyq)(context, builder)
            qlae__xnng = cgutils.alloca_once(builder, lir.IntType(64))
            vrybf__tuviz = cgutils.alloca_once(builder, lir.IntType(64))
            dfjzi__hnpda = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            pvt__zsbd = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            egrbb__wpy = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            qdjeu__veoe = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            exame__dgc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64)
                .as_pointer(), lir.IntType(8).as_pointer().as_pointer(),
                lir.IntType(8).as_pointer().as_pointer(), lir.IntType(8).
                as_pointer().as_pointer(), lir.IntType(8).as_pointer().
                as_pointer()])
            qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
                exame__dgc, name='info_to_nullable_array')
            builder.call(qcksh__idgzh, [in_info, qlae__xnng, vrybf__tuviz,
                dfjzi__hnpda, pvt__zsbd, egrbb__wpy, qdjeu__veoe])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            opv__rnp = context.get_value_type(types.intp)
            dqmq__pcgw = cgutils.pack_array(builder, [builder.load(
                qlae__xnng)], ty=opv__rnp)
            qcyu__elohp = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(gryk__tmvv)))
            hqu__qpk = cgutils.pack_array(builder, [qcyu__elohp], ty=opv__rnp)
            zezn__eeq = builder.bitcast(builder.load(dfjzi__hnpda), context
                .get_data_type(gryk__tmvv).as_pointer())
            numba.np.arrayobj.populate_array(btyd__wbc, data=zezn__eeq,
                shape=dqmq__pcgw, strides=hqu__qpk, itemsize=qcyu__elohp,
                meminfo=builder.load(egrbb__wpy))
            arr.data = btyd__wbc._getvalue()
            dqmq__pcgw = cgutils.pack_array(builder, [builder.load(
                vrybf__tuviz)], ty=opv__rnp)
            qcyu__elohp = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(types.uint8)))
            hqu__qpk = cgutils.pack_array(builder, [qcyu__elohp], ty=opv__rnp)
            zezn__eeq = builder.bitcast(builder.load(pvt__zsbd), context.
                get_data_type(types.uint8).as_pointer())
            numba.np.arrayobj.populate_array(npdzd__drfb, data=zezn__eeq,
                shape=dqmq__pcgw, strides=hqu__qpk, itemsize=qcyu__elohp,
                meminfo=builder.load(qdjeu__veoe))
            arr.null_bitmap = npdzd__drfb._getvalue()
            return arr._getvalue()
        if isinstance(arr_type, IntervalArrayType):
            arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            wlsie__pwk = context.make_array(arr_type.arr_type)(context, builder
                )
            rqxk__hon = context.make_array(arr_type.arr_type)(context, builder)
            qlae__xnng = cgutils.alloca_once(builder, lir.IntType(64))
            oomdq__euzs = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            vunzv__igmau = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            hktm__ibfey = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            ynm__rdwia = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            exame__dgc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
                as_pointer().as_pointer(), lir.IntType(8).as_pointer().
                as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir
                .IntType(8).as_pointer().as_pointer()])
            qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
                exame__dgc, name='info_to_interval_array')
            builder.call(qcksh__idgzh, [in_info, qlae__xnng, oomdq__euzs,
                vunzv__igmau, hktm__ibfey, ynm__rdwia])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            opv__rnp = context.get_value_type(types.intp)
            dqmq__pcgw = cgutils.pack_array(builder, [builder.load(
                qlae__xnng)], ty=opv__rnp)
            qcyu__elohp = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
            hqu__qpk = cgutils.pack_array(builder, [qcyu__elohp], ty=opv__rnp)
            rwd__tayv = builder.bitcast(builder.load(oomdq__euzs), context.
                get_data_type(arr_type.arr_type.dtype).as_pointer())
            numba.np.arrayobj.populate_array(wlsie__pwk, data=rwd__tayv,
                shape=dqmq__pcgw, strides=hqu__qpk, itemsize=qcyu__elohp,
                meminfo=builder.load(hktm__ibfey))
            arr.left = wlsie__pwk._getvalue()
            eudt__wnky = builder.bitcast(builder.load(vunzv__igmau),
                context.get_data_type(arr_type.arr_type.dtype).as_pointer())
            numba.np.arrayobj.populate_array(rqxk__hon, data=eudt__wnky,
                shape=dqmq__pcgw, strides=hqu__qpk, itemsize=qcyu__elohp,
                meminfo=builder.load(ynm__rdwia))
            arr.right = rqxk__hon._getvalue()
            return arr._getvalue()
        raise BodoError(
            f'info_to_array(): array type {arr_type} is not supported')
    return arr_type(info_type, array_type), codegen


@intrinsic
def test_alloc_np(typingctx, len_typ, arr_type):
    array_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type

    def codegen(context, builder, sig, args):
        offzx__sisnf, asek__vtd = args
        gboc__yypeg = numba_to_c_type(array_type.dtype)
        wdgb__dhsmm = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), gboc__yypeg))
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='alloc_numpy')
        return builder.call(qcksh__idgzh, [offzx__sisnf, builder.load(
            wdgb__dhsmm)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        offzx__sisnf, kqxqw__xvrjd = args
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='alloc_string_array')
        return builder.call(qcksh__idgzh, [offzx__sisnf, kqxqw__xvrjd])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    fuqjd__flmfc, = args
    qctl__hftjm = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], fuqjd__flmfc)
    exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer().as_pointer(), lir.IntType(64)])
    qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
        exame__dgc, name='arr_info_list_to_table')
    return builder.call(qcksh__idgzh, [qctl__hftjm.data, qctl__hftjm.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='info_from_table')
        return builder.call(qcksh__idgzh, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    issmv__dnv = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        qqchd__ysh, zkh__nta, asek__vtd = args
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='info_from_table')
        llzwi__iixef = cgutils.create_struct_proxy(issmv__dnv)(context, builder
            )
        llzwi__iixef.parent = cgutils.get_null_value(llzwi__iixef.parent.type)
        xip__bvy = context.make_array(table_idx_arr_t)(context, builder,
            zkh__nta)
        abf__sfrg = context.get_constant(types.int64, -1)
        yig__jnzwz = context.get_constant(types.int64, 0)
        wfcg__kxp = cgutils.alloca_once_value(builder, yig__jnzwz)
        for t, fcsw__rnz in issmv__dnv.type_to_blk.items():
            yqse__oabt = context.get_constant(types.int64, len(issmv__dnv.
                block_to_arr_ind[fcsw__rnz]))
            asek__vtd, giem__mjt = ListInstance.allocate_ex(context,
                builder, types.List(t), yqse__oabt)
            giem__mjt.size = yqse__oabt
            zaz__vfs = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(issmv__dnv.block_to_arr_ind[
                fcsw__rnz], dtype=np.int64))
            gxln__dntlp = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, zaz__vfs)
            with cgutils.for_range(builder, yqse__oabt) as loop:
                tjlf__koda = loop.index
                zbf__mji = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    gxln__dntlp, tjlf__koda)
                ayyxz__wznjr = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, xip__bvy, zbf__mji)
                tvg__ryzg = builder.icmp_unsigned('!=', ayyxz__wznjr, abf__sfrg
                    )
                with builder.if_else(tvg__ryzg) as (then, orelse):
                    with then:
                        vpjlz__ulot = builder.call(qcksh__idgzh, [
                            qqchd__ysh, ayyxz__wznjr])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            vpjlz__ulot])
                        giem__mjt.inititem(tjlf__koda, arr, incref=False)
                        offzx__sisnf = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(offzx__sisnf, wfcg__kxp)
                    with orelse:
                        rvjt__wdex = context.get_constant_null(t)
                        giem__mjt.inititem(tjlf__koda, rvjt__wdex, incref=False
                            )
            setattr(llzwi__iixef, f'block_{fcsw__rnz}', giem__mjt.value)
        llzwi__iixef.len = builder.load(wfcg__kxp)
        return llzwi__iixef._getvalue()
    return issmv__dnv(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    issmv__dnv = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        hhc__kpe, asek__vtd = args
        pghd__kunm = lir.Constant(lir.IntType(64), len(issmv__dnv.arr_types))
        asek__vtd, yeyxk__qbsq = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), pghd__kunm)
        yeyxk__qbsq.size = pghd__kunm
        hdp__sglo = cgutils.create_struct_proxy(issmv__dnv)(context,
            builder, hhc__kpe)
        for t, fcsw__rnz in issmv__dnv.type_to_blk.items():
            yqse__oabt = context.get_constant(types.int64, len(issmv__dnv.
                block_to_arr_ind[fcsw__rnz]))
            zodrl__jrnot = getattr(hdp__sglo, f'block_{fcsw__rnz}')
            erqft__akcf = ListInstance(context, builder, types.List(t),
                zodrl__jrnot)
            zaz__vfs = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(issmv__dnv.block_to_arr_ind[
                fcsw__rnz], dtype=np.int64))
            gxln__dntlp = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, zaz__vfs)
            with cgutils.for_range(builder, yqse__oabt) as loop:
                tjlf__koda = loop.index
                zbf__mji = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    gxln__dntlp, tjlf__koda)
                luxyj__nex = signature(types.none, issmv__dnv, types.List(t
                    ), types.int64, types.int64)
                uqyp__xvo = hhc__kpe, zodrl__jrnot, tjlf__koda, zbf__mji
                bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                    builder, luxyj__nex, uqyp__xvo)
                arr = erqft__akcf.getitem(tjlf__koda)
                rttg__ydlc = signature(array_info_type, t)
                ofcp__hxrq = arr,
                fwm__blln = array_to_info_codegen(context, builder,
                    rttg__ydlc, ofcp__hxrq)
                yeyxk__qbsq.inititem(zbf__mji, fwm__blln, incref=False)
        gpaiw__jrk = yeyxk__qbsq.value
        vyag__lhth = signature(table_type, types.List(array_info_type))
        mbd__yrcx = gpaiw__jrk,
        qqchd__ysh = arr_info_list_to_table_codegen(context, builder,
            vyag__lhth, mbd__yrcx)
        context.nrt.decref(builder, types.List(array_info_type), gpaiw__jrk)
        return qqchd__ysh
    return table_type(issmv__dnv, py_table_type_t), codegen


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='delete_table')
        builder.call(qcksh__idgzh, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='shuffle_table')
        vfsvc__lyuch = builder.call(qcksh__idgzh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vfsvc__lyuch
    return table_type(table_t, types.int64, types.boolean, types.int32
        ), codegen


class ShuffleInfoType(types.Type):

    def __init__(self):
        super(ShuffleInfoType, self).__init__(name='ShuffleInfoType()')


shuffle_info_type = ShuffleInfoType()
register_model(ShuffleInfoType)(models.OpaqueModel)
get_shuffle_info = types.ExternalFunction('get_shuffle_info',
    shuffle_info_type(table_type))
delete_shuffle_info = types.ExternalFunction('delete_shuffle_info', types.
    void(shuffle_info_type))
reverse_shuffle_table = types.ExternalFunction('reverse_shuffle_table',
    table_type(table_type, shuffle_info_type))


@intrinsic
def hash_join_table(typingctx, left_table_t, right_table_t, left_parallel_t,
    right_parallel_t, n_keys_t, n_data_left_t, n_data_right_t, same_vect_t,
    same_need_typechange_t, is_left_t, is_right_t, is_join_t,
    optional_col_t, indicator, _bodo_na_equal, cond_func, left_col_nums,
    left_col_nums_len, right_col_nums, right_col_nums_len):
    assert left_table_t == table_type
    assert right_table_t == table_type

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(1), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(8).as_pointer(), lir.IntType(64)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='hash_join_table')
        vfsvc__lyuch = builder.call(qcksh__idgzh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vfsvc__lyuch
    return table_type(left_table_t, right_table_t, types.boolean, types.
        boolean, types.int64, types.int64, types.int64, types.voidptr,
        types.voidptr, types.boolean, types.boolean, types.boolean, types.
        boolean, types.boolean, types.boolean, types.voidptr, types.voidptr,
        types.int64, types.voidptr, types.int64), codegen


@intrinsic
def compute_node_partition_by_hash(typingctx, table_t, n_keys_t, n_pes_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='compute_node_partition_by_hash')
        vfsvc__lyuch = builder.call(qcksh__idgzh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vfsvc__lyuch
    return table_type(table_t, types.int64, types.int64), codegen


@intrinsic
def sort_values_table(typingctx, table_t, n_keys_t, vect_ascending_t,
    na_position_b_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='sort_values_table')
        vfsvc__lyuch = builder.call(qcksh__idgzh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vfsvc__lyuch
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='sample_table')
        vfsvc__lyuch = builder.call(qcksh__idgzh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vfsvc__lyuch
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='shuffle_renormalization')
        vfsvc__lyuch = builder.call(qcksh__idgzh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vfsvc__lyuch
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='shuffle_renormalization_group')
        vfsvc__lyuch = builder.call(qcksh__idgzh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vfsvc__lyuch
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1)])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='drop_duplicates_table')
        vfsvc__lyuch = builder.call(qcksh__idgzh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vfsvc__lyuch
    return table_type(table_t, types.boolean, types.int64, types.int64,
        types.boolean), codegen


@intrinsic
def pivot_groupby_and_aggregate(typingctx, table_t, n_keys_t,
    dispatch_table_t, dispatch_info_t, input_has_index, ftypes,
    func_offsets, udf_n_redvars, is_parallel, is_crosstab, skipdropna_t,
    return_keys, return_index, update_cb, combine_cb, eval_cb,
    udf_table_dummy_t):
    assert table_t == table_type
    assert dispatch_table_t == table_type
    assert dispatch_info_t == table_type
    assert udf_table_dummy_t == table_type

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='pivot_groupby_and_aggregate')
        vfsvc__lyuch = builder.call(qcksh__idgzh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vfsvc__lyuch
    return table_type(table_t, types.int64, table_t, table_t, types.boolean,
        types.voidptr, types.voidptr, types.voidptr, types.boolean, types.
        boolean, types.boolean, types.boolean, types.boolean, types.voidptr,
        types.voidptr, types.voidptr, table_t), codegen


@intrinsic
def groupby_and_aggregate(typingctx, table_t, n_keys_t, input_has_index,
    ftypes, func_offsets, udf_n_redvars, is_parallel, skipdropna_t,
    shift_periods_t, transform_func, head_n, return_keys, return_index,
    dropna, update_cb, combine_cb, eval_cb, general_udfs_cb, udf_table_dummy_t
    ):
    assert table_t == table_type
    assert udf_table_dummy_t == table_type

    def codegen(context, builder, sig, args):
        exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        qcksh__idgzh = cgutils.get_or_insert_function(builder.module,
            exame__dgc, name='groupby_and_aggregate')
        vfsvc__lyuch = builder.call(qcksh__idgzh, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vfsvc__lyuch
    return table_type(table_t, types.int64, types.boolean, types.voidptr,
        types.voidptr, types.voidptr, types.boolean, types.boolean, types.
        int64, types.int64, types.int64, types.boolean, types.boolean,
        types.boolean, types.voidptr, types.voidptr, types.voidptr, types.
        voidptr, table_t), codegen


get_groupby_labels = types.ExternalFunction('get_groupby_labels', types.
    int64(table_type, types.voidptr, types.voidptr, types.boolean, types.bool_)
    )
_array_isin = types.ExternalFunction('array_isin', types.void(
    array_info_type, array_info_type, array_info_type, types.bool_))


@numba.njit
def array_isin(out_arr, in_arr, in_values, is_parallel):
    udh__qoiv = array_to_info(in_arr)
    lgk__nilwt = array_to_info(in_values)
    jug__vqv = array_to_info(out_arr)
    vuwz__qwff = arr_info_list_to_table([udh__qoiv, lgk__nilwt, jug__vqv])
    _array_isin(jug__vqv, udh__qoiv, lgk__nilwt, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(vuwz__qwff)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.voidptr, array_info_type))


@numba.njit
def get_search_regex(in_arr, case, pat, out_arr):
    udh__qoiv = array_to_info(in_arr)
    jug__vqv = array_to_info(out_arr)
    _get_search_regex(udh__qoiv, case, pat, jug__vqv)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_dtype, c_ind):
    from llvmlite import ir as lir
    if isinstance(col_dtype, types.Number) or col_dtype in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                llzwi__iixef, abx__htskq = args
                llzwi__iixef = builder.bitcast(llzwi__iixef, lir.IntType(8)
                    .as_pointer().as_pointer())
                kasqi__eap = lir.Constant(lir.IntType(64), c_ind)
                ssl__ohuf = builder.load(builder.gep(llzwi__iixef, [
                    kasqi__eap]))
                ssl__ohuf = builder.bitcast(ssl__ohuf, context.
                    get_data_type(col_dtype).as_pointer())
                return builder.load(builder.gep(ssl__ohuf, [abx__htskq]))
            return col_dtype(types.voidptr, types.int64), codegen
        return getitem_func
    if col_dtype == types.unicode_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                llzwi__iixef, abx__htskq = args
                exame__dgc = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64), lir.IntType(64).as_pointer()])
                tasw__mqs = cgutils.get_or_insert_function(builder.module,
                    exame__dgc, name='array_info_getitem')
                kasqi__eap = lir.Constant(lir.IntType(64), c_ind)
                qjc__nyw = cgutils.alloca_once(builder, lir.IntType(64))
                args = llzwi__iixef, kasqi__eap, abx__htskq, qjc__nyw
                dfjzi__hnpda = builder.call(tasw__mqs, args)
                return context.make_tuple(builder, sig.return_type, [
                    dfjzi__hnpda, builder.load(qjc__nyw)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{col_dtype}' column data type not supported"
        )


def _gen_row_na_check_intrinsic(col_array_dtype, c_ind):
    if isinstance(col_array_dtype, bodo.libs.int_arr_ext.IntegerArrayType
        ) or col_array_dtype in [bodo.libs.bool_arr_ext.boolean_array, bodo
        .libs.str_arr_ext.string_array_type] or isinstance(col_array_dtype,
        types.Array) and col_array_dtype.dtype == bodo.datetime_date_type:

        @intrinsic
        def checkna_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                ltjbk__aadk, abx__htskq = args
                ltjbk__aadk = builder.bitcast(ltjbk__aadk, lir.IntType(8).
                    as_pointer().as_pointer())
                kasqi__eap = lir.Constant(lir.IntType(64), c_ind)
                ssl__ohuf = builder.load(builder.gep(ltjbk__aadk, [kasqi__eap])
                    )
                bigwg__qwad = builder.bitcast(ssl__ohuf, context.
                    get_data_type(types.bool_).as_pointer())
                ptjf__jrx = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    bigwg__qwad, abx__htskq)
                tumu__zncdk = builder.icmp_unsigned('!=', ptjf__jrx, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(tumu__zncdk, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        col_dtype = col_array_dtype.dtype
        if col_dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    llzwi__iixef, abx__htskq = args
                    llzwi__iixef = builder.bitcast(llzwi__iixef, lir.
                        IntType(8).as_pointer().as_pointer())
                    kasqi__eap = lir.Constant(lir.IntType(64), c_ind)
                    ssl__ohuf = builder.load(builder.gep(llzwi__iixef, [
                        kasqi__eap]))
                    ssl__ohuf = builder.bitcast(ssl__ohuf, context.
                        get_data_type(col_dtype).as_pointer())
                    udb__kdyv = builder.load(builder.gep(ssl__ohuf, [
                        abx__htskq]))
                    tumu__zncdk = builder.icmp_unsigned('!=', udb__kdyv,
                        lir.Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(tumu__zncdk, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(col_dtype, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    llzwi__iixef, abx__htskq = args
                    llzwi__iixef = builder.bitcast(llzwi__iixef, lir.
                        IntType(8).as_pointer().as_pointer())
                    kasqi__eap = lir.Constant(lir.IntType(64), c_ind)
                    ssl__ohuf = builder.load(builder.gep(llzwi__iixef, [
                        kasqi__eap]))
                    ssl__ohuf = builder.bitcast(ssl__ohuf, context.
                        get_data_type(col_dtype).as_pointer())
                    udb__kdyv = builder.load(builder.gep(ssl__ohuf, [
                        abx__htskq]))
                    vsiwc__hlkl = signature(types.bool_, col_dtype)
                    ptjf__jrx = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, vsiwc__hlkl, (udb__kdyv,))
                    return builder.not_(builder.sext(ptjf__jrx, lir.IntType(8))
                        )
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
