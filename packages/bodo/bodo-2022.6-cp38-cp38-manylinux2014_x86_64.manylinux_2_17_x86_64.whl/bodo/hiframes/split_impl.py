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
        lxsi__hza = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, lxsi__hza)


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
    jlxep__ujw = context.get_value_type(str_arr_split_view_payload_type)
    zyo__ner = context.get_abi_sizeof(jlxep__ujw)
    dtfjt__exhyj = context.get_value_type(types.voidptr)
    irpsl__unwuv = context.get_value_type(types.uintp)
    lsloi__twc = lir.FunctionType(lir.VoidType(), [dtfjt__exhyj,
        irpsl__unwuv, dtfjt__exhyj])
    mrak__jjv = cgutils.get_or_insert_function(builder.module, lsloi__twc,
        name='dtor_str_arr_split_view')
    uchs__oba = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, zyo__ner), mrak__jjv)
    jmj__myx = context.nrt.meminfo_data(builder, uchs__oba)
    stmnr__ervb = builder.bitcast(jmj__myx, jlxep__ujw.as_pointer())
    return uchs__oba, stmnr__ervb


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        imn__gaul, kvcfl__ukprm = args
        uchs__oba, stmnr__ervb = construct_str_arr_split_view(context, builder)
        xiwnm__xqqh = _get_str_binary_arr_payload(context, builder,
            imn__gaul, string_array_type)
        smcm__mpw = lir.FunctionType(lir.VoidType(), [stmnr__ervb.type, lir
            .IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        uji__erojk = cgutils.get_or_insert_function(builder.module,
            smcm__mpw, name='str_arr_split_view_impl')
        spesc__ypdjo = context.make_helper(builder, offset_arr_type,
            xiwnm__xqqh.offsets).data
        qnd__udp = context.make_helper(builder, char_arr_type, xiwnm__xqqh.data
            ).data
        dteiz__hbsnj = context.make_helper(builder, null_bitmap_arr_type,
            xiwnm__xqqh.null_bitmap).data
        epc__hemkx = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(uji__erojk, [stmnr__ervb, xiwnm__xqqh.n_arrays,
            spesc__ypdjo, qnd__udp, dteiz__hbsnj, epc__hemkx])
        luq__wcz = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(stmnr__ervb))
        nahkh__cfon = context.make_helper(builder, string_array_split_view_type
            )
        nahkh__cfon.num_items = xiwnm__xqqh.n_arrays
        nahkh__cfon.index_offsets = luq__wcz.index_offsets
        nahkh__cfon.data_offsets = luq__wcz.data_offsets
        nahkh__cfon.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [imn__gaul])
        nahkh__cfon.null_bitmap = luq__wcz.null_bitmap
        nahkh__cfon.meminfo = uchs__oba
        eif__ats = nahkh__cfon._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, eif__ats)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    wfkc__jracs = context.make_helper(builder, string_array_split_view_type,
        val)
    fcz__dgb = context.insert_const_string(builder.module, 'numpy')
    gfwl__fsg = c.pyapi.import_module_noblock(fcz__dgb)
    dtype = c.pyapi.object_getattr_string(gfwl__fsg, 'object_')
    ign__zvnli = builder.sext(wfkc__jracs.num_items, c.pyapi.longlong)
    kmvsz__ecp = c.pyapi.long_from_longlong(ign__zvnli)
    pcyn__vmtvd = c.pyapi.call_method(gfwl__fsg, 'ndarray', (kmvsz__ecp, dtype)
        )
    onbjy__fyv = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    pfs__tfwry = c.pyapi._get_function(onbjy__fyv, name='array_getptr1')
    ndoqu__ojwqs = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    indmd__cnjf = c.pyapi._get_function(ndoqu__ojwqs, name='array_setitem')
    ywk__jij = c.pyapi.object_getattr_string(gfwl__fsg, 'nan')
    with cgutils.for_range(builder, wfkc__jracs.num_items) as vqex__whebf:
        str_ind = vqex__whebf.index
        ffv__kcnw = builder.sext(builder.load(builder.gep(wfkc__jracs.
            index_offsets, [str_ind])), lir.IntType(64))
        nfzq__ybur = builder.sext(builder.load(builder.gep(wfkc__jracs.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        fjh__dcekk = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        mnaj__dmsq = builder.gep(wfkc__jracs.null_bitmap, [fjh__dcekk])
        tzwdc__cxc = builder.load(mnaj__dmsq)
        ifbxt__eapbt = builder.trunc(builder.and_(str_ind, lir.Constant(lir
            .IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(tzwdc__cxc, ifbxt__eapbt), lir.
            Constant(lir.IntType(8), 1))
        bhzbf__jsmy = builder.sub(nfzq__ybur, ffv__kcnw)
        bhzbf__jsmy = builder.sub(bhzbf__jsmy, bhzbf__jsmy.type(1))
        wnc__ihl = builder.call(pfs__tfwry, [pcyn__vmtvd, str_ind])
        vvj__tkoh = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(vvj__tkoh) as (zgnoe__mbh, snqel__spqi):
            with zgnoe__mbh:
                lttsr__rtzgs = c.pyapi.list_new(bhzbf__jsmy)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    lttsr__rtzgs), likely=True):
                    with cgutils.for_range(c.builder, bhzbf__jsmy
                        ) as vqex__whebf:
                        kmb__fnj = builder.add(ffv__kcnw, vqex__whebf.index)
                        data_start = builder.load(builder.gep(wfkc__jracs.
                            data_offsets, [kmb__fnj]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        aftp__voemj = builder.load(builder.gep(wfkc__jracs.
                            data_offsets, [builder.add(kmb__fnj, kmb__fnj.
                            type(1))]))
                        ngpe__mpb = builder.gep(builder.extract_value(
                            wfkc__jracs.data, 0), [data_start])
                        cszkr__rmyjj = builder.sext(builder.sub(aftp__voemj,
                            data_start), lir.IntType(64))
                        njl__xhl = c.pyapi.string_from_string_and_size(
                            ngpe__mpb, cszkr__rmyjj)
                        c.pyapi.list_setitem(lttsr__rtzgs, vqex__whebf.
                            index, njl__xhl)
                builder.call(indmd__cnjf, [pcyn__vmtvd, wnc__ihl, lttsr__rtzgs]
                    )
            with snqel__spqi:
                builder.call(indmd__cnjf, [pcyn__vmtvd, wnc__ihl, ywk__jij])
    c.pyapi.decref(gfwl__fsg)
    c.pyapi.decref(dtype)
    c.pyapi.decref(ywk__jij)
    return pcyn__vmtvd


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        ztgcm__uqkq, wdul__pjb, ngpe__mpb = args
        uchs__oba, stmnr__ervb = construct_str_arr_split_view(context, builder)
        smcm__mpw = lir.FunctionType(lir.VoidType(), [stmnr__ervb.type, lir
            .IntType(64), lir.IntType(64)])
        uji__erojk = cgutils.get_or_insert_function(builder.module,
            smcm__mpw, name='str_arr_split_view_alloc')
        builder.call(uji__erojk, [stmnr__ervb, ztgcm__uqkq, wdul__pjb])
        luq__wcz = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(stmnr__ervb))
        nahkh__cfon = context.make_helper(builder, string_array_split_view_type
            )
        nahkh__cfon.num_items = ztgcm__uqkq
        nahkh__cfon.index_offsets = luq__wcz.index_offsets
        nahkh__cfon.data_offsets = luq__wcz.data_offsets
        nahkh__cfon.data = ngpe__mpb
        nahkh__cfon.null_bitmap = luq__wcz.null_bitmap
        context.nrt.incref(builder, data_t, ngpe__mpb)
        nahkh__cfon.meminfo = uchs__oba
        eif__ats = nahkh__cfon._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, eif__ats)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        ybdjm__aanab, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            ybdjm__aanab = builder.extract_value(ybdjm__aanab, 0)
        return builder.bitcast(builder.gep(ybdjm__aanab, [ind]), lir.
            IntType(8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        ybdjm__aanab, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            ybdjm__aanab = builder.extract_value(ybdjm__aanab, 0)
        return builder.load(builder.gep(ybdjm__aanab, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        ybdjm__aanab, ind, quya__uyxkz = args
        fwxq__zkq = builder.gep(ybdjm__aanab, [ind])
        builder.store(quya__uyxkz, fwxq__zkq)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        ubwq__jzbyc, ind = args
        egig__kwt = context.make_helper(builder, arr_ctypes_t, ubwq__jzbyc)
        hlvr__etq = context.make_helper(builder, arr_ctypes_t)
        hlvr__etq.data = builder.gep(egig__kwt.data, [ind])
        hlvr__etq.meminfo = egig__kwt.meminfo
        exvs__xim = hlvr__etq._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, exvs__xim)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    eytn__gtt = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not eytn__gtt:
        return 0, 0, 0
    kmb__fnj = getitem_c_arr(arr._index_offsets, item_ind)
    kcis__savcl = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    zfw__vjuez = kcis__savcl - kmb__fnj
    if str_ind >= zfw__vjuez:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, kmb__fnj + str_ind)
    data_start += 1
    if kmb__fnj + str_ind == 0:
        data_start = 0
    aftp__voemj = getitem_c_arr(arr._data_offsets, kmb__fnj + str_ind + 1)
    ztu__glbq = aftp__voemj - data_start
    return 1, data_start, ztu__glbq


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
        mwoo__mvyqb = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            kmb__fnj = getitem_c_arr(A._index_offsets, ind)
            kcis__savcl = getitem_c_arr(A._index_offsets, ind + 1)
            gvvs__radcb = kcis__savcl - kmb__fnj - 1
            imn__gaul = bodo.libs.str_arr_ext.pre_alloc_string_array(
                gvvs__radcb, -1)
            for mbnec__lbbq in range(gvvs__radcb):
                data_start = getitem_c_arr(A._data_offsets, kmb__fnj +
                    mbnec__lbbq)
                data_start += 1
                if kmb__fnj + mbnec__lbbq == 0:
                    data_start = 0
                aftp__voemj = getitem_c_arr(A._data_offsets, kmb__fnj +
                    mbnec__lbbq + 1)
                ztu__glbq = aftp__voemj - data_start
                fwxq__zkq = get_array_ctypes_ptr(A._data, data_start)
                hoqqs__hszp = bodo.libs.str_arr_ext.decode_utf8(fwxq__zkq,
                    ztu__glbq)
                imn__gaul[mbnec__lbbq] = hoqqs__hszp
            return imn__gaul
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        spvdx__qbyz = offset_type.bitwidth // 8

        def _impl(A, ind):
            gvvs__radcb = len(A)
            if gvvs__radcb != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            ztgcm__uqkq = 0
            wdul__pjb = 0
            for mbnec__lbbq in range(gvvs__radcb):
                if ind[mbnec__lbbq]:
                    ztgcm__uqkq += 1
                    kmb__fnj = getitem_c_arr(A._index_offsets, mbnec__lbbq)
                    kcis__savcl = getitem_c_arr(A._index_offsets, 
                        mbnec__lbbq + 1)
                    wdul__pjb += kcis__savcl - kmb__fnj
            pcyn__vmtvd = pre_alloc_str_arr_view(ztgcm__uqkq, wdul__pjb, A.
                _data)
            item_ind = 0
            guvfc__arja = 0
            for mbnec__lbbq in range(gvvs__radcb):
                if ind[mbnec__lbbq]:
                    kmb__fnj = getitem_c_arr(A._index_offsets, mbnec__lbbq)
                    kcis__savcl = getitem_c_arr(A._index_offsets, 
                        mbnec__lbbq + 1)
                    mev__pcslj = kcis__savcl - kmb__fnj
                    setitem_c_arr(pcyn__vmtvd._index_offsets, item_ind,
                        guvfc__arja)
                    fwxq__zkq = get_c_arr_ptr(A._data_offsets, kmb__fnj)
                    rmaia__fekdc = get_c_arr_ptr(pcyn__vmtvd._data_offsets,
                        guvfc__arja)
                    _memcpy(rmaia__fekdc, fwxq__zkq, mev__pcslj, spvdx__qbyz)
                    eytn__gtt = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, mbnec__lbbq)
                    bodo.libs.int_arr_ext.set_bit_to_arr(pcyn__vmtvd.
                        _null_bitmap, item_ind, eytn__gtt)
                    item_ind += 1
                    guvfc__arja += mev__pcslj
            setitem_c_arr(pcyn__vmtvd._index_offsets, item_ind, guvfc__arja)
            return pcyn__vmtvd
        return _impl
