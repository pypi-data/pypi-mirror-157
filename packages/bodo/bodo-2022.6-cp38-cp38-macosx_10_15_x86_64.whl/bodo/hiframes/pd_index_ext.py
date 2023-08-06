import datetime
import operator
import warnings
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_constant
from numba.core.typing.templates import AttributeTemplate, signature
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
import bodo.hiframes
import bodo.utils.conversion
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_overload_const_func, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_udf_error_msg, get_udf_out_arr_type, get_val_type_maybe_str_literal, is_const_func_type, is_heterogeneous_tuple_type, is_iterable_type, is_overload_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_nan, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_none, is_overload_true, is_str_arr_type, parse_dtype, raise_bodo_error
from bodo.utils.utils import is_null_value
_dt_index_data_typ = types.Array(types.NPDatetime('ns'), 1, 'C')
_timedelta_index_data_typ = types.Array(types.NPTimedelta('ns'), 1, 'C')
iNaT = pd._libs.tslibs.iNaT
NaT = types.NPDatetime('ns')('NaT')
idx_cpy_arg_defaults = dict(deep=False, dtype=None, names=None)
idx_typ_to_format_str_map = dict()


@typeof_impl.register(pd.Index)
def typeof_pd_index(val, c):
    if val.inferred_type == 'string' or pd._libs.lib.infer_dtype(val, True
        ) == 'string':
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'bytes' or pd._libs.lib.infer_dtype(val, True
        ) == 'bytes':
        return BinaryIndexType(get_val_type_maybe_str_literal(val.name))
    if val.equals(pd.Index([])):
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'date':
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'integer' or pd._libs.lib.infer_dtype(val, True
        ) == 'integer':
        if isinstance(val.dtype, pd.core.arrays.integer._IntegerDtype):
            eum__izcwi = val.dtype.numpy_dtype
            dtype = numba.np.numpy_support.from_dtype(eum__izcwi)
        else:
            dtype = types.int64
        return NumericIndexType(dtype, get_val_type_maybe_str_literal(val.
            name), IntegerArrayType(dtype))
    if val.inferred_type == 'boolean' or pd._libs.lib.infer_dtype(val, True
        ) == 'boolean':
        return NumericIndexType(types.bool_, get_val_type_maybe_str_literal
            (val.name), boolean_array)
    raise NotImplementedError(f'unsupported pd.Index type {val}')


class DatetimeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.datetime64ns, 1, 'C'
            ) if data is None else data
        super(DatetimeIndexType, self).__init__(name=
            f'DatetimeIndex({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def tzval(self):
        return self.data.tz if isinstance(self.data, bodo.DatetimeArrayType
            ) else None

    def copy(self):
        return DatetimeIndexType(self.name_typ, self.data)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, bodo.hiframes.
            pd_timestamp_ext.PandasTimestampType(self.tzval))

    @property
    def pandas_type_name(self):
        return self.data.dtype.type_name

    @property
    def numpy_type_name(self):
        return str(self.data.dtype)


types.datetime_index = DatetimeIndexType()


@typeof_impl.register(pd.DatetimeIndex)
def typeof_datetime_index(val, c):
    if isinstance(val.dtype, pd.DatetimeTZDtype):
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name),
            DatetimeArrayType(val.tz))
    return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(DatetimeIndexType)
class DatetimeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cenq__mxgkc = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(_dt_index_data_typ.dtype, types.int64))]
        super(DatetimeIndexModel, self).__init__(dmm, fe_type, cenq__mxgkc)


make_attribute_wrapper(DatetimeIndexType, 'data', '_data')
make_attribute_wrapper(DatetimeIndexType, 'name', '_name')
make_attribute_wrapper(DatetimeIndexType, 'dict', '_dict')


@overload_method(DatetimeIndexType, 'copy', no_unliteral=True)
def overload_datetime_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    sjx__dli = dict(deep=deep, dtype=dtype, names=names)
    siqq__hago = idx_typ_to_format_str_map[DatetimeIndexType].format('copy()')
    check_unsupported_args('copy', sjx__dli, idx_cpy_arg_defaults, fn_str=
        siqq__hago, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), A._name)
    return impl


@box(DatetimeIndexType)
def box_dt_index(typ, val, c):
    yivl__nyv = c.context.insert_const_string(c.builder.module, 'pandas')
    xfcit__aeqfb = c.pyapi.import_module_noblock(yivl__nyv)
    ngkws__fda = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, ngkws__fda.data)
    jii__jxsk = c.pyapi.from_native_value(typ.data, ngkws__fda.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ngkws__fda.name)
    efdj__nyeu = c.pyapi.from_native_value(typ.name_typ, ngkws__fda.name, c
        .env_manager)
    args = c.pyapi.tuple_pack([jii__jxsk])
    gxicf__xfz = c.pyapi.object_getattr_string(xfcit__aeqfb, 'DatetimeIndex')
    kws = c.pyapi.dict_pack([('name', efdj__nyeu)])
    syaaj__fwv = c.pyapi.call(gxicf__xfz, args, kws)
    c.pyapi.decref(jii__jxsk)
    c.pyapi.decref(efdj__nyeu)
    c.pyapi.decref(xfcit__aeqfb)
    c.pyapi.decref(gxicf__xfz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return syaaj__fwv


@unbox(DatetimeIndexType)
def unbox_datetime_index(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        ctsu__qlbp = c.pyapi.object_getattr_string(val, 'array')
    else:
        ctsu__qlbp = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, ctsu__qlbp).value
    efdj__nyeu = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, efdj__nyeu).value
    ppov__bdkyw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ppov__bdkyw.data = data
    ppov__bdkyw.name = name
    dtype = _dt_index_data_typ.dtype
    gzb__tdi, amj__kzh = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    ppov__bdkyw.dict = amj__kzh
    c.pyapi.decref(ctsu__qlbp)
    c.pyapi.decref(efdj__nyeu)
    return NativeValue(ppov__bdkyw._getvalue())


@intrinsic
def init_datetime_index(typingctx, data, name):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        htv__bhdkf, wlbfx__ghvx = args
        ngkws__fda = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        ngkws__fda.data = htv__bhdkf
        ngkws__fda.name = wlbfx__ghvx
        context.nrt.incref(builder, signature.args[0], htv__bhdkf)
        context.nrt.incref(builder, signature.args[1], wlbfx__ghvx)
        dtype = _dt_index_data_typ.dtype
        ngkws__fda.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return ngkws__fda._getvalue()
    kudmz__cih = DatetimeIndexType(name, data)
    sig = signature(kudmz__cih, data, name)
    return sig, codegen


def init_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) >= 1 and not kws
    cigz__jyuva = args[0]
    if equiv_set.has_shape(cigz__jyuva):
        return ArrayAnalysis.AnalyzeResult(shape=cigz__jyuva, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_datetime_index
    ) = init_index_equiv


def gen_dti_field_impl(field):
    btrw__gkmt = 'def impl(dti):\n'
    btrw__gkmt += '    numba.parfors.parfor.init_prange()\n'
    btrw__gkmt += '    A = bodo.hiframes.pd_index_ext.get_index_data(dti)\n'
    btrw__gkmt += '    name = bodo.hiframes.pd_index_ext.get_index_name(dti)\n'
    btrw__gkmt += '    n = len(A)\n'
    btrw__gkmt += '    S = np.empty(n, np.int64)\n'
    btrw__gkmt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    btrw__gkmt += '        val = A[i]\n'
    btrw__gkmt += '        ts = bodo.utils.conversion.box_if_dt64(val)\n'
    if field in ['weekday']:
        btrw__gkmt += '        S[i] = ts.' + field + '()\n'
    else:
        btrw__gkmt += '        S[i] = ts.' + field + '\n'
    btrw__gkmt += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    hzehy__rpxwo = {}
    exec(btrw__gkmt, {'numba': numba, 'np': np, 'bodo': bodo}, hzehy__rpxwo)
    impl = hzehy__rpxwo['impl']
    return impl


def _install_dti_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        if field in ['is_leap_year']:
            continue
        impl = gen_dti_field_impl(field)
        overload_attribute(DatetimeIndexType, field)(lambda dti: impl)


_install_dti_date_fields()


