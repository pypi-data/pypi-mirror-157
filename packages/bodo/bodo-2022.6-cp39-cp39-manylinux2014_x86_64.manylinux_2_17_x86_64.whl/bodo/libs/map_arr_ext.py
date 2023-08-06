"""Array implementation for map values.
Corresponds to Spark's MapType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Map arrays: https://github.com/apache/arrow/blob/master/format/Schema.fbs

The implementation uses an array(struct) array underneath similar to Spark and Arrow.
For example: [{1: 2.1, 3: 1.1}, {5: -1.0}]
[[{"key": 1, "value" 2.1}, {"key": 3, "value": 1.1}], [{"key": 5, "value": -1.0}]]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, _get_array_item_arr_payload, offset_type
from bodo.libs.struct_arr_ext import StructArrayType, _get_struct_arr_payload
from bodo.utils.cg_helpers import dict_keys, dict_merge_from_seq2, dict_values, gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit
from bodo.utils.typing import BodoError
from bodo.libs import array_ext, hdist
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('map_array_from_sequence', array_ext.map_array_from_sequence)
ll.add_symbol('np_array_from_map_array', array_ext.np_array_from_map_array)


class MapArrayType(types.ArrayCompatible):

    def __init__(self, key_arr_type, value_arr_type):
        self.key_arr_type = key_arr_type
        self.value_arr_type = value_arr_type
        super(MapArrayType, self).__init__(name='MapArrayType({}, {})'.
            format(key_arr_type, value_arr_type))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.DictType(self.key_arr_type.dtype, self.value_arr_type.
            dtype)

    def copy(self):
        return MapArrayType(self.key_arr_type, self.value_arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_map_arr_data_type(map_type):
    vedqa__ydjy = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(vedqa__ydjy)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ijvt__lfue = _get_map_arr_data_type(fe_type)
        tekuq__tcumv = [('data', ijvt__lfue)]
        models.StructModel.__init__(self, dmm, fe_type, tekuq__tcumv)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    mcdv__vdggq = all(isinstance(ozyhy__ocmp, types.Array) and ozyhy__ocmp.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for ozyhy__ocmp in (typ.key_arr_type, typ.
        value_arr_type))
    if mcdv__vdggq:
        mcn__bvwq = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        fxwoc__uwxix = cgutils.get_or_insert_function(c.builder.module,
            mcn__bvwq, name='count_total_elems_list_array')
        kzd__rau = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            fxwoc__uwxix, [val])])
    else:
        kzd__rau = get_array_elem_counts(c, c.builder, c.context, val, typ)
    ijvt__lfue = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, ijvt__lfue, kzd__rau, c
        )
    yuzyc__rqva = _get_array_item_arr_payload(c.context, c.builder,
        ijvt__lfue, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, yuzyc__rqva.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, yuzyc__rqva.offsets).data
    ajdk__kuxc = _get_struct_arr_payload(c.context, c.builder, ijvt__lfue.
        dtype, yuzyc__rqva.data)
    key_arr = c.builder.extract_value(ajdk__kuxc.data, 0)
    value_arr = c.builder.extract_value(ajdk__kuxc.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    ocyl__vwsae, hudt__idqd = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [ajdk__kuxc.null_bitmap])
    if mcdv__vdggq:
        utnr__keyny = c.context.make_array(ijvt__lfue.dtype.data[0])(c.
            context, c.builder, key_arr).data
        qeyyq__zjeej = c.context.make_array(ijvt__lfue.dtype.data[1])(c.
            context, c.builder, value_arr).data
        mcn__bvwq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        vdctl__vjs = cgutils.get_or_insert_function(c.builder.module,
            mcn__bvwq, name='map_array_from_sequence')
        pwa__mxgmg = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        vghlh__zal = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(vdctl__vjs, [val, c.builder.bitcast(utnr__keyny, lir
            .IntType(8).as_pointer()), c.builder.bitcast(qeyyq__zjeej, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), pwa__mxgmg), lir.Constant(lir.IntType
            (32), vghlh__zal)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    pdqyp__dql = c.context.make_helper(c.builder, typ)
    pdqyp__dql.data = data_arr
    pln__ciczo = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(pdqyp__dql._getvalue(), is_error=pln__ciczo)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    hoce__oeg = context.insert_const_string(builder.module, 'pandas')
    xufe__lgzxu = c.pyapi.import_module_noblock(hoce__oeg)
    lynh__ygz = c.pyapi.object_getattr_string(xufe__lgzxu, 'NA')
    lkn__zhn = c.context.get_constant(offset_type, 0)
    builder.store(lkn__zhn, offsets_ptr)
    adme__dxtd = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as jcp__zccag:
        jrt__dcazo = jcp__zccag.index
        item_ind = builder.load(adme__dxtd)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [jrt__dcazo]))
        thy__cvqp = seq_getitem(builder, context, val, jrt__dcazo)
        set_bitmap_bit(builder, null_bitmap_ptr, jrt__dcazo, 0)
        sfxnc__cuvsm = is_na_value(builder, context, thy__cvqp, lynh__ygz)
        ycp__rpx = builder.icmp_unsigned('!=', sfxnc__cuvsm, lir.Constant(
            sfxnc__cuvsm.type, 1))
        with builder.if_then(ycp__rpx):
            set_bitmap_bit(builder, null_bitmap_ptr, jrt__dcazo, 1)
            ubusk__dxpz = dict_keys(builder, context, thy__cvqp)
            ssw__epae = dict_values(builder, context, thy__cvqp)
            n_items = bodo.utils.utils.object_length(c, ubusk__dxpz)
            _unbox_array_item_array_copy_data(typ.key_arr_type, ubusk__dxpz,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type, ssw__epae,
                c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), adme__dxtd)
            c.pyapi.decref(ubusk__dxpz)
            c.pyapi.decref(ssw__epae)
        c.pyapi.decref(thy__cvqp)
    builder.store(builder.trunc(builder.load(adme__dxtd), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(xufe__lgzxu)
    c.pyapi.decref(lynh__ygz)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    pdqyp__dql = c.context.make_helper(c.builder, typ, val)
    data_arr = pdqyp__dql.data
    ijvt__lfue = _get_map_arr_data_type(typ)
    yuzyc__rqva = _get_array_item_arr_payload(c.context, c.builder,
        ijvt__lfue, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, yuzyc__rqva.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, yuzyc__rqva.offsets).data
    ajdk__kuxc = _get_struct_arr_payload(c.context, c.builder, ijvt__lfue.
        dtype, yuzyc__rqva.data)
    key_arr = c.builder.extract_value(ajdk__kuxc.data, 0)
    value_arr = c.builder.extract_value(ajdk__kuxc.data, 1)
    if all(isinstance(ozyhy__ocmp, types.Array) and ozyhy__ocmp.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type) for
        ozyhy__ocmp in (typ.key_arr_type, typ.value_arr_type)):
        utnr__keyny = c.context.make_array(ijvt__lfue.dtype.data[0])(c.
            context, c.builder, key_arr).data
        qeyyq__zjeej = c.context.make_array(ijvt__lfue.dtype.data[1])(c.
            context, c.builder, value_arr).data
        mcn__bvwq = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        dqn__zqqxv = cgutils.get_or_insert_function(c.builder.module,
            mcn__bvwq, name='np_array_from_map_array')
        pwa__mxgmg = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        vghlh__zal = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(dqn__zqqxv, [yuzyc__rqva.n_arrays, c.builder.
            bitcast(utnr__keyny, lir.IntType(8).as_pointer()), c.builder.
            bitcast(qeyyq__zjeej, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), pwa__mxgmg), lir
            .Constant(lir.IntType(32), vghlh__zal)])
    else:
        arr = _box_map_array_generic(typ, c, yuzyc__rqva.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    hoce__oeg = context.insert_const_string(builder.module, 'numpy')
    qbzqf__caw = c.pyapi.import_module_noblock(hoce__oeg)
    oah__uisj = c.pyapi.object_getattr_string(qbzqf__caw, 'object_')
    utmac__phx = c.pyapi.long_from_longlong(n_maps)
    bna__ojag = c.pyapi.call_method(qbzqf__caw, 'ndarray', (utmac__phx,
        oah__uisj))
    pmmlu__xjr = c.pyapi.object_getattr_string(qbzqf__caw, 'nan')
    wfsi__uqxv = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    adme__dxtd = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as jcp__zccag:
        fvpxr__ohdt = jcp__zccag.index
        pyarray_setitem(builder, context, bna__ojag, fvpxr__ohdt, pmmlu__xjr)
        uba__oeve = get_bitmap_bit(builder, null_bitmap_ptr, fvpxr__ohdt)
        qlwik__mez = builder.icmp_unsigned('!=', uba__oeve, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(qlwik__mez):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(fvpxr__ohdt, lir.Constant(
                fvpxr__ohdt.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [fvpxr__ohdt]))), lir.IntType(64))
            item_ind = builder.load(adme__dxtd)
            thy__cvqp = c.pyapi.dict_new()
            uyn__poztv = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            ocyl__vwsae, trdor__zkdl = c.pyapi.call_jit_code(uyn__poztv,
                typ.key_arr_type(typ.key_arr_type, types.int64, types.int64
                ), [key_arr, item_ind, n_items])
            ocyl__vwsae, jaju__xnu = c.pyapi.call_jit_code(uyn__poztv, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            qis__wrfi = c.pyapi.from_native_value(typ.key_arr_type,
                trdor__zkdl, c.env_manager)
            yqgrt__yhf = c.pyapi.from_native_value(typ.value_arr_type,
                jaju__xnu, c.env_manager)
            hjnz__tmmoy = c.pyapi.call_function_objargs(wfsi__uqxv, (
                qis__wrfi, yqgrt__yhf))
            dict_merge_from_seq2(builder, context, thy__cvqp, hjnz__tmmoy)
            builder.store(builder.add(item_ind, n_items), adme__dxtd)
            pyarray_setitem(builder, context, bna__ojag, fvpxr__ohdt, thy__cvqp
                )
            c.pyapi.decref(hjnz__tmmoy)
            c.pyapi.decref(qis__wrfi)
            c.pyapi.decref(yqgrt__yhf)
            c.pyapi.decref(thy__cvqp)
    c.pyapi.decref(wfsi__uqxv)
    c.pyapi.decref(qbzqf__caw)
    c.pyapi.decref(oah__uisj)
    c.pyapi.decref(utmac__phx)
    c.pyapi.decref(pmmlu__xjr)
    return bna__ojag


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    pdqyp__dql = context.make_helper(builder, sig.return_type)
    pdqyp__dql.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return pdqyp__dql._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    owt__bcn = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return owt__bcn(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    jwyy__wiesq = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(jwyy__wiesq)


def pre_alloc_map_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_map_arr_ext_pre_alloc_map_array
    ) = pre_alloc_map_array_equiv


@overload(len, no_unliteral=True)
def overload_map_arr_len(A):
    if isinstance(A, MapArrayType):
        return lambda A: len(A._data)


@overload_attribute(MapArrayType, 'shape')
def overload_map_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(MapArrayType, 'dtype')
def overload_map_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(MapArrayType, 'ndim')
def overload_map_arr_ndim(A):
    return lambda A: 1


@overload_attribute(MapArrayType, 'nbytes')
def overload_map_arr_nbytes(A):
    return lambda A: A._data.nbytes


@overload_method(MapArrayType, 'copy')
def overload_map_arr_copy(A):
    return lambda A: init_map_arr(A._data.copy())


@overload(operator.setitem, no_unliteral=True)
def map_arr_setitem(arr, ind, val):
    if not isinstance(arr, MapArrayType):
        return
    laqt__lnm = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            pll__ncvj = val.keys()
            dhrr__bbce = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), laqt__lnm, ('key', 'value'))
            for lfoan__yyq, njvz__qcs in enumerate(pll__ncvj):
                dhrr__bbce[lfoan__yyq] = bodo.libs.struct_arr_ext.init_struct((
                    njvz__qcs, val[njvz__qcs]), ('key', 'value'))
            arr._data[ind] = dhrr__bbce
        return map_arr_setitem_impl
    raise BodoError(
        'operator.setitem with MapArrays is only supported with an integer index.'
        )


@overload(operator.getitem, no_unliteral=True)
def map_arr_getitem(arr, ind):
    if not isinstance(arr, MapArrayType):
        return
    if isinstance(ind, types.Integer):

        def map_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            fcnz__odv = dict()
            xcimt__bipl = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            dhrr__bbce = bodo.libs.array_item_arr_ext.get_data(arr._data)
            shtc__sxuw, pwhbn__ril = bodo.libs.struct_arr_ext.get_data(
                dhrr__bbce)
            eaev__ogml = xcimt__bipl[ind]
            wkwb__awana = xcimt__bipl[ind + 1]
            for lfoan__yyq in range(eaev__ogml, wkwb__awana):
                fcnz__odv[shtc__sxuw[lfoan__yyq]] = pwhbn__ril[lfoan__yyq]
            return fcnz__odv
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
