"""Nullable integer array corresponding to Pandas IntegerArray.
However, nulls are stored in bit arrays similar to Arrow's arrays.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs.str_arr_ext import kBitmask
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('mask_arr_to_bitmap', hstr_ext.mask_arr_to_bitmap)
ll.add_symbol('is_pd_int_array', array_ext.is_pd_int_array)
ll.add_symbol('int_array_from_sequence', array_ext.int_array_from_sequence)
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, check_unsupported_args, is_iterable_type, is_list_like_index_type, is_overload_false, is_overload_none, is_overload_true, parse_dtype, raise_bodo_error, to_nullable_type


class IntegerArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(IntegerArrayType, self).__init__(name=
            f'IntegerArrayType({dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntegerArrayType(self.dtype)

    @property
    def get_pandas_scalar_type_instance(self):
        lmg__uyu = int(np.log2(self.dtype.bitwidth // 8))
        kzdae__zfvyz = 0 if self.dtype.signed else 4
        idx = lmg__uyu + kzdae__zfvyz
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qkm__cwdtq = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, qkm__cwdtq)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    xwmfl__kharv = 8 * val.dtype.itemsize
    pahmi__ckre = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(pahmi__ckre, xwmfl__kharv))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        slxxe__hyel = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(slxxe__hyel)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    wgyea__jedh = c.context.insert_const_string(c.builder.module, 'pandas')
    gco__tnmu = c.pyapi.import_module_noblock(wgyea__jedh)
    zaht__yjkzw = c.pyapi.call_method(gco__tnmu, str(typ)[:-2], ())
    c.pyapi.decref(gco__tnmu)
    return zaht__yjkzw


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    xwmfl__kharv = 8 * val.itemsize
    pahmi__ckre = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(pahmi__ckre, xwmfl__kharv))
    return IntDtype(dtype)


def _register_int_dtype(t):
    typeof_impl.register(t)(typeof_pd_int_dtype)
    int_dtype = typeof_pd_int_dtype(t(), None)
    type_callable(t)(lambda c: lambda : int_dtype)
    lower_builtin(t)(lambda c, b, s, a: c.get_dummy_value())


pd_int_dtype_classes = (pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.
    Int64Dtype, pd.UInt8Dtype, pd.UInt16Dtype, pd.UInt32Dtype, pd.UInt64Dtype)
for t in pd_int_dtype_classes:
    _register_int_dtype(t)


@numba.extending.register_jitable
def mask_arr_to_bitmap(mask_arr):
    n = len(mask_arr)
    oxvxy__noy = n + 7 >> 3
    cjs__zmrhr = np.empty(oxvxy__noy, np.uint8)
    for i in range(n):
        kix__lruha = i // 8
        cjs__zmrhr[kix__lruha] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            cjs__zmrhr[kix__lruha]) & kBitmask[i % 8]
    return cjs__zmrhr


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    mrlr__hhs = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(mrlr__hhs)
    c.pyapi.decref(mrlr__hhs)
    orn__uagra = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oxvxy__noy = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    hth__npzk = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [oxvxy__noy])
    mlbq__gxq = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    kosn__vtdss = cgutils.get_or_insert_function(c.builder.module,
        mlbq__gxq, name='is_pd_int_array')
    tyv__qmyef = c.builder.call(kosn__vtdss, [obj])
    pqrhg__amx = c.builder.icmp_unsigned('!=', tyv__qmyef, tyv__qmyef.type(0))
    with c.builder.if_else(pqrhg__amx) as (irc__dwxk, afzd__ymh):
        with irc__dwxk:
            ihd__pam = c.pyapi.object_getattr_string(obj, '_data')
            orn__uagra.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), ihd__pam).value
            yflq__eez = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), yflq__eez).value
            c.pyapi.decref(ihd__pam)
            c.pyapi.decref(yflq__eez)
            hrplm__ojrp = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            mlbq__gxq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            kosn__vtdss = cgutils.get_or_insert_function(c.builder.module,
                mlbq__gxq, name='mask_arr_to_bitmap')
            c.builder.call(kosn__vtdss, [hth__npzk.data, hrplm__ojrp.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with afzd__ymh:
            cuo__xnd = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
                types.Array(typ.dtype, 1, 'C'), [n])
            mlbq__gxq = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            ckjnf__hpn = cgutils.get_or_insert_function(c.builder.module,
                mlbq__gxq, name='int_array_from_sequence')
            c.builder.call(ckjnf__hpn, [obj, c.builder.bitcast(cuo__xnd.
                data, lir.IntType(8).as_pointer()), hth__npzk.data])
            orn__uagra.data = cuo__xnd._getvalue()
    orn__uagra.null_bitmap = hth__npzk._getvalue()
    vuqwx__uthaq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(orn__uagra._getvalue(), is_error=vuqwx__uthaq)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    orn__uagra = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        orn__uagra.data, c.env_manager)
    ybbqd__blaao = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, orn__uagra.null_bitmap).data
    mrlr__hhs = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(mrlr__hhs)
    wgyea__jedh = c.context.insert_const_string(c.builder.module, 'numpy')
    jivun__bvdap = c.pyapi.import_module_noblock(wgyea__jedh)
    ims__pfglc = c.pyapi.object_getattr_string(jivun__bvdap, 'bool_')
    mask_arr = c.pyapi.call_method(jivun__bvdap, 'empty', (mrlr__hhs,
        ims__pfglc))
    pxj__dlzet = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    rpo__fcmh = c.pyapi.object_getattr_string(pxj__dlzet, 'data')
    rkal__ledig = c.builder.inttoptr(c.pyapi.long_as_longlong(rpo__fcmh),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as tad__wrr:
        i = tad__wrr.index
        edxf__nbu = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        ybldb__yyng = c.builder.load(cgutils.gep(c.builder, ybbqd__blaao,
            edxf__nbu))
        dvzdw__wtlb = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(ybldb__yyng, dvzdw__wtlb), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        xllj__rth = cgutils.gep(c.builder, rkal__ledig, i)
        c.builder.store(val, xllj__rth)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        orn__uagra.null_bitmap)
    wgyea__jedh = c.context.insert_const_string(c.builder.module, 'pandas')
    gco__tnmu = c.pyapi.import_module_noblock(wgyea__jedh)
    ubt__oledz = c.pyapi.object_getattr_string(gco__tnmu, 'arrays')
    zaht__yjkzw = c.pyapi.call_method(ubt__oledz, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(gco__tnmu)
    c.pyapi.decref(mrlr__hhs)
    c.pyapi.decref(jivun__bvdap)
    c.pyapi.decref(ims__pfglc)
    c.pyapi.decref(pxj__dlzet)
    c.pyapi.decref(rpo__fcmh)
    c.pyapi.decref(ubt__oledz)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return zaht__yjkzw


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        wqpxu__ejn, kfv__cngiw = args
        orn__uagra = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        orn__uagra.data = wqpxu__ejn
        orn__uagra.null_bitmap = kfv__cngiw
        context.nrt.incref(builder, signature.args[0], wqpxu__ejn)
        context.nrt.incref(builder, signature.args[1], kfv__cngiw)
        return orn__uagra._getvalue()
    zafe__ydamv = IntegerArrayType(data.dtype)
    vxv__dhy = zafe__ydamv(data, null_bitmap)
    return vxv__dhy, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    ror__udnq = np.empty(n, pyval.dtype.type)
    sck__puyb = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        her__vszue = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(sck__puyb, i, int(not her__vszue))
        if not her__vszue:
            ror__udnq[i] = s
    zvo__fmr = context.get_constant_generic(builder, types.Array(typ.dtype,
        1, 'C'), ror__udnq)
    sjbuw__qwyne = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), sck__puyb)
    return lir.Constant.literal_struct([zvo__fmr, sjbuw__qwyne])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    vma__vcwtc = args[0]
    if equiv_set.has_shape(vma__vcwtc):
        return ArrayAnalysis.AnalyzeResult(shape=vma__vcwtc, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    vma__vcwtc = args[0]
    if equiv_set.has_shape(vma__vcwtc):
        return ArrayAnalysis.AnalyzeResult(shape=vma__vcwtc, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_init_integer_array = (
    init_integer_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_integer_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_integer_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_integer_array
numba.core.ir_utils.alias_func_extensions['get_int_arr_data',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_int_arr_bitmap',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_int_array(n, dtype):
    ror__udnq = np.empty(n, dtype)
    bzp__itb = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(ror__udnq, bzp__itb)


def alloc_int_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_alloc_int_array = (
    alloc_int_array_equiv)


@numba.extending.register_jitable
def set_bit_to_arr(bits, i, bit_is_set):
    bits[i // 8] ^= np.uint8(-np.uint8(bit_is_set) ^ bits[i // 8]) & kBitmask[
        i % 8]


@numba.extending.register_jitable
def get_bit_bitmap_arr(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@overload(operator.getitem, no_unliteral=True)
def int_arr_getitem(A, ind):
    if not isinstance(A, IntegerArrayType):
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            qsn__wucjk, ussx__uwect = array_getitem_bool_index(A, ind)
            return init_integer_array(qsn__wucjk, ussx__uwect)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            qsn__wucjk, ussx__uwect = array_getitem_int_index(A, ind)
            return init_integer_array(qsn__wucjk, ussx__uwect)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            qsn__wucjk, ussx__uwect = array_getitem_slice_index(A, ind)
            return init_integer_array(qsn__wucjk, ussx__uwect)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    ijfcl__uyx = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    kcu__vlhp = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if kcu__vlhp:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(ijfcl__uyx)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or kcu__vlhp):
        raise BodoError(ijfcl__uyx)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):

        def impl_arr_ind_mask(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind_mask
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for IntegerArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_int_arr_len(A):
    if isinstance(A, IntegerArrayType):
        return lambda A: len(A._data)


@overload_attribute(IntegerArrayType, 'shape')
def overload_int_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(IntegerArrayType, 'dtype')
def overload_int_arr_dtype(A):
    dtype_class = getattr(pd, '{}Int{}Dtype'.format('' if A.dtype.signed else
        'U', A.dtype.bitwidth))
    return lambda A: dtype_class()


@overload_attribute(IntegerArrayType, 'ndim')
def overload_int_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntegerArrayType, 'nbytes')
def int_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(IntegerArrayType, 'copy', no_unliteral=True)
def overload_int_arr_copy(A, dtype=None):
    if not is_overload_none(dtype):
        return lambda A, dtype=None: A.astype(dtype, copy=True)
    else:
        return lambda A, dtype=None: bodo.libs.int_arr_ext.init_integer_array(
            bodo.libs.int_arr_ext.get_int_arr_data(A).copy(), bodo.libs.
            int_arr_ext.get_int_arr_bitmap(A).copy())


@overload_method(IntegerArrayType, 'astype', no_unliteral=True)
def overload_int_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "IntegerArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.NumberClass):
        dtype = dtype.dtype
    if isinstance(dtype, IntDtype) and A.dtype == dtype.dtype:
        if is_overload_false(copy):
            return lambda A, dtype, copy=True: A
        elif is_overload_true(copy):
            return lambda A, dtype, copy=True: A.copy()
        else:

            def impl(A, dtype, copy=True):
                if copy:
                    return A.copy()
                else:
                    return A
            return impl
    if isinstance(dtype, IntDtype):
        np_dtype = dtype.dtype
        return (lambda A, dtype, copy=True: bodo.libs.int_arr_ext.
            init_integer_array(bodo.libs.int_arr_ext.get_int_arr_data(A).
            astype(np_dtype), bodo.libs.int_arr_ext.get_int_arr_bitmap(A).
            copy()))
    nb_dtype = parse_dtype(dtype, 'IntegerArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.int_arr_ext.get_int_arr_data(A)
            n = len(data)
            wxig__bmhh = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                wxig__bmhh[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    wxig__bmhh[i] = np.nan
            return wxig__bmhh
        return impl_float
    return lambda A, dtype, copy=True: bodo.libs.int_arr_ext.get_int_arr_data(A
        ).astype(nb_dtype)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def apply_null_mask(arr, bitmap, mask_fill, inplace):
    assert isinstance(arr, types.Array)
    if isinstance(arr.dtype, types.Integer):
        if is_overload_none(inplace):
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap.copy()))
        else:
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap))
    if isinstance(arr.dtype, types.Float):

        def impl(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = np.nan
            return arr
        return impl
    if arr.dtype == types.bool_:

        def impl_bool(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = mask_fill
            return arr
        return impl_bool
    return lambda arr, bitmap, mask_fill, inplace: arr


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def merge_bitmaps(B1, B2, n, inplace):
    assert B1 == types.Array(types.uint8, 1, 'C')
    assert B2 == types.Array(types.uint8, 1, 'C')
    if not is_overload_none(inplace):

        def impl_inplace(B1, B2, n, inplace):
            for i in numba.parfors.parfor.internal_prange(n):
                smnnh__kroo = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                eoj__pvhal = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                vsb__hkkiw = smnnh__kroo & eoj__pvhal
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, vsb__hkkiw)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        oxvxy__noy = n + 7 >> 3
        wxig__bmhh = np.empty(oxvxy__noy, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            smnnh__kroo = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            eoj__pvhal = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            vsb__hkkiw = smnnh__kroo & eoj__pvhal
            bodo.libs.int_arr_ext.set_bit_to_arr(wxig__bmhh, i, vsb__hkkiw)
        return wxig__bmhh
    return impl


ufunc_aliases = {'subtract': 'sub', 'multiply': 'mul', 'floor_divide':
    'floordiv', 'true_divide': 'truediv', 'power': 'pow', 'remainder':
    'mod', 'divide': 'div', 'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    if n_inputs == 1:

        def overload_int_arr_op_nin_1(A):
            if isinstance(A, IntegerArrayType):
                return get_nullable_array_unary_impl(op, A)
        return overload_int_arr_op_nin_1
    elif n_inputs == 2:

        def overload_series_op_nin_2(lhs, rhs):
            if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
                IntegerArrayType):
                return get_nullable_array_binary_impl(op, lhs, rhs)
        return overload_series_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for lrf__yus in numba.np.ufunc_db.get_ufuncs():
        mkgso__bta = create_op_overload(lrf__yus, lrf__yus.nin)
        overload(lrf__yus, no_unliteral=True)(mkgso__bta)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        mkgso__bta = create_op_overload(op, 2)
        overload(op)(mkgso__bta)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        mkgso__bta = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(mkgso__bta)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        mkgso__bta = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(mkgso__bta)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    mun__rww = len(arrs.types)
    buz__ati = 'def f(arrs):\n'
    zaht__yjkzw = ', '.join('arrs[{}]._data'.format(i) for i in range(mun__rww)
        )
    buz__ati += '  return ({}{})\n'.format(zaht__yjkzw, ',' if mun__rww == 
        1 else '')
    ttcye__jaf = {}
    exec(buz__ati, {}, ttcye__jaf)
    impl = ttcye__jaf['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    mun__rww = len(arrs.types)
    acmdl__gejhu = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        mun__rww))
    buz__ati = 'def f(arrs):\n'
    buz__ati += '  n = {}\n'.format(acmdl__gejhu)
    buz__ati += '  n_bytes = (n + 7) >> 3\n'
    buz__ati += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    buz__ati += '  curr_bit = 0\n'
    for i in range(mun__rww):
        buz__ati += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        buz__ati += '  for j in range(len(arrs[{}])):\n'.format(i)
        buz__ati += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        buz__ati += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        buz__ati += '    curr_bit += 1\n'
    buz__ati += '  return new_mask\n'
    ttcye__jaf = {}
    exec(buz__ati, {'np': np, 'bodo': bodo}, ttcye__jaf)
    impl = ttcye__jaf['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    uefcr__yjc = dict(skipna=skipna, min_count=min_count)
    frgcn__lde = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', uefcr__yjc, frgcn__lde)

    def impl(A, skipna=True, min_count=0):
        numba.parfors.parfor.init_prange()
        s = 0
        for i in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, i):
                val = A[i]
            s += val
        return s
    return impl


@overload_method(IntegerArrayType, 'unique', no_unliteral=True)
def overload_unique(A):
    dtype = A.dtype

    def impl_int_arr(A):
        data = []
        dvzdw__wtlb = []
        ejv__goay = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not ejv__goay:
                    data.append(dtype(1))
                    dvzdw__wtlb.append(False)
                    ejv__goay = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                dvzdw__wtlb.append(True)
        qsn__wucjk = np.array(data)
        n = len(qsn__wucjk)
        oxvxy__noy = n + 7 >> 3
        ussx__uwect = np.empty(oxvxy__noy, np.uint8)
        for nide__vegx in range(n):
            set_bit_to_arr(ussx__uwect, nide__vegx, dvzdw__wtlb[nide__vegx])
        return init_integer_array(qsn__wucjk, ussx__uwect)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    ffhvj__thlr = numba.core.registry.cpu_target.typing_context
    dner__tdqn = ffhvj__thlr.resolve_function_type(op, (types.Array(A.dtype,
        1, 'C'),), {}).return_type
    dner__tdqn = to_nullable_type(dner__tdqn)

    def impl(A):
        n = len(A)
        bjfcx__prcb = bodo.utils.utils.alloc_type(n, dner__tdqn, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(bjfcx__prcb, i)
                continue
            bjfcx__prcb[i] = op(A[i])
        return bjfcx__prcb
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    wcebt__puj = isinstance(lhs, (types.Number, types.Boolean))
    ypm__qfl = isinstance(rhs, (types.Number, types.Boolean))
    jyy__glxz = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    bawmw__sjwm = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    ffhvj__thlr = numba.core.registry.cpu_target.typing_context
    dner__tdqn = ffhvj__thlr.resolve_function_type(op, (jyy__glxz,
        bawmw__sjwm), {}).return_type
    dner__tdqn = to_nullable_type(dner__tdqn)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    ftw__xdux = 'lhs' if wcebt__puj else 'lhs[i]'
    cwj__rywei = 'rhs' if ypm__qfl else 'rhs[i]'
    irc__gfql = ('False' if wcebt__puj else
        'bodo.libs.array_kernels.isna(lhs, i)')
    ebjlv__rna = ('False' if ypm__qfl else
        'bodo.libs.array_kernels.isna(rhs, i)')
    buz__ati = 'def impl(lhs, rhs):\n'
    buz__ati += '  n = len({})\n'.format('lhs' if not wcebt__puj else 'rhs')
    if inplace:
        buz__ati += '  out_arr = {}\n'.format('lhs' if not wcebt__puj else
            'rhs')
    else:
        buz__ati += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    buz__ati += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    buz__ati += '    if ({}\n'.format(irc__gfql)
    buz__ati += '        or {}):\n'.format(ebjlv__rna)
    buz__ati += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    buz__ati += '      continue\n'
    buz__ati += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(ftw__xdux, cwj__rywei))
    buz__ati += '  return out_arr\n'
    ttcye__jaf = {}
    exec(buz__ati, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        dner__tdqn, 'op': op}, ttcye__jaf)
    impl = ttcye__jaf['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        wcebt__puj = lhs in [pd_timedelta_type]
        ypm__qfl = rhs in [pd_timedelta_type]
        if wcebt__puj:

            def impl(lhs, rhs):
                n = len(rhs)
                bjfcx__prcb = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(bjfcx__prcb, i)
                        continue
                    bjfcx__prcb[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs, rhs[i]))
                return bjfcx__prcb
            return impl
        elif ypm__qfl:

            def impl(lhs, rhs):
                n = len(lhs)
                bjfcx__prcb = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(bjfcx__prcb, i)
                        continue
                    bjfcx__prcb[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs[i], rhs))
                return bjfcx__prcb
            return impl
    return impl
