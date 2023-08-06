import operator
import llvmlite.binding as ll
import numba
import numba.core.typing.typeof
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, impl_ret_new_ref
from numba.extending import box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import offset_type
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, _memcpy, char_arr_type, get_data_ptr, null_bitmap_arr_type, offset_arr_type, string_array_type
ll.add_symbol('array_setitem', hstr_ext.array_setitem)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
ll.add_symbol('dtor_str_arr_split_view', hstr_ext.dtor_str_arr_split_view)
ll.add_symbol('str_arr_split_view_impl', hstr_ext.str_arr_split_view_impl)
ll.add_symbol('str_arr_split_view_alloc', hstr_ext.str_arr_split_view_alloc)
char_typ = types.uint8
data_ctypes_type = types.ArrayCTypes(types.Array(char_typ, 1, 'C'))
offset_ctypes_type = types.ArrayCTypes(types.Array(offset_type, 1, 'C'))


class StringArraySplitViewType(types.ArrayCompatible):

    def __init__(self):
        super(StringArraySplitViewType, self).__init__(name=
            'StringArraySplitViewType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_array_type

    def copy(self):
        return StringArraySplitViewType()


string_array_split_view_type = StringArraySplitViewType()


class StringArraySplitViewPayloadType(types.Type):

    def __init__(self):
        super(StringArraySplitViewPayloadType, self).__init__(name=
            'StringArraySplitViewPayloadType()')


str_arr_split_view_payload_type = StringArraySplitViewPayloadType()


@register_model(StringArraySplitViewPayloadType)
class StringArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        nwe__iodbs = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, nwe__iodbs)


str_arr_model_members = [('num_items', types.uint64), ('index_offsets',
    types.CPointer(offset_type)), ('data_offsets', types.CPointer(
    offset_type)), ('data', data_ctypes_type), ('null_bitmap', types.
    CPointer(char_typ)), ('meminfo', types.MemInfoPointer(
    str_arr_split_view_payload_type))]


