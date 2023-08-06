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
        misam__aqljo = context.make_helper(builder, arr_type, in_arr)
        in_arr = misam__aqljo.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        spzy__vbs = context.make_helper(builder, arr_type, in_arr)
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='list_string_array_to_info')
        return builder.call(jqkrq__wjpz, [spzy__vbs.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                smb__hig = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for clcev__zqp in arr_typ.data:
                    smb__hig += get_types(clcev__zqp)
                return smb__hig
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
            cphj__svahz = context.compile_internal(builder, lambda a: len(a
                ), types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                mxjqq__uote = context.make_helper(builder, arr_typ, value=arr)
                osiq__zcy = get_lengths(_get_map_arr_data_type(arr_typ),
                    mxjqq__uote.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                gcbo__tioe = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                osiq__zcy = get_lengths(arr_typ.dtype, gcbo__tioe.data)
                osiq__zcy = cgutils.pack_array(builder, [gcbo__tioe.
                    n_arrays] + [builder.extract_value(osiq__zcy,
                    lzf__lttrc) for lzf__lttrc in range(osiq__zcy.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                gcbo__tioe = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                osiq__zcy = []
                for lzf__lttrc, clcev__zqp in enumerate(arr_typ.data):
                    ukr__nntqu = get_lengths(clcev__zqp, builder.
                        extract_value(gcbo__tioe.data, lzf__lttrc))
                    osiq__zcy += [builder.extract_value(ukr__nntqu,
                        ygby__icrsf) for ygby__icrsf in range(ukr__nntqu.
                        type.count)]
                osiq__zcy = cgutils.pack_array(builder, [cphj__svahz,
                    context.get_constant(types.int64, -1)] + osiq__zcy)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                osiq__zcy = cgutils.pack_array(builder, [cphj__svahz])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return osiq__zcy

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                mxjqq__uote = context.make_helper(builder, arr_typ, value=arr)
                mgpx__opb = get_buffers(_get_map_arr_data_type(arr_typ),
                    mxjqq__uote.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                gcbo__tioe = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                cqxs__wgftr = get_buffers(arr_typ.dtype, gcbo__tioe.data)
                vek__zyi = context.make_array(types.Array(offset_type, 1, 'C')
                    )(context, builder, gcbo__tioe.offsets)
                ohn__qnrcg = builder.bitcast(vek__zyi.data, lir.IntType(8).
                    as_pointer())
                mhmn__fvb = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, gcbo__tioe.null_bitmap)
                phihm__aherv = builder.bitcast(mhmn__fvb.data, lir.IntType(
                    8).as_pointer())
                mgpx__opb = cgutils.pack_array(builder, [ohn__qnrcg,
                    phihm__aherv] + [builder.extract_value(cqxs__wgftr,
                    lzf__lttrc) for lzf__lttrc in range(cqxs__wgftr.type.
                    count)])
            elif isinstance(arr_typ, StructArrayType):
                gcbo__tioe = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                cqxs__wgftr = []
                for lzf__lttrc, clcev__zqp in enumerate(arr_typ.data):
                    gjqht__ckg = get_buffers(clcev__zqp, builder.
                        extract_value(gcbo__tioe.data, lzf__lttrc))
                    cqxs__wgftr += [builder.extract_value(gjqht__ckg,
                        ygby__icrsf) for ygby__icrsf in range(gjqht__ckg.
                        type.count)]
                mhmn__fvb = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, gcbo__tioe.null_bitmap)
                phihm__aherv = builder.bitcast(mhmn__fvb.data, lir.IntType(
                    8).as_pointer())
                mgpx__opb = cgutils.pack_array(builder, [phihm__aherv] +
                    cqxs__wgftr)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                plub__klz = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    plub__klz = int128_type
                elif arr_typ == datetime_date_array_type:
                    plub__klz = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                sqljq__kuaw = context.make_array(types.Array(plub__klz, 1, 'C')
                    )(context, builder, arr.data)
                mhmn__fvb = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, arr.null_bitmap)
                vgla__hraox = builder.bitcast(sqljq__kuaw.data, lir.IntType
                    (8).as_pointer())
                phihm__aherv = builder.bitcast(mhmn__fvb.data, lir.IntType(
                    8).as_pointer())
                mgpx__opb = cgutils.pack_array(builder, [phihm__aherv,
                    vgla__hraox])
            elif arr_typ in (string_array_type, binary_array_type):
                gcbo__tioe = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                sudcb__kewxh = context.make_helper(builder, offset_arr_type,
                    gcbo__tioe.offsets).data
                emlsq__fzwf = context.make_helper(builder, char_arr_type,
                    gcbo__tioe.data).data
                bpn__xudhr = context.make_helper(builder,
                    null_bitmap_arr_type, gcbo__tioe.null_bitmap).data
                mgpx__opb = cgutils.pack_array(builder, [builder.bitcast(
                    sudcb__kewxh, lir.IntType(8).as_pointer()), builder.
                    bitcast(bpn__xudhr, lir.IntType(8).as_pointer()),
                    builder.bitcast(emlsq__fzwf, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                vgla__hraox = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                wtj__izm = lir.Constant(lir.IntType(8).as_pointer(), None)
                mgpx__opb = cgutils.pack_array(builder, [wtj__izm, vgla__hraox]
                    )
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return mgpx__opb

        def get_field_names(arr_typ):
            vjen__hvdmb = []
            if isinstance(arr_typ, StructArrayType):
                for gfz__ztoxb, zea__uazpc in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    vjen__hvdmb.append(gfz__ztoxb)
                    vjen__hvdmb += get_field_names(zea__uazpc)
            elif isinstance(arr_typ, ArrayItemArrayType):
                vjen__hvdmb += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                vjen__hvdmb += get_field_names(_get_map_arr_data_type(arr_typ))
            return vjen__hvdmb
        smb__hig = get_types(arr_type)
        cclt__ywjce = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in smb__hig])
        dqvmj__fgjm = cgutils.alloca_once_value(builder, cclt__ywjce)
        osiq__zcy = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, osiq__zcy)
        mgpx__opb = get_buffers(arr_type, in_arr)
        dtcv__qzfl = cgutils.alloca_once_value(builder, mgpx__opb)
        vjen__hvdmb = get_field_names(arr_type)
        if len(vjen__hvdmb) == 0:
            vjen__hvdmb = ['irrelevant']
        uuwh__gmb = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in vjen__hvdmb])
        lrqmt__qnv = cgutils.alloca_once_value(builder, uuwh__gmb)
        if isinstance(arr_type, MapArrayType):
            qvadq__auc = _get_map_arr_data_type(arr_type)
            nsmt__yhq = context.make_helper(builder, arr_type, value=in_arr)
            izlj__ehqa = nsmt__yhq.data
        else:
            qvadq__auc = arr_type
            izlj__ehqa = in_arr
        ucaq__wrb = context.make_helper(builder, qvadq__auc, izlj__ehqa)
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='nested_array_to_info')
        ngmoz__waovg = builder.call(jqkrq__wjpz, [builder.bitcast(
            dqvmj__fgjm, lir.IntType(32).as_pointer()), builder.bitcast(
            dtcv__qzfl, lir.IntType(8).as_pointer().as_pointer()), builder.
            bitcast(lengths_ptr, lir.IntType(64).as_pointer()), builder.
            bitcast(lrqmt__qnv, lir.IntType(8).as_pointer()), ucaq__wrb.
            meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ngmoz__waovg
    if arr_type in (string_array_type, binary_array_type):
        orrmp__kwx = context.make_helper(builder, arr_type, in_arr)
        qjo__fcr = ArrayItemArrayType(char_arr_type)
        spzy__vbs = context.make_helper(builder, qjo__fcr, orrmp__kwx.data)
        gcbo__tioe = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        sudcb__kewxh = context.make_helper(builder, offset_arr_type,
            gcbo__tioe.offsets).data
        emlsq__fzwf = context.make_helper(builder, char_arr_type,
            gcbo__tioe.data).data
        bpn__xudhr = context.make_helper(builder, null_bitmap_arr_type,
            gcbo__tioe.null_bitmap).data
        thkr__suqc = builder.zext(builder.load(builder.gep(sudcb__kewxh, [
            gcbo__tioe.n_arrays])), lir.IntType(64))
        bgc__lmfbc = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='string_array_to_info')
        return builder.call(jqkrq__wjpz, [gcbo__tioe.n_arrays, thkr__suqc,
            emlsq__fzwf, sudcb__kewxh, bpn__xudhr, spzy__vbs.meminfo,
            bgc__lmfbc])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        llc__sekfh = arr.data
        dxsij__kpj = arr.indices
        sig = array_info_type(arr_type.data)
        jjtmv__mfnbw = array_to_info_codegen(context, builder, sig, (
            llc__sekfh,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        zir__leic = array_to_info_codegen(context, builder, sig, (
            dxsij__kpj,), False)
        nfmge__num = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, dxsij__kpj)
        phihm__aherv = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, nfmge__num.null_bitmap).data
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='dict_str_array_to_info')
        sdz__zvfys = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(jqkrq__wjpz, [jjtmv__mfnbw, zir__leic, builder.
            bitcast(phihm__aherv, lir.IntType(8).as_pointer()), sdz__zvfys])
    qmq__fdtdm = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        gzex__nnzqv = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        iqhyi__buak = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(iqhyi__buak, 1, 'C')
        qmq__fdtdm = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if qmq__fdtdm:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        cphj__svahz = builder.extract_value(arr.shape, 0)
        ocbne__btrzq = arr_type.dtype
        joxd__ragsb = numba_to_c_type(ocbne__btrzq)
        dvko__nhwb = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), joxd__ragsb))
        if qmq__fdtdm:
            dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
                dfg__khsvv, name='categorical_array_to_info')
            return builder.call(jqkrq__wjpz, [cphj__svahz, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                dvko__nhwb), gzex__nnzqv, arr.meminfo])
        else:
            dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
                dfg__khsvv, name='numpy_array_to_info')
            return builder.call(jqkrq__wjpz, [cphj__svahz, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                dvko__nhwb), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        ocbne__btrzq = arr_type.dtype
        plub__klz = ocbne__btrzq
        if isinstance(arr_type, DecimalArrayType):
            plub__klz = int128_type
        if arr_type == datetime_date_array_type:
            plub__klz = types.int64
        sqljq__kuaw = context.make_array(types.Array(plub__klz, 1, 'C'))(
            context, builder, arr.data)
        cphj__svahz = builder.extract_value(sqljq__kuaw.shape, 0)
        qtdh__wvzx = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        joxd__ragsb = numba_to_c_type(ocbne__btrzq)
        dvko__nhwb = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), joxd__ragsb))
        if isinstance(arr_type, DecimalArrayType):
            dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
                dfg__khsvv, name='decimal_array_to_info')
            return builder.call(jqkrq__wjpz, [cphj__svahz, builder.bitcast(
                sqljq__kuaw.data, lir.IntType(8).as_pointer()), builder.
                load(dvko__nhwb), builder.bitcast(qtdh__wvzx.data, lir.
                IntType(8).as_pointer()), sqljq__kuaw.meminfo, qtdh__wvzx.
                meminfo, context.get_constant(types.int32, arr_type.
                precision), context.get_constant(types.int32, arr_type.scale)])
        else:
            dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
                dfg__khsvv, name='nullable_array_to_info')
            return builder.call(jqkrq__wjpz, [cphj__svahz, builder.bitcast(
                sqljq__kuaw.data, lir.IntType(8).as_pointer()), builder.
                load(dvko__nhwb), builder.bitcast(qtdh__wvzx.data, lir.
                IntType(8).as_pointer()), sqljq__kuaw.meminfo, qtdh__wvzx.
                meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        day__unpdl = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        sqwe__ldlw = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        cphj__svahz = builder.extract_value(day__unpdl.shape, 0)
        joxd__ragsb = numba_to_c_type(arr_type.arr_type.dtype)
        dvko__nhwb = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), joxd__ragsb))
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='interval_array_to_info')
        return builder.call(jqkrq__wjpz, [cphj__svahz, builder.bitcast(
            day__unpdl.data, lir.IntType(8).as_pointer()), builder.bitcast(
            sqwe__ldlw.data, lir.IntType(8).as_pointer()), builder.load(
            dvko__nhwb), day__unpdl.meminfo, sqwe__ldlw.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    zassd__uyi = cgutils.alloca_once(builder, lir.IntType(64))
    vgla__hraox = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    nvni__vzykl = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    dfg__khsvv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    jqkrq__wjpz = cgutils.get_or_insert_function(builder.module, dfg__khsvv,
        name='info_to_numpy_array')
    builder.call(jqkrq__wjpz, [in_info, zassd__uyi, vgla__hraox, nvni__vzykl])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    qlnz__njun = context.get_value_type(types.intp)
    qksiy__chpe = cgutils.pack_array(builder, [builder.load(zassd__uyi)],
        ty=qlnz__njun)
    btmf__ptaf = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    gwqh__bkvd = cgutils.pack_array(builder, [btmf__ptaf], ty=qlnz__njun)
    emlsq__fzwf = builder.bitcast(builder.load(vgla__hraox), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=emlsq__fzwf, shape=
        qksiy__chpe, strides=gwqh__bkvd, itemsize=btmf__ptaf, meminfo=
        builder.load(nvni__vzykl))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    dwits__fxg = context.make_helper(builder, arr_type)
    dfg__khsvv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    jqkrq__wjpz = cgutils.get_or_insert_function(builder.module, dfg__khsvv,
        name='info_to_list_string_array')
    builder.call(jqkrq__wjpz, [in_info, dwits__fxg._get_ptr_by_name('meminfo')]
        )
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return dwits__fxg._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    bluwv__vmrn = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        imfkw__vkaaz = lengths_pos
        huzx__alb = infos_pos
        fvpat__hyymb, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        oyl__hrtkp = ArrayItemArrayPayloadType(arr_typ)
        swsv__qhgwy = context.get_data_type(oyl__hrtkp)
        txwak__bdps = context.get_abi_sizeof(swsv__qhgwy)
        xpmx__efx = define_array_item_dtor(context, builder, arr_typ,
            oyl__hrtkp)
        ltrrw__wzez = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, txwak__bdps), xpmx__efx)
        cbbbw__vbkd = context.nrt.meminfo_data(builder, ltrrw__wzez)
        but__tpwe = builder.bitcast(cbbbw__vbkd, swsv__qhgwy.as_pointer())
        gcbo__tioe = cgutils.create_struct_proxy(oyl__hrtkp)(context, builder)
        gcbo__tioe.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), imfkw__vkaaz)
        gcbo__tioe.data = fvpat__hyymb
        qnh__qrotd = builder.load(array_infos_ptr)
        pzaxp__vpw = builder.bitcast(builder.extract_value(qnh__qrotd,
            huzx__alb), bluwv__vmrn)
        gcbo__tioe.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, pzaxp__vpw)
        hopnz__euxb = builder.bitcast(builder.extract_value(qnh__qrotd, 
            huzx__alb + 1), bluwv__vmrn)
        gcbo__tioe.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, hopnz__euxb)
        builder.store(gcbo__tioe._getvalue(), but__tpwe)
        spzy__vbs = context.make_helper(builder, arr_typ)
        spzy__vbs.meminfo = ltrrw__wzez
        return spzy__vbs._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        efdxy__zsg = []
        huzx__alb = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for qknqy__fasbg in arr_typ.data:
            fvpat__hyymb, lengths_pos, infos_pos = nested_to_array(context,
                builder, qknqy__fasbg, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            efdxy__zsg.append(fvpat__hyymb)
        oyl__hrtkp = StructArrayPayloadType(arr_typ.data)
        swsv__qhgwy = context.get_value_type(oyl__hrtkp)
        txwak__bdps = context.get_abi_sizeof(swsv__qhgwy)
        xpmx__efx = define_struct_arr_dtor(context, builder, arr_typ,
            oyl__hrtkp)
        ltrrw__wzez = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, txwak__bdps), xpmx__efx)
        cbbbw__vbkd = context.nrt.meminfo_data(builder, ltrrw__wzez)
        but__tpwe = builder.bitcast(cbbbw__vbkd, swsv__qhgwy.as_pointer())
        gcbo__tioe = cgutils.create_struct_proxy(oyl__hrtkp)(context, builder)
        gcbo__tioe.data = cgutils.pack_array(builder, efdxy__zsg
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, efdxy__zsg)
        qnh__qrotd = builder.load(array_infos_ptr)
        hopnz__euxb = builder.bitcast(builder.extract_value(qnh__qrotd,
            huzx__alb), bluwv__vmrn)
        gcbo__tioe.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, hopnz__euxb)
        builder.store(gcbo__tioe._getvalue(), but__tpwe)
        gwr__pqndf = context.make_helper(builder, arr_typ)
        gwr__pqndf.meminfo = ltrrw__wzez
        return gwr__pqndf._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        qnh__qrotd = builder.load(array_infos_ptr)
        gji__fevu = builder.bitcast(builder.extract_value(qnh__qrotd,
            infos_pos), bluwv__vmrn)
        orrmp__kwx = context.make_helper(builder, arr_typ)
        qjo__fcr = ArrayItemArrayType(char_arr_type)
        spzy__vbs = context.make_helper(builder, qjo__fcr)
        dfg__khsvv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='info_to_string_array')
        builder.call(jqkrq__wjpz, [gji__fevu, spzy__vbs._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        orrmp__kwx.data = spzy__vbs._getvalue()
        return orrmp__kwx._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        qnh__qrotd = builder.load(array_infos_ptr)
        vqvtp__whumo = builder.bitcast(builder.extract_value(qnh__qrotd, 
            infos_pos + 1), bluwv__vmrn)
        return _lower_info_to_array_numpy(arr_typ, context, builder,
            vqvtp__whumo), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        plub__klz = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            plub__klz = int128_type
        elif arr_typ == datetime_date_array_type:
            plub__klz = types.int64
        qnh__qrotd = builder.load(array_infos_ptr)
        hopnz__euxb = builder.bitcast(builder.extract_value(qnh__qrotd,
            infos_pos), bluwv__vmrn)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, hopnz__euxb)
        vqvtp__whumo = builder.bitcast(builder.extract_value(qnh__qrotd, 
            infos_pos + 1), bluwv__vmrn)
        arr.data = _lower_info_to_array_numpy(types.Array(plub__klz, 1, 'C'
            ), context, builder, vqvtp__whumo)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, rynb__tki = args
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
                return 1 + sum([get_num_arrays(qknqy__fasbg) for
                    qknqy__fasbg in arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(qknqy__fasbg) for
                    qknqy__fasbg in arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            cii__mgjp = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            cii__mgjp = _get_map_arr_data_type(arr_type)
        else:
            cii__mgjp = arr_type
        bhhv__ykz = get_num_arrays(cii__mgjp)
        osiq__zcy = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), 0) for rynb__tki in range(bhhv__ykz)])
        lengths_ptr = cgutils.alloca_once_value(builder, osiq__zcy)
        wtj__izm = lir.Constant(lir.IntType(8).as_pointer(), None)
        rdhr__cam = cgutils.pack_array(builder, [wtj__izm for rynb__tki in
            range(get_num_infos(cii__mgjp))])
        array_infos_ptr = cgutils.alloca_once_value(builder, rdhr__cam)
        dfg__khsvv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='info_to_nested_array')
        builder.call(jqkrq__wjpz, [in_info, builder.bitcast(lengths_ptr,
            lir.IntType(64).as_pointer()), builder.bitcast(array_infos_ptr,
            lir.IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, rynb__tki, rynb__tki = nested_to_array(context, builder,
            cii__mgjp, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            misam__aqljo = context.make_helper(builder, arr_type)
            misam__aqljo.data = arr
            context.nrt.incref(builder, cii__mgjp, arr)
            arr = misam__aqljo._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, cii__mgjp)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        orrmp__kwx = context.make_helper(builder, arr_type)
        qjo__fcr = ArrayItemArrayType(char_arr_type)
        spzy__vbs = context.make_helper(builder, qjo__fcr)
        dfg__khsvv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='info_to_string_array')
        builder.call(jqkrq__wjpz, [in_info, spzy__vbs._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        orrmp__kwx.data = spzy__vbs._getvalue()
        return orrmp__kwx._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='get_nested_info')
        jjtmv__mfnbw = builder.call(jqkrq__wjpz, [in_info, lir.Constant(lir
            .IntType(32), 1)])
        zir__leic = builder.call(jqkrq__wjpz, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        sjfrg__aals = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        sjfrg__aals.data = info_to_array_codegen(context, builder, sig, (
            jjtmv__mfnbw, context.get_constant_null(arr_type.data)))
        hsk__dwdgw = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = hsk__dwdgw(array_info_type, hsk__dwdgw)
        sjfrg__aals.indices = info_to_array_codegen(context, builder, sig,
            (zir__leic, context.get_constant_null(hsk__dwdgw)))
        dfg__khsvv = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='get_has_global_dictionary')
        sdz__zvfys = builder.call(jqkrq__wjpz, [in_info])
        sjfrg__aals.has_global_dictionary = builder.trunc(sdz__zvfys,
            cgutils.bool_t)
        return sjfrg__aals._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        iqhyi__buak = get_categories_int_type(arr_type.dtype)
        znvw__off = types.Array(iqhyi__buak, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(znvw__off, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            qou__vcgmg = bodo.utils.utils.create_categorical_type(arr_type.
                dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(qou__vcgmg))
            int_type = arr_type.dtype.int_type
            bnfp__vik = arr_type.dtype.data.data
            rzric__rbsv = context.get_constant_generic(builder, bnfp__vik,
                qou__vcgmg)
            ocbne__btrzq = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(bnfp__vik), [rzric__rbsv])
        else:
            ocbne__btrzq = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, ocbne__btrzq)
        out_arr.dtype = ocbne__btrzq
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        emlsq__fzwf = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = emlsq__fzwf
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        plub__klz = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            plub__klz = int128_type
        elif arr_type == datetime_date_array_type:
            plub__klz = types.int64
        dovq__yya = types.Array(plub__klz, 1, 'C')
        sqljq__kuaw = context.make_array(dovq__yya)(context, builder)
        ivg__etyeq = types.Array(types.uint8, 1, 'C')
        xgbt__nne = context.make_array(ivg__etyeq)(context, builder)
        zassd__uyi = cgutils.alloca_once(builder, lir.IntType(64))
        iahdj__nrwuy = cgutils.alloca_once(builder, lir.IntType(64))
        vgla__hraox = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        tysk__kmncl = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        nvni__vzykl = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        kiwx__byd = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        dfg__khsvv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='info_to_nullable_array')
        builder.call(jqkrq__wjpz, [in_info, zassd__uyi, iahdj__nrwuy,
            vgla__hraox, tysk__kmncl, nvni__vzykl, kiwx__byd])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        qlnz__njun = context.get_value_type(types.intp)
        qksiy__chpe = cgutils.pack_array(builder, [builder.load(zassd__uyi)
            ], ty=qlnz__njun)
        btmf__ptaf = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(plub__klz)))
        gwqh__bkvd = cgutils.pack_array(builder, [btmf__ptaf], ty=qlnz__njun)
        emlsq__fzwf = builder.bitcast(builder.load(vgla__hraox), context.
            get_data_type(plub__klz).as_pointer())
        numba.np.arrayobj.populate_array(sqljq__kuaw, data=emlsq__fzwf,
            shape=qksiy__chpe, strides=gwqh__bkvd, itemsize=btmf__ptaf,
            meminfo=builder.load(nvni__vzykl))
        arr.data = sqljq__kuaw._getvalue()
        qksiy__chpe = cgutils.pack_array(builder, [builder.load(
            iahdj__nrwuy)], ty=qlnz__njun)
        btmf__ptaf = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(types.uint8)))
        gwqh__bkvd = cgutils.pack_array(builder, [btmf__ptaf], ty=qlnz__njun)
        emlsq__fzwf = builder.bitcast(builder.load(tysk__kmncl), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(xgbt__nne, data=emlsq__fzwf, shape
            =qksiy__chpe, strides=gwqh__bkvd, itemsize=btmf__ptaf, meminfo=
            builder.load(kiwx__byd))
        arr.null_bitmap = xgbt__nne._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        day__unpdl = context.make_array(arr_type.arr_type)(context, builder)
        sqwe__ldlw = context.make_array(arr_type.arr_type)(context, builder)
        zassd__uyi = cgutils.alloca_once(builder, lir.IntType(64))
        vmdh__ciau = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        uhlg__xgwgg = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        jrtc__twdn = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        lfik__ilbcg = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        dfg__khsvv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='info_to_interval_array')
        builder.call(jqkrq__wjpz, [in_info, zassd__uyi, vmdh__ciau,
            uhlg__xgwgg, jrtc__twdn, lfik__ilbcg])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        qlnz__njun = context.get_value_type(types.intp)
        qksiy__chpe = cgutils.pack_array(builder, [builder.load(zassd__uyi)
            ], ty=qlnz__njun)
        btmf__ptaf = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
        gwqh__bkvd = cgutils.pack_array(builder, [btmf__ptaf], ty=qlnz__njun)
        pikhe__mpcht = builder.bitcast(builder.load(vmdh__ciau), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(day__unpdl, data=pikhe__mpcht,
            shape=qksiy__chpe, strides=gwqh__bkvd, itemsize=btmf__ptaf,
            meminfo=builder.load(jrtc__twdn))
        arr.left = day__unpdl._getvalue()
        giwy__oqnjx = builder.bitcast(builder.load(uhlg__xgwgg), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(sqwe__ldlw, data=giwy__oqnjx,
            shape=qksiy__chpe, strides=gwqh__bkvd, itemsize=btmf__ptaf,
            meminfo=builder.load(lfik__ilbcg))
        arr.right = sqwe__ldlw._getvalue()
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
        cphj__svahz, rynb__tki = args
        joxd__ragsb = numba_to_c_type(array_type.dtype)
        dvko__nhwb = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), joxd__ragsb))
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='alloc_numpy')
        return builder.call(jqkrq__wjpz, [cphj__svahz, builder.load(
            dvko__nhwb)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        cphj__svahz, wskqc__fzux = args
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='alloc_string_array')
        return builder.call(jqkrq__wjpz, [cphj__svahz, wskqc__fzux])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    ohlsl__isyf, = args
    xkg__eza = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], ohlsl__isyf)
    dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer().as_pointer(), lir.IntType(64)])
    jqkrq__wjpz = cgutils.get_or_insert_function(builder.module, dfg__khsvv,
        name='arr_info_list_to_table')
    return builder.call(jqkrq__wjpz, [xkg__eza.data, xkg__eza.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='info_from_table')
        return builder.call(jqkrq__wjpz, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    tchi__uxf = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, mbidc__phxqn, rynb__tki = args
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='info_from_table')
        ztwin__gxmm = cgutils.create_struct_proxy(tchi__uxf)(context, builder)
        ztwin__gxmm.parent = cgutils.get_null_value(ztwin__gxmm.parent.type)
        wnct__nig = context.make_array(table_idx_arr_t)(context, builder,
            mbidc__phxqn)
        roz__qqe = context.get_constant(types.int64, -1)
        wnq__mab = context.get_constant(types.int64, 0)
        pdutk__kyulj = cgutils.alloca_once_value(builder, wnq__mab)
        for t, jam__arie in tchi__uxf.type_to_blk.items():
            btj__lkmv = context.get_constant(types.int64, len(tchi__uxf.
                block_to_arr_ind[jam__arie]))
            rynb__tki, icq__icrba = ListInstance.allocate_ex(context,
                builder, types.List(t), btj__lkmv)
            icq__icrba.size = btj__lkmv
            bctdt__myu = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(tchi__uxf.block_to_arr_ind[
                jam__arie], dtype=np.int64))
            tothw__ajddv = context.make_array(types.Array(types.int64, 1, 'C')
                )(context, builder, bctdt__myu)
            with cgutils.for_range(builder, btj__lkmv) as fey__mezf:
                lzf__lttrc = fey__mezf.index
                nctea__amk = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    tothw__ajddv, lzf__lttrc)
                brpff__mquyc = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, wnct__nig, nctea__amk)
                ogy__opqr = builder.icmp_unsigned('!=', brpff__mquyc, roz__qqe)
                with builder.if_else(ogy__opqr) as (dba__rdx, vek__yqawm):
                    with dba__rdx:
                        vhb__wqgj = builder.call(jqkrq__wjpz, [cpp_table,
                            brpff__mquyc])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            vhb__wqgj])
                        icq__icrba.inititem(lzf__lttrc, arr, incref=False)
                        cphj__svahz = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(cphj__svahz, pdutk__kyulj)
                    with vek__yqawm:
                        pqj__oxub = context.get_constant_null(t)
                        icq__icrba.inititem(lzf__lttrc, pqj__oxub, incref=False
                            )
            setattr(ztwin__gxmm, f'block_{jam__arie}', icq__icrba.value)
        ztwin__gxmm.len = builder.load(pdutk__kyulj)
        return ztwin__gxmm._getvalue()
    return tchi__uxf(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t):
    fiscn__wryn = out_col_inds_t.instance_type.meta
    tchi__uxf = unwrap_typeref(out_types_t.types[0])
    lnfwr__cox = [unwrap_typeref(out_types_t.types[lzf__lttrc]) for
        lzf__lttrc in range(1, len(out_types_t.types))]
    koqrk__uamkk = {}
    ekeiw__qujbl = get_overload_const_int(n_table_cols_t)
    monkn__phr = {blny__vugbc: lzf__lttrc for lzf__lttrc, blny__vugbc in
        enumerate(fiscn__wryn)}
    sfxm__qgap = (
        'def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t):\n'
        )
    if tchi__uxf == types.none:
        sfxm__qgap += f'  py_table = None\n'
    else:
        sfxm__qgap += f'  py_table = init_table(py_table_type, False)\n'
        sfxm__qgap += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for cghw__ivnfi, jam__arie in tchi__uxf.type_to_blk.items():
            jyh__mvc = [monkn__phr.get(lzf__lttrc, -1) for lzf__lttrc in
                tchi__uxf.block_to_arr_ind[jam__arie]]
            koqrk__uamkk[f'out_inds_{jam__arie}'] = np.array(jyh__mvc, np.int64
                )
            koqrk__uamkk[f'out_type_{jam__arie}'] = cghw__ivnfi
            koqrk__uamkk[f'typ_list_{jam__arie}'] = types.List(cghw__ivnfi)
            jlz__kol = f'out_type_{jam__arie}'
            if type_has_unknown_cats(cghw__ivnfi):
                sfxm__qgap += f"""  in_arr_list_{jam__arie} = get_table_block(out_types_t[0], {jam__arie})
"""
                jlz__kol = f'in_arr_list_{jam__arie}[i]'
            btj__lkmv = len(tchi__uxf.block_to_arr_ind[jam__arie])
            sfxm__qgap += f"""  arr_list_{jam__arie} = alloc_list_like(typ_list_{jam__arie}, {btj__lkmv}, False)
"""
            sfxm__qgap += f'  for i in range(len(arr_list_{jam__arie})):\n'
            sfxm__qgap += (
                f'    cpp_ind_{jam__arie} = out_inds_{jam__arie}[i]\n')
            sfxm__qgap += f'    if cpp_ind_{jam__arie} == -1:\n'
            sfxm__qgap += f'      continue\n'
            sfxm__qgap += f"""    arr_{jam__arie} = info_to_array(info_from_table(cpp_table, cpp_ind_{jam__arie}), {jlz__kol})
"""
            sfxm__qgap += f'    arr_list_{jam__arie}[i] = arr_{jam__arie}\n'
            sfxm__qgap += f"""  py_table = set_table_block(py_table, arr_list_{jam__arie}, {jam__arie})
"""
    awq__khemx = []
    for lzf__lttrc, t in enumerate(lnfwr__cox):
        mnk__lwyb = monkn__phr.get(ekeiw__qujbl + lzf__lttrc, -1)
        if mnk__lwyb != -1:
            koqrk__uamkk[f'extra_arr_type_{lzf__lttrc}'] = t
            jlz__kol = f'extra_arr_type_{lzf__lttrc}'
            if type_has_unknown_cats(t):
                jlz__kol = f'out_types_t[{lzf__lttrc + 1}]'
            sfxm__qgap += f"""  out_{lzf__lttrc} = info_to_array(info_from_table(cpp_table, {mnk__lwyb}), {jlz__kol})
"""
            awq__khemx.append(f'out_{lzf__lttrc}')
    if tchi__uxf != types.none:
        sfxm__qgap += f"  return (py_table, {', '.join(awq__khemx)})\n"
    else:
        reey__iqwc = ',' if len(awq__khemx) == 1 else ''
        sfxm__qgap += f"  return ({', '.join(awq__khemx)}{reey__iqwc})\n"
    koqrk__uamkk.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(fiscn__wryn), 'py_table_type': tchi__uxf})
    laxkp__vay = {}
    exec(sfxm__qgap, koqrk__uamkk, laxkp__vay)
    return laxkp__vay['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    tchi__uxf = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, rynb__tki = args
        hlon__opq = cgutils.create_struct_proxy(tchi__uxf)(context, builder,
            py_table)
        if tchi__uxf.has_runtime_cols:
            cnb__mgp = lir.Constant(lir.IntType(64), 0)
            for jam__arie, t in enumerate(tchi__uxf.arr_types):
                sdtp__fkgxd = getattr(hlon__opq, f'block_{jam__arie}')
                dmew__guocl = ListInstance(context, builder, types.List(t),
                    sdtp__fkgxd)
                cnb__mgp = builder.add(cnb__mgp, dmew__guocl.size)
        else:
            cnb__mgp = lir.Constant(lir.IntType(64), len(tchi__uxf.arr_types))
        rynb__tki, bkx__gttk = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), cnb__mgp)
        bkx__gttk.size = cnb__mgp
        if tchi__uxf.has_runtime_cols:
            zuxxi__fwimo = lir.Constant(lir.IntType(64), 0)
            for jam__arie, t in enumerate(tchi__uxf.arr_types):
                sdtp__fkgxd = getattr(hlon__opq, f'block_{jam__arie}')
                dmew__guocl = ListInstance(context, builder, types.List(t),
                    sdtp__fkgxd)
                btj__lkmv = dmew__guocl.size
                with cgutils.for_range(builder, btj__lkmv) as fey__mezf:
                    lzf__lttrc = fey__mezf.index
                    arr = dmew__guocl.getitem(lzf__lttrc)
                    cptpe__scza = signature(array_info_type, t)
                    hjbsz__djkp = arr,
                    xwfi__hkdr = array_to_info_codegen(context, builder,
                        cptpe__scza, hjbsz__djkp)
                    bkx__gttk.inititem(builder.add(zuxxi__fwimo, lzf__lttrc
                        ), xwfi__hkdr, incref=False)
                zuxxi__fwimo = builder.add(zuxxi__fwimo, btj__lkmv)
        else:
            for t, jam__arie in tchi__uxf.type_to_blk.items():
                btj__lkmv = context.get_constant(types.int64, len(tchi__uxf
                    .block_to_arr_ind[jam__arie]))
                sdtp__fkgxd = getattr(hlon__opq, f'block_{jam__arie}')
                dmew__guocl = ListInstance(context, builder, types.List(t),
                    sdtp__fkgxd)
                bctdt__myu = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(tchi__uxf.
                    block_to_arr_ind[jam__arie], dtype=np.int64))
                tothw__ajddv = context.make_array(types.Array(types.int64, 
                    1, 'C'))(context, builder, bctdt__myu)
                with cgutils.for_range(builder, btj__lkmv) as fey__mezf:
                    lzf__lttrc = fey__mezf.index
                    nctea__amk = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        tothw__ajddv, lzf__lttrc)
                    ckdil__tkc = signature(types.none, tchi__uxf, types.
                        List(t), types.int64, types.int64)
                    ooxdl__cup = py_table, sdtp__fkgxd, lzf__lttrc, nctea__amk
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, ckdil__tkc, ooxdl__cup)
                    arr = dmew__guocl.getitem(lzf__lttrc)
                    cptpe__scza = signature(array_info_type, t)
                    hjbsz__djkp = arr,
                    xwfi__hkdr = array_to_info_codegen(context, builder,
                        cptpe__scza, hjbsz__djkp)
                    bkx__gttk.inititem(nctea__amk, xwfi__hkdr, incref=False)
        isxt__vytm = bkx__gttk.value
        qcirs__cruoo = signature(table_type, types.List(array_info_type))
        qxerw__esnu = isxt__vytm,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            qcirs__cruoo, qxerw__esnu)
        context.nrt.decref(builder, types.List(array_info_type), isxt__vytm)
        return cpp_table
    return table_type(tchi__uxf, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    whvgd__tbfqv = in_col_inds_t.instance_type.meta
    koqrk__uamkk = {}
    ekeiw__qujbl = get_overload_const_int(n_table_cols_t)
    uxb__ioicw = defaultdict(list)
    monkn__phr = {}
    for lzf__lttrc, blny__vugbc in enumerate(whvgd__tbfqv):
        if blny__vugbc in monkn__phr:
            uxb__ioicw[blny__vugbc].append(lzf__lttrc)
        else:
            monkn__phr[blny__vugbc] = lzf__lttrc
    sfxm__qgap = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    sfxm__qgap += (
        f'  cpp_arr_list = alloc_empty_list_type({len(whvgd__tbfqv)}, array_info_type)\n'
        )
    if py_table != types.none:
        for jam__arie in py_table.type_to_blk.values():
            jyh__mvc = [monkn__phr.get(lzf__lttrc, -1) for lzf__lttrc in
                py_table.block_to_arr_ind[jam__arie]]
            koqrk__uamkk[f'out_inds_{jam__arie}'] = np.array(jyh__mvc, np.int64
                )
            koqrk__uamkk[f'arr_inds_{jam__arie}'] = np.array(py_table.
                block_to_arr_ind[jam__arie], np.int64)
            sfxm__qgap += (
                f'  arr_list_{jam__arie} = get_table_block(py_table, {jam__arie})\n'
                )
            sfxm__qgap += f'  for i in range(len(arr_list_{jam__arie})):\n'
            sfxm__qgap += (
                f'    out_arr_ind_{jam__arie} = out_inds_{jam__arie}[i]\n')
            sfxm__qgap += f'    if out_arr_ind_{jam__arie} == -1:\n'
            sfxm__qgap += f'      continue\n'
            sfxm__qgap += (
                f'    arr_ind_{jam__arie} = arr_inds_{jam__arie}[i]\n')
            sfxm__qgap += f"""    ensure_column_unboxed(py_table, arr_list_{jam__arie}, i, arr_ind_{jam__arie})
"""
            sfxm__qgap += f"""    cpp_arr_list[out_arr_ind_{jam__arie}] = array_to_info(arr_list_{jam__arie}[i])
"""
        for aqsjp__ktzf, ntlo__fsp in uxb__ioicw.items():
            if aqsjp__ktzf < ekeiw__qujbl:
                jam__arie = py_table.block_nums[aqsjp__ktzf]
                apz__iba = py_table.block_offsets[aqsjp__ktzf]
                for mnk__lwyb in ntlo__fsp:
                    sfxm__qgap += f"""  cpp_arr_list[{mnk__lwyb}] = array_to_info(arr_list_{jam__arie}[{apz__iba}])
"""
    for lzf__lttrc in range(len(extra_arrs_tup)):
        ncib__get = monkn__phr.get(ekeiw__qujbl + lzf__lttrc, -1)
        if ncib__get != -1:
            isy__sgve = [ncib__get] + uxb__ioicw.get(ekeiw__qujbl +
                lzf__lttrc, [])
            for mnk__lwyb in isy__sgve:
                sfxm__qgap += f"""  cpp_arr_list[{mnk__lwyb}] = array_to_info(extra_arrs_tup[{lzf__lttrc}])
"""
    sfxm__qgap += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    koqrk__uamkk.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    laxkp__vay = {}
    exec(sfxm__qgap, koqrk__uamkk, laxkp__vay)
    return laxkp__vay['impl']


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        dfg__khsvv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='delete_table')
        builder.call(jqkrq__wjpz, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='shuffle_table')
        ngmoz__waovg = builder.call(jqkrq__wjpz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ngmoz__waovg
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
        dfg__khsvv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='delete_shuffle_info')
        return builder.call(jqkrq__wjpz, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='reverse_shuffle_table')
        return builder.call(jqkrq__wjpz, args)
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
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='hash_join_table')
        ngmoz__waovg = builder.call(jqkrq__wjpz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ngmoz__waovg
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
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='sort_values_table')
        ngmoz__waovg = builder.call(jqkrq__wjpz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ngmoz__waovg
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='sample_table')
        ngmoz__waovg = builder.call(jqkrq__wjpz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ngmoz__waovg
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='shuffle_renormalization')
        ngmoz__waovg = builder.call(jqkrq__wjpz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ngmoz__waovg
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='shuffle_renormalization_group')
        ngmoz__waovg = builder.call(jqkrq__wjpz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ngmoz__waovg
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='drop_duplicates_table')
        ngmoz__waovg = builder.call(jqkrq__wjpz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ngmoz__waovg
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
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='pivot_groupby_and_aggregate')
        ngmoz__waovg = builder.call(jqkrq__wjpz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ngmoz__waovg
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
        dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        jqkrq__wjpz = cgutils.get_or_insert_function(builder.module,
            dfg__khsvv, name='groupby_and_aggregate')
        ngmoz__waovg = builder.call(jqkrq__wjpz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ngmoz__waovg
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
    oor__vyqn = array_to_info(in_arr)
    dnuy__lhsp = array_to_info(in_values)
    lwa__daa = array_to_info(out_arr)
    ujaw__mde = arr_info_list_to_table([oor__vyqn, dnuy__lhsp, lwa__daa])
    _array_isin(lwa__daa, oor__vyqn, dnuy__lhsp, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(ujaw__mde)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, pat, out_arr):
    oor__vyqn = array_to_info(in_arr)
    lwa__daa = array_to_info(out_arr)
    _get_search_regex(oor__vyqn, case, pat, lwa__daa)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    itkc__nql = col_array_typ.dtype
    if isinstance(itkc__nql, types.Number) or itkc__nql in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                ztwin__gxmm, gab__etw = args
                ztwin__gxmm = builder.bitcast(ztwin__gxmm, lir.IntType(8).
                    as_pointer().as_pointer())
                ahcy__cioz = lir.Constant(lir.IntType(64), c_ind)
                cktg__mgv = builder.load(builder.gep(ztwin__gxmm, [ahcy__cioz])
                    )
                cktg__mgv = builder.bitcast(cktg__mgv, context.
                    get_data_type(itkc__nql).as_pointer())
                return builder.load(builder.gep(cktg__mgv, [gab__etw]))
            return itkc__nql(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.string_array_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                ztwin__gxmm, gab__etw = args
                ztwin__gxmm = builder.bitcast(ztwin__gxmm, lir.IntType(8).
                    as_pointer().as_pointer())
                ahcy__cioz = lir.Constant(lir.IntType(64), c_ind)
                cktg__mgv = builder.load(builder.gep(ztwin__gxmm, [ahcy__cioz])
                    )
                dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                akxum__kvfik = cgutils.get_or_insert_function(builder.
                    module, dfg__khsvv, name='array_info_getitem')
                mjj__hkfe = cgutils.alloca_once(builder, lir.IntType(64))
                args = cktg__mgv, gab__etw, mjj__hkfe
                vgla__hraox = builder.call(akxum__kvfik, args)
                return context.make_tuple(builder, sig.return_type, [
                    vgla__hraox, builder.load(mjj__hkfe)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                pmn__gqvh = lir.Constant(lir.IntType(64), 1)
                xba__cqnh = lir.Constant(lir.IntType(64), 2)
                ztwin__gxmm, gab__etw = args
                ztwin__gxmm = builder.bitcast(ztwin__gxmm, lir.IntType(8).
                    as_pointer().as_pointer())
                ahcy__cioz = lir.Constant(lir.IntType(64), c_ind)
                cktg__mgv = builder.load(builder.gep(ztwin__gxmm, [ahcy__cioz])
                    )
                dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64)])
                mjmbq__lilao = cgutils.get_or_insert_function(builder.
                    module, dfg__khsvv, name='get_nested_info')
                args = cktg__mgv, xba__cqnh
                meug__zszy = builder.call(mjmbq__lilao, args)
                dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer()])
                yexv__mzp = cgutils.get_or_insert_function(builder.module,
                    dfg__khsvv, name='array_info_getdata1')
                args = meug__zszy,
                xhvhh__qmits = builder.call(yexv__mzp, args)
                xhvhh__qmits = builder.bitcast(xhvhh__qmits, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                gyy__uonox = builder.sext(builder.load(builder.gep(
                    xhvhh__qmits, [gab__etw])), lir.IntType(64))
                args = cktg__mgv, pmn__gqvh
                ddsov__vvxft = builder.call(mjmbq__lilao, args)
                dfg__khsvv = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                akxum__kvfik = cgutils.get_or_insert_function(builder.
                    module, dfg__khsvv, name='array_info_getitem')
                mjj__hkfe = cgutils.alloca_once(builder, lir.IntType(64))
                args = ddsov__vvxft, gyy__uonox, mjj__hkfe
                vgla__hraox = builder.call(akxum__kvfik, args)
                return context.make_tuple(builder, sig.return_type, [
                    vgla__hraox, builder.load(mjj__hkfe)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{itkc__nql}' column data type not supported"
        )


def _gen_row_na_check_intrinsic(col_array_dtype, c_ind):
    if (isinstance(col_array_dtype, bodo.libs.int_arr_ext.IntegerArrayType) or
        col_array_dtype == bodo.libs.bool_arr_ext.boolean_array or
        is_str_arr_type(col_array_dtype) or isinstance(col_array_dtype,
        types.Array) and col_array_dtype.dtype == bodo.datetime_date_type):

        @intrinsic
        def checkna_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                aekmi__khc, gab__etw = args
                aekmi__khc = builder.bitcast(aekmi__khc, lir.IntType(8).
                    as_pointer().as_pointer())
                ahcy__cioz = lir.Constant(lir.IntType(64), c_ind)
                cktg__mgv = builder.load(builder.gep(aekmi__khc, [ahcy__cioz]))
                bpn__xudhr = builder.bitcast(cktg__mgv, context.
                    get_data_type(types.bool_).as_pointer())
                btdoq__ykrhs = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    bpn__xudhr, gab__etw)
                cur__pebdr = builder.icmp_unsigned('!=', btdoq__ykrhs, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(cur__pebdr, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        itkc__nql = col_array_dtype.dtype
        if itkc__nql in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    ztwin__gxmm, gab__etw = args
                    ztwin__gxmm = builder.bitcast(ztwin__gxmm, lir.IntType(
                        8).as_pointer().as_pointer())
                    ahcy__cioz = lir.Constant(lir.IntType(64), c_ind)
                    cktg__mgv = builder.load(builder.gep(ztwin__gxmm, [
                        ahcy__cioz]))
                    cktg__mgv = builder.bitcast(cktg__mgv, context.
                        get_data_type(itkc__nql).as_pointer())
                    ludoo__vheoc = builder.load(builder.gep(cktg__mgv, [
                        gab__etw]))
                    cur__pebdr = builder.icmp_unsigned('!=', ludoo__vheoc,
                        lir.Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(cur__pebdr, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(itkc__nql, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    ztwin__gxmm, gab__etw = args
                    ztwin__gxmm = builder.bitcast(ztwin__gxmm, lir.IntType(
                        8).as_pointer().as_pointer())
                    ahcy__cioz = lir.Constant(lir.IntType(64), c_ind)
                    cktg__mgv = builder.load(builder.gep(ztwin__gxmm, [
                        ahcy__cioz]))
                    cktg__mgv = builder.bitcast(cktg__mgv, context.
                        get_data_type(itkc__nql).as_pointer())
                    ludoo__vheoc = builder.load(builder.gep(cktg__mgv, [
                        gab__etw]))
                    ivac__zmjy = signature(types.bool_, itkc__nql)
                    btdoq__ykrhs = numba.np.npyfuncs.np_real_isnan_impl(context
                        , builder, ivac__zmjy, (ludoo__vheoc,))
                    return builder.not_(builder.sext(btdoq__ykrhs, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