@overload_attribute(DatetimeIndexType, 'is_leap_year')
def overload_datetime_index_is_leap_year(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        sadat__mquh = len(A)
        S = np.empty(sadat__mquh, np.bool_)
        for i in numba.parfors.parfor.internal_prange(sadat__mquh):
            val = A[i]
            ibk__djcvb = bodo.utils.conversion.box_if_dt64(val)
            S[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(ibk__djcvb.year)
        return S
    return impl


@overload_attribute(DatetimeIndexType, 'date')
def overload_datetime_index_date(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        sadat__mquh = len(A)
        S = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            sadat__mquh)
        for i in numba.parfors.parfor.internal_prange(sadat__mquh):
            val = A[i]
            ibk__djcvb = bodo.utils.conversion.box_if_dt64(val)
            S[i] = datetime.date(ibk__djcvb.year, ibk__djcvb.month,
                ibk__djcvb.day)
        return S
    return impl


@numba.njit(no_cpython_wrapper=True)
def _dti_val_finalize(s, count):
    if not count:
        s = iNaT
    return bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(s)


@numba.njit(no_cpython_wrapper=True)
def _tdi_val_finalize(s, count):
    return pd.Timedelta('nan') if not count else pd.Timedelta(s)


@overload_method(DatetimeIndexType, 'min', no_unliteral=True)
def overload_datetime_index_min(dti, axis=None, skipna=True):
    vwgld__zch = dict(axis=axis, skipna=skipna)
    vrsnf__bgvf = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.min', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.min()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        pdar__fda = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_max_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(pdar__fda)):
            if not bodo.libs.array_kernels.isna(pdar__fda, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(pdar__fda
                    [i])
                s = min(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'max', no_unliteral=True)
def overload_datetime_index_max(dti, axis=None, skipna=True):
    vwgld__zch = dict(axis=axis, skipna=skipna)
    vrsnf__bgvf = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.max', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.max()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        pdar__fda = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_min_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(pdar__fda)):
            if not bodo.libs.array_kernels.isna(pdar__fda, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(pdar__fda
                    [i])
                s = max(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'tz_convert', no_unliteral=True)
def overload_pd_datetime_tz_convert(A, tz):

    def impl(A, tz):
        return init_datetime_index(A._data.tz_convert(tz), A._name)
    return impl


@infer_getattr
class DatetimeIndexAttribute(AttributeTemplate):
    key = DatetimeIndexType

    def resolve_values(self, ary):
        return _dt_index_data_typ


@overload(pd.DatetimeIndex, no_unliteral=True)
def pd_datetimeindex_overload(data=None, freq=None, tz=None, normalize=
    False, closed=None, ambiguous='raise', dayfirst=False, yearfirst=False,
    dtype=None, copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.DatetimeIndex() expected')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'pandas.DatetimeIndex()')
    vwgld__zch = dict(freq=freq, tz=tz, normalize=normalize, closed=closed,
        ambiguous=ambiguous, dayfirst=dayfirst, yearfirst=yearfirst, dtype=
        dtype, copy=copy)
    vrsnf__bgvf = dict(freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False)
    check_unsupported_args('pandas.DatetimeIndex', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')

    def f(data=None, freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False, name=None):
        ylxbv__rgsp = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_dt64ns(ylxbv__rgsp)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


def overload_sub_operator_datetime_index(lhs, rhs):
    if isinstance(lhs, DatetimeIndexType
        ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        yfja__qpprk = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            pdar__fda = bodo.hiframes.pd_index_ext.get_index_data(lhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(lhs)
            sadat__mquh = len(pdar__fda)
            S = np.empty(sadat__mquh, yfja__qpprk)
            qajy__emy = rhs.value
            for i in numba.parfors.parfor.internal_prange(sadat__mquh):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    pdar__fda[i]) - qajy__emy)
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl
    if isinstance(rhs, DatetimeIndexType
        ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        yfja__qpprk = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            pdar__fda = bodo.hiframes.pd_index_ext.get_index_data(rhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(rhs)
            sadat__mquh = len(pdar__fda)
            S = np.empty(sadat__mquh, yfja__qpprk)
            qajy__emy = lhs.value
            for i in numba.parfors.parfor.internal_prange(sadat__mquh):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    qajy__emy - bodo.hiframes.pd_timestamp_ext.
                    dt64_to_integer(pdar__fda[i]))
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl


def gen_dti_str_binop_impl(op, is_lhs_dti):
    hijhe__txhbb = numba.core.utils.OPERATORS_TO_BUILTINS[op]
    btrw__gkmt = 'def impl(lhs, rhs):\n'
    if is_lhs_dti:
        btrw__gkmt += '  dt_index, _str = lhs, rhs\n'
        eyjy__imm = 'arr[i] {} other'.format(hijhe__txhbb)
    else:
        btrw__gkmt += '  dt_index, _str = rhs, lhs\n'
        eyjy__imm = 'other {} arr[i]'.format(hijhe__txhbb)
    btrw__gkmt += (
        '  arr = bodo.hiframes.pd_index_ext.get_index_data(dt_index)\n')
    btrw__gkmt += '  l = len(arr)\n'
    btrw__gkmt += (
        '  other = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(_str)\n')
    btrw__gkmt += '  S = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    btrw__gkmt += '  for i in numba.parfors.parfor.internal_prange(l):\n'
    btrw__gkmt += '    S[i] = {}\n'.format(eyjy__imm)
    btrw__gkmt += '  return S\n'
    hzehy__rpxwo = {}
    exec(btrw__gkmt, {'bodo': bodo, 'numba': numba, 'np': np}, hzehy__rpxwo)
    impl = hzehy__rpxwo['impl']
    return impl


def overload_binop_dti_str(op):

    def overload_impl(lhs, rhs):
        if isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, True)
        if isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, False)
    return overload_impl


@overload(pd.Index, inline='always', no_unliteral=True)
def pd_index_overload(data=None, dtype=None, copy=False, name=None,
    tupleize_cols=True):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'pandas.Index()')
    data = types.unliteral(data) if not isinstance(data, types.LiteralList
        ) else data
    if not is_overload_none(dtype):
        kwk__gjm = parse_dtype(dtype, 'pandas.Index')
        qdtug__gbezv = False
    else:
        kwk__gjm = getattr(data, 'dtype', None)
        qdtug__gbezv = True
    if isinstance(kwk__gjm, types.misc.PyObject):
        raise BodoError(
            "pd.Index() object 'dtype' is not specific enough for typing. Please provide a more exact type (e.g. str)."
            )
    if isinstance(data, RangeIndexType):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.RangeIndex(data, name=name)
    elif isinstance(data, DatetimeIndexType) or kwk__gjm == types.NPDatetime(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.DatetimeIndex(data, name=name)
    elif isinstance(data, TimedeltaIndexType) or kwk__gjm == types.NPTimedelta(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.TimedeltaIndex(data, name=name)
    elif is_heterogeneous_tuple_type(data):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return bodo.hiframes.pd_index_ext.init_heter_index(data, name)
        return impl
    elif bodo.utils.utils.is_array_typ(data, False) or isinstance(data, (
        SeriesType, types.List, types.UniTuple)):
        if isinstance(kwk__gjm, (types.Integer, types.Float, types.Boolean)):
            if qdtug__gbezv:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    ylxbv__rgsp = bodo.utils.conversion.coerce_to_array(data)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        ylxbv__rgsp, name)
            else:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    ylxbv__rgsp = bodo.utils.conversion.coerce_to_array(data)
                    lrti__zhlsu = bodo.utils.conversion.fix_arr_dtype(
                        ylxbv__rgsp, kwk__gjm)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        lrti__zhlsu, name)
        elif kwk__gjm in [types.string, bytes_type]:

            def impl(data=None, dtype=None, copy=False, name=None,
                tupleize_cols=True):
                return bodo.hiframes.pd_index_ext.init_binary_str_index(bodo
                    .utils.conversion.coerce_to_array(data), name)
        else:
            raise BodoError(
                'pd.Index(): provided array is of unsupported type.')
    elif is_overload_none(data):
        raise BodoError(
            'data argument in pd.Index() is invalid: None or scalar is not acceptable'
            )
    else:
        raise BodoError(
            f'pd.Index(): the provided argument type {data} is not supported')
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_datetime_index_getitem(dti, ind):
    if isinstance(dti, DatetimeIndexType):
        if isinstance(ind, types.Integer):

            def impl(dti, ind):
                yrh__dbhs = bodo.hiframes.pd_index_ext.get_index_data(dti)
                val = yrh__dbhs[ind]
                return bodo.utils.conversion.box_if_dt64(val)
            return impl
        else:

            def impl(dti, ind):
                yrh__dbhs = bodo.hiframes.pd_index_ext.get_index_data(dti)
                name = bodo.hiframes.pd_index_ext.get_index_name(dti)
                qaeri__frj = yrh__dbhs[ind]
                return bodo.hiframes.pd_index_ext.init_datetime_index(
                    qaeri__frj, name)
            return impl


@overload(operator.getitem, no_unliteral=True)
def overload_timedelta_index_getitem(I, ind):
    if not isinstance(I, TimedeltaIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            lsxqr__ocqx = bodo.hiframes.pd_index_ext.get_index_data(I)
            return pd.Timedelta(lsxqr__ocqx[ind])
        return impl

    def impl(I, ind):
        lsxqr__ocqx = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        qaeri__frj = lsxqr__ocqx[ind]
        return bodo.hiframes.pd_index_ext.init_timedelta_index(qaeri__frj, name
            )
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_categorical_index_getitem(I, ind):
    if not isinstance(I, CategoricalIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            syl__flknk = bodo.hiframes.pd_index_ext.get_index_data(I)
            val = syl__flknk[ind]
            return val
        return impl
    if isinstance(ind, types.SliceType):

        def impl(I, ind):
            syl__flknk = bodo.hiframes.pd_index_ext.get_index_data(I)
            name = bodo.hiframes.pd_index_ext.get_index_name(I)
            qaeri__frj = syl__flknk[ind]
            return bodo.hiframes.pd_index_ext.init_categorical_index(qaeri__frj
                , name)
        return impl
    raise BodoError(
        f'pd.CategoricalIndex.__getitem__: unsupported index type {ind}')


@numba.njit(no_cpython_wrapper=True)
def validate_endpoints(closed):
    kuqkg__cfl = False
    fdr__bwmxm = False
    if closed is None:
        kuqkg__cfl = True
        fdr__bwmxm = True
    elif closed == 'left':
        kuqkg__cfl = True
    elif closed == 'right':
        fdr__bwmxm = True
    else:
        raise ValueError("Closed has to be either 'left', 'right' or None")
    return kuqkg__cfl, fdr__bwmxm


@numba.njit(no_cpython_wrapper=True)
def to_offset_value(freq):
    if freq is None:
        return None
    with numba.objmode(r='int64'):
        r = pd.tseries.frequencies.to_offset(freq).nanos
    return r


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _dummy_convert_none_to_int(val):
    if is_overload_none(val):

        def impl(val):
            return 0
        return impl
    if isinstance(val, types.Optional):

        def impl(val):
            if val is None:
                return 0
            return bodo.utils.indexing.unoptional(val)
        return impl
    return lambda val: val


@overload(pd.date_range, inline='always')
def pd_date_range_overload(start=None, end=None, periods=None, freq=None,
    tz=None, normalize=False, name=None, closed=None):
    vwgld__zch = dict(tz=tz, normalize=normalize, closed=closed)
    vrsnf__bgvf = dict(tz=None, normalize=False, closed=None)
    check_unsupported_args('pandas.date_range', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='General')
    if not is_overload_none(tz):
        raise_bodo_error('pd.date_range(): tz argument not supported yet')
    joo__xuohw = ''
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
        joo__xuohw = "  freq = 'D'\n"
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise_bodo_error(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )
    btrw__gkmt = """def f(start=None, end=None, periods=None, freq=None, tz=None, normalize=False, name=None, closed=None):
"""
    btrw__gkmt += joo__xuohw
    if is_overload_none(start):
        btrw__gkmt += "  start_t = pd.Timestamp('1800-01-03')\n"
    else:
        btrw__gkmt += '  start_t = pd.Timestamp(start)\n'
    if is_overload_none(end):
        btrw__gkmt += "  end_t = pd.Timestamp('1800-01-03')\n"
    else:
        btrw__gkmt += '  end_t = pd.Timestamp(end)\n'
    if not is_overload_none(freq):
        btrw__gkmt += (
            '  stride = bodo.hiframes.pd_index_ext.to_offset_value(freq)\n')
        if is_overload_none(periods):
            btrw__gkmt += '  b = start_t.value\n'
            btrw__gkmt += (
                '  e = b + (end_t.value - b) // stride * stride + stride // 2 + 1\n'
                )
        elif not is_overload_none(start):
            btrw__gkmt += '  b = start_t.value\n'
            btrw__gkmt += '  addend = np.int64(periods) * np.int64(stride)\n'
            btrw__gkmt += '  e = np.int64(b) + addend\n'
        elif not is_overload_none(end):
            btrw__gkmt += '  e = end_t.value + stride\n'
            btrw__gkmt += '  addend = np.int64(periods) * np.int64(-stride)\n'
            btrw__gkmt += '  b = np.int64(e) + addend\n'
        else:
            raise_bodo_error(
                "at least 'start' or 'end' should be specified if a 'period' is given."
                )
        btrw__gkmt += '  arr = np.arange(b, e, stride, np.int64)\n'
    else:
        btrw__gkmt += '  delta = end_t.value - start_t.value\n'
        btrw__gkmt += '  step = delta / (periods - 1)\n'
        btrw__gkmt += '  arr1 = np.arange(0, periods, 1, np.float64)\n'
        btrw__gkmt += '  arr1 *= step\n'
        btrw__gkmt += '  arr1 += start_t.value\n'
        btrw__gkmt += '  arr = arr1.astype(np.int64)\n'
        btrw__gkmt += '  arr[-1] = end_t.value\n'
    btrw__gkmt += '  A = bodo.utils.conversion.convert_to_dt64ns(arr)\n'
    btrw__gkmt += (
        '  return bodo.hiframes.pd_index_ext.init_datetime_index(A, name)\n')
    hzehy__rpxwo = {}
    exec(btrw__gkmt, {'bodo': bodo, 'np': np, 'pd': pd}, hzehy__rpxwo)
    f = hzehy__rpxwo['f']
    return f


@overload(pd.timedelta_range, no_unliteral=True)
def pd_timedelta_range_overload(start=None, end=None, periods=None, freq=
    None, name=None, closed=None):
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise BodoError(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )

    def f(start=None, end=None, periods=None, freq=None, name=None, closed=None
        ):
        if freq is None and (start is None or end is None or periods is None):
            freq = 'D'
        freq = bodo.hiframes.pd_index_ext.to_offset_value(freq)
        hiu__ljjq = pd.Timedelta('1 day')
        if start is not None:
            hiu__ljjq = pd.Timedelta(start)
        cof__lofoh = pd.Timedelta('1 day')
        if end is not None:
            cof__lofoh = pd.Timedelta(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of start and end are defined'
                )
        kuqkg__cfl, fdr__bwmxm = bodo.hiframes.pd_index_ext.validate_endpoints(
            closed)
        if freq is not None:
            nnny__bbdtg = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = hiu__ljjq.value
                miae__teqnk = b + (cof__lofoh.value - b
                    ) // nnny__bbdtg * nnny__bbdtg + nnny__bbdtg // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = hiu__ljjq.value
                zize__ftvw = np.int64(periods) * np.int64(nnny__bbdtg)
                miae__teqnk = np.int64(b) + zize__ftvw
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                miae__teqnk = cof__lofoh.value + nnny__bbdtg
                zize__ftvw = np.int64(periods) * np.int64(-nnny__bbdtg)
                b = np.int64(miae__teqnk) + zize__ftvw
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            irk__rekg = np.arange(b, miae__teqnk, nnny__bbdtg, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            wqq__xcv = cof__lofoh.value - hiu__ljjq.value
            step = wqq__xcv / (periods - 1)
            syb__yvns = np.arange(0, periods, 1, np.float64)
            syb__yvns *= step
            syb__yvns += hiu__ljjq.value
            irk__rekg = syb__yvns.astype(np.int64)
            irk__rekg[-1] = cof__lofoh.value
        if not kuqkg__cfl and len(irk__rekg) and irk__rekg[0
            ] == hiu__ljjq.value:
            irk__rekg = irk__rekg[1:]
        if not fdr__bwmxm and len(irk__rekg) and irk__rekg[-1
            ] == cof__lofoh.value:
            irk__rekg = irk__rekg[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(irk__rekg)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return f


@overload_method(DatetimeIndexType, 'isocalendar', inline='always',
    no_unliteral=True)
def overload_pd_timestamp_isocalendar(idx):
    nfr__wtdac = ColNamesMetaType(('year', 'week', 'day'))

    def impl(idx):
        A = bodo.hiframes.pd_index_ext.get_index_data(idx)
        numba.parfors.parfor.init_prange()
        sadat__mquh = len(A)
        mrla__wli = bodo.libs.int_arr_ext.alloc_int_array(sadat__mquh, np.
            uint32)
        twiq__lwsvd = bodo.libs.int_arr_ext.alloc_int_array(sadat__mquh, np
            .uint32)
        xezj__hezq = bodo.libs.int_arr_ext.alloc_int_array(sadat__mquh, np.
            uint32)
        for i in numba.parfors.parfor.internal_prange(sadat__mquh):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(mrla__wli, i)
                bodo.libs.array_kernels.setna(twiq__lwsvd, i)
                bodo.libs.array_kernels.setna(xezj__hezq, i)
                continue
            mrla__wli[i], twiq__lwsvd[i], xezj__hezq[i
                ] = bodo.utils.conversion.box_if_dt64(A[i]).isocalendar()
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((mrla__wli,
            twiq__lwsvd, xezj__hezq), idx, nfr__wtdac)
    return impl


class TimedeltaIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.timedelta64ns, 1, 'C'
            ) if data is None else data
        super(TimedeltaIndexType, self).__init__(name=
            f'TimedeltaIndexType({name_typ}, {self.data})')
    ndim = 1

    def copy(self):
        return TimedeltaIndexType(self.name_typ)

    @property
    def dtype(self):
        return types.NPTimedelta('ns')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.name_typ, self.data

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, bodo.pd_timedelta_type
            )

    @property
    def pandas_type_name(self):
        return 'timedelta'

    @property
    def numpy_type_name(self):
        return 'timedelta64[ns]'


timedelta_index = TimedeltaIndexType()
types.timedelta_index = timedelta_index


@register_model(TimedeltaIndexType)
class TimedeltaIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cenq__mxgkc = [('data', _timedelta_index_data_typ), ('name',
            fe_type.name_typ), ('dict', types.DictType(
            _timedelta_index_data_typ.dtype, types.int64))]
        super(TimedeltaIndexTypeModel, self).__init__(dmm, fe_type, cenq__mxgkc
            )


@typeof_impl.register(pd.TimedeltaIndex)
def typeof_timedelta_index(val, c):
    return TimedeltaIndexType(get_val_type_maybe_str_literal(val.name))


@box(TimedeltaIndexType)
def box_timedelta_index(typ, val, c):
    yivl__nyv = c.context.insert_const_string(c.builder.module, 'pandas')
    xfcit__aeqfb = c.pyapi.import_module_noblock(yivl__nyv)
    timedelta_index = numba.core.cgutils.create_struct_proxy(typ)(c.context,
        c.builder, val)
    c.context.nrt.incref(c.builder, _timedelta_index_data_typ,
        timedelta_index.data)
    jii__jxsk = c.pyapi.from_native_value(_timedelta_index_data_typ,
        timedelta_index.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, timedelta_index.name)
    efdj__nyeu = c.pyapi.from_native_value(typ.name_typ, timedelta_index.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([jii__jxsk])
    kws = c.pyapi.dict_pack([('name', efdj__nyeu)])
    gxicf__xfz = c.pyapi.object_getattr_string(xfcit__aeqfb, 'TimedeltaIndex')
    syaaj__fwv = c.pyapi.call(gxicf__xfz, args, kws)
    c.pyapi.decref(jii__jxsk)
    c.pyapi.decref(efdj__nyeu)
    c.pyapi.decref(xfcit__aeqfb)
    c.pyapi.decref(gxicf__xfz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return syaaj__fwv


@unbox(TimedeltaIndexType)
def unbox_timedelta_index(typ, val, c):
    udqb__lqx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_timedelta_index_data_typ, udqb__lqx).value
    efdj__nyeu = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, efdj__nyeu).value
    c.pyapi.decref(udqb__lqx)
    c.pyapi.decref(efdj__nyeu)
    ppov__bdkyw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ppov__bdkyw.data = data
    ppov__bdkyw.name = name
    dtype = _timedelta_index_data_typ.dtype
    gzb__tdi, amj__kzh = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    ppov__bdkyw.dict = amj__kzh
    return NativeValue(ppov__bdkyw._getvalue())


@intrinsic
def init_timedelta_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        htv__bhdkf, wlbfx__ghvx = args
        timedelta_index = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        timedelta_index.data = htv__bhdkf
        timedelta_index.name = wlbfx__ghvx
        context.nrt.incref(builder, signature.args[0], htv__bhdkf)
        context.nrt.incref(builder, signature.args[1], wlbfx__ghvx)
        dtype = _timedelta_index_data_typ.dtype
        timedelta_index.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return timedelta_index._getvalue()
    kudmz__cih = TimedeltaIndexType(name)
    sig = signature(kudmz__cih, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_timedelta_index
    ) = init_index_equiv


@infer_getattr
class TimedeltaIndexAttribute(AttributeTemplate):
    key = TimedeltaIndexType

    def resolve_values(self, ary):
        return _timedelta_index_data_typ


make_attribute_wrapper(TimedeltaIndexType, 'data', '_data')
make_attribute_wrapper(TimedeltaIndexType, 'name', '_name')
make_attribute_wrapper(TimedeltaIndexType, 'dict', '_dict')


@overload_method(TimedeltaIndexType, 'copy', no_unliteral=True)
def overload_timedelta_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    sjx__dli = dict(deep=deep, dtype=dtype, names=names)
    siqq__hago = idx_typ_to_format_str_map[TimedeltaIndexType].format('copy()')
    check_unsupported_args('TimedeltaIndex.copy', sjx__dli,
        idx_cpy_arg_defaults, fn_str=siqq__hago, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), A._name)
    return impl


@overload_method(TimedeltaIndexType, 'min', inline='always', no_unliteral=True)
def overload_timedelta_index_min(tdi, axis=None, skipna=True):
    vwgld__zch = dict(axis=axis, skipna=skipna)
    vrsnf__bgvf = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.min', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        sadat__mquh = len(data)
        uoi__fdrow = numba.cpython.builtins.get_type_max_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(sadat__mquh):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            uoi__fdrow = min(uoi__fdrow, val)
        bmjxr__akgat = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            uoi__fdrow)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(bmjxr__akgat, count
            )
    return impl


@overload_method(TimedeltaIndexType, 'max', inline='always', no_unliteral=True)
def overload_timedelta_index_max(tdi, axis=None, skipna=True):
    vwgld__zch = dict(axis=axis, skipna=skipna)
    vrsnf__bgvf = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.max', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    if not is_overload_none(axis) or not is_overload_true(skipna):
        raise BodoError(
            'Index.min(): axis and skipna arguments not supported yet')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        sadat__mquh = len(data)
        hsa__pohh = numba.cpython.builtins.get_type_min_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(sadat__mquh):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            hsa__pohh = max(hsa__pohh, val)
        bmjxr__akgat = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            hsa__pohh)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(bmjxr__akgat, count
            )
    return impl


def gen_tdi_field_impl(field):
    btrw__gkmt = 'def impl(tdi):\n'
    btrw__gkmt += '    numba.parfors.parfor.init_prange()\n'
    btrw__gkmt += '    A = bodo.hiframes.pd_index_ext.get_index_data(tdi)\n'
    btrw__gkmt += '    name = bodo.hiframes.pd_index_ext.get_index_name(tdi)\n'
    btrw__gkmt += '    n = len(A)\n'
    btrw__gkmt += '    S = np.empty(n, np.int64)\n'
    btrw__gkmt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    btrw__gkmt += (
        '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
        )
    if field == 'nanoseconds':
        btrw__gkmt += '        S[i] = td64 % 1000\n'
    elif field == 'microseconds':
        btrw__gkmt += '        S[i] = td64 // 1000 % 100000\n'
    elif field == 'seconds':
        btrw__gkmt += (
            '        S[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
    elif field == 'days':
        btrw__gkmt += (
            '        S[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
    else:
        assert False, 'invalid timedelta field'
    btrw__gkmt += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    hzehy__rpxwo = {}
    exec(btrw__gkmt, {'numba': numba, 'np': np, 'bodo': bodo}, hzehy__rpxwo)
    impl = hzehy__rpxwo['impl']
    return impl


def _install_tdi_time_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        impl = gen_tdi_field_impl(field)
        overload_attribute(TimedeltaIndexType, field)(lambda tdi: impl)


_install_tdi_time_fields()


@overload(pd.TimedeltaIndex, no_unliteral=True)
def pd_timedelta_index_overload(data=None, unit=None, freq=None, dtype=None,
    copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.TimedeltaIndex() expected')
    vwgld__zch = dict(unit=unit, freq=freq, dtype=dtype, copy=copy)
    vrsnf__bgvf = dict(unit=None, freq=None, dtype=None, copy=False)
    check_unsupported_args('pandas.TimedeltaIndex', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')

    def impl(data=None, unit=None, freq=None, dtype=None, copy=False, name=None
        ):
        ylxbv__rgsp = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_td64ns(ylxbv__rgsp)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return impl


class RangeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None):
        if name_typ is None:
            name_typ = types.none
        self.name_typ = name_typ
        super(RangeIndexType, self).__init__(name='RangeIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return RangeIndexType(self.name_typ)

    @property
    def iterator_type(self):
        return types.iterators.RangeIteratorType(types.int64)

    @property
    def dtype(self):
        return types.int64

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)

    def unify(self, typingctx, other):
        if isinstance(other, NumericIndexType):
            name_typ = self.name_typ.unify(typingctx, other.name_typ)
            if name_typ is None:
                name_typ = types.none
            return NumericIndexType(types.int64, name_typ)


@typeof_impl.register(pd.RangeIndex)
def typeof_pd_range_index(val, c):
    return RangeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(RangeIndexType)
class RangeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cenq__mxgkc = [('start', types.int64), ('stop', types.int64), (
            'step', types.int64), ('name', fe_type.name_typ)]
        super(RangeIndexModel, self).__init__(dmm, fe_type, cenq__mxgkc)


make_attribute_wrapper(RangeIndexType, 'start', '_start')
make_attribute_wrapper(RangeIndexType, 'stop', '_stop')
make_attribute_wrapper(RangeIndexType, 'step', '_step')
make_attribute_wrapper(RangeIndexType, 'name', '_name')


@overload_method(RangeIndexType, 'copy', no_unliteral=True)
def overload_range_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    sjx__dli = dict(deep=deep, dtype=dtype, names=names)
    siqq__hago = idx_typ_to_format_str_map[RangeIndexType].format('copy()')
    check_unsupported_args('RangeIndex.copy', sjx__dli,
        idx_cpy_arg_defaults, fn_str=siqq__hago, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, A._name)
    return impl


@box(RangeIndexType)
def box_range_index(typ, val, c):
    yivl__nyv = c.context.insert_const_string(c.builder.module, 'pandas')
    tybl__vzu = c.pyapi.import_module_noblock(yivl__nyv)
    xxz__gwtb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    aoz__pbwg = c.pyapi.from_native_value(types.int64, xxz__gwtb.start, c.
        env_manager)
    soeqz__cpt = c.pyapi.from_native_value(types.int64, xxz__gwtb.stop, c.
        env_manager)
    ives__uiqx = c.pyapi.from_native_value(types.int64, xxz__gwtb.step, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, xxz__gwtb.name)
    efdj__nyeu = c.pyapi.from_native_value(typ.name_typ, xxz__gwtb.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([aoz__pbwg, soeqz__cpt, ives__uiqx])
    kws = c.pyapi.dict_pack([('name', efdj__nyeu)])
    gxicf__xfz = c.pyapi.object_getattr_string(tybl__vzu, 'RangeIndex')
    ckiy__vhxlr = c.pyapi.call(gxicf__xfz, args, kws)
    c.pyapi.decref(aoz__pbwg)
    c.pyapi.decref(soeqz__cpt)
    c.pyapi.decref(ives__uiqx)
    c.pyapi.decref(efdj__nyeu)
    c.pyapi.decref(tybl__vzu)
    c.pyapi.decref(gxicf__xfz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return ckiy__vhxlr


@intrinsic
def init_range_index(typingctx, start, stop, step, name=None):
    name = types.none if name is None else name
    fjy__arvp = is_overload_constant_int(step) and get_overload_const_int(step
        ) == 0

    def codegen(context, builder, signature, args):
        assert len(args) == 4
        if fjy__arvp:
            raise_bodo_error('Step must not be zero')
        vgl__hohs = cgutils.is_scalar_zero(builder, args[2])
        ngw__gkqrz = context.get_python_api(builder)
        with builder.if_then(vgl__hohs):
            ngw__gkqrz.err_format('PyExc_ValueError', 'Step must not be zero')
            val = context.get_constant(types.int32, -1)
            builder.ret(val)
        xxz__gwtb = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        xxz__gwtb.start = args[0]
        xxz__gwtb.stop = args[1]
        xxz__gwtb.step = args[2]
        xxz__gwtb.name = args[3]
        context.nrt.incref(builder, signature.return_type.name_typ, args[3])
        return xxz__gwtb._getvalue()
    return RangeIndexType(name)(start, stop, step, name), codegen


def init_range_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    start, stop, step, eey__rzg = args
    if self.typemap[start.name] == types.IntegerLiteral(0) and self.typemap[
        step.name] == types.IntegerLiteral(1) and equiv_set.has_shape(stop):
        return ArrayAnalysis.AnalyzeResult(shape=stop, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_range_index
    ) = init_range_index_equiv


@unbox(RangeIndexType)
def unbox_range_index(typ, val, c):
    aoz__pbwg = c.pyapi.object_getattr_string(val, 'start')
    start = c.pyapi.to_native_value(types.int64, aoz__pbwg).value
    soeqz__cpt = c.pyapi.object_getattr_string(val, 'stop')
    stop = c.pyapi.to_native_value(types.int64, soeqz__cpt).value
    ives__uiqx = c.pyapi.object_getattr_string(val, 'step')
    step = c.pyapi.to_native_value(types.int64, ives__uiqx).value
    efdj__nyeu = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, efdj__nyeu).value
    c.pyapi.decref(aoz__pbwg)
    c.pyapi.decref(soeqz__cpt)
    c.pyapi.decref(ives__uiqx)
    c.pyapi.decref(efdj__nyeu)
    xxz__gwtb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xxz__gwtb.start = start
    xxz__gwtb.stop = stop
    xxz__gwtb.step = step
    xxz__gwtb.name = name
    return NativeValue(xxz__gwtb._getvalue())


@lower_constant(RangeIndexType)
def lower_constant_range_index(context, builder, ty, pyval):
    start = context.get_constant(types.int64, pyval.start)
    stop = context.get_constant(types.int64, pyval.stop)
    step = context.get_constant(types.int64, pyval.step)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    return lir.Constant.literal_struct([start, stop, step, name])


@overload(pd.RangeIndex, no_unliteral=True, inline='always')
def range_index_overload(start=None, stop=None, step=None, dtype=None, copy
    =False, name=None):

    def _ensure_int_or_none(value, field):
        ogrvm__gvfm = (
            'RangeIndex(...) must be called with integers, {value} was passed for {field}'
            )
        if not is_overload_none(value) and not isinstance(value, types.
            IntegerLiteral) and not isinstance(value, types.Integer):
            raise BodoError(ogrvm__gvfm.format(value=value, field=field))
    _ensure_int_or_none(start, 'start')
    _ensure_int_or_none(stop, 'stop')
    _ensure_int_or_none(step, 'step')
    if is_overload_none(start) and is_overload_none(stop) and is_overload_none(
        step):
        ogrvm__gvfm = 'RangeIndex(...) must be called with integers'
        raise BodoError(ogrvm__gvfm)
    cdti__nasak = 'start'
    xau__zvxdf = 'stop'
    ysfcw__eiq = 'step'
    if is_overload_none(start):
        cdti__nasak = '0'
    if is_overload_none(stop):
        xau__zvxdf = 'start'
        cdti__nasak = '0'
    if is_overload_none(step):
        ysfcw__eiq = '1'
    btrw__gkmt = """def _pd_range_index_imp(start=None, stop=None, step=None, dtype=None, copy=False, name=None):
"""
    btrw__gkmt += '  return init_range_index({}, {}, {}, name)\n'.format(
        cdti__nasak, xau__zvxdf, ysfcw__eiq)
    hzehy__rpxwo = {}
    exec(btrw__gkmt, {'init_range_index': init_range_index}, hzehy__rpxwo)
    ghsk__nzkl = hzehy__rpxwo['_pd_range_index_imp']
    return ghsk__nzkl


@overload(pd.CategoricalIndex, no_unliteral=True, inline='always')
def categorical_index_overload(data=None, categories=None, ordered=None,
    dtype=None, copy=False, name=None):
    raise BodoError('pd.CategoricalIndex() initializer not yet supported.')


@overload_attribute(RangeIndexType, 'start')
def rangeIndex_get_start(ri):

    def impl(ri):
        return ri._start
    return impl


@overload_attribute(RangeIndexType, 'stop')
def rangeIndex_get_stop(ri):

    def impl(ri):
        return ri._stop
    return impl


@overload_attribute(RangeIndexType, 'step')
def rangeIndex_get_step(ri):

    def impl(ri):
        return ri._step
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_range_index_getitem(I, idx):
    if isinstance(I, RangeIndexType):
        if isinstance(types.unliteral(idx), types.Integer):
            return lambda I, idx: idx * I._step + I._start
        if isinstance(idx, types.SliceType):

            def impl(I, idx):
                musop__muilx = numba.cpython.unicode._normalize_slice(idx,
                    len(I))
                name = bodo.hiframes.pd_index_ext.get_index_name(I)
                start = I._start + I._step * musop__muilx.start
                stop = I._start + I._step * musop__muilx.stop
                step = I._step * musop__muilx.step
                return bodo.hiframes.pd_index_ext.init_range_index(start,
                    stop, step, name)
            return impl
        return lambda I, idx: bodo.hiframes.pd_index_ext.init_numeric_index(np
            .arange(I._start, I._stop, I._step, np.int64)[idx], bodo.
            hiframes.pd_index_ext.get_index_name(I))


@overload(len, no_unliteral=True)
def overload_range_len(r):
    if isinstance(r, RangeIndexType):
        return lambda r: max(0, -(-(r._stop - r._start) // r._step))


class PeriodIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, freq, name_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.freq = freq
        self.name_typ = name_typ
        super(PeriodIndexType, self).__init__(name=
            'PeriodIndexType({}, {})'.format(freq, name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return PeriodIndexType(self.freq, self.name_typ)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'period[{self.freq}]'


@typeof_impl.register(pd.PeriodIndex)
def typeof_pd_period_index(val, c):
    return PeriodIndexType(val.freqstr, get_val_type_maybe_str_literal(val.
        name))


@register_model(PeriodIndexType)
class PeriodIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cenq__mxgkc = [('data', bodo.IntegerArrayType(types.int64)), (
            'name', fe_type.name_typ), ('dict', types.DictType(types.int64,
            types.int64))]
        super(PeriodIndexModel, self).__init__(dmm, fe_type, cenq__mxgkc)


make_attribute_wrapper(PeriodIndexType, 'data', '_data')
make_attribute_wrapper(PeriodIndexType, 'name', '_name')
make_attribute_wrapper(PeriodIndexType, 'dict', '_dict')


@overload_method(PeriodIndexType, 'copy', no_unliteral=True)
def overload_period_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    freq = A.freq
    sjx__dli = dict(deep=deep, dtype=dtype, names=names)
    siqq__hago = idx_typ_to_format_str_map[PeriodIndexType].format('copy()')
    check_unsupported_args('PeriodIndex.copy', sjx__dli,
        idx_cpy_arg_defaults, fn_str=siqq__hago, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), name, freq)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), A._name, freq)
    return impl


@intrinsic
def init_period_index(typingctx, data, name, freq):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        htv__bhdkf, wlbfx__ghvx, eey__rzg = args
        mmjg__cpd = signature.return_type
        ktxgo__qyx = cgutils.create_struct_proxy(mmjg__cpd)(context, builder)
        ktxgo__qyx.data = htv__bhdkf
        ktxgo__qyx.name = wlbfx__ghvx
        context.nrt.incref(builder, signature.args[0], args[0])
        context.nrt.incref(builder, signature.args[1], args[1])
        ktxgo__qyx.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(types.int64, types.int64), types.DictType(
            types.int64, types.int64)(), [])
        return ktxgo__qyx._getvalue()
    ptc__iycha = get_overload_const_str(freq)
    kudmz__cih = PeriodIndexType(ptc__iycha, name)
    sig = signature(kudmz__cih, data, name, freq)
    return sig, codegen


@box(PeriodIndexType)
def box_period_index(typ, val, c):
    yivl__nyv = c.context.insert_const_string(c.builder.module, 'pandas')
    tybl__vzu = c.pyapi.import_module_noblock(yivl__nyv)
    ppov__bdkyw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, bodo.IntegerArrayType(types.int64),
        ppov__bdkyw.data)
    ctsu__qlbp = c.pyapi.from_native_value(bodo.IntegerArrayType(types.
        int64), ppov__bdkyw.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ppov__bdkyw.name)
    efdj__nyeu = c.pyapi.from_native_value(typ.name_typ, ppov__bdkyw.name,
        c.env_manager)
    vpex__wrivx = c.pyapi.string_from_constant_string(typ.freq)
    args = c.pyapi.tuple_pack([])
    kws = c.pyapi.dict_pack([('ordinal', ctsu__qlbp), ('name', efdj__nyeu),
        ('freq', vpex__wrivx)])
    gxicf__xfz = c.pyapi.object_getattr_string(tybl__vzu, 'PeriodIndex')
    ckiy__vhxlr = c.pyapi.call(gxicf__xfz, args, kws)
    c.pyapi.decref(ctsu__qlbp)
    c.pyapi.decref(efdj__nyeu)
    c.pyapi.decref(vpex__wrivx)
    c.pyapi.decref(tybl__vzu)
    c.pyapi.decref(gxicf__xfz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return ckiy__vhxlr


@unbox(PeriodIndexType)
def unbox_period_index(typ, val, c):
    arr_typ = bodo.IntegerArrayType(types.int64)
    brnx__jkhr = c.pyapi.object_getattr_string(val, 'asi8')
    ugbv__gxqua = c.pyapi.call_method(val, 'isna', ())
    efdj__nyeu = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, efdj__nyeu).value
    yivl__nyv = c.context.insert_const_string(c.builder.module, 'pandas')
    xfcit__aeqfb = c.pyapi.import_module_noblock(yivl__nyv)
    wyd__izgfg = c.pyapi.object_getattr_string(xfcit__aeqfb, 'arrays')
    ctsu__qlbp = c.pyapi.call_method(wyd__izgfg, 'IntegerArray', (
        brnx__jkhr, ugbv__gxqua))
    data = c.pyapi.to_native_value(arr_typ, ctsu__qlbp).value
    c.pyapi.decref(brnx__jkhr)
    c.pyapi.decref(ugbv__gxqua)
    c.pyapi.decref(efdj__nyeu)
    c.pyapi.decref(xfcit__aeqfb)
    c.pyapi.decref(wyd__izgfg)
    c.pyapi.decref(ctsu__qlbp)
    ppov__bdkyw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ppov__bdkyw.data = data
    ppov__bdkyw.name = name
    gzb__tdi, amj__kzh = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(types.int64, types.int64), types.DictType(types.int64, types.
        int64)(), [])
    ppov__bdkyw.dict = amj__kzh
    return NativeValue(ppov__bdkyw._getvalue())


class CategoricalIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
        assert isinstance(data, CategoricalArrayType
            ), 'CategoricalIndexType expects CategoricalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(CategoricalIndexType, self).__init__(name=
            f'CategoricalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return CategoricalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'categorical'

    @property
    def numpy_type_name(self):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        return str(get_categories_int_type(self.dtype))

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, self.dtype.elem_type)


@register_model(CategoricalIndexType)
class CategoricalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        ljfe__qsssl = get_categories_int_type(fe_type.data.dtype)
        cenq__mxgkc = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(ljfe__qsssl, types.int64))]
        super(CategoricalIndexTypeModel, self).__init__(dmm, fe_type,
            cenq__mxgkc)


@typeof_impl.register(pd.CategoricalIndex)
def typeof_categorical_index(val, c):
    return CategoricalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(CategoricalIndexType)
def box_categorical_index(typ, val, c):
    yivl__nyv = c.context.insert_const_string(c.builder.module, 'pandas')
    xfcit__aeqfb = c.pyapi.import_module_noblock(yivl__nyv)
    jnyvo__knvi = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, jnyvo__knvi.data)
    jii__jxsk = c.pyapi.from_native_value(typ.data, jnyvo__knvi.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, jnyvo__knvi.name)
    efdj__nyeu = c.pyapi.from_native_value(typ.name_typ, jnyvo__knvi.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([jii__jxsk])
    kws = c.pyapi.dict_pack([('name', efdj__nyeu)])
    gxicf__xfz = c.pyapi.object_getattr_string(xfcit__aeqfb, 'CategoricalIndex'
        )
    syaaj__fwv = c.pyapi.call(gxicf__xfz, args, kws)
    c.pyapi.decref(jii__jxsk)
    c.pyapi.decref(efdj__nyeu)
    c.pyapi.decref(xfcit__aeqfb)
    c.pyapi.decref(gxicf__xfz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return syaaj__fwv


@unbox(CategoricalIndexType)
def unbox_categorical_index(typ, val, c):
    from bodo.hiframes.pd_categorical_ext import get_categories_int_type
    udqb__lqx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, udqb__lqx).value
    efdj__nyeu = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, efdj__nyeu).value
    c.pyapi.decref(udqb__lqx)
    c.pyapi.decref(efdj__nyeu)
    ppov__bdkyw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ppov__bdkyw.data = data
    ppov__bdkyw.name = name
    dtype = get_categories_int_type(typ.data.dtype)
    gzb__tdi, amj__kzh = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    ppov__bdkyw.dict = amj__kzh
    return NativeValue(ppov__bdkyw._getvalue())


@intrinsic
def init_categorical_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        htv__bhdkf, wlbfx__ghvx = args
        jnyvo__knvi = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        jnyvo__knvi.data = htv__bhdkf
        jnyvo__knvi.name = wlbfx__ghvx
        context.nrt.incref(builder, signature.args[0], htv__bhdkf)
        context.nrt.incref(builder, signature.args[1], wlbfx__ghvx)
        dtype = get_categories_int_type(signature.return_type.data.dtype)
        jnyvo__knvi.dict = context.compile_internal(builder, lambda : numba
            .typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return jnyvo__knvi._getvalue()
    kudmz__cih = CategoricalIndexType(data, name)
    sig = signature(kudmz__cih, data, name)
    return sig, codegen


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_categorical_index
    ) = init_index_equiv
make_attribute_wrapper(CategoricalIndexType, 'data', '_data')
make_attribute_wrapper(CategoricalIndexType, 'name', '_name')
make_attribute_wrapper(CategoricalIndexType, 'dict', '_dict')


@overload_method(CategoricalIndexType, 'copy', no_unliteral=True)
def overload_categorical_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    siqq__hago = idx_typ_to_format_str_map[CategoricalIndexType].format(
        'copy()')
    sjx__dli = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('CategoricalIndex.copy', sjx__dli,
        idx_cpy_arg_defaults, fn_str=siqq__hago, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), A._name)
    return impl


