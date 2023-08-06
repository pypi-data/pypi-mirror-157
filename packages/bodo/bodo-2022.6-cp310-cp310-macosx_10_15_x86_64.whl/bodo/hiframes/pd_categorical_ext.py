import enum
import operator
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.utils.typing import NOT_CONSTANT, BodoError, MetaType, check_unsupported_args, dtype_to_array_type, get_literal_value, get_overload_const, get_overload_const_bool, is_common_scalar_dtype, is_iterable_type, is_list_like_index_type, is_literal_type, is_overload_constant_bool, is_overload_none, is_overload_true, is_scalar_type, raise_bodo_error


class PDCategoricalDtype(types.Opaque):

    def __init__(self, categories, elem_type, ordered, data=None, int_type=None
        ):
        self.categories = categories
        self.elem_type = elem_type
        self.ordered = ordered
        self.data = _get_cat_index_type(elem_type) if data is None else data
        self.int_type = int_type
        tgbe__kzspt = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=tgbe__kzspt)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    iudgn__dsis = tuple(val.categories.values)
    elem_type = None if len(iudgn__dsis) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(iudgn__dsis, elem_type, val.ordered, bodo.
        typeof(val.categories), int_type)


def _get_cat_index_type(elem_type):
    elem_type = bodo.string_type if elem_type is None else elem_type
    return bodo.utils.typing.get_index_type_from_dtype(elem_type)


@lower_constant(PDCategoricalDtype)
def lower_constant_categorical_type(context, builder, typ, pyval):
    categories = context.get_constant_generic(builder, bodo.typeof(pyval.
        categories), pyval.categories)
    ordered = context.get_constant(types.bool_, pyval.ordered)
    return lir.Constant.literal_struct([categories, ordered])


@register_model(PDCategoricalDtype)
class PDCategoricalDtypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hbaot__hcn = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, hbaot__hcn)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    zwt__ajamq = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    pawi__ynce = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, ncez__hclcj, ncez__hclcj = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    ktrak__xkn = PDCategoricalDtype(pawi__ynce, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, zwt__ajamq)
    return ktrak__xkn(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pwub__mgqbe = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, pwub__mgqbe).value
    c.pyapi.decref(pwub__mgqbe)
    iqmy__zauef = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, iqmy__zauef).value
    c.pyapi.decref(iqmy__zauef)
    hsif__doy = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=hsif__doy)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    pwub__mgqbe = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    ycimw__ncqd = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    nke__hdlx = c.context.insert_const_string(c.builder.module, 'pandas')
    uodb__agpfr = c.pyapi.import_module_noblock(nke__hdlx)
    tes__cnku = c.pyapi.call_method(uodb__agpfr, 'CategoricalDtype', (
        ycimw__ncqd, pwub__mgqbe))
    c.pyapi.decref(pwub__mgqbe)
    c.pyapi.decref(ycimw__ncqd)
    c.pyapi.decref(uodb__agpfr)
    c.context.nrt.decref(c.builder, typ, val)
    return tes__cnku


@overload_attribute(PDCategoricalDtype, 'nbytes')
def pd_categorical_nbytes_overload(A):
    return lambda A: A.categories.nbytes + bodo.io.np_io.get_dtype_size(types
        .bool_)


class CategoricalArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(CategoricalArrayType, self).__init__(name=
            f'CategoricalArrayType({dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return CategoricalArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.Categorical)
def _typeof_pd_cat(val, c):
    return CategoricalArrayType(bodo.typeof(val.dtype))


@register_model(CategoricalArrayType)
class CategoricalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        lzc__uhdst = get_categories_int_type(fe_type.dtype)
        hbaot__hcn = [('dtype', fe_type.dtype), ('codes', types.Array(
            lzc__uhdst, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, hbaot__hcn)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    eyp__gyr = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), eyp__gyr).value
    c.pyapi.decref(eyp__gyr)
    tes__cnku = c.pyapi.object_getattr_string(val, 'dtype')
    wde__pran = c.pyapi.to_native_value(typ.dtype, tes__cnku).value
    c.pyapi.decref(tes__cnku)
    aamsj__ppmcn = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    aamsj__ppmcn.codes = codes
    aamsj__ppmcn.dtype = wde__pran
    return NativeValue(aamsj__ppmcn._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    wcztj__lfkz = get_categories_int_type(typ.dtype)
    hjmn__spp = context.get_constant_generic(builder, types.Array(
        wcztj__lfkz, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, hjmn__spp])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    rjxtw__aauw = len(cat_dtype.categories)
    if rjxtw__aauw < np.iinfo(np.int8).max:
        dtype = types.int8
    elif rjxtw__aauw < np.iinfo(np.int16).max:
        dtype = types.int16
    elif rjxtw__aauw < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    nke__hdlx = c.context.insert_const_string(c.builder.module, 'pandas')
    uodb__agpfr = c.pyapi.import_module_noblock(nke__hdlx)
    lzc__uhdst = get_categories_int_type(dtype)
    gruzh__rset = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    lxplu__iwwsr = types.Array(lzc__uhdst, 1, 'C')
    c.context.nrt.incref(c.builder, lxplu__iwwsr, gruzh__rset.codes)
    eyp__gyr = c.pyapi.from_native_value(lxplu__iwwsr, gruzh__rset.codes, c
        .env_manager)
    c.context.nrt.incref(c.builder, dtype, gruzh__rset.dtype)
    tes__cnku = c.pyapi.from_native_value(dtype, gruzh__rset.dtype, c.
        env_manager)
    dbn__zhglc = c.pyapi.borrow_none()
    wpyby__ree = c.pyapi.object_getattr_string(uodb__agpfr, 'Categorical')
    ptd__chc = c.pyapi.call_method(wpyby__ree, 'from_codes', (eyp__gyr,
        dbn__zhglc, dbn__zhglc, tes__cnku))
    c.pyapi.decref(wpyby__ree)
    c.pyapi.decref(eyp__gyr)
    c.pyapi.decref(tes__cnku)
    c.pyapi.decref(uodb__agpfr)
    c.context.nrt.decref(c.builder, typ, val)
    return ptd__chc


def _to_readonly(t):
    from bodo.hiframes.pd_index_ext import DatetimeIndexType, NumericIndexType, TimedeltaIndexType
    if isinstance(t, CategoricalArrayType):
        return CategoricalArrayType(_to_readonly(t.dtype))
    if isinstance(t, PDCategoricalDtype):
        return PDCategoricalDtype(t.categories, t.elem_type, t.ordered,
            _to_readonly(t.data), t.int_type)
    if isinstance(t, types.Array):
        return types.Array(t.dtype, t.ndim, 'C', True)
    if isinstance(t, NumericIndexType):
        return NumericIndexType(t.dtype, t.name_typ, _to_readonly(t.data))
    if isinstance(t, (DatetimeIndexType, TimedeltaIndexType)):
        return t.__class__(t.name_typ, _to_readonly(t.data))
    return t


@lower_cast(CategoricalArrayType, CategoricalArrayType)
def cast_cat_arr(context, builder, fromty, toty, val):
    if _to_readonly(toty) == fromty:
        return val
    raise BodoError(f'Cannot cast from {fromty} to {toty}')


def create_cmp_op_overload(op):

    def overload_cat_arr_cmp(A, other):
        if not isinstance(A, CategoricalArrayType):
            return
        if A.dtype.categories and is_literal_type(other) and types.unliteral(
            other) == A.dtype.elem_type:
            val = get_literal_value(other)
            sqzu__lkp = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                zoxe__ojtyk = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), sqzu__lkp)
                return zoxe__ojtyk
            return impl_lit

        def impl(A, other):
            sqzu__lkp = get_code_for_value(A.dtype, other)
            zoxe__ojtyk = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), sqzu__lkp)
            return zoxe__ojtyk
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        wzrcp__hstrv = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(wzrcp__hstrv)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    gruzh__rset = cat_dtype.categories
    n = len(gruzh__rset)
    for rufj__dwz in range(n):
        if gruzh__rset[rufj__dwz] == val:
            return rufj__dwz
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    sac__pfjw = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype')
    if sac__pfjw != A.dtype.elem_type and sac__pfjw != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if sac__pfjw == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            zoxe__ojtyk = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for rufj__dwz in numba.parfors.parfor.internal_prange(n):
                kthtl__scxvc = codes[rufj__dwz]
                if kthtl__scxvc == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(
                            zoxe__ojtyk, rufj__dwz)
                    else:
                        bodo.libs.array_kernels.setna(zoxe__ojtyk, rufj__dwz)
                    continue
                zoxe__ojtyk[rufj__dwz] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[kthtl__scxvc]))
            return zoxe__ojtyk
        return impl
    lxplu__iwwsr = dtype_to_array_type(sac__pfjw)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        zoxe__ojtyk = bodo.utils.utils.alloc_type(n, lxplu__iwwsr, (-1,))
        for rufj__dwz in numba.parfors.parfor.internal_prange(n):
            kthtl__scxvc = codes[rufj__dwz]
            if kthtl__scxvc == -1:
                bodo.libs.array_kernels.setna(zoxe__ojtyk, rufj__dwz)
                continue
            zoxe__ojtyk[rufj__dwz] = bodo.utils.conversion.unbox_if_timestamp(
                categories[kthtl__scxvc])
        return zoxe__ojtyk
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        stzu__mycfj, wde__pran = args
        gruzh__rset = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        gruzh__rset.codes = stzu__mycfj
        gruzh__rset.dtype = wde__pran
        context.nrt.incref(builder, signature.args[0], stzu__mycfj)
        context.nrt.incref(builder, signature.args[1], wde__pran)
        return gruzh__rset._getvalue()
    eqx__opv = CategoricalArrayType(cat_dtype)
    sig = eqx__opv(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    mvx__ogdi = args[0]
    if equiv_set.has_shape(mvx__ogdi):
        return ArrayAnalysis.AnalyzeResult(shape=mvx__ogdi, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    lzc__uhdst = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, lzc__uhdst)
        return init_categorical_array(codes, cat_dtype)
    return impl


def alloc_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_alloc_categorical_array
    ) = alloc_categorical_array_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_categorical_arr_codes(A):
    return lambda A: A.codes


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_categorical_array',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_categorical_arr_codes',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func


