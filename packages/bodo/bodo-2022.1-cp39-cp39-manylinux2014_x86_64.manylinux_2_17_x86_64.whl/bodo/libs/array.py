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
        eero__vxpes = context.make_helper(builder, arr_type, in_arr)
        in_arr = eero__vxpes.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        tlr__mza = context.make_helper(builder, arr_type, in_arr)
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='list_string_array_to_info')
        return builder.call(gvrii__pwef, [tlr__mza.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                sxvc__owl = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for ilhl__zbmpz in arr_typ.data:
                    sxvc__owl += get_types(ilhl__zbmpz)
                return sxvc__owl
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
            zoh__haw = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                ixvju__thri = context.make_helper(builder, arr_typ, value=arr)
                gfep__xejeg = get_lengths(_get_map_arr_data_type(arr_typ),
                    ixvju__thri.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                uslzp__dbr = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                gfep__xejeg = get_lengths(arr_typ.dtype, uslzp__dbr.data)
                gfep__xejeg = cgutils.pack_array(builder, [uslzp__dbr.
                    n_arrays] + [builder.extract_value(gfep__xejeg,
                    alx__qlj) for alx__qlj in range(gfep__xejeg.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                uslzp__dbr = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                gfep__xejeg = []
                for alx__qlj, ilhl__zbmpz in enumerate(arr_typ.data):
                    zldj__mfwwq = get_lengths(ilhl__zbmpz, builder.
                        extract_value(uslzp__dbr.data, alx__qlj))
                    gfep__xejeg += [builder.extract_value(zldj__mfwwq,
                        dpf__ezp) for dpf__ezp in range(zldj__mfwwq.type.count)
                        ]
                gfep__xejeg = cgutils.pack_array(builder, [zoh__haw,
                    context.get_constant(types.int64, -1)] + gfep__xejeg)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                gfep__xejeg = cgutils.pack_array(builder, [zoh__haw])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray')
            return gfep__xejeg

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                ixvju__thri = context.make_helper(builder, arr_typ, value=arr)
                nwg__ibez = get_buffers(_get_map_arr_data_type(arr_typ),
                    ixvju__thri.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                uslzp__dbr = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                pfrhu__toczh = get_buffers(arr_typ.dtype, uslzp__dbr.data)
                jyhz__qudod = context.make_array(types.Array(offset_type, 1,
                    'C'))(context, builder, uslzp__dbr.offsets)
                ifm__pcwd = builder.bitcast(jyhz__qudod.data, lir.IntType(8
                    ).as_pointer())
                xruwu__dbx = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, uslzp__dbr.null_bitmap)
                huv__vye = builder.bitcast(xruwu__dbx.data, lir.IntType(8).
                    as_pointer())
                nwg__ibez = cgutils.pack_array(builder, [ifm__pcwd,
                    huv__vye] + [builder.extract_value(pfrhu__toczh,
                    alx__qlj) for alx__qlj in range(pfrhu__toczh.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                uslzp__dbr = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                pfrhu__toczh = []
                for alx__qlj, ilhl__zbmpz in enumerate(arr_typ.data):
                    gkl__ahrr = get_buffers(ilhl__zbmpz, builder.
                        extract_value(uslzp__dbr.data, alx__qlj))
                    pfrhu__toczh += [builder.extract_value(gkl__ahrr,
                        dpf__ezp) for dpf__ezp in range(gkl__ahrr.type.count)]
                xruwu__dbx = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, uslzp__dbr.null_bitmap)
                huv__vye = builder.bitcast(xruwu__dbx.data, lir.IntType(8).
                    as_pointer())
                nwg__ibez = cgutils.pack_array(builder, [huv__vye] +
                    pfrhu__toczh)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                vmm__ifmw = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    vmm__ifmw = int128_type
                elif arr_typ == datetime_date_array_type:
                    vmm__ifmw = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                guue__uprl = context.make_array(types.Array(vmm__ifmw, 1, 'C')
                    )(context, builder, arr.data)
                xruwu__dbx = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, arr.null_bitmap)
                dptes__uda = builder.bitcast(guue__uprl.data, lir.IntType(8
                    ).as_pointer())
                huv__vye = builder.bitcast(xruwu__dbx.data, lir.IntType(8).
                    as_pointer())
                nwg__ibez = cgutils.pack_array(builder, [huv__vye, dptes__uda])
            elif arr_typ in (string_array_type, binary_array_type):
                uslzp__dbr = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                wiln__goguw = context.make_helper(builder, offset_arr_type,
                    uslzp__dbr.offsets).data
                pyrd__tsmf = context.make_helper(builder, char_arr_type,
                    uslzp__dbr.data).data
                pcba__bpt = context.make_helper(builder,
                    null_bitmap_arr_type, uslzp__dbr.null_bitmap).data
                nwg__ibez = cgutils.pack_array(builder, [builder.bitcast(
                    wiln__goguw, lir.IntType(8).as_pointer()), builder.
                    bitcast(pcba__bpt, lir.IntType(8).as_pointer()),
                    builder.bitcast(pyrd__tsmf, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                dptes__uda = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                gmfj__qls = lir.Constant(lir.IntType(8).as_pointer(), None)
                nwg__ibez = cgutils.pack_array(builder, [gmfj__qls, dptes__uda]
                    )
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return nwg__ibez

        def get_field_names(arr_typ):
            dag__haj = []
            if isinstance(arr_typ, StructArrayType):
                for amfu__lfs, wct__hud in zip(arr_typ.dtype.names, arr_typ
                    .data):
                    dag__haj.append(amfu__lfs)
                    dag__haj += get_field_names(wct__hud)
            elif isinstance(arr_typ, ArrayItemArrayType):
                dag__haj += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                dag__haj += get_field_names(_get_map_arr_data_type(arr_typ))
            return dag__haj
        sxvc__owl = get_types(arr_type)
        qwj__nmdg = cgutils.pack_array(builder, [context.get_constant(types
            .int32, t) for t in sxvc__owl])
        swv__hldx = cgutils.alloca_once_value(builder, qwj__nmdg)
        gfep__xejeg = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, gfep__xejeg)
        nwg__ibez = get_buffers(arr_type, in_arr)
        gjxr__lipew = cgutils.alloca_once_value(builder, nwg__ibez)
        dag__haj = get_field_names(arr_type)
        if len(dag__haj) == 0:
            dag__haj = ['irrelevant']
        qih__htbj = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in dag__haj])
        xlprc__bidx = cgutils.alloca_once_value(builder, qih__htbj)
        if isinstance(arr_type, MapArrayType):
            rtg__fpj = _get_map_arr_data_type(arr_type)
            acv__wgzl = context.make_helper(builder, arr_type, value=in_arr)
            rrq__klrrs = acv__wgzl.data
        else:
            rtg__fpj = arr_type
            rrq__klrrs = in_arr
        bmnvy__ldc = context.make_helper(builder, rtg__fpj, rrq__klrrs)
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='nested_array_to_info')
        vhidt__epv = builder.call(gvrii__pwef, [builder.bitcast(swv__hldx,
            lir.IntType(32).as_pointer()), builder.bitcast(gjxr__lipew, lir
            .IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            xlprc__bidx, lir.IntType(8).as_pointer()), bmnvy__ldc.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vhidt__epv
    if arr_type in (string_array_type, binary_array_type):
        qpe__ioze = context.make_helper(builder, arr_type, in_arr)
        fzmuz__fmae = ArrayItemArrayType(char_arr_type)
        tlr__mza = context.make_helper(builder, fzmuz__fmae, qpe__ioze.data)
        uslzp__dbr = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        wiln__goguw = context.make_helper(builder, offset_arr_type,
            uslzp__dbr.offsets).data
        pyrd__tsmf = context.make_helper(builder, char_arr_type, uslzp__dbr
            .data).data
        pcba__bpt = context.make_helper(builder, null_bitmap_arr_type,
            uslzp__dbr.null_bitmap).data
        rlv__rhsx = builder.zext(builder.load(builder.gep(wiln__goguw, [
            uslzp__dbr.n_arrays])), lir.IntType(64))
        nrkp__tjs = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='string_array_to_info')
        return builder.call(gvrii__pwef, [uslzp__dbr.n_arrays, rlv__rhsx,
            pyrd__tsmf, wiln__goguw, pcba__bpt, tlr__mza.meminfo, nrkp__tjs])
    bfsq__braf = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        oal__zzl = context.compile_internal(builder, lambda a: len(a.dtype.
            categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        fnvj__qrk = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(fnvj__qrk, 1, 'C')
        bfsq__braf = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        zoh__haw = builder.extract_value(arr.shape, 0)
        yjvky__wlpc = arr_type.dtype
        gdqj__mscqu = numba_to_c_type(yjvky__wlpc)
        zrt__nszcu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), gdqj__mscqu))
        if bfsq__braf:
            bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            gvrii__pwef = cgutils.get_or_insert_function(builder.module,
                bio__hkkl, name='categorical_array_to_info')
            return builder.call(gvrii__pwef, [zoh__haw, builder.bitcast(arr
                .data, lir.IntType(8).as_pointer()), builder.load(
                zrt__nszcu), oal__zzl, arr.meminfo])
        else:
            bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            gvrii__pwef = cgutils.get_or_insert_function(builder.module,
                bio__hkkl, name='numpy_array_to_info')
            return builder.call(gvrii__pwef, [zoh__haw, builder.bitcast(arr
                .data, lir.IntType(8).as_pointer()), builder.load(
                zrt__nszcu), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        yjvky__wlpc = arr_type.dtype
        vmm__ifmw = yjvky__wlpc
        if isinstance(arr_type, DecimalArrayType):
            vmm__ifmw = int128_type
        if arr_type == datetime_date_array_type:
            vmm__ifmw = types.int64
        guue__uprl = context.make_array(types.Array(vmm__ifmw, 1, 'C'))(context
            , builder, arr.data)
        zoh__haw = builder.extract_value(guue__uprl.shape, 0)
        ovf__jnak = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        gdqj__mscqu = numba_to_c_type(yjvky__wlpc)
        zrt__nszcu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), gdqj__mscqu))
        if isinstance(arr_type, DecimalArrayType):
            bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            gvrii__pwef = cgutils.get_or_insert_function(builder.module,
                bio__hkkl, name='decimal_array_to_info')
            return builder.call(gvrii__pwef, [zoh__haw, builder.bitcast(
                guue__uprl.data, lir.IntType(8).as_pointer()), builder.load
                (zrt__nszcu), builder.bitcast(ovf__jnak.data, lir.IntType(8
                ).as_pointer()), guue__uprl.meminfo, ovf__jnak.meminfo,
                context.get_constant(types.int32, arr_type.precision),
                context.get_constant(types.int32, arr_type.scale)])
        else:
            bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            gvrii__pwef = cgutils.get_or_insert_function(builder.module,
                bio__hkkl, name='nullable_array_to_info')
            return builder.call(gvrii__pwef, [zoh__haw, builder.bitcast(
                guue__uprl.data, lir.IntType(8).as_pointer()), builder.load
                (zrt__nszcu), builder.bitcast(ovf__jnak.data, lir.IntType(8
                ).as_pointer()), guue__uprl.meminfo, ovf__jnak.meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        yek__wozvc = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        unckl__gxfw = context.make_array(arr_type.arr_type)(context,
            builder, arr.right)
        zoh__haw = builder.extract_value(yek__wozvc.shape, 0)
        gdqj__mscqu = numba_to_c_type(arr_type.arr_type.dtype)
        zrt__nszcu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), gdqj__mscqu))
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='interval_array_to_info')
        return builder.call(gvrii__pwef, [zoh__haw, builder.bitcast(
            yek__wozvc.data, lir.IntType(8).as_pointer()), builder.bitcast(
            unckl__gxfw.data, lir.IntType(8).as_pointer()), builder.load(
            zrt__nszcu), yek__wozvc.meminfo, unckl__gxfw.meminfo])
    raise BodoError(f'array_to_info(): array type {arr_type} is not supported')


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    uejwd__dmqhe = cgutils.alloca_once(builder, lir.IntType(64))
    dptes__uda = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    lmfd__kle = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    bio__hkkl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(64).as_pointer(), lir.IntType(8).as_pointer().
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    gvrii__pwef = cgutils.get_or_insert_function(builder.module, bio__hkkl,
        name='info_to_numpy_array')
    builder.call(gvrii__pwef, [in_info, uejwd__dmqhe, dptes__uda, lmfd__kle])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    vui__otrzx = context.get_value_type(types.intp)
    vil__wqqi = cgutils.pack_array(builder, [builder.load(uejwd__dmqhe)],
        ty=vui__otrzx)
    hctxy__zawj = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    zpvv__gtug = cgutils.pack_array(builder, [hctxy__zawj], ty=vui__otrzx)
    pyrd__tsmf = builder.bitcast(builder.load(dptes__uda), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=pyrd__tsmf, shape=vil__wqqi,
        strides=zpvv__gtug, itemsize=hctxy__zawj, meminfo=builder.load(
        lmfd__kle))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    nqgrn__kbqe = context.make_helper(builder, arr_type)
    bio__hkkl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(8).as_pointer().as_pointer()])
    gvrii__pwef = cgutils.get_or_insert_function(builder.module, bio__hkkl,
        name='info_to_list_string_array')
    builder.call(gvrii__pwef, [in_info, nqgrn__kbqe._get_ptr_by_name(
        'meminfo')])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return nqgrn__kbqe._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    hytum__aof = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        ibaaf__qwcgd = lengths_pos
        huwaw__yrpqi = infos_pos
        glvsz__tcoiz, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        rhwpp__wtep = ArrayItemArrayPayloadType(arr_typ)
        vvno__krxw = context.get_data_type(rhwpp__wtep)
        bwe__ekqx = context.get_abi_sizeof(vvno__krxw)
        rqz__zfu = define_array_item_dtor(context, builder, arr_typ,
            rhwpp__wtep)
        vhpcu__pimgh = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, bwe__ekqx), rqz__zfu)
        lhjx__fxaew = context.nrt.meminfo_data(builder, vhpcu__pimgh)
        xlot__rhol = builder.bitcast(lhjx__fxaew, vvno__krxw.as_pointer())
        uslzp__dbr = cgutils.create_struct_proxy(rhwpp__wtep)(context, builder)
        uslzp__dbr.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), ibaaf__qwcgd)
        uslzp__dbr.data = glvsz__tcoiz
        smfm__qghd = builder.load(array_infos_ptr)
        qtl__jvodh = builder.bitcast(builder.extract_value(smfm__qghd,
            huwaw__yrpqi), hytum__aof)
        uslzp__dbr.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, qtl__jvodh)
        absx__bmh = builder.bitcast(builder.extract_value(smfm__qghd, 
            huwaw__yrpqi + 1), hytum__aof)
        uslzp__dbr.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, absx__bmh)
        builder.store(uslzp__dbr._getvalue(), xlot__rhol)
        tlr__mza = context.make_helper(builder, arr_typ)
        tlr__mza.meminfo = vhpcu__pimgh
        return tlr__mza._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        ixjp__cnioj = []
        huwaw__yrpqi = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for uiz__xcadj in arr_typ.data:
            glvsz__tcoiz, lengths_pos, infos_pos = nested_to_array(context,
                builder, uiz__xcadj, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            ixjp__cnioj.append(glvsz__tcoiz)
        rhwpp__wtep = StructArrayPayloadType(arr_typ.data)
        vvno__krxw = context.get_value_type(rhwpp__wtep)
        bwe__ekqx = context.get_abi_sizeof(vvno__krxw)
        rqz__zfu = define_struct_arr_dtor(context, builder, arr_typ,
            rhwpp__wtep)
        vhpcu__pimgh = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, bwe__ekqx), rqz__zfu)
        lhjx__fxaew = context.nrt.meminfo_data(builder, vhpcu__pimgh)
        xlot__rhol = builder.bitcast(lhjx__fxaew, vvno__krxw.as_pointer())
        uslzp__dbr = cgutils.create_struct_proxy(rhwpp__wtep)(context, builder)
        uslzp__dbr.data = cgutils.pack_array(builder, ixjp__cnioj
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, ixjp__cnioj)
        smfm__qghd = builder.load(array_infos_ptr)
        absx__bmh = builder.bitcast(builder.extract_value(smfm__qghd,
            huwaw__yrpqi), hytum__aof)
        uslzp__dbr.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, absx__bmh)
        builder.store(uslzp__dbr._getvalue(), xlot__rhol)
        ucv__rhdkh = context.make_helper(builder, arr_typ)
        ucv__rhdkh.meminfo = vhpcu__pimgh
        return ucv__rhdkh._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        smfm__qghd = builder.load(array_infos_ptr)
        tfvso__rcth = builder.bitcast(builder.extract_value(smfm__qghd,
            infos_pos), hytum__aof)
        qpe__ioze = context.make_helper(builder, arr_typ)
        fzmuz__fmae = ArrayItemArrayType(char_arr_type)
        tlr__mza = context.make_helper(builder, fzmuz__fmae)
        bio__hkkl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='info_to_string_array')
        builder.call(gvrii__pwef, [tfvso__rcth, tlr__mza._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        qpe__ioze.data = tlr__mza._getvalue()
        return qpe__ioze._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        smfm__qghd = builder.load(array_infos_ptr)
        qsg__ysn = builder.bitcast(builder.extract_value(smfm__qghd, 
            infos_pos + 1), hytum__aof)
        return _lower_info_to_array_numpy(arr_typ, context, builder, qsg__ysn
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        vmm__ifmw = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            vmm__ifmw = int128_type
        elif arr_typ == datetime_date_array_type:
            vmm__ifmw = types.int64
        smfm__qghd = builder.load(array_infos_ptr)
        absx__bmh = builder.bitcast(builder.extract_value(smfm__qghd,
            infos_pos), hytum__aof)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, absx__bmh)
        qsg__ysn = builder.bitcast(builder.extract_value(smfm__qghd, 
            infos_pos + 1), hytum__aof)
        arr.data = _lower_info_to_array_numpy(types.Array(vmm__ifmw, 1, 'C'
            ), context, builder, qsg__ysn)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


@intrinsic
def info_to_array(typingctx, info_type, array_type):
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    assert info_type == array_info_type

    def codegen(context, builder, sig, args):
        in_info, bwo__qgamv = args
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
                    return 1 + sum([get_num_arrays(uiz__xcadj) for
                        uiz__xcadj in arr_typ.data])
                else:
                    return 1

            def get_num_infos(arr_typ):
                if isinstance(arr_typ, ArrayItemArrayType):
                    return 2 + get_num_infos(arr_typ.dtype)
                elif isinstance(arr_typ, StructArrayType):
                    return 1 + sum([get_num_infos(uiz__xcadj) for
                        uiz__xcadj in arr_typ.data])
                elif arr_typ in (string_array_type, binary_array_type):
                    return 1
                else:
                    return 2
            if isinstance(arr_type, TupleArrayType):
                sdv__hvg = StructArrayType(arr_type.data, ('dummy',) * len(
                    arr_type.data))
            elif isinstance(arr_type, MapArrayType):
                sdv__hvg = _get_map_arr_data_type(arr_type)
            else:
                sdv__hvg = arr_type
            dgyrp__eywx = get_num_arrays(sdv__hvg)
            gfep__xejeg = cgutils.pack_array(builder, [lir.Constant(lir.
                IntType(64), 0) for bwo__qgamv in range(dgyrp__eywx)])
            lengths_ptr = cgutils.alloca_once_value(builder, gfep__xejeg)
            gmfj__qls = lir.Constant(lir.IntType(8).as_pointer(), None)
            bci__aek = cgutils.pack_array(builder, [gmfj__qls for
                bwo__qgamv in range(get_num_infos(sdv__hvg))])
            array_infos_ptr = cgutils.alloca_once_value(builder, bci__aek)
            bio__hkkl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
                as_pointer().as_pointer()])
            gvrii__pwef = cgutils.get_or_insert_function(builder.module,
                bio__hkkl, name='info_to_nested_array')
            builder.call(gvrii__pwef, [in_info, builder.bitcast(lengths_ptr,
                lir.IntType(64).as_pointer()), builder.bitcast(
                array_infos_ptr, lir.IntType(8).as_pointer().as_pointer())])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            arr, bwo__qgamv, bwo__qgamv = nested_to_array(context, builder,
                sdv__hvg, lengths_ptr, array_infos_ptr, 0, 0)
            if isinstance(arr_type, TupleArrayType):
                eero__vxpes = context.make_helper(builder, arr_type)
                eero__vxpes.data = arr
                context.nrt.incref(builder, sdv__hvg, arr)
                arr = eero__vxpes._getvalue()
            elif isinstance(arr_type, MapArrayType):
                sig = signature(arr_type, sdv__hvg)
                arr = init_map_arr_codegen(context, builder, sig, (arr,))
            return arr
        if arr_type in (string_array_type, binary_array_type):
            qpe__ioze = context.make_helper(builder, arr_type)
            fzmuz__fmae = ArrayItemArrayType(char_arr_type)
            tlr__mza = context.make_helper(builder, fzmuz__fmae)
            bio__hkkl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
            gvrii__pwef = cgutils.get_or_insert_function(builder.module,
                bio__hkkl, name='info_to_string_array')
            builder.call(gvrii__pwef, [in_info, tlr__mza._get_ptr_by_name(
                'meminfo')])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            qpe__ioze.data = tlr__mza._getvalue()
            return qpe__ioze._getvalue()
        if isinstance(arr_type, CategoricalArrayType):
            out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            fnvj__qrk = get_categories_int_type(arr_type.dtype)
            hjyd__nkaq = types.Array(fnvj__qrk, 1, 'C')
            out_arr.codes = _lower_info_to_array_numpy(hjyd__nkaq, context,
                builder, in_info)
            if isinstance(array_type, types.TypeRef):
                assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
                is_ordered = arr_type.dtype.ordered
                yyu__xwam = pd.CategoricalDtype(arr_type.dtype.categories,
                    is_ordered).categories.values
                new_cats_tup = MetaType(tuple(yyu__xwam))
                int_type = arr_type.dtype.int_type
                ellyr__vuq = bodo.typeof(yyu__xwam)
                bwiim__bgcwl = context.get_constant_generic(builder,
                    ellyr__vuq, yyu__xwam)
                yjvky__wlpc = context.compile_internal(builder, lambda
                    c_arr: bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                    bodo.utils.conversion.index_from_array(c_arr),
                    is_ordered, int_type, new_cats_tup), arr_type.dtype(
                    ellyr__vuq), [bwiim__bgcwl])
            else:
                yjvky__wlpc = cgutils.create_struct_proxy(arr_type)(context,
                    builder, args[1]).dtype
                context.nrt.incref(builder, arr_type.dtype, yjvky__wlpc)
            out_arr.dtype = yjvky__wlpc
            return out_arr._getvalue()
        if isinstance(arr_type, types.Array):
            return _lower_info_to_array_numpy(arr_type, context, builder,
                in_info)
        if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
            ) or arr_type in (boolean_array, datetime_date_array_type):
            arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            vmm__ifmw = arr_type.dtype
            if isinstance(arr_type, DecimalArrayType):
                vmm__ifmw = int128_type
            elif arr_type == datetime_date_array_type:
                vmm__ifmw = types.int64
            ktx__dowa = types.Array(vmm__ifmw, 1, 'C')
            guue__uprl = context.make_array(ktx__dowa)(context, builder)
            nyb__yqqe = types.Array(types.uint8, 1, 'C')
            afns__mpq = context.make_array(nyb__yqqe)(context, builder)
            uejwd__dmqhe = cgutils.alloca_once(builder, lir.IntType(64))
            wjk__ley = cgutils.alloca_once(builder, lir.IntType(64))
            dptes__uda = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            ellv__efsm = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            lmfd__kle = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            gqd__uqyj = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            bio__hkkl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64)
                .as_pointer(), lir.IntType(8).as_pointer().as_pointer(),
                lir.IntType(8).as_pointer().as_pointer(), lir.IntType(8).
                as_pointer().as_pointer(), lir.IntType(8).as_pointer().
                as_pointer()])
            gvrii__pwef = cgutils.get_or_insert_function(builder.module,
                bio__hkkl, name='info_to_nullable_array')
            builder.call(gvrii__pwef, [in_info, uejwd__dmqhe, wjk__ley,
                dptes__uda, ellv__efsm, lmfd__kle, gqd__uqyj])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            vui__otrzx = context.get_value_type(types.intp)
            vil__wqqi = cgutils.pack_array(builder, [builder.load(
                uejwd__dmqhe)], ty=vui__otrzx)
            hctxy__zawj = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(vmm__ifmw)))
            zpvv__gtug = cgutils.pack_array(builder, [hctxy__zawj], ty=
                vui__otrzx)
            pyrd__tsmf = builder.bitcast(builder.load(dptes__uda), context.
                get_data_type(vmm__ifmw).as_pointer())
            numba.np.arrayobj.populate_array(guue__uprl, data=pyrd__tsmf,
                shape=vil__wqqi, strides=zpvv__gtug, itemsize=hctxy__zawj,
                meminfo=builder.load(lmfd__kle))
            arr.data = guue__uprl._getvalue()
            vil__wqqi = cgutils.pack_array(builder, [builder.load(wjk__ley)
                ], ty=vui__otrzx)
            hctxy__zawj = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(types.uint8)))
            zpvv__gtug = cgutils.pack_array(builder, [hctxy__zawj], ty=
                vui__otrzx)
            pyrd__tsmf = builder.bitcast(builder.load(ellv__efsm), context.
                get_data_type(types.uint8).as_pointer())
            numba.np.arrayobj.populate_array(afns__mpq, data=pyrd__tsmf,
                shape=vil__wqqi, strides=zpvv__gtug, itemsize=hctxy__zawj,
                meminfo=builder.load(gqd__uqyj))
            arr.null_bitmap = afns__mpq._getvalue()
            return arr._getvalue()
        if isinstance(arr_type, IntervalArrayType):
            arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            yek__wozvc = context.make_array(arr_type.arr_type)(context, builder
                )
            unckl__gxfw = context.make_array(arr_type.arr_type)(context,
                builder)
            uejwd__dmqhe = cgutils.alloca_once(builder, lir.IntType(64))
            vwhl__qlfcf = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            atf__ipsrv = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            nds__ymv = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
                )
            ywlw__zyzxb = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            bio__hkkl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
                as_pointer().as_pointer(), lir.IntType(8).as_pointer().
                as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir
                .IntType(8).as_pointer().as_pointer()])
            gvrii__pwef = cgutils.get_or_insert_function(builder.module,
                bio__hkkl, name='info_to_interval_array')
            builder.call(gvrii__pwef, [in_info, uejwd__dmqhe, vwhl__qlfcf,
                atf__ipsrv, nds__ymv, ywlw__zyzxb])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            vui__otrzx = context.get_value_type(types.intp)
            vil__wqqi = cgutils.pack_array(builder, [builder.load(
                uejwd__dmqhe)], ty=vui__otrzx)
            hctxy__zawj = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
            zpvv__gtug = cgutils.pack_array(builder, [hctxy__zawj], ty=
                vui__otrzx)
            qtgh__axnmc = builder.bitcast(builder.load(vwhl__qlfcf),
                context.get_data_type(arr_type.arr_type.dtype).as_pointer())
            numba.np.arrayobj.populate_array(yek__wozvc, data=qtgh__axnmc,
                shape=vil__wqqi, strides=zpvv__gtug, itemsize=hctxy__zawj,
                meminfo=builder.load(nds__ymv))
            arr.left = yek__wozvc._getvalue()
            oihbt__ppm = builder.bitcast(builder.load(atf__ipsrv), context.
                get_data_type(arr_type.arr_type.dtype).as_pointer())
            numba.np.arrayobj.populate_array(unckl__gxfw, data=oihbt__ppm,
                shape=vil__wqqi, strides=zpvv__gtug, itemsize=hctxy__zawj,
                meminfo=builder.load(ywlw__zyzxb))
            arr.right = unckl__gxfw._getvalue()
            return arr._getvalue()
        raise BodoError(
            f'info_to_array(): array type {arr_type} is not supported')
    return arr_type(info_type, array_type), codegen