class IntervalIndexType(types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.libs.interval_arr_ext import IntervalArrayType
        assert isinstance(data, IntervalArrayType
            ), 'IntervalIndexType expects IntervalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(IntervalIndexType, self).__init__(name=
            f'IntervalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return IntervalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'interval[{self.data.arr_type.dtype}, right]'


@register_model(IntervalIndexType)
class IntervalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cenq__mxgkc = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(types.UniTuple(fe_type.data.arr_type.
            dtype, 2), types.int64))]
        super(IntervalIndexTypeModel, self).__init__(dmm, fe_type, cenq__mxgkc)


@typeof_impl.register(pd.IntervalIndex)
def typeof_interval_index(val, c):
    return IntervalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(IntervalIndexType)
def box_interval_index(typ, val, c):
    yivl__nyv = c.context.insert_const_string(c.builder.module, 'pandas')
    xfcit__aeqfb = c.pyapi.import_module_noblock(yivl__nyv)
    mzj__rkt = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, mzj__rkt.data)
    jii__jxsk = c.pyapi.from_native_value(typ.data, mzj__rkt.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, mzj__rkt.name)
    efdj__nyeu = c.pyapi.from_native_value(typ.name_typ, mzj__rkt.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([jii__jxsk])
    kws = c.pyapi.dict_pack([('name', efdj__nyeu)])
    gxicf__xfz = c.pyapi.object_getattr_string(xfcit__aeqfb, 'IntervalIndex')
    syaaj__fwv = c.pyapi.call(gxicf__xfz, args, kws)
    c.pyapi.decref(jii__jxsk)
    c.pyapi.decref(efdj__nyeu)
    c.pyapi.decref(xfcit__aeqfb)
    c.pyapi.decref(gxicf__xfz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return syaaj__fwv


@unbox(IntervalIndexType)
def unbox_interval_index(typ, val, c):
    udqb__lqx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, udqb__lqx).value
    efdj__nyeu = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, efdj__nyeu).value
    c.pyapi.decref(udqb__lqx)
    c.pyapi.decref(efdj__nyeu)
    ppov__bdkyw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ppov__bdkyw.data = data
    ppov__bdkyw.name = name
    dtype = types.UniTuple(typ.data.arr_type.dtype, 2)
    gzb__tdi, amj__kzh = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    ppov__bdkyw.dict = amj__kzh
    return NativeValue(ppov__bdkyw._getvalue())


