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
    meq__esh = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(meq__esh)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        idov__pdpv = _get_map_arr_data_type(fe_type)
        kmnqm__txvm = [('data', idov__pdpv)]
        models.StructModel.__init__(self, dmm, fe_type, kmnqm__txvm)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    hrj__opi = all(isinstance(hzbu__qhzz, types.Array) and hzbu__qhzz.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        hzbu__qhzz in (typ.key_arr_type, typ.value_arr_type))
    if hrj__opi:
        hcner__jdip = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        uymtl__xgfj = cgutils.get_or_insert_function(c.builder.module,
            hcner__jdip, name='count_total_elems_list_array')
        lygo__pdbwf = cgutils.pack_array(c.builder, [n_maps, c.builder.call
            (uymtl__xgfj, [val])])
    else:
        lygo__pdbwf = get_array_elem_counts(c, c.builder, c.context, val, typ)
    idov__pdpv = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, idov__pdpv,
        lygo__pdbwf, c)
    iyl__nbqy = _get_array_item_arr_payload(c.context, c.builder,
        idov__pdpv, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, iyl__nbqy.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, iyl__nbqy.offsets).data
    eoxjj__qud = _get_struct_arr_payload(c.context, c.builder, idov__pdpv.
        dtype, iyl__nbqy.data)
    key_arr = c.builder.extract_value(eoxjj__qud.data, 0)
    value_arr = c.builder.extract_value(eoxjj__qud.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    frtfi__lepp, oqjk__rbt = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [eoxjj__qud.null_bitmap])
    if hrj__opi:
        mcj__wpqr = c.context.make_array(idov__pdpv.dtype.data[0])(c.
            context, c.builder, key_arr).data
        wksq__cvsco = c.context.make_array(idov__pdpv.dtype.data[1])(c.
            context, c.builder, value_arr).data
        hcner__jdip = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        xmuiy__oozk = cgutils.get_or_insert_function(c.builder.module,
            hcner__jdip, name='map_array_from_sequence')
        vvh__fnkve = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        uhat__fxtg = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(xmuiy__oozk, [val, c.builder.bitcast(mcj__wpqr, lir.
            IntType(8).as_pointer()), c.builder.bitcast(wksq__cvsco, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), vvh__fnkve), lir.Constant(lir.IntType
            (32), uhat__fxtg)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    dubyf__ekarw = c.context.make_helper(c.builder, typ)
    dubyf__ekarw.data = data_arr
    qrdvl__hoqux = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(dubyf__ekarw._getvalue(), is_error=qrdvl__hoqux)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    phkb__jput = context.insert_const_string(builder.module, 'pandas')
    xnk__dxjl = c.pyapi.import_module_noblock(phkb__jput)
    deoir__sekx = c.pyapi.object_getattr_string(xnk__dxjl, 'NA')
    tqvl__wqfz = c.context.get_constant(offset_type, 0)
    builder.store(tqvl__wqfz, offsets_ptr)
    mvd__xqrlj = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as zex__sgxpi:
        sjd__iaycg = zex__sgxpi.index
        item_ind = builder.load(mvd__xqrlj)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [sjd__iaycg]))
        bajyg__ecuz = seq_getitem(builder, context, val, sjd__iaycg)
        set_bitmap_bit(builder, null_bitmap_ptr, sjd__iaycg, 0)
        ajx__nlnu = is_na_value(builder, context, bajyg__ecuz, deoir__sekx)
        ycwz__jeyp = builder.icmp_unsigned('!=', ajx__nlnu, lir.Constant(
            ajx__nlnu.type, 1))
        with builder.if_then(ycwz__jeyp):
            set_bitmap_bit(builder, null_bitmap_ptr, sjd__iaycg, 1)
            oov__bswy = dict_keys(builder, context, bajyg__ecuz)
            cxc__gppwj = dict_values(builder, context, bajyg__ecuz)
            n_items = bodo.utils.utils.object_length(c, oov__bswy)
            _unbox_array_item_array_copy_data(typ.key_arr_type, oov__bswy,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                cxc__gppwj, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), mvd__xqrlj)
            c.pyapi.decref(oov__bswy)
            c.pyapi.decref(cxc__gppwj)
        c.pyapi.decref(bajyg__ecuz)
    builder.store(builder.trunc(builder.load(mvd__xqrlj), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(xnk__dxjl)
    c.pyapi.decref(deoir__sekx)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    dubyf__ekarw = c.context.make_helper(c.builder, typ, val)
    data_arr = dubyf__ekarw.data
    idov__pdpv = _get_map_arr_data_type(typ)
    iyl__nbqy = _get_array_item_arr_payload(c.context, c.builder,
        idov__pdpv, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, iyl__nbqy.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, iyl__nbqy.offsets).data
    eoxjj__qud = _get_struct_arr_payload(c.context, c.builder, idov__pdpv.
        dtype, iyl__nbqy.data)
    key_arr = c.builder.extract_value(eoxjj__qud.data, 0)
    value_arr = c.builder.extract_value(eoxjj__qud.data, 1)
    if all(isinstance(hzbu__qhzz, types.Array) and hzbu__qhzz.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type) for
        hzbu__qhzz in (typ.key_arr_type, typ.value_arr_type)):
        mcj__wpqr = c.context.make_array(idov__pdpv.dtype.data[0])(c.
            context, c.builder, key_arr).data
        wksq__cvsco = c.context.make_array(idov__pdpv.dtype.data[1])(c.
            context, c.builder, value_arr).data
        hcner__jdip = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        vbyf__duti = cgutils.get_or_insert_function(c.builder.module,
            hcner__jdip, name='np_array_from_map_array')
        vvh__fnkve = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        uhat__fxtg = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(vbyf__duti, [iyl__nbqy.n_arrays, c.builder.
            bitcast(mcj__wpqr, lir.IntType(8).as_pointer()), c.builder.
            bitcast(wksq__cvsco, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), vvh__fnkve), lir
            .Constant(lir.IntType(32), uhat__fxtg)])
    else:
        arr = _box_map_array_generic(typ, c, iyl__nbqy.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    phkb__jput = context.insert_const_string(builder.module, 'numpy')
    dry__ihpia = c.pyapi.import_module_noblock(phkb__jput)
    mjgh__ozqgb = c.pyapi.object_getattr_string(dry__ihpia, 'object_')
    tszf__jys = c.pyapi.long_from_longlong(n_maps)
    sutfl__iaw = c.pyapi.call_method(dry__ihpia, 'ndarray', (tszf__jys,
        mjgh__ozqgb))
    emarw__obsxp = c.pyapi.object_getattr_string(dry__ihpia, 'nan')
    bnokt__kkeln = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    mvd__xqrlj = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as zex__sgxpi:
        naliy__lul = zex__sgxpi.index
        pyarray_setitem(builder, context, sutfl__iaw, naliy__lul, emarw__obsxp)
        lnfts__pzkf = get_bitmap_bit(builder, null_bitmap_ptr, naliy__lul)
        wghj__gguy = builder.icmp_unsigned('!=', lnfts__pzkf, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(wghj__gguy):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(naliy__lul, lir.Constant(
                naliy__lul.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [naliy__lul]))), lir.IntType(64))
            item_ind = builder.load(mvd__xqrlj)
            bajyg__ecuz = c.pyapi.dict_new()
            nnh__uaer = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            frtfi__lepp, zsxv__yyvi = c.pyapi.call_jit_code(nnh__uaer, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            frtfi__lepp, dalh__aivg = c.pyapi.call_jit_code(nnh__uaer, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            ldpyh__wsaxr = c.pyapi.from_native_value(typ.key_arr_type,
                zsxv__yyvi, c.env_manager)
            utgon__tvuz = c.pyapi.from_native_value(typ.value_arr_type,
                dalh__aivg, c.env_manager)
            bwk__jmk = c.pyapi.call_function_objargs(bnokt__kkeln, (
                ldpyh__wsaxr, utgon__tvuz))
            dict_merge_from_seq2(builder, context, bajyg__ecuz, bwk__jmk)
            builder.store(builder.add(item_ind, n_items), mvd__xqrlj)
            pyarray_setitem(builder, context, sutfl__iaw, naliy__lul,
                bajyg__ecuz)
            c.pyapi.decref(bwk__jmk)
            c.pyapi.decref(ldpyh__wsaxr)
            c.pyapi.decref(utgon__tvuz)
            c.pyapi.decref(bajyg__ecuz)
    c.pyapi.decref(bnokt__kkeln)
    c.pyapi.decref(dry__ihpia)
    c.pyapi.decref(mjgh__ozqgb)
    c.pyapi.decref(tszf__jys)
    c.pyapi.decref(emarw__obsxp)
    return sutfl__iaw


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    dubyf__ekarw = context.make_helper(builder, sig.return_type)
    dubyf__ekarw.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return dubyf__ekarw._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    dmi__xuy = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return dmi__xuy(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    iib__ljf = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(num_maps
        , nested_counts, struct_typ)
    return init_map_arr(iib__ljf)


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
    tvbx__dohq = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            gjuxy__rtqae = val.keys()
            ttr__odem = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), tvbx__dohq, ('key', 'value'))
            for hfi__scwo, ydh__kqyh in enumerate(gjuxy__rtqae):
                ttr__odem[hfi__scwo] = bodo.libs.struct_arr_ext.init_struct((
                    ydh__kqyh, val[ydh__kqyh]), ('key', 'value'))
            arr._data[ind] = ttr__odem
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
            eig__edzs = dict()
            iod__xrcb = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            ttr__odem = bodo.libs.array_item_arr_ext.get_data(arr._data)
            bcdwc__qzfi, kakr__nss = bodo.libs.struct_arr_ext.get_data(
                ttr__odem)
            vdsa__txv = iod__xrcb[ind]
            kid__crgdx = iod__xrcb[ind + 1]
            for hfi__scwo in range(vdsa__txv, kid__crgdx):
                eig__edzs[bcdwc__qzfi[hfi__scwo]] = kakr__nss[hfi__scwo]
            return eig__edzs
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