@intrinsic
def test_alloc_np(typingctx, len_typ, arr_type):
    array_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type

    def codegen(context, builder, sig, args):
        zoh__haw, bwo__qgamv = args
        gdqj__mscqu = numba_to_c_type(array_type.dtype)
        zrt__nszcu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), gdqj__mscqu))
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='alloc_numpy')
        return builder.call(gvrii__pwef, [zoh__haw, builder.load(zrt__nszcu)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        zoh__haw, znbi__ysaw = args
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='alloc_string_array')
        return builder.call(gvrii__pwef, [zoh__haw, znbi__ysaw])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    izwtm__oeyxk, = args
    qvjr__nbssq = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], izwtm__oeyxk)
    bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(
        8).as_pointer().as_pointer(), lir.IntType(64)])
    gvrii__pwef = cgutils.get_or_insert_function(builder.module, bio__hkkl,
        name='arr_info_list_to_table')
    return builder.call(gvrii__pwef, [qvjr__nbssq.data, qvjr__nbssq.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='info_from_table')
        return builder.call(gvrii__pwef, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    mls__yvucx = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        pfxto__huz, hne__eqyfp, bwo__qgamv = args
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='info_from_table')
        zuy__vvldx = cgutils.create_struct_proxy(mls__yvucx)(context, builder)
        zuy__vvldx.parent = cgutils.get_null_value(zuy__vvldx.parent.type)
        oekp__jnus = context.make_array(table_idx_arr_t)(context, builder,
            hne__eqyfp)
        xmmow__evmet = context.get_constant(types.int64, -1)
        lpkxh__ocqqj = context.get_constant(types.int64, 0)
        ogosw__wjvd = cgutils.alloca_once_value(builder, lpkxh__ocqqj)
        for t, jwhv__jxd in mls__yvucx.type_to_blk.items():
            ekipu__bne = context.get_constant(types.int64, len(mls__yvucx.
                block_to_arr_ind[jwhv__jxd]))
            bwo__qgamv, hju__awbyd = ListInstance.allocate_ex(context,
                builder, types.List(t), ekipu__bne)
            hju__awbyd.size = ekipu__bne
            kgdra__wcehl = context.make_constant_array(builder, types.Array
                (types.int64, 1, 'C'), np.array(mls__yvucx.block_to_arr_ind
                [jwhv__jxd], dtype=np.int64))
            wgiwx__ptvt = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, kgdra__wcehl)
            with cgutils.for_range(builder, ekipu__bne) as loop:
                alx__qlj = loop.index
                scoma__lsg = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    wgiwx__ptvt, alx__qlj)
                mzuv__isfg = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, oekp__jnus, scoma__lsg)
                xicvo__zov = builder.icmp_unsigned('!=', mzuv__isfg,
                    xmmow__evmet)
                with builder.if_else(xicvo__zov) as (then, orelse):
                    with then:
                        qjwyu__elyr = builder.call(gvrii__pwef, [pfxto__huz,
                            mzuv__isfg])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            qjwyu__elyr])
                        hju__awbyd.inititem(alx__qlj, arr, incref=False)
                        zoh__haw = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(zoh__haw, ogosw__wjvd)
                    with orelse:
                        xbia__szo = context.get_constant_null(t)
                        hju__awbyd.inititem(alx__qlj, xbia__szo, incref=False)
            setattr(zuy__vvldx, f'block_{jwhv__jxd}', hju__awbyd.value)
        zuy__vvldx.len = builder.load(ogosw__wjvd)
        return zuy__vvldx._getvalue()
    return mls__yvucx(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    mls__yvucx = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        bjnw__mro, bwo__qgamv = args
        lbumm__bapgl = lir.Constant(lir.IntType(64), len(mls__yvucx.arr_types))
        bwo__qgamv, kkqr__giazi = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), lbumm__bapgl)
        kkqr__giazi.size = lbumm__bapgl
        xepdc__knzbl = cgutils.create_struct_proxy(mls__yvucx)(context,
            builder, bjnw__mro)
        for t, jwhv__jxd in mls__yvucx.type_to_blk.items():
            ekipu__bne = context.get_constant(types.int64, len(mls__yvucx.
                block_to_arr_ind[jwhv__jxd]))
            yqhxz__clgd = getattr(xepdc__knzbl, f'block_{jwhv__jxd}')
            uwveu__tmhq = ListInstance(context, builder, types.List(t),
                yqhxz__clgd)
            kgdra__wcehl = context.make_constant_array(builder, types.Array
                (types.int64, 1, 'C'), np.array(mls__yvucx.block_to_arr_ind
                [jwhv__jxd], dtype=np.int64))
            wgiwx__ptvt = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, kgdra__wcehl)
            with cgutils.for_range(builder, ekipu__bne) as loop:
                alx__qlj = loop.index
                scoma__lsg = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    wgiwx__ptvt, alx__qlj)
                rrjkc__nnop = signature(types.none, mls__yvucx, types.List(
                    t), types.int64, types.int64)
                txj__pjl = bjnw__mro, yqhxz__clgd, alx__qlj, scoma__lsg
                bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                    builder, rrjkc__nnop, txj__pjl)
                arr = uwveu__tmhq.getitem(alx__qlj)
                zllh__pld = signature(array_info_type, t)
                nzmau__rwfcz = arr,
                bsftw__rvbd = array_to_info_codegen(context, builder,
                    zllh__pld, nzmau__rwfcz)
                kkqr__giazi.inititem(scoma__lsg, bsftw__rvbd, incref=False)
        raf__myznp = kkqr__giazi.value
        tptz__hmeuj = signature(table_type, types.List(array_info_type))
        afwew__gdc = raf__myznp,
        pfxto__huz = arr_info_list_to_table_codegen(context, builder,
            tptz__hmeuj, afwew__gdc)
        context.nrt.decref(builder, types.List(array_info_type), raf__myznp)
        return pfxto__huz
    return table_type(mls__yvucx, py_table_type_t), codegen


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        bio__hkkl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='delete_table')
        builder.call(gvrii__pwef, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='shuffle_table')
        vhidt__epv = builder.call(gvrii__pwef, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vhidt__epv
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
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(1), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(8).as_pointer(), lir.IntType(64)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='hash_join_table')
        vhidt__epv = builder.call(gvrii__pwef, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vhidt__epv
    return table_type(left_table_t, right_table_t, types.boolean, types.
        boolean, types.int64, types.int64, types.int64, types.voidptr,
        types.voidptr, types.boolean, types.boolean, types.boolean, types.
        boolean, types.boolean, types.boolean, types.voidptr, types.voidptr,
        types.int64, types.voidptr, types.int64), codegen


@intrinsic
def compute_node_partition_by_hash(typingctx, table_t, n_keys_t, n_pes_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='compute_node_partition_by_hash')
        vhidt__epv = builder.call(gvrii__pwef, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vhidt__epv
    return table_type(table_t, types.int64, types.int64), codegen


@intrinsic
def sort_values_table(typingctx, table_t, n_keys_t, vect_ascending_t,
    na_position_b_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='sort_values_table')
        vhidt__epv = builder.call(gvrii__pwef, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vhidt__epv
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='sample_table')
        vhidt__epv = builder.call(gvrii__pwef, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vhidt__epv
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='shuffle_renormalization')
        vhidt__epv = builder.call(gvrii__pwef, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vhidt__epv
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='shuffle_renormalization_group')
        vhidt__epv = builder.call(gvrii__pwef, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vhidt__epv
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1)])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='drop_duplicates_table')
        vhidt__epv = builder.call(gvrii__pwef, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vhidt__epv
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
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='pivot_groupby_and_aggregate')
        vhidt__epv = builder.call(gvrii__pwef, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vhidt__epv
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
        bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        gvrii__pwef = cgutils.get_or_insert_function(builder.module,
            bio__hkkl, name='groupby_and_aggregate')
        vhidt__epv = builder.call(gvrii__pwef, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return vhidt__epv
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
    pbg__lhk = array_to_info(in_arr)
    gjch__aov = array_to_info(in_values)
    pjx__yufz = array_to_info(out_arr)
    xhz__fqlla = arr_info_list_to_table([pbg__lhk, gjch__aov, pjx__yufz])
    _array_isin(pjx__yufz, pbg__lhk, gjch__aov, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(xhz__fqlla)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.voidptr, array_info_type))


@numba.njit
def get_search_regex(in_arr, case, pat, out_arr):
    pbg__lhk = array_to_info(in_arr)
    pjx__yufz = array_to_info(out_arr)
    _get_search_regex(pbg__lhk, case, pat, pjx__yufz)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_dtype, c_ind):
    from llvmlite import ir as lir
    if isinstance(col_dtype, types.Number) or col_dtype in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                zuy__vvldx, cjk__qkl = args
                zuy__vvldx = builder.bitcast(zuy__vvldx, lir.IntType(8).
                    as_pointer().as_pointer())
                upw__akcj = lir.Constant(lir.IntType(64), c_ind)
                wqhv__hdph = builder.load(builder.gep(zuy__vvldx, [upw__akcj]))
                wqhv__hdph = builder.bitcast(wqhv__hdph, context.
                    get_data_type(col_dtype).as_pointer())
                return builder.load(builder.gep(wqhv__hdph, [cjk__qkl]))
            return col_dtype(types.voidptr, types.int64), codegen
        return getitem_func
    if col_dtype == types.unicode_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                zuy__vvldx, cjk__qkl = args
                bio__hkkl = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64), lir.IntType(64).as_pointer()])
                hgbx__ndwc = cgutils.get_or_insert_function(builder.module,
                    bio__hkkl, name='array_info_getitem')
                upw__akcj = lir.Constant(lir.IntType(64), c_ind)
                vzfu__fml = cgutils.alloca_once(builder, lir.IntType(64))
                args = zuy__vvldx, upw__akcj, cjk__qkl, vzfu__fml
                dptes__uda = builder.call(hgbx__ndwc, args)
                return context.make_tuple(builder, sig.return_type, [
                    dptes__uda, builder.load(vzfu__fml)])
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
                ruijf__doyb, cjk__qkl = args
                ruijf__doyb = builder.bitcast(ruijf__doyb, lir.IntType(8).
                    as_pointer().as_pointer())
                upw__akcj = lir.Constant(lir.IntType(64), c_ind)
                wqhv__hdph = builder.load(builder.gep(ruijf__doyb, [upw__akcj])
                    )
                pcba__bpt = builder.bitcast(wqhv__hdph, context.
                    get_data_type(types.bool_).as_pointer())
                hat__wkwpm = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    pcba__bpt, cjk__qkl)
                dad__iigf = builder.icmp_unsigned('!=', hat__wkwpm, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(dad__iigf, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        col_dtype = col_array_dtype.dtype
        if col_dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    zuy__vvldx, cjk__qkl = args
                    zuy__vvldx = builder.bitcast(zuy__vvldx, lir.IntType(8)
                        .as_pointer().as_pointer())
                    upw__akcj = lir.Constant(lir.IntType(64), c_ind)
                    wqhv__hdph = builder.load(builder.gep(zuy__vvldx, [
                        upw__akcj]))
                    wqhv__hdph = builder.bitcast(wqhv__hdph, context.
                        get_data_type(col_dtype).as_pointer())
                    zlgk__drdd = builder.load(builder.gep(wqhv__hdph, [
                        cjk__qkl]))
                    dad__iigf = builder.icmp_unsigned('!=', zlgk__drdd, lir
                        .Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(dad__iigf, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(col_dtype, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    zuy__vvldx, cjk__qkl = args
                    zuy__vvldx = builder.bitcast(zuy__vvldx, lir.IntType(8)
                        .as_pointer().as_pointer())
                    upw__akcj = lir.Constant(lir.IntType(64), c_ind)
                    wqhv__hdph = builder.load(builder.gep(zuy__vvldx, [
                        upw__akcj]))
                    wqhv__hdph = builder.bitcast(wqhv__hdph, context.
                        get_data_type(col_dtype).as_pointer())
                    zlgk__drdd = builder.load(builder.gep(wqhv__hdph, [
                        cjk__qkl]))
                    jth__uhjg = signature(types.bool_, col_dtype)
                    hat__wkwpm = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, jth__uhjg, (zlgk__drdd,))
                    return builder.not_(builder.sext(hat__wkwpm, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
