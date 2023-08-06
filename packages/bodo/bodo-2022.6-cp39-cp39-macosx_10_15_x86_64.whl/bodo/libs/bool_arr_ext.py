"""Nullable boolean array that stores data in Numpy format (1 byte per value)
but nulls are stored in bit arrays (1 bit per value) similar to Arrow's nulls.
Pandas converts boolean array to object when NAs are introduced.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import NativeValue, box, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.libs.str_arr_ext import string_array_type
from bodo.utils.typing import is_list_like_index_type
ll.add_symbol('is_bool_array', hstr_ext.is_bool_array)
ll.add_symbol('is_pd_boolean_array', hstr_ext.is_pd_boolean_array)
ll.add_symbol('unbox_bool_array_obj', hstr_ext.unbox_bool_array_obj)
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, is_iterable_type, is_overload_false, is_overload_true, parse_dtype, raise_bodo_error


class BooleanArrayType(types.ArrayCompatible):

    def __init__(self):
        super(BooleanArrayType, self).__init__(name='BooleanArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.bool_

    def copy(self):
        return BooleanArrayType()


boolean_array = BooleanArrayType()


@typeof_impl.register(pd.arrays.BooleanArray)
def typeof_boolean_array(val, c):
    return boolean_array


data_type = types.Array(types.bool_, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(BooleanArrayType)
class BooleanArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fnxdz__kaemt = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, fnxdz__kaemt)


make_attribute_wrapper(BooleanArrayType, 'data', '_data')
make_attribute_wrapper(BooleanArrayType, 'null_bitmap', '_null_bitmap')


class BooleanDtype(types.Number):

    def __init__(self):
        self.dtype = types.bool_
        super(BooleanDtype, self).__init__('BooleanDtype')


boolean_dtype = BooleanDtype()
register_model(BooleanDtype)(models.OpaqueModel)


@box(BooleanDtype)
def box_boolean_dtype(typ, val, c):
    jsji__ueqb = c.context.insert_const_string(c.builder.module, 'pandas')
    iiym__led = c.pyapi.import_module_noblock(jsji__ueqb)
    yqpki__rbcf = c.pyapi.call_method(iiym__led, 'BooleanDtype', ())
    c.pyapi.decref(iiym__led)
    return yqpki__rbcf


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    ifeeu__zym = n + 7 >> 3
    return np.full(ifeeu__zym, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    nqve__yhaib = c.context.typing_context.resolve_value_type(func)
    pxrlq__tkvcc = nqve__yhaib.get_call_type(c.context.typing_context,
        arg_typs, {})
    yln__ydqaz = c.context.get_function(nqve__yhaib, pxrlq__tkvcc)
    nlnh__zfv = c.context.call_conv.get_function_type(pxrlq__tkvcc.
        return_type, pxrlq__tkvcc.args)
    bwlv__acpz = c.builder.module
    rxrfj__vjv = lir.Function(bwlv__acpz, nlnh__zfv, name=bwlv__acpz.
        get_unique_name('.func_conv'))
    rxrfj__vjv.linkage = 'internal'
    pjun__rvetu = lir.IRBuilder(rxrfj__vjv.append_basic_block())
    ffoi__tlyf = c.context.call_conv.decode_arguments(pjun__rvetu,
        pxrlq__tkvcc.args, rxrfj__vjv)
    eyi__jxc = yln__ydqaz(pjun__rvetu, ffoi__tlyf)
    c.context.call_conv.return_value(pjun__rvetu, eyi__jxc)
    wqe__ummz, wzvo__ifbq = c.context.call_conv.call_function(c.builder,
        rxrfj__vjv, pxrlq__tkvcc.return_type, pxrlq__tkvcc.args, args)
    return wzvo__ifbq


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    ehhrn__xpor = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(ehhrn__xpor)
    c.pyapi.decref(ehhrn__xpor)
    nlnh__zfv = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    bnjq__nkbb = cgutils.get_or_insert_function(c.builder.module, nlnh__zfv,
        name='is_bool_array')
    nlnh__zfv = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    rxrfj__vjv = cgutils.get_or_insert_function(c.builder.module, nlnh__zfv,
        name='is_pd_boolean_array')
    dtrli__nytr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hofe__hqrs = c.builder.call(rxrfj__vjv, [obj])
    vbv__xrty = c.builder.icmp_unsigned('!=', hofe__hqrs, hofe__hqrs.type(0))
    with c.builder.if_else(vbv__xrty) as (awcdv__idq, hami__jbv):
        with awcdv__idq:
            swx__ujqw = c.pyapi.object_getattr_string(obj, '_data')
            dtrli__nytr.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), swx__ujqw).value
            nkbl__ijw = c.pyapi.object_getattr_string(obj, '_mask')
            kob__qrooc = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), nkbl__ijw).value
            ifeeu__zym = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            regw__iva = c.context.make_array(types.Array(types.bool_, 1, 'C'))(
                c.context, c.builder, kob__qrooc)
            ojvt__tarr = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [ifeeu__zym])
            nlnh__zfv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            rxrfj__vjv = cgutils.get_or_insert_function(c.builder.module,
                nlnh__zfv, name='mask_arr_to_bitmap')
            c.builder.call(rxrfj__vjv, [ojvt__tarr.data, regw__iva.data, n])
            dtrli__nytr.null_bitmap = ojvt__tarr._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), kob__qrooc)
            c.pyapi.decref(swx__ujqw)
            c.pyapi.decref(nkbl__ijw)
        with hami__jbv:
            cog__djvkf = c.builder.call(bnjq__nkbb, [obj])
            usy__jpxwz = c.builder.icmp_unsigned('!=', cog__djvkf,
                cog__djvkf.type(0))
            with c.builder.if_else(usy__jpxwz) as (bjgba__hko, vdal__ogpmb):
                with bjgba__hko:
                    dtrli__nytr.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    dtrli__nytr.null_bitmap = call_func_in_unbox(
                        gen_full_bitmap, (n,), (types.int64,), c)
                with vdal__ogpmb:
                    dtrli__nytr.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    ifeeu__zym = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    dtrli__nytr.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [ifeeu__zym])._getvalue()
                    iwa__fugqu = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, dtrli__nytr.data
                        ).data
                    tkr__neqc = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, dtrli__nytr.
                        null_bitmap).data
                    nlnh__zfv = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    rxrfj__vjv = cgutils.get_or_insert_function(c.builder.
                        module, nlnh__zfv, name='unbox_bool_array_obj')
                    c.builder.call(rxrfj__vjv, [obj, iwa__fugqu, tkr__neqc, n])
    return NativeValue(dtrli__nytr._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    dtrli__nytr = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        dtrli__nytr.data, c.env_manager)
    jpdj__rdyee = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, dtrli__nytr.null_bitmap).data
    ehhrn__xpor = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(ehhrn__xpor)
    jsji__ueqb = c.context.insert_const_string(c.builder.module, 'numpy')
    dtc__avx = c.pyapi.import_module_noblock(jsji__ueqb)
    ulq__bzbh = c.pyapi.object_getattr_string(dtc__avx, 'bool_')
    kob__qrooc = c.pyapi.call_method(dtc__avx, 'empty', (ehhrn__xpor,
        ulq__bzbh))
    zqqxf__bzf = c.pyapi.object_getattr_string(kob__qrooc, 'ctypes')
    sat__jihl = c.pyapi.object_getattr_string(zqqxf__bzf, 'data')
    vam__zxj = c.builder.inttoptr(c.pyapi.long_as_longlong(sat__jihl), lir.
        IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as xjx__kgt:
        dizl__mvo = xjx__kgt.index
        meaqn__qpj = c.builder.lshr(dizl__mvo, lir.Constant(lir.IntType(64), 3)
            )
        gic__bjxad = c.builder.load(cgutils.gep(c.builder, jpdj__rdyee,
            meaqn__qpj))
        fosn__vwm = c.builder.trunc(c.builder.and_(dizl__mvo, lir.Constant(
            lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(gic__bjxad, fosn__vwm), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        kof__xtnhl = cgutils.gep(c.builder, vam__zxj, dizl__mvo)
        c.builder.store(val, kof__xtnhl)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        dtrli__nytr.null_bitmap)
    jsji__ueqb = c.context.insert_const_string(c.builder.module, 'pandas')
    iiym__led = c.pyapi.import_module_noblock(jsji__ueqb)
    gafit__pfouz = c.pyapi.object_getattr_string(iiym__led, 'arrays')
    yqpki__rbcf = c.pyapi.call_method(gafit__pfouz, 'BooleanArray', (data,
        kob__qrooc))
    c.pyapi.decref(iiym__led)
    c.pyapi.decref(ehhrn__xpor)
    c.pyapi.decref(dtc__avx)
    c.pyapi.decref(ulq__bzbh)
    c.pyapi.decref(zqqxf__bzf)
    c.pyapi.decref(sat__jihl)
    c.pyapi.decref(gafit__pfouz)
    c.pyapi.decref(data)
    c.pyapi.decref(kob__qrooc)
    return yqpki__rbcf


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    nglk__yrlp = np.empty(n, np.bool_)
    wqg__lfb = np.empty(n + 7 >> 3, np.uint8)
    for dizl__mvo, s in enumerate(pyval):
        sypm__huex = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(wqg__lfb, dizl__mvo, int(not
            sypm__huex))
        if not sypm__huex:
            nglk__yrlp[dizl__mvo] = s
    tom__dus = context.get_constant_generic(builder, data_type, nglk__yrlp)
    fjprz__pix = context.get_constant_generic(builder, nulls_type, wqg__lfb)
    return lir.Constant.literal_struct([tom__dus, fjprz__pix])


def lower_init_bool_array(context, builder, signature, args):
    eaqtt__zevcy, rdx__kliy = args
    dtrli__nytr = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    dtrli__nytr.data = eaqtt__zevcy
    dtrli__nytr.null_bitmap = rdx__kliy
    context.nrt.incref(builder, signature.args[0], eaqtt__zevcy)
    context.nrt.incref(builder, signature.args[1], rdx__kliy)
    return dtrli__nytr._getvalue()


@intrinsic
def init_bool_array(typingctx, data, null_bitmap=None):
    assert data == types.Array(types.bool_, 1, 'C')
    assert null_bitmap == types.Array(types.uint8, 1, 'C')
    sig = boolean_array(data, null_bitmap)
    return sig, lower_init_bool_array


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_bool_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    toso__ylij = args[0]
    if equiv_set.has_shape(toso__ylij):
        return ArrayAnalysis.AnalyzeResult(shape=toso__ylij, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    toso__ylij = args[0]
    if equiv_set.has_shape(toso__ylij):
        return ArrayAnalysis.AnalyzeResult(shape=toso__ylij, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_init_bool_array = (
    init_bool_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_bool_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_bool_array',
    'bodo.libs.bool_arr_ext'] = alias_ext_init_bool_array
numba.core.ir_utils.alias_func_extensions['get_bool_arr_data',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_bool_arr_bitmap',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_bool_array(n):
    nglk__yrlp = np.empty(n, dtype=np.bool_)
    gdbgh__pdkz = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(nglk__yrlp, gdbgh__pdkz)


def alloc_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_alloc_bool_array = (
    alloc_bool_array_equiv)


@overload(operator.getitem, no_unliteral=True)
def bool_arr_getitem(A, ind):
    if A != boolean_array:
        return
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            blf__ezcf, edyv__sepht = array_getitem_bool_index(A, ind)
            return init_bool_array(blf__ezcf, edyv__sepht)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            blf__ezcf, edyv__sepht = array_getitem_int_index(A, ind)
            return init_bool_array(blf__ezcf, edyv__sepht)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            blf__ezcf, edyv__sepht = array_getitem_slice_index(A, ind)
            return init_bool_array(blf__ezcf, edyv__sepht)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    oxwgj__joz = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(oxwgj__joz)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(oxwgj__joz)
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
        f'setitem for BooleanArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_bool_arr_len(A):
    if A == boolean_array:
        return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'size')
def overload_bool_arr_size(A):
    return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'shape')
def overload_bool_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(BooleanArrayType, 'dtype')
def overload_bool_arr_dtype(A):
    return lambda A: pd.BooleanDtype()


@overload_attribute(BooleanArrayType, 'ndim')
def overload_bool_arr_ndim(A):
    return lambda A: 1


@overload_attribute(BooleanArrayType, 'nbytes')
def bool_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(BooleanArrayType, 'copy', no_unliteral=True)
def overload_bool_arr_copy(A):
    return lambda A: bodo.libs.bool_arr_ext.init_bool_array(bodo.libs.
        bool_arr_ext.get_bool_arr_data(A).copy(), bodo.libs.bool_arr_ext.
        get_bool_arr_bitmap(A).copy())


@overload_method(BooleanArrayType, 'sum', no_unliteral=True, inline='always')
def overload_bool_sum(A):

    def impl(A):
        numba.parfors.parfor.init_prange()
        s = 0
        for dizl__mvo in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, dizl__mvo):
                val = A[dizl__mvo]
            s += val
        return s
    return impl


@overload_method(BooleanArrayType, 'astype', no_unliteral=True)
def overload_bool_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "BooleanArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if dtype == types.bool_:
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
    nb_dtype = parse_dtype(dtype, 'BooleanArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
            n = len(data)
            ztb__tln = np.empty(n, nb_dtype)
            for dizl__mvo in numba.parfors.parfor.internal_prange(n):
                ztb__tln[dizl__mvo] = data[dizl__mvo]
                if bodo.libs.array_kernels.isna(A, dizl__mvo):
                    ztb__tln[dizl__mvo] = np.nan
            return ztb__tln
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        ztb__tln = np.empty(n, dtype=np.bool_)
        for dizl__mvo in numba.parfors.parfor.internal_prange(n):
            ztb__tln[dizl__mvo] = data[dizl__mvo]
            if bodo.libs.array_kernels.isna(A, dizl__mvo):
                ztb__tln[dizl__mvo] = value
        return ztb__tln
    return impl


@overload(str, no_unliteral=True)
def overload_str_bool(val):
    if val == types.bool_:

        def impl(val):
            if val:
                return 'True'
            return 'False'
        return impl


ufunc_aliases = {'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    pbhd__yvu = op.__name__
    pbhd__yvu = ufunc_aliases.get(pbhd__yvu, pbhd__yvu)
    if n_inputs == 1:

        def overload_bool_arr_op_nin_1(A):
            if isinstance(A, BooleanArrayType):
                return bodo.libs.int_arr_ext.get_nullable_array_unary_impl(op,
                    A)
        return overload_bool_arr_op_nin_1
    elif n_inputs == 2:

        def overload_bool_arr_op_nin_2(lhs, rhs):
            if lhs == boolean_array or rhs == boolean_array:
                return bodo.libs.int_arr_ext.get_nullable_array_binary_impl(op,
                    lhs, rhs)
        return overload_bool_arr_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for dytls__gejfb in numba.np.ufunc_db.get_ufuncs():
        ynu__nulba = create_op_overload(dytls__gejfb, dytls__gejfb.nin)
        overload(dytls__gejfb, no_unliteral=True)(ynu__nulba)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        ynu__nulba = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(ynu__nulba)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        ynu__nulba = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(ynu__nulba)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        ynu__nulba = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(ynu__nulba)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        fosn__vwm = []
        sqhy__simtm = False
        sizf__qfi = False
        wbor__oqa = False
        for dizl__mvo in range(len(A)):
            if bodo.libs.array_kernels.isna(A, dizl__mvo):
                if not sqhy__simtm:
                    data.append(False)
                    fosn__vwm.append(False)
                    sqhy__simtm = True
                continue
            val = A[dizl__mvo]
            if val and not sizf__qfi:
                data.append(True)
                fosn__vwm.append(True)
                sizf__qfi = True
            if not val and not wbor__oqa:
                data.append(False)
                fosn__vwm.append(True)
                wbor__oqa = True
            if sqhy__simtm and sizf__qfi and wbor__oqa:
                break
        blf__ezcf = np.array(data)
        n = len(blf__ezcf)
        ifeeu__zym = 1
        edyv__sepht = np.empty(ifeeu__zym, np.uint8)
        for xjsnk__ftg in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(edyv__sepht, xjsnk__ftg,
                fosn__vwm[xjsnk__ftg])
        return init_bool_array(blf__ezcf, edyv__sepht)
    return impl_bool_arr


@overload(operator.getitem, no_unliteral=True)
def bool_arr_ind_getitem(A, ind):
    if ind == boolean_array and (isinstance(A, (types.Array, bodo.libs.
        int_arr_ext.IntegerArrayType)) or isinstance(A, bodo.libs.
        struct_arr_ext.StructArrayType) or isinstance(A, bodo.libs.
        array_item_arr_ext.ArrayItemArrayType) or isinstance(A, bodo.libs.
        map_arr_ext.MapArrayType) or A in (string_array_type, bodo.hiframes
        .split_impl.string_array_split_view_type, boolean_array)):
        return lambda A, ind: A[ind._data]


@lower_cast(types.Array(types.bool_, 1, 'C'), boolean_array)
def cast_np_bool_arr_to_bool_arr(context, builder, fromty, toty, val):
    func = lambda A: bodo.libs.bool_arr_ext.init_bool_array(A, np.full(len(
        A) + 7 >> 3, 255, np.uint8))
    yqpki__rbcf = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, yqpki__rbcf)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    plt__qzdkt = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        xzkwy__sfs = bodo.utils.utils.is_array_typ(val1, False)
        uict__crzgp = bodo.utils.utils.is_array_typ(val2, False)
        apd__atwjy = 'val1' if xzkwy__sfs else 'val2'
        aga__vlj = 'def impl(val1, val2):\n'
        aga__vlj += f'  n = len({apd__atwjy})\n'
        aga__vlj += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        aga__vlj += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if xzkwy__sfs:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            nqs__dye = 'val1[i]'
        else:
            null1 = 'False\n'
            nqs__dye = 'val1'
        if uict__crzgp:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            wvvr__jzmg = 'val2[i]'
        else:
            null2 = 'False\n'
            wvvr__jzmg = 'val2'
        if plt__qzdkt:
            aga__vlj += f"""    result, isna_val = compute_or_body({null1}, {null2}, {nqs__dye}, {wvvr__jzmg})
