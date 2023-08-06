"""Dictionary encoded array data type, similar to DictionaryArray of Arrow.
The purpose is to improve memory consumption and performance over string_array_type for
string arrays that have a lot of repetitive values (typical in practice).
Can be extended to be used with types other than strings as well.
See:
https://bodo.atlassian.net/browse/BE-2295
https://bodo.atlassian.net/wiki/spaces/B/pages/993722369/Dictionary-encoded+String+Array+Support+in+Parquet+read+compute+...
https://arrow.apache.org/docs/cpp/api/array.html#dictionary-encoded
"""
import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_builtin, lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
import bodo
from bodo.libs import hstr_ext
from bodo.libs.bool_arr_ext import init_bool_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, get_str_arr_item_length, overload_str_arr_astype, pre_alloc_string_array
from bodo.utils.typing import BodoArrayIterator, is_overload_none, raise_bodo_error
ll.add_symbol('box_dict_str_array', hstr_ext.box_dict_str_array)
dict_indices_arr_type = IntegerArrayType(types.int32)


class DictionaryArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self, arr_data_type):
        self.data = arr_data_type
        super(DictionaryArrayType, self).__init__(name=
            f'DictionaryArrayType({arr_data_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def iterator_type(self):
        return BodoArrayIterator(self)

    @property
    def dtype(self):
        return self.data.dtype

    def copy(self):
        return DictionaryArrayType(self.data)

    @property
    def indices_type(self):
        return dict_indices_arr_type

    @property
    def indices_dtype(self):
        return dict_indices_arr_type.dtype

    def unify(self, typingctx, other):
        if other == bodo.string_array_type:
            return bodo.string_array_type


dict_str_arr_type = DictionaryArrayType(bodo.string_array_type)


@register_model(DictionaryArrayType)
class DictionaryArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        nkii__ynqmi = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, nkii__ynqmi)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        drfd__efmyq, cqroc__lebm, odt__dfizv = args
        zrjhf__ekeuf = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        zrjhf__ekeuf.data = drfd__efmyq
        zrjhf__ekeuf.indices = cqroc__lebm
        zrjhf__ekeuf.has_global_dictionary = odt__dfizv
        context.nrt.incref(builder, signature.args[0], drfd__efmyq)
        context.nrt.incref(builder, signature.args[1], cqroc__lebm)
        return zrjhf__ekeuf._getvalue()
    khix__tzkm = DictionaryArrayType(data_t)
    yso__ijy = khix__tzkm(data_t, indices_t, types.bool_)
    return yso__ijy, codegen


@typeof_impl.register(pa.DictionaryArray)
def typeof_dict_value(val, c):
    if val.type.value_type == pa.string():
        return dict_str_arr_type


def to_pa_dict_arr(A):
    if isinstance(A, pa.DictionaryArray):
        return A
    for i in range(len(A)):
        if pd.isna(A[i]):
            A[i] = None
    return pa.array(A).dictionary_encode()


