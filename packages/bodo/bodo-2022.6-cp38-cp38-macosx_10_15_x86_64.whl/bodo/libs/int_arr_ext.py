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
        axja__thpu = int(np.log2(self.dtype.bitwidth // 8))
        kalr__hzr = 0 if self.dtype.signed else 4
        idx = axja__thpu + kalr__hzr
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        nahmg__szorz = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, nahmg__szorz)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    jyhfs__ribej = 8 * val.dtype.itemsize
    bvlpj__cuuk = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(bvlpj__cuuk, jyhfs__ribej))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        qbqpb__hdt = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(qbqpb__hdt)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    bqa__fcscf = c.context.insert_const_string(c.builder.module, 'pandas')
    eyoh__xrde = c.pyapi.import_module_noblock(bqa__fcscf)
    domlj__twbdv = c.pyapi.call_method(eyoh__xrde, str(typ)[:-2], ())
    c.pyapi.decref(eyoh__xrde)
    return domlj__twbdv


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    jyhfs__ribej = 8 * val.itemsize
    bvlpj__cuuk = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(bvlpj__cuuk, jyhfs__ribej))
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
    gio__rqbhz = n + 7 >> 3
    ikoqq__oko = np.empty(gio__rqbhz, np.uint8)
    for i in range(n):
        nmkr__efll = i // 8
        ikoqq__oko[nmkr__efll] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            ikoqq__oko[nmkr__efll]) & kBitmask[i % 8]
    return ikoqq__oko


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    ssfwu__pty = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(ssfwu__pty)
    c.pyapi.decref(ssfwu__pty)
    vzthd__bso = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    gio__rqbhz = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    xlpru__vnixc = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [gio__rqbhz])
    gfn__cscfg = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    vwtw__avr = cgutils.get_or_insert_function(c.builder.module, gfn__cscfg,
        name='is_pd_int_array')
    lhob__rcoo = c.builder.call(vwtw__avr, [obj])
    ybr__vmm = c.builder.icmp_unsigned('!=', lhob__rcoo, lhob__rcoo.type(0))
    with c.builder.if_else(ybr__vmm) as (oxo__oudb, zhyyc__num):
        with oxo__oudb:
            wfysv__xdnll = c.pyapi.object_getattr_string(obj, '_data')
            vzthd__bso.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), wfysv__xdnll).value
            mjejd__otae = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), mjejd__otae).value
            c.pyapi.decref(wfysv__xdnll)
            c.pyapi.decref(mjejd__otae)
            hbfq__utfvv = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            gfn__cscfg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            vwtw__avr = cgutils.get_or_insert_function(c.builder.module,
                gfn__cscfg, name='mask_arr_to_bitmap')
            c.builder.call(vwtw__avr, [xlpru__vnixc.data, hbfq__utfvv.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with zhyyc__num:
            zjhcr__feavb = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            gfn__cscfg = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            plp__zqc = cgutils.get_or_insert_function(c.builder.module,
                gfn__cscfg, name='int_array_from_sequence')
            c.builder.call(plp__zqc, [obj, c.builder.bitcast(zjhcr__feavb.
                data, lir.IntType(8).as_pointer()), xlpru__vnixc.data])
            vzthd__bso.data = zjhcr__feavb._getvalue()
    vzthd__bso.null_bitmap = xlpru__vnixc._getvalue()
    torkv__amrsj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vzthd__bso._getvalue(), is_error=torkv__amrsj)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    vzthd__bso = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        vzthd__bso.data, c.env_manager)
    pxbwl__pdai = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, vzthd__bso.null_bitmap).data
    ssfwu__pty = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(ssfwu__pty)
    bqa__fcscf = c.context.insert_const_string(c.builder.module, 'numpy')
    znctt__nbl = c.pyapi.import_module_noblock(bqa__fcscf)
    uqjyc__uqhr = c.pyapi.object_getattr_string(znctt__nbl, 'bool_')
    mask_arr = c.pyapi.call_method(znctt__nbl, 'empty', (ssfwu__pty,
        uqjyc__uqhr))
    rzjs__wdudz = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    htw__dkn = c.pyapi.object_getattr_string(rzjs__wdudz, 'data')
    jtn__rfi = c.builder.inttoptr(c.pyapi.long_as_longlong(htw__dkn), lir.
        IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as bop__scsad:
        i = bop__scsad.index
        eqhns__phpmo = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        mrc__pjmf = c.builder.load(cgutils.gep(c.builder, pxbwl__pdai,
            eqhns__phpmo))
        yjgai__sbk = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(mrc__pjmf, yjgai__sbk), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        tvumn__via = cgutils.gep(c.builder, jtn__rfi, i)
        c.builder.store(val, tvumn__via)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        vzthd__bso.null_bitmap)
    bqa__fcscf = c.context.insert_const_string(c.builder.module, 'pandas')
    eyoh__xrde = c.pyapi.import_module_noblock(bqa__fcscf)
    nhe__sxrek = c.pyapi.object_getattr_string(eyoh__xrde, 'arrays')
    domlj__twbdv = c.pyapi.call_method(nhe__sxrek, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(eyoh__xrde)
    c.pyapi.decref(ssfwu__pty)
    c.pyapi.decref(znctt__nbl)
    c.pyapi.decref(uqjyc__uqhr)
    c.pyapi.decref(rzjs__wdudz)
    c.pyapi.decref(htw__dkn)
    c.pyapi.decref(nhe__sxrek)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return domlj__twbdv


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        kyrvq__rey, owdow__gdpl = args
        vzthd__bso = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        vzthd__bso.data = kyrvq__rey
        vzthd__bso.null_bitmap = owdow__gdpl
        context.nrt.incref(builder, signature.args[0], kyrvq__rey)
        context.nrt.incref(builder, signature.args[1], owdow__gdpl)
        return vzthd__bso._getvalue()
    yec__sqi = IntegerArrayType(data.dtype)
    mjlze__hbacl = yec__sqi(data, null_bitmap)
    return mjlze__hbacl, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    ewa__xblxj = np.empty(n, pyval.dtype.type)
    lhnf__xsfeu = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        pepjk__ceyql = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(lhnf__xsfeu, i, int(not
            pepjk__ceyql))
        if not pepjk__ceyql:
            ewa__xblxj[i] = s
    qfae__mpcp = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), ewa__xblxj)
    cmh__xjzbv = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), lhnf__xsfeu)
    return lir.Constant.literal_struct([qfae__mpcp, cmh__xjzbv])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    zjg__igf = args[0]
    if equiv_set.has_shape(zjg__igf):
        return ArrayAnalysis.AnalyzeResult(shape=zjg__igf, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    zjg__igf = args[0]
    if equiv_set.has_shape(zjg__igf):
        return ArrayAnalysis.AnalyzeResult(shape=zjg__igf, pre=[])
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
    ewa__xblxj = np.empty(n, dtype)
    ktjxw__wzvt = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(ewa__xblxj, ktjxw__wzvt)


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
            jrn__nmto, xlts__jzg = array_getitem_bool_index(A, ind)
            return init_integer_array(jrn__nmto, xlts__jzg)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            jrn__nmto, xlts__jzg = array_getitem_int_index(A, ind)
            return init_integer_array(jrn__nmto, xlts__jzg)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            jrn__nmto, xlts__jzg = array_getitem_slice_index(A, ind)
            return init_integer_array(jrn__nmto, xlts__jzg)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    uvsy__mmcwx = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    huzo__dwn = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if huzo__dwn:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(uvsy__mmcwx)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or huzo__dwn):
        raise BodoError(uvsy__mmcwx)
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
            klgo__nqmhm = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                klgo__nqmhm[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    klgo__nqmhm[i] = np.nan
            return klgo__nqmhm
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
                goylk__ucgvp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                rqjr__mdj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                bnz__oopq = goylk__ucgvp & rqjr__mdj
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, bnz__oopq)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        gio__rqbhz = n + 7 >> 3
        klgo__nqmhm = np.empty(gio__rqbhz, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            goylk__ucgvp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            rqjr__mdj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            bnz__oopq = goylk__ucgvp & rqjr__mdj
            bodo.libs.int_arr_ext.set_bit_to_arr(klgo__nqmhm, i, bnz__oopq)
        return klgo__nqmhm
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
    for nzoq__cdiw in numba.np.ufunc_db.get_ufuncs():
        xxm__iqnl = create_op_overload(nzoq__cdiw, nzoq__cdiw.nin)
        overload(nzoq__cdiw, no_unliteral=True)(xxm__iqnl)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        xxm__iqnl = create_op_overload(op, 2)
        overload(op)(xxm__iqnl)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        xxm__iqnl = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(xxm__iqnl)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        xxm__iqnl = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(xxm__iqnl)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    xurzs__hhkxv = len(arrs.types)
    byz__ycl = 'def f(arrs):\n'
    domlj__twbdv = ', '.join('arrs[{}]._data'.format(i) for i in range(
        xurzs__hhkxv))
    byz__ycl += '  return ({}{})\n'.format(domlj__twbdv, ',' if 
        xurzs__hhkxv == 1 else '')
    hkx__zjfxh = {}
    exec(byz__ycl, {}, hkx__zjfxh)
    impl = hkx__zjfxh['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    xurzs__hhkxv = len(arrs.types)
    xow__lzws = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        xurzs__hhkxv))
    byz__ycl = 'def f(arrs):\n'
    byz__ycl += '  n = {}\n'.format(xow__lzws)
    byz__ycl += '  n_bytes = (n + 7) >> 3\n'
    byz__ycl += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    byz__ycl += '  curr_bit = 0\n'
    for i in range(xurzs__hhkxv):
        byz__ycl += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        byz__ycl += '  for j in range(len(arrs[{}])):\n'.format(i)
        byz__ycl += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        byz__ycl += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        byz__ycl += '    curr_bit += 1\n'
    byz__ycl += '  return new_mask\n'
    hkx__zjfxh = {}
    exec(byz__ycl, {'np': np, 'bodo': bodo}, hkx__zjfxh)
    impl = hkx__zjfxh['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    yqfw__jos = dict(skipna=skipna, min_count=min_count)
    bbwbx__xex = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', yqfw__jos, bbwbx__xex)

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
        yjgai__sbk = []
        wqim__jfdaq = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not wqim__jfdaq:
                    data.append(dtype(1))
                    yjgai__sbk.append(False)
                    wqim__jfdaq = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                yjgai__sbk.append(True)
        jrn__nmto = np.array(data)
        n = len(jrn__nmto)
        gio__rqbhz = n + 7 >> 3
        xlts__jzg = np.empty(gio__rqbhz, np.uint8)
        for aanrn__oylxl in range(n):
            set_bit_to_arr(xlts__jzg, aanrn__oylxl, yjgai__sbk[aanrn__oylxl])
        return init_integer_array(jrn__nmto, xlts__jzg)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    cgek__cyxpj = numba.core.registry.cpu_target.typing_context
    toj__cfv = cgek__cyxpj.resolve_function_type(op, (types.Array(A.dtype, 
        1, 'C'),), {}).return_type
    toj__cfv = to_nullable_type(toj__cfv)

    def impl(A):
        n = len(A)
        axxnj__dwtku = bodo.utils.utils.alloc_type(n, toj__cfv, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(axxnj__dwtku, i)
                continue
            axxnj__dwtku[i] = op(A[i])
        return axxnj__dwtku
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    ubjos__ecgr = isinstance(lhs, (types.Number, types.Boolean))
    oedc__hrzj = isinstance(rhs, (types.Number, types.Boolean))
    ublng__qgrzf = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    jek__bmegs = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    cgek__cyxpj = numba.core.registry.cpu_target.typing_context
    toj__cfv = cgek__cyxpj.resolve_function_type(op, (ublng__qgrzf,
        jek__bmegs), {}).return_type
    toj__cfv = to_nullable_type(toj__cfv)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    kxgl__qbl = 'lhs' if ubjos__ecgr else 'lhs[i]'
    usunk__ufhci = 'rhs' if oedc__hrzj else 'rhs[i]'
    xkisc__htxsy = ('False' if ubjos__ecgr else
        'bodo.libs.array_kernels.isna(lhs, i)')
    onui__sra = ('False' if oedc__hrzj else
        'bodo.libs.array_kernels.isna(rhs, i)')
    byz__ycl = 'def impl(lhs, rhs):\n'
    byz__ycl += '  n = len({})\n'.format('lhs' if not ubjos__ecgr else 'rhs')
    if inplace:
        byz__ycl += '  out_arr = {}\n'.format('lhs' if not ubjos__ecgr else
            'rhs')
    else:
        byz__ycl += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    byz__ycl += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    byz__ycl += '    if ({}\n'.format(xkisc__htxsy)
    byz__ycl += '        or {}):\n'.format(onui__sra)
    byz__ycl += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    byz__ycl += '      continue\n'
    byz__ycl += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(kxgl__qbl, usunk__ufhci))
    byz__ycl += '  return out_arr\n'
    hkx__zjfxh = {}
    exec(byz__ycl, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        toj__cfv, 'op': op}, hkx__zjfxh)
    impl = hkx__zjfxh['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        ubjos__ecgr = lhs in [pd_timedelta_type]
        oedc__hrzj = rhs in [pd_timedelta_type]
        if ubjos__ecgr:

            def impl(lhs, rhs):
                n = len(rhs)
                axxnj__dwtku = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(axxnj__dwtku, i)
                        continue
                    axxnj__dwtku[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs, rhs[i]))
                return axxnj__dwtku
            return impl
        elif oedc__hrzj:

            def impl(lhs, rhs):
                n = len(lhs)
                axxnj__dwtku = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(axxnj__dwtku, i)
                        continue
                    axxnj__dwtku[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs[i], rhs))
                return axxnj__dwtku
            return impl
    return impl
