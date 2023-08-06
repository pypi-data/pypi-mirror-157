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
        atgly__pwqcf = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, atgly__pwqcf)


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
    xxtjt__rdm = c.context.insert_const_string(c.builder.module, 'pandas')
    tjn__link = c.pyapi.import_module_noblock(xxtjt__rdm)
    goqr__armln = c.pyapi.call_method(tjn__link, 'BooleanDtype', ())
    c.pyapi.decref(tjn__link)
    return goqr__armln


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    txy__tuwyr = n + 7 >> 3
    return np.full(txy__tuwyr, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    nfta__dowpp = c.context.typing_context.resolve_value_type(func)
    zlepl__vygq = nfta__dowpp.get_call_type(c.context.typing_context,
        arg_typs, {})
    uakn__aomzb = c.context.get_function(nfta__dowpp, zlepl__vygq)
    zdl__udzw = c.context.call_conv.get_function_type(zlepl__vygq.
        return_type, zlepl__vygq.args)
    vcwr__qqv = c.builder.module
    bapv__tgt = lir.Function(vcwr__qqv, zdl__udzw, name=vcwr__qqv.
        get_unique_name('.func_conv'))
    bapv__tgt.linkage = 'internal'
    ajgja__ghdlg = lir.IRBuilder(bapv__tgt.append_basic_block())
    uzcr__pyshm = c.context.call_conv.decode_arguments(ajgja__ghdlg,
        zlepl__vygq.args, bapv__tgt)
    sarks__qqif = uakn__aomzb(ajgja__ghdlg, uzcr__pyshm)
    c.context.call_conv.return_value(ajgja__ghdlg, sarks__qqif)
    cgner__gxvhh, gcx__zrclj = c.context.call_conv.call_function(c.builder,
        bapv__tgt, zlepl__vygq.return_type, zlepl__vygq.args, args)
    return gcx__zrclj


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    swubj__eusl = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(swubj__eusl)
    c.pyapi.decref(swubj__eusl)
    zdl__udzw = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    tooy__atypp = cgutils.get_or_insert_function(c.builder.module,
        zdl__udzw, name='is_bool_array')
    zdl__udzw = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    bapv__tgt = cgutils.get_or_insert_function(c.builder.module, zdl__udzw,
        name='is_pd_boolean_array')
    ixkz__dvea = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tzmio__cbkd = c.builder.call(bapv__tgt, [obj])
    tywa__xjlza = c.builder.icmp_unsigned('!=', tzmio__cbkd, tzmio__cbkd.
        type(0))
    with c.builder.if_else(tywa__xjlza) as (onp__une, krm__wbgt):
        with onp__une:
            dqi__fhtk = c.pyapi.object_getattr_string(obj, '_data')
            ixkz__dvea.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), dqi__fhtk).value
            vor__dykk = c.pyapi.object_getattr_string(obj, '_mask')
            svd__ixh = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), vor__dykk).value
            txy__tuwyr = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            erag__jret = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, svd__ixh)
            gkt__mpwn = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [txy__tuwyr])
            zdl__udzw = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            bapv__tgt = cgutils.get_or_insert_function(c.builder.module,
                zdl__udzw, name='mask_arr_to_bitmap')
            c.builder.call(bapv__tgt, [gkt__mpwn.data, erag__jret.data, n])
            ixkz__dvea.null_bitmap = gkt__mpwn._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), svd__ixh)
            c.pyapi.decref(dqi__fhtk)
            c.pyapi.decref(vor__dykk)
        with krm__wbgt:
            wfe__wvd = c.builder.call(tooy__atypp, [obj])
            ipee__eubc = c.builder.icmp_unsigned('!=', wfe__wvd, wfe__wvd.
                type(0))
            with c.builder.if_else(ipee__eubc) as (rvtn__sdi, vjmd__dgd):
                with rvtn__sdi:
                    ixkz__dvea.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    ixkz__dvea.null_bitmap = call_func_in_unbox(gen_full_bitmap
                        , (n,), (types.int64,), c)
                with vjmd__dgd:
                    ixkz__dvea.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    txy__tuwyr = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    ixkz__dvea.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [txy__tuwyr])._getvalue()
                    jpz__vvac = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, ixkz__dvea.data
                        ).data
                    qmtup__rztli = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, ixkz__dvea.
                        null_bitmap).data
                    zdl__udzw = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    bapv__tgt = cgutils.get_or_insert_function(c.builder.
                        module, zdl__udzw, name='unbox_bool_array_obj')
                    c.builder.call(bapv__tgt, [obj, jpz__vvac, qmtup__rztli, n]
                        )
    return NativeValue(ixkz__dvea._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    ixkz__dvea = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        ixkz__dvea.data, c.env_manager)
    ffmx__pyfx = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, ixkz__dvea.null_bitmap).data
    swubj__eusl = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(swubj__eusl)
    xxtjt__rdm = c.context.insert_const_string(c.builder.module, 'numpy')
    aoavh__gymu = c.pyapi.import_module_noblock(xxtjt__rdm)
    ggx__bmmwa = c.pyapi.object_getattr_string(aoavh__gymu, 'bool_')
    svd__ixh = c.pyapi.call_method(aoavh__gymu, 'empty', (swubj__eusl,
        ggx__bmmwa))
    mhv__hcdua = c.pyapi.object_getattr_string(svd__ixh, 'ctypes')
    nlzlg__quy = c.pyapi.object_getattr_string(mhv__hcdua, 'data')
    jbz__igk = c.builder.inttoptr(c.pyapi.long_as_longlong(nlzlg__quy), lir
        .IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as kuzx__fck:
        aqzr__kjan = kuzx__fck.index
        szsv__nsen = c.builder.lshr(aqzr__kjan, lir.Constant(lir.IntType(64
            ), 3))
        xrsq__lma = c.builder.load(cgutils.gep(c.builder, ffmx__pyfx,
            szsv__nsen))
        iwpo__hxnc = c.builder.trunc(c.builder.and_(aqzr__kjan, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(xrsq__lma, iwpo__hxnc), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        yknd__peocf = cgutils.gep(c.builder, jbz__igk, aqzr__kjan)
        c.builder.store(val, yknd__peocf)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        ixkz__dvea.null_bitmap)
    xxtjt__rdm = c.context.insert_const_string(c.builder.module, 'pandas')
    tjn__link = c.pyapi.import_module_noblock(xxtjt__rdm)
    xavwk__nxp = c.pyapi.object_getattr_string(tjn__link, 'arrays')
    goqr__armln = c.pyapi.call_method(xavwk__nxp, 'BooleanArray', (data,
        svd__ixh))
    c.pyapi.decref(tjn__link)
    c.pyapi.decref(swubj__eusl)
    c.pyapi.decref(aoavh__gymu)
    c.pyapi.decref(ggx__bmmwa)
    c.pyapi.decref(mhv__hcdua)
    c.pyapi.decref(nlzlg__quy)
    c.pyapi.decref(xavwk__nxp)
    c.pyapi.decref(data)
    c.pyapi.decref(svd__ixh)
    return goqr__armln


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    qbo__wpihj = np.empty(n, np.bool_)
    cux__cqwe = np.empty(n + 7 >> 3, np.uint8)
    for aqzr__kjan, s in enumerate(pyval):
        rpwt__whp = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(cux__cqwe, aqzr__kjan, int(not
            rpwt__whp))
        if not rpwt__whp:
            qbo__wpihj[aqzr__kjan] = s
    pdx__xyhl = context.get_constant_generic(builder, data_type, qbo__wpihj)
    yfcol__wrq = context.get_constant_generic(builder, nulls_type, cux__cqwe)
    return lir.Constant.literal_struct([pdx__xyhl, yfcol__wrq])


def lower_init_bool_array(context, builder, signature, args):
    kyt__nki, hmbhd__kvzqg = args
    ixkz__dvea = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    ixkz__dvea.data = kyt__nki
    ixkz__dvea.null_bitmap = hmbhd__kvzqg
    context.nrt.incref(builder, signature.args[0], kyt__nki)
    context.nrt.incref(builder, signature.args[1], hmbhd__kvzqg)
    return ixkz__dvea._getvalue()


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
    gclgs__oxn = args[0]
    if equiv_set.has_shape(gclgs__oxn):
        return ArrayAnalysis.AnalyzeResult(shape=gclgs__oxn, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    gclgs__oxn = args[0]
    if equiv_set.has_shape(gclgs__oxn):
        return ArrayAnalysis.AnalyzeResult(shape=gclgs__oxn, pre=[])
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
    qbo__wpihj = np.empty(n, dtype=np.bool_)
    pwkac__nlkh = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(qbo__wpihj, pwkac__nlkh)


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
            ofgm__eoro, liqkb__odgds = array_getitem_bool_index(A, ind)
            return init_bool_array(ofgm__eoro, liqkb__odgds)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            ofgm__eoro, liqkb__odgds = array_getitem_int_index(A, ind)
            return init_bool_array(ofgm__eoro, liqkb__odgds)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            ofgm__eoro, liqkb__odgds = array_getitem_slice_index(A, ind)
            return init_bool_array(ofgm__eoro, liqkb__odgds)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    vsei__xzljk = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(vsei__xzljk)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(vsei__xzljk)
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
        for aqzr__kjan in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, aqzr__kjan):
                val = A[aqzr__kjan]
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
            xtvz__fcr = np.empty(n, nb_dtype)
            for aqzr__kjan in numba.parfors.parfor.internal_prange(n):
                xtvz__fcr[aqzr__kjan] = data[aqzr__kjan]
                if bodo.libs.array_kernels.isna(A, aqzr__kjan):
                    xtvz__fcr[aqzr__kjan] = np.nan
            return xtvz__fcr
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        xtvz__fcr = np.empty(n, dtype=np.bool_)
        for aqzr__kjan in numba.parfors.parfor.internal_prange(n):
            xtvz__fcr[aqzr__kjan] = data[aqzr__kjan]
            if bodo.libs.array_kernels.isna(A, aqzr__kjan):
                xtvz__fcr[aqzr__kjan] = value
        return xtvz__fcr
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
    vft__iwk = op.__name__
    vft__iwk = ufunc_aliases.get(vft__iwk, vft__iwk)
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
    for ncw__liic in numba.np.ufunc_db.get_ufuncs():
        qqoej__pffp = create_op_overload(ncw__liic, ncw__liic.nin)
        overload(ncw__liic, no_unliteral=True)(qqoej__pffp)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        qqoej__pffp = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(qqoej__pffp)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        qqoej__pffp = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(qqoej__pffp)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        qqoej__pffp = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(qqoej__pffp)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        iwpo__hxnc = []
        lmvr__pef = False
        zglqe__hvn = False
        uiu__pfv = False
        for aqzr__kjan in range(len(A)):
            if bodo.libs.array_kernels.isna(A, aqzr__kjan):
                if not lmvr__pef:
                    data.append(False)
                    iwpo__hxnc.append(False)
                    lmvr__pef = True
                continue
            val = A[aqzr__kjan]
            if val and not zglqe__hvn:
                data.append(True)
                iwpo__hxnc.append(True)
                zglqe__hvn = True
            if not val and not uiu__pfv:
                data.append(False)
                iwpo__hxnc.append(True)
                uiu__pfv = True
            if lmvr__pef and zglqe__hvn and uiu__pfv:
                break
        ofgm__eoro = np.array(data)
        n = len(ofgm__eoro)
        txy__tuwyr = 1
        liqkb__odgds = np.empty(txy__tuwyr, np.uint8)
        for qxc__eux in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(liqkb__odgds, qxc__eux,
                iwpo__hxnc[qxc__eux])
        return init_bool_array(ofgm__eoro, liqkb__odgds)
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
    goqr__armln = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, goqr__armln)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    kwfln__vgwr = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        mpnc__ksdx = bodo.utils.utils.is_array_typ(val1, False)
        xwafh__zbslm = bodo.utils.utils.is_array_typ(val2, False)
        xgvp__uodlv = 'val1' if mpnc__ksdx else 'val2'
        upjfi__txirc = 'def impl(val1, val2):\n'
        upjfi__txirc += f'  n = len({xgvp__uodlv})\n'
        upjfi__txirc += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        upjfi__txirc += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if mpnc__ksdx:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            wwga__taqg = 'val1[i]'
        else:
            null1 = 'False\n'
            wwga__taqg = 'val1'
        if xwafh__zbslm:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            qyo__vgeuo = 'val2[i]'
        else:
            null2 = 'False\n'
            qyo__vgeuo = 'val2'
        if kwfln__vgwr:
            upjfi__txirc += f"""    result, isna_val = compute_or_body({null1}, {null2}, {wwga__taqg}, {qyo__vgeuo})
"""
        else:
            upjfi__txirc += f"""    result, isna_val = compute_and_body({null1}, {null2}, {wwga__taqg}, {qyo__vgeuo})
"""
        upjfi__txirc += '    out_arr[i] = result\n'
        upjfi__txirc += '    if isna_val:\n'
        upjfi__txirc += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        upjfi__txirc += '      continue\n'
        upjfi__txirc += '  return out_arr\n'
        fkgsa__cal = {}
        exec(upjfi__txirc, {'bodo': bodo, 'numba': numba,
            'compute_and_body': compute_and_body, 'compute_or_body':
            compute_or_body}, fkgsa__cal)
        impl = fkgsa__cal['impl']
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
        vgyl__extc = boolean_array
        return vgyl__extc(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    yjm__kne = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array) and (
        bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype == types.
        bool_ or typ1 == types.bool_) and (bodo.utils.utils.is_array_typ(
        typ2, False) and typ2.dtype == types.bool_ or typ2 == types.bool_)
    return yjm__kne


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        gkpl__dmy = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(gkpl__dmy)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(gkpl__dmy)


_install_nullable_logical_lowering()
