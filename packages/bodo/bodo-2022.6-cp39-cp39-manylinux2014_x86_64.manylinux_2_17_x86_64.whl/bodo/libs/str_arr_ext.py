"""Array implementation for string objects, which are usually immutable.
The characters are stored in a contingous data array, and an offsets array marks the
the individual strings. For example:
value:             ['a', 'bc', '', 'abc', None, 'bb']
data:              [a, b, c, a, b, c, b, b]
offsets:           [0, 1, 3, 3, 6, 6, 8]
"""
import glob
import operator
import numba
import numba.core.typing.typeof
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.unsafe.bytes import memcpy_region
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, type_callable, typeof_impl, unbox
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, pre_alloc_binary_array
from bodo.libs.str_ext import memcmp, string_type, unicode_to_utf8_and_len
from bodo.utils.typing import BodoArrayIterator, BodoError, decode_if_dict_array, is_list_like_index_type, is_overload_constant_int, is_overload_none, is_overload_true, is_str_arr_type, parse_dtype, raise_bodo_error
use_pd_string_array = False
char_type = types.uint8
char_arr_type = types.Array(char_type, 1, 'C')
offset_arr_type = types.Array(offset_type, 1, 'C')
null_bitmap_arr_type = types.Array(types.uint8, 1, 'C')
data_ctypes_type = types.ArrayCTypes(char_arr_type)
offset_ctypes_type = types.ArrayCTypes(offset_arr_type)


class StringArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self):
        super(StringArrayType, self).__init__(name='StringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    @property
    def iterator_type(self):
        return BodoArrayIterator(self)

    def copy(self):
        return StringArrayType()


string_array_type = StringArrayType()


@typeof_impl.register(pd.arrays.StringArray)
def typeof_string_array(val, c):
    return string_array_type


@register_model(BinaryArrayType)
@register_model(StringArrayType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        chyp__dvcsh = ArrayItemArrayType(char_arr_type)
        ubv__ssvif = [('data', chyp__dvcsh)]
        models.StructModel.__init__(self, dmm, fe_type, ubv__ssvif)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        obs__bfz, = args
        jsj__krxta = context.make_helper(builder, string_array_type)
        jsj__krxta.data = obs__bfz
        context.nrt.incref(builder, data_typ, obs__bfz)
        return jsj__krxta._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    ubmq__lmc = c.context.insert_const_string(c.builder.module, 'pandas')
    rnuu__nvj = c.pyapi.import_module_noblock(ubmq__lmc)
    ivin__msw = c.pyapi.call_method(rnuu__nvj, 'StringDtype', ())
    c.pyapi.decref(rnuu__nvj)
    return ivin__msw


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        atl__arv = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs, rhs)
        if atl__arv is not None:
            return atl__arv
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ctl__ozllp = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ctl__ozllp)
                for i in numba.parfors.parfor.internal_prange(ctl__ozllp):
                    if bodo.libs.array_kernels.isna(lhs, i
                        ) or bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_both
        if is_str_arr_type(lhs) and types.unliteral(rhs) == string_type:

            def impl_left(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ctl__ozllp = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ctl__ozllp)
                for i in numba.parfors.parfor.internal_prange(ctl__ozllp):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs)
                    out_arr[i] = val
                return out_arr
            return impl_left
        if types.unliteral(lhs) == string_type and is_str_arr_type(rhs):

            def impl_right(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ctl__ozllp = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ctl__ozllp)
                for i in numba.parfors.parfor.internal_prange(ctl__ozllp):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs, rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_right
        raise_bodo_error(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_string_array_binary_op


def overload_add_operator_string_array(lhs, rhs):
    evwc__scil = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    upj__xgjkc = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and upj__xgjkc or evwc__scil and is_str_arr_type(
        rhs):

        def impl_both(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j
                    ) or bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs[j]
            return out_arr
        return impl_both
    if is_str_arr_type(lhs) and types.unliteral(rhs) == string_type:

        def impl_left(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs
            return out_arr
        return impl_left
    if types.unliteral(lhs) == string_type and is_str_arr_type(rhs):

        def impl_right(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(rhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs + rhs[j]
            return out_arr
        return impl_right


def overload_mul_operator_str_arr(lhs, rhs):
    if is_str_arr_type(lhs) and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] * rhs
            return out_arr
        return impl
    if isinstance(lhs, types.Integer) and is_str_arr_type(rhs):

        def impl(lhs, rhs):
            return rhs * lhs
        return impl


def _get_str_binary_arr_payload(context, builder, arr_value, arr_typ):
    assert arr_typ == string_array_type or arr_typ == binary_array_type
    xwd__pjrjz = context.make_helper(builder, arr_typ, arr_value)
    chyp__dvcsh = ArrayItemArrayType(char_arr_type)
    ldj__asb = _get_array_item_arr_payload(context, builder, chyp__dvcsh,
        xwd__pjrjz.data)
    return ldj__asb


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            string_array_type)
        return ldj__asb.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            sig.args[0])
        bzb__tgz = context.make_helper(builder, offset_arr_type, ldj__asb.
            offsets).data
        return _get_num_total_chars(builder, bzb__tgz, ldj__asb.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            sig.args[0])
        wgy__vqqr = context.make_helper(builder, offset_arr_type, ldj__asb.
            offsets)
        wjl__bvgrb = context.make_helper(builder, offset_ctypes_type)
        wjl__bvgrb.data = builder.bitcast(wgy__vqqr.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        wjl__bvgrb.meminfo = wgy__vqqr.meminfo
        ivin__msw = wjl__bvgrb._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            ivin__msw)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            sig.args[0])
        obs__bfz = context.make_helper(builder, char_arr_type, ldj__asb.data)
        wjl__bvgrb = context.make_helper(builder, data_ctypes_type)
        wjl__bvgrb.data = obs__bfz.data
        wjl__bvgrb.meminfo = obs__bfz.meminfo
        ivin__msw = wjl__bvgrb._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, ivin__msw)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        lub__xbth, ind = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, lub__xbth,
            sig.args[0])
        obs__bfz = context.make_helper(builder, char_arr_type, ldj__asb.data)
        wjl__bvgrb = context.make_helper(builder, data_ctypes_type)
        wjl__bvgrb.data = builder.gep(obs__bfz.data, [ind])
        wjl__bvgrb.meminfo = obs__bfz.meminfo
        ivin__msw = wjl__bvgrb._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, ivin__msw)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        weplk__xqn, ulr__vvu, uvqa__txy, zkzkq__tdipo = args
        aivmz__mec = builder.bitcast(builder.gep(weplk__xqn, [ulr__vvu]),
            lir.IntType(8).as_pointer())
        ljhj__jgh = builder.bitcast(builder.gep(uvqa__txy, [zkzkq__tdipo]),
            lir.IntType(8).as_pointer())
        ucjfa__wuqo = builder.load(ljhj__jgh)
        builder.store(ucjfa__wuqo, aivmz__mec)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            sig.args[0])
        nqvtr__ugo = context.make_helper(builder, null_bitmap_arr_type,
            ldj__asb.null_bitmap)
        wjl__bvgrb = context.make_helper(builder, data_ctypes_type)
        wjl__bvgrb.data = nqvtr__ugo.data
        wjl__bvgrb.meminfo = nqvtr__ugo.meminfo
        ivin__msw = wjl__bvgrb._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, ivin__msw)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            sig.args[0])
        bzb__tgz = context.make_helper(builder, offset_arr_type, ldj__asb.
            offsets).data
        return builder.load(builder.gep(bzb__tgz, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, ldj__asb.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        oys__cuz, ind = args
        if in_bitmap_typ == data_ctypes_type:
            wjl__bvgrb = context.make_helper(builder, data_ctypes_type,
                oys__cuz)
            oys__cuz = wjl__bvgrb.data
        return builder.load(builder.gep(oys__cuz, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        oys__cuz, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            wjl__bvgrb = context.make_helper(builder, data_ctypes_type,
                oys__cuz)
            oys__cuz = wjl__bvgrb.data
        builder.store(val, builder.gep(oys__cuz, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        bwud__nypg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        kigxm__xim = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        dul__cgi = context.make_helper(builder, offset_arr_type, bwud__nypg
            .offsets).data
        itzp__hif = context.make_helper(builder, offset_arr_type,
            kigxm__xim.offsets).data
        jwvq__chnho = context.make_helper(builder, char_arr_type,
            bwud__nypg.data).data
        ziws__mks = context.make_helper(builder, char_arr_type, kigxm__xim.data
            ).data
        czy__vtjb = context.make_helper(builder, null_bitmap_arr_type,
            bwud__nypg.null_bitmap).data
        vsi__xzmbh = context.make_helper(builder, null_bitmap_arr_type,
            kigxm__xim.null_bitmap).data
        gjrmr__bdtoe = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, itzp__hif, dul__cgi, gjrmr__bdtoe)
        cgutils.memcpy(builder, ziws__mks, jwvq__chnho, builder.load(
            builder.gep(dul__cgi, [ind])))
        roh__damhd = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        tvke__hnzcr = builder.lshr(roh__damhd, lir.Constant(lir.IntType(64), 3)
            )
        cgutils.memcpy(builder, vsi__xzmbh, czy__vtjb, tvke__hnzcr)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        bwud__nypg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        kigxm__xim = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        dul__cgi = context.make_helper(builder, offset_arr_type, bwud__nypg
            .offsets).data
        jwvq__chnho = context.make_helper(builder, char_arr_type,
            bwud__nypg.data).data
        ziws__mks = context.make_helper(builder, char_arr_type, kigxm__xim.data
            ).data
        num_total_chars = _get_num_total_chars(builder, dul__cgi,
            bwud__nypg.n_arrays)
        cgutils.memcpy(builder, ziws__mks, jwvq__chnho, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        bwud__nypg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        kigxm__xim = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        dul__cgi = context.make_helper(builder, offset_arr_type, bwud__nypg
            .offsets).data
        itzp__hif = context.make_helper(builder, offset_arr_type,
            kigxm__xim.offsets).data
        czy__vtjb = context.make_helper(builder, null_bitmap_arr_type,
            bwud__nypg.null_bitmap).data
        ctl__ozllp = bwud__nypg.n_arrays
        qsh__kyt = context.get_constant(offset_type, 0)
        ijo__ujay = cgutils.alloca_once_value(builder, qsh__kyt)
        with cgutils.for_range(builder, ctl__ozllp) as cvj__lvdmn:
            afxf__ysevm = lower_is_na(context, builder, czy__vtjb,
                cvj__lvdmn.index)
            with cgutils.if_likely(builder, builder.not_(afxf__ysevm)):
                sqcgr__hocp = builder.load(builder.gep(dul__cgi, [
                    cvj__lvdmn.index]))
                lmncg__fuk = builder.load(ijo__ujay)
                builder.store(sqcgr__hocp, builder.gep(itzp__hif, [lmncg__fuk])
                    )
                builder.store(builder.add(lmncg__fuk, lir.Constant(context.
                    get_value_type(offset_type), 1)), ijo__ujay)
        lmncg__fuk = builder.load(ijo__ujay)
        sqcgr__hocp = builder.load(builder.gep(dul__cgi, [ctl__ozllp]))
        builder.store(sqcgr__hocp, builder.gep(itzp__hif, [lmncg__fuk]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        jzljs__ylcu, ind, str, xtg__latg = args
        jzljs__ylcu = context.make_array(sig.args[0])(context, builder,
            jzljs__ylcu)
        lmjm__vzx = builder.gep(jzljs__ylcu.data, [ind])
        cgutils.raw_memcpy(builder, lmjm__vzx, str, xtg__latg, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        lmjm__vzx, ind, dhb__uryc, xtg__latg = args
        lmjm__vzx = builder.gep(lmjm__vzx, [ind])
        cgutils.raw_memcpy(builder, lmjm__vzx, dhb__uryc, xtg__latg, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            jstc__opvw = A._data
            return np.int64(getitem_str_offset(jstc__opvw, idx + 1) -
                getitem_str_offset(jstc__opvw, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    jmt__msn = np.int64(getitem_str_offset(A, i))
    cuidp__kow = np.int64(getitem_str_offset(A, i + 1))
    l = cuidp__kow - jmt__msn
    lpuc__waam = get_data_ptr_ind(A, jmt__msn)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(lpuc__waam, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    rgpl__yzttn = getitem_str_offset(A, i)
    ignim__bexcz = getitem_str_offset(A, i + 1)
    obt__knwl = ignim__bexcz - rgpl__yzttn
    icu__jwqa = getitem_str_offset(B, j)
    pstjx__rqkut = icu__jwqa + obt__knwl
    setitem_str_offset(B, j + 1, pstjx__rqkut)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if obt__knwl != 0:
        obs__bfz = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(obs__bfz, np.
            int64(icu__jwqa), np.int64(pstjx__rqkut))
        kba__imed = get_data_ptr(B).data
        pkhay__lmo = get_data_ptr(A).data
        memcpy_region(kba__imed, icu__jwqa, pkhay__lmo, rgpl__yzttn,
            obt__knwl, 1)


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    ctl__ozllp = len(str_arr)
    vda__fprit = np.empty(ctl__ozllp, np.bool_)
    for i in range(ctl__ozllp):
        vda__fprit[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return vda__fprit


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            ctl__ozllp = len(data)
            l = []
            for i in range(ctl__ozllp):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        tzzr__bvj = data.count
        zdydh__tivfv = ['to_list_if_immutable_arr(data[{}])'.format(i) for
            i in range(tzzr__bvj)]
        if is_overload_true(str_null_bools):
            zdydh__tivfv += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(tzzr__bvj) if is_str_arr_type(data.types[i]) or data.
                types[i] == binary_array_type]
        cxcvf__qni = 'def f(data, str_null_bools=None):\n'
        cxcvf__qni += '  return ({}{})\n'.format(', '.join(zdydh__tivfv), 
            ',' if tzzr__bvj == 1 else '')
        artmh__zgufu = {}
        exec(cxcvf__qni, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, artmh__zgufu)
        plea__qdxpd = artmh__zgufu['f']
        return plea__qdxpd
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                ctl__ozllp = len(list_data)
                for i in range(ctl__ozllp):
                    dhb__uryc = list_data[i]
                    str_arr[i] = dhb__uryc
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                ctl__ozllp = len(list_data)
                for i in range(ctl__ozllp):
                    dhb__uryc = list_data[i]
                    str_arr[i] = dhb__uryc
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        tzzr__bvj = str_arr.count
        mlr__yimz = 0
        cxcvf__qni = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(tzzr__bvj):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                cxcvf__qni += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, tzzr__bvj + mlr__yimz))
                mlr__yimz += 1
            else:
                cxcvf__qni += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        cxcvf__qni += '  return\n'
        artmh__zgufu = {}
        exec(cxcvf__qni, {'cp_str_list_to_array': cp_str_list_to_array},
            artmh__zgufu)
        sld__vve = artmh__zgufu['f']
        return sld__vve
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            ctl__ozllp = len(str_list)
            str_arr = pre_alloc_string_array(ctl__ozllp, -1)
            for i in range(ctl__ozllp):
                dhb__uryc = str_list[i]
                str_arr[i] = dhb__uryc
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            ctl__ozllp = len(A)
            sye__xmpb = 0
            for i in range(ctl__ozllp):
                dhb__uryc = A[i]
                sye__xmpb += get_utf8_size(dhb__uryc)
            return sye__xmpb
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        ctl__ozllp = len(arr)
        n_chars = num_total_chars(arr)
        upw__bnkqi = pre_alloc_string_array(ctl__ozllp, np.int64(n_chars))
        copy_str_arr_slice(upw__bnkqi, arr, ctl__ozllp)
        return upw__bnkqi
    return copy_impl


@overload(len, no_unliteral=True)
def str_arr_len_overload(str_arr):
    if str_arr == string_array_type:

        def str_arr_len(str_arr):
            return str_arr.size
        return str_arr_len


@overload_attribute(StringArrayType, 'size')
def str_arr_size_overload(str_arr):
    return lambda str_arr: len(str_arr._data)


@overload_attribute(StringArrayType, 'shape')
def str_arr_shape_overload(str_arr):
    return lambda str_arr: (str_arr.size,)


@overload_attribute(StringArrayType, 'nbytes')
def str_arr_nbytes_overload(str_arr):
    return lambda str_arr: str_arr._data.nbytes


@overload_method(types.Array, 'tolist', no_unliteral=True)
@overload_method(StringArrayType, 'tolist', no_unliteral=True)
def overload_to_list(arr):
    return lambda arr: list(arr)


import llvmlite.binding as ll
from llvmlite import ir as lir
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('setitem_string_array', hstr_ext.setitem_string_array)
ll.add_symbol('is_na', hstr_ext.is_na)
ll.add_symbol('string_array_from_sequence', array_ext.
    string_array_from_sequence)
ll.add_symbol('pd_array_from_string_array', hstr_ext.pd_array_from_string_array
    )
ll.add_symbol('np_array_from_string_array', hstr_ext.np_array_from_string_array
    )
ll.add_symbol('convert_len_arr_to_offset32', hstr_ext.
    convert_len_arr_to_offset32)
ll.add_symbol('convert_len_arr_to_offset', hstr_ext.convert_len_arr_to_offset)
ll.add_symbol('set_string_array_range', hstr_ext.set_string_array_range)
ll.add_symbol('str_arr_to_int64', hstr_ext.str_arr_to_int64)
ll.add_symbol('str_arr_to_float64', hstr_ext.str_arr_to_float64)
ll.add_symbol('get_utf8_size', hstr_ext.get_utf8_size)
ll.add_symbol('print_str_arr', hstr_ext.print_str_arr)
ll.add_symbol('inplace_int64_to_str', hstr_ext.inplace_int64_to_str)
inplace_int64_to_str = types.ExternalFunction('inplace_int64_to_str', types
    .void(types.voidptr, types.int64, types.int64))
convert_len_arr_to_offset32 = types.ExternalFunction(
    'convert_len_arr_to_offset32', types.void(types.voidptr, types.intp))
convert_len_arr_to_offset = types.ExternalFunction('convert_len_arr_to_offset',
    types.void(types.voidptr, types.voidptr, types.intp))
setitem_string_array = types.ExternalFunction('setitem_string_array', types
    .void(types.CPointer(offset_type), types.CPointer(char_type), types.
    uint64, types.voidptr, types.intp, offset_type, offset_type, types.intp))
_get_utf8_size = types.ExternalFunction('get_utf8_size', types.intp(types.
    voidptr, types.intp, offset_type))
_print_str_arr = types.ExternalFunction('print_str_arr', types.void(types.
    uint64, types.uint64, types.CPointer(offset_type), types.CPointer(
    char_type)))


@numba.generated_jit(nopython=True)
def empty_str_arr(in_seq):
    cxcvf__qni = 'def f(in_seq):\n'
    cxcvf__qni += '    n_strs = len(in_seq)\n'
    cxcvf__qni += '    A = pre_alloc_string_array(n_strs, -1)\n'
    cxcvf__qni += '    return A\n'
    artmh__zgufu = {}
    exec(cxcvf__qni, {'pre_alloc_string_array': pre_alloc_string_array},
        artmh__zgufu)
    yqz__ehpz = artmh__zgufu['f']
    return yqz__ehpz


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        ubrl__wxqo = 'pre_alloc_binary_array'
    else:
        ubrl__wxqo = 'pre_alloc_string_array'
    cxcvf__qni = 'def f(in_seq):\n'
    cxcvf__qni += '    n_strs = len(in_seq)\n'
    cxcvf__qni += f'    A = {ubrl__wxqo}(n_strs, -1)\n'
    cxcvf__qni += '    for i in range(n_strs):\n'
    cxcvf__qni += '        A[i] = in_seq[i]\n'
    cxcvf__qni += '    return A\n'
    artmh__zgufu = {}
    exec(cxcvf__qni, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, artmh__zgufu)
    yqz__ehpz = artmh__zgufu['f']
    return yqz__ehpz


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            sig.args[0])
        zgkdt__gpjki = builder.add(ldj__asb.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        uwvj__uvwf = builder.lshr(lir.Constant(lir.IntType(64), offset_type
            .bitwidth), lir.Constant(lir.IntType(64), 3))
        tvke__hnzcr = builder.mul(zgkdt__gpjki, uwvj__uvwf)
        llifl__irqu = context.make_array(offset_arr_type)(context, builder,
            ldj__asb.offsets).data
        cgutils.memset(builder, llifl__irqu, tvke__hnzcr, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            sig.args[0])
        ijjh__rcy = ldj__asb.n_arrays
        tvke__hnzcr = builder.lshr(builder.add(ijjh__rcy, lir.Constant(lir.
            IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        dqoh__ltb = context.make_array(null_bitmap_arr_type)(context,
            builder, ldj__asb.null_bitmap).data
        cgutils.memset(builder, dqoh__ltb, tvke__hnzcr, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@numba.njit
def pre_alloc_string_array(n_strs, n_chars):
    if n_chars is None:
        n_chars = -1
    str_arr = init_str_arr(bodo.libs.array_item_arr_ext.
        pre_alloc_array_item_array(np.int64(n_strs), (np.int64(n_chars),),
        char_arr_type))
    if n_chars == 0:
        set_all_offsets_to_0(str_arr)
    return str_arr


@register_jitable
def gen_na_str_array_lens(n_strs, total_len, len_arr):
    str_arr = pre_alloc_string_array(n_strs, total_len)
    set_bitmap_all_NA(str_arr)
    offsets = bodo.libs.array_item_arr_ext.get_offsets(str_arr._data)
    xlipw__ooku = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        hqpt__mvps = len(len_arr)
        for i in range(hqpt__mvps):
            offsets[i] = xlipw__ooku
            xlipw__ooku += len_arr[i]
        offsets[hqpt__mvps] = xlipw__ooku
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    svra__rmct = i // 8
    ovy__grf = getitem_str_bitmap(bits, svra__rmct)
    ovy__grf ^= np.uint8(-np.uint8(bit_is_set) ^ ovy__grf) & kBitmask[i % 8]
    setitem_str_bitmap(bits, svra__rmct, ovy__grf)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    rhll__pcvk = get_null_bitmap_ptr(out_str_arr)
    sopws__kzudp = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        vsq__jyizx = get_bit_bitmap(sopws__kzudp, j)
        set_bit_to(rhll__pcvk, out_start + j, vsq__jyizx)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, lub__xbth, zru__lbi, dcx__smv = args
        bwud__nypg = _get_str_binary_arr_payload(context, builder,
            lub__xbth, string_array_type)
        kigxm__xim = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        dul__cgi = context.make_helper(builder, offset_arr_type, bwud__nypg
            .offsets).data
        itzp__hif = context.make_helper(builder, offset_arr_type,
            kigxm__xim.offsets).data
        jwvq__chnho = context.make_helper(builder, char_arr_type,
            bwud__nypg.data).data
        ziws__mks = context.make_helper(builder, char_arr_type, kigxm__xim.data
            ).data
        num_total_chars = _get_num_total_chars(builder, dul__cgi,
            bwud__nypg.n_arrays)
        knae__ckrd = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        qqbp__yit = cgutils.get_or_insert_function(builder.module,
            knae__ckrd, name='set_string_array_range')
        builder.call(qqbp__yit, [itzp__hif, ziws__mks, dul__cgi,
            jwvq__chnho, zru__lbi, dcx__smv, bwud__nypg.n_arrays,
            num_total_chars])
        qxvvq__tpvkv = context.typing_context.resolve_value_type(
            copy_nulls_range)
        hmubb__yls = qxvvq__tpvkv.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        ply__scln = context.get_function(qxvvq__tpvkv, hmubb__yls)
        ply__scln(builder, (out_arr, lub__xbth, zru__lbi))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    ork__kgz = c.context.make_helper(c.builder, typ, val)
    chyp__dvcsh = ArrayItemArrayType(char_arr_type)
    ldj__asb = _get_array_item_arr_payload(c.context, c.builder,
        chyp__dvcsh, ork__kgz.data)
    hved__gqdwn = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    dtm__hsyas = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        dtm__hsyas = 'pd_array_from_string_array'
    knae__ckrd = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    etcp__irjp = cgutils.get_or_insert_function(c.builder.module,
        knae__ckrd, name=dtm__hsyas)
    bzb__tgz = c.context.make_array(offset_arr_type)(c.context, c.builder,
        ldj__asb.offsets).data
    lpuc__waam = c.context.make_array(char_arr_type)(c.context, c.builder,
        ldj__asb.data).data
    dqoh__ltb = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, ldj__asb.null_bitmap).data
    arr = c.builder.call(etcp__irjp, [ldj__asb.n_arrays, bzb__tgz,
        lpuc__waam, dqoh__ltb, hved__gqdwn])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            string_array_type)
        dqoh__ltb = context.make_array(null_bitmap_arr_type)(context,
            builder, ldj__asb.null_bitmap).data
        ivg__cxzh = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        nzh__axth = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        ovy__grf = builder.load(builder.gep(dqoh__ltb, [ivg__cxzh],
            inbounds=True))
        hte__vmpu = lir.ArrayType(lir.IntType(8), 8)
        wezbz__ves = cgutils.alloca_once_value(builder, lir.Constant(
            hte__vmpu, (1, 2, 4, 8, 16, 32, 64, 128)))
        ophf__asfoo = builder.load(builder.gep(wezbz__ves, [lir.Constant(
            lir.IntType(64), 0), nzh__axth], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(ovy__grf,
            ophf__asfoo), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            string_array_type)
        ivg__cxzh = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        nzh__axth = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        dqoh__ltb = context.make_array(null_bitmap_arr_type)(context,
            builder, ldj__asb.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, ldj__asb.
            offsets).data
        xnbun__fomy = builder.gep(dqoh__ltb, [ivg__cxzh], inbounds=True)
        ovy__grf = builder.load(xnbun__fomy)
        hte__vmpu = lir.ArrayType(lir.IntType(8), 8)
        wezbz__ves = cgutils.alloca_once_value(builder, lir.Constant(
            hte__vmpu, (1, 2, 4, 8, 16, 32, 64, 128)))
        ophf__asfoo = builder.load(builder.gep(wezbz__ves, [lir.Constant(
            lir.IntType(64), 0), nzh__axth], inbounds=True))
        ophf__asfoo = builder.xor(ophf__asfoo, lir.Constant(lir.IntType(8), -1)
            )
        builder.store(builder.and_(ovy__grf, ophf__asfoo), xnbun__fomy)
        if str_arr_typ == string_array_type:
            hsar__qspm = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            lepey__aznbp = builder.icmp_unsigned('!=', hsar__qspm, ldj__asb
                .n_arrays)
            with builder.if_then(lepey__aznbp):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [hsar__qspm]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            string_array_type)
        ivg__cxzh = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        nzh__axth = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        dqoh__ltb = context.make_array(null_bitmap_arr_type)(context,
            builder, ldj__asb.null_bitmap).data
        xnbun__fomy = builder.gep(dqoh__ltb, [ivg__cxzh], inbounds=True)
        ovy__grf = builder.load(xnbun__fomy)
        hte__vmpu = lir.ArrayType(lir.IntType(8), 8)
        wezbz__ves = cgutils.alloca_once_value(builder, lir.Constant(
            hte__vmpu, (1, 2, 4, 8, 16, 32, 64, 128)))
        ophf__asfoo = builder.load(builder.gep(wezbz__ves, [lir.Constant(
            lir.IntType(64), 0), nzh__axth], inbounds=True))
        builder.store(builder.or_(ovy__grf, ophf__asfoo), xnbun__fomy)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, in_str_arr,
            string_array_type)
        tvke__hnzcr = builder.udiv(builder.add(ldj__asb.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        dqoh__ltb = context.make_array(null_bitmap_arr_type)(context,
            builder, ldj__asb.null_bitmap).data
        cgutils.memset(builder, dqoh__ltb, tvke__hnzcr, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    sfes__vox = context.make_helper(builder, string_array_type, str_arr)
    chyp__dvcsh = ArrayItemArrayType(char_arr_type)
    ygw__xcc = context.make_helper(builder, chyp__dvcsh, sfes__vox.data)
    ldw__kwacj = ArrayItemArrayPayloadType(chyp__dvcsh)
    gffc__ajglt = context.nrt.meminfo_data(builder, ygw__xcc.meminfo)
    cdmqs__xrry = builder.bitcast(gffc__ajglt, context.get_value_type(
        ldw__kwacj).as_pointer())
    return cdmqs__xrry


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        myjcb__givrl, hoffb__kixob = args
        hqk__zfuu = _get_str_binary_arr_data_payload_ptr(context, builder,
            hoffb__kixob)
        wkue__ljjbf = _get_str_binary_arr_data_payload_ptr(context, builder,
            myjcb__givrl)
        gvx__pityq = _get_str_binary_arr_payload(context, builder,
            hoffb__kixob, sig.args[1])
        uqlte__wqt = _get_str_binary_arr_payload(context, builder,
            myjcb__givrl, sig.args[0])
        context.nrt.incref(builder, char_arr_type, gvx__pityq.data)
        context.nrt.incref(builder, offset_arr_type, gvx__pityq.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, gvx__pityq.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, uqlte__wqt.data)
        context.nrt.decref(builder, offset_arr_type, uqlte__wqt.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, uqlte__wqt.
            null_bitmap)
        builder.store(builder.load(hqk__zfuu), wkue__ljjbf)
        return context.get_dummy_value()
    return types.none(to_arr_typ, from_arr_typ), codegen


dummy_use = numba.njit(lambda a: None)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_utf8_size(s):
    if isinstance(s, types.StringLiteral):
        l = len(s.literal_value.encode())
        return lambda s: l

    def impl(s):
        if s is None:
            return 0
        s = bodo.utils.indexing.unoptional(s)
        if s._is_ascii == 1:
            return len(s)
        ctl__ozllp = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return ctl__ozllp
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, lmjm__vzx, vmh__qwfz = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, arr, sig.
            args[0])
        offsets = context.make_helper(builder, offset_arr_type, ldj__asb.
            offsets).data
        data = context.make_helper(builder, char_arr_type, ldj__asb.data).data
        knae__ckrd = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        wwfid__qxazm = cgutils.get_or_insert_function(builder.module,
            knae__ckrd, name='setitem_string_array')
        ztdqp__aaw = context.get_constant(types.int32, -1)
        dkyqq__sakxh = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, ldj__asb.
            n_arrays)
        builder.call(wwfid__qxazm, [offsets, data, num_total_chars, builder
            .extract_value(lmjm__vzx, 0), vmh__qwfz, ztdqp__aaw,
            dkyqq__sakxh, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    knae__ckrd = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    siwv__qpij = cgutils.get_or_insert_function(builder.module, knae__ckrd,
        name='is_na')
    return builder.call(siwv__qpij, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        aivmz__mec, ljhj__jgh, tzzr__bvj, czk__ykcr = args
        cgutils.raw_memcpy(builder, aivmz__mec, ljhj__jgh, tzzr__bvj, czk__ykcr
            )
        return context.get_dummy_value()
    return types.void(types.voidptr, types.voidptr, types.intp, types.intp
        ), codegen


@numba.njit
def print_str_arr(arr):
    _print_str_arr(num_strings(arr), num_total_chars(arr), get_offset_ptr(
        arr), get_data_ptr(arr))


def inplace_eq(A, i, val):
    return A[i] == val


@overload(inplace_eq)
def inplace_eq_overload(A, ind, val):

    def impl(A, ind, val):
        heh__pbwlz, npa__oab = unicode_to_utf8_and_len(val)
        gay__nsec = getitem_str_offset(A, ind)
        jhb__mhu = getitem_str_offset(A, ind + 1)
        tvnb__qftgp = jhb__mhu - gay__nsec
        if tvnb__qftgp != npa__oab:
            return False
        lmjm__vzx = get_data_ptr_ind(A, gay__nsec)
        return memcmp(lmjm__vzx, heh__pbwlz, npa__oab) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        gay__nsec = getitem_str_offset(A, ind)
        tvnb__qftgp = bodo.libs.str_ext.int_to_str_len(val)
        lwp__mcla = gay__nsec + tvnb__qftgp
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            gay__nsec, lwp__mcla)
        lmjm__vzx = get_data_ptr_ind(A, gay__nsec)
        inplace_int64_to_str(lmjm__vzx, tvnb__qftgp, val)
        setitem_str_offset(A, ind + 1, gay__nsec + tvnb__qftgp)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        lmjm__vzx, = args
        cwirr__xhsgl = context.insert_const_string(builder.module, '<NA>')
        esvfl__drel = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, lmjm__vzx, cwirr__xhsgl, esvfl__drel, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    fnrry__qry = len('<NA>')

    def impl(A, ind):
        gay__nsec = getitem_str_offset(A, ind)
        lwp__mcla = gay__nsec + fnrry__qry
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            gay__nsec, lwp__mcla)
        lmjm__vzx = get_data_ptr_ind(A, gay__nsec)
        inplace_set_NA_str(lmjm__vzx)
        setitem_str_offset(A, ind + 1, gay__nsec + fnrry__qry)
        str_arr_set_not_na(A, ind)
    return impl


@overload(operator.getitem, no_unliteral=True)
def str_arr_getitem_int(A, ind):
    if A != string_array_type:
        return
    if isinstance(ind, types.Integer):

        def str_arr_getitem_impl(A, ind):
            if ind < 0:
                ind += A.size
            gay__nsec = getitem_str_offset(A, ind)
            jhb__mhu = getitem_str_offset(A, ind + 1)
            vmh__qwfz = jhb__mhu - gay__nsec
            lmjm__vzx = get_data_ptr_ind(A, gay__nsec)
            nwpwa__sqc = decode_utf8(lmjm__vzx, vmh__qwfz)
            return nwpwa__sqc
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            ctl__ozllp = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(ctl__ozllp):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            kba__imed = get_data_ptr(out_arr).data
            pkhay__lmo = get_data_ptr(A).data
            mlr__yimz = 0
            lmncg__fuk = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(ctl__ozllp):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    qkf__ddeoc = get_str_arr_item_length(A, i)
                    if qkf__ddeoc == 1:
                        copy_single_char(kba__imed, lmncg__fuk, pkhay__lmo,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(kba__imed, lmncg__fuk, pkhay__lmo,
                            getitem_str_offset(A, i), qkf__ddeoc, 1)
                    lmncg__fuk += qkf__ddeoc
                    setitem_str_offset(out_arr, mlr__yimz + 1, lmncg__fuk)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, mlr__yimz)
                    else:
                        str_arr_set_not_na(out_arr, mlr__yimz)
                    mlr__yimz += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            ctl__ozllp = len(ind)
            out_arr = pre_alloc_string_array(ctl__ozllp, -1)
            mlr__yimz = 0
            for i in range(ctl__ozllp):
                dhb__uryc = A[ind[i]]
                out_arr[mlr__yimz] = dhb__uryc
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, mlr__yimz)
                mlr__yimz += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            ctl__ozllp = len(A)
            tbfp__fvrxa = numba.cpython.unicode._normalize_slice(ind,
                ctl__ozllp)
            blwoe__chyu = numba.cpython.unicode._slice_span(tbfp__fvrxa)
            if tbfp__fvrxa.step == 1:
                gay__nsec = getitem_str_offset(A, tbfp__fvrxa.start)
                jhb__mhu = getitem_str_offset(A, tbfp__fvrxa.stop)
                n_chars = jhb__mhu - gay__nsec
                upw__bnkqi = pre_alloc_string_array(blwoe__chyu, np.int64(
                    n_chars))
                for i in range(blwoe__chyu):
                    upw__bnkqi[i] = A[tbfp__fvrxa.start + i]
                    if str_arr_is_na(A, tbfp__fvrxa.start + i):
                        str_arr_set_na(upw__bnkqi, i)
                return upw__bnkqi
            else:
                upw__bnkqi = pre_alloc_string_array(blwoe__chyu, -1)
                for i in range(blwoe__chyu):
                    upw__bnkqi[i] = A[tbfp__fvrxa.start + i * tbfp__fvrxa.step]
                    if str_arr_is_na(A, tbfp__fvrxa.start + i * tbfp__fvrxa
                        .step):
                        str_arr_set_na(upw__bnkqi, i)
                return upw__bnkqi
        return str_arr_slice_impl
    raise BodoError(
        f'getitem for StringArray with indexing type {ind} not supported.')


dummy_use = numba.njit(lambda a: None)


@overload(operator.setitem)
def str_arr_setitem(A, idx, val):
    if A != string_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    qjv__xiije = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(qjv__xiije)
        dbpi__ihf = 4

        def impl_scalar(A, idx, val):
            qoob__ejj = (val._length if val._is_ascii else dbpi__ihf * val.
                _length)
            obs__bfz = A._data
            gay__nsec = np.int64(getitem_str_offset(A, idx))
            lwp__mcla = gay__nsec + qoob__ejj
            bodo.libs.array_item_arr_ext.ensure_data_capacity(obs__bfz,
                gay__nsec, lwp__mcla)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                lwp__mcla, val._data, val._length, val._kind, val._is_ascii,
                idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                tbfp__fvrxa = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                jmt__msn = tbfp__fvrxa.start
                obs__bfz = A._data
                gay__nsec = np.int64(getitem_str_offset(A, jmt__msn))
                lwp__mcla = gay__nsec + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(obs__bfz,
                    gay__nsec, lwp__mcla)
                set_string_array_range(A, val, jmt__msn, gay__nsec)
                bspyy__tlcyi = 0
                for i in range(tbfp__fvrxa.start, tbfp__fvrxa.stop,
                    tbfp__fvrxa.step):
                    if str_arr_is_na(val, bspyy__tlcyi):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    bspyy__tlcyi += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                axwbk__itds = str_list_to_array(val)
                A[idx] = axwbk__itds
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                tbfp__fvrxa = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                for i in range(tbfp__fvrxa.start, tbfp__fvrxa.stop,
                    tbfp__fvrxa.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(qjv__xiije)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                ctl__ozllp = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(ctl__ozllp, -1)
                for i in numba.parfors.parfor.internal_prange(ctl__ozllp):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        out_arr[i] = val
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_scalar
        elif val == string_array_type or isinstance(val, types.Array
            ) and isinstance(val.dtype, types.UnicodeCharSeq):

            def impl_bool_arr(A, idx, val):
                ctl__ozllp = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(ctl__ozllp, -1)
                gwmv__jqpy = 0
                for i in numba.parfors.parfor.internal_prange(ctl__ozllp):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, gwmv__jqpy):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, gwmv__jqpy)
                        else:
                            out_arr[i] = str(val[gwmv__jqpy])
                        gwmv__jqpy += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(qjv__xiije)
    raise BodoError(qjv__xiije)


@overload_attribute(StringArrayType, 'dtype')
def overload_str_arr_dtype(A):
    return lambda A: pd.StringDtype()


@overload_attribute(StringArrayType, 'ndim')
def overload_str_arr_ndim(A):
    return lambda A: 1


@overload_method(StringArrayType, 'astype', no_unliteral=True)
def overload_str_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "StringArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.Function) and dtype.key[0] == str:
        return lambda A, dtype, copy=True: A
    jyon__tuvax = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(jyon__tuvax, (types.Float, types.Integer)
        ) and jyon__tuvax not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(jyon__tuvax, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ctl__ozllp = len(A)
            B = np.empty(ctl__ozllp, jyon__tuvax)
            for i in numba.parfors.parfor.internal_prange(ctl__ozllp):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif jyon__tuvax == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ctl__ozllp = len(A)
            B = np.empty(ctl__ozllp, jyon__tuvax)
            for i in numba.parfors.parfor.internal_prange(ctl__ozllp):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif jyon__tuvax == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ctl__ozllp = len(A)
            B = np.empty(ctl__ozllp, jyon__tuvax)
            for i in numba.parfors.parfor.internal_prange(ctl__ozllp):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ctl__ozllp = len(A)
            B = np.empty(ctl__ozllp, jyon__tuvax)
            for i in numba.parfors.parfor.internal_prange(ctl__ozllp):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        lmjm__vzx, vmh__qwfz = args
        mvxhd__mbcal = context.get_python_api(builder)
        eccvf__ncoc = mvxhd__mbcal.string_from_string_and_size(lmjm__vzx,
            vmh__qwfz)
        zqar__gad = mvxhd__mbcal.to_native_value(string_type, eccvf__ncoc
            ).value
        gpsxg__rcdy = cgutils.create_struct_proxy(string_type)(context,
            builder, zqar__gad)
        gpsxg__rcdy.hash = gpsxg__rcdy.hash.type(-1)
        mvxhd__mbcal.decref(eccvf__ncoc)
        return gpsxg__rcdy._getvalue()
    return string_type(types.voidptr, types.intp), codegen


def get_arr_data_ptr(arr, ind):
    return arr


@overload(get_arr_data_ptr, no_unliteral=True)
def overload_get_arr_data_ptr(arr, ind):
    assert isinstance(types.unliteral(ind), types.Integer)
    if isinstance(arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(arr, ind):
            return bodo.hiframes.split_impl.get_c_arr_ptr(arr._data.ctypes, ind
                )
        return impl_int
    assert isinstance(arr, types.Array)

    def impl_np(arr, ind):
        return bodo.hiframes.split_impl.get_c_arr_ptr(arr.ctypes, ind)
    return impl_np


def set_to_numeric_out_na_err(out_arr, out_ind, err_code):
    pass


@overload(set_to_numeric_out_na_err)
def set_to_numeric_out_na_err_overload(out_arr, out_ind, err_code):
    if isinstance(out_arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(out_arr, out_ind, err_code):
            bodo.libs.int_arr_ext.set_bit_to_arr(out_arr._null_bitmap,
                out_ind, 0 if err_code == -1 else 1)
        return impl_int
    assert isinstance(out_arr, types.Array)
    if isinstance(out_arr.dtype, types.Float):

        def impl_np(out_arr, out_ind, err_code):
            if err_code == -1:
                out_arr[out_ind] = np.nan
        return impl_np
    return lambda out_arr, out_ind, err_code: None


@numba.njit(no_cpython_wrapper=True)
def str_arr_item_to_numeric(out_arr, out_ind, str_arr, ind):
    str_arr = decode_if_dict_array(str_arr)
    err_code = _str_arr_item_to_numeric(get_arr_data_ptr(out_arr, out_ind),
        str_arr, ind, out_arr.dtype)
    set_to_numeric_out_na_err(out_arr, out_ind, err_code)


@intrinsic
def _str_arr_item_to_numeric(typingctx, out_ptr_t, str_arr_t, ind_t,
    out_dtype_t=None):
    assert str_arr_t == string_array_type, '_str_arr_item_to_numeric: str arr expected'
    assert ind_t == types.int64, '_str_arr_item_to_numeric: integer index expected'

    def codegen(context, builder, sig, args):
        ftyyd__ulfh, arr, ind, rra__reo = args
        ldj__asb = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, ldj__asb.
            offsets).data
        data = context.make_helper(builder, char_arr_type, ldj__asb.data).data
        knae__ckrd = lir.FunctionType(lir.IntType(32), [ftyyd__ulfh.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        vbnt__fjyws = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            vbnt__fjyws = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        eakp__rnqpu = cgutils.get_or_insert_function(builder.module,
            knae__ckrd, vbnt__fjyws)
        return builder.call(eakp__rnqpu, [ftyyd__ulfh, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    hved__gqdwn = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    knae__ckrd = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(32)])
    his__xmcz = cgutils.get_or_insert_function(c.builder.module, knae__ckrd,
        name='string_array_from_sequence')
    wjuzl__zonu = c.builder.call(his__xmcz, [val, hved__gqdwn])
    chyp__dvcsh = ArrayItemArrayType(char_arr_type)
    ygw__xcc = c.context.make_helper(c.builder, chyp__dvcsh)
    ygw__xcc.meminfo = wjuzl__zonu
    sfes__vox = c.context.make_helper(c.builder, typ)
    obs__bfz = ygw__xcc._getvalue()
    sfes__vox.data = obs__bfz
    vxq__sszde = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(sfes__vox._getvalue(), is_error=vxq__sszde)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    ctl__ozllp = len(pyval)
    lmncg__fuk = 0
    zdayk__nrkb = np.empty(ctl__ozllp + 1, np_offset_type)
    vkmlf__atyew = []
    blhr__erij = np.empty(ctl__ozllp + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        zdayk__nrkb[i] = lmncg__fuk
        agizj__adp = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(blhr__erij, i, int(not agizj__adp)
            )
        if agizj__adp:
            continue
        yuks__tawbe = list(s.encode()) if isinstance(s, str) else list(s)
        vkmlf__atyew.extend(yuks__tawbe)
        lmncg__fuk += len(yuks__tawbe)
    zdayk__nrkb[ctl__ozllp] = lmncg__fuk
    fnbh__ghps = np.array(vkmlf__atyew, np.uint8)
    rfhqe__ibwc = context.get_constant(types.int64, ctl__ozllp)
    fepc__wifgq = context.get_constant_generic(builder, char_arr_type,
        fnbh__ghps)
    xtlq__obm = context.get_constant_generic(builder, offset_arr_type,
        zdayk__nrkb)
    yujx__kkhxc = context.get_constant_generic(builder,
        null_bitmap_arr_type, blhr__erij)
    ldj__asb = lir.Constant.literal_struct([rfhqe__ibwc, fepc__wifgq,
        xtlq__obm, yujx__kkhxc])
    ldj__asb = cgutils.global_constant(builder, '.const.payload', ldj__asb
        ).bitcast(cgutils.voidptr_t)
    hdqt__avomw = context.get_constant(types.int64, -1)
    pubh__yip = context.get_constant_null(types.voidptr)
    lerye__vewcq = lir.Constant.literal_struct([hdqt__avomw, pubh__yip,
        pubh__yip, ldj__asb, hdqt__avomw])
    lerye__vewcq = cgutils.global_constant(builder, '.const.meminfo',
        lerye__vewcq).bitcast(cgutils.voidptr_t)
    obs__bfz = lir.Constant.literal_struct([lerye__vewcq])
    sfes__vox = lir.Constant.literal_struct([obs__bfz])
    return sfes__vox


def pre_alloc_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_str_arr_ext_pre_alloc_string_array
    ) = pre_alloc_str_arr_equiv


@overload(glob.glob, no_unliteral=True)
def overload_glob_glob(pathname, recursive=False):

    def _glob_glob_impl(pathname, recursive=False):
        with numba.objmode(l='list_str_type'):
            l = glob.glob(pathname, recursive=recursive)
        return l
    return _glob_glob_impl
