"""Tools for handling bodo arrays, e.g. passing to C/C++ code
"""
from collections import defaultdict
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
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, get_overload_const_int, is_str_arr_type, raise_bodo_error, type_has_unknown_cats, unwrap_typeref
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, numba_to_c_type
ll.add_symbol('list_string_array_to_info', array_ext.list_string_array_to_info)
ll.add_symbol('nested_array_to_info', array_ext.nested_array_to_info)
ll.add_symbol('string_array_to_info', array_ext.string_array_to_info)
ll.add_symbol('dict_str_array_to_info', array_ext.dict_str_array_to_info)
ll.add_symbol('get_nested_info', array_ext.get_nested_info)
ll.add_symbol('get_has_global_dictionary', array_ext.get_has_global_dictionary)
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
ll.add_symbol('array_info_getitem', array_ext.array_info_getitem)
ll.add_symbol('array_info_getdata1', array_ext.array_info_getdata1)


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


def array_to_info_codegen(context, builder, sig, args, incref=True):
    in_arr, = args
    arr_type = sig.args[0]
    if incref:
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, TupleArrayType):
        flsk__jvw = context.make_helper(builder, arr_type, in_arr)
        in_arr = flsk__jvw.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        btx__zhct = context.make_helper(builder, arr_type, in_arr)
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='list_string_array_to_info')
        return builder.call(fpjkz__smjg, [btx__zhct.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                ysy__osmnv = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for zqzrg__cuzbh in arr_typ.data:
                    ysy__osmnv += get_types(zqzrg__cuzbh)
                return ysy__osmnv
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
            silx__dmms = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                gmb__dyeo = context.make_helper(builder, arr_typ, value=arr)
                caq__ruxx = get_lengths(_get_map_arr_data_type(arr_typ),
                    gmb__dyeo.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                mnvi__mun = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                caq__ruxx = get_lengths(arr_typ.dtype, mnvi__mun.data)
                caq__ruxx = cgutils.pack_array(builder, [mnvi__mun.n_arrays
                    ] + [builder.extract_value(caq__ruxx, dld__kwfly) for
                    dld__kwfly in range(caq__ruxx.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                mnvi__mun = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                caq__ruxx = []
                for dld__kwfly, zqzrg__cuzbh in enumerate(arr_typ.data):
                    clulu__guv = get_lengths(zqzrg__cuzbh, builder.
                        extract_value(mnvi__mun.data, dld__kwfly))
                    caq__ruxx += [builder.extract_value(clulu__guv,
                        mdztk__wudq) for mdztk__wudq in range(clulu__guv.
                        type.count)]
                caq__ruxx = cgutils.pack_array(builder, [silx__dmms,
                    context.get_constant(types.int64, -1)] + caq__ruxx)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                caq__ruxx = cgutils.pack_array(builder, [silx__dmms])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return caq__ruxx

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                gmb__dyeo = context.make_helper(builder, arr_typ, value=arr)
                obtn__mzw = get_buffers(_get_map_arr_data_type(arr_typ),
                    gmb__dyeo.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                mnvi__mun = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                aczfe__hpj = get_buffers(arr_typ.dtype, mnvi__mun.data)
                rxzp__xnepa = context.make_array(types.Array(offset_type, 1,
                    'C'))(context, builder, mnvi__mun.offsets)
                qlw__oovw = builder.bitcast(rxzp__xnepa.data, lir.IntType(8
                    ).as_pointer())
                gyin__ypu = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, mnvi__mun.null_bitmap)
                cnr__qxy = builder.bitcast(gyin__ypu.data, lir.IntType(8).
                    as_pointer())
                obtn__mzw = cgutils.pack_array(builder, [qlw__oovw,
                    cnr__qxy] + [builder.extract_value(aczfe__hpj,
                    dld__kwfly) for dld__kwfly in range(aczfe__hpj.type.count)]
                    )
            elif isinstance(arr_typ, StructArrayType):
                mnvi__mun = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                aczfe__hpj = []
                for dld__kwfly, zqzrg__cuzbh in enumerate(arr_typ.data):
                    iestb__pdpav = get_buffers(zqzrg__cuzbh, builder.
                        extract_value(mnvi__mun.data, dld__kwfly))
                    aczfe__hpj += [builder.extract_value(iestb__pdpav,
                        mdztk__wudq) for mdztk__wudq in range(iestb__pdpav.
                        type.count)]
                gyin__ypu = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, mnvi__mun.null_bitmap)
                cnr__qxy = builder.bitcast(gyin__ypu.data, lir.IntType(8).
                    as_pointer())
                obtn__mzw = cgutils.pack_array(builder, [cnr__qxy] + aczfe__hpj
                    )
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                pptmc__tcg = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    pptmc__tcg = int128_type
                elif arr_typ == datetime_date_array_type:
                    pptmc__tcg = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                qdeug__kcpa = context.make_array(types.Array(pptmc__tcg, 1,
                    'C'))(context, builder, arr.data)
                gyin__ypu = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, arr.null_bitmap)
                andlt__twgz = builder.bitcast(qdeug__kcpa.data, lir.IntType
                    (8).as_pointer())
                cnr__qxy = builder.bitcast(gyin__ypu.data, lir.IntType(8).
                    as_pointer())
                obtn__mzw = cgutils.pack_array(builder, [cnr__qxy, andlt__twgz]
                    )
            elif arr_typ in (string_array_type, binary_array_type):
                mnvi__mun = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                bvvn__tzuvh = context.make_helper(builder, offset_arr_type,
                    mnvi__mun.offsets).data
                nny__tidwm = context.make_helper(builder, char_arr_type,
                    mnvi__mun.data).data
                qambh__sbzf = context.make_helper(builder,
                    null_bitmap_arr_type, mnvi__mun.null_bitmap).data
                obtn__mzw = cgutils.pack_array(builder, [builder.bitcast(
                    bvvn__tzuvh, lir.IntType(8).as_pointer()), builder.
                    bitcast(qambh__sbzf, lir.IntType(8).as_pointer()),
                    builder.bitcast(nny__tidwm, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                andlt__twgz = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                iezh__rhde = lir.Constant(lir.IntType(8).as_pointer(), None)
                obtn__mzw = cgutils.pack_array(builder, [iezh__rhde,
                    andlt__twgz])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return obtn__mzw

        def get_field_names(arr_typ):
            iyhsi__lhcx = []
            if isinstance(arr_typ, StructArrayType):
                for zxmk__jslt, akta__wpcxq in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    iyhsi__lhcx.append(zxmk__jslt)
                    iyhsi__lhcx += get_field_names(akta__wpcxq)
            elif isinstance(arr_typ, ArrayItemArrayType):
                iyhsi__lhcx += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                iyhsi__lhcx += get_field_names(_get_map_arr_data_type(arr_typ))
            return iyhsi__lhcx
        ysy__osmnv = get_types(arr_type)
        kxso__ijaro = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in ysy__osmnv])
        hsfrf__qyon = cgutils.alloca_once_value(builder, kxso__ijaro)
        caq__ruxx = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, caq__ruxx)
        obtn__mzw = get_buffers(arr_type, in_arr)
        rohgg__fecu = cgutils.alloca_once_value(builder, obtn__mzw)
        iyhsi__lhcx = get_field_names(arr_type)
        if len(iyhsi__lhcx) == 0:
            iyhsi__lhcx = ['irrelevant']
        xrit__navgp = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in iyhsi__lhcx])
        njnhf__sulez = cgutils.alloca_once_value(builder, xrit__navgp)
        if isinstance(arr_type, MapArrayType):
            cmzga__duc = _get_map_arr_data_type(arr_type)
            xdr__wts = context.make_helper(builder, arr_type, value=in_arr)
            nzdmj__skcd = xdr__wts.data
        else:
            cmzga__duc = arr_type
            nzdmj__skcd = in_arr
        hvp__zpi = context.make_helper(builder, cmzga__duc, nzdmj__skcd)
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='nested_array_to_info')
        ljxsh__bfo = builder.call(fpjkz__smjg, [builder.bitcast(hsfrf__qyon,
            lir.IntType(32).as_pointer()), builder.bitcast(rohgg__fecu, lir
            .IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            njnhf__sulez, lir.IntType(8).as_pointer()), hvp__zpi.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ljxsh__bfo
    if arr_type in (string_array_type, binary_array_type):
        kpei__iubhp = context.make_helper(builder, arr_type, in_arr)
        yyiqi__rtlek = ArrayItemArrayType(char_arr_type)
        btx__zhct = context.make_helper(builder, yyiqi__rtlek, kpei__iubhp.data
            )
        mnvi__mun = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        bvvn__tzuvh = context.make_helper(builder, offset_arr_type,
            mnvi__mun.offsets).data
        nny__tidwm = context.make_helper(builder, char_arr_type, mnvi__mun.data
            ).data
        qambh__sbzf = context.make_helper(builder, null_bitmap_arr_type,
            mnvi__mun.null_bitmap).data
        kxo__fhk = builder.zext(builder.load(builder.gep(bvvn__tzuvh, [
            mnvi__mun.n_arrays])), lir.IntType(64))
        kupz__gcl = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='string_array_to_info')
        return builder.call(fpjkz__smjg, [mnvi__mun.n_arrays, kxo__fhk,
            nny__tidwm, bvvn__tzuvh, qambh__sbzf, btx__zhct.meminfo, kupz__gcl]
            )
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        mzq__flhk = arr.data
        kti__hzrm = arr.indices
        sig = array_info_type(arr_type.data)
        njeei__iqnj = array_to_info_codegen(context, builder, sig, (
            mzq__flhk,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        ohzk__puz = array_to_info_codegen(context, builder, sig, (kti__hzrm
            ,), False)
        znwk__ssru = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, kti__hzrm)
        cnr__qxy = context.make_array(types.Array(types.uint8, 1, 'C'))(context
            , builder, znwk__ssru.null_bitmap).data
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='dict_str_array_to_info')
        pdbu__diml = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(fpjkz__smjg, [njeei__iqnj, ohzk__puz, builder.
            bitcast(cnr__qxy, lir.IntType(8).as_pointer()), pdbu__diml])
    ngbo__dljqo = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        yfah__ivmsm = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        ihd__intef = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(ihd__intef, 1, 'C')
        ngbo__dljqo = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if ngbo__dljqo:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        silx__dmms = builder.extract_value(arr.shape, 0)
        cks__zklxg = arr_type.dtype
        ous__bte = numba_to_c_type(cks__zklxg)
        chd__xjjg = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ous__bte))
        if ngbo__dljqo:
            jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(64), lir.IntType(8).as_pointer()])
            fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
                jtjw__atwvn, name='categorical_array_to_info')
            return builder.call(fpjkz__smjg, [silx__dmms, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                chd__xjjg), yfah__ivmsm, arr.meminfo])
        else:
            jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer()])
            fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
                jtjw__atwvn, name='numpy_array_to_info')
            return builder.call(fpjkz__smjg, [silx__dmms, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                chd__xjjg), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        cks__zklxg = arr_type.dtype
        pptmc__tcg = cks__zklxg
        if isinstance(arr_type, DecimalArrayType):
            pptmc__tcg = int128_type
        if arr_type == datetime_date_array_type:
            pptmc__tcg = types.int64
        qdeug__kcpa = context.make_array(types.Array(pptmc__tcg, 1, 'C'))(
            context, builder, arr.data)
        silx__dmms = builder.extract_value(qdeug__kcpa.shape, 0)
        mnraw__rtcka = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        ous__bte = numba_to_c_type(cks__zklxg)
        chd__xjjg = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ous__bte))
        if isinstance(arr_type, DecimalArrayType):
            jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer(), lir.IntType(32), lir.
                IntType(32)])
            fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
                jtjw__atwvn, name='decimal_array_to_info')
            return builder.call(fpjkz__smjg, [silx__dmms, builder.bitcast(
                qdeug__kcpa.data, lir.IntType(8).as_pointer()), builder.
                load(chd__xjjg), builder.bitcast(mnraw__rtcka.data, lir.
                IntType(8).as_pointer()), qdeug__kcpa.meminfo, mnraw__rtcka
                .meminfo, context.get_constant(types.int32, arr_type.
                precision), context.get_constant(types.int32, arr_type.scale)])
        else:
            jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer()])
            fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
                jtjw__atwvn, name='nullable_array_to_info')
            return builder.call(fpjkz__smjg, [silx__dmms, builder.bitcast(
                qdeug__kcpa.data, lir.IntType(8).as_pointer()), builder.
                load(chd__xjjg), builder.bitcast(mnraw__rtcka.data, lir.
                IntType(8).as_pointer()), qdeug__kcpa.meminfo, mnraw__rtcka
                .meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        ikj__oeuxf = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        sqcqn__fibf = context.make_array(arr_type.arr_type)(context,
            builder, arr.right)
        silx__dmms = builder.extract_value(ikj__oeuxf.shape, 0)
        ous__bte = numba_to_c_type(arr_type.arr_type.dtype)
        chd__xjjg = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ous__bte))
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='interval_array_to_info')
        return builder.call(fpjkz__smjg, [silx__dmms, builder.bitcast(
            ikj__oeuxf.data, lir.IntType(8).as_pointer()), builder.bitcast(
            sqcqn__fibf.data, lir.IntType(8).as_pointer()), builder.load(
            chd__xjjg), ikj__oeuxf.meminfo, sqcqn__fibf.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    dwa__zjkm = cgutils.alloca_once(builder, lir.IntType(64))
    andlt__twgz = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    wzdkk__dkuw = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    jtjw__atwvn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
        jtjw__atwvn, name='info_to_numpy_array')
    builder.call(fpjkz__smjg, [in_info, dwa__zjkm, andlt__twgz, wzdkk__dkuw])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    mfn__izdoy = context.get_value_type(types.intp)
    jay__jgw = cgutils.pack_array(builder, [builder.load(dwa__zjkm)], ty=
        mfn__izdoy)
    njr__ixyv = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    olq__utwlk = cgutils.pack_array(builder, [njr__ixyv], ty=mfn__izdoy)
    nny__tidwm = builder.bitcast(builder.load(andlt__twgz), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=nny__tidwm, shape=jay__jgw,
        strides=olq__utwlk, itemsize=njr__ixyv, meminfo=builder.load(
        wzdkk__dkuw))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    aqlv__sqjwq = context.make_helper(builder, arr_type)
    jtjw__atwvn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
        jtjw__atwvn, name='info_to_list_string_array')
    builder.call(fpjkz__smjg, [in_info, aqlv__sqjwq._get_ptr_by_name(
        'meminfo')])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return aqlv__sqjwq._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    jek__oszc = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        luq__hieam = lengths_pos
        ypqh__dkyjd = infos_pos
        fxri__ynuz, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        vbrwv__iuyrf = ArrayItemArrayPayloadType(arr_typ)
        utzja__alnlo = context.get_data_type(vbrwv__iuyrf)
        dxh__xfq = context.get_abi_sizeof(utzja__alnlo)
        hutt__puvt = define_array_item_dtor(context, builder, arr_typ,
            vbrwv__iuyrf)
        yerwc__sndof = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, dxh__xfq), hutt__puvt)
        llmrm__cvpli = context.nrt.meminfo_data(builder, yerwc__sndof)
        urids__geci = builder.bitcast(llmrm__cvpli, utzja__alnlo.as_pointer())
        mnvi__mun = cgutils.create_struct_proxy(vbrwv__iuyrf)(context, builder)
        mnvi__mun.n_arrays = builder.extract_value(builder.load(lengths_ptr
            ), luq__hieam)
        mnvi__mun.data = fxri__ynuz
        ojtdb__vpi = builder.load(array_infos_ptr)
        kmyd__nwll = builder.bitcast(builder.extract_value(ojtdb__vpi,
            ypqh__dkyjd), jek__oszc)
        mnvi__mun.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, kmyd__nwll)
        tikf__cbdw = builder.bitcast(builder.extract_value(ojtdb__vpi, 
            ypqh__dkyjd + 1), jek__oszc)
        mnvi__mun.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, tikf__cbdw)
        builder.store(mnvi__mun._getvalue(), urids__geci)
        btx__zhct = context.make_helper(builder, arr_typ)
        btx__zhct.meminfo = yerwc__sndof
        return btx__zhct._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        sgdz__kwubd = []
        ypqh__dkyjd = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for hqfgy__vgrp in arr_typ.data:
            fxri__ynuz, lengths_pos, infos_pos = nested_to_array(context,
                builder, hqfgy__vgrp, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            sgdz__kwubd.append(fxri__ynuz)
        vbrwv__iuyrf = StructArrayPayloadType(arr_typ.data)
        utzja__alnlo = context.get_value_type(vbrwv__iuyrf)
        dxh__xfq = context.get_abi_sizeof(utzja__alnlo)
        hutt__puvt = define_struct_arr_dtor(context, builder, arr_typ,
            vbrwv__iuyrf)
        yerwc__sndof = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, dxh__xfq), hutt__puvt)
        llmrm__cvpli = context.nrt.meminfo_data(builder, yerwc__sndof)
        urids__geci = builder.bitcast(llmrm__cvpli, utzja__alnlo.as_pointer())
        mnvi__mun = cgutils.create_struct_proxy(vbrwv__iuyrf)(context, builder)
        mnvi__mun.data = cgutils.pack_array(builder, sgdz__kwubd
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, sgdz__kwubd)
        ojtdb__vpi = builder.load(array_infos_ptr)
        tikf__cbdw = builder.bitcast(builder.extract_value(ojtdb__vpi,
            ypqh__dkyjd), jek__oszc)
        mnvi__mun.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, tikf__cbdw)
        builder.store(mnvi__mun._getvalue(), urids__geci)
        cdwsy__jpa = context.make_helper(builder, arr_typ)
        cdwsy__jpa.meminfo = yerwc__sndof
        return cdwsy__jpa._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        ojtdb__vpi = builder.load(array_infos_ptr)
        cmk__xozcc = builder.bitcast(builder.extract_value(ojtdb__vpi,
            infos_pos), jek__oszc)
        kpei__iubhp = context.make_helper(builder, arr_typ)
        yyiqi__rtlek = ArrayItemArrayType(char_arr_type)
        btx__zhct = context.make_helper(builder, yyiqi__rtlek)
        jtjw__atwvn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='info_to_string_array')
        builder.call(fpjkz__smjg, [cmk__xozcc, btx__zhct._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        kpei__iubhp.data = btx__zhct._getvalue()
        return kpei__iubhp._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        ojtdb__vpi = builder.load(array_infos_ptr)
        chfv__huk = builder.bitcast(builder.extract_value(ojtdb__vpi, 
            infos_pos + 1), jek__oszc)
        return _lower_info_to_array_numpy(arr_typ, context, builder, chfv__huk
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        pptmc__tcg = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            pptmc__tcg = int128_type
        elif arr_typ == datetime_date_array_type:
            pptmc__tcg = types.int64
        ojtdb__vpi = builder.load(array_infos_ptr)
        tikf__cbdw = builder.bitcast(builder.extract_value(ojtdb__vpi,
            infos_pos), jek__oszc)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, tikf__cbdw)
        chfv__huk = builder.bitcast(builder.extract_value(ojtdb__vpi, 
            infos_pos + 1), jek__oszc)
        arr.data = _lower_info_to_array_numpy(types.Array(pptmc__tcg, 1,
            'C'), context, builder, chfv__huk)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, zvaa__lejqu = args
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
                return 1 + sum([get_num_arrays(hqfgy__vgrp) for hqfgy__vgrp in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(hqfgy__vgrp) for hqfgy__vgrp in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            lfle__ixmy = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            lfle__ixmy = _get_map_arr_data_type(arr_type)
        else:
            lfle__ixmy = arr_type
        eves__kxagb = get_num_arrays(lfle__ixmy)
        caq__ruxx = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), 0) for zvaa__lejqu in range(eves__kxagb)])
        lengths_ptr = cgutils.alloca_once_value(builder, caq__ruxx)
        iezh__rhde = lir.Constant(lir.IntType(8).as_pointer(), None)
        vpm__tfzb = cgutils.pack_array(builder, [iezh__rhde for zvaa__lejqu in
            range(get_num_infos(lfle__ixmy))])
        array_infos_ptr = cgutils.alloca_once_value(builder, vpm__tfzb)
        jtjw__atwvn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='info_to_nested_array')
        builder.call(fpjkz__smjg, [in_info, builder.bitcast(lengths_ptr,
            lir.IntType(64).as_pointer()), builder.bitcast(array_infos_ptr,
            lir.IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, zvaa__lejqu, zvaa__lejqu = nested_to_array(context, builder,
            lfle__ixmy, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            flsk__jvw = context.make_helper(builder, arr_type)
            flsk__jvw.data = arr
            context.nrt.incref(builder, lfle__ixmy, arr)
            arr = flsk__jvw._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, lfle__ixmy)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        kpei__iubhp = context.make_helper(builder, arr_type)
        yyiqi__rtlek = ArrayItemArrayType(char_arr_type)
        btx__zhct = context.make_helper(builder, yyiqi__rtlek)
        jtjw__atwvn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='info_to_string_array')
        builder.call(fpjkz__smjg, [in_info, btx__zhct._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        kpei__iubhp.data = btx__zhct._getvalue()
        return kpei__iubhp._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='get_nested_info')
        njeei__iqnj = builder.call(fpjkz__smjg, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        ohzk__puz = builder.call(fpjkz__smjg, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        vmk__eyfl = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        vmk__eyfl.data = info_to_array_codegen(context, builder, sig, (
            njeei__iqnj, context.get_constant_null(arr_type.data)))
        xsd__woz = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = xsd__woz(array_info_type, xsd__woz)
        vmk__eyfl.indices = info_to_array_codegen(context, builder, sig, (
            ohzk__puz, context.get_constant_null(xsd__woz)))
        jtjw__atwvn = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='get_has_global_dictionary')
        pdbu__diml = builder.call(fpjkz__smjg, [in_info])
        vmk__eyfl.has_global_dictionary = builder.trunc(pdbu__diml, cgutils
            .bool_t)
        return vmk__eyfl._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        ihd__intef = get_categories_int_type(arr_type.dtype)
        hhvf__vuew = types.Array(ihd__intef, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(hhvf__vuew, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            kzsx__scf = bodo.utils.utils.create_categorical_type(arr_type.
                dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(kzsx__scf))
            int_type = arr_type.dtype.int_type
            xing__secl = arr_type.dtype.data.data
            hpjy__agxia = context.get_constant_generic(builder, xing__secl,
                kzsx__scf)
            cks__zklxg = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(xing__secl), [hpjy__agxia])
        else:
            cks__zklxg = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, cks__zklxg)
        out_arr.dtype = cks__zklxg
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        nny__tidwm = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = nny__tidwm
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        pptmc__tcg = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            pptmc__tcg = int128_type
        elif arr_type == datetime_date_array_type:
            pptmc__tcg = types.int64
        ifym__zgoy = types.Array(pptmc__tcg, 1, 'C')
        qdeug__kcpa = context.make_array(ifym__zgoy)(context, builder)
        gvx__fun = types.Array(types.uint8, 1, 'C')
        wboab__sbj = context.make_array(gvx__fun)(context, builder)
        dwa__zjkm = cgutils.alloca_once(builder, lir.IntType(64))
        fpobk__uanua = cgutils.alloca_once(builder, lir.IntType(64))
        andlt__twgz = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        jkfde__okc = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        wzdkk__dkuw = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        rzj__guamt = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        jtjw__atwvn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='info_to_nullable_array')
        builder.call(fpjkz__smjg, [in_info, dwa__zjkm, fpobk__uanua,
            andlt__twgz, jkfde__okc, wzdkk__dkuw, rzj__guamt])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        mfn__izdoy = context.get_value_type(types.intp)
        jay__jgw = cgutils.pack_array(builder, [builder.load(dwa__zjkm)],
            ty=mfn__izdoy)
        njr__ixyv = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(pptmc__tcg)))
        olq__utwlk = cgutils.pack_array(builder, [njr__ixyv], ty=mfn__izdoy)
        nny__tidwm = builder.bitcast(builder.load(andlt__twgz), context.
            get_data_type(pptmc__tcg).as_pointer())
        numba.np.arrayobj.populate_array(qdeug__kcpa, data=nny__tidwm,
            shape=jay__jgw, strides=olq__utwlk, itemsize=njr__ixyv, meminfo
            =builder.load(wzdkk__dkuw))
        arr.data = qdeug__kcpa._getvalue()
        jay__jgw = cgutils.pack_array(builder, [builder.load(fpobk__uanua)],
            ty=mfn__izdoy)
        njr__ixyv = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(types.uint8)))
        olq__utwlk = cgutils.pack_array(builder, [njr__ixyv], ty=mfn__izdoy)
        nny__tidwm = builder.bitcast(builder.load(jkfde__okc), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(wboab__sbj, data=nny__tidwm, shape
            =jay__jgw, strides=olq__utwlk, itemsize=njr__ixyv, meminfo=
            builder.load(rzj__guamt))
        arr.null_bitmap = wboab__sbj._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        ikj__oeuxf = context.make_array(arr_type.arr_type)(context, builder)
        sqcqn__fibf = context.make_array(arr_type.arr_type)(context, builder)
        dwa__zjkm = cgutils.alloca_once(builder, lir.IntType(64))
        abbs__frej = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        iaq__hii = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        tnbjd__acq = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        xrwf__mbma = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        jtjw__atwvn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='info_to_interval_array')
        builder.call(fpjkz__smjg, [in_info, dwa__zjkm, abbs__frej, iaq__hii,
            tnbjd__acq, xrwf__mbma])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        mfn__izdoy = context.get_value_type(types.intp)
        jay__jgw = cgutils.pack_array(builder, [builder.load(dwa__zjkm)],
            ty=mfn__izdoy)
        njr__ixyv = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(arr_type.arr_type.dtype)))
        olq__utwlk = cgutils.pack_array(builder, [njr__ixyv], ty=mfn__izdoy)
        quyj__albye = builder.bitcast(builder.load(abbs__frej), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(ikj__oeuxf, data=quyj__albye,
            shape=jay__jgw, strides=olq__utwlk, itemsize=njr__ixyv, meminfo
            =builder.load(tnbjd__acq))
        arr.left = ikj__oeuxf._getvalue()
        zoxt__igsm = builder.bitcast(builder.load(iaq__hii), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(sqcqn__fibf, data=zoxt__igsm,
            shape=jay__jgw, strides=olq__utwlk, itemsize=njr__ixyv, meminfo
            =builder.load(xrwf__mbma))
        arr.right = sqcqn__fibf._getvalue()
        return arr._getvalue()
    raise_bodo_error(f'info_to_array(): array type {arr_type} is not supported'
        )


@intrinsic
def info_to_array(typingctx, info_type, array_type):
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    assert info_type == array_info_type, 'info_to_array: expected info type'
    return arr_type(info_type, array_type), info_to_array_codegen


@intrinsic
def test_alloc_np(typingctx, len_typ, arr_type):
    array_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type

    def codegen(context, builder, sig, args):
        silx__dmms, zvaa__lejqu = args
        ous__bte = numba_to_c_type(array_type.dtype)
        chd__xjjg = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ous__bte))
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='alloc_numpy')
        return builder.call(fpjkz__smjg, [silx__dmms, builder.load(chd__xjjg)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        silx__dmms, dzpe__himk = args
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='alloc_string_array')
        return builder.call(fpjkz__smjg, [silx__dmms, dzpe__himk])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    rqo__cngn, = args
    oltic__bfqe = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], rqo__cngn)
    jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer().as_pointer(), lir.IntType(64)])
    fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
        jtjw__atwvn, name='arr_info_list_to_table')
    return builder.call(fpjkz__smjg, [oltic__bfqe.data, oltic__bfqe.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='info_from_table')
        return builder.call(fpjkz__smjg, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    dlylb__wvr = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, gfeuz__xspde, zvaa__lejqu = args
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='info_from_table')
        xkhb__xvlw = cgutils.create_struct_proxy(dlylb__wvr)(context, builder)
        xkhb__xvlw.parent = cgutils.get_null_value(xkhb__xvlw.parent.type)
        ohw__gaxz = context.make_array(table_idx_arr_t)(context, builder,
            gfeuz__xspde)
        iaezp__rxuk = context.get_constant(types.int64, -1)
        didny__putq = context.get_constant(types.int64, 0)
        zer__qavlp = cgutils.alloca_once_value(builder, didny__putq)
        for t, mng__lxlu in dlylb__wvr.type_to_blk.items():
            pucp__mxjnr = context.get_constant(types.int64, len(dlylb__wvr.
                block_to_arr_ind[mng__lxlu]))
            zvaa__lejqu, yrad__tqxno = ListInstance.allocate_ex(context,
                builder, types.List(t), pucp__mxjnr)
            yrad__tqxno.size = pucp__mxjnr
            fttf__skzv = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(dlylb__wvr.block_to_arr_ind[
                mng__lxlu], dtype=np.int64))
            shgj__xlef = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, fttf__skzv)
            with cgutils.for_range(builder, pucp__mxjnr) as jhyb__fima:
                dld__kwfly = jhyb__fima.index
                sub__cim = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    shgj__xlef, dld__kwfly)
                gdlhj__ymjgh = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, ohw__gaxz, sub__cim)
                gqxhn__nzqsy = builder.icmp_unsigned('!=', gdlhj__ymjgh,
                    iaezp__rxuk)
                with builder.if_else(gqxhn__nzqsy) as (pidcy__upx, nuv__hhwzd):
                    with pidcy__upx:
                        ziccm__dca = builder.call(fpjkz__smjg, [cpp_table,
                            gdlhj__ymjgh])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            ziccm__dca])
                        yrad__tqxno.inititem(dld__kwfly, arr, incref=False)
                        silx__dmms = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(silx__dmms, zer__qavlp)
                    with nuv__hhwzd:
                        ihfui__ieiw = context.get_constant_null(t)
                        yrad__tqxno.inititem(dld__kwfly, ihfui__ieiw,
                            incref=False)
            setattr(xkhb__xvlw, f'block_{mng__lxlu}', yrad__tqxno.value)
        xkhb__xvlw.len = builder.load(zer__qavlp)
        return xkhb__xvlw._getvalue()
    return dlylb__wvr(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t):
    bxmww__uotm = out_col_inds_t.instance_type.meta
    dlylb__wvr = unwrap_typeref(out_types_t.types[0])
    rznr__amsmt = [unwrap_typeref(out_types_t.types[dld__kwfly]) for
        dld__kwfly in range(1, len(out_types_t.types))]
    paqj__khwh = {}
    ajfkt__wzqqj = get_overload_const_int(n_table_cols_t)
    miltm__esjv = {heb__mvnd: dld__kwfly for dld__kwfly, heb__mvnd in
        enumerate(bxmww__uotm)}
    ifm__obgnr = (
        'def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t):\n'
        )
    if dlylb__wvr == types.none:
        ifm__obgnr += f'  py_table = None\n'
    else:
        ifm__obgnr += f'  py_table = init_table(py_table_type, False)\n'
        ifm__obgnr += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for aqptl__olcj, mng__lxlu in dlylb__wvr.type_to_blk.items():
            pvqg__mwh = [miltm__esjv.get(dld__kwfly, -1) for dld__kwfly in
                dlylb__wvr.block_to_arr_ind[mng__lxlu]]
            paqj__khwh[f'out_inds_{mng__lxlu}'] = np.array(pvqg__mwh, np.int64)
            paqj__khwh[f'out_type_{mng__lxlu}'] = aqptl__olcj
            paqj__khwh[f'typ_list_{mng__lxlu}'] = types.List(aqptl__olcj)
            daoqm__iyj = f'out_type_{mng__lxlu}'
            if type_has_unknown_cats(aqptl__olcj):
                ifm__obgnr += f"""  in_arr_list_{mng__lxlu} = get_table_block(out_types_t[0], {mng__lxlu})
"""
                daoqm__iyj = f'in_arr_list_{mng__lxlu}[i]'
            pucp__mxjnr = len(dlylb__wvr.block_to_arr_ind[mng__lxlu])
            ifm__obgnr += f"""  arr_list_{mng__lxlu} = alloc_list_like(typ_list_{mng__lxlu}, {pucp__mxjnr}, False)
"""
            ifm__obgnr += f'  for i in range(len(arr_list_{mng__lxlu})):\n'
            ifm__obgnr += (
                f'    cpp_ind_{mng__lxlu} = out_inds_{mng__lxlu}[i]\n')
            ifm__obgnr += f'    if cpp_ind_{mng__lxlu} == -1:\n'
            ifm__obgnr += f'      continue\n'
            ifm__obgnr += f"""    arr_{mng__lxlu} = info_to_array(info_from_table(cpp_table, cpp_ind_{mng__lxlu}), {daoqm__iyj})
"""
            ifm__obgnr += f'    arr_list_{mng__lxlu}[i] = arr_{mng__lxlu}\n'
            ifm__obgnr += f"""  py_table = set_table_block(py_table, arr_list_{mng__lxlu}, {mng__lxlu})
"""
    lbxd__kjo = []
    for dld__kwfly, t in enumerate(rznr__amsmt):
        awh__fth = miltm__esjv.get(ajfkt__wzqqj + dld__kwfly, -1)
        if awh__fth != -1:
            paqj__khwh[f'extra_arr_type_{dld__kwfly}'] = t
            daoqm__iyj = f'extra_arr_type_{dld__kwfly}'
            if type_has_unknown_cats(t):
                daoqm__iyj = f'out_types_t[{dld__kwfly + 1}]'
            ifm__obgnr += f"""  out_{dld__kwfly} = info_to_array(info_from_table(cpp_table, {awh__fth}), {daoqm__iyj})
"""
            lbxd__kjo.append(f'out_{dld__kwfly}')
    if dlylb__wvr != types.none:
        ifm__obgnr += f"  return (py_table, {', '.join(lbxd__kjo)})\n"
    else:
        zmme__jtw = ',' if len(lbxd__kjo) == 1 else ''
        ifm__obgnr += f"  return ({', '.join(lbxd__kjo)}{zmme__jtw})\n"
    paqj__khwh.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(bxmww__uotm), 'py_table_type': dlylb__wvr})
    ktfml__ncqt = {}
    exec(ifm__obgnr, paqj__khwh, ktfml__ncqt)
    return ktfml__ncqt['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    dlylb__wvr = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, zvaa__lejqu = args
        aqnh__mbxo = cgutils.create_struct_proxy(dlylb__wvr)(context,
            builder, py_table)
        if dlylb__wvr.has_runtime_cols:
            txr__xva = lir.Constant(lir.IntType(64), 0)
            for mng__lxlu, t in enumerate(dlylb__wvr.arr_types):
                sukci__rhum = getattr(aqnh__mbxo, f'block_{mng__lxlu}')
                unpip__eejr = ListInstance(context, builder, types.List(t),
                    sukci__rhum)
                txr__xva = builder.add(txr__xva, unpip__eejr.size)
        else:
            txr__xva = lir.Constant(lir.IntType(64), len(dlylb__wvr.arr_types))
        zvaa__lejqu, abom__ycr = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), txr__xva)
        abom__ycr.size = txr__xva
        if dlylb__wvr.has_runtime_cols:
            knd__prlsl = lir.Constant(lir.IntType(64), 0)
            for mng__lxlu, t in enumerate(dlylb__wvr.arr_types):
                sukci__rhum = getattr(aqnh__mbxo, f'block_{mng__lxlu}')
                unpip__eejr = ListInstance(context, builder, types.List(t),
                    sukci__rhum)
                pucp__mxjnr = unpip__eejr.size
                with cgutils.for_range(builder, pucp__mxjnr) as jhyb__fima:
                    dld__kwfly = jhyb__fima.index
                    arr = unpip__eejr.getitem(dld__kwfly)
                    iitn__vrw = signature(array_info_type, t)
                    dbs__mhm = arr,
                    trbz__ygdu = array_to_info_codegen(context, builder,
                        iitn__vrw, dbs__mhm)
                    abom__ycr.inititem(builder.add(knd__prlsl, dld__kwfly),
                        trbz__ygdu, incref=False)
                knd__prlsl = builder.add(knd__prlsl, pucp__mxjnr)
        else:
            for t, mng__lxlu in dlylb__wvr.type_to_blk.items():
                pucp__mxjnr = context.get_constant(types.int64, len(
                    dlylb__wvr.block_to_arr_ind[mng__lxlu]))
                sukci__rhum = getattr(aqnh__mbxo, f'block_{mng__lxlu}')
                unpip__eejr = ListInstance(context, builder, types.List(t),
                    sukci__rhum)
                fttf__skzv = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(dlylb__wvr.
                    block_to_arr_ind[mng__lxlu], dtype=np.int64))
                shgj__xlef = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, fttf__skzv)
                with cgutils.for_range(builder, pucp__mxjnr) as jhyb__fima:
                    dld__kwfly = jhyb__fima.index
                    sub__cim = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        shgj__xlef, dld__kwfly)
                    gbbo__azz = signature(types.none, dlylb__wvr, types.
                        List(t), types.int64, types.int64)
                    bcci__jrc = py_table, sukci__rhum, dld__kwfly, sub__cim
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, gbbo__azz, bcci__jrc)
                    arr = unpip__eejr.getitem(dld__kwfly)
                    iitn__vrw = signature(array_info_type, t)
                    dbs__mhm = arr,
                    trbz__ygdu = array_to_info_codegen(context, builder,
                        iitn__vrw, dbs__mhm)
                    abom__ycr.inititem(sub__cim, trbz__ygdu, incref=False)
        gel__pff = abom__ycr.value
        swlv__eqwoq = signature(table_type, types.List(array_info_type))
        lfyy__hbnt = gel__pff,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            swlv__eqwoq, lfyy__hbnt)
        context.nrt.decref(builder, types.List(array_info_type), gel__pff)
        return cpp_table
    return table_type(dlylb__wvr, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    nrj__vmziw = in_col_inds_t.instance_type.meta
    paqj__khwh = {}
    ajfkt__wzqqj = get_overload_const_int(n_table_cols_t)
    xce__chui = defaultdict(list)
    miltm__esjv = {}
    for dld__kwfly, heb__mvnd in enumerate(nrj__vmziw):
        if heb__mvnd in miltm__esjv:
            xce__chui[heb__mvnd].append(dld__kwfly)
        else:
            miltm__esjv[heb__mvnd] = dld__kwfly
    ifm__obgnr = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    ifm__obgnr += (
        f'  cpp_arr_list = alloc_empty_list_type({len(nrj__vmziw)}, array_info_type)\n'
        )
    if py_table != types.none:
        for mng__lxlu in py_table.type_to_blk.values():
            pvqg__mwh = [miltm__esjv.get(dld__kwfly, -1) for dld__kwfly in
                py_table.block_to_arr_ind[mng__lxlu]]
            paqj__khwh[f'out_inds_{mng__lxlu}'] = np.array(pvqg__mwh, np.int64)
            paqj__khwh[f'arr_inds_{mng__lxlu}'] = np.array(py_table.
                block_to_arr_ind[mng__lxlu], np.int64)
            ifm__obgnr += (
                f'  arr_list_{mng__lxlu} = get_table_block(py_table, {mng__lxlu})\n'
                )
            ifm__obgnr += f'  for i in range(len(arr_list_{mng__lxlu})):\n'
            ifm__obgnr += (
                f'    out_arr_ind_{mng__lxlu} = out_inds_{mng__lxlu}[i]\n')
            ifm__obgnr += f'    if out_arr_ind_{mng__lxlu} == -1:\n'
            ifm__obgnr += f'      continue\n'
            ifm__obgnr += (
                f'    arr_ind_{mng__lxlu} = arr_inds_{mng__lxlu}[i]\n')
            ifm__obgnr += f"""    ensure_column_unboxed(py_table, arr_list_{mng__lxlu}, i, arr_ind_{mng__lxlu})
"""
            ifm__obgnr += f"""    cpp_arr_list[out_arr_ind_{mng__lxlu}] = array_to_info(arr_list_{mng__lxlu}[i])
"""
        for rvogg__rejrw, dorn__qvnwp in xce__chui.items():
            if rvogg__rejrw < ajfkt__wzqqj:
                mng__lxlu = py_table.block_nums[rvogg__rejrw]
                borih__ykne = py_table.block_offsets[rvogg__rejrw]
                for awh__fth in dorn__qvnwp:
                    ifm__obgnr += f"""  cpp_arr_list[{awh__fth}] = array_to_info(arr_list_{mng__lxlu}[{borih__ykne}])
"""
    for dld__kwfly in range(len(extra_arrs_tup)):
        pcxz__ghe = miltm__esjv.get(ajfkt__wzqqj + dld__kwfly, -1)
        if pcxz__ghe != -1:
            geg__xbjrt = [pcxz__ghe] + xce__chui.get(ajfkt__wzqqj +
                dld__kwfly, [])
            for awh__fth in geg__xbjrt:
                ifm__obgnr += f"""  cpp_arr_list[{awh__fth}] = array_to_info(extra_arrs_tup[{dld__kwfly}])
"""
    ifm__obgnr += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    paqj__khwh.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    ktfml__ncqt = {}
    exec(ifm__obgnr, paqj__khwh, ktfml__ncqt)
    return ktfml__ncqt['impl']


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        jtjw__atwvn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='delete_table')
        builder.call(fpjkz__smjg, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='shuffle_table')
        ljxsh__bfo = builder.call(fpjkz__smjg, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ljxsh__bfo
    return table_type(table_t, types.int64, types.boolean, types.int32
        ), codegen


class ShuffleInfoType(types.Type):

    def __init__(self):
        super(ShuffleInfoType, self).__init__(name='ShuffleInfoType()')


shuffle_info_type = ShuffleInfoType()
register_model(ShuffleInfoType)(models.OpaqueModel)
get_shuffle_info = types.ExternalFunction('get_shuffle_info',
    shuffle_info_type(table_type))


@intrinsic
def delete_shuffle_info(typingctx, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[0] == types.none:
            return
        jtjw__atwvn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='delete_shuffle_info')
        return builder.call(fpjkz__smjg, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='reverse_shuffle_table')
        return builder.call(fpjkz__smjg, args)
    return table_type(table_type, shuffle_info_t), codegen


@intrinsic
def get_null_shuffle_info(typingctx):

    def codegen(context, builder, sig, args):
        return context.get_constant_null(sig.return_type)
    return shuffle_info_type(), codegen


@intrinsic
def hash_join_table(typingctx, left_table_t, right_table_t, left_parallel_t,
    right_parallel_t, n_keys_t, n_data_left_t, n_data_right_t, same_vect_t,
    key_in_out_t, same_need_typechange_t, is_left_t, is_right_t, is_join_t,
    extra_data_col_t, indicator, _bodo_na_equal, cond_func, left_col_nums,
    left_col_nums_len, right_col_nums, right_col_nums_len, num_rows_ptr_t):
    assert left_table_t == table_type
    assert right_table_t == table_type

    def codegen(context, builder, sig, args):
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='hash_join_table')
        ljxsh__bfo = builder.call(fpjkz__smjg, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ljxsh__bfo
    return table_type(left_table_t, right_table_t, types.boolean, types.
        boolean, types.int64, types.int64, types.int64, types.voidptr,
        types.voidptr, types.voidptr, types.boolean, types.boolean, types.
        boolean, types.boolean, types.boolean, types.boolean, types.voidptr,
        types.voidptr, types.int64, types.voidptr, types.int64, types.voidptr
        ), codegen


@intrinsic
def sort_values_table(typingctx, table_t, n_keys_t, vect_ascending_t,
    na_position_b_t, dead_keys_t, n_rows_t, parallel_t):
    assert table_t == table_type, 'C++ table type expected'

    def codegen(context, builder, sig, args):
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='sort_values_table')
        ljxsh__bfo = builder.call(fpjkz__smjg, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ljxsh__bfo
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='sample_table')
        ljxsh__bfo = builder.call(fpjkz__smjg, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ljxsh__bfo
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='shuffle_renormalization')
        ljxsh__bfo = builder.call(fpjkz__smjg, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ljxsh__bfo
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='shuffle_renormalization_group')
        ljxsh__bfo = builder.call(fpjkz__smjg, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ljxsh__bfo
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='drop_duplicates_table')
        ljxsh__bfo = builder.call(fpjkz__smjg, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ljxsh__bfo
    return table_type(table_t, types.boolean, types.int64, types.int64,
        types.boolean, types.boolean), codegen


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
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='pivot_groupby_and_aggregate')
        ljxsh__bfo = builder.call(fpjkz__smjg, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ljxsh__bfo
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
        jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        fpjkz__smjg = cgutils.get_or_insert_function(builder.module,
            jtjw__atwvn, name='groupby_and_aggregate')
        ljxsh__bfo = builder.call(fpjkz__smjg, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ljxsh__bfo
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


@numba.njit(no_cpython_wrapper=True)
def array_isin(out_arr, in_arr, in_values, is_parallel):
    in_arr = decode_if_dict_array(in_arr)
    in_values = decode_if_dict_array(in_values)
    eckso__ywvzb = array_to_info(in_arr)
    jno__icwf = array_to_info(in_values)
    vpmr__fezpk = array_to_info(out_arr)
    xzj__imx = arr_info_list_to_table([eckso__ywvzb, jno__icwf, vpmr__fezpk])
    _array_isin(vpmr__fezpk, eckso__ywvzb, jno__icwf, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(xzj__imx)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, pat, out_arr):
    eckso__ywvzb = array_to_info(in_arr)
    vpmr__fezpk = array_to_info(out_arr)
    _get_search_regex(eckso__ywvzb, case, pat, vpmr__fezpk)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    nivqx__giew = col_array_typ.dtype
    if isinstance(nivqx__giew, types.Number) or nivqx__giew in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                xkhb__xvlw, fwt__xgmc = args
                xkhb__xvlw = builder.bitcast(xkhb__xvlw, lir.IntType(8).
                    as_pointer().as_pointer())
                zumlv__qylsb = lir.Constant(lir.IntType(64), c_ind)
                fse__kgy = builder.load(builder.gep(xkhb__xvlw, [zumlv__qylsb])
                    )
                fse__kgy = builder.bitcast(fse__kgy, context.get_data_type(
                    nivqx__giew).as_pointer())
                return builder.load(builder.gep(fse__kgy, [fwt__xgmc]))
            return nivqx__giew(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.string_array_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                xkhb__xvlw, fwt__xgmc = args
                xkhb__xvlw = builder.bitcast(xkhb__xvlw, lir.IntType(8).
                    as_pointer().as_pointer())
                zumlv__qylsb = lir.Constant(lir.IntType(64), c_ind)
                fse__kgy = builder.load(builder.gep(xkhb__xvlw, [zumlv__qylsb])
                    )
                jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                len__tlw = cgutils.get_or_insert_function(builder.module,
                    jtjw__atwvn, name='array_info_getitem')
                vqr__fojmu = cgutils.alloca_once(builder, lir.IntType(64))
                args = fse__kgy, fwt__xgmc, vqr__fojmu
                andlt__twgz = builder.call(len__tlw, args)
                return context.make_tuple(builder, sig.return_type, [
                    andlt__twgz, builder.load(vqr__fojmu)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                jvd__cvji = lir.Constant(lir.IntType(64), 1)
                tckyb__wlsp = lir.Constant(lir.IntType(64), 2)
                xkhb__xvlw, fwt__xgmc = args
                xkhb__xvlw = builder.bitcast(xkhb__xvlw, lir.IntType(8).
                    as_pointer().as_pointer())
                zumlv__qylsb = lir.Constant(lir.IntType(64), c_ind)
                fse__kgy = builder.load(builder.gep(xkhb__xvlw, [zumlv__qylsb])
                    )
                jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64)])
                vri__ajzqm = cgutils.get_or_insert_function(builder.module,
                    jtjw__atwvn, name='get_nested_info')
                args = fse__kgy, tckyb__wlsp
                dxyho__kai = builder.call(vri__ajzqm, args)
                jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer()])
                aljiu__rgl = cgutils.get_or_insert_function(builder.module,
                    jtjw__atwvn, name='array_info_getdata1')
                args = dxyho__kai,
                ipyjv__hpwt = builder.call(aljiu__rgl, args)
                ipyjv__hpwt = builder.bitcast(ipyjv__hpwt, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                pbzah__acrqn = builder.sext(builder.load(builder.gep(
                    ipyjv__hpwt, [fwt__xgmc])), lir.IntType(64))
                args = fse__kgy, jvd__cvji
                jej__cdej = builder.call(vri__ajzqm, args)
                jtjw__atwvn = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                len__tlw = cgutils.get_or_insert_function(builder.module,
                    jtjw__atwvn, name='array_info_getitem')
                vqr__fojmu = cgutils.alloca_once(builder, lir.IntType(64))
                args = jej__cdej, pbzah__acrqn, vqr__fojmu
                andlt__twgz = builder.call(len__tlw, args)
                return context.make_tuple(builder, sig.return_type, [
                    andlt__twgz, builder.load(vqr__fojmu)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{nivqx__giew}' column data type not supported"
        )


def _gen_row_na_check_intrinsic(col_array_dtype, c_ind):
    if (isinstance(col_array_dtype, bodo.libs.int_arr_ext.IntegerArrayType) or
        col_array_dtype == bodo.libs.bool_arr_ext.boolean_array or
        is_str_arr_type(col_array_dtype) or isinstance(col_array_dtype,
        types.Array) and col_array_dtype.dtype == bodo.datetime_date_type):

        @intrinsic
        def checkna_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                xpzof__yzcu, fwt__xgmc = args
                xpzof__yzcu = builder.bitcast(xpzof__yzcu, lir.IntType(8).
                    as_pointer().as_pointer())
                zumlv__qylsb = lir.Constant(lir.IntType(64), c_ind)
                fse__kgy = builder.load(builder.gep(xpzof__yzcu, [
                    zumlv__qylsb]))
                qambh__sbzf = builder.bitcast(fse__kgy, context.
                    get_data_type(types.bool_).as_pointer())
                jtq__tnjhn = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    qambh__sbzf, fwt__xgmc)
                jok__hbkr = builder.icmp_unsigned('!=', jtq__tnjhn, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(jok__hbkr, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        nivqx__giew = col_array_dtype.dtype
        if nivqx__giew in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    xkhb__xvlw, fwt__xgmc = args
                    xkhb__xvlw = builder.bitcast(xkhb__xvlw, lir.IntType(8)
                        .as_pointer().as_pointer())
                    zumlv__qylsb = lir.Constant(lir.IntType(64), c_ind)
                    fse__kgy = builder.load(builder.gep(xkhb__xvlw, [
                        zumlv__qylsb]))
                    fse__kgy = builder.bitcast(fse__kgy, context.
                        get_data_type(nivqx__giew).as_pointer())
                    fwg__bpjov = builder.load(builder.gep(fse__kgy, [
                        fwt__xgmc]))
                    jok__hbkr = builder.icmp_unsigned('!=', fwg__bpjov, lir
                        .Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(jok__hbkr, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(nivqx__giew, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    xkhb__xvlw, fwt__xgmc = args
                    xkhb__xvlw = builder.bitcast(xkhb__xvlw, lir.IntType(8)
                        .as_pointer().as_pointer())
                    zumlv__qylsb = lir.Constant(lir.IntType(64), c_ind)
                    fse__kgy = builder.load(builder.gep(xkhb__xvlw, [
                        zumlv__qylsb]))
                    fse__kgy = builder.bitcast(fse__kgy, context.
                        get_data_type(nivqx__giew).as_pointer())
                    fwg__bpjov = builder.load(builder.gep(fse__kgy, [
                        fwt__xgmc]))
                    izzea__urzw = signature(types.bool_, nivqx__giew)
                    jtq__tnjhn = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, izzea__urzw, (fwg__bpjov,))
                    return builder.not_(builder.sext(jtq__tnjhn, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