@unbox(DictionaryArrayType)
def unbox_dict_arr(typ, val, c):
    if bodo.hiframes.boxing._use_dict_str_type:
        dgpj__wmt = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(dgpj__wmt, [val])
        c.pyapi.decref(dgpj__wmt)
    zrjhf__ekeuf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rpq__frbfu = c.pyapi.object_getattr_string(val, 'dictionary')
    nuny__rczvy = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    hjuxq__ibvr = c.pyapi.call_method(rpq__frbfu, 'to_numpy', (nuny__rczvy,))
    zrjhf__ekeuf.data = c.unbox(typ.data, hjuxq__ibvr).value
    zco__gxyh = c.pyapi.object_getattr_string(val, 'indices')
    nbc__jeb = c.context.insert_const_string(c.builder.module, 'pandas')
    xaegv__sbbag = c.pyapi.import_module_noblock(nbc__jeb)
    ihxjt__zdbh = c.pyapi.string_from_constant_string('Int32')
    json__sqsjo = c.pyapi.call_method(xaegv__sbbag, 'array', (zco__gxyh,
        ihxjt__zdbh))
    zrjhf__ekeuf.indices = c.unbox(dict_indices_arr_type, json__sqsjo).value
    zrjhf__ekeuf.has_global_dictionary = c.context.get_constant(types.bool_,
        False)
    c.pyapi.decref(rpq__frbfu)
    c.pyapi.decref(nuny__rczvy)
    c.pyapi.decref(hjuxq__ibvr)
    c.pyapi.decref(zco__gxyh)
    c.pyapi.decref(xaegv__sbbag)
    c.pyapi.decref(ihxjt__zdbh)
    c.pyapi.decref(json__sqsjo)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    qtju__syowx = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(zrjhf__ekeuf._getvalue(), is_error=qtju__syowx)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    zrjhf__ekeuf = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, zrjhf__ekeuf.data)
        teeg__rmal = c.box(typ.data, zrjhf__ekeuf.data)
        dbaz__uicux = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, zrjhf__ekeuf.indices)
        obe__khvs = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        qgs__itse = cgutils.get_or_insert_function(c.builder.module,
            obe__khvs, name='box_dict_str_array')
        tgtyb__jcji = cgutils.create_struct_proxy(types.Array(types.int32, 
            1, 'C'))(c.context, c.builder, dbaz__uicux.data)
        qrfj__iam = c.builder.extract_value(tgtyb__jcji.shape, 0)
        iqnie__ythz = tgtyb__jcji.data
        ewpq__dqy = cgutils.create_struct_proxy(types.Array(types.int8, 1, 'C')
            )(c.context, c.builder, dbaz__uicux.null_bitmap).data
        hjuxq__ibvr = c.builder.call(qgs__itse, [qrfj__iam, teeg__rmal,
            iqnie__ythz, ewpq__dqy])
        c.pyapi.decref(teeg__rmal)
    else:
        nbc__jeb = c.context.insert_const_string(c.builder.module, 'pyarrow')
        vnlrq__xpys = c.pyapi.import_module_noblock(nbc__jeb)
        qbv__zqwl = c.pyapi.object_getattr_string(vnlrq__xpys,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, zrjhf__ekeuf.data)
        teeg__rmal = c.box(typ.data, zrjhf__ekeuf.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, zrjhf__ekeuf
            .indices)
        zco__gxyh = c.box(dict_indices_arr_type, zrjhf__ekeuf.indices)
        psbvu__cjs = c.pyapi.call_method(qbv__zqwl, 'from_arrays', (
            zco__gxyh, teeg__rmal))
        nuny__rczvy = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        hjuxq__ibvr = c.pyapi.call_method(psbvu__cjs, 'to_numpy', (
            nuny__rczvy,))
        c.pyapi.decref(vnlrq__xpys)
        c.pyapi.decref(teeg__rmal)
        c.pyapi.decref(zco__gxyh)
        c.pyapi.decref(qbv__zqwl)
        c.pyapi.decref(psbvu__cjs)
        c.pyapi.decref(nuny__rczvy)
    c.context.nrt.decref(c.builder, typ, val)
    return hjuxq__ibvr


@overload(len, no_unliteral=True)
def overload_dict_arr_len(A):
    if isinstance(A, DictionaryArrayType):
        return lambda A: len(A._indices)


@overload_attribute(DictionaryArrayType, 'shape')
def overload_dict_arr_shape(A):
    return lambda A: (len(A._indices),)


@overload_attribute(DictionaryArrayType, 'ndim')
def overload_dict_arr_ndim(A):
    return lambda A: 1


@overload_attribute(DictionaryArrayType, 'size')
def overload_dict_arr_size(A):
    return lambda A: len(A._indices)


@overload_method(DictionaryArrayType, 'tolist', no_unliteral=True)
def overload_dict_arr_tolist(A):
    return lambda A: list(A)


overload_method(DictionaryArrayType, 'astype', no_unliteral=True)(
    overload_str_arr_astype)