"""
        else:
            aga__vlj += f"""    result, isna_val = compute_and_body({null1}, {null2}, {nqs__dye}, {wvvr__jzmg})
"""
        aga__vlj += '    out_arr[i] = result\n'
        aga__vlj += '    if isna_val:\n'
        aga__vlj += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        aga__vlj += '      continue\n'
        aga__vlj += '  return out_arr\n'
        hubs__fnm = {}
        exec(aga__vlj, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, hubs__fnm)
        impl = hubs__fnm['impl']
        return impl
    return bool_array_impl


def compute_or_body(null1, null2, val1, val2):
    pass


@overload(compute_or_body)
def overload_compute_or_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == False
        elif null2:
            return val1, val1 == False
        else:
            return val1 | val2, False
    return impl


def compute_and_body(null1, null2, val1, val2):
    pass


@overload(compute_and_body)
def overload_compute_and_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == True
        elif null2:
            return val1, val1 == True
        else:
            return val1 & val2, False
    return impl


def create_boolean_array_logical_lower_impl(op):

    def logical_lower_impl(context, builder, sig, args):
        impl = create_nullable_logical_op_overload(op)(*sig.args)
        return context.compile_internal(builder, impl, sig, args)
    return logical_lower_impl


class BooleanArrayLogicalOperatorTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        if not is_valid_boolean_array_logical_op(args[0], args[1]):
            return
        mjiv__qgx = boolean_array
        return mjiv__qgx(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    kax__pfty = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return kax__pfty


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        upslt__cfhs = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(upslt__cfhs)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(upslt__cfhs)


_install_nullable_logical_lowering()