@intrinsic
def init_interval_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        htv__bhdkf, wlbfx__ghvx = args
        mzj__rkt = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        mzj__rkt.data = htv__bhdkf
        mzj__rkt.name = wlbfx__ghvx
        context.nrt.incref(builder, signature.args[0], htv__bhdkf)
        context.nrt.incref(builder, signature.args[1], wlbfx__ghvx)
        dtype = types.UniTuple(data.arr_type.dtype, 2)
        mzj__rkt.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return mzj__rkt._getvalue()
    kudmz__cih = IntervalIndexType(data, name)
    sig = signature(kudmz__cih, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_interval_index
    ) = init_index_equiv
make_attribute_wrapper(IntervalIndexType, 'data', '_data')
make_attribute_wrapper(IntervalIndexType, 'name', '_name')
make_attribute_wrapper(IntervalIndexType, 'dict', '_dict')


class NumericIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, dtype, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.dtype = dtype
        self.name_typ = name_typ
        data = dtype_to_array_type(dtype) if data is None else data
        self.data = data
        super(NumericIndexType, self).__init__(name=
            f'NumericIndexType({dtype}, {name_typ}, {data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return NumericIndexType(self.dtype, self.name_typ, self.data)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)


with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    Int64Index = pd.Int64Index
    UInt64Index = pd.UInt64Index
    Float64Index = pd.Float64Index


@typeof_impl.register(Int64Index)
def typeof_pd_int64_index(val, c):
    return NumericIndexType(types.int64, get_val_type_maybe_str_literal(val
        .name))


@typeof_impl.register(UInt64Index)
def typeof_pd_uint64_index(val, c):
    return NumericIndexType(types.uint64, get_val_type_maybe_str_literal(
        val.name))


@typeof_impl.register(Float64Index)
def typeof_pd_float64_index(val, c):
    return NumericIndexType(types.float64, get_val_type_maybe_str_literal(
        val.name))


@register_model(NumericIndexType)
class NumericIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cenq__mxgkc = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(fe_type.dtype, types.int64))]
        super(NumericIndexModel, self).__init__(dmm, fe_type, cenq__mxgkc)


make_attribute_wrapper(NumericIndexType, 'data', '_data')
make_attribute_wrapper(NumericIndexType, 'name', '_name')
make_attribute_wrapper(NumericIndexType, 'dict', '_dict')


@overload_method(NumericIndexType, 'copy', no_unliteral=True)
def overload_numeric_index_copy(A, name=None, deep=False, dtype=None, names
    =None):
    siqq__hago = idx_typ_to_format_str_map[NumericIndexType].format('copy()')
    sjx__dli = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', sjx__dli, idx_cpy_arg_defaults,
        fn_str=siqq__hago, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(NumericIndexType)
def box_numeric_index(typ, val, c):
    yivl__nyv = c.context.insert_const_string(c.builder.module, 'pandas')
    tybl__vzu = c.pyapi.import_module_noblock(yivl__nyv)
    ppov__bdkyw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, ppov__bdkyw.data)
    ctsu__qlbp = c.pyapi.from_native_value(typ.data, ppov__bdkyw.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ppov__bdkyw.name)
    efdj__nyeu = c.pyapi.from_native_value(typ.name_typ, ppov__bdkyw.name,
        c.env_manager)
    zdb__diyk = c.pyapi.make_none()
    cti__nbfkl = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    ckiy__vhxlr = c.pyapi.call_method(tybl__vzu, 'Index', (ctsu__qlbp,
        zdb__diyk, cti__nbfkl, efdj__nyeu))
    c.pyapi.decref(ctsu__qlbp)
    c.pyapi.decref(zdb__diyk)
    c.pyapi.decref(cti__nbfkl)
    c.pyapi.decref(efdj__nyeu)
    c.pyapi.decref(tybl__vzu)
    c.context.nrt.decref(c.builder, typ, val)
    return ckiy__vhxlr


@intrinsic
def init_numeric_index(typingctx, data, name=None):
    name = types.none if is_overload_none(name) else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        mmjg__cpd = signature.return_type
        ppov__bdkyw = cgutils.create_struct_proxy(mmjg__cpd)(context, builder)
        ppov__bdkyw.data = args[0]
        ppov__bdkyw.name = args[1]
        context.nrt.incref(builder, mmjg__cpd.data, args[0])
        context.nrt.incref(builder, mmjg__cpd.name_typ, args[1])
        dtype = mmjg__cpd.dtype
        ppov__bdkyw.dict = context.compile_internal(builder, lambda : numba
            .typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return ppov__bdkyw._getvalue()
    return NumericIndexType(data.dtype, name, data)(data, name), codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_numeric_index
    ) = init_index_equiv


@unbox(NumericIndexType)
def unbox_numeric_index(typ, val, c):
    udqb__lqx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, udqb__lqx).value
    efdj__nyeu = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, efdj__nyeu).value
    c.pyapi.decref(udqb__lqx)
    c.pyapi.decref(efdj__nyeu)
    ppov__bdkyw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ppov__bdkyw.data = data
    ppov__bdkyw.name = name
    dtype = typ.dtype
    gzb__tdi, amj__kzh = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    ppov__bdkyw.dict = amj__kzh
    return NativeValue(ppov__bdkyw._getvalue())


def create_numeric_constructor(func, func_str, default_dtype):

    def overload_impl(data=None, dtype=None, copy=False, name=None):
        qvx__bno = dict(dtype=dtype)
        sobia__odlel = dict(dtype=None)
        check_unsupported_args(func_str, qvx__bno, sobia__odlel,
            package_name='pandas', module_name='Index')
        if is_overload_false(copy):

            def impl(data=None, dtype=None, copy=False, name=None):
                ylxbv__rgsp = bodo.utils.conversion.coerce_to_ndarray(data)
                vkxh__sba = bodo.utils.conversion.fix_arr_dtype(ylxbv__rgsp,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(vkxh__sba,
                    name)
        else:

            def impl(data=None, dtype=None, copy=False, name=None):
                ylxbv__rgsp = bodo.utils.conversion.coerce_to_ndarray(data)
                if copy:
                    ylxbv__rgsp = ylxbv__rgsp.copy()
                vkxh__sba = bodo.utils.conversion.fix_arr_dtype(ylxbv__rgsp,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(vkxh__sba,
                    name)
        return impl
    return overload_impl


def _install_numeric_constructors():
    for func, func_str, default_dtype in ((Int64Index, 'pandas.Int64Index',
        np.int64), (UInt64Index, 'pandas.UInt64Index', np.uint64), (
        Float64Index, 'pandas.Float64Index', np.float64)):
        overload_impl = create_numeric_constructor(func, func_str,
            default_dtype)
        overload(func, no_unliteral=True)(overload_impl)


_install_numeric_constructors()


class StringIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = string_array_type if data_typ is None else data_typ
        super(StringIndexType, self).__init__(name=
            f'StringIndexType({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return StringIndexType(self.name_typ, self.data)

    @property
    def dtype(self):
        return string_type

    @property
    def pandas_type_name(self):
        return 'unicode'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


@register_model(StringIndexType)
class StringIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cenq__mxgkc = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(string_type, types.int64))]
        super(StringIndexModel, self).__init__(dmm, fe_type, cenq__mxgkc)


make_attribute_wrapper(StringIndexType, 'data', '_data')
make_attribute_wrapper(StringIndexType, 'name', '_name')
make_attribute_wrapper(StringIndexType, 'dict', '_dict')


class BinaryIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data_typ=None):
        assert data_typ is None or data_typ == binary_array_type, 'data_typ must be binary_array_type'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = binary_array_type
        super(BinaryIndexType, self).__init__(name='BinaryIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return BinaryIndexType(self.name_typ)

    @property
    def dtype(self):
        return bytes_type

    @property
    def pandas_type_name(self):
        return 'bytes'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


@register_model(BinaryIndexType)
class BinaryIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cenq__mxgkc = [('data', binary_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(bytes_type, types.int64))]
        super(BinaryIndexModel, self).__init__(dmm, fe_type, cenq__mxgkc)


make_attribute_wrapper(BinaryIndexType, 'data', '_data')
make_attribute_wrapper(BinaryIndexType, 'name', '_name')
make_attribute_wrapper(BinaryIndexType, 'dict', '_dict')


@unbox(BinaryIndexType)
@unbox(StringIndexType)
def unbox_binary_str_index(typ, val, c):
    qqsfs__vzj = typ.data
    scalar_type = typ.data.dtype
    udqb__lqx = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(qqsfs__vzj, udqb__lqx).value
    efdj__nyeu = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, efdj__nyeu).value
    c.pyapi.decref(udqb__lqx)
    c.pyapi.decref(efdj__nyeu)
    ppov__bdkyw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ppov__bdkyw.data = data
    ppov__bdkyw.name = name
    gzb__tdi, amj__kzh = c.pyapi.call_jit_code(lambda : numba.typed.Dict.
        empty(scalar_type, types.int64), types.DictType(scalar_type, types.
        int64)(), [])
    ppov__bdkyw.dict = amj__kzh
    return NativeValue(ppov__bdkyw._getvalue())


@box(BinaryIndexType)
@box(StringIndexType)
def box_binary_str_index(typ, val, c):
    qqsfs__vzj = typ.data
    yivl__nyv = c.context.insert_const_string(c.builder.module, 'pandas')
    tybl__vzu = c.pyapi.import_module_noblock(yivl__nyv)
    ppov__bdkyw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, qqsfs__vzj, ppov__bdkyw.data)
    ctsu__qlbp = c.pyapi.from_native_value(qqsfs__vzj, ppov__bdkyw.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ppov__bdkyw.name)
    efdj__nyeu = c.pyapi.from_native_value(typ.name_typ, ppov__bdkyw.name,
        c.env_manager)
    zdb__diyk = c.pyapi.make_none()
    cti__nbfkl = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    ckiy__vhxlr = c.pyapi.call_method(tybl__vzu, 'Index', (ctsu__qlbp,
        zdb__diyk, cti__nbfkl, efdj__nyeu))
    c.pyapi.decref(ctsu__qlbp)
    c.pyapi.decref(zdb__diyk)
    c.pyapi.decref(cti__nbfkl)
    c.pyapi.decref(efdj__nyeu)
    c.pyapi.decref(tybl__vzu)
    c.context.nrt.decref(c.builder, typ, val)
    return ckiy__vhxlr


@intrinsic
def init_binary_str_index(typingctx, data, name=None):
    name = types.none if name is None else name
    sig = type(bodo.utils.typing.get_index_type_from_dtype(data.dtype))(name,
        data)(data, name)
    vjuir__hxob = get_binary_str_codegen(is_binary=data.dtype == bytes_type)
    return sig, vjuir__hxob


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_binary_str_index
    ) = init_index_equiv


def get_binary_str_codegen(is_binary=False):
    if is_binary:
        sazuk__phstk = 'bytes_type'
    else:
        sazuk__phstk = 'string_type'
    btrw__gkmt = 'def impl(context, builder, signature, args):\n'
    btrw__gkmt += '    assert len(args) == 2\n'
    btrw__gkmt += '    index_typ = signature.return_type\n'
    btrw__gkmt += (
        '    index_val = cgutils.create_struct_proxy(index_typ)(context, builder)\n'
        )
    btrw__gkmt += '    index_val.data = args[0]\n'
    btrw__gkmt += '    index_val.name = args[1]\n'
    btrw__gkmt += '    # increase refcount of stored values\n'
    btrw__gkmt += (
        '    context.nrt.incref(builder, signature.args[0], args[0])\n')
    btrw__gkmt += (
        '    context.nrt.incref(builder, index_typ.name_typ, args[1])\n')
    btrw__gkmt += '    # create empty dict for get_loc hashmap\n'
    btrw__gkmt += '    index_val.dict = context.compile_internal(\n'
    btrw__gkmt += '       builder,\n'
    btrw__gkmt += (
        f'       lambda: numba.typed.Dict.empty({sazuk__phstk}, types.int64),\n'
        )
    btrw__gkmt += (
        f'        types.DictType({sazuk__phstk}, types.int64)(), [],)\n')
    btrw__gkmt += '    return index_val._getvalue()\n'
    hzehy__rpxwo = {}
    exec(btrw__gkmt, {'bodo': bodo, 'signature': signature, 'cgutils':
        cgutils, 'numba': numba, 'types': types, 'bytes_type': bytes_type,
        'string_type': string_type}, hzehy__rpxwo)
    impl = hzehy__rpxwo['impl']
    return impl


@overload_method(BinaryIndexType, 'copy', no_unliteral=True)
@overload_method(StringIndexType, 'copy', no_unliteral=True)
def overload_binary_string_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    typ = type(A)
    siqq__hago = idx_typ_to_format_str_map[typ].format('copy()')
    sjx__dli = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', sjx__dli, idx_cpy_arg_defaults,
        fn_str=siqq__hago, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), A._name)
    return impl


@overload_attribute(BinaryIndexType, 'name')
@overload_attribute(StringIndexType, 'name')
@overload_attribute(DatetimeIndexType, 'name')
@overload_attribute(TimedeltaIndexType, 'name')
@overload_attribute(RangeIndexType, 'name')
@overload_attribute(PeriodIndexType, 'name')
@overload_attribute(NumericIndexType, 'name')
@overload_attribute(IntervalIndexType, 'name')
@overload_attribute(CategoricalIndexType, 'name')
@overload_attribute(MultiIndexType, 'name')
def Index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_index_getitem(I, ind):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType)
        ) and isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, NumericIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_numeric_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))
    if isinstance(I, (StringIndexType, BinaryIndexType)):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_binary_str_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))


def array_type_to_index(arr_typ, name_typ=None):
    if is_str_arr_type(arr_typ):
        return StringIndexType(name_typ, arr_typ)
    if arr_typ == bodo.binary_array_type:
        return BinaryIndexType(name_typ)
    assert isinstance(arr_typ, (types.Array, IntegerArrayType, bodo.
        CategoricalArrayType)) or arr_typ in (bodo.datetime_date_array_type,
        bodo.boolean_array
        ), f'Converting array type {arr_typ} to index not supported'
    if (arr_typ == bodo.datetime_date_array_type or arr_typ.dtype == types.
        NPDatetime('ns')):
        return DatetimeIndexType(name_typ)
    if isinstance(arr_typ, bodo.DatetimeArrayType):
        return DatetimeIndexType(name_typ, arr_typ)
    if isinstance(arr_typ, bodo.CategoricalArrayType):
        return CategoricalIndexType(arr_typ, name_typ)
    if arr_typ.dtype == types.NPTimedelta('ns'):
        return TimedeltaIndexType(name_typ)
    if isinstance(arr_typ.dtype, (types.Integer, types.Float, types.Boolean)):
        return NumericIndexType(arr_typ.dtype, name_typ, arr_typ)
    raise BodoError(f'invalid index type {arr_typ}')


def is_pd_index_type(t):
    return isinstance(t, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType,
        PeriodIndexType, StringIndexType, BinaryIndexType, RangeIndexType,
        HeterogeneousIndexType))


def _verify_setop_compatible(func_name, I, other):
    if not is_pd_index_type(other) and not isinstance(other, (SeriesType,
        types.Array)):
        raise BodoError(
            f'pd.Index.{func_name}(): unsupported type for argument other: {other}'
            )
    frw__dpcg = I.dtype if not isinstance(I, RangeIndexType) else types.int64
    asgv__mlq = other.dtype if not isinstance(other, RangeIndexType
        ) else types.int64
    if frw__dpcg != asgv__mlq:
        raise BodoError(
            f'Index.{func_name}(): incompatible types {frw__dpcg} and {asgv__mlq}'
            )