@overload_method(CategoricalArrayType, 'copy', no_unliteral=True)
def cat_arr_copy_overload(arr):
    return lambda arr: init_categorical_array(arr.codes.copy(), arr.dtype)


def build_replace_dicts(to_replace, value, categories):
    return dict(), np.empty(len(categories) + 1), 0


@overload(build_replace_dicts, no_unliteral=True)
def _build_replace_dicts(to_replace, value, categories):
    if isinstance(to_replace, types.Number) or to_replace == bodo.string_type:

        def impl(to_replace, value, categories):
            return build_replace_dicts([to_replace], value, categories)
        return impl
    else:

        def impl(to_replace, value, categories):
            n = len(categories)
            kscrc__foifv = {}
            hjmn__spp = np.empty(n + 1, np.int64)
            ofdn__xeh = {}
            oroq__rfntc = []
            xmb__vhseo = {}
            for rufj__dwz in range(n):
                xmb__vhseo[categories[rufj__dwz]] = rufj__dwz
            for waclo__unepg in to_replace:
                if waclo__unepg != value:
                    if waclo__unepg in xmb__vhseo:
                        if value in xmb__vhseo:
                            kscrc__foifv[waclo__unepg] = waclo__unepg
                            hto__ksbp = xmb__vhseo[waclo__unepg]
                            ofdn__xeh[hto__ksbp] = xmb__vhseo[value]
                            oroq__rfntc.append(hto__ksbp)
                        else:
                            kscrc__foifv[waclo__unepg] = value
                            xmb__vhseo[value] = xmb__vhseo[waclo__unepg]
            kri__enkkw = np.sort(np.array(oroq__rfntc))
            oqd__bfwbb = 0
            nfc__muhz = []
            for wxg__dmxi in range(-1, n):
                while oqd__bfwbb < len(kri__enkkw) and wxg__dmxi > kri__enkkw[
                    oqd__bfwbb]:
                    oqd__bfwbb += 1
                nfc__muhz.append(oqd__bfwbb)
            for rqkwu__xpiy in range(-1, n):
                rao__kua = rqkwu__xpiy
                if rqkwu__xpiy in ofdn__xeh:
                    rao__kua = ofdn__xeh[rqkwu__xpiy]
                hjmn__spp[rqkwu__xpiy + 1] = rao__kua - nfc__muhz[rao__kua + 1]
            return kscrc__foifv, hjmn__spp, len(kri__enkkw)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for rufj__dwz in range(len(new_codes_arr)):
        new_codes_arr[rufj__dwz] = codes_map_arr[old_codes_arr[rufj__dwz] + 1]


@overload_method(CategoricalArrayType, 'replace', inline='always',
    no_unliteral=True)
