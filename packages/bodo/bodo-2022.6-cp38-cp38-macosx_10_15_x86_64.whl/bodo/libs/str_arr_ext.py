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
        kut__bxbqo = ArrayItemArrayType(char_arr_type)
        uxv__fcyz = [('data', kut__bxbqo)]
        models.StructModel.__init__(self, dmm, fe_type, uxv__fcyz)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        xjf__wjji, = args
        papo__lqjiu = context.make_helper(builder, string_array_type)
        papo__lqjiu.data = xjf__wjji
        context.nrt.incref(builder, data_typ, xjf__wjji)
        return papo__lqjiu._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    tsqi__ovf = c.context.insert_const_string(c.builder.module, 'pandas')
    ajvy__vqdr = c.pyapi.import_module_noblock(tsqi__ovf)
    qab__gds = c.pyapi.call_method(ajvy__vqdr, 'StringDtype', ())
    c.pyapi.decref(ajvy__vqdr)
    return qab__gds


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        zrbxj__wkdq = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs,
            rhs)
        if zrbxj__wkdq is not None:
            return zrbxj__wkdq
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ibrby__twk = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ibrby__twk)
                for i in numba.parfors.parfor.internal_prange(ibrby__twk):
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
                ibrby__twk = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ibrby__twk)
                for i in numba.parfors.parfor.internal_prange(ibrby__twk):
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
                ibrby__twk = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ibrby__twk)
                for i in numba.parfors.parfor.internal_prange(ibrby__twk):
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
    nhpdx__twn = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    fhn__zygk = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and fhn__zygk or nhpdx__twn and is_str_arr_type(rhs
        ):

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
    fnfym__bxs = context.make_helper(builder, arr_typ, arr_value)
    kut__bxbqo = ArrayItemArrayType(char_arr_type)
    fio__koss = _get_array_item_arr_payload(context, builder, kut__bxbqo,
        fnfym__bxs.data)
    return fio__koss


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return fio__koss.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        khxgl__dpfy = context.make_helper(builder, offset_arr_type,
            fio__koss.offsets).data
        return _get_num_total_chars(builder, khxgl__dpfy, fio__koss.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        mnvn__ysuq = context.make_helper(builder, offset_arr_type,
            fio__koss.offsets)
        rnv__alxya = context.make_helper(builder, offset_ctypes_type)
        rnv__alxya.data = builder.bitcast(mnvn__ysuq.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        rnv__alxya.meminfo = mnvn__ysuq.meminfo
        qab__gds = rnv__alxya._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type, qab__gds
            )
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        xjf__wjji = context.make_helper(builder, char_arr_type, fio__koss.data)
        rnv__alxya = context.make_helper(builder, data_ctypes_type)
        rnv__alxya.data = xjf__wjji.data
        rnv__alxya.meminfo = xjf__wjji.meminfo
        qab__gds = rnv__alxya._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, qab__gds)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        tksh__puyj, ind = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            tksh__puyj, sig.args[0])
        xjf__wjji = context.make_helper(builder, char_arr_type, fio__koss.data)
        rnv__alxya = context.make_helper(builder, data_ctypes_type)
        rnv__alxya.data = builder.gep(xjf__wjji.data, [ind])
        rnv__alxya.meminfo = xjf__wjji.meminfo
        qab__gds = rnv__alxya._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, qab__gds)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        ffmjv__qcm, mpitq__onika, hhqka__mcal, fmsm__aqwi = args
        tear__chv = builder.bitcast(builder.gep(ffmjv__qcm, [mpitq__onika]),
            lir.IntType(8).as_pointer())
        mfooe__xwpc = builder.bitcast(builder.gep(hhqka__mcal, [fmsm__aqwi]
            ), lir.IntType(8).as_pointer())
        iys__ykzd = builder.load(mfooe__xwpc)
        builder.store(iys__ykzd, tear__chv)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        fha__jaoa = context.make_helper(builder, null_bitmap_arr_type,
            fio__koss.null_bitmap)
        rnv__alxya = context.make_helper(builder, data_ctypes_type)
        rnv__alxya.data = fha__jaoa.data
        rnv__alxya.meminfo = fha__jaoa.meminfo
        qab__gds = rnv__alxya._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, qab__gds)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        khxgl__dpfy = context.make_helper(builder, offset_arr_type,
            fio__koss.offsets).data
        return builder.load(builder.gep(khxgl__dpfy, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, fio__koss.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        hhwp__yai, ind = args
        if in_bitmap_typ == data_ctypes_type:
            rnv__alxya = context.make_helper(builder, data_ctypes_type,
                hhwp__yai)
            hhwp__yai = rnv__alxya.data
        return builder.load(builder.gep(hhwp__yai, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        hhwp__yai, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            rnv__alxya = context.make_helper(builder, data_ctypes_type,
                hhwp__yai)
            hhwp__yai = rnv__alxya.data
        builder.store(val, builder.gep(hhwp__yai, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        hefe__dbf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        kexip__ohv = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        vsh__phulo = context.make_helper(builder, offset_arr_type,
            hefe__dbf.offsets).data
        beznz__vcoww = context.make_helper(builder, offset_arr_type,
            kexip__ohv.offsets).data
        knni__oeb = context.make_helper(builder, char_arr_type, hefe__dbf.data
            ).data
        wcsv__drprz = context.make_helper(builder, char_arr_type,
            kexip__ohv.data).data
        nbesu__qmst = context.make_helper(builder, null_bitmap_arr_type,
            hefe__dbf.null_bitmap).data
        arr__vnv = context.make_helper(builder, null_bitmap_arr_type,
            kexip__ohv.null_bitmap).data
        mvcj__htpuq = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, beznz__vcoww, vsh__phulo, mvcj__htpuq)
        cgutils.memcpy(builder, wcsv__drprz, knni__oeb, builder.load(
            builder.gep(vsh__phulo, [ind])))
        glxxg__nbxgs = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        guzuc__kuotc = builder.lshr(glxxg__nbxgs, lir.Constant(lir.IntType(
            64), 3))
        cgutils.memcpy(builder, arr__vnv, nbesu__qmst, guzuc__kuotc)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        hefe__dbf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        kexip__ohv = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        vsh__phulo = context.make_helper(builder, offset_arr_type,
            hefe__dbf.offsets).data
        knni__oeb = context.make_helper(builder, char_arr_type, hefe__dbf.data
            ).data
        wcsv__drprz = context.make_helper(builder, char_arr_type,
            kexip__ohv.data).data
        num_total_chars = _get_num_total_chars(builder, vsh__phulo,
            hefe__dbf.n_arrays)
        cgutils.memcpy(builder, wcsv__drprz, knni__oeb, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        hefe__dbf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        kexip__ohv = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        vsh__phulo = context.make_helper(builder, offset_arr_type,
            hefe__dbf.offsets).data
        beznz__vcoww = context.make_helper(builder, offset_arr_type,
            kexip__ohv.offsets).data
        nbesu__qmst = context.make_helper(builder, null_bitmap_arr_type,
            hefe__dbf.null_bitmap).data
        ibrby__twk = hefe__dbf.n_arrays
        lfvh__xqw = context.get_constant(offset_type, 0)
        oxfeb__cif = cgutils.alloca_once_value(builder, lfvh__xqw)
        with cgutils.for_range(builder, ibrby__twk) as nbd__tnml:
            nnu__khfv = lower_is_na(context, builder, nbesu__qmst,
                nbd__tnml.index)
            with cgutils.if_likely(builder, builder.not_(nnu__khfv)):
                gfm__uvw = builder.load(builder.gep(vsh__phulo, [nbd__tnml.
                    index]))
                wazef__chur = builder.load(oxfeb__cif)
                builder.store(gfm__uvw, builder.gep(beznz__vcoww, [
                    wazef__chur]))
                builder.store(builder.add(wazef__chur, lir.Constant(context
                    .get_value_type(offset_type), 1)), oxfeb__cif)
        wazef__chur = builder.load(oxfeb__cif)
        gfm__uvw = builder.load(builder.gep(vsh__phulo, [ibrby__twk]))
        builder.store(gfm__uvw, builder.gep(beznz__vcoww, [wazef__chur]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        avd__ikyw, ind, str, sjdgw__ygy = args
        avd__ikyw = context.make_array(sig.args[0])(context, builder, avd__ikyw
            )
        hppn__eochm = builder.gep(avd__ikyw.data, [ind])
        cgutils.raw_memcpy(builder, hppn__eochm, str, sjdgw__ygy, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        hppn__eochm, ind, vpguz__fprvz, sjdgw__ygy = args
        hppn__eochm = builder.gep(hppn__eochm, [ind])
        cgutils.raw_memcpy(builder, hppn__eochm, vpguz__fprvz, sjdgw__ygy, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            fke__rgo = A._data
            return np.int64(getitem_str_offset(fke__rgo, idx + 1) -
                getitem_str_offset(fke__rgo, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    itzje__umjrv = np.int64(getitem_str_offset(A, i))
    olk__gzb = np.int64(getitem_str_offset(A, i + 1))
    l = olk__gzb - itzje__umjrv
    rmkb__ianbs = get_data_ptr_ind(A, itzje__umjrv)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(rmkb__ianbs, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    sgk__nbs = getitem_str_offset(A, i)
    eucpr__djd = getitem_str_offset(A, i + 1)
    hvjix__kzvd = eucpr__djd - sgk__nbs
    jnf__qgz = getitem_str_offset(B, j)
    nssx__pnlen = jnf__qgz + hvjix__kzvd
    setitem_str_offset(B, j + 1, nssx__pnlen)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if hvjix__kzvd != 0:
        xjf__wjji = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(xjf__wjji, np.
            int64(jnf__qgz), np.int64(nssx__pnlen))
        rgjy__hpfv = get_data_ptr(B).data
        iumz__ybq = get_data_ptr(A).data
        memcpy_region(rgjy__hpfv, jnf__qgz, iumz__ybq, sgk__nbs, hvjix__kzvd, 1
            )


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    ibrby__twk = len(str_arr)
    ubyom__dlol = np.empty(ibrby__twk, np.bool_)
    for i in range(ibrby__twk):
        ubyom__dlol[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return ubyom__dlol


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            ibrby__twk = len(data)
            l = []
            for i in range(ibrby__twk):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        vcvpv__vfa = data.count
        hbtr__bbk = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(vcvpv__vfa)]
        if is_overload_true(str_null_bools):
            hbtr__bbk += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(vcvpv__vfa) if is_str_arr_type(data.types[i]) or data
                .types[i] == binary_array_type]
        vuv__vgeg = 'def f(data, str_null_bools=None):\n'
        vuv__vgeg += '  return ({}{})\n'.format(', '.join(hbtr__bbk), ',' if
            vcvpv__vfa == 1 else '')
        egjd__tkww = {}
        exec(vuv__vgeg, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, egjd__tkww)
        ixp__dtkv = egjd__tkww['f']
        return ixp__dtkv
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                ibrby__twk = len(list_data)
                for i in range(ibrby__twk):
                    vpguz__fprvz = list_data[i]
                    str_arr[i] = vpguz__fprvz
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                ibrby__twk = len(list_data)
                for i in range(ibrby__twk):
                    vpguz__fprvz = list_data[i]
                    str_arr[i] = vpguz__fprvz
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        vcvpv__vfa = str_arr.count
        alpe__efbk = 0
        vuv__vgeg = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(vcvpv__vfa):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                vuv__vgeg += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, vcvpv__vfa + alpe__efbk))
                alpe__efbk += 1
            else:
                vuv__vgeg += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        vuv__vgeg += '  return\n'
        egjd__tkww = {}
        exec(vuv__vgeg, {'cp_str_list_to_array': cp_str_list_to_array},
            egjd__tkww)
        hmcfe__fjyz = egjd__tkww['f']
        return hmcfe__fjyz
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            ibrby__twk = len(str_list)
            str_arr = pre_alloc_string_array(ibrby__twk, -1)
            for i in range(ibrby__twk):
                vpguz__fprvz = str_list[i]
                str_arr[i] = vpguz__fprvz
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            ibrby__twk = len(A)
            olrv__mkb = 0
            for i in range(ibrby__twk):
                vpguz__fprvz = A[i]
                olrv__mkb += get_utf8_size(vpguz__fprvz)
            return olrv__mkb
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        ibrby__twk = len(arr)
        n_chars = num_total_chars(arr)
        appen__exp = pre_alloc_string_array(ibrby__twk, np.int64(n_chars))
        copy_str_arr_slice(appen__exp, arr, ibrby__twk)
        return appen__exp
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
    vuv__vgeg = 'def f(in_seq):\n'
    vuv__vgeg += '    n_strs = len(in_seq)\n'
    vuv__vgeg += '    A = pre_alloc_string_array(n_strs, -1)\n'
    vuv__vgeg += '    return A\n'
    egjd__tkww = {}
    exec(vuv__vgeg, {'pre_alloc_string_array': pre_alloc_string_array},
        egjd__tkww)
    rsbv__hoad = egjd__tkww['f']
    return rsbv__hoad


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        thd__kzow = 'pre_alloc_binary_array'
    else:
        thd__kzow = 'pre_alloc_string_array'
    vuv__vgeg = 'def f(in_seq):\n'
    vuv__vgeg += '    n_strs = len(in_seq)\n'
    vuv__vgeg += f'    A = {thd__kzow}(n_strs, -1)\n'
    vuv__vgeg += '    for i in range(n_strs):\n'
    vuv__vgeg += '        A[i] = in_seq[i]\n'
    vuv__vgeg += '    return A\n'
    egjd__tkww = {}
    exec(vuv__vgeg, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, egjd__tkww)
    rsbv__hoad = egjd__tkww['f']
    return rsbv__hoad


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        kzup__gnsok = builder.add(fio__koss.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        oyqnl__dlai = builder.lshr(lir.Constant(lir.IntType(64),
            offset_type.bitwidth), lir.Constant(lir.IntType(64), 3))
        guzuc__kuotc = builder.mul(kzup__gnsok, oyqnl__dlai)
        poukd__pxyhh = context.make_array(offset_arr_type)(context, builder,
            fio__koss.offsets).data
        cgutils.memset(builder, poukd__pxyhh, guzuc__kuotc, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        zsol__thgwa = fio__koss.n_arrays
        guzuc__kuotc = builder.lshr(builder.add(zsol__thgwa, lir.Constant(
            lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        lrxzk__njf = context.make_array(null_bitmap_arr_type)(context,
            builder, fio__koss.null_bitmap).data
        cgutils.memset(builder, lrxzk__njf, guzuc__kuotc, 0)
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
    cpa__pcth = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        hmw__weoru = len(len_arr)
        for i in range(hmw__weoru):
            offsets[i] = cpa__pcth
            cpa__pcth += len_arr[i]
        offsets[hmw__weoru] = cpa__pcth
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    uow__gufl = i // 8
    ihx__ied = getitem_str_bitmap(bits, uow__gufl)
    ihx__ied ^= np.uint8(-np.uint8(bit_is_set) ^ ihx__ied) & kBitmask[i % 8]
    setitem_str_bitmap(bits, uow__gufl, ihx__ied)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    ukiub__azhhu = get_null_bitmap_ptr(out_str_arr)
    yoczx__dcith = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        xtjq__jfn = get_bit_bitmap(yoczx__dcith, j)
        set_bit_to(ukiub__azhhu, out_start + j, xtjq__jfn)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, tksh__puyj, dnyq__ffjz, fhxy__qdzfb = args
        hefe__dbf = _get_str_binary_arr_payload(context, builder,
            tksh__puyj, string_array_type)
        kexip__ohv = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        vsh__phulo = context.make_helper(builder, offset_arr_type,
            hefe__dbf.offsets).data
        beznz__vcoww = context.make_helper(builder, offset_arr_type,
            kexip__ohv.offsets).data
        knni__oeb = context.make_helper(builder, char_arr_type, hefe__dbf.data
            ).data
        wcsv__drprz = context.make_helper(builder, char_arr_type,
            kexip__ohv.data).data
        num_total_chars = _get_num_total_chars(builder, vsh__phulo,
            hefe__dbf.n_arrays)
        obp__hqwyr = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        kvze__lmk = cgutils.get_or_insert_function(builder.module,
            obp__hqwyr, name='set_string_array_range')
        builder.call(kvze__lmk, [beznz__vcoww, wcsv__drprz, vsh__phulo,
            knni__oeb, dnyq__ffjz, fhxy__qdzfb, hefe__dbf.n_arrays,
            num_total_chars])
        bqzv__epm = context.typing_context.resolve_value_type(copy_nulls_range)
        ncb__iipde = bqzv__epm.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        ntu__hpw = context.get_function(bqzv__epm, ncb__iipde)
        ntu__hpw(builder, (out_arr, tksh__puyj, dnyq__ffjz))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    zoq__enhd = c.context.make_helper(c.builder, typ, val)
    kut__bxbqo = ArrayItemArrayType(char_arr_type)
    fio__koss = _get_array_item_arr_payload(c.context, c.builder,
        kut__bxbqo, zoq__enhd.data)
    ovxv__tjfhs = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    xiv__rpxb = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        xiv__rpxb = 'pd_array_from_string_array'
    obp__hqwyr = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    abqy__leg = cgutils.get_or_insert_function(c.builder.module, obp__hqwyr,
        name=xiv__rpxb)
    khxgl__dpfy = c.context.make_array(offset_arr_type)(c.context, c.
        builder, fio__koss.offsets).data
    rmkb__ianbs = c.context.make_array(char_arr_type)(c.context, c.builder,
        fio__koss.data).data
    lrxzk__njf = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, fio__koss.null_bitmap).data
    arr = c.builder.call(abqy__leg, [fio__koss.n_arrays, khxgl__dpfy,
        rmkb__ianbs, lrxzk__njf, ovxv__tjfhs])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        lrxzk__njf = context.make_array(null_bitmap_arr_type)(context,
            builder, fio__koss.null_bitmap).data
        qkqaj__tkv = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        iggx__awb = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        ihx__ied = builder.load(builder.gep(lrxzk__njf, [qkqaj__tkv],
            inbounds=True))
        okz__oocw = lir.ArrayType(lir.IntType(8), 8)
        hej__pkvi = cgutils.alloca_once_value(builder, lir.Constant(
            okz__oocw, (1, 2, 4, 8, 16, 32, 64, 128)))
        netj__ckqbk = builder.load(builder.gep(hej__pkvi, [lir.Constant(lir
            .IntType(64), 0), iggx__awb], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(ihx__ied,
            netj__ckqbk), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        qkqaj__tkv = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        iggx__awb = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        lrxzk__njf = context.make_array(null_bitmap_arr_type)(context,
            builder, fio__koss.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, fio__koss.
            offsets).data
        bsgfh__vnq = builder.gep(lrxzk__njf, [qkqaj__tkv], inbounds=True)
        ihx__ied = builder.load(bsgfh__vnq)
        okz__oocw = lir.ArrayType(lir.IntType(8), 8)
        hej__pkvi = cgutils.alloca_once_value(builder, lir.Constant(
            okz__oocw, (1, 2, 4, 8, 16, 32, 64, 128)))
        netj__ckqbk = builder.load(builder.gep(hej__pkvi, [lir.Constant(lir
            .IntType(64), 0), iggx__awb], inbounds=True))
        netj__ckqbk = builder.xor(netj__ckqbk, lir.Constant(lir.IntType(8), -1)
            )
        builder.store(builder.and_(ihx__ied, netj__ckqbk), bsgfh__vnq)
        if str_arr_typ == string_array_type:
            ybrma__ndc = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            vcdwq__epohl = builder.icmp_unsigned('!=', ybrma__ndc,
                fio__koss.n_arrays)
            with builder.if_then(vcdwq__epohl):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [ybrma__ndc]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        qkqaj__tkv = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        iggx__awb = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        lrxzk__njf = context.make_array(null_bitmap_arr_type)(context,
            builder, fio__koss.null_bitmap).data
        bsgfh__vnq = builder.gep(lrxzk__njf, [qkqaj__tkv], inbounds=True)
        ihx__ied = builder.load(bsgfh__vnq)
        okz__oocw = lir.ArrayType(lir.IntType(8), 8)
        hej__pkvi = cgutils.alloca_once_value(builder, lir.Constant(
            okz__oocw, (1, 2, 4, 8, 16, 32, 64, 128)))
        netj__ckqbk = builder.load(builder.gep(hej__pkvi, [lir.Constant(lir
            .IntType(64), 0), iggx__awb], inbounds=True))
        builder.store(builder.or_(ihx__ied, netj__ckqbk), bsgfh__vnq)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        fio__koss = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        guzuc__kuotc = builder.udiv(builder.add(fio__koss.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        lrxzk__njf = context.make_array(null_bitmap_arr_type)(context,
            builder, fio__koss.null_bitmap).data
        cgutils.memset(builder, lrxzk__njf, guzuc__kuotc, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    nibz__esapl = context.make_helper(builder, string_array_type, str_arr)
    kut__bxbqo = ArrayItemArrayType(char_arr_type)
    vdy__vvx = context.make_helper(builder, kut__bxbqo, nibz__esapl.data)
    wbwph__jcket = ArrayItemArrayPayloadType(kut__bxbqo)
    ezfs__vkjlt = context.nrt.meminfo_data(builder, vdy__vvx.meminfo)
    fms__oezzn = builder.bitcast(ezfs__vkjlt, context.get_value_type(
        wbwph__jcket).as_pointer())
    return fms__oezzn


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        zjwu__avrpt, zdfy__day = args
        hme__epqt = _get_str_binary_arr_data_payload_ptr(context, builder,
            zdfy__day)
        ltjbh__qbc = _get_str_binary_arr_data_payload_ptr(context, builder,
            zjwu__avrpt)
        fixdu__jxgoc = _get_str_binary_arr_payload(context, builder,
            zdfy__day, sig.args[1])
        rfku__gex = _get_str_binary_arr_payload(context, builder,
            zjwu__avrpt, sig.args[0])
        context.nrt.incref(builder, char_arr_type, fixdu__jxgoc.data)
        context.nrt.incref(builder, offset_arr_type, fixdu__jxgoc.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, fixdu__jxgoc.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, rfku__gex.data)
        context.nrt.decref(builder, offset_arr_type, rfku__gex.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, rfku__gex.null_bitmap
            )
        builder.store(builder.load(hme__epqt), ltjbh__qbc)
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
        ibrby__twk = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return ibrby__twk
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, hppn__eochm, iztlm__qmv = args
        fio__koss = _get_str_binary_arr_payload(context, builder, arr, sig.
            args[0])
        offsets = context.make_helper(builder, offset_arr_type, fio__koss.
            offsets).data
        data = context.make_helper(builder, char_arr_type, fio__koss.data).data
        obp__hqwyr = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        wxtfa__arvze = cgutils.get_or_insert_function(builder.module,
            obp__hqwyr, name='setitem_string_array')
        izi__mqd = context.get_constant(types.int32, -1)
        fwa__cna = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, fio__koss.
            n_arrays)
        builder.call(wxtfa__arvze, [offsets, data, num_total_chars, builder
            .extract_value(hppn__eochm, 0), iztlm__qmv, izi__mqd, fwa__cna,
            ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    obp__hqwyr = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    zdd__ktaps = cgutils.get_or_insert_function(builder.module, obp__hqwyr,
        name='is_na')
    return builder.call(zdd__ktaps, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        tear__chv, mfooe__xwpc, vcvpv__vfa, xwnnf__lzq = args
        cgutils.raw_memcpy(builder, tear__chv, mfooe__xwpc, vcvpv__vfa,
            xwnnf__lzq)
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
        hvujz__fgnr, cogdi__noa = unicode_to_utf8_and_len(val)
        jbyn__jswos = getitem_str_offset(A, ind)
        wdv__hpjfx = getitem_str_offset(A, ind + 1)
        pibh__exvj = wdv__hpjfx - jbyn__jswos
        if pibh__exvj != cogdi__noa:
            return False
        hppn__eochm = get_data_ptr_ind(A, jbyn__jswos)
        return memcmp(hppn__eochm, hvujz__fgnr, cogdi__noa) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        jbyn__jswos = getitem_str_offset(A, ind)
        pibh__exvj = bodo.libs.str_ext.int_to_str_len(val)
        tius__iri = jbyn__jswos + pibh__exvj
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            jbyn__jswos, tius__iri)
        hppn__eochm = get_data_ptr_ind(A, jbyn__jswos)
        inplace_int64_to_str(hppn__eochm, pibh__exvj, val)
        setitem_str_offset(A, ind + 1, jbyn__jswos + pibh__exvj)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        hppn__eochm, = args
        fnyn__zqan = context.insert_const_string(builder.module, '<NA>')
        uioo__xrgvo = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, hppn__eochm, fnyn__zqan, uioo__xrgvo, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    xkyn__rmxc = len('<NA>')

    def impl(A, ind):
        jbyn__jswos = getitem_str_offset(A, ind)
        tius__iri = jbyn__jswos + xkyn__rmxc
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            jbyn__jswos, tius__iri)
        hppn__eochm = get_data_ptr_ind(A, jbyn__jswos)
        inplace_set_NA_str(hppn__eochm)
        setitem_str_offset(A, ind + 1, jbyn__jswos + xkyn__rmxc)
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
            jbyn__jswos = getitem_str_offset(A, ind)
            wdv__hpjfx = getitem_str_offset(A, ind + 1)
            iztlm__qmv = wdv__hpjfx - jbyn__jswos
            hppn__eochm = get_data_ptr_ind(A, jbyn__jswos)
            uluos__edl = decode_utf8(hppn__eochm, iztlm__qmv)
            return uluos__edl
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            ibrby__twk = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(ibrby__twk):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            rgjy__hpfv = get_data_ptr(out_arr).data
            iumz__ybq = get_data_ptr(A).data
            alpe__efbk = 0
            wazef__chur = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(ibrby__twk):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    srr__mzc = get_str_arr_item_length(A, i)
                    if srr__mzc == 1:
                        copy_single_char(rgjy__hpfv, wazef__chur, iumz__ybq,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(rgjy__hpfv, wazef__chur, iumz__ybq,
                            getitem_str_offset(A, i), srr__mzc, 1)
                    wazef__chur += srr__mzc
                    setitem_str_offset(out_arr, alpe__efbk + 1, wazef__chur)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, alpe__efbk)
                    else:
                        str_arr_set_not_na(out_arr, alpe__efbk)
                    alpe__efbk += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            ibrby__twk = len(ind)
            out_arr = pre_alloc_string_array(ibrby__twk, -1)
            alpe__efbk = 0
            for i in range(ibrby__twk):
                vpguz__fprvz = A[ind[i]]
                out_arr[alpe__efbk] = vpguz__fprvz
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, alpe__efbk)
                alpe__efbk += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            ibrby__twk = len(A)
            kknei__tac = numba.cpython.unicode._normalize_slice(ind, ibrby__twk
                )
            tuhx__xep = numba.cpython.unicode._slice_span(kknei__tac)
            if kknei__tac.step == 1:
                jbyn__jswos = getitem_str_offset(A, kknei__tac.start)
                wdv__hpjfx = getitem_str_offset(A, kknei__tac.stop)
                n_chars = wdv__hpjfx - jbyn__jswos
                appen__exp = pre_alloc_string_array(tuhx__xep, np.int64(
                    n_chars))
                for i in range(tuhx__xep):
                    appen__exp[i] = A[kknei__tac.start + i]
                    if str_arr_is_na(A, kknei__tac.start + i):
                        str_arr_set_na(appen__exp, i)
                return appen__exp
            else:
                appen__exp = pre_alloc_string_array(tuhx__xep, -1)
                for i in range(tuhx__xep):
                    appen__exp[i] = A[kknei__tac.start + i * kknei__tac.step]
                    if str_arr_is_na(A, kknei__tac.start + i * kknei__tac.step
                        ):
                        str_arr_set_na(appen__exp, i)
                return appen__exp
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
    hvv__efrk = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(hvv__efrk)
        equls__nttf = 4

        def impl_scalar(A, idx, val):
            ywxv__emj = (val._length if val._is_ascii else equls__nttf *
                val._length)
            xjf__wjji = A._data
            jbyn__jswos = np.int64(getitem_str_offset(A, idx))
            tius__iri = jbyn__jswos + ywxv__emj
            bodo.libs.array_item_arr_ext.ensure_data_capacity(xjf__wjji,
                jbyn__jswos, tius__iri)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                tius__iri, val._data, val._length, val._kind, val._is_ascii,
                idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                kknei__tac = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                itzje__umjrv = kknei__tac.start
                xjf__wjji = A._data
                jbyn__jswos = np.int64(getitem_str_offset(A, itzje__umjrv))
                tius__iri = jbyn__jswos + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(xjf__wjji,
                    jbyn__jswos, tius__iri)
                set_string_array_range(A, val, itzje__umjrv, jbyn__jswos)
                fkbv__tlwl = 0
                for i in range(kknei__tac.start, kknei__tac.stop,
                    kknei__tac.step):
                    if str_arr_is_na(val, fkbv__tlwl):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    fkbv__tlwl += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                ujvv__eql = str_list_to_array(val)
                A[idx] = ujvv__eql
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                kknei__tac = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                for i in range(kknei__tac.start, kknei__tac.stop,
                    kknei__tac.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(hvv__efrk)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                ibrby__twk = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(ibrby__twk, -1)
                for i in numba.parfors.parfor.internal_prange(ibrby__twk):
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
                ibrby__twk = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(ibrby__twk, -1)
                ordc__rwtmw = 0
                for i in numba.parfors.parfor.internal_prange(ibrby__twk):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, ordc__rwtmw):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, ordc__rwtmw)
                        else:
                            out_arr[i] = str(val[ordc__rwtmw])
                        ordc__rwtmw += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(hvv__efrk)
    raise BodoError(hvv__efrk)


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
    xfcvd__mtkuk = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(xfcvd__mtkuk, (types.Float, types.Integer)
        ) and xfcvd__mtkuk not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(xfcvd__mtkuk, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ibrby__twk = len(A)
            B = np.empty(ibrby__twk, xfcvd__mtkuk)
            for i in numba.parfors.parfor.internal_prange(ibrby__twk):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif xfcvd__mtkuk == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ibrby__twk = len(A)
            B = np.empty(ibrby__twk, xfcvd__mtkuk)
            for i in numba.parfors.parfor.internal_prange(ibrby__twk):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif xfcvd__mtkuk == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ibrby__twk = len(A)
            B = np.empty(ibrby__twk, xfcvd__mtkuk)
            for i in numba.parfors.parfor.internal_prange(ibrby__twk):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ibrby__twk = len(A)
            B = np.empty(ibrby__twk, xfcvd__mtkuk)
            for i in numba.parfors.parfor.internal_prange(ibrby__twk):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        hppn__eochm, iztlm__qmv = args
        guzc__ajha = context.get_python_api(builder)
        jiua__lwxq = guzc__ajha.string_from_string_and_size(hppn__eochm,
            iztlm__qmv)
        ayg__agosu = guzc__ajha.to_native_value(string_type, jiua__lwxq).value
        lsgfx__qzik = cgutils.create_struct_proxy(string_type)(context,
            builder, ayg__agosu)
        lsgfx__qzik.hash = lsgfx__qzik.hash.type(-1)
        guzc__ajha.decref(jiua__lwxq)
        return lsgfx__qzik._getvalue()
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
        swpo__ijxzi, arr, ind, zhi__pumh = args
        fio__koss = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, fio__koss.
            offsets).data
        data = context.make_helper(builder, char_arr_type, fio__koss.data).data
        obp__hqwyr = lir.FunctionType(lir.IntType(32), [swpo__ijxzi.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        yzsi__afv = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            yzsi__afv = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        dke__zxrin = cgutils.get_or_insert_function(builder.module,
            obp__hqwyr, yzsi__afv)
        return builder.call(dke__zxrin, [swpo__ijxzi, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    ovxv__tjfhs = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    obp__hqwyr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(32)])
    ths__blt = cgutils.get_or_insert_function(c.builder.module, obp__hqwyr,
        name='string_array_from_sequence')
    lbuk__mue = c.builder.call(ths__blt, [val, ovxv__tjfhs])
    kut__bxbqo = ArrayItemArrayType(char_arr_type)
    vdy__vvx = c.context.make_helper(c.builder, kut__bxbqo)
    vdy__vvx.meminfo = lbuk__mue
    nibz__esapl = c.context.make_helper(c.builder, typ)
    xjf__wjji = vdy__vvx._getvalue()
    nibz__esapl.data = xjf__wjji
    ajdp__gez = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(nibz__esapl._getvalue(), is_error=ajdp__gez)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    ibrby__twk = len(pyval)
    wazef__chur = 0
    ixh__mtuvy = np.empty(ibrby__twk + 1, np_offset_type)
    mkozm__rces = []
    srqs__txieq = np.empty(ibrby__twk + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        ixh__mtuvy[i] = wazef__chur
        hfi__nksyh = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(srqs__txieq, i, int(not
            hfi__nksyh))
        if hfi__nksyh:
            continue
        wtie__gdi = list(s.encode()) if isinstance(s, str) else list(s)
        mkozm__rces.extend(wtie__gdi)
        wazef__chur += len(wtie__gdi)
    ixh__mtuvy[ibrby__twk] = wazef__chur
    amdhb__klw = np.array(mkozm__rces, np.uint8)
    iik__nwx = context.get_constant(types.int64, ibrby__twk)
    acqz__yvs = context.get_constant_generic(builder, char_arr_type, amdhb__klw
        )
    nfazl__eko = context.get_constant_generic(builder, offset_arr_type,
        ixh__mtuvy)
    fdbmd__iqwg = context.get_constant_generic(builder,
        null_bitmap_arr_type, srqs__txieq)
    fio__koss = lir.Constant.literal_struct([iik__nwx, acqz__yvs,
        nfazl__eko, fdbmd__iqwg])
    fio__koss = cgutils.global_constant(builder, '.const.payload', fio__koss
        ).bitcast(cgutils.voidptr_t)
    debnm__pze = context.get_constant(types.int64, -1)
    ulp__zoh = context.get_constant_null(types.voidptr)
    zjgn__xahtq = lir.Constant.literal_struct([debnm__pze, ulp__zoh,
        ulp__zoh, fio__koss, debnm__pze])
    zjgn__xahtq = cgutils.global_constant(builder, '.const.meminfo',
        zjgn__xahtq).bitcast(cgutils.voidptr_t)
    xjf__wjji = lir.Constant.literal_struct([zjgn__xahtq])
    nibz__esapl = lir.Constant.literal_struct([xjf__wjji])
    return nibz__esapl


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