@overload_method(NumericIndexType, 'union', inline='always')
@overload_method(StringIndexType, 'union', inline='always')
@overload_method(BinaryIndexType, 'union', inline='always')
@overload_method(DatetimeIndexType, 'union', inline='always')
@overload_method(TimedeltaIndexType, 'union', inline='always')
@overload_method(RangeIndexType, 'union', inline='always')
def overload_index_union(I, other, sort=None):
    vwgld__zch = dict(sort=sort)
    dyy__klza = dict(sort=None)
    check_unsupported_args('Index.union', vwgld__zch, dyy__klza,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('union', I, other)
    riny__rsp = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        qal__vdvai = bodo.utils.conversion.coerce_to_array(I)
        bxxgv__cghx = bodo.utils.conversion.coerce_to_array(other)
        tbdd__ybd = bodo.libs.array_kernels.concat([qal__vdvai, bxxgv__cghx])
        ixkf__fifgj = bodo.libs.array_kernels.unique(tbdd__ybd)
        return riny__rsp(ixkf__fifgj, None)
    return impl


@overload_method(NumericIndexType, 'intersection', inline='always')
@overload_method(StringIndexType, 'intersection', inline='always')
@overload_method(BinaryIndexType, 'intersection', inline='always')
@overload_method(DatetimeIndexType, 'intersection', inline='always')
@overload_method(TimedeltaIndexType, 'intersection', inline='always')
@overload_method(RangeIndexType, 'intersection', inline='always')
def overload_index_intersection(I, other, sort=None):
    vwgld__zch = dict(sort=sort)
    dyy__klza = dict(sort=None)
    check_unsupported_args('Index.intersection', vwgld__zch, dyy__klza,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('intersection', I, other)
    riny__rsp = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        qal__vdvai = bodo.utils.conversion.coerce_to_array(I)
        bxxgv__cghx = bodo.utils.conversion.coerce_to_array(other)
        nooe__oxy = bodo.libs.array_kernels.unique(qal__vdvai)
        oeu__medc = bodo.libs.array_kernels.unique(bxxgv__cghx)
        tbdd__ybd = bodo.libs.array_kernels.concat([nooe__oxy, oeu__medc])
        ghwe__bnwis = pd.Series(tbdd__ybd).sort_values().values
        ptyc__khzoh = bodo.libs.array_kernels.intersection_mask(ghwe__bnwis)
        return riny__rsp(ghwe__bnwis[ptyc__khzoh], None)
    return impl


@overload_method(NumericIndexType, 'difference', inline='always')
@overload_method(StringIndexType, 'difference', inline='always')
@overload_method(BinaryIndexType, 'difference', inline='always')
@overload_method(DatetimeIndexType, 'difference', inline='always')
@overload_method(TimedeltaIndexType, 'difference', inline='always')
@overload_method(RangeIndexType, 'difference', inline='always')
def overload_index_difference(I, other, sort=None):
    vwgld__zch = dict(sort=sort)
    dyy__klza = dict(sort=None)
    check_unsupported_args('Index.difference', vwgld__zch, dyy__klza,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('difference', I, other)
    riny__rsp = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        qal__vdvai = bodo.utils.conversion.coerce_to_array(I)
        bxxgv__cghx = bodo.utils.conversion.coerce_to_array(other)
        nooe__oxy = bodo.libs.array_kernels.unique(qal__vdvai)
        oeu__medc = bodo.libs.array_kernels.unique(bxxgv__cghx)
        ptyc__khzoh = np.empty(len(nooe__oxy), np.bool_)
        bodo.libs.array.array_isin(ptyc__khzoh, nooe__oxy, oeu__medc, False)
        return riny__rsp(nooe__oxy[~ptyc__khzoh], None)
    return impl


@overload_method(NumericIndexType, 'symmetric_difference', inline='always')
@overload_method(StringIndexType, 'symmetric_difference', inline='always')
@overload_method(BinaryIndexType, 'symmetric_difference', inline='always')
@overload_method(DatetimeIndexType, 'symmetric_difference', inline='always')
@overload_method(TimedeltaIndexType, 'symmetric_difference', inline='always')
@overload_method(RangeIndexType, 'symmetric_difference', inline='always')
def overload_index_symmetric_difference(I, other, result_name=None, sort=None):
    vwgld__zch = dict(result_name=result_name, sort=sort)
    dyy__klza = dict(result_name=None, sort=None)
    check_unsupported_args('Index.symmetric_difference', vwgld__zch,
        dyy__klza, package_name='pandas', module_name='Index')
    _verify_setop_compatible('symmetric_difference', I, other)
    riny__rsp = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, result_name=None, sort=None):
        qal__vdvai = bodo.utils.conversion.coerce_to_array(I)
        bxxgv__cghx = bodo.utils.conversion.coerce_to_array(other)
        nooe__oxy = bodo.libs.array_kernels.unique(qal__vdvai)
        oeu__medc = bodo.libs.array_kernels.unique(bxxgv__cghx)
        jxco__ixdsx = np.empty(len(nooe__oxy), np.bool_)
        ncqik__ppix = np.empty(len(oeu__medc), np.bool_)
        bodo.libs.array.array_isin(jxco__ixdsx, nooe__oxy, oeu__medc, False)
        bodo.libs.array.array_isin(ncqik__ppix, oeu__medc, nooe__oxy, False)
        lwfxd__teabh = bodo.libs.array_kernels.concat([nooe__oxy[~
            jxco__ixdsx], oeu__medc[~ncqik__ppix]])
        return riny__rsp(lwfxd__teabh, None)
    return impl


@overload_method(RangeIndexType, 'take', no_unliteral=True)
@overload_method(NumericIndexType, 'take', no_unliteral=True)
@overload_method(StringIndexType, 'take', no_unliteral=True)
@overload_method(BinaryIndexType, 'take', no_unliteral=True)
@overload_method(CategoricalIndexType, 'take', no_unliteral=True)
@overload_method(PeriodIndexType, 'take', no_unliteral=True)
@overload_method(DatetimeIndexType, 'take', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'take', no_unliteral=True)
def overload_index_take(I, indices, axis=0, allow_fill=True, fill_value=None):
    vwgld__zch = dict(axis=axis, allow_fill=allow_fill, fill_value=fill_value)
    dyy__klza = dict(axis=0, allow_fill=True, fill_value=None)
    check_unsupported_args('Index.take', vwgld__zch, dyy__klza,
        package_name='pandas', module_name='Index')
    return lambda I, indices: I[indices]


def _init_engine(I, ban_unique=True):
    pass


@overload(_init_engine)
def overload_init_engine(I, ban_unique=True):
    if isinstance(I, CategoricalIndexType):

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                irk__rekg = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(irk__rekg)):
                    if not bodo.libs.array_kernels.isna(irk__rekg, i):
                        val = (bodo.hiframes.pd_categorical_ext.
                            get_code_for_value(irk__rekg.dtype, irk__rekg[i]))
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl
    else:

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                irk__rekg = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(irk__rekg)):
                    if not bodo.libs.array_kernels.isna(irk__rekg, i):
                        val = irk__rekg[i]
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl


@overload(operator.contains, no_unliteral=True)
def index_contains(I, val):
    if not is_index_type(I):
        return
    if isinstance(I, RangeIndexType):
        return lambda I, val: range_contains(I.start, I.stop, I.step, val)
    if isinstance(I, CategoricalIndexType):

        def impl(I, val):
            key = bodo.utils.conversion.unbox_if_timestamp(val)
            if not is_null_value(I._dict):
                _init_engine(I, False)
                irk__rekg = bodo.utils.conversion.coerce_to_array(I)
                hzww__wccf = (bodo.hiframes.pd_categorical_ext.
                    get_code_for_value(irk__rekg.dtype, key))
                return hzww__wccf in I._dict
            else:
                ogrvm__gvfm = (
                    'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                    )
                warnings.warn(ogrvm__gvfm)
                irk__rekg = bodo.utils.conversion.coerce_to_array(I)
                ind = -1
                for i in range(len(irk__rekg)):
                    if not bodo.libs.array_kernels.isna(irk__rekg, i):
                        if irk__rekg[i] == key:
                            ind = i
            return ind != -1
        return impl

    def impl(I, val):
        key = bodo.utils.conversion.unbox_if_timestamp(val)
        if not is_null_value(I._dict):
            _init_engine(I, False)
            return key in I._dict
        else:
            ogrvm__gvfm = (
                'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                )
            warnings.warn(ogrvm__gvfm)
            irk__rekg = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(irk__rekg)):
                if not bodo.libs.array_kernels.isna(irk__rekg, i):
                    if irk__rekg[i] == key:
                        ind = i
        return ind != -1
    return impl


@register_jitable
def range_contains(start, stop, step, val):
    if step > 0 and not start <= val < stop:
        return False
    if step < 0 and not stop <= val < start:
        return False
    return (val - start) % step == 0


@overload_method(RangeIndexType, 'get_loc', no_unliteral=True)
@overload_method(NumericIndexType, 'get_loc', no_unliteral=True)
@overload_method(StringIndexType, 'get_loc', no_unliteral=True)
@overload_method(BinaryIndexType, 'get_loc', no_unliteral=True)
@overload_method(PeriodIndexType, 'get_loc', no_unliteral=True)
@overload_method(DatetimeIndexType, 'get_loc', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'get_loc', no_unliteral=True)
def overload_index_get_loc(I, key, method=None, tolerance=None):
    vwgld__zch = dict(method=method, tolerance=tolerance)
    vrsnf__bgvf = dict(method=None, tolerance=None)
    check_unsupported_args('Index.get_loc', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    key = types.unliteral(key)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'DatetimeIndex.get_loc')
    if key == pd_timestamp_type:
        key = bodo.datetime64ns
    if key == pd_timedelta_type:
        key = bodo.timedelta64ns
    if key != I.dtype:
        raise_bodo_error(
            'Index.get_loc(): invalid label type in Index.get_loc()')
    if isinstance(I, RangeIndexType):

        def impl_range(I, key, method=None, tolerance=None):
            if not range_contains(I.start, I.stop, I.step, key):
                raise KeyError('Index.get_loc(): key not found')
            return key - I.start if I.step == 1 else (key - I.start) // I.step
        return impl_range

    def impl(I, key, method=None, tolerance=None):
        key = bodo.utils.conversion.unbox_if_timestamp(key)
        if not is_null_value(I._dict):
            _init_engine(I)
            ind = I._dict.get(key, -1)
        else:
            ogrvm__gvfm = (
                'Index.get_loc() can be slow for global Index objects (pass as argument to JIT function for better performance).'
                )
            warnings.warn(ogrvm__gvfm)
            irk__rekg = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(irk__rekg)):
                if irk__rekg[i] == key:
                    if ind != -1:
                        raise ValueError(
                            'Index.get_loc(): non-unique Index not supported yet'
                            )
                    ind = i
        if ind == -1:
            raise KeyError('Index.get_loc(): key not found')
        return ind
    return impl


def create_isna_specific_method(overload_name):

    def overload_index_isna_specific_method(I):
        dvkpd__snxhu = overload_name in {'isna', 'isnull'}
        if isinstance(I, RangeIndexType):

            def impl(I):
                numba.parfors.parfor.init_prange()
                sadat__mquh = len(I)
                mko__ryy = np.empty(sadat__mquh, np.bool_)
                for i in numba.parfors.parfor.internal_prange(sadat__mquh):
                    mko__ryy[i] = not dvkpd__snxhu
                return mko__ryy
            return impl
        btrw__gkmt = f"""def impl(I):
    numba.parfors.parfor.init_prange()
    arr = bodo.hiframes.pd_index_ext.get_index_data(I)
    n = len(arr)
    out_arr = np.empty(n, np.bool_)
    for i in numba.parfors.parfor.internal_prange(n):
       out_arr[i] = {'' if dvkpd__snxhu else 'not '}bodo.libs.array_kernels.isna(arr, i)
    return out_arr
"""
        hzehy__rpxwo = {}
        exec(btrw__gkmt, {'bodo': bodo, 'np': np, 'numba': numba}, hzehy__rpxwo
            )
        impl = hzehy__rpxwo['impl']
        return impl
    return overload_index_isna_specific_method


isna_overload_types = (RangeIndexType, NumericIndexType, StringIndexType,
    BinaryIndexType, CategoricalIndexType, PeriodIndexType,
    DatetimeIndexType, TimedeltaIndexType)
isna_specific_methods = 'isna', 'notna', 'isnull', 'notnull'


def _install_isna_specific_methods():
    for qlel__xuag in isna_overload_types:
        for overload_name in isna_specific_methods:
            overload_impl = create_isna_specific_method(overload_name)
            overload_method(qlel__xuag, overload_name, no_unliteral=True,
                inline='always')(overload_impl)


_install_isna_specific_methods()


@overload_attribute(RangeIndexType, 'values')
@overload_attribute(NumericIndexType, 'values')
@overload_attribute(StringIndexType, 'values')
@overload_attribute(BinaryIndexType, 'values')
@overload_attribute(CategoricalIndexType, 'values')
@overload_attribute(PeriodIndexType, 'values')
@overload_attribute(DatetimeIndexType, 'values')
@overload_attribute(TimedeltaIndexType, 'values')
def overload_values(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I, 'Index.values'
        )
    return lambda I: bodo.utils.conversion.coerce_to_array(I)


@overload(len, no_unliteral=True)
def overload_index_len(I):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType,
        PeriodIndexType, IntervalIndexType, CategoricalIndexType,
        DatetimeIndexType, TimedeltaIndexType, HeterogeneousIndexType)):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I))


@overload(len, no_unliteral=True)
def overload_multi_index_len(I):
    if isinstance(I, MultiIndexType):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I)[0])


@overload_attribute(DatetimeIndexType, 'shape')
@overload_attribute(NumericIndexType, 'shape')
@overload_attribute(StringIndexType, 'shape')
@overload_attribute(BinaryIndexType, 'shape')
@overload_attribute(PeriodIndexType, 'shape')
@overload_attribute(TimedeltaIndexType, 'shape')
@overload_attribute(IntervalIndexType, 'shape')
@overload_attribute(CategoricalIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)),)


@overload_attribute(RangeIndexType, 'shape')
def overload_range_index_shape(s):
    return lambda s: (len(s),)


@overload_attribute(MultiIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)[0]),)