def overload_replace(arr, to_replace, value):

    def impl(arr, to_replace, value):
        return bodo.hiframes.pd_categorical_ext.cat_replace(arr, to_replace,
            value)
    return impl


def cat_replace(arr, to_replace, value):
    return


@overload(cat_replace, no_unliteral=True)
def cat_replace_overload(arr, to_replace, value):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(to_replace,
        'CategoricalArray.replace()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'CategoricalArray.replace()')
    azldj__cjth = arr.dtype.ordered
    pbccp__awq = arr.dtype.elem_type
    vkm__ipg = get_overload_const(to_replace)
    lyv__crr = get_overload_const(value)
    if (arr.dtype.categories is not None and vkm__ipg is not NOT_CONSTANT and
        lyv__crr is not NOT_CONSTANT):
        qlj__rulf, codes_map_arr, ncez__hclcj = python_build_replace_dicts(
            vkm__ipg, lyv__crr, arr.dtype.categories)
        if len(qlj__rulf) == 0:
            return lambda arr, to_replace, value: arr.copy()
        dsua__nyk = []
        for jhrn__lizx in arr.dtype.categories:
            if jhrn__lizx in qlj__rulf:
                oiycx__beoqv = qlj__rulf[jhrn__lizx]
                if oiycx__beoqv != jhrn__lizx:
                    dsua__nyk.append(oiycx__beoqv)
            else:
                dsua__nyk.append(jhrn__lizx)
        imw__rcpd = bodo.utils.utils.create_categorical_type(dsua__nyk, arr
            .dtype.data.data, azldj__cjth)
        lljd__rgt = MetaType(tuple(imw__rcpd))

        def impl_dtype(arr, to_replace, value):
            ypfw__dhm = init_cat_dtype(bodo.utils.conversion.
                index_from_array(imw__rcpd), azldj__cjth, None, lljd__rgt)
            gruzh__rset = alloc_categorical_array(len(arr.codes), ypfw__dhm)
            reassign_codes(gruzh__rset.codes, arr.codes, codes_map_arr)
            return gruzh__rset
        return impl_dtype
    pbccp__awq = arr.dtype.elem_type
    if pbccp__awq == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            kscrc__foifv, codes_map_arr, lkzcq__rqnz = build_replace_dicts(
                to_replace, value, categories.values)
            if len(kscrc__foifv) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), azldj__cjth,
                    None, None))
            n = len(categories)
            imw__rcpd = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                lkzcq__rqnz, -1)
            zkuc__oerd = 0
            for wxg__dmxi in range(n):
                pvqf__iikmq = categories[wxg__dmxi]
                if pvqf__iikmq in kscrc__foifv:
                    brln__tgsn = kscrc__foifv[pvqf__iikmq]
                    if brln__tgsn != pvqf__iikmq:
                        imw__rcpd[zkuc__oerd] = brln__tgsn
                        zkuc__oerd += 1
                else:
                    imw__rcpd[zkuc__oerd] = pvqf__iikmq
                    zkuc__oerd += 1
            gruzh__rset = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                imw__rcpd), azldj__cjth, None, None))
            reassign_codes(gruzh__rset.codes, arr.codes, codes_map_arr)
            return gruzh__rset
        return impl_str
    byiiv__pnk = dtype_to_array_type(pbccp__awq)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        kscrc__foifv, codes_map_arr, lkzcq__rqnz = build_replace_dicts(
            to_replace, value, categories.values)
        if len(kscrc__foifv) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), azldj__cjth, None, None))
        n = len(categories)
        imw__rcpd = bodo.utils.utils.alloc_type(n - lkzcq__rqnz, byiiv__pnk,
            None)
        zkuc__oerd = 0
        for rufj__dwz in range(n):
            pvqf__iikmq = categories[rufj__dwz]
            if pvqf__iikmq in kscrc__foifv:
                brln__tgsn = kscrc__foifv[pvqf__iikmq]
                if brln__tgsn != pvqf__iikmq:
                    imw__rcpd[zkuc__oerd] = brln__tgsn
                    zkuc__oerd += 1
            else:
                imw__rcpd[zkuc__oerd] = pvqf__iikmq
                zkuc__oerd += 1
        gruzh__rset = alloc_categorical_array(len(arr.codes),
            init_cat_dtype(bodo.utils.conversion.index_from_array(imw__rcpd
            ), azldj__cjth, None, None))
        reassign_codes(gruzh__rset.codes, arr.codes, codes_map_arr)
        return gruzh__rset
    return impl