@register_model(StringArraySplitViewType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        models.StructModel.__init__(self, dmm, fe_type, str_arr_model_members)


make_attribute_wrapper(StringArraySplitViewType, 'num_items', '_num_items')
make_attribute_wrapper(StringArraySplitViewType, 'index_offsets',
    '_index_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data_offsets',
    '_data_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data', '_data')
make_attribute_wrapper(StringArraySplitViewType, 'null_bitmap', '_null_bitmap')


def construct_str_arr_split_view(context, builder):
    qccw__zomp = context.get_value_type(str_arr_split_view_payload_type)
    cixw__sqx = context.get_abi_sizeof(qccw__zomp)
    iawz__bjf = context.get_value_type(types.voidptr)
    kchye__vbjgk = context.get_value_type(types.uintp)
    gcj__kio = lir.FunctionType(lir.VoidType(), [iawz__bjf, kchye__vbjgk,
        iawz__bjf])
    ikm__ybuo = cgutils.get_or_insert_function(builder.module, gcj__kio,
        name='dtor_str_arr_split_view')
    wyae__qldz = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, cixw__sqx), ikm__ybuo)
    zwnmd__kvi = context.nrt.meminfo_data(builder, wyae__qldz)
    npw__uyswz = builder.bitcast(zwnmd__kvi, qccw__zomp.as_pointer())
    return wyae__qldz, npw__uyswz


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        dsh__fliv, wiz__byt = args
        wyae__qldz, npw__uyswz = construct_str_arr_split_view(context, builder)
        lbtl__mbjth = _get_str_binary_arr_payload(context, builder,
            dsh__fliv, string_array_type)
        gysd__cksw = lir.FunctionType(lir.VoidType(), [npw__uyswz.type, lir
            .IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        vjg__islzl = cgutils.get_or_insert_function(builder.module,
            gysd__cksw, name='str_arr_split_view_impl')
        jtxk__omw = context.make_helper(builder, offset_arr_type,
            lbtl__mbjth.offsets).data
        owuj__mxs = context.make_helper(builder, char_arr_type, lbtl__mbjth
            .data).data
        sjvsd__gckw = context.make_helper(builder, null_bitmap_arr_type,
            lbtl__mbjth.null_bitmap).data
        odtkr__pss = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(vjg__islzl, [npw__uyswz, lbtl__mbjth.n_arrays,
            jtxk__omw, owuj__mxs, sjvsd__gckw, odtkr__pss])
        pypu__fwuo = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(npw__uyswz))
        kogvv__dum = context.make_helper(builder, string_array_split_view_type)
        kogvv__dum.num_items = lbtl__mbjth.n_arrays
        kogvv__dum.index_offsets = pypu__fwuo.index_offsets
        kogvv__dum.data_offsets = pypu__fwuo.data_offsets
        kogvv__dum.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [dsh__fliv])
        kogvv__dum.null_bitmap = pypu__fwuo.null_bitmap
        kogvv__dum.meminfo = wyae__qldz
        udd__deqkw = kogvv__dum._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, udd__deqkw)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    kcd__hak = context.make_helper(builder, string_array_split_view_type, val)
    nowh__psha = context.insert_const_string(builder.module, 'numpy')
    duvc__rvqa = c.pyapi.import_module_noblock(nowh__psha)
    dtype = c.pyapi.object_getattr_string(duvc__rvqa, 'object_')
    dkyw__cocxp = builder.sext(kcd__hak.num_items, c.pyapi.longlong)
    rsy__mid = c.pyapi.long_from_longlong(dkyw__cocxp)
    dhypk__yvbjz = c.pyapi.call_method(duvc__rvqa, 'ndarray', (rsy__mid, dtype)
        )
    hwfc__hpsz = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    ouc__hljb = c.pyapi._get_function(hwfc__hpsz, name='array_getptr1')
    sogv__gehk = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    hwyve__iknrq = c.pyapi._get_function(sogv__gehk, name='array_setitem')
    ptr__ftqic = c.pyapi.object_getattr_string(duvc__rvqa, 'nan')
    with cgutils.for_range(builder, kcd__hak.num_items) as leho__gqgt:
        str_ind = leho__gqgt.index
        cfcdl__bnynb = builder.sext(builder.load(builder.gep(kcd__hak.
            index_offsets, [str_ind])), lir.IntType(64))
        ukhoo__xaqbq = builder.sext(builder.load(builder.gep(kcd__hak.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        xpw__may = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        mhesr__ahja = builder.gep(kcd__hak.null_bitmap, [xpw__may])
        wlidl__wipln = builder.load(mhesr__ahja)
        iub__nfqe = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(wlidl__wipln, iub__nfqe), lir.
            Constant(lir.IntType(8), 1))
        abe__prxck = builder.sub(ukhoo__xaqbq, cfcdl__bnynb)
        abe__prxck = builder.sub(abe__prxck, abe__prxck.type(1))
        cgh__zqfic = builder.call(ouc__hljb, [dhypk__yvbjz, str_ind])
        hajg__imt = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(hajg__imt) as (jze__tlzf, aghw__hnrs):
            with jze__tlzf:
                cct__esn = c.pyapi.list_new(abe__prxck)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    cct__esn), likely=True):
                    with cgutils.for_range(c.builder, abe__prxck
                        ) as leho__gqgt:
                        ggw__qdr = builder.add(cfcdl__bnynb, leho__gqgt.index)
                        data_start = builder.load(builder.gep(kcd__hak.
                            data_offsets, [ggw__qdr]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        bqhrz__jzuyh = builder.load(builder.gep(kcd__hak.
                            data_offsets, [builder.add(ggw__qdr, ggw__qdr.
                            type(1))]))
                        sggw__xsgps = builder.gep(builder.extract_value(
                            kcd__hak.data, 0), [data_start])
                        pfgm__olje = builder.sext(builder.sub(bqhrz__jzuyh,
                            data_start), lir.IntType(64))
                        xwa__vlw = c.pyapi.string_from_string_and_size(
                            sggw__xsgps, pfgm__olje)
                        c.pyapi.list_setitem(cct__esn, leho__gqgt.index,
                            xwa__vlw)
                builder.call(hwyve__iknrq, [dhypk__yvbjz, cgh__zqfic, cct__esn]
                    )
            with aghw__hnrs:
                builder.call(hwyve__iknrq, [dhypk__yvbjz, cgh__zqfic,
                    ptr__ftqic])
    c.pyapi.decref(duvc__rvqa)
    c.pyapi.decref(dtype)
    c.pyapi.decref(ptr__ftqic)
    return dhypk__yvbjz


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        ulwz__lyg, krftm__xgy, sggw__xsgps = args
        wyae__qldz, npw__uyswz = construct_str_arr_split_view(context, builder)
        gysd__cksw = lir.FunctionType(lir.VoidType(), [npw__uyswz.type, lir
            .IntType(64), lir.IntType(64)])
        vjg__islzl = cgutils.get_or_insert_function(builder.module,
            gysd__cksw, name='str_arr_split_view_alloc')
        builder.call(vjg__islzl, [npw__uyswz, ulwz__lyg, krftm__xgy])
        pypu__fwuo = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(npw__uyswz))
        kogvv__dum = context.make_helper(builder, string_array_split_view_type)
        kogvv__dum.num_items = ulwz__lyg
        kogvv__dum.index_offsets = pypu__fwuo.index_offsets
        kogvv__dum.data_offsets = pypu__fwuo.data_offsets
        kogvv__dum.data = sggw__xsgps
        kogvv__dum.null_bitmap = pypu__fwuo.null_bitmap
        context.nrt.incref(builder, data_t, sggw__xsgps)
        kogvv__dum.meminfo = wyae__qldz
        udd__deqkw = kogvv__dum._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, udd__deqkw)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        xudfz__zwqvy, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            xudfz__zwqvy = builder.extract_value(xudfz__zwqvy, 0)
        return builder.bitcast(builder.gep(xudfz__zwqvy, [ind]), lir.
            IntType(8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        xudfz__zwqvy, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            xudfz__zwqvy = builder.extract_value(xudfz__zwqvy, 0)
        return builder.load(builder.gep(xudfz__zwqvy, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        xudfz__zwqvy, ind, xhzpu__vrm = args
        hroo__snyl = builder.gep(xudfz__zwqvy, [ind])
        builder.store(xhzpu__vrm, hroo__snyl)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        hevf__lggid, ind = args
        nwp__zgtrl = context.make_helper(builder, arr_ctypes_t, hevf__lggid)
        ufbb__fsai = context.make_helper(builder, arr_ctypes_t)
        ufbb__fsai.data = builder.gep(nwp__zgtrl.data, [ind])
        ufbb__fsai.meminfo = nwp__zgtrl.meminfo
        kal__cwrp = ufbb__fsai._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, kal__cwrp)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    sxa__dlpct = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not sxa__dlpct:
        return 0, 0, 0
    ggw__qdr = getitem_c_arr(arr._index_offsets, item_ind)
    uhxa__atz = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    mmcbj__fdga = uhxa__atz - ggw__qdr
    if str_ind >= mmcbj__fdga:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, ggw__qdr + str_ind)
    data_start += 1
    if ggw__qdr + str_ind == 0:
        data_start = 0
    bqhrz__jzuyh = getitem_c_arr(arr._data_offsets, ggw__qdr + str_ind + 1)
    rpi__rpnh = bqhrz__jzuyh - data_start
    return 1, data_start, rpi__rpnh


@numba.njit(no_cpython_wrapper=True)
def get_split_view_data_ptr(arr, data_start):
    return get_array_ctypes_ptr(arr._data, data_start)


@overload(len, no_unliteral=True)
def str_arr_split_view_len_overload(arr):
    if arr == string_array_split_view_type:
        return lambda arr: np.int64(arr._num_items)


@overload_attribute(StringArraySplitViewType, 'shape')
def overload_split_view_arr_shape(A):
    return lambda A: (np.int64(A._num_items),)


@overload(operator.getitem, no_unliteral=True)
def str_arr_split_view_getitem_overload(A, ind):
    if A != string_array_split_view_type:
        return
    if A == string_array_split_view_type and isinstance(ind, types.Integer):
        rkj__hhqxr = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            ggw__qdr = getitem_c_arr(A._index_offsets, ind)
            uhxa__atz = getitem_c_arr(A._index_offsets, ind + 1)
            tydj__wrl = uhxa__atz - ggw__qdr - 1
            dsh__fliv = bodo.libs.str_arr_ext.pre_alloc_string_array(tydj__wrl,
                -1)
            for zvv__uus in range(tydj__wrl):
                data_start = getitem_c_arr(A._data_offsets, ggw__qdr + zvv__uus
                    )
                data_start += 1
                if ggw__qdr + zvv__uus == 0:
                    data_start = 0
                bqhrz__jzuyh = getitem_c_arr(A._data_offsets, ggw__qdr +
                    zvv__uus + 1)
                rpi__rpnh = bqhrz__jzuyh - data_start
                hroo__snyl = get_array_ctypes_ptr(A._data, data_start)
                kfsie__kdya = bodo.libs.str_arr_ext.decode_utf8(hroo__snyl,
                    rpi__rpnh)
                dsh__fliv[zvv__uus] = kfsie__kdya
            return dsh__fliv
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        fsr__sdm = offset_type.bitwidth // 8

        def _impl(A, ind):
            tydj__wrl = len(A)
            if tydj__wrl != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            ulwz__lyg = 0
            krftm__xgy = 0
            for zvv__uus in range(tydj__wrl):
                if ind[zvv__uus]:
                    ulwz__lyg += 1
                    ggw__qdr = getitem_c_arr(A._index_offsets, zvv__uus)
                    uhxa__atz = getitem_c_arr(A._index_offsets, zvv__uus + 1)
                    krftm__xgy += uhxa__atz - ggw__qdr
            dhypk__yvbjz = pre_alloc_str_arr_view(ulwz__lyg, krftm__xgy, A.
                _data)
            item_ind = 0
            calu__ddxkw = 0
            for zvv__uus in range(tydj__wrl):
                if ind[zvv__uus]:
                    ggw__qdr = getitem_c_arr(A._index_offsets, zvv__uus)
                    uhxa__atz = getitem_c_arr(A._index_offsets, zvv__uus + 1)
                    djag__sujxd = uhxa__atz - ggw__qdr
                    setitem_c_arr(dhypk__yvbjz._index_offsets, item_ind,
                        calu__ddxkw)
                    hroo__snyl = get_c_arr_ptr(A._data_offsets, ggw__qdr)
                    dolte__mszfy = get_c_arr_ptr(dhypk__yvbjz._data_offsets,
                        calu__ddxkw)
                    _memcpy(dolte__mszfy, hroo__snyl, djag__sujxd, fsr__sdm)
                    sxa__dlpct = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, zvv__uus)
                    bodo.libs.int_arr_ext.set_bit_to_arr(dhypk__yvbjz.
                        _null_bitmap, item_ind, sxa__dlpct)
                    item_ind += 1
                    calu__ddxkw += djag__sujxd
            setitem_c_arr(dhypk__yvbjz._index_offsets, item_ind, calu__ddxkw)
            return dhypk__yvbjz
        return _impl
