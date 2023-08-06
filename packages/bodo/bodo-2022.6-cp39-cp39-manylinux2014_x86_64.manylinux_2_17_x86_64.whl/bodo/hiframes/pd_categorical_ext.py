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
        crg__zrg = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=crg__zrg)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    ifzj__gvwdq = tuple(val.categories.values)
    elem_type = None if len(ifzj__gvwdq) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(ifzj__gvwdq, elem_type, val.ordered, bodo.
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
        lws__cpu = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, lws__cpu)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    olmm__xpl = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    jleg__ewgsz = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, syblq__hnane, syblq__hnane = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    frm__ijgm = PDCategoricalDtype(jleg__ewgsz, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, olmm__xpl)
    return frm__ijgm(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hsh__hemb = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, hsh__hemb).value
    c.pyapi.decref(hsh__hemb)
    sxbg__wgb = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, sxbg__wgb).value
    c.pyapi.decref(sxbg__wgb)
    gxn__odpn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=gxn__odpn)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    hsh__hemb = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    ppjig__eqpuf = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    mbbu__ttpy = c.context.insert_const_string(c.builder.module, 'pandas')
    yess__jjny = c.pyapi.import_module_noblock(mbbu__ttpy)
    wdyul__pevps = c.pyapi.call_method(yess__jjny, 'CategoricalDtype', (
        ppjig__eqpuf, hsh__hemb))
    c.pyapi.decref(hsh__hemb)
    c.pyapi.decref(ppjig__eqpuf)
    c.pyapi.decref(yess__jjny)
    c.context.nrt.decref(c.builder, typ, val)
    return wdyul__pevps


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
        ixame__bitq = get_categories_int_type(fe_type.dtype)
        lws__cpu = [('dtype', fe_type.dtype), ('codes', types.Array(
            ixame__bitq, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, lws__cpu)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    yun__xkpi = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), yun__xkpi
        ).value
    c.pyapi.decref(yun__xkpi)
    wdyul__pevps = c.pyapi.object_getattr_string(val, 'dtype')
    nzird__llrp = c.pyapi.to_native_value(typ.dtype, wdyul__pevps).value
    c.pyapi.decref(wdyul__pevps)
    yolpk__xyk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    yolpk__xyk.codes = codes
    yolpk__xyk.dtype = nzird__llrp
    return NativeValue(yolpk__xyk._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    wej__onbf = get_categories_int_type(typ.dtype)
    nyd__ogaa = context.get_constant_generic(builder, types.Array(wej__onbf,
        1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, nyd__ogaa])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    dgk__bnxg = len(cat_dtype.categories)
    if dgk__bnxg < np.iinfo(np.int8).max:
        dtype = types.int8
    elif dgk__bnxg < np.iinfo(np.int16).max:
        dtype = types.int16
    elif dgk__bnxg < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    mbbu__ttpy = c.context.insert_const_string(c.builder.module, 'pandas')
    yess__jjny = c.pyapi.import_module_noblock(mbbu__ttpy)
    ixame__bitq = get_categories_int_type(dtype)
    qup__jkw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    veodz__lhgqv = types.Array(ixame__bitq, 1, 'C')
    c.context.nrt.incref(c.builder, veodz__lhgqv, qup__jkw.codes)
    yun__xkpi = c.pyapi.from_native_value(veodz__lhgqv, qup__jkw.codes, c.
        env_manager)
    c.context.nrt.incref(c.builder, dtype, qup__jkw.dtype)
    wdyul__pevps = c.pyapi.from_native_value(dtype, qup__jkw.dtype, c.
        env_manager)
    scki__qct = c.pyapi.borrow_none()
    bej__kyagt = c.pyapi.object_getattr_string(yess__jjny, 'Categorical')
    ciike__elmqu = c.pyapi.call_method(bej__kyagt, 'from_codes', (yun__xkpi,
        scki__qct, scki__qct, wdyul__pevps))
    c.pyapi.decref(bej__kyagt)
    c.pyapi.decref(yun__xkpi)
    c.pyapi.decref(wdyul__pevps)
    c.pyapi.decref(yess__jjny)
    c.context.nrt.decref(c.builder, typ, val)
    return ciike__elmqu


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
            vwu__irod = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                jhdt__nuyx = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), vwu__irod)
                return jhdt__nuyx
            return impl_lit

        def impl(A, other):
            vwu__irod = get_code_for_value(A.dtype, other)
            jhdt__nuyx = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), vwu__irod)
            return jhdt__nuyx
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        xvca__nzls = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(xvca__nzls)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    qup__jkw = cat_dtype.categories
    n = len(qup__jkw)
    for jqii__brp in range(n):
        if qup__jkw[jqii__brp] == val:
            return jqii__brp
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    bhdj__osa = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype')
    if bhdj__osa != A.dtype.elem_type and bhdj__osa != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if bhdj__osa == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            jhdt__nuyx = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for jqii__brp in numba.parfors.parfor.internal_prange(n):
                dhyi__kvkad = codes[jqii__brp]
                if dhyi__kvkad == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(jhdt__nuyx
                            , jqii__brp)
                    else:
                        bodo.libs.array_kernels.setna(jhdt__nuyx, jqii__brp)
                    continue
                jhdt__nuyx[jqii__brp] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[dhyi__kvkad]))
            return jhdt__nuyx
        return impl
    veodz__lhgqv = dtype_to_array_type(bhdj__osa)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        jhdt__nuyx = bodo.utils.utils.alloc_type(n, veodz__lhgqv, (-1,))
        for jqii__brp in numba.parfors.parfor.internal_prange(n):
            dhyi__kvkad = codes[jqii__brp]
            if dhyi__kvkad == -1:
                bodo.libs.array_kernels.setna(jhdt__nuyx, jqii__brp)
                continue
            jhdt__nuyx[jqii__brp] = bodo.utils.conversion.unbox_if_timestamp(
                categories[dhyi__kvkad])
        return jhdt__nuyx
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        zpc__edag, nzird__llrp = args
        qup__jkw = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        qup__jkw.codes = zpc__edag
        qup__jkw.dtype = nzird__llrp
        context.nrt.incref(builder, signature.args[0], zpc__edag)
        context.nrt.incref(builder, signature.args[1], nzird__llrp)
        return qup__jkw._getvalue()
    fqz__kjhh = CategoricalArrayType(cat_dtype)
    sig = fqz__kjhh(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    boq__qyoza = args[0]
    if equiv_set.has_shape(boq__qyoza):
        return ArrayAnalysis.AnalyzeResult(shape=boq__qyoza, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    ixame__bitq = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, ixame__bitq)
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
            hiy__qdaf = {}
            nyd__ogaa = np.empty(n + 1, np.int64)
            wou__zep = {}
            qgsa__eal = []
            gedie__wqxr = {}
            for jqii__brp in range(n):
                gedie__wqxr[categories[jqii__brp]] = jqii__brp
            for otk__xhuz in to_replace:
                if otk__xhuz != value:
                    if otk__xhuz in gedie__wqxr:
                        if value in gedie__wqxr:
                            hiy__qdaf[otk__xhuz] = otk__xhuz
                            umj__mhuui = gedie__wqxr[otk__xhuz]
                            wou__zep[umj__mhuui] = gedie__wqxr[value]
                            qgsa__eal.append(umj__mhuui)
                        else:
                            hiy__qdaf[otk__xhuz] = value
                            gedie__wqxr[value] = gedie__wqxr[otk__xhuz]
            oatn__wfljq = np.sort(np.array(qgsa__eal))
            ktcl__pny = 0
            gdpsf__cast = []
            for ockn__rxt in range(-1, n):
                while ktcl__pny < len(oatn__wfljq) and ockn__rxt > oatn__wfljq[
                    ktcl__pny]:
                    ktcl__pny += 1
                gdpsf__cast.append(ktcl__pny)
            for cvqit__efnmt in range(-1, n):
                ssg__vojv = cvqit__efnmt
                if cvqit__efnmt in wou__zep:
                    ssg__vojv = wou__zep[cvqit__efnmt]
                nyd__ogaa[cvqit__efnmt + 1] = ssg__vojv - gdpsf__cast[
                    ssg__vojv + 1]
            return hiy__qdaf, nyd__ogaa, len(oatn__wfljq)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for jqii__brp in range(len(new_codes_arr)):
        new_codes_arr[jqii__brp] = codes_map_arr[old_codes_arr[jqii__brp] + 1]


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
    ejg__bkaf = arr.dtype.ordered
    uodt__egio = arr.dtype.elem_type
    hrb__npeoq = get_overload_const(to_replace)
    qjbcg__ppyx = get_overload_const(value)
    if (arr.dtype.categories is not None and hrb__npeoq is not NOT_CONSTANT and
        qjbcg__ppyx is not NOT_CONSTANT):
        mynu__vtyg, codes_map_arr, syblq__hnane = python_build_replace_dicts(
            hrb__npeoq, qjbcg__ppyx, arr.dtype.categories)
        if len(mynu__vtyg) == 0:
            return lambda arr, to_replace, value: arr.copy()
        pem__jbcp = []
        for gjybi__qftp in arr.dtype.categories:
            if gjybi__qftp in mynu__vtyg:
                qumf__jxj = mynu__vtyg[gjybi__qftp]
                if qumf__jxj != gjybi__qftp:
                    pem__jbcp.append(qumf__jxj)
            else:
                pem__jbcp.append(gjybi__qftp)
        utq__ljib = bodo.utils.utils.create_categorical_type(pem__jbcp, arr
            .dtype.data.data, ejg__bkaf)
        guemc__yby = MetaType(tuple(utq__ljib))

        def impl_dtype(arr, to_replace, value):
            ynr__imkd = init_cat_dtype(bodo.utils.conversion.
                index_from_array(utq__ljib), ejg__bkaf, None, guemc__yby)
            qup__jkw = alloc_categorical_array(len(arr.codes), ynr__imkd)
            reassign_codes(qup__jkw.codes, arr.codes, codes_map_arr)
            return qup__jkw
        return impl_dtype
    uodt__egio = arr.dtype.elem_type
    if uodt__egio == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            hiy__qdaf, codes_map_arr, gcnb__vxtl = build_replace_dicts(
                to_replace, value, categories.values)
            if len(hiy__qdaf) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), ejg__bkaf,
                    None, None))
            n = len(categories)
            utq__ljib = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                gcnb__vxtl, -1)
            nvttx__jqlrh = 0
            for ockn__rxt in range(n):
                jjy__zvi = categories[ockn__rxt]
                if jjy__zvi in hiy__qdaf:
                    gyzuy__trg = hiy__qdaf[jjy__zvi]
                    if gyzuy__trg != jjy__zvi:
                        utq__ljib[nvttx__jqlrh] = gyzuy__trg
                        nvttx__jqlrh += 1
                else:
                    utq__ljib[nvttx__jqlrh] = jjy__zvi
                    nvttx__jqlrh += 1
            qup__jkw = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                utq__ljib), ejg__bkaf, None, None))
            reassign_codes(qup__jkw.codes, arr.codes, codes_map_arr)
            return qup__jkw
        return impl_str
    gnhb__yvsys = dtype_to_array_type(uodt__egio)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        hiy__qdaf, codes_map_arr, gcnb__vxtl = build_replace_dicts(to_replace,
            value, categories.values)
        if len(hiy__qdaf) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), ejg__bkaf, None, None))
        n = len(categories)
        utq__ljib = bodo.utils.utils.alloc_type(n - gcnb__vxtl, gnhb__yvsys,
            None)
        nvttx__jqlrh = 0
        for jqii__brp in range(n):
            jjy__zvi = categories[jqii__brp]
            if jjy__zvi in hiy__qdaf:
                gyzuy__trg = hiy__qdaf[jjy__zvi]
                if gyzuy__trg != jjy__zvi:
                    utq__ljib[nvttx__jqlrh] = gyzuy__trg
                    nvttx__jqlrh += 1
            else:
                utq__ljib[nvttx__jqlrh] = jjy__zvi
                nvttx__jqlrh += 1
        qup__jkw = alloc_categorical_array(len(arr.codes), init_cat_dtype(
            bodo.utils.conversion.index_from_array(utq__ljib), ejg__bkaf,
            None, None))
        reassign_codes(qup__jkw.codes, arr.codes, codes_map_arr)
        return qup__jkw
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
    ove__zgp = dict()
    ftoqv__bye = 0
    for jqii__brp in range(len(vals)):
        val = vals[jqii__brp]
        if val in ove__zgp:
            continue
        ove__zgp[val] = ftoqv__bye
        ftoqv__bye += 1
    return ove__zgp


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    ove__zgp = dict()
    for jqii__brp in range(len(vals)):
        val = vals[jqii__brp]
        ove__zgp[val] = jqii__brp
    return ove__zgp


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    hxad__xeca = dict(fastpath=fastpath)
    jcwvn__wap = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', hxad__xeca, jcwvn__wap)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        cmlu__knjd = get_overload_const(categories)
        if cmlu__knjd is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                lhg__zjs = False
            else:
                lhg__zjs = get_overload_const_bool(ordered)
            hat__swlp = pd.CategoricalDtype(pd.array(cmlu__knjd), lhg__zjs
                ).categories.array
            sojla__tndo = MetaType(tuple(hat__swlp))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                ynr__imkd = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(hat__swlp), lhg__zjs, None, sojla__tndo)
                return bodo.utils.conversion.fix_arr_dtype(data, ynr__imkd)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            ifzj__gvwdq = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                ifzj__gvwdq, ordered, None, None)
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
            ctdl__iczf = arr.codes[ind]
            return arr.dtype.categories[max(ctdl__iczf, 0)]
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
    for jqii__brp in range(len(arr1)):
        if arr1[jqii__brp] != arr2[jqii__brp]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    gtoa__vffy = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    emzqa__agbjf = not isinstance(val, CategoricalArrayType
        ) and is_iterable_type(val) and is_common_scalar_dtype([val.dtype,
        arr.dtype.elem_type]) and not (isinstance(arr.dtype.elem_type,
        types.Integer) and isinstance(val.dtype, types.Float))
    osjxo__vsvox = categorical_arrs_match(arr, val)
    hoa__ptqvb = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    owg__lbq = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not gtoa__vffy:
            raise BodoError(hoa__ptqvb)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            ctdl__iczf = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = ctdl__iczf
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (gtoa__vffy or emzqa__agbjf or osjxo__vsvox !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(hoa__ptqvb)
        if osjxo__vsvox == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(owg__lbq)
        if gtoa__vffy:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                llzxe__syeus = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for ockn__rxt in range(n):
                    arr.codes[ind[ockn__rxt]] = llzxe__syeus
            return impl_scalar
        if osjxo__vsvox == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for jqii__brp in range(n):
                    arr.codes[ind[jqii__brp]] = val.codes[jqii__brp]
            return impl_arr_ind_mask
        if osjxo__vsvox == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(owg__lbq)
                n = len(val.codes)
                for jqii__brp in range(n):
                    arr.codes[ind[jqii__brp]] = val.codes[jqii__brp]
            return impl_arr_ind_mask
        if emzqa__agbjf:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for ockn__rxt in range(n):
                    ebo__dzz = bodo.utils.conversion.unbox_if_timestamp(val
                        [ockn__rxt])
                    if ebo__dzz not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    ctdl__iczf = categories.get_loc(ebo__dzz)
                    arr.codes[ind[ockn__rxt]] = ctdl__iczf
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (gtoa__vffy or emzqa__agbjf or osjxo__vsvox !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(hoa__ptqvb)
        if osjxo__vsvox == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(owg__lbq)
        if gtoa__vffy:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                llzxe__syeus = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for ockn__rxt in range(n):
                    if ind[ockn__rxt]:
                        arr.codes[ockn__rxt] = llzxe__syeus
            return impl_scalar
        if osjxo__vsvox == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                keywz__alzfa = 0
                for jqii__brp in range(n):
                    if ind[jqii__brp]:
                        arr.codes[jqii__brp] = val.codes[keywz__alzfa]
                        keywz__alzfa += 1
            return impl_bool_ind_mask
        if osjxo__vsvox == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(owg__lbq)
                n = len(ind)
                keywz__alzfa = 0
                for jqii__brp in range(n):
                    if ind[jqii__brp]:
                        arr.codes[jqii__brp] = val.codes[keywz__alzfa]
                        keywz__alzfa += 1
            return impl_bool_ind_mask
        if emzqa__agbjf:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                keywz__alzfa = 0
                categories = arr.dtype.categories
                for ockn__rxt in range(n):
                    if ind[ockn__rxt]:
                        ebo__dzz = bodo.utils.conversion.unbox_if_timestamp(val
                            [keywz__alzfa])
                        if ebo__dzz not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        ctdl__iczf = categories.get_loc(ebo__dzz)
                        arr.codes[ockn__rxt] = ctdl__iczf
                        keywz__alzfa += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (gtoa__vffy or emzqa__agbjf or osjxo__vsvox !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(hoa__ptqvb)
        if osjxo__vsvox == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(owg__lbq)
        if gtoa__vffy:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                llzxe__syeus = arr.dtype.categories.get_loc(val)
                eypf__zef = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                for ockn__rxt in range(eypf__zef.start, eypf__zef.stop,
                    eypf__zef.step):
                    arr.codes[ockn__rxt] = llzxe__syeus
            return impl_scalar
        if osjxo__vsvox == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if osjxo__vsvox == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(owg__lbq)
                arr.codes[ind] = val.codes
            return impl_arr
        if emzqa__agbjf:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                eypf__zef = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                keywz__alzfa = 0
                for ockn__rxt in range(eypf__zef.start, eypf__zef.stop,
                    eypf__zef.step):
                    ebo__dzz = bodo.utils.conversion.unbox_if_timestamp(val
                        [keywz__alzfa])
                    if ebo__dzz not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    ctdl__iczf = categories.get_loc(ebo__dzz)
                    arr.codes[ockn__rxt] = ctdl__iczf
                    keywz__alzfa += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