@overload(len, no_unliteral=True)
def overload_cat_arr_len(A):
    if isinstance(A, CategoricalArrayType):
        return lambda A: len(A.codes)


@overload_attribute(CategoricalArrayType, 'shape')
def overload_cat_arr_shape(A):
    return lambda A: (len(A.codes),)


@overload_attribute(CategoricalArrayType, 'ndim')
def overload_cat_arr_ndim(A):
    return lambda A: 1


@overload_attribute(CategoricalArrayType, 'nbytes')
def cat_arr_nbytes_overload(A):
    return lambda A: A.codes.nbytes + A.dtype.nbytes


@register_jitable
def get_label_dict_from_categories(vals):
    sbgm__vngb = dict()
    uezrz__gjia = 0
    for rufj__dwz in range(len(vals)):
        val = vals[rufj__dwz]
        if val in sbgm__vngb:
            continue
        sbgm__vngb[val] = uezrz__gjia
        uezrz__gjia += 1
    return sbgm__vngb


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    sbgm__vngb = dict()
    for rufj__dwz in range(len(vals)):
        val = vals[rufj__dwz]
        sbgm__vngb[val] = rufj__dwz
    return sbgm__vngb


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    tyzk__wzawj = dict(fastpath=fastpath)
    bxloj__bqxt = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', tyzk__wzawj, bxloj__bqxt)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        fog__eqqcp = get_overload_const(categories)
        if fog__eqqcp is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                kiluw__nwjqa = False
            else:
                kiluw__nwjqa = get_overload_const_bool(ordered)
            xcbqg__bifu = pd.CategoricalDtype(pd.array(fog__eqqcp),
                kiluw__nwjqa).categories.array
            ddc__iayui = MetaType(tuple(xcbqg__bifu))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                ypfw__dhm = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(xcbqg__bifu), kiluw__nwjqa, None,
                    ddc__iayui)
                return bodo.utils.conversion.fix_arr_dtype(data, ypfw__dhm)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            iudgn__dsis = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                iudgn__dsis, ordered, None, None)
            return bodo.utils.conversion.fix_arr_dtype(data, cat_dtype)
        return impl_cats
    elif is_overload_none(ordered):

        def impl_auto(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, 'category')
        return impl_auto
    raise BodoError(
        f'pd.Categorical(): argument combination not supported yet: {values}, {categories}, {ordered}, {dtype}'
        )


@overload(operator.getitem, no_unliteral=True)
def categorical_array_getitem(arr, ind):
    if not isinstance(arr, CategoricalArrayType):
        return
    if isinstance(ind, types.Integer):

        def categorical_getitem_impl(arr, ind):
            oulm__ukdvc = arr.codes[ind]
            return arr.dtype.categories[max(oulm__ukdvc, 0)]
        return categorical_getitem_impl
    if is_list_like_index_type(ind) or isinstance(ind, types.SliceType):

        def impl_bool(arr, ind):
            return init_categorical_array(arr.codes[ind], arr.dtype)
        return impl_bool
    raise BodoError(
        f'getitem for CategoricalArrayType with indexing type {ind} not supported.'
        )


class CategoricalMatchingValues(enum.Enum):
    DIFFERENT_TYPES = -1
    DONT_MATCH = 0
    MAY_MATCH = 1
    DO_MATCH = 2


def categorical_arrs_match(arr1, arr2):
    if not (isinstance(arr1, CategoricalArrayType) and isinstance(arr2,
        CategoricalArrayType)):
        return CategoricalMatchingValues.DIFFERENT_TYPES
    if arr1.dtype.categories is None or arr2.dtype.categories is None:
        return CategoricalMatchingValues.MAY_MATCH
    return (CategoricalMatchingValues.DO_MATCH if arr1.dtype.categories ==
        arr2.dtype.categories and arr1.dtype.ordered == arr2.dtype.ordered else
        CategoricalMatchingValues.DONT_MATCH)