@overload_attribute(NumericIndexType, 'is_monotonic', inline='always')
@overload_attribute(RangeIndexType, 'is_monotonic', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic', inline='always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic', inline='always')
@overload_attribute(NumericIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_increasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_increasing', inline=
    'always')
def overload_index_is_montonic(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.is_monotonic_increasing')
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            irk__rekg = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(irk__rekg, 1)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step > 0 or len(I) <= 1
        return impl


@overload_attribute(NumericIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_decreasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_decreasing', inline=
    'always')
def overload_index_is_montonic_decreasing(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.is_monotonic_decreasing')
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            irk__rekg = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(irk__rekg, 2)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step < 0 or len(I) <= 1
        return impl


@overload_method(NumericIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(DatetimeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(TimedeltaIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(StringIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(PeriodIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(CategoricalIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(BinaryIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(RangeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
def overload_index_duplicated(I, keep='first'):
    if isinstance(I, RangeIndexType):

        def impl(I, keep='first'):
            return np.zeros(len(I), np.bool_)
        return impl

    def impl(I, keep='first'):
        irk__rekg = bodo.hiframes.pd_index_ext.get_index_data(I)
        mko__ryy = bodo.libs.array_kernels.duplicated((irk__rekg,))
        return mko__ryy
    return impl


@overload_method(NumericIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'any', no_unliteral=True, inline='always')
def overload_index_any(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            return len(I) > 0 and (I._start != 0 or len(I) > 1)
        return impl

    def impl(I):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_any(A)
    return impl


@overload_method(NumericIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'all', no_unliteral=True, inline='always')
def overload_index_all(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            return len(I) == 0 or I._step > 0 and (I._start > 0 or I._stop <= 0
                ) or I._step < 0 and (I._start < 0 or I._stop >= 0
                ) or I._start % I._step != 0
        return impl

    def impl(I):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(RangeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(NumericIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(StringIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(BinaryIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(CategoricalIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(PeriodIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
def overload_index_drop_duplicates(I, keep='first'):
    vwgld__zch = dict(keep=keep)
    vrsnf__bgvf = dict(keep='first')
    check_unsupported_args('Index.drop_duplicates', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):
        return lambda I, keep='first': I.copy()
    btrw__gkmt = """def impl(I, keep='first'):
    data = bodo.hiframes.pd_index_ext.get_index_data(I)
    arr = bodo.libs.array_kernels.drop_duplicates_array(data)
    name = bodo.hiframes.pd_index_ext.get_index_name(I)
"""
    if isinstance(I, PeriodIndexType):
        btrw__gkmt += f"""    return bodo.hiframes.pd_index_ext.init_period_index(arr, name, '{I.freq}')
"""
    else:
        btrw__gkmt += (
            '    return bodo.utils.conversion.index_from_array(arr, name)')
    hzehy__rpxwo = {}
    exec(btrw__gkmt, {'bodo': bodo}, hzehy__rpxwo)
    impl = hzehy__rpxwo['impl']
    return impl


@numba.generated_jit(nopython=True)
def get_index_data(S):
    return lambda S: S._data


@numba.generated_jit(nopython=True)
def get_index_name(S):
    return lambda S: S._name


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_index_data',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_datetime_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_timedelta_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_numeric_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_binary_str_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_categorical_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func


def get_index_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    cigz__jyuva = args[0]
    if isinstance(self.typemap[cigz__jyuva.name], (HeterogeneousIndexType,
        MultiIndexType)):
        return None
    if equiv_set.has_shape(cigz__jyuva):
        return ArrayAnalysis.AnalyzeResult(shape=cigz__jyuva, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_get_index_data
    ) = get_index_data_equiv


@overload_method(RangeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(NumericIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(StringIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(BinaryIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(CategoricalIndexType, 'map', inline='always', no_unliteral
    =True)
@overload_method(PeriodIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(DatetimeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'map', inline='always', no_unliteral=True)
def overload_index_map(I, mapper, na_action=None):
    if not is_const_func_type(mapper):
        raise BodoError("Index.map(): 'mapper' should be a function")
    vwgld__zch = dict(na_action=na_action)
    wtfm__wdto = dict(na_action=None)
    check_unsupported_args('Index.map', vwgld__zch, wtfm__wdto,
        package_name='pandas', module_name='Index')
    dtype = I.dtype
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'DatetimeIndex.map')
    if dtype == types.NPDatetime('ns'):
        dtype = pd_timestamp_type
    if dtype == types.NPTimedelta('ns'):
        dtype = pd_timedelta_type
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = dtype.elem_type
    dhz__cjuen = numba.core.registry.cpu_target.typing_context
    cgk__vpd = numba.core.registry.cpu_target.target_context
    try:
        lmjwc__xczn = get_const_func_output_type(mapper, (dtype,), {},
            dhz__cjuen, cgk__vpd)
    except Exception as miae__teqnk:
        raise_bodo_error(get_udf_error_msg('Index.map()', miae__teqnk))
    gttca__oqyy = get_udf_out_arr_type(lmjwc__xczn)
    func = get_overload_const_func(mapper, None)
    btrw__gkmt = 'def f(I, mapper, na_action=None):\n'
    btrw__gkmt += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    btrw__gkmt += '  A = bodo.utils.conversion.coerce_to_array(I)\n'
    btrw__gkmt += '  numba.parfors.parfor.init_prange()\n'
    btrw__gkmt += '  n = len(A)\n'
    btrw__gkmt += '  S = bodo.utils.utils.alloc_type(n, _arr_typ, (-1,))\n'
    btrw__gkmt += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    btrw__gkmt += '    t2 = bodo.utils.conversion.box_if_dt64(A[i])\n'
    btrw__gkmt += '    v = map_func(t2)\n'
    btrw__gkmt += '    S[i] = bodo.utils.conversion.unbox_if_timestamp(v)\n'
    btrw__gkmt += '  return bodo.utils.conversion.index_from_array(S, name)\n'
    wkopf__eiug = bodo.compiler.udf_jit(func)
    hzehy__rpxwo = {}
    exec(btrw__gkmt, {'numba': numba, 'np': np, 'pd': pd, 'bodo': bodo,
        'map_func': wkopf__eiug, '_arr_typ': gttca__oqyy,
        'init_nested_counts': bodo.utils.indexing.init_nested_counts,
        'add_nested_counts': bodo.utils.indexing.add_nested_counts,
        'data_arr_type': gttca__oqyy.dtype}, hzehy__rpxwo)
    f = hzehy__rpxwo['f']
    return f


@lower_builtin(operator.is_, NumericIndexType, NumericIndexType)
@lower_builtin(operator.is_, StringIndexType, StringIndexType)
@lower_builtin(operator.is_, BinaryIndexType, BinaryIndexType)
@lower_builtin(operator.is_, PeriodIndexType, PeriodIndexType)
@lower_builtin(operator.is_, DatetimeIndexType, DatetimeIndexType)
@lower_builtin(operator.is_, TimedeltaIndexType, TimedeltaIndexType)
@lower_builtin(operator.is_, IntervalIndexType, IntervalIndexType)
@lower_builtin(operator.is_, CategoricalIndexType, CategoricalIndexType)
def index_is(context, builder, sig, args):
    tqmzj__mahme, lstk__rlm = sig.args
    if tqmzj__mahme != lstk__rlm:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return a._data is b._data and a._name is b._name
    return context.compile_internal(builder, index_is_impl, sig, args)


@lower_builtin(operator.is_, RangeIndexType, RangeIndexType)
def range_index_is(context, builder, sig, args):
    tqmzj__mahme, lstk__rlm = sig.args
    if tqmzj__mahme != lstk__rlm:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._start == b._start and a._stop == b._stop and a._step ==
            b._step and a._name is b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)


def create_binary_op_overload(op):

    def overload_index_binary_op(lhs, rhs):
        if is_index_type(lhs):
            btrw__gkmt = """def impl(lhs, rhs):
  arr = bodo.utils.conversion.coerce_to_array(lhs)
"""
            if rhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                btrw__gkmt += """  dt = bodo.utils.conversion.unbox_if_timestamp(rhs)
  return op(arr, dt)
"""
            else:
                btrw__gkmt += """  rhs_arr = bodo.utils.conversion.get_array_if_series_or_index(rhs)
  return op(arr, rhs_arr)
"""
            hzehy__rpxwo = {}
            exec(btrw__gkmt, {'bodo': bodo, 'op': op}, hzehy__rpxwo)
            impl = hzehy__rpxwo['impl']
            return impl
        if is_index_type(rhs):
            btrw__gkmt = """def impl(lhs, rhs):
  arr = bodo.utils.conversion.coerce_to_array(rhs)
"""
            if lhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                btrw__gkmt += """  dt = bodo.utils.conversion.unbox_if_timestamp(lhs)
  return op(dt, arr)
"""
            else:
                btrw__gkmt += """  lhs_arr = bodo.utils.conversion.get_array_if_series_or_index(lhs)
  return op(lhs_arr, arr)
"""
            hzehy__rpxwo = {}
            exec(btrw__gkmt, {'bodo': bodo, 'op': op}, hzehy__rpxwo)
            impl = hzehy__rpxwo['impl']
            return impl
        if isinstance(lhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(lhs.data):

                def impl3(lhs, rhs):
                    data = bodo.utils.conversion.coerce_to_array(lhs)
                    irk__rekg = bodo.utils.conversion.coerce_to_array(data)
                    ago__ixlsg = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    mko__ryy = op(irk__rekg, ago__ixlsg)
                    return mko__ryy
                return impl3
            count = len(lhs.data.types)
            btrw__gkmt = 'def f(lhs, rhs):\n'
            btrw__gkmt += '  return [{}]\n'.format(','.join(
                'op(lhs[{}], rhs{})'.format(i, f'[{i}]' if is_iterable_type
                (rhs) else '') for i in range(count)))
            hzehy__rpxwo = {}
            exec(btrw__gkmt, {'op': op, 'np': np}, hzehy__rpxwo)
            impl = hzehy__rpxwo['f']
            return impl
        if isinstance(rhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(rhs.data):

                def impl4(lhs, rhs):
                    data = bodo.hiframes.pd_index_ext.get_index_data(rhs)
                    irk__rekg = bodo.utils.conversion.coerce_to_array(data)
                    ago__ixlsg = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    mko__ryy = op(ago__ixlsg, irk__rekg)
                    return mko__ryy
                return impl4
            count = len(rhs.data.types)
            btrw__gkmt = 'def f(lhs, rhs):\n'
            btrw__gkmt += '  return [{}]\n'.format(','.join(
                'op(lhs{}, rhs[{}])'.format(f'[{i}]' if is_iterable_type(
                lhs) else '', i) for i in range(count)))
            hzehy__rpxwo = {}
            exec(btrw__gkmt, {'op': op, 'np': np}, hzehy__rpxwo)
            impl = hzehy__rpxwo['f']
            return impl
    return overload_index_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        overload_impl = create_binary_op_overload(op)
        overload(op, inline='always')(overload_impl)


_install_binary_ops()


def is_index_type(t):
    return isinstance(t, (RangeIndexType, NumericIndexType, StringIndexType,
        BinaryIndexType, PeriodIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType))


@lower_cast(RangeIndexType, NumericIndexType)
def cast_range_index_to_int_index(context, builder, fromty, toty, val):
    f = lambda I: init_numeric_index(np.arange(I._start, I._stop, I._step),
        bodo.hiframes.pd_index_ext.get_index_name(I))
    return context.compile_internal(builder, f, toty(fromty), [val])


class HeterogeneousIndexType(types.Type):
    ndim = 1

    def __init__(self, data=None, name_typ=None):
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        super(HeterogeneousIndexType, self).__init__(name=
            f'heter_index({data}, {name_typ})')

    def copy(self):
        return HeterogeneousIndexType(self.data, self.name_typ)

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return 'object'


@register_model(HeterogeneousIndexType)
class HeterogeneousIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cenq__mxgkc = [('data', fe_type.data), ('name', fe_type.name_typ)]
        super(HeterogeneousIndexModel, self).__init__(dmm, fe_type, cenq__mxgkc
            )


make_attribute_wrapper(HeterogeneousIndexType, 'data', '_data')
make_attribute_wrapper(HeterogeneousIndexType, 'name', '_name')


@overload_method(HeterogeneousIndexType, 'copy', no_unliteral=True)
def overload_heter_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    siqq__hago = idx_typ_to_format_str_map[HeterogeneousIndexType].format(
        'copy()')
    sjx__dli = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', sjx__dli, idx_cpy_arg_defaults,
        fn_str=siqq__hago, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(HeterogeneousIndexType)
def box_heter_index(typ, val, c):
    yivl__nyv = c.context.insert_const_string(c.builder.module, 'pandas')
    tybl__vzu = c.pyapi.import_module_noblock(yivl__nyv)
    ppov__bdkyw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, ppov__bdkyw.data)
    ctsu__qlbp = c.pyapi.from_native_value(typ.data, ppov__bdkyw.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ppov__bdkyw.name)
    efdj__nyeu = c.pyapi.from_native_value(typ.name_typ, ppov__bdkyw.name,
        c.env_manager)
    zdb__diyk = c.pyapi.make_none()
    cti__nbfkl = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    ckiy__vhxlr = c.pyapi.call_method(tybl__vzu, 'Index', (ctsu__qlbp,
        zdb__diyk, cti__nbfkl, efdj__nyeu))
    c.pyapi.decref(ctsu__qlbp)
    c.pyapi.decref(zdb__diyk)
    c.pyapi.decref(cti__nbfkl)
    c.pyapi.decref(efdj__nyeu)
    c.pyapi.decref(tybl__vzu)
    c.context.nrt.decref(c.builder, typ, val)
    return ckiy__vhxlr


@intrinsic
def init_heter_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        mmjg__cpd = signature.return_type
        ppov__bdkyw = cgutils.create_struct_proxy(mmjg__cpd)(context, builder)
        ppov__bdkyw.data = args[0]
        ppov__bdkyw.name = args[1]
        context.nrt.incref(builder, mmjg__cpd.data, args[0])
        context.nrt.incref(builder, mmjg__cpd.name_typ, args[1])
        return ppov__bdkyw._getvalue()
    return HeterogeneousIndexType(data, name)(data, name), codegen


@overload_attribute(HeterogeneousIndexType, 'name')
def heter_index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload_attribute(NumericIndexType, 'nbytes')
@overload_attribute(DatetimeIndexType, 'nbytes')
@overload_attribute(TimedeltaIndexType, 'nbytes')
@overload_attribute(RangeIndexType, 'nbytes')
@overload_attribute(StringIndexType, 'nbytes')
@overload_attribute(BinaryIndexType, 'nbytes')
@overload_attribute(CategoricalIndexType, 'nbytes')
@overload_attribute(PeriodIndexType, 'nbytes')
def overload_nbytes(I):
    if isinstance(I, RangeIndexType):

        def _impl_nbytes(I):
            return bodo.io.np_io.get_dtype_size(type(I._start)
                ) + bodo.io.np_io.get_dtype_size(type(I._step)
                ) + bodo.io.np_io.get_dtype_size(type(I._stop))
        return _impl_nbytes
    else:

        def _impl_nbytes(I):
            return I._data.nbytes
        return _impl_nbytes


@overload_method(NumericIndexType, 'to_series', inline='always')
@overload_method(DatetimeIndexType, 'to_series', inline='always')
@overload_method(TimedeltaIndexType, 'to_series', inline='always')
@overload_method(RangeIndexType, 'to_series', inline='always')
@overload_method(StringIndexType, 'to_series', inline='always')
@overload_method(BinaryIndexType, 'to_series', inline='always')
@overload_method(CategoricalIndexType, 'to_series', inline='always')
def overload_index_to_series(I, index=None, name=None):
    if not (is_overload_constant_str(name) or is_overload_constant_int(name
        ) or is_overload_none(name)):
        raise_bodo_error(
            f'Index.to_series(): only constant string/int are supported for argument name'
            )
    if is_overload_none(name):
        bfwx__ixd = 'bodo.hiframes.pd_index_ext.get_index_name(I)'
    else:
        bfwx__ixd = 'name'
    btrw__gkmt = 'def impl(I, index=None, name=None):\n'
    btrw__gkmt += '    data = bodo.utils.conversion.index_to_array(I)\n'
    if is_overload_none(index):
        btrw__gkmt += '    new_index = I\n'
    elif is_pd_index_type(index):
        btrw__gkmt += '    new_index = index\n'
    elif isinstance(index, SeriesType):
        btrw__gkmt += (
            '    arr = bodo.utils.conversion.coerce_to_array(index)\n')
        btrw__gkmt += (
            '    index_name = bodo.hiframes.pd_series_ext.get_series_name(index)\n'
            )
        btrw__gkmt += (
            '    new_index = bodo.utils.conversion.index_from_array(arr, index_name)\n'
            )
    elif bodo.utils.utils.is_array_typ(index, False):
        btrw__gkmt += (
            '    new_index = bodo.utils.conversion.index_from_array(index)\n')
    elif isinstance(index, (types.List, types.BaseTuple)):
        btrw__gkmt += (
            '    arr = bodo.utils.conversion.coerce_to_array(index)\n')
        btrw__gkmt += (
            '    new_index = bodo.utils.conversion.index_from_array(arr)\n')
    else:
        raise_bodo_error(
            f'Index.to_series(): unsupported type for argument index: {type(index).__name__}'
            )
    btrw__gkmt += f'    new_name = {bfwx__ixd}\n'
    btrw__gkmt += (
        '    return bodo.hiframes.pd_series_ext.init_series(data, new_index, new_name)'
        )
    hzehy__rpxwo = {}
    exec(btrw__gkmt, {'bodo': bodo, 'np': np}, hzehy__rpxwo)
    impl = hzehy__rpxwo['impl']
    return impl


@overload_method(NumericIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(DatetimeIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(TimedeltaIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(RangeIndexType, 'to_frame', inline='always', no_unliteral=True
    )
@overload_method(StringIndexType, 'to_frame', inline='always', no_unliteral
    =True)
@overload_method(BinaryIndexType, 'to_frame', inline='always', no_unliteral
    =True)
@overload_method(CategoricalIndexType, 'to_frame', inline='always',
    no_unliteral=True)
def overload_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        ajb__kllz = 'I'
    elif is_overload_false(index):
        ajb__kllz = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'Index.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'Index.to_frame(): index argument must be a compile time constant')
    btrw__gkmt = 'def impl(I, index=True, name=None):\n'
    btrw__gkmt += '    data = bodo.utils.conversion.index_to_array(I)\n'
    btrw__gkmt += f'    new_index = {ajb__kllz}\n'
    if is_overload_none(name) and I.name_typ == types.none:
        vbgf__kbp = ColNamesMetaType((0,))
    elif is_overload_none(name):
        vbgf__kbp = ColNamesMetaType((I.name_typ,))
    elif is_overload_constant_str(name):
        vbgf__kbp = ColNamesMetaType((get_overload_const_str(name),))
    elif is_overload_constant_int(name):
        vbgf__kbp = ColNamesMetaType((get_overload_const_int(name),))
    else:
        raise_bodo_error(
            f'Index.to_frame(): only constant string/int are supported for argument name'
            )
    btrw__gkmt += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((data,), new_index, __col_name_meta_value)
"""
    hzehy__rpxwo = {}
    exec(btrw__gkmt, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        vbgf__kbp}, hzehy__rpxwo)
    impl = hzehy__rpxwo['impl']
    return impl


@overload_method(MultiIndexType, 'to_frame', inline='always', no_unliteral=True
    )
def overload_multi_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        ajb__kllz = 'I'
    elif is_overload_false(index):
        ajb__kllz = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a compile time constant'
            )
    btrw__gkmt = 'def impl(I, index=True, name=None):\n'
    btrw__gkmt += '    data = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    btrw__gkmt += f'    new_index = {ajb__kllz}\n'
    ajwk__cfsj = len(I.array_types)
    if is_overload_none(name) and I.names_typ == (types.none,) * ajwk__cfsj:
        vbgf__kbp = ColNamesMetaType(tuple(range(ajwk__cfsj)))
    elif is_overload_none(name):
        vbgf__kbp = ColNamesMetaType(I.names_typ)
    elif is_overload_constant_tuple(name) or is_overload_constant_list(name):
        if is_overload_constant_list(name):
            names = tuple(get_overload_const_list(name))
        else:
            names = get_overload_const_tuple(name)
        if ajwk__cfsj != len(names):
            raise_bodo_error(
                f'MultiIndex.to_frame(): expected {ajwk__cfsj} names, not {len(names)}'
                )
        if all(is_overload_constant_str(czj__aagiq) or
            is_overload_constant_int(czj__aagiq) for czj__aagiq in names):
            vbgf__kbp = ColNamesMetaType(names)
        else:
            raise_bodo_error(
                'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
                )
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
            )
    btrw__gkmt += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(data, new_index, __col_name_meta_value,)
"""
    hzehy__rpxwo = {}
    exec(btrw__gkmt, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        vbgf__kbp}, hzehy__rpxwo)
    impl = hzehy__rpxwo['impl']
    return impl


@overload_method(NumericIndexType, 'to_numpy', inline='always')
@overload_method(DatetimeIndexType, 'to_numpy', inline='always')
@overload_method(TimedeltaIndexType, 'to_numpy', inline='always')
@overload_method(RangeIndexType, 'to_numpy', inline='always')
@overload_method(StringIndexType, 'to_numpy', inline='always')
@overload_method(BinaryIndexType, 'to_numpy', inline='always')
@overload_method(CategoricalIndexType, 'to_numpy', inline='always')
@overload_method(IntervalIndexType, 'to_numpy', inline='always')
def overload_index_to_numpy(I, dtype=None, copy=False, na_value=None):
    vwgld__zch = dict(dtype=dtype, na_value=na_value)
    vrsnf__bgvf = dict(dtype=None, na_value=None)
    check_unsupported_args('Index.to_numpy', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    if not is_overload_bool(copy):
        raise_bodo_error('Index.to_numpy(): copy argument must be a boolean')
    if isinstance(I, RangeIndexType):

        def impl(I, dtype=None, copy=False, na_value=None):
            return np.arange(I._start, I._stop, I._step)
        return impl
    if is_overload_true(copy):

        def impl(I, dtype=None, copy=False, na_value=None):
            return bodo.hiframes.pd_index_ext.get_index_data(I).copy()
        return impl
    if is_overload_false(copy):

        def impl(I, dtype=None, copy=False, na_value=None):
            return bodo.hiframes.pd_index_ext.get_index_data(I)
        return impl

    def impl(I, dtype=None, copy=False, na_value=None):
        data = bodo.hiframes.pd_index_ext.get_index_data(I)
        return data.copy() if copy else data
    return impl


@overload_method(NumericIndexType, 'to_list', inline='always')
@overload_method(RangeIndexType, 'to_list', inline='always')
@overload_method(StringIndexType, 'to_list', inline='always')
@overload_method(BinaryIndexType, 'to_list', inline='always')
@overload_method(CategoricalIndexType, 'to_list', inline='always')
@overload_method(DatetimeIndexType, 'to_list', inline='always')
@overload_method(TimedeltaIndexType, 'to_list', inline='always')
@overload_method(NumericIndexType, 'tolist', inline='always')
@overload_method(RangeIndexType, 'tolist', inline='always')
@overload_method(StringIndexType, 'tolist', inline='always')
@overload_method(BinaryIndexType, 'tolist', inline='always')
@overload_method(CategoricalIndexType, 'tolist', inline='always')
@overload_method(DatetimeIndexType, 'tolist', inline='always')
@overload_method(TimedeltaIndexType, 'tolist', inline='always')
def overload_index_to_list(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            lfwmw__sgu = list()
            for i in range(I._start, I._stop, I.step):
                lfwmw__sgu.append(i)
            return lfwmw__sgu
        return impl

    def impl(I):
        lfwmw__sgu = list()
        for i in range(len(I)):
            lfwmw__sgu.append(I[i])
        return lfwmw__sgu
    return impl


@overload_attribute(NumericIndexType, 'T')
@overload_attribute(DatetimeIndexType, 'T')
@overload_attribute(TimedeltaIndexType, 'T')
@overload_attribute(RangeIndexType, 'T')
@overload_attribute(StringIndexType, 'T')
@overload_attribute(BinaryIndexType, 'T')
@overload_attribute(CategoricalIndexType, 'T')
@overload_attribute(PeriodIndexType, 'T')
@overload_attribute(MultiIndexType, 'T')
@overload_attribute(IntervalIndexType, 'T')
def overload_T(I):
    return lambda I: I


@overload_attribute(NumericIndexType, 'size')
@overload_attribute(DatetimeIndexType, 'size')
@overload_attribute(TimedeltaIndexType, 'size')
@overload_attribute(RangeIndexType, 'size')
@overload_attribute(StringIndexType, 'size')
@overload_attribute(BinaryIndexType, 'size')
@overload_attribute(CategoricalIndexType, 'size')
@overload_attribute(PeriodIndexType, 'size')
@overload_attribute(MultiIndexType, 'size')
@overload_attribute(IntervalIndexType, 'size')
def overload_size(I):
    return lambda I: len(I)


@overload_attribute(NumericIndexType, 'ndim')
@overload_attribute(DatetimeIndexType, 'ndim')
@overload_attribute(TimedeltaIndexType, 'ndim')
@overload_attribute(RangeIndexType, 'ndim')
@overload_attribute(StringIndexType, 'ndim')
@overload_attribute(BinaryIndexType, 'ndim')
@overload_attribute(CategoricalIndexType, 'ndim')
@overload_attribute(PeriodIndexType, 'ndim')
@overload_attribute(MultiIndexType, 'ndim')
@overload_attribute(IntervalIndexType, 'ndim')
def overload_ndim(I):
    return lambda I: 1


@overload_attribute(NumericIndexType, 'nlevels')
@overload_attribute(DatetimeIndexType, 'nlevels')
@overload_attribute(TimedeltaIndexType, 'nlevels')
@overload_attribute(RangeIndexType, 'nlevels')
@overload_attribute(StringIndexType, 'nlevels')
@overload_attribute(BinaryIndexType, 'nlevels')
@overload_attribute(CategoricalIndexType, 'nlevels')
@overload_attribute(PeriodIndexType, 'nlevels')
@overload_attribute(MultiIndexType, 'nlevels')
@overload_attribute(IntervalIndexType, 'nlevels')
def overload_nlevels(I):
    if isinstance(I, MultiIndexType):
        return lambda I: len(I._data)
    return lambda I: 1


@overload_attribute(NumericIndexType, 'empty')
@overload_attribute(DatetimeIndexType, 'empty')
@overload_attribute(TimedeltaIndexType, 'empty')
@overload_attribute(RangeIndexType, 'empty')
@overload_attribute(StringIndexType, 'empty')
@overload_attribute(BinaryIndexType, 'empty')
@overload_attribute(CategoricalIndexType, 'empty')
@overload_attribute(PeriodIndexType, 'empty')
@overload_attribute(MultiIndexType, 'empty')
@overload_attribute(IntervalIndexType, 'empty')
def overload_empty(I):
    return lambda I: len(I) == 0


@overload_attribute(NumericIndexType, 'is_all_dates')
@overload_attribute(DatetimeIndexType, 'is_all_dates')
@overload_attribute(TimedeltaIndexType, 'is_all_dates')
@overload_attribute(RangeIndexType, 'is_all_dates')
@overload_attribute(StringIndexType, 'is_all_dates')
@overload_attribute(BinaryIndexType, 'is_all_dates')
@overload_attribute(CategoricalIndexType, 'is_all_dates')
@overload_attribute(PeriodIndexType, 'is_all_dates')
@overload_attribute(MultiIndexType, 'is_all_dates')
@overload_attribute(IntervalIndexType, 'is_all_dates')
def overload_is_all_dates(I):
    if isinstance(I, (DatetimeIndexType, TimedeltaIndexType, PeriodIndexType)):
        return lambda I: True
    else:
        return lambda I: False


@overload_attribute(NumericIndexType, 'inferred_type')
@overload_attribute(DatetimeIndexType, 'inferred_type')
@overload_attribute(TimedeltaIndexType, 'inferred_type')
@overload_attribute(RangeIndexType, 'inferred_type')
@overload_attribute(StringIndexType, 'inferred_type')
@overload_attribute(BinaryIndexType, 'inferred_type')
@overload_attribute(CategoricalIndexType, 'inferred_type')
@overload_attribute(PeriodIndexType, 'inferred_type')
@overload_attribute(MultiIndexType, 'inferred_type')
@overload_attribute(IntervalIndexType, 'inferred_type')
def overload_inferred_type(I):
    if isinstance(I, NumericIndexType):
        if isinstance(I.dtype, types.Integer):
            return lambda I: 'integer'
        elif isinstance(I.dtype, types.Float):
            return lambda I: 'floating'
        elif isinstance(I.dtype, types.Boolean):
            return lambda I: 'boolean'
        return
    if isinstance(I, StringIndexType):

        def impl(I):
            if len(I._data) == 0:
                return 'empty'
            return 'string'
        return impl
    ukwfi__ddwah = {DatetimeIndexType: 'datetime64', TimedeltaIndexType:
        'timedelta64', RangeIndexType: 'integer', BinaryIndexType: 'bytes',
        CategoricalIndexType: 'categorical', PeriodIndexType: 'period',
        IntervalIndexType: 'interval', MultiIndexType: 'mixed'}
    inferred_type = ukwfi__ddwah[type(I)]
    return lambda I: inferred_type


@overload_attribute(NumericIndexType, 'dtype')
@overload_attribute(DatetimeIndexType, 'dtype')
@overload_attribute(TimedeltaIndexType, 'dtype')
@overload_attribute(RangeIndexType, 'dtype')
@overload_attribute(StringIndexType, 'dtype')
@overload_attribute(BinaryIndexType, 'dtype')
@overload_attribute(CategoricalIndexType, 'dtype')
@overload_attribute(MultiIndexType, 'dtype')
def overload_inferred_type(I):
    if isinstance(I, NumericIndexType):
        if isinstance(I.dtype, types.Boolean):
            return lambda I: np.dtype('O')
        dtype = I.dtype
        return lambda I: dtype
    if isinstance(I, CategoricalIndexType):
        dtype = bodo.utils.utils.create_categorical_type(I.dtype.categories,
            I.data, I.dtype.ordered)
        return lambda I: dtype
    czvy__vrdby = {DatetimeIndexType: np.dtype('datetime64[ns]'),
        TimedeltaIndexType: np.dtype('timedelta64[ns]'), RangeIndexType: np
        .dtype('int64'), StringIndexType: np.dtype('O'), BinaryIndexType:
        np.dtype('O'), MultiIndexType: np.dtype('O')}
    dtype = czvy__vrdby[type(I)]
    return lambda I: dtype


@overload_attribute(NumericIndexType, 'names')
@overload_attribute(DatetimeIndexType, 'names')
@overload_attribute(TimedeltaIndexType, 'names')
@overload_attribute(RangeIndexType, 'names')
@overload_attribute(StringIndexType, 'names')
@overload_attribute(BinaryIndexType, 'names')
@overload_attribute(CategoricalIndexType, 'names')
@overload_attribute(IntervalIndexType, 'names')
@overload_attribute(PeriodIndexType, 'names')
@overload_attribute(MultiIndexType, 'names')
def overload_names(I):
    if isinstance(I, MultiIndexType):
        return lambda I: I._names
    return lambda I: (I._name,)


@overload_method(NumericIndexType, 'rename', inline='always')
@overload_method(DatetimeIndexType, 'rename', inline='always')
@overload_method(TimedeltaIndexType, 'rename', inline='always')
@overload_method(RangeIndexType, 'rename', inline='always')
@overload_method(StringIndexType, 'rename', inline='always')
@overload_method(BinaryIndexType, 'rename', inline='always')
@overload_method(CategoricalIndexType, 'rename', inline='always')
@overload_method(PeriodIndexType, 'rename', inline='always')
@overload_method(IntervalIndexType, 'rename', inline='always')
@overload_method(HeterogeneousIndexType, 'rename', inline='always')
def overload_rename(I, name, inplace=False):
    if is_overload_true(inplace):
        raise BodoError('Index.rename(): inplace index renaming unsupported')
    return init_index_from_index(I, name)


def init_index_from_index(I, name):
    nlfsa__zbkt = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index}
    if type(I) in nlfsa__zbkt:
        init_func = nlfsa__zbkt[type(I)]
        return lambda I, name, inplace=False: init_func(bodo.hiframes.
            pd_index_ext.get_index_data(I).copy(), name)
    if isinstance(I, RangeIndexType):
        return lambda I, name, inplace=False: I.copy(name=name)
    if isinstance(I, PeriodIndexType):
        freq = I.freq
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_period_index(bodo.hiframes.pd_index_ext.get_index_data(I).
            copy(), name, freq))
    if isinstance(I, HeterogeneousIndexType):
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_heter_index(bodo.hiframes.pd_index_ext.get_index_data(I),
            name))
    raise_bodo_error(f'init_index(): Unknown type {type(I)}')


def get_index_constructor(I):
    jsa__qiykv = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index, RangeIndexType: bodo.
        hiframes.pd_index_ext.init_range_index}
    if type(I) in jsa__qiykv:
        return jsa__qiykv[type(I)]
    raise BodoError(
        f'Unsupported type for standard Index constructor: {type(I)}')


@overload_method(NumericIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'min', no_unliteral=True, inline=
    'always')
def overload_index_min(I, axis=None, skipna=True):
    vwgld__zch = dict(axis=axis, skipna=skipna)
    vrsnf__bgvf = dict(axis=None, skipna=True)
    check_unsupported_args('Index.min', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            jjif__lorp = len(I)
            if jjif__lorp == 0:
                return np.nan
            if I._step < 0:
                return I._start + I._step * (jjif__lorp - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.min(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        irk__rekg = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_min(irk__rekg)
    return impl


@overload_method(NumericIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'max', no_unliteral=True, inline=
    'always')
def overload_index_max(I, axis=None, skipna=True):
    vwgld__zch = dict(axis=axis, skipna=skipna)
    vrsnf__bgvf = dict(axis=None, skipna=True)
    check_unsupported_args('Index.max', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            jjif__lorp = len(I)
            if jjif__lorp == 0:
                return np.nan
            if I._step > 0:
                return I._start + I._step * (jjif__lorp - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.max(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        irk__rekg = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_max(irk__rekg)
    return impl


@overload_method(NumericIndexType, 'argmin', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(PeriodIndexType, 'argmin', no_unliteral=True, inline='always')
def overload_index_argmin(I, axis=0, skipna=True):
    vwgld__zch = dict(axis=axis, skipna=skipna)
    vrsnf__bgvf = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmin', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.argmin()')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, skipna=True):
            return (I._step < 0) * (len(I) - 1)
        return impl
    if isinstance(I, CategoricalIndexType) and not I.dtype.ordered:
        raise BodoError(
            'Index.argmin(): only ordered categoricals are possible')

    def impl(I, axis=0, skipna=True):
        irk__rekg = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = init_numeric_index(np.arange(len(irk__rekg)))
        return bodo.libs.array_ops.array_op_idxmin(irk__rekg, index)
    return impl


@overload_method(NumericIndexType, 'argmax', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(PeriodIndexType, 'argmax', no_unliteral=True, inline='always')
def overload_index_argmax(I, axis=0, skipna=True):
    vwgld__zch = dict(axis=axis, skipna=skipna)
    vrsnf__bgvf = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmax', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.argmax()')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, skipna=True):
            return (I._step > 0) * (len(I) - 1)
        return impl
    if isinstance(I, CategoricalIndexType) and not I.dtype.ordered:
        raise BodoError(
            'Index.argmax(): only ordered categoricals are possible')

    def impl(I, axis=0, skipna=True):
        irk__rekg = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = np.arange(len(irk__rekg))
        return bodo.libs.array_ops.array_op_idxmax(irk__rekg, index)
    return impl


@overload_method(NumericIndexType, 'unique', no_unliteral=True, inline='always'
    )
@overload_method(BinaryIndexType, 'unique', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'unique', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(IntervalIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(DatetimeIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'unique', no_unliteral=True, inline=
    'always')
def overload_index_unique(I):
    riny__rsp = get_index_constructor(I)

    def impl(I):
        irk__rekg = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        gaee__ktnt = bodo.libs.array_kernels.unique(irk__rekg)
        return riny__rsp(gaee__ktnt, name)
    return impl


@overload_method(RangeIndexType, 'unique', no_unliteral=True, inline='always')
def overload_range_index_unique(I):

    def impl(I):
        return I.copy()
    return impl


@overload_method(NumericIndexType, 'nunique', inline='always')
@overload_method(BinaryIndexType, 'nunique', inline='always')
@overload_method(StringIndexType, 'nunique', inline='always')
@overload_method(CategoricalIndexType, 'nunique', inline='always')
@overload_method(DatetimeIndexType, 'nunique', inline='always')
@overload_method(TimedeltaIndexType, 'nunique', inline='always')
@overload_method(PeriodIndexType, 'nunique', inline='always')
def overload_index_nunique(I, dropna=True):

    def impl(I, dropna=True):
        irk__rekg = bodo.hiframes.pd_index_ext.get_index_data(I)
        sadat__mquh = bodo.libs.array_kernels.nunique(irk__rekg, dropna)
        return sadat__mquh
    return impl


@overload_method(RangeIndexType, 'nunique', inline='always')
def overload_range_index_nunique(I, dropna=True):

    def impl(I, dropna=True):
        start = I._start
        stop = I._stop
        step = I._step
        return max(0, -(-(stop - start) // step))
    return impl


@overload_method(NumericIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(TimedeltaIndexType, 'isin', no_unliteral=True, inline='always'
    )
def overload_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            vxn__vbaha = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_index_ext.get_index_data(I)
            sadat__mquh = len(A)
            mko__ryy = np.empty(sadat__mquh, np.bool_)
            bodo.libs.array.array_isin(mko__ryy, A, vxn__vbaha, False)
            return mko__ryy
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        mko__ryy = bodo.libs.array_ops.array_op_isin(A, values)
        return mko__ryy
    return impl


@overload_method(RangeIndexType, 'isin', no_unliteral=True, inline='always')
def overload_range_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            vxn__vbaha = bodo.utils.conversion.coerce_to_array(values)
            A = np.arange(I.start, I.stop, I.step)
            sadat__mquh = len(A)
            mko__ryy = np.empty(sadat__mquh, np.bool_)
            bodo.libs.array.array_isin(mko__ryy, A, vxn__vbaha, False)
            return mko__ryy
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Index.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = np.arange(I.start, I.stop, I.step)
        mko__ryy = bodo.libs.array_ops.array_op_isin(A, values)
        return mko__ryy
    return impl


@register_jitable
def order_range(I, ascending):
    step = I._step
    if ascending == (step > 0):
        return I.copy()
    else:
        start = I._start
        stop = I._stop
        name = get_index_name(I)
        jjif__lorp = len(I)
        hmm__vqd = start + step * (jjif__lorp - 1)
        oov__yzvo = hmm__vqd - step * jjif__lorp
        return init_range_index(hmm__vqd, oov__yzvo, -step, name)


@overload_method(NumericIndexType, 'sort_values', no_unliteral=True, inline
    ='always')
@overload_method(BinaryIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
@overload_method(StringIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(RangeIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
def overload_index_sort_values(I, return_indexer=False, ascending=True,
    na_position='last', key=None):
    vwgld__zch = dict(return_indexer=return_indexer, key=key)
    vrsnf__bgvf = dict(return_indexer=False, key=None)
    check_unsupported_args('Index.sort_values', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Index.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Index.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    if isinstance(I, RangeIndexType):

        def impl(I, return_indexer=False, ascending=True, na_position=
            'last', key=None):
            return order_range(I, ascending)
        return impl
    riny__rsp = get_index_constructor(I)
    zwz__rlpfh = ColNamesMetaType(('$_bodo_col_',))

    def impl(I, return_indexer=False, ascending=True, na_position='last',
        key=None):
        irk__rekg = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = get_index_name(I)
        index = init_range_index(0, len(irk__rekg), 1, None)
        cvsew__prk = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            irk__rekg,), index, zwz__rlpfh)
        tblv__hawd = cvsew__prk.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=False, na_position=na_position)
        mko__ryy = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(tblv__hawd
            , 0)
        return riny__rsp(mko__ryy, name)
    return impl


@overload_method(NumericIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(BinaryIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(CategoricalIndexType, 'argsort', no_unliteral=True, inline
    ='always')
@overload_method(DatetimeIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(PeriodIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(RangeIndexType, 'argsort', no_unliteral=True, inline='always')
def overload_index_argsort(I, axis=0, kind='quicksort', order=None):
    vwgld__zch = dict(axis=axis, kind=kind, order=order)
    vrsnf__bgvf = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Index.argsort', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, kind='quicksort', order=None):
            if I._step > 0:
                return np.arange(0, len(I), 1)
            else:
                return np.arange(len(I) - 1, -1, -1)
        return impl

    def impl(I, axis=0, kind='quicksort', order=None):
        irk__rekg = bodo.hiframes.pd_index_ext.get_index_data(I)
        mko__ryy = bodo.hiframes.series_impl.argsort(irk__rekg)
        return mko__ryy
    return impl


@overload_method(NumericIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'where', no_unliteral=True, inline='always'
    )
@overload_method(TimedeltaIndexType, 'where', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'where', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'where', no_unliteral=True, inline='always')
def overload_index_where(I, cond, other=np.nan):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.where()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Index.where()')
    bodo.hiframes.series_impl._validate_arguments_mask_where('where',
        'Index', I, cond, other, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False)
    if is_overload_constant_nan(other):
        zadlt__ebrke = 'None'
    else:
        zadlt__ebrke = 'other'
    btrw__gkmt = 'def impl(I, cond, other=np.nan):\n'
    if isinstance(I, RangeIndexType):
        btrw__gkmt += '  arr = np.arange(I._start, I._stop, I._step)\n'
        riny__rsp = 'init_numeric_index'
    else:
        btrw__gkmt += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    btrw__gkmt += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    btrw__gkmt += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {zadlt__ebrke})\n'
        )
    btrw__gkmt += f'  return constructor(out_arr, name)\n'
    hzehy__rpxwo = {}
    riny__rsp = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(btrw__gkmt, {'bodo': bodo, 'np': np, 'constructor': riny__rsp},
        hzehy__rpxwo)
    impl = hzehy__rpxwo['impl']
    return impl


@overload_method(NumericIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(StringIndexType, 'putmask', no_unliteral=True, inline='always'
    )
@overload_method(BinaryIndexType, 'putmask', no_unliteral=True, inline='always'
    )
@overload_method(DatetimeIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'putmask', no_unliteral=True, inline
    ='always')
@overload_method(RangeIndexType, 'putmask', no_unliteral=True, inline='always')
def overload_index_putmask(I, cond, other):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.putmask()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Index.putmask()')
    bodo.hiframes.series_impl._validate_arguments_mask_where('putmask',
        'Index', I, cond, other, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False)
    if is_overload_constant_nan(other):
        zadlt__ebrke = 'None'
    else:
        zadlt__ebrke = 'other'
    btrw__gkmt = 'def impl(I, cond, other):\n'
    btrw__gkmt += '  cond = ~cond\n'
    if isinstance(I, RangeIndexType):
        btrw__gkmt += '  arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        btrw__gkmt += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    btrw__gkmt += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    btrw__gkmt += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {zadlt__ebrke})\n'
        )
    btrw__gkmt += f'  return constructor(out_arr, name)\n'
    hzehy__rpxwo = {}
    riny__rsp = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(btrw__gkmt, {'bodo': bodo, 'np': np, 'constructor': riny__rsp},
        hzehy__rpxwo)
    impl = hzehy__rpxwo['impl']
    return impl


@overload_method(NumericIndexType, 'repeat', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'repeat', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(DatetimeIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'repeat', no_unliteral=True, inline='always')
def overload_index_repeat(I, repeats, axis=None):
    vwgld__zch = dict(axis=axis)
    vrsnf__bgvf = dict(axis=None)
    check_unsupported_args('Index.repeat', vwgld__zch, vrsnf__bgvf,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Index.repeat(): 'repeats' should be an integer or array of integers"
            )
    btrw__gkmt = 'def impl(I, repeats, axis=None):\n'
    if not isinstance(repeats, types.Integer):
        btrw__gkmt += (
            '    repeats = bodo.utils.conversion.coerce_to_array(repeats)\n')
    if isinstance(I, RangeIndexType):
        btrw__gkmt += '    arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        btrw__gkmt += (
            '    arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n')
    btrw__gkmt += '    name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    btrw__gkmt += (
        '    out_arr = bodo.libs.array_kernels.repeat_kernel(arr, repeats)\n')
    btrw__gkmt += '    return constructor(out_arr, name)'
    hzehy__rpxwo = {}
    riny__rsp = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(btrw__gkmt, {'bodo': bodo, 'np': np, 'constructor': riny__rsp},
        hzehy__rpxwo)
    impl = hzehy__rpxwo['impl']
    return impl


@overload_method(NumericIndexType, 'is_integer', inline='always')
def overload_is_integer_numeric(I):
    truth = isinstance(I.dtype, types.Integer)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_floating', inline='always')
def overload_is_floating_numeric(I):
    truth = isinstance(I.dtype, types.Float)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_boolean', inline='always')
def overload_is_boolean_numeric(I):
    truth = isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_numeric', inline='always')
def overload_is_numeric_numeric(I):
    truth = not isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_object', inline='always')
def overload_is_object_numeric(I):
    truth = isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(StringIndexType, 'is_object', inline='always')
@overload_method(BinaryIndexType, 'is_object', inline='always')
@overload_method(RangeIndexType, 'is_numeric', inline='always')
@overload_method(RangeIndexType, 'is_integer', inline='always')
@overload_method(CategoricalIndexType, 'is_categorical', inline='always')
@overload_method(IntervalIndexType, 'is_interval', inline='always')
@overload_method(MultiIndexType, 'is_object', inline='always')
def overload_is_methods_true(I):
    return lambda I: True


@overload_method(NumericIndexType, 'is_categorical', inline='always')
@overload_method(NumericIndexType, 'is_interval', inline='always')
@overload_method(StringIndexType, 'is_boolean', inline='always')
@overload_method(StringIndexType, 'is_floating', inline='always')
@overload_method(StringIndexType, 'is_categorical', inline='always')
@overload_method(StringIndexType, 'is_integer', inline='always')
@overload_method(StringIndexType, 'is_interval', inline='always')
@overload_method(StringIndexType, 'is_numeric', inline='always')
@overload_method(BinaryIndexType, 'is_boolean', inline='always')
@overload_method(BinaryIndexType, 'is_floating', inline='always')
@overload_method(BinaryIndexType, 'is_categorical', inline='always')
@overload_method(BinaryIndexType, 'is_integer', inline='always')
@overload_method(BinaryIndexType, 'is_interval', inline='always')
@overload_method(BinaryIndexType, 'is_numeric', inline='always')
@overload_method(DatetimeIndexType, 'is_boolean', inline='always')
@overload_method(DatetimeIndexType, 'is_floating', inline='always')
@overload_method(DatetimeIndexType, 'is_categorical', inline='always')
@overload_method(DatetimeIndexType, 'is_integer', inline='always')
@overload_method(DatetimeIndexType, 'is_interval', inline='always')
@overload_method(DatetimeIndexType, 'is_numeric', inline='always')
@overload_method(DatetimeIndexType, 'is_object', inline='always')
@overload_method(TimedeltaIndexType, 'is_boolean', inline='always')
@overload_method(TimedeltaIndexType, 'is_floating', inline='always')
@overload_method(TimedeltaIndexType, 'is_categorical', inline='always')
@overload_method(TimedeltaIndexType, 'is_integer', inline='always')
@overload_method(TimedeltaIndexType, 'is_interval', inline='always')
@overload_method(TimedeltaIndexType, 'is_numeric', inline='always')
@overload_method(TimedeltaIndexType, 'is_object', inline='always')
@overload_method(RangeIndexType, 'is_boolean', inline='always')
@overload_method(RangeIndexType, 'is_floating', inline='always')
@overload_method(RangeIndexType, 'is_categorical', inline='always')
@overload_method(RangeIndexType, 'is_interval', inline='always')
@overload_method(RangeIndexType, 'is_object', inline='always')
@overload_method(IntervalIndexType, 'is_boolean', inline='always')
@overload_method(IntervalIndexType, 'is_floating', inline='always')
@overload_method(IntervalIndexType, 'is_categorical', inline='always')
@overload_method(IntervalIndexType, 'is_integer', inline='always')
@overload_method(IntervalIndexType, 'is_numeric', inline='always')
@overload_method(IntervalIndexType, 'is_object', inline='always')
@overload_method(CategoricalIndexType, 'is_boolean', inline='always')
@overload_method(CategoricalIndexType, 'is_floating', inline='always')
@overload_method(CategoricalIndexType, 'is_integer', inline='always')
@overload_method(CategoricalIndexType, 'is_interval', inline='always')
@overload_method(CategoricalIndexType, 'is_numeric', inline='always')
@overload_method(CategoricalIndexType, 'is_object', inline='always')
@overload_method(PeriodIndexType, 'is_boolean', inline='always')
@overload_method(PeriodIndexType, 'is_floating', inline='always')
@overload_method(PeriodIndexType, 'is_categorical', inline='always')
@overload_method(PeriodIndexType, 'is_integer', inline='always')
@overload_method(PeriodIndexType, 'is_interval', inline='always')
@overload_method(PeriodIndexType, 'is_numeric', inline='always')
@overload_method(PeriodIndexType, 'is_object', inline='always')
@overload_method(MultiIndexType, 'is_boolean', inline='always')
@overload_method(MultiIndexType, 'is_floating', inline='always')
@overload_method(MultiIndexType, 'is_categorical', inline='always')
@overload_method(MultiIndexType, 'is_integer', inline='always')
@overload_method(MultiIndexType, 'is_interval', inline='always')
@overload_method(MultiIndexType, 'is_numeric', inline='always')
def overload_is_methods_false(I):
    return lambda I: False


@overload(operator.getitem, no_unliteral=True)
def overload_heter_index_getitem(I, ind):
    if not isinstance(I, HeterogeneousIndexType):
        return
    if isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, HeterogeneousIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_heter_index(bodo
            .hiframes.pd_index_ext.get_index_data(I)[ind], bodo.hiframes.
            pd_index_ext.get_index_name(I))


@lower_constant(DatetimeIndexType)
@lower_constant(TimedeltaIndexType)
def lower_constant_time_index(context, builder, ty, pyval):
    if isinstance(ty.data, bodo.DatetimeArrayType):
        data = context.get_constant_generic(builder, ty.data, pyval.array)
    else:
        data = context.get_constant_generic(builder, types.Array(types.
            int64, 1, 'C'), pyval.values.view(np.int64))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    ghe__exs = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, ghe__exs])


@lower_constant(PeriodIndexType)
def lower_constant_period_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, bodo.IntegerArrayType(
        types.int64), pd.arrays.IntegerArray(pyval.asi8, pyval.isna()))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    ghe__exs = context.get_constant_null(types.DictType(types.int64, types.
        int64))
    return lir.Constant.literal_struct([data, name, ghe__exs])


@lower_constant(NumericIndexType)
def lower_constant_numeric_index(context, builder, ty, pyval):
    assert isinstance(ty.dtype, (types.Integer, types.Float, types.Boolean))
    data = context.get_constant_generic(builder, types.Array(ty.dtype, 1,
        'C'), pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    ghe__exs = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, ghe__exs])


@lower_constant(StringIndexType)
@lower_constant(BinaryIndexType)
def lower_constant_binary_string_index(context, builder, ty, pyval):
    qqsfs__vzj = ty.data
    scalar_type = ty.data.dtype
    data = context.get_constant_generic(builder, qqsfs__vzj, pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    ghe__exs = context.get_constant_null(types.DictType(scalar_type, types.
        int64))
    return lir.Constant.literal_struct([data, name, ghe__exs])


@lower_builtin('getiter', RangeIndexType)
def getiter_range_index(context, builder, sig, args):
    [mag__xpu] = sig.args
    [index] = args
    njpy__fkzz = context.make_helper(builder, mag__xpu, value=index)
    iie__ngp = context.make_helper(builder, sig.return_type)
    qesk__obpp = cgutils.alloca_once_value(builder, njpy__fkzz.start)
    sajr__twjnc = context.get_constant(types.intp, 0)
    fjqf__xvplq = cgutils.alloca_once_value(builder, sajr__twjnc)
    iie__ngp.iter = qesk__obpp
    iie__ngp.stop = njpy__fkzz.stop
    iie__ngp.step = njpy__fkzz.step
    iie__ngp.count = fjqf__xvplq
    zjhxn__hkgyn = builder.sub(njpy__fkzz.stop, njpy__fkzz.start)
    zvebi__huyrz = context.get_constant(types.intp, 1)
    rsm__qxnsa = builder.icmp_signed('>', zjhxn__hkgyn, sajr__twjnc)
    gean__mteo = builder.icmp_signed('>', njpy__fkzz.step, sajr__twjnc)
    lls__oqix = builder.not_(builder.xor(rsm__qxnsa, gean__mteo))
    with builder.if_then(lls__oqix):
        oyx__ozwwk = builder.srem(zjhxn__hkgyn, njpy__fkzz.step)
        oyx__ozwwk = builder.select(rsm__qxnsa, oyx__ozwwk, builder.neg(
            oyx__ozwwk))
        zekh__xznqx = builder.icmp_signed('>', oyx__ozwwk, sajr__twjnc)
        hzd__dplae = builder.add(builder.sdiv(zjhxn__hkgyn, njpy__fkzz.step
            ), builder.select(zekh__xznqx, zvebi__huyrz, sajr__twjnc))
        builder.store(hzd__dplae, fjqf__xvplq)
    syaaj__fwv = iie__ngp._getvalue()
    jhv__lilvn = impl_ret_new_ref(context, builder, sig.return_type, syaaj__fwv
        )
    return jhv__lilvn


def _install_index_getiter():
    index_types = [NumericIndexType, StringIndexType, BinaryIndexType,
        CategoricalIndexType, TimedeltaIndexType, DatetimeIndexType]
    for typ in index_types:
        lower_builtin('getiter', typ)(numba.np.arrayobj.getiter_array)


_install_index_getiter()
index_unsupported_methods = ['append', 'asof', 'asof_locs', 'astype',
    'delete', 'drop', 'droplevel', 'dropna', 'equals', 'factorize',
    'fillna', 'format', 'get_indexer', 'get_indexer_for',
    'get_indexer_non_unique', 'get_level_values', 'get_slice_bound',
    'get_value', 'groupby', 'holds_integer', 'identical', 'insert', 'is_',
    'is_mixed', 'is_type_compatible', 'item', 'join', 'memory_usage',
    'ravel', 'reindex', 'searchsorted', 'set_names', 'set_value', 'shift',
    'slice_indexer', 'slice_locs', 'sort', 'sortlevel', 'str',
    'to_flat_index', 'to_native_types', 'transpose', 'value_counts', 'view']
index_unsupported_atrs = ['array', 'asi8', 'has_duplicates', 'hasnans',
    'is_unique']
cat_idx_unsupported_atrs = ['codes', 'categories', 'ordered',
    'is_monotonic', 'is_monotonic_increasing', 'is_monotonic_decreasing']
cat_idx_unsupported_methods = ['rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered', 'get_loc', 'isin',
    'all', 'any', 'union', 'intersection', 'difference', 'symmetric_difference'
    ]
interval_idx_unsupported_atrs = ['closed', 'is_empty',
    'is_non_overlapping_monotonic', 'is_overlapping', 'left', 'right',
    'mid', 'length', 'values', 'nbytes', 'is_monotonic',
    'is_monotonic_increasing', 'is_monotonic_decreasing', 'dtype']
interval_idx_unsupported_methods = ['contains', 'copy', 'overlaps',
    'set_closed', 'to_tuples', 'take', 'get_loc', 'isna', 'isnull', 'map',
    'isin', 'all', 'any', 'argsort', 'sort_values', 'argmax', 'argmin',
    'where', 'putmask', 'nunique', 'union', 'intersection', 'difference',
    'symmetric_difference', 'to_series', 'to_frame', 'to_list', 'tolist',
    'repeat', 'min', 'max']
multi_index_unsupported_atrs = ['levshape', 'levels', 'codes', 'dtypes',
    'values', 'nbytes', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
multi_index_unsupported_methods = ['copy', 'set_levels', 'set_codes',
    'swaplevel', 'reorder_levels', 'remove_unused_levels', 'get_loc',
    'get_locs', 'get_loc_level', 'take', 'isna', 'isnull', 'map', 'isin',
    'unique', 'all', 'any', 'argsort', 'sort_values', 'argmax', 'argmin',
    'where', 'putmask', 'nunique', 'union', 'intersection', 'difference',
    'symmetric_difference', 'to_series', 'to_list', 'tolist', 'to_numpy',
    'repeat', 'min', 'max']
dt_index_unsupported_atrs = ['time', 'timez', 'tz', 'freq', 'freqstr',
    'inferred_freq']
dt_index_unsupported_methods = ['normalize', 'strftime', 'snap',
    'tz_localize', 'round', 'floor', 'ceil', 'to_period', 'to_perioddelta',
    'to_pydatetime', 'month_name', 'day_name', 'mean', 'indexer_at_time',
    'indexer_between', 'indexer_between_time', 'all', 'any']
td_index_unsupported_atrs = ['components', 'inferred_freq']
td_index_unsupported_methods = ['to_pydatetime', 'round', 'floor', 'ceil',
    'mean', 'all', 'any']
period_index_unsupported_atrs = ['day', 'dayofweek', 'day_of_week',
    'dayofyear', 'day_of_year', 'days_in_month', 'daysinmonth', 'freq',
    'freqstr', 'hour', 'is_leap_year', 'minute', 'month', 'quarter',
    'second', 'week', 'weekday', 'weekofyear', 'year', 'end_time', 'qyear',
    'start_time', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing', 'dtype']
period_index_unsupported_methods = ['asfreq', 'strftime', 'to_timestamp',
    'isin', 'unique', 'all', 'any', 'where', 'putmask', 'sort_values',
    'union', 'intersection', 'difference', 'symmetric_difference',
    'to_series', 'to_frame', 'to_numpy', 'to_list', 'tolist', 'repeat',
    'min', 'max']
string_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
string_index_unsupported_methods = ['min', 'max']
binary_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
binary_index_unsupported_methods = ['repeat', 'min', 'max']
index_types = [('pandas.RangeIndex.{}', RangeIndexType), (
    'pandas.Index.{} with numeric data', NumericIndexType), (
    'pandas.Index.{} with string data', StringIndexType), (
    'pandas.Index.{} with binary data', BinaryIndexType), (
    'pandas.TimedeltaIndex.{}', TimedeltaIndexType), (
    'pandas.IntervalIndex.{}', IntervalIndexType), (
    'pandas.CategoricalIndex.{}', CategoricalIndexType), (
    'pandas.PeriodIndex.{}', PeriodIndexType), ('pandas.DatetimeIndex.{}',
    DatetimeIndexType), ('pandas.MultiIndex.{}', MultiIndexType)]
for name, typ in index_types:
    idx_typ_to_format_str_map[typ] = name


def _install_index_unsupported():
    for iha__xia in index_unsupported_methods:
        for htxpf__ovmqp, typ in index_types:
            overload_method(typ, iha__xia, no_unliteral=True)(
                create_unsupported_overload(htxpf__ovmqp.format(iha__xia +
                '()')))
    for eok__edit in index_unsupported_atrs:
        for htxpf__ovmqp, typ in index_types:
            overload_attribute(typ, eok__edit, no_unliteral=True)(
                create_unsupported_overload(htxpf__ovmqp.format(eok__edit)))
    sann__zoe = [(StringIndexType, string_index_unsupported_atrs), (
        BinaryIndexType, binary_index_unsupported_atrs), (
        CategoricalIndexType, cat_idx_unsupported_atrs), (IntervalIndexType,
        interval_idx_unsupported_atrs), (MultiIndexType,
        multi_index_unsupported_atrs), (DatetimeIndexType,
        dt_index_unsupported_atrs), (TimedeltaIndexType,
        td_index_unsupported_atrs), (PeriodIndexType,
        period_index_unsupported_atrs)]
    bmdll__sgtlq = [(CategoricalIndexType, cat_idx_unsupported_methods), (
        IntervalIndexType, interval_idx_unsupported_methods), (
        MultiIndexType, multi_index_unsupported_methods), (
        DatetimeIndexType, dt_index_unsupported_methods), (
        TimedeltaIndexType, td_index_unsupported_methods), (PeriodIndexType,
        period_index_unsupported_methods), (BinaryIndexType,
        binary_index_unsupported_methods), (StringIndexType,
        string_index_unsupported_methods)]
    for typ, ato__mnip in bmdll__sgtlq:
        htxpf__ovmqp = idx_typ_to_format_str_map[typ]
        for umpy__jvizz in ato__mnip:
            overload_method(typ, umpy__jvizz, no_unliteral=True)(
                create_unsupported_overload(htxpf__ovmqp.format(umpy__jvizz +
                '()')))
    for typ, hqgyp__ywp in sann__zoe:
        htxpf__ovmqp = idx_typ_to_format_str_map[typ]
        for eok__edit in hqgyp__ywp:
            overload_attribute(typ, eok__edit, no_unliteral=True)(
                create_unsupported_overload(htxpf__ovmqp.format(eok__edit)))


_install_index_unsupported()
