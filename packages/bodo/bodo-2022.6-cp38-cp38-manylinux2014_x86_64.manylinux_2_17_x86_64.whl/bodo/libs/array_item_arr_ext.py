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
        ladvn__gaxud = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, ladvn__gaxud)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        ladvn__gaxud = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, ladvn__gaxud)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    zle__dyap = builder.module
    sru__ogxja = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    laihr__uovm = cgutils.get_or_insert_function(zle__dyap, sru__ogxja,
        name='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not laihr__uovm.is_declaration:
        return laihr__uovm
    laihr__uovm.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(laihr__uovm.append_basic_block())
    lentt__rdaz = laihr__uovm.args[0]
    bfwdw__twd = context.get_value_type(payload_type).as_pointer()
    ynpp__qll = builder.bitcast(lentt__rdaz, bfwdw__twd)
    agy__ctcz = context.make_helper(builder, payload_type, ref=ynpp__qll)
    context.nrt.decref(builder, array_item_type.dtype, agy__ctcz.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'), agy__ctcz
        .offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), agy__ctcz
        .null_bitmap)
    builder.ret_void()
    return laihr__uovm


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    axwbs__hijh = context.get_value_type(payload_type)
    batc__ouefl = context.get_abi_sizeof(axwbs__hijh)
    qkrjl__rsdpv = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    jkb__xjb = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, batc__ouefl), qkrjl__rsdpv)
    fpo__ylkzf = context.nrt.meminfo_data(builder, jkb__xjb)
    ooxf__lqpgr = builder.bitcast(fpo__ylkzf, axwbs__hijh.as_pointer())
    agy__ctcz = cgutils.create_struct_proxy(payload_type)(context, builder)
    agy__ctcz.n_arrays = n_arrays
    cdd__sah = n_elems.type.count
    chy__vdc = builder.extract_value(n_elems, 0)
    tiwxw__pwllf = cgutils.alloca_once_value(builder, chy__vdc)
    hfv__tvj = builder.icmp_signed('==', chy__vdc, lir.Constant(chy__vdc.
        type, -1))
    with builder.if_then(hfv__tvj):
        builder.store(n_arrays, tiwxw__pwllf)
    n_elems = cgutils.pack_array(builder, [builder.load(tiwxw__pwllf)] + [
        builder.extract_value(n_elems, eqonc__qkjlt) for eqonc__qkjlt in
        range(1, cdd__sah)])
    agy__ctcz.data = gen_allocate_array(context, builder, array_item_type.
        dtype, n_elems, c)
    wij__eowh = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    rfy__nxrgy = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [wij__eowh])
    offsets_ptr = rfy__nxrgy.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    agy__ctcz.offsets = rfy__nxrgy._getvalue()
    taljj__nuas = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    ewbg__cebh = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [taljj__nuas])
    null_bitmap_ptr = ewbg__cebh.data
    agy__ctcz.null_bitmap = ewbg__cebh._getvalue()
    builder.store(agy__ctcz._getvalue(), ooxf__lqpgr)
    return jkb__xjb, agy__ctcz.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    vmcwt__gkca, mijj__hdvkk = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    vqoxo__fkz = context.insert_const_string(builder.module, 'pandas')
    pdyj__utanz = c.pyapi.import_module_noblock(vqoxo__fkz)
    mcg__adt = c.pyapi.object_getattr_string(pdyj__utanz, 'NA')
    muu__ycxvi = c.context.get_constant(offset_type, 0)
    builder.store(muu__ycxvi, offsets_ptr)
    lviq__slvon = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as kdfto__cku:
        xylwi__ovt = kdfto__cku.index
        item_ind = builder.load(lviq__slvon)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [xylwi__ovt]))
        arr_obj = seq_getitem(builder, context, val, xylwi__ovt)
        set_bitmap_bit(builder, null_bitmap_ptr, xylwi__ovt, 0)
        bte__mblk = is_na_value(builder, context, arr_obj, mcg__adt)
        mjfd__eate = builder.icmp_unsigned('!=', bte__mblk, lir.Constant(
            bte__mblk.type, 1))
        with builder.if_then(mjfd__eate):
            set_bitmap_bit(builder, null_bitmap_ptr, xylwi__ovt, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), lviq__slvon)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(lviq__slvon), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(pdyj__utanz)
    c.pyapi.decref(mcg__adt)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    ege__krv = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types
        .int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if ege__krv:
        sru__ogxja = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        lajae__olwyd = cgutils.get_or_insert_function(c.builder.module,
            sru__ogxja, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(
            lajae__olwyd, [val])])
    else:
        qybs__sic = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            qybs__sic, eqonc__qkjlt) for eqonc__qkjlt in range(1, qybs__sic
            .type.count)])
    jkb__xjb, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if ege__krv:
        xxrh__muyl = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        avgce__rthww = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        sru__ogxja = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        laihr__uovm = cgutils.get_or_insert_function(c.builder.module,
            sru__ogxja, name='array_item_array_from_sequence')
        c.builder.call(laihr__uovm, [val, c.builder.bitcast(avgce__rthww,
            lir.IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir
            .Constant(lir.IntType(32), xxrh__muyl)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    fgets__zfevz = c.context.make_helper(c.builder, typ)
    fgets__zfevz.meminfo = jkb__xjb
    iuusc__gfq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(fgets__zfevz._getvalue(), is_error=iuusc__gfq)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    fgets__zfevz = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    fpo__ylkzf = context.nrt.meminfo_data(builder, fgets__zfevz.meminfo)
    ooxf__lqpgr = builder.bitcast(fpo__ylkzf, context.get_value_type(
        payload_type).as_pointer())
    agy__ctcz = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(ooxf__lqpgr))
    return agy__ctcz


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    vqoxo__fkz = context.insert_const_string(builder.module, 'numpy')
    orbo__gxkm = c.pyapi.import_module_noblock(vqoxo__fkz)
    usy__xre = c.pyapi.object_getattr_string(orbo__gxkm, 'object_')
    wat__bndjs = c.pyapi.long_from_longlong(n_arrays)
    omccv__aac = c.pyapi.call_method(orbo__gxkm, 'ndarray', (wat__bndjs,
        usy__xre))
    fgvid__tit = c.pyapi.object_getattr_string(orbo__gxkm, 'nan')
    lviq__slvon = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as kdfto__cku:
        xylwi__ovt = kdfto__cku.index
        pyarray_setitem(builder, context, omccv__aac, xylwi__ovt, fgvid__tit)
        lbqwq__gxql = get_bitmap_bit(builder, null_bitmap_ptr, xylwi__ovt)
        wgyea__cxy = builder.icmp_unsigned('!=', lbqwq__gxql, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(wgyea__cxy):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(xylwi__ovt, lir.Constant(
                xylwi__ovt.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [xylwi__ovt]))), lir.IntType(64))
            item_ind = builder.load(lviq__slvon)
            vmcwt__gkca, sgxdm__uvhz = c.pyapi.call_jit_code(lambda
                data_arr, item_ind, n_items: data_arr[item_ind:item_ind +
                n_items], typ.dtype(typ.dtype, types.int64, types.int64), [
                data_arr, item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), lviq__slvon)
            arr_obj = c.pyapi.from_native_value(typ.dtype, sgxdm__uvhz, c.
                env_manager)
            pyarray_setitem(builder, context, omccv__aac, xylwi__ovt, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(orbo__gxkm)
    c.pyapi.decref(usy__xre)
    c.pyapi.decref(wat__bndjs)
    c.pyapi.decref(fgvid__tit)
    return omccv__aac


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    agy__ctcz = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = agy__ctcz.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), agy__ctcz.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), agy__ctcz.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        xxrh__muyl = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        avgce__rthww = c.context.make_helper(c.builder, typ.dtype, data_arr
            ).data
        sru__ogxja = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        tvu__zupcy = cgutils.get_or_insert_function(c.builder.module,
            sru__ogxja, name='np_array_from_array_item_array')
        arr = c.builder.call(tvu__zupcy, [agy__ctcz.n_arrays, c.builder.
            bitcast(avgce__rthww, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), xxrh__muyl)])
    else:
        arr = _box_array_item_array_generic(typ, c, agy__ctcz.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    pdhl__revel, umo__orfl, xujln__gjkz = args
    iblku__qxtm = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    lwpr__zwzz = sig.args[1]
    if not isinstance(lwpr__zwzz, types.UniTuple):
        umo__orfl = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for xujln__gjkz in range(iblku__qxtm)])
    elif lwpr__zwzz.count < iblku__qxtm:
        umo__orfl = cgutils.pack_array(builder, [builder.extract_value(
            umo__orfl, eqonc__qkjlt) for eqonc__qkjlt in range(lwpr__zwzz.
            count)] + [lir.Constant(lir.IntType(64), -1) for xujln__gjkz in
            range(iblku__qxtm - lwpr__zwzz.count)])
    jkb__xjb, xujln__gjkz, xujln__gjkz, xujln__gjkz = (
        construct_array_item_array(context, builder, array_item_type,
        pdhl__revel, umo__orfl))
    fgets__zfevz = context.make_helper(builder, array_item_type)
    fgets__zfevz.meminfo = jkb__xjb
    return fgets__zfevz._getvalue()


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
    n_arrays, feg__ikd, rfy__nxrgy, ewbg__cebh = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    axwbs__hijh = context.get_value_type(payload_type)
    batc__ouefl = context.get_abi_sizeof(axwbs__hijh)
    qkrjl__rsdpv = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    jkb__xjb = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, batc__ouefl), qkrjl__rsdpv)
    fpo__ylkzf = context.nrt.meminfo_data(builder, jkb__xjb)
    ooxf__lqpgr = builder.bitcast(fpo__ylkzf, axwbs__hijh.as_pointer())
    agy__ctcz = cgutils.create_struct_proxy(payload_type)(context, builder)
    agy__ctcz.n_arrays = n_arrays
    agy__ctcz.data = feg__ikd
    agy__ctcz.offsets = rfy__nxrgy
    agy__ctcz.null_bitmap = ewbg__cebh
    builder.store(agy__ctcz._getvalue(), ooxf__lqpgr)
    context.nrt.incref(builder, signature.args[1], feg__ikd)
    context.nrt.incref(builder, signature.args[2], rfy__nxrgy)
    context.nrt.incref(builder, signature.args[3], ewbg__cebh)
    fgets__zfevz = context.make_helper(builder, array_item_type)
    fgets__zfevz.meminfo = jkb__xjb
    return fgets__zfevz._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    aeyaw__qnm = ArrayItemArrayType(data_type)
    sig = aeyaw__qnm(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        agy__ctcz = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            agy__ctcz.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        agy__ctcz = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        avgce__rthww = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, agy__ctcz.offsets).data
        rfy__nxrgy = builder.bitcast(avgce__rthww, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(rfy__nxrgy, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        agy__ctcz = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            agy__ctcz.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        agy__ctcz = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            agy__ctcz.null_bitmap)
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
        agy__ctcz = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return agy__ctcz.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, itk__ehp = args
        fgets__zfevz = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        fpo__ylkzf = context.nrt.meminfo_data(builder, fgets__zfevz.meminfo)
        ooxf__lqpgr = builder.bitcast(fpo__ylkzf, context.get_value_type(
            payload_type).as_pointer())
        agy__ctcz = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(ooxf__lqpgr))
        context.nrt.decref(builder, data_typ, agy__ctcz.data)
        agy__ctcz.data = itk__ehp
        context.nrt.incref(builder, data_typ, itk__ehp)
        builder.store(agy__ctcz._getvalue(), ooxf__lqpgr)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    feg__ikd = get_data(arr)
    tren__dfej = len(feg__ikd)
    if tren__dfej < new_size:
        otxa__iax = max(2 * tren__dfej, new_size)
        itk__ehp = bodo.libs.array_kernels.resize_and_copy(feg__ikd,
            old_size, otxa__iax)
        replace_data_arr(arr, itk__ehp)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    feg__ikd = get_data(arr)
    rfy__nxrgy = get_offsets(arr)
    ycp__gntmi = len(feg__ikd)
    oknki__avjw = rfy__nxrgy[-1]
    if ycp__gntmi != oknki__avjw:
        itk__ehp = bodo.libs.array_kernels.resize_and_copy(feg__ikd,
            oknki__avjw, oknki__avjw)
        replace_data_arr(arr, itk__ehp)


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
            rfy__nxrgy = get_offsets(arr)
            feg__ikd = get_data(arr)
            bws__grf = rfy__nxrgy[ind]
            cimn__sabn = rfy__nxrgy[ind + 1]
            return feg__ikd[bws__grf:cimn__sabn]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        asgb__nugze = arr.dtype

        def impl_bool(arr, ind):
            ntck__gvvqv = len(arr)
            if ntck__gvvqv != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            ewbg__cebh = get_null_bitmap(arr)
            n_arrays = 0
            pxf__yqakw = init_nested_counts(asgb__nugze)
            for eqonc__qkjlt in range(ntck__gvvqv):
                if ind[eqonc__qkjlt]:
                    n_arrays += 1
                    rhox__ixmww = arr[eqonc__qkjlt]
                    pxf__yqakw = add_nested_counts(pxf__yqakw, rhox__ixmww)
            omccv__aac = pre_alloc_array_item_array(n_arrays, pxf__yqakw,
                asgb__nugze)
            eka__snqjv = get_null_bitmap(omccv__aac)
            pmq__thxnq = 0
            for fdv__ojb in range(ntck__gvvqv):
                if ind[fdv__ojb]:
                    omccv__aac[pmq__thxnq] = arr[fdv__ojb]
                    eoh__are = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ewbg__cebh, fdv__ojb)
                    bodo.libs.int_arr_ext.set_bit_to_arr(eka__snqjv,
                        pmq__thxnq, eoh__are)
                    pmq__thxnq += 1
            return omccv__aac
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        asgb__nugze = arr.dtype

        def impl_int(arr, ind):
            ewbg__cebh = get_null_bitmap(arr)
            ntck__gvvqv = len(ind)
            n_arrays = ntck__gvvqv
            pxf__yqakw = init_nested_counts(asgb__nugze)
            for pjjjm__mklp in range(ntck__gvvqv):
                eqonc__qkjlt = ind[pjjjm__mklp]
                rhox__ixmww = arr[eqonc__qkjlt]
                pxf__yqakw = add_nested_counts(pxf__yqakw, rhox__ixmww)
            omccv__aac = pre_alloc_array_item_array(n_arrays, pxf__yqakw,
                asgb__nugze)
            eka__snqjv = get_null_bitmap(omccv__aac)
            for gnuh__tcgws in range(ntck__gvvqv):
                fdv__ojb = ind[gnuh__tcgws]
                omccv__aac[gnuh__tcgws] = arr[fdv__ojb]
                eoh__are = bodo.libs.int_arr_ext.get_bit_bitmap_arr(ewbg__cebh,
                    fdv__ojb)
                bodo.libs.int_arr_ext.set_bit_to_arr(eka__snqjv,
                    gnuh__tcgws, eoh__are)
            return omccv__aac
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            ntck__gvvqv = len(arr)
            fhim__epbd = numba.cpython.unicode._normalize_slice(ind,
                ntck__gvvqv)
            jfl__rrzb = np.arange(fhim__epbd.start, fhim__epbd.stop,
                fhim__epbd.step)
            return arr[jfl__rrzb]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            rfy__nxrgy = get_offsets(A)
            ewbg__cebh = get_null_bitmap(A)
            if idx == 0:
                rfy__nxrgy[0] = 0
            n_items = len(val)
            jndnv__naf = rfy__nxrgy[idx] + n_items
            ensure_data_capacity(A, rfy__nxrgy[idx], jndnv__naf)
            feg__ikd = get_data(A)
            rfy__nxrgy[idx + 1] = rfy__nxrgy[idx] + n_items
            feg__ikd[rfy__nxrgy[idx]:rfy__nxrgy[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(ewbg__cebh, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            fhim__epbd = numba.cpython.unicode._normalize_slice(idx, len(A))
            for eqonc__qkjlt in range(fhim__epbd.start, fhim__epbd.stop,
                fhim__epbd.step):
                A[eqonc__qkjlt] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            rfy__nxrgy = get_offsets(A)
            ewbg__cebh = get_null_bitmap(A)
            otww__toa = get_offsets(val)
            fsdp__zfeo = get_data(val)
            mmsfm__qyoa = get_null_bitmap(val)
            ntck__gvvqv = len(A)
            fhim__epbd = numba.cpython.unicode._normalize_slice(idx,
                ntck__gvvqv)
            zwyes__gfz, kpdbd__ijcdo = fhim__epbd.start, fhim__epbd.stop
            assert fhim__epbd.step == 1
            if zwyes__gfz == 0:
                rfy__nxrgy[zwyes__gfz] = 0
            vwrml__exgk = rfy__nxrgy[zwyes__gfz]
            jndnv__naf = vwrml__exgk + len(fsdp__zfeo)
            ensure_data_capacity(A, vwrml__exgk, jndnv__naf)
            feg__ikd = get_data(A)
            feg__ikd[vwrml__exgk:vwrml__exgk + len(fsdp__zfeo)] = fsdp__zfeo
            rfy__nxrgy[zwyes__gfz:kpdbd__ijcdo + 1] = otww__toa + vwrml__exgk
            jolc__ovt = 0
            for eqonc__qkjlt in range(zwyes__gfz, kpdbd__ijcdo):
                eoh__are = bodo.libs.int_arr_ext.get_bit_bitmap_arr(mmsfm__qyoa
                    , jolc__ovt)
                bodo.libs.int_arr_ext.set_bit_to_arr(ewbg__cebh,
                    eqonc__qkjlt, eoh__are)
                jolc__ovt += 1
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