@register_jitable
def cat_dtype_equal(dtype1, dtype2):
    if dtype1.ordered != dtype2.ordered or len(dtype1.categories) != len(dtype2
        .categories):
        return False
    arr1 = dtype1.categories.values
    arr2 = dtype2.categories.values
    for rufj__dwz in range(len(arr1)):
        if arr1[rufj__dwz] != arr2[rufj__dwz]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    rdy__lbyia = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    akea__yqm = not isinstance(val, CategoricalArrayType) and is_iterable_type(
        val) and is_common_scalar_dtype([val.dtype, arr.dtype.elem_type]
        ) and not (isinstance(arr.dtype.elem_type, types.Integer) and
        isinstance(val.dtype, types.Float))
    fnv__ihsb = categorical_arrs_match(arr, val)
    wjum__vqstx = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    jslmo__phuum = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not rdy__lbyia:
            raise BodoError(wjum__vqstx)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            oulm__ukdvc = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = oulm__ukdvc
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (rdy__lbyia or akea__yqm or fnv__ihsb !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(wjum__vqstx)
        if fnv__ihsb == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(jslmo__phuum)
        if rdy__lbyia:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                cgyt__vmm = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for wxg__dmxi in range(n):
                    arr.codes[ind[wxg__dmxi]] = cgyt__vmm
            return impl_scalar
        if fnv__ihsb == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for rufj__dwz in range(n):
                    arr.codes[ind[rufj__dwz]] = val.codes[rufj__dwz]
            return impl_arr_ind_mask
        if fnv__ihsb == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(jslmo__phuum)
                n = len(val.codes)
                for rufj__dwz in range(n):
                    arr.codes[ind[rufj__dwz]] = val.codes[rufj__dwz]
            return impl_arr_ind_mask
        if akea__yqm:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for wxg__dmxi in range(n):
                    ojxa__onsy = bodo.utils.conversion.unbox_if_timestamp(val
                        [wxg__dmxi])
                    if ojxa__onsy not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    oulm__ukdvc = categories.get_loc(ojxa__onsy)
                    arr.codes[ind[wxg__dmxi]] = oulm__ukdvc
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (rdy__lbyia or akea__yqm or fnv__ihsb !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(wjum__vqstx)
        if fnv__ihsb == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(jslmo__phuum)
        if rdy__lbyia:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                cgyt__vmm = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for wxg__dmxi in range(n):
                    if ind[wxg__dmxi]:
                        arr.codes[wxg__dmxi] = cgyt__vmm
            return impl_scalar
        if fnv__ihsb == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                cwd__qyar = 0
                for rufj__dwz in range(n):
                    if ind[rufj__dwz]:
                        arr.codes[rufj__dwz] = val.codes[cwd__qyar]
                        cwd__qyar += 1
            return impl_bool_ind_mask
        if fnv__ihsb == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(jslmo__phuum)
                n = len(ind)
                cwd__qyar = 0
                for rufj__dwz in range(n):
                    if ind[rufj__dwz]:
                        arr.codes[rufj__dwz] = val.codes[cwd__qyar]
                        cwd__qyar += 1
            return impl_bool_ind_mask
        if akea__yqm:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                cwd__qyar = 0
                categories = arr.dtype.categories
                for wxg__dmxi in range(n):
                    if ind[wxg__dmxi]:
                        ojxa__onsy = bodo.utils.conversion.unbox_if_timestamp(
                            val[cwd__qyar])
                        if ojxa__onsy not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        oulm__ukdvc = categories.get_loc(ojxa__onsy)
                        arr.codes[wxg__dmxi] = oulm__ukdvc
                        cwd__qyar += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (rdy__lbyia or akea__yqm or fnv__ihsb !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(wjum__vqstx)
        if fnv__ihsb == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(jslmo__phuum)
        if rdy__lbyia:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                cgyt__vmm = arr.dtype.categories.get_loc(val)
                kkwjx__lrvh = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                for wxg__dmxi in range(kkwjx__lrvh.start, kkwjx__lrvh.stop,
                    kkwjx__lrvh.step):
                    arr.codes[wxg__dmxi] = cgyt__vmm
            return impl_scalar
        if fnv__ihsb == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if fnv__ihsb == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(jslmo__phuum)
                arr.codes[ind] = val.codes
            return impl_arr
        if akea__yqm:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                kkwjx__lrvh = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                cwd__qyar = 0
                for wxg__dmxi in range(kkwjx__lrvh.start, kkwjx__lrvh.stop,
                    kkwjx__lrvh.step):
                    ojxa__onsy = bodo.utils.conversion.unbox_if_timestamp(val
                        [cwd__qyar])
                    if ojxa__onsy not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    oulm__ukdvc = categories.get_loc(ojxa__onsy)
                    arr.codes[wxg__dmxi] = oulm__ukdvc
                    cwd__qyar += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
