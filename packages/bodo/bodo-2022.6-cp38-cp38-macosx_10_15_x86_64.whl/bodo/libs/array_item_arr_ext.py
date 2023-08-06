"""Array implementation for variable-size array items.
Corresponds to Spark's ArrayType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Variable-size List: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in a contingous data array, while an offsets array marks the
individual arrays. For example:
value:             [[1, 2], [3], None, [5, 4, 6], []]
data:              [1, 2, 3, 5, 4, 6]
offsets:           [0, 2, 3, 3, 6, 6]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, is_iterable_type, is_list_like_index_type
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('array_item_array_from_sequence', array_ext.
    array_item_array_from_sequence)
ll.add_symbol('np_array_from_array_item_array', array_ext.
    np_array_from_array_item_array)
offset_type = types.uint64
np_offset_type = numba.np.numpy_support.as_dtype(offset_type)


class ArrayItemArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        assert bodo.utils.utils.is_array_typ(dtype, False)
        self.dtype = dtype
        super(ArrayItemArrayType, self).__init__(name=
            'ArrayItemArrayType({})'.format(dtype))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return ArrayItemArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class ArrayItemArrayPayloadType(types.Type):

    def __init__(self, array_type):
        self.array_type = array_type
        super(ArrayItemArrayPayloadType, self).__init__(name=
            'ArrayItemArrayPayloadType({})'.format(array_type))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(ArrayItemArrayPayloadType)
class ArrayItemArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        sumqn__mswir = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, sumqn__mswir)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        sumqn__mswir = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, sumqn__mswir)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    axc__sim = builder.module
    tceq__lgl = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    lfbfn__gyts = cgutils.get_or_insert_function(axc__sim, tceq__lgl, name=
        '.dtor.array_item.{}'.format(array_item_type.dtype))
    if not lfbfn__gyts.is_declaration:
        return lfbfn__gyts
    lfbfn__gyts.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(lfbfn__gyts.append_basic_block())
    mhjv__vxfsp = lfbfn__gyts.args[0]
    cwh__noiv = context.get_value_type(payload_type).as_pointer()
    amr__nwnu = builder.bitcast(mhjv__vxfsp, cwh__noiv)
    msj__zaz = context.make_helper(builder, payload_type, ref=amr__nwnu)
    context.nrt.decref(builder, array_item_type.dtype, msj__zaz.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'), msj__zaz.
        offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), msj__zaz.
        null_bitmap)
    builder.ret_void()
    return lfbfn__gyts


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    mrpdh__lpdgx = context.get_value_type(payload_type)
    qwxs__qhcr = context.get_abi_sizeof(mrpdh__lpdgx)
    cuv__bduv = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    xwbhb__pxekx = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, qwxs__qhcr), cuv__bduv)
    izoet__edkdb = context.nrt.meminfo_data(builder, xwbhb__pxekx)
    alelq__lgw = builder.bitcast(izoet__edkdb, mrpdh__lpdgx.as_pointer())
    msj__zaz = cgutils.create_struct_proxy(payload_type)(context, builder)
    msj__zaz.n_arrays = n_arrays
    afkz__cvc = n_elems.type.count
    bortx__auzmo = builder.extract_value(n_elems, 0)
    flnf__lqca = cgutils.alloca_once_value(builder, bortx__auzmo)
    waghu__yfr = builder.icmp_signed('==', bortx__auzmo, lir.Constant(
        bortx__auzmo.type, -1))
    with builder.if_then(waghu__yfr):
        builder.store(n_arrays, flnf__lqca)
    n_elems = cgutils.pack_array(builder, [builder.load(flnf__lqca)] + [
        builder.extract_value(n_elems, rjysm__jqd) for rjysm__jqd in range(
        1, afkz__cvc)])
    msj__zaz.data = gen_allocate_array(context, builder, array_item_type.
        dtype, n_elems, c)
    fmj__xprx = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    vnkcq__aqzhy = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [fmj__xprx])
    offsets_ptr = vnkcq__aqzhy.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    msj__zaz.offsets = vnkcq__aqzhy._getvalue()
    rsowj__kgrbx = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    qgh__uxwrr = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [rsowj__kgrbx])
    null_bitmap_ptr = qgh__uxwrr.data
    msj__zaz.null_bitmap = qgh__uxwrr._getvalue()
    builder.store(msj__zaz._getvalue(), alelq__lgw)
    return xwbhb__pxekx, msj__zaz.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    fxnwq__msyb, mprmr__dvlc = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    zair__yij = context.insert_const_string(builder.module, 'pandas')
    fmksh__saxvs = c.pyapi.import_module_noblock(zair__yij)
    eydrk__fuh = c.pyapi.object_getattr_string(fmksh__saxvs, 'NA')
    griw__zcsgh = c.context.get_constant(offset_type, 0)
    builder.store(griw__zcsgh, offsets_ptr)
    bdrjj__vlxe = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as leo__xcwdn:
        dspi__jqntt = leo__xcwdn.index
        item_ind = builder.load(bdrjj__vlxe)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [dspi__jqntt]))
        arr_obj = seq_getitem(builder, context, val, dspi__jqntt)
        set_bitmap_bit(builder, null_bitmap_ptr, dspi__jqntt, 0)
        sgpz__qycj = is_na_value(builder, context, arr_obj, eydrk__fuh)
        kjt__plnoh = builder.icmp_unsigned('!=', sgpz__qycj, lir.Constant(
            sgpz__qycj.type, 1))
        with builder.if_then(kjt__plnoh):
            set_bitmap_bit(builder, null_bitmap_ptr, dspi__jqntt, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), bdrjj__vlxe)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(bdrjj__vlxe), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(fmksh__saxvs)
    c.pyapi.decref(eydrk__fuh)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    ukyi__roq = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if ukyi__roq:
        tceq__lgl = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        jofjn__ouq = cgutils.get_or_insert_function(c.builder.module,
            tceq__lgl, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(jofjn__ouq,
            [val])])
    else:
        lftxl__bzvyo = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            lftxl__bzvyo, rjysm__jqd) for rjysm__jqd in range(1,
            lftxl__bzvyo.type.count)])
    xwbhb__pxekx, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if ukyi__roq:
        oor__ccg = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        dywud__sqv = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        tceq__lgl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        lfbfn__gyts = cgutils.get_or_insert_function(c.builder.module,
            tceq__lgl, name='array_item_array_from_sequence')
        c.builder.call(lfbfn__gyts, [val, c.builder.bitcast(dywud__sqv, lir
            .IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), oor__ccg)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    qxn__wub = c.context.make_helper(c.builder, typ)
    qxn__wub.meminfo = xwbhb__pxekx
    jxujw__bwazb = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qxn__wub._getvalue(), is_error=jxujw__bwazb)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    qxn__wub = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    izoet__edkdb = context.nrt.meminfo_data(builder, qxn__wub.meminfo)
    alelq__lgw = builder.bitcast(izoet__edkdb, context.get_value_type(
        payload_type).as_pointer())
    msj__zaz = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(alelq__lgw))
    return msj__zaz


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    zair__yij = context.insert_const_string(builder.module, 'numpy')
    yku__ahq = c.pyapi.import_module_noblock(zair__yij)
    jlm__oxast = c.pyapi.object_getattr_string(yku__ahq, 'object_')
    lyjd__ebtb = c.pyapi.long_from_longlong(n_arrays)
    xpkrs__mgsio = c.pyapi.call_method(yku__ahq, 'ndarray', (lyjd__ebtb,
        jlm__oxast))
    ajhgb__xcx = c.pyapi.object_getattr_string(yku__ahq, 'nan')
    bdrjj__vlxe = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as leo__xcwdn:
        dspi__jqntt = leo__xcwdn.index
        pyarray_setitem(builder, context, xpkrs__mgsio, dspi__jqntt, ajhgb__xcx
            )
        ldeys__vcda = get_bitmap_bit(builder, null_bitmap_ptr, dspi__jqntt)
        dozm__jzjp = builder.icmp_unsigned('!=', ldeys__vcda, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(dozm__jzjp):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(dspi__jqntt, lir.Constant(
                dspi__jqntt.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [dspi__jqntt]))), lir.IntType(64))
            item_ind = builder.load(bdrjj__vlxe)
            fxnwq__msyb, dtghm__fgug = c.pyapi.call_jit_code(lambda
                data_arr, item_ind, n_items: data_arr[item_ind:item_ind +
                n_items], typ.dtype(typ.dtype, types.int64, types.int64), [
                data_arr, item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), bdrjj__vlxe)
            arr_obj = c.pyapi.from_native_value(typ.dtype, dtghm__fgug, c.
                env_manager)
            pyarray_setitem(builder, context, xpkrs__mgsio, dspi__jqntt,
                arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(yku__ahq)
    c.pyapi.decref(jlm__oxast)
    c.pyapi.decref(lyjd__ebtb)
    c.pyapi.decref(ajhgb__xcx)
    return xpkrs__mgsio


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    msj__zaz = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = msj__zaz.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), msj__zaz.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), msj__zaz.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        oor__ccg = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        dywud__sqv = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        tceq__lgl = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        heg__jkl = cgutils.get_or_insert_function(c.builder.module,
            tceq__lgl, name='np_array_from_array_item_array')
        arr = c.builder.call(heg__jkl, [msj__zaz.n_arrays, c.builder.
            bitcast(dywud__sqv, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), oor__ccg)])
    else:
        arr = _box_array_item_array_generic(typ, c, msj__zaz.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    qhwdd__wry, iyafe__zla, nqgsr__teooc = args
    qnl__fji = bodo.utils.transform.get_type_alloc_counts(array_item_type.dtype
        )
    xdss__mrth = sig.args[1]
    if not isinstance(xdss__mrth, types.UniTuple):
        iyafe__zla = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for nqgsr__teooc in range(qnl__fji)])
    elif xdss__mrth.count < qnl__fji:
        iyafe__zla = cgutils.pack_array(builder, [builder.extract_value(
            iyafe__zla, rjysm__jqd) for rjysm__jqd in range(xdss__mrth.
            count)] + [lir.Constant(lir.IntType(64), -1) for nqgsr__teooc in
            range(qnl__fji - xdss__mrth.count)])
    xwbhb__pxekx, nqgsr__teooc, nqgsr__teooc, nqgsr__teooc = (
        construct_array_item_array(context, builder, array_item_type,
        qhwdd__wry, iyafe__zla))
    qxn__wub = context.make_helper(builder, array_item_type)
    qxn__wub.meminfo = xwbhb__pxekx
    return qxn__wub._getvalue()


@intrinsic
def pre_alloc_array_item_array(typingctx, num_arrs_typ, num_values_typ,
    dtype_typ=None):
    assert isinstance(num_arrs_typ, types.Integer)
    array_item_type = ArrayItemArrayType(dtype_typ.instance_type)
    num_values_typ = types.unliteral(num_values_typ)
    return array_item_type(types.int64, num_values_typ, dtype_typ
        ), lower_pre_alloc_array_item_array


def pre_alloc_array_item_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_array_item_arr_ext_pre_alloc_array_item_array
    ) = pre_alloc_array_item_array_equiv


def init_array_item_array_codegen(context, builder, signature, args):
    n_arrays, hymdp__trxo, vnkcq__aqzhy, qgh__uxwrr = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    mrpdh__lpdgx = context.get_value_type(payload_type)
    qwxs__qhcr = context.get_abi_sizeof(mrpdh__lpdgx)
    cuv__bduv = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    xwbhb__pxekx = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, qwxs__qhcr), cuv__bduv)
    izoet__edkdb = context.nrt.meminfo_data(builder, xwbhb__pxekx)
    alelq__lgw = builder.bitcast(izoet__edkdb, mrpdh__lpdgx.as_pointer())
    msj__zaz = cgutils.create_struct_proxy(payload_type)(context, builder)
    msj__zaz.n_arrays = n_arrays
    msj__zaz.data = hymdp__trxo
    msj__zaz.offsets = vnkcq__aqzhy
    msj__zaz.null_bitmap = qgh__uxwrr
    builder.store(msj__zaz._getvalue(), alelq__lgw)
    context.nrt.incref(builder, signature.args[1], hymdp__trxo)
    context.nrt.incref(builder, signature.args[2], vnkcq__aqzhy)
    context.nrt.incref(builder, signature.args[3], qgh__uxwrr)
    qxn__wub = context.make_helper(builder, array_item_type)
    qxn__wub.meminfo = xwbhb__pxekx
    return qxn__wub._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    fas__mmfck = ArrayItemArrayType(data_type)
    sig = fas__mmfck(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        msj__zaz = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            msj__zaz.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        msj__zaz = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        dywud__sqv = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, msj__zaz.offsets).data
        vnkcq__aqzhy = builder.bitcast(dywud__sqv, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(vnkcq__aqzhy, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        msj__zaz = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            msj__zaz.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        msj__zaz = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            msj__zaz.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


def alias_ext_single_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_offsets',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_data',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_null_bitmap',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array


@intrinsic
def get_n_arrays(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        msj__zaz = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return msj__zaz.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, slrh__vxucs = args
        qxn__wub = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        izoet__edkdb = context.nrt.meminfo_data(builder, qxn__wub.meminfo)
        alelq__lgw = builder.bitcast(izoet__edkdb, context.get_value_type(
            payload_type).as_pointer())
        msj__zaz = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(alelq__lgw))
        context.nrt.decref(builder, data_typ, msj__zaz.data)
        msj__zaz.data = slrh__vxucs
        context.nrt.incref(builder, data_typ, slrh__vxucs)
        builder.store(msj__zaz._getvalue(), alelq__lgw)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    hymdp__trxo = get_data(arr)
    ldgg__cch = len(hymdp__trxo)
    if ldgg__cch < new_size:
        gpiux__rnrb = max(2 * ldgg__cch, new_size)
        slrh__vxucs = bodo.libs.array_kernels.resize_and_copy(hymdp__trxo,
            old_size, gpiux__rnrb)
        replace_data_arr(arr, slrh__vxucs)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    hymdp__trxo = get_data(arr)
    vnkcq__aqzhy = get_offsets(arr)
    xiodv__gmyo = len(hymdp__trxo)
    giau__iyi = vnkcq__aqzhy[-1]
    if xiodv__gmyo != giau__iyi:
        slrh__vxucs = bodo.libs.array_kernels.resize_and_copy(hymdp__trxo,
            giau__iyi, giau__iyi)
        replace_data_arr(arr, slrh__vxucs)


@overload(len, no_unliteral=True)
def overload_array_item_arr_len(A):
    if isinstance(A, ArrayItemArrayType):
        return lambda A: get_n_arrays(A)


@overload_attribute(ArrayItemArrayType, 'shape')
def overload_array_item_arr_shape(A):
    return lambda A: (get_n_arrays(A),)


@overload_attribute(ArrayItemArrayType, 'dtype')
def overload_array_item_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(ArrayItemArrayType, 'ndim')
def overload_array_item_arr_ndim(A):
    return lambda A: 1


@overload_attribute(ArrayItemArrayType, 'nbytes')
def overload_array_item_arr_nbytes(A):
    return lambda A: get_data(A).nbytes + get_offsets(A
        ).nbytes + get_null_bitmap(A).nbytes


@overload(operator.getitem, no_unliteral=True)
def array_item_arr_getitem_array(arr, ind):
    if not isinstance(arr, ArrayItemArrayType):
        return
    if isinstance(ind, types.Integer):

        def array_item_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            vnkcq__aqzhy = get_offsets(arr)
            hymdp__trxo = get_data(arr)
            ygxl__htks = vnkcq__aqzhy[ind]
            glj__ocro = vnkcq__aqzhy[ind + 1]
            return hymdp__trxo[ygxl__htks:glj__ocro]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        ykrk__fgibj = arr.dtype

        def impl_bool(arr, ind):
            fglcm__tehaa = len(arr)
            if fglcm__tehaa != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            qgh__uxwrr = get_null_bitmap(arr)
            n_arrays = 0
            tlc__gpfkg = init_nested_counts(ykrk__fgibj)
            for rjysm__jqd in range(fglcm__tehaa):
                if ind[rjysm__jqd]:
                    n_arrays += 1
                    wsepz__ocke = arr[rjysm__jqd]
                    tlc__gpfkg = add_nested_counts(tlc__gpfkg, wsepz__ocke)
            xpkrs__mgsio = pre_alloc_array_item_array(n_arrays, tlc__gpfkg,
                ykrk__fgibj)
            qrsvt__zmp = get_null_bitmap(xpkrs__mgsio)
            nom__vgomg = 0
            for jjazb__ydc in range(fglcm__tehaa):
                if ind[jjazb__ydc]:
                    xpkrs__mgsio[nom__vgomg] = arr[jjazb__ydc]
                    iwwmp__feekj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        qgh__uxwrr, jjazb__ydc)
                    bodo.libs.int_arr_ext.set_bit_to_arr(qrsvt__zmp,
                        nom__vgomg, iwwmp__feekj)
                    nom__vgomg += 1
            return xpkrs__mgsio
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        ykrk__fgibj = arr.dtype

        def impl_int(arr, ind):
            qgh__uxwrr = get_null_bitmap(arr)
            fglcm__tehaa = len(ind)
            n_arrays = fglcm__tehaa
            tlc__gpfkg = init_nested_counts(ykrk__fgibj)
            for iiiz__ecbgv in range(fglcm__tehaa):
                rjysm__jqd = ind[iiiz__ecbgv]
                wsepz__ocke = arr[rjysm__jqd]
                tlc__gpfkg = add_nested_counts(tlc__gpfkg, wsepz__ocke)
            xpkrs__mgsio = pre_alloc_array_item_array(n_arrays, tlc__gpfkg,
                ykrk__fgibj)
            qrsvt__zmp = get_null_bitmap(xpkrs__mgsio)
            for biqn__cjml in range(fglcm__tehaa):
                jjazb__ydc = ind[biqn__cjml]
                xpkrs__mgsio[biqn__cjml] = arr[jjazb__ydc]
                iwwmp__feekj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    qgh__uxwrr, jjazb__ydc)
                bodo.libs.int_arr_ext.set_bit_to_arr(qrsvt__zmp, biqn__cjml,
                    iwwmp__feekj)
            return xpkrs__mgsio
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            fglcm__tehaa = len(arr)
            wowrr__yoce = numba.cpython.unicode._normalize_slice(ind,
                fglcm__tehaa)
            pkuil__pobis = np.arange(wowrr__yoce.start, wowrr__yoce.stop,
                wowrr__yoce.step)
            return arr[pkuil__pobis]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            vnkcq__aqzhy = get_offsets(A)
            qgh__uxwrr = get_null_bitmap(A)
            if idx == 0:
                vnkcq__aqzhy[0] = 0
            n_items = len(val)
            mjfvx__kjjsh = vnkcq__aqzhy[idx] + n_items
            ensure_data_capacity(A, vnkcq__aqzhy[idx], mjfvx__kjjsh)
            hymdp__trxo = get_data(A)
            vnkcq__aqzhy[idx + 1] = vnkcq__aqzhy[idx] + n_items
            hymdp__trxo[vnkcq__aqzhy[idx]:vnkcq__aqzhy[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(qgh__uxwrr, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            wowrr__yoce = numba.cpython.unicode._normalize_slice(idx, len(A))
            for rjysm__jqd in range(wowrr__yoce.start, wowrr__yoce.stop,
                wowrr__yoce.step):
                A[rjysm__jqd] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            vnkcq__aqzhy = get_offsets(A)
            qgh__uxwrr = get_null_bitmap(A)
            vsr__wgzp = get_offsets(val)
            chkp__rjko = get_data(val)
            ivr__koi = get_null_bitmap(val)
            fglcm__tehaa = len(A)
            wowrr__yoce = numba.cpython.unicode._normalize_slice(idx,
                fglcm__tehaa)
            hjn__yhv, exbh__fmc = wowrr__yoce.start, wowrr__yoce.stop
            assert wowrr__yoce.step == 1
            if hjn__yhv == 0:
                vnkcq__aqzhy[hjn__yhv] = 0
            lpp__lmqz = vnkcq__aqzhy[hjn__yhv]
            mjfvx__kjjsh = lpp__lmqz + len(chkp__rjko)
            ensure_data_capacity(A, lpp__lmqz, mjfvx__kjjsh)
            hymdp__trxo = get_data(A)
            hymdp__trxo[lpp__lmqz:lpp__lmqz + len(chkp__rjko)] = chkp__rjko
            vnkcq__aqzhy[hjn__yhv:exbh__fmc + 1] = vsr__wgzp + lpp__lmqz
            facn__nkqqi = 0
            for rjysm__jqd in range(hjn__yhv, exbh__fmc):
                iwwmp__feekj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    ivr__koi, facn__nkqqi)
                bodo.libs.int_arr_ext.set_bit_to_arr(qgh__uxwrr, rjysm__jqd,
                    iwwmp__feekj)
                facn__nkqqi += 1
        return impl_slice
    raise BodoError(
        'only setitem with scalar index is currently supported for list arrays'
        )


@overload_method(ArrayItemArrayType, 'copy', no_unliteral=True)
def overload_array_item_arr_copy(A):

    def copy_impl(A):
        return init_array_item_array(len(A), get_data(A).copy(),
            get_offsets(A).copy(), get_null_bitmap(A).copy())
    return copy_impl