@overload_method(DictionaryArrayType, 'copy', no_unliteral=True)
def overload_dict_arr_copy(A):

    def copy_impl(A):
        return init_dict_arr(A._data.copy(), A._indices.copy(), A.
            _has_global_dictionary)
    return copy_impl


@overload_attribute(DictionaryArrayType, 'dtype')
def overload_dict_arr_dtype(A):
    return lambda A: A._data.dtype


@overload_attribute(DictionaryArrayType, 'nbytes')
def dict_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._indices.nbytes


@lower_constant(DictionaryArrayType)
def lower_constant_dict_arr(context, builder, typ, pyval):
    if bodo.hiframes.boxing._use_dict_str_type and isinstance(pyval, np.ndarray
        ):
        pyval = pa.array(pyval).dictionary_encode()
    ftin__wpwme = pyval.dictionary.to_numpy(False)
    pbp__ddje = pd.array(pyval.indices, 'Int32')
    ftin__wpwme = context.get_constant_generic(builder, typ.data, ftin__wpwme)
    pbp__ddje = context.get_constant_generic(builder, dict_indices_arr_type,
        pbp__ddje)
    pbq__tykg = context.get_constant(types.bool_, False)
    nnmoy__ptkmc = lir.Constant.literal_struct([ftin__wpwme, pbp__ddje,
        pbq__tykg])
    return nnmoy__ptkmc


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            fhc__kctew = A._indices[ind]
            return A._data[fhc__kctew]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        drfd__efmyq = A._data
        cqroc__lebm = A._indices
        qrfj__iam = len(cqroc__lebm)
        mnh__qbsbw = [get_str_arr_item_length(drfd__efmyq, i) for i in
            range(len(drfd__efmyq))]
        uon__jrd = 0
        for i in range(qrfj__iam):
            if not bodo.libs.array_kernels.isna(cqroc__lebm, i):
                uon__jrd += mnh__qbsbw[cqroc__lebm[i]]
        krubd__sygx = pre_alloc_string_array(qrfj__iam, uon__jrd)
        for i in range(qrfj__iam):
            if bodo.libs.array_kernels.isna(cqroc__lebm, i):
                bodo.libs.array_kernels.setna(krubd__sygx, i)
                continue
            ind = cqroc__lebm[i]
            if bodo.libs.array_kernels.isna(drfd__efmyq, ind):
                bodo.libs.array_kernels.setna(krubd__sygx, i)
                continue
            krubd__sygx[i] = drfd__efmyq[ind]
        return krubd__sygx
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    fhc__kctew = -1
    drfd__efmyq = arr._data
    for i in range(len(drfd__efmyq)):
        if bodo.libs.array_kernels.isna(drfd__efmyq, i):
            continue
        if drfd__efmyq[i] == val:
            fhc__kctew = i
            break
    return fhc__kctew


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    qrfj__iam = len(arr)
    fhc__kctew = find_dict_ind(arr, val)
    if fhc__kctew == -1:
        return init_bool_array(np.full(qrfj__iam, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == fhc__kctew


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    qrfj__iam = len(arr)
    fhc__kctew = find_dict_ind(arr, val)
    if fhc__kctew == -1:
        return init_bool_array(np.full(qrfj__iam, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != fhc__kctew


def get_binary_op_overload(op, lhs, rhs):
    if op == operator.eq:
        if lhs == dict_str_arr_type and types.unliteral(rhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_eq(lhs, rhs)
        if rhs == dict_str_arr_type and types.unliteral(lhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_eq(rhs, lhs)
    if op == operator.ne:
        if lhs == dict_str_arr_type and types.unliteral(rhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_ne(lhs, rhs)
        if rhs == dict_str_arr_type and types.unliteral(lhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_ne(rhs, lhs)


def convert_dict_arr_to_int(arr, dtype):
    return arr


@overload(convert_dict_arr_to_int)
def convert_dict_arr_to_int_overload(arr, dtype):

    def impl(arr, dtype):
        ijzw__jfm = arr._data
        fxq__tngwc = bodo.libs.int_arr_ext.alloc_int_array(len(ijzw__jfm),
            dtype)
        for ytt__zaab in range(len(ijzw__jfm)):
            if bodo.libs.array_kernels.isna(ijzw__jfm, ytt__zaab):
                bodo.libs.array_kernels.setna(fxq__tngwc, ytt__zaab)
                continue
            fxq__tngwc[ytt__zaab] = np.int64(ijzw__jfm[ytt__zaab])
        qrfj__iam = len(arr)
        cqroc__lebm = arr._indices
        krubd__sygx = bodo.libs.int_arr_ext.alloc_int_array(qrfj__iam, dtype)
        for i in range(qrfj__iam):
            if bodo.libs.array_kernels.isna(cqroc__lebm, i):
                bodo.libs.array_kernels.setna(krubd__sygx, i)
                continue
            krubd__sygx[i] = fxq__tngwc[cqroc__lebm[i]]
        return krubd__sygx
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    yfe__qmy = len(arrs)
    wvs__ymi = 'def impl(arrs, sep):\n'
    wvs__ymi += '  ind_map = {}\n'
    wvs__ymi += '  out_strs = []\n'
    wvs__ymi += '  n = len(arrs[0])\n'
    for i in range(yfe__qmy):
        wvs__ymi += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(yfe__qmy):
        wvs__ymi += f'  data{i} = arrs[{i}]._data\n'
    wvs__ymi += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    wvs__ymi += '  for i in range(n):\n'
    wzmt__upw = ' or '.join([f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for
        i in range(yfe__qmy)])
    wvs__ymi += f'    if {wzmt__upw}:\n'
    wvs__ymi += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    wvs__ymi += '      continue\n'
    for i in range(yfe__qmy):
        wvs__ymi += f'    ind{i} = indices{i}[i]\n'
    vux__bqp = '(' + ', '.join(f'ind{i}' for i in range(yfe__qmy)) + ')'
    wvs__ymi += f'    if {vux__bqp} not in ind_map:\n'
    wvs__ymi += '      out_ind = len(out_strs)\n'
    wvs__ymi += f'      ind_map[{vux__bqp}] = out_ind\n'
    crwx__lkwct = "''" if is_overload_none(sep) else 'sep'
    aljnu__jmys = ', '.join([f'data{i}[ind{i}]' for i in range(yfe__qmy)])
    wvs__ymi += f'      v = {crwx__lkwct}.join([{aljnu__jmys}])\n'
    wvs__ymi += '      out_strs.append(v)\n'
    wvs__ymi += '    else:\n'
    wvs__ymi += f'      out_ind = ind_map[{vux__bqp}]\n'
    wvs__ymi += '    out_indices[i] = out_ind\n'
    wvs__ymi += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    wvs__ymi += (
        '  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)\n'
        )
    smb__yxg = {}
    exec(wvs__ymi, {'bodo': bodo, 'numba': numba, 'np': np}, smb__yxg)
    impl = smb__yxg['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    jadtn__fglu = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    yso__ijy = toty(fromty)
    swnh__hyia = context.compile_internal(builder, jadtn__fglu, yso__ijy, (
        val,))
    return impl_ret_new_ref(context, builder, toty, swnh__hyia)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    ftin__wpwme = arr._data
    bdzh__mpp = len(ftin__wpwme)
    unfz__gmsb = pre_alloc_string_array(bdzh__mpp, -1)
    if regex:
        ecdf__nfn = re.compile(pat, flags)
        for i in range(bdzh__mpp):
            if bodo.libs.array_kernels.isna(ftin__wpwme, i):
                bodo.libs.array_kernels.setna(unfz__gmsb, i)
                continue
            unfz__gmsb[i] = ecdf__nfn.sub(repl=repl, string=ftin__wpwme[i])
    else:
        for i in range(bdzh__mpp):
            if bodo.libs.array_kernels.isna(ftin__wpwme, i):
                bodo.libs.array_kernels.setna(unfz__gmsb, i)
                continue
            unfz__gmsb[i] = ftin__wpwme[i].replace(pat, repl)
    return init_dict_arr(unfz__gmsb, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    zrjhf__ekeuf = arr._data
    zdf__ukcbo = len(zrjhf__ekeuf)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(zdf__ukcbo)
    for i in range(zdf__ukcbo):
        dict_arr_out[i] = zrjhf__ekeuf[i].startswith(pat)
    pbp__ddje = arr._indices
    gsmvs__bxz = len(pbp__ddje)
    krubd__sygx = bodo.libs.bool_arr_ext.alloc_bool_array(gsmvs__bxz)
    for i in range(gsmvs__bxz):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(krubd__sygx, i)
        else:
            krubd__sygx[i] = dict_arr_out[pbp__ddje[i]]
    return krubd__sygx


@register_jitable
def str_endswith(arr, pat, na):
    zrjhf__ekeuf = arr._data
    zdf__ukcbo = len(zrjhf__ekeuf)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(zdf__ukcbo)
    for i in range(zdf__ukcbo):
        dict_arr_out[i] = zrjhf__ekeuf[i].endswith(pat)
    pbp__ddje = arr._indices
    gsmvs__bxz = len(pbp__ddje)
    krubd__sygx = bodo.libs.bool_arr_ext.alloc_bool_array(gsmvs__bxz)
    for i in range(gsmvs__bxz):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(krubd__sygx, i)
        else:
            krubd__sygx[i] = dict_arr_out[pbp__ddje[i]]
    return krubd__sygx


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    zrjhf__ekeuf = arr._data
    wmy__bgjys = pd.Series(zrjhf__ekeuf)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = wmy__bgjys.array._str_contains(pat, case, flags, na,
            regex)
    pbp__ddje = arr._indices
    gsmvs__bxz = len(pbp__ddje)
    krubd__sygx = bodo.libs.bool_arr_ext.alloc_bool_array(gsmvs__bxz)
    for i in range(gsmvs__bxz):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(krubd__sygx, i)
        else:
            krubd__sygx[i] = dict_arr_out[pbp__ddje[i]]
    return krubd__sygx


@register_jitable
def str_contains_non_regex(arr, pat, case):
    zrjhf__ekeuf = arr._data
    zdf__ukcbo = len(zrjhf__ekeuf)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(zdf__ukcbo)
    if not case:
        akgtx__dng = pat.upper()
    for i in range(zdf__ukcbo):
        if case:
            dict_arr_out[i] = pat in zrjhf__ekeuf[i]
        else:
            dict_arr_out[i] = akgtx__dng in zrjhf__ekeuf[i].upper()
    pbp__ddje = arr._indices
    gsmvs__bxz = len(pbp__ddje)
    krubd__sygx = bodo.libs.bool_arr_ext.alloc_bool_array(gsmvs__bxz)
    for i in range(gsmvs__bxz):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(krubd__sygx, i)
        else:
            krubd__sygx[i] = dict_arr_out[pbp__ddje[i]]
    return krubd__sygx


def create_simple_str2str_methods(func_name, func_args):
    wvs__ymi = f"""def str_{func_name}({', '.join(func_args)}):
    data_arr = arr._data
    n_data = len(data_arr)
    out_str_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_data, -1)
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            bodo.libs.array_kernels.setna(out_str_arr, i)
            continue
        out_str_arr[i] = data_arr[i].{func_name}({', '.join(func_args[1:])})
    return init_dict_arr(out_str_arr, arr._indices.copy(), arr._has_global_dictionary)
"""
    smb__yxg = {}
    exec(wvs__ymi, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, smb__yxg)
    return smb__yxg[f'str_{func_name}']


def _register_simple_str2str_methods():
    bqr__lra = {**dict.fromkeys(['capitalize', 'lower', 'swapcase', 'title',
        'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip', 'strip'],
        ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust', 'rjust'],
        ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'], ('arr',
        'width'))}
    for func_name in bqr__lra.keys():
        hpwy__qcugg = create_simple_str2str_methods(func_name, bqr__lra[
            func_name])
        hpwy__qcugg = register_jitable(hpwy__qcugg)
        globals()[f'str_{func_name}'] = hpwy__qcugg


_register_simple_str2str_methods()


def create_find_methods(func_name):
    wvs__ymi = f"""def str_{func_name}(arr, sub, start, end):
  data_arr = arr._data
  indices_arr = arr._indices
  n_data = len(data_arr)
  n_indices = len(indices_arr)
  tmp_dict_arr = bodo.libs.int_arr_ext.alloc_int_array(n_data, np.int64)
  out_int_arr = bodo.libs.int_arr_ext.alloc_int_array(n_indices, np.int64)
  for i in range(n_data):
    if bodo.libs.array_kernels.isna(data_arr, i):
      bodo.libs.array_kernels.setna(tmp_dict_arr, i)
      continue
    tmp_dict_arr[i] = data_arr[i].{func_name}(sub, start, end)
  for i in range(n_indices):
    if bodo.libs.array_kernels.isna(indices_arr, i) or bodo.libs.array_kernels.isna(
      tmp_dict_arr, indices_arr[i]
    ):
      bodo.libs.array_kernels.setna(out_int_arr, i)
    else:
      out_int_arr[i] = tmp_dict_arr[indices_arr[i]]
  return out_int_arr"""
    smb__yxg = {}
    exec(wvs__ymi, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, smb__yxg)
    return smb__yxg[f'str_{func_name}']


def _register_find_methods():
    zuy__tpag = ['find', 'rfind']
    for func_name in zuy__tpag:
        hpwy__qcugg = create_find_methods(func_name)
        hpwy__qcugg = register_jitable(hpwy__qcugg)
        globals()[f'str_{func_name}'] = hpwy__qcugg


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    ftin__wpwme = arr._data
    pbp__ddje = arr._indices
    bdzh__mpp = len(ftin__wpwme)
    gsmvs__bxz = len(pbp__ddje)
    zrtks__qpzqg = bodo.libs.int_arr_ext.alloc_int_array(bdzh__mpp, np.int64)
    tvi__xzoub = bodo.libs.int_arr_ext.alloc_int_array(gsmvs__bxz, np.int64)
    regex = re.compile(pat, flags)
    for i in range(bdzh__mpp):
        if bodo.libs.array_kernels.isna(ftin__wpwme, i):
            bodo.libs.array_kernels.setna(zrtks__qpzqg, i)
            continue
        zrtks__qpzqg[i] = bodo.libs.str_ext.str_findall_count(regex,
            ftin__wpwme[i])
    for i in range(gsmvs__bxz):
        if bodo.libs.array_kernels.isna(pbp__ddje, i
            ) or bodo.libs.array_kernels.isna(zrtks__qpzqg, pbp__ddje[i]):
            bodo.libs.array_kernels.setna(tvi__xzoub, i)
        else:
            tvi__xzoub[i] = zrtks__qpzqg[pbp__ddje[i]]
    return tvi__xzoub


@register_jitable
def str_len(arr):
    ftin__wpwme = arr._data
    pbp__ddje = arr._indices
    gsmvs__bxz = len(pbp__ddje)
    zrtks__qpzqg = bodo.libs.array_kernels.get_arr_lens(ftin__wpwme, False)
    tvi__xzoub = bodo.libs.int_arr_ext.alloc_int_array(gsmvs__bxz, np.int64)
    for i in range(gsmvs__bxz):
        if bodo.libs.array_kernels.isna(pbp__ddje, i
            ) or bodo.libs.array_kernels.isna(zrtks__qpzqg, pbp__ddje[i]):
            bodo.libs.array_kernels.setna(tvi__xzoub, i)
        else:
            tvi__xzoub[i] = zrtks__qpzqg[pbp__ddje[i]]
    return tvi__xzoub


@register_jitable
def str_slice(arr, start, stop, step):
    ftin__wpwme = arr._data
    bdzh__mpp = len(ftin__wpwme)
    unfz__gmsb = bodo.libs.str_arr_ext.pre_alloc_string_array(bdzh__mpp, -1)
    for i in range(bdzh__mpp):
        if bodo.libs.array_kernels.isna(ftin__wpwme, i):
            bodo.libs.array_kernels.setna(unfz__gmsb, i)
            continue
        unfz__gmsb[i] = ftin__wpwme[i][start:stop:step]
    return init_dict_arr(unfz__gmsb, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    ftin__wpwme = arr._data
    pbp__ddje = arr._indices
    bdzh__mpp = len(ftin__wpwme)
    gsmvs__bxz = len(pbp__ddje)
    unfz__gmsb = pre_alloc_string_array(bdzh__mpp, -1)
    krubd__sygx = pre_alloc_string_array(gsmvs__bxz, -1)
    for ytt__zaab in range(bdzh__mpp):
        if bodo.libs.array_kernels.isna(ftin__wpwme, ytt__zaab) or not -len(
            ftin__wpwme[ytt__zaab]) <= i < len(ftin__wpwme[ytt__zaab]):
            bodo.libs.array_kernels.setna(unfz__gmsb, ytt__zaab)
            continue
        unfz__gmsb[ytt__zaab] = ftin__wpwme[ytt__zaab][i]
    for ytt__zaab in range(gsmvs__bxz):
        if bodo.libs.array_kernels.isna(pbp__ddje, ytt__zaab
            ) or bodo.libs.array_kernels.isna(unfz__gmsb, pbp__ddje[ytt__zaab]
            ):
            bodo.libs.array_kernels.setna(krubd__sygx, ytt__zaab)
            continue
        krubd__sygx[ytt__zaab] = unfz__gmsb[pbp__ddje[ytt__zaab]]
    return krubd__sygx


@register_jitable
def str_repeat_int(arr, repeats):
    ftin__wpwme = arr._data
    bdzh__mpp = len(ftin__wpwme)
    unfz__gmsb = pre_alloc_string_array(bdzh__mpp, -1)
    for i in range(bdzh__mpp):
        if bodo.libs.array_kernels.isna(ftin__wpwme, i):
            bodo.libs.array_kernels.setna(unfz__gmsb, i)
            continue
        unfz__gmsb[i] = ftin__wpwme[i] * repeats
    return init_dict_arr(unfz__gmsb, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    wvs__ymi = f"""def str_{func_name}(arr):
    data_arr = arr._data
    indices_arr = arr._indices
    n_data = len(data_arr)
    n_indices = len(indices_arr)
    out_dict_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n_data)
    out_bool_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n_indices)
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            bodo.libs.array_kernels.setna(out_dict_arr, i)
            continue
        out_dict_arr[i] = np.bool_(data_arr[i].{func_name}())
    for i in range(n_indices):
        if bodo.libs.array_kernels.isna(indices_arr, i) or bodo.libs.array_kernels.isna(
            data_arr, indices_arr[i]        ):
            bodo.libs.array_kernels.setna(out_bool_arr, i)
        else:
            out_bool_arr[i] = out_dict_arr[indices_arr[i]]
    return out_bool_arr"""
    smb__yxg = {}
    exec(wvs__ymi, {'bodo': bodo, 'numba': numba, 'np': np, 'init_dict_arr':
        init_dict_arr}, smb__yxg)
    return smb__yxg[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        hpwy__qcugg = create_str2bool_methods(func_name)
        hpwy__qcugg = register_jitable(hpwy__qcugg)
        globals()[f'str_{func_name}'] = hpwy__qcugg


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    ftin__wpwme = arr._data
    pbp__ddje = arr._indices
    bdzh__mpp = len(ftin__wpwme)
    gsmvs__bxz = len(pbp__ddje)
    regex = re.compile(pat, flags=flags)
    flxi__gzn = []
    for xwm__wwop in range(n_cols):
        flxi__gzn.append(pre_alloc_string_array(bdzh__mpp, -1))
    ecoot__bii = bodo.libs.bool_arr_ext.alloc_bool_array(bdzh__mpp)
    kjudx__gflxj = pbp__ddje.copy()
    for i in range(bdzh__mpp):
        if bodo.libs.array_kernels.isna(ftin__wpwme, i):
            ecoot__bii[i] = True
            for ytt__zaab in range(n_cols):
                bodo.libs.array_kernels.setna(flxi__gzn[ytt__zaab], i)
            continue
        bwee__tnyl = regex.search(ftin__wpwme[i])
        if bwee__tnyl:
            ecoot__bii[i] = False
            jqats__zgq = bwee__tnyl.groups()
            for ytt__zaab in range(n_cols):
                flxi__gzn[ytt__zaab][i] = jqats__zgq[ytt__zaab]
        else:
            ecoot__bii[i] = True
            for ytt__zaab in range(n_cols):
                bodo.libs.array_kernels.setna(flxi__gzn[ytt__zaab], i)
    for i in range(gsmvs__bxz):
        if ecoot__bii[kjudx__gflxj[i]]:
            bodo.libs.array_kernels.setna(kjudx__gflxj, i)
    zufv__whnty = [init_dict_arr(flxi__gzn[i], kjudx__gflxj.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return zufv__whnty


def create_extractall_methods(is_multi_group):
    zbvrn__zofr = '_multi' if is_multi_group else ''
    wvs__ymi = f"""def str_extractall{zbvrn__zofr}(arr, regex, n_cols, index_arr):
    data_arr = arr._data
    indices_arr = arr._indices
    n_data = len(data_arr)
    n_indices = len(indices_arr)
    indices_count = [0 for _ in range(n_data)]
    for i in range(n_indices):
        if not bodo.libs.array_kernels.isna(indices_arr, i):
            indices_count[indices_arr[i]] += 1
    dict_group_count = []
    out_dict_len = out_ind_len = 0
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            continue
        m = regex.findall(data_arr[i])
        dict_group_count.append((out_dict_len, len(m)))
        out_dict_len += len(m)
        out_ind_len += indices_count[i] * len(m)
    out_dict_arr_list = []
    for _ in range(n_cols):
        out_dict_arr_list.append(pre_alloc_string_array(out_dict_len, -1))
    out_indices_arr = bodo.libs.int_arr_ext.alloc_int_array(out_ind_len, np.int32)
    out_ind_arr = bodo.utils.utils.alloc_type(out_ind_len, index_arr, (-1,))
    out_match_arr = np.empty(out_ind_len, np.int64)
    curr_ind = 0
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            continue
        m = regex.findall(data_arr[i])
        for s in m:
            for j in range(n_cols):
                out_dict_arr_list[j][curr_ind] = s{'[j]' if is_multi_group else ''}
            curr_ind += 1
    curr_ind = 0
    for i in range(n_indices):
        if bodo.libs.array_kernels.isna(indices_arr, i):
            continue
        n_rows = dict_group_count[indices_arr[i]][1]
        for k in range(n_rows):
            out_indices_arr[curr_ind] = dict_group_count[indices_arr[i]][0] + k
            out_ind_arr[curr_ind] = index_arr[i]
            out_match_arr[curr_ind] = k
            curr_ind += 1
    out_arr_list = [
        init_dict_arr(
            out_dict_arr_list[i], out_indices_arr.copy(), arr._has_global_dictionary
        )
        for i in range(n_cols)
    ]
    return (out_ind_arr, out_match_arr, out_arr_list) 
"""
    smb__yxg = {}
    exec(wvs__ymi, {'bodo': bodo, 'numba': numba, 'np': np, 'init_dict_arr':
        init_dict_arr, 'pre_alloc_string_array': pre_alloc_string_array},
        smb__yxg)
    return smb__yxg[f'str_extractall{zbvrn__zofr}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        zbvrn__zofr = '_multi' if is_multi_group else ''
        hpwy__qcugg = create_extractall_methods(is_multi_group)
        hpwy__qcugg = register_jitable(hpwy__qcugg)
        globals()[f'str_extractall{zbvrn__zofr}'] = hpwy__qcugg


_register_extractall_methods()
