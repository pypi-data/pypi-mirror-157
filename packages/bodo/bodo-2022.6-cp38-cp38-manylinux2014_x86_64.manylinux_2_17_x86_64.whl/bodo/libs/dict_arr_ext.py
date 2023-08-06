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
        kqb__wubbq = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, kqb__wubbq)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        pvrfg__luqnn, twcfk__jdwu, ystu__ciq = args
        imln__nbcj = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        imln__nbcj.data = pvrfg__luqnn
        imln__nbcj.indices = twcfk__jdwu
        imln__nbcj.has_global_dictionary = ystu__ciq
        context.nrt.incref(builder, signature.args[0], pvrfg__luqnn)
        context.nrt.incref(builder, signature.args[1], twcfk__jdwu)
        return imln__nbcj._getvalue()
    anyv__lbk = DictionaryArrayType(data_t)
    tty__xmvnc = anyv__lbk(data_t, indices_t, types.bool_)
    return tty__xmvnc, codegen


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
        cob__kexam = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(cob__kexam, [val])
        c.pyapi.decref(cob__kexam)
    imln__nbcj = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ofzx__rwjfw = c.pyapi.object_getattr_string(val, 'dictionary')
    bljv__ittc = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    ymfsf__mbfvn = c.pyapi.call_method(ofzx__rwjfw, 'to_numpy', (bljv__ittc,))
    imln__nbcj.data = c.unbox(typ.data, ymfsf__mbfvn).value
    ojt__qyzh = c.pyapi.object_getattr_string(val, 'indices')
    ripb__spon = c.context.insert_const_string(c.builder.module, 'pandas')
    anrpc__uuyt = c.pyapi.import_module_noblock(ripb__spon)
    vzb__poyaa = c.pyapi.string_from_constant_string('Int32')
    wrg__goyfg = c.pyapi.call_method(anrpc__uuyt, 'array', (ojt__qyzh,
        vzb__poyaa))
    imln__nbcj.indices = c.unbox(dict_indices_arr_type, wrg__goyfg).value
    imln__nbcj.has_global_dictionary = c.context.get_constant(types.bool_, 
        False)
    c.pyapi.decref(ofzx__rwjfw)
    c.pyapi.decref(bljv__ittc)
    c.pyapi.decref(ymfsf__mbfvn)
    c.pyapi.decref(ojt__qyzh)
    c.pyapi.decref(anrpc__uuyt)
    c.pyapi.decref(vzb__poyaa)
    c.pyapi.decref(wrg__goyfg)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    wcly__uwzmn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(imln__nbcj._getvalue(), is_error=wcly__uwzmn)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    imln__nbcj = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, imln__nbcj.data)
        ajxx__mjo = c.box(typ.data, imln__nbcj.data)
        kunnp__lxm = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, imln__nbcj.indices)
        wqn__ridpk = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        oaoi__fvjl = cgutils.get_or_insert_function(c.builder.module,
            wqn__ridpk, name='box_dict_str_array')
        gdbmi__sfuu = cgutils.create_struct_proxy(types.Array(types.int32, 
            1, 'C'))(c.context, c.builder, kunnp__lxm.data)
        tsmpm__uhpy = c.builder.extract_value(gdbmi__sfuu.shape, 0)
        uoz__pon = gdbmi__sfuu.data
        pll__llg = cgutils.create_struct_proxy(types.Array(types.int8, 1, 'C')
            )(c.context, c.builder, kunnp__lxm.null_bitmap).data
        ymfsf__mbfvn = c.builder.call(oaoi__fvjl, [tsmpm__uhpy, ajxx__mjo,
            uoz__pon, pll__llg])
        c.pyapi.decref(ajxx__mjo)
    else:
        ripb__spon = c.context.insert_const_string(c.builder.module, 'pyarrow')
        haqls__scjdo = c.pyapi.import_module_noblock(ripb__spon)
        isyv__fbkky = c.pyapi.object_getattr_string(haqls__scjdo,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, imln__nbcj.data)
        ajxx__mjo = c.box(typ.data, imln__nbcj.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, imln__nbcj.
            indices)
        ojt__qyzh = c.box(dict_indices_arr_type, imln__nbcj.indices)
        idkuz__ukrv = c.pyapi.call_method(isyv__fbkky, 'from_arrays', (
            ojt__qyzh, ajxx__mjo))
        bljv__ittc = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        ymfsf__mbfvn = c.pyapi.call_method(idkuz__ukrv, 'to_numpy', (
            bljv__ittc,))
        c.pyapi.decref(haqls__scjdo)
        c.pyapi.decref(ajxx__mjo)
        c.pyapi.decref(ojt__qyzh)
        c.pyapi.decref(isyv__fbkky)
        c.pyapi.decref(idkuz__ukrv)
        c.pyapi.decref(bljv__ittc)
    c.context.nrt.decref(c.builder, typ, val)
    return ymfsf__mbfvn


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
    miy__nus = pyval.dictionary.to_numpy(False)
    rql__yfok = pd.array(pyval.indices, 'Int32')
    miy__nus = context.get_constant_generic(builder, typ.data, miy__nus)
    rql__yfok = context.get_constant_generic(builder, dict_indices_arr_type,
        rql__yfok)
    mpt__aibgi = context.get_constant(types.bool_, False)
    gtm__jvvtz = lir.Constant.literal_struct([miy__nus, rql__yfok, mpt__aibgi])
    return gtm__jvvtz


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            pruxj__pmkq = A._indices[ind]
            return A._data[pruxj__pmkq]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        pvrfg__luqnn = A._data
        twcfk__jdwu = A._indices
        tsmpm__uhpy = len(twcfk__jdwu)
        kjt__ddliu = [get_str_arr_item_length(pvrfg__luqnn, i) for i in
            range(len(pvrfg__luqnn))]
        bndtz__pxjbf = 0
        for i in range(tsmpm__uhpy):
            if not bodo.libs.array_kernels.isna(twcfk__jdwu, i):
                bndtz__pxjbf += kjt__ddliu[twcfk__jdwu[i]]
        wswnq__sxwr = pre_alloc_string_array(tsmpm__uhpy, bndtz__pxjbf)
        for i in range(tsmpm__uhpy):
            if bodo.libs.array_kernels.isna(twcfk__jdwu, i):
                bodo.libs.array_kernels.setna(wswnq__sxwr, i)
                continue
            ind = twcfk__jdwu[i]
            if bodo.libs.array_kernels.isna(pvrfg__luqnn, ind):
                bodo.libs.array_kernels.setna(wswnq__sxwr, i)
                continue
            wswnq__sxwr[i] = pvrfg__luqnn[ind]
        return wswnq__sxwr
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    pruxj__pmkq = -1
    pvrfg__luqnn = arr._data
    for i in range(len(pvrfg__luqnn)):
        if bodo.libs.array_kernels.isna(pvrfg__luqnn, i):
            continue
        if pvrfg__luqnn[i] == val:
            pruxj__pmkq = i
            break
    return pruxj__pmkq


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    tsmpm__uhpy = len(arr)
    pruxj__pmkq = find_dict_ind(arr, val)
    if pruxj__pmkq == -1:
        return init_bool_array(np.full(tsmpm__uhpy, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == pruxj__pmkq


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    tsmpm__uhpy = len(arr)
    pruxj__pmkq = find_dict_ind(arr, val)
    if pruxj__pmkq == -1:
        return init_bool_array(np.full(tsmpm__uhpy, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != pruxj__pmkq


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
        mke__hlvom = arr._data
        bgfb__vgz = bodo.libs.int_arr_ext.alloc_int_array(len(mke__hlvom),
            dtype)
        for xrthn__qggc in range(len(mke__hlvom)):
            if bodo.libs.array_kernels.isna(mke__hlvom, xrthn__qggc):
                bodo.libs.array_kernels.setna(bgfb__vgz, xrthn__qggc)
                continue
            bgfb__vgz[xrthn__qggc] = np.int64(mke__hlvom[xrthn__qggc])
        tsmpm__uhpy = len(arr)
        twcfk__jdwu = arr._indices
        wswnq__sxwr = bodo.libs.int_arr_ext.alloc_int_array(tsmpm__uhpy, dtype)
        for i in range(tsmpm__uhpy):
            if bodo.libs.array_kernels.isna(twcfk__jdwu, i):
                bodo.libs.array_kernels.setna(wswnq__sxwr, i)
                continue
            wswnq__sxwr[i] = bgfb__vgz[twcfk__jdwu[i]]
        return wswnq__sxwr
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    mcy__ifj = len(arrs)
    kmjjo__mmwh = 'def impl(arrs, sep):\n'
    kmjjo__mmwh += '  ind_map = {}\n'
    kmjjo__mmwh += '  out_strs = []\n'
    kmjjo__mmwh += '  n = len(arrs[0])\n'
    for i in range(mcy__ifj):
        kmjjo__mmwh += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(mcy__ifj):
        kmjjo__mmwh += f'  data{i} = arrs[{i}]._data\n'
    kmjjo__mmwh += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    kmjjo__mmwh += '  for i in range(n):\n'
    flici__bxpby = ' or '.join([
        f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for i in range(mcy__ifj)]
        )
    kmjjo__mmwh += f'    if {flici__bxpby}:\n'
    kmjjo__mmwh += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    kmjjo__mmwh += '      continue\n'
    for i in range(mcy__ifj):
        kmjjo__mmwh += f'    ind{i} = indices{i}[i]\n'
    zuoj__wlnii = '(' + ', '.join(f'ind{i}' for i in range(mcy__ifj)) + ')'
    kmjjo__mmwh += f'    if {zuoj__wlnii} not in ind_map:\n'
    kmjjo__mmwh += '      out_ind = len(out_strs)\n'
    kmjjo__mmwh += f'      ind_map[{zuoj__wlnii}] = out_ind\n'
    edw__dmi = "''" if is_overload_none(sep) else 'sep'
    dyhd__rcuvn = ', '.join([f'data{i}[ind{i}]' for i in range(mcy__ifj)])
    kmjjo__mmwh += f'      v = {edw__dmi}.join([{dyhd__rcuvn}])\n'
    kmjjo__mmwh += '      out_strs.append(v)\n'
    kmjjo__mmwh += '    else:\n'
    kmjjo__mmwh += f'      out_ind = ind_map[{zuoj__wlnii}]\n'
    kmjjo__mmwh += '    out_indices[i] = out_ind\n'
    kmjjo__mmwh += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    kmjjo__mmwh += """  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)
"""
    uwo__nhpa = {}
    exec(kmjjo__mmwh, {'bodo': bodo, 'numba': numba, 'np': np}, uwo__nhpa)
    impl = uwo__nhpa['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    siumx__dsrv = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    tty__xmvnc = toty(fromty)
    msyqh__pkcjy = context.compile_internal(builder, siumx__dsrv,
        tty__xmvnc, (val,))
    return impl_ret_new_ref(context, builder, toty, msyqh__pkcjy)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    miy__nus = arr._data
    aorcz__uew = len(miy__nus)
    kie__zwvl = pre_alloc_string_array(aorcz__uew, -1)
    if regex:
        hbnuq__axdy = re.compile(pat, flags)
        for i in range(aorcz__uew):
            if bodo.libs.array_kernels.isna(miy__nus, i):
                bodo.libs.array_kernels.setna(kie__zwvl, i)
                continue
            kie__zwvl[i] = hbnuq__axdy.sub(repl=repl, string=miy__nus[i])
    else:
        for i in range(aorcz__uew):
            if bodo.libs.array_kernels.isna(miy__nus, i):
                bodo.libs.array_kernels.setna(kie__zwvl, i)
                continue
            kie__zwvl[i] = miy__nus[i].replace(pat, repl)
    return init_dict_arr(kie__zwvl, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    imln__nbcj = arr._data
    vdfcl__vtm = len(imln__nbcj)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(vdfcl__vtm)
    for i in range(vdfcl__vtm):
        dict_arr_out[i] = imln__nbcj[i].startswith(pat)
    rql__yfok = arr._indices
    vzgu__ondhx = len(rql__yfok)
    wswnq__sxwr = bodo.libs.bool_arr_ext.alloc_bool_array(vzgu__ondhx)
    for i in range(vzgu__ondhx):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(wswnq__sxwr, i)
        else:
            wswnq__sxwr[i] = dict_arr_out[rql__yfok[i]]
    return wswnq__sxwr


@register_jitable
def str_endswith(arr, pat, na):
    imln__nbcj = arr._data
    vdfcl__vtm = len(imln__nbcj)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(vdfcl__vtm)
    for i in range(vdfcl__vtm):
        dict_arr_out[i] = imln__nbcj[i].endswith(pat)
    rql__yfok = arr._indices
    vzgu__ondhx = len(rql__yfok)
    wswnq__sxwr = bodo.libs.bool_arr_ext.alloc_bool_array(vzgu__ondhx)
    for i in range(vzgu__ondhx):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(wswnq__sxwr, i)
        else:
            wswnq__sxwr[i] = dict_arr_out[rql__yfok[i]]
    return wswnq__sxwr


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    imln__nbcj = arr._data
    hbjyq__hjbz = pd.Series(imln__nbcj)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = hbjyq__hjbz.array._str_contains(pat, case, flags, na,
            regex)
    rql__yfok = arr._indices
    vzgu__ondhx = len(rql__yfok)
    wswnq__sxwr = bodo.libs.bool_arr_ext.alloc_bool_array(vzgu__ondhx)
    for i in range(vzgu__ondhx):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(wswnq__sxwr, i)
        else:
            wswnq__sxwr[i] = dict_arr_out[rql__yfok[i]]
    return wswnq__sxwr


@register_jitable
def str_contains_non_regex(arr, pat, case):
    imln__nbcj = arr._data
    vdfcl__vtm = len(imln__nbcj)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(vdfcl__vtm)
    if not case:
        nrchh__dknyt = pat.upper()
    for i in range(vdfcl__vtm):
        if case:
            dict_arr_out[i] = pat in imln__nbcj[i]
        else:
            dict_arr_out[i] = nrchh__dknyt in imln__nbcj[i].upper()
    rql__yfok = arr._indices
    vzgu__ondhx = len(rql__yfok)
    wswnq__sxwr = bodo.libs.bool_arr_ext.alloc_bool_array(vzgu__ondhx)
    for i in range(vzgu__ondhx):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(wswnq__sxwr, i)
        else:
            wswnq__sxwr[i] = dict_arr_out[rql__yfok[i]]
    return wswnq__sxwr


def create_simple_str2str_methods(func_name, func_args):
    kmjjo__mmwh = f"""def str_{func_name}({', '.join(func_args)}):
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
    uwo__nhpa = {}
    exec(kmjjo__mmwh, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, uwo__nhpa)
    return uwo__nhpa[f'str_{func_name}']


def _register_simple_str2str_methods():
    izt__rtd = {**dict.fromkeys(['capitalize', 'lower', 'swapcase', 'title',
        'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip', 'strip'],
        ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust', 'rjust'],
        ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'], ('arr',
        'width'))}
    for func_name in izt__rtd.keys():
        hupv__haow = create_simple_str2str_methods(func_name, izt__rtd[
            func_name])
        hupv__haow = register_jitable(hupv__haow)
        globals()[f'str_{func_name}'] = hupv__haow


_register_simple_str2str_methods()


def create_find_methods(func_name):
    kmjjo__mmwh = f"""def str_{func_name}(arr, sub, start, end):
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
    uwo__nhpa = {}
    exec(kmjjo__mmwh, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, uwo__nhpa)
    return uwo__nhpa[f'str_{func_name}']


def _register_find_methods():
    ckct__cafx = ['find', 'rfind']
    for func_name in ckct__cafx:
        hupv__haow = create_find_methods(func_name)
        hupv__haow = register_jitable(hupv__haow)
        globals()[f'str_{func_name}'] = hupv__haow


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    miy__nus = arr._data
    rql__yfok = arr._indices
    aorcz__uew = len(miy__nus)
    vzgu__ondhx = len(rql__yfok)
    moyf__vlvj = bodo.libs.int_arr_ext.alloc_int_array(aorcz__uew, np.int64)
    ppc__mvebz = bodo.libs.int_arr_ext.alloc_int_array(vzgu__ondhx, np.int64)
    regex = re.compile(pat, flags)
    for i in range(aorcz__uew):
        if bodo.libs.array_kernels.isna(miy__nus, i):
            bodo.libs.array_kernels.setna(moyf__vlvj, i)
            continue
        moyf__vlvj[i] = bodo.libs.str_ext.str_findall_count(regex, miy__nus[i])
    for i in range(vzgu__ondhx):
        if bodo.libs.array_kernels.isna(rql__yfok, i
            ) or bodo.libs.array_kernels.isna(moyf__vlvj, rql__yfok[i]):
            bodo.libs.array_kernels.setna(ppc__mvebz, i)
        else:
            ppc__mvebz[i] = moyf__vlvj[rql__yfok[i]]
    return ppc__mvebz


@register_jitable
def str_len(arr):
    miy__nus = arr._data
    rql__yfok = arr._indices
    vzgu__ondhx = len(rql__yfok)
    moyf__vlvj = bodo.libs.array_kernels.get_arr_lens(miy__nus, False)
    ppc__mvebz = bodo.libs.int_arr_ext.alloc_int_array(vzgu__ondhx, np.int64)
    for i in range(vzgu__ondhx):
        if bodo.libs.array_kernels.isna(rql__yfok, i
            ) or bodo.libs.array_kernels.isna(moyf__vlvj, rql__yfok[i]):
            bodo.libs.array_kernels.setna(ppc__mvebz, i)
        else:
            ppc__mvebz[i] = moyf__vlvj[rql__yfok[i]]
    return ppc__mvebz


@register_jitable
def str_slice(arr, start, stop, step):
    miy__nus = arr._data
    aorcz__uew = len(miy__nus)
    kie__zwvl = bodo.libs.str_arr_ext.pre_alloc_string_array(aorcz__uew, -1)
    for i in range(aorcz__uew):
        if bodo.libs.array_kernels.isna(miy__nus, i):
            bodo.libs.array_kernels.setna(kie__zwvl, i)
            continue
        kie__zwvl[i] = miy__nus[i][start:stop:step]
    return init_dict_arr(kie__zwvl, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    miy__nus = arr._data
    rql__yfok = arr._indices
    aorcz__uew = len(miy__nus)
    vzgu__ondhx = len(rql__yfok)
    kie__zwvl = pre_alloc_string_array(aorcz__uew, -1)
    wswnq__sxwr = pre_alloc_string_array(vzgu__ondhx, -1)
    for xrthn__qggc in range(aorcz__uew):
        if bodo.libs.array_kernels.isna(miy__nus, xrthn__qggc) or not -len(
            miy__nus[xrthn__qggc]) <= i < len(miy__nus[xrthn__qggc]):
            bodo.libs.array_kernels.setna(kie__zwvl, xrthn__qggc)
            continue
        kie__zwvl[xrthn__qggc] = miy__nus[xrthn__qggc][i]
    for xrthn__qggc in range(vzgu__ondhx):
        if bodo.libs.array_kernels.isna(rql__yfok, xrthn__qggc
            ) or bodo.libs.array_kernels.isna(kie__zwvl, rql__yfok[xrthn__qggc]
            ):
            bodo.libs.array_kernels.setna(wswnq__sxwr, xrthn__qggc)
            continue
        wswnq__sxwr[xrthn__qggc] = kie__zwvl[rql__yfok[xrthn__qggc]]
    return wswnq__sxwr


@register_jitable
def str_repeat_int(arr, repeats):
    miy__nus = arr._data
    aorcz__uew = len(miy__nus)
    kie__zwvl = pre_alloc_string_array(aorcz__uew, -1)
    for i in range(aorcz__uew):
        if bodo.libs.array_kernels.isna(miy__nus, i):
            bodo.libs.array_kernels.setna(kie__zwvl, i)
            continue
        kie__zwvl[i] = miy__nus[i] * repeats
    return init_dict_arr(kie__zwvl, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    kmjjo__mmwh = f"""def str_{func_name}(arr):
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
    uwo__nhpa = {}
    exec(kmjjo__mmwh, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, uwo__nhpa)
    return uwo__nhpa[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        hupv__haow = create_str2bool_methods(func_name)
        hupv__haow = register_jitable(hupv__haow)
        globals()[f'str_{func_name}'] = hupv__haow


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    miy__nus = arr._data
    rql__yfok = arr._indices
    aorcz__uew = len(miy__nus)
    vzgu__ondhx = len(rql__yfok)
    regex = re.compile(pat, flags=flags)
    jdf__wiu = []
    for skx__bln in range(n_cols):
        jdf__wiu.append(pre_alloc_string_array(aorcz__uew, -1))
    yogp__arn = bodo.libs.bool_arr_ext.alloc_bool_array(aorcz__uew)
    oawk__ddmwa = rql__yfok.copy()
    for i in range(aorcz__uew):
        if bodo.libs.array_kernels.isna(miy__nus, i):
            yogp__arn[i] = True
            for xrthn__qggc in range(n_cols):
                bodo.libs.array_kernels.setna(jdf__wiu[xrthn__qggc], i)
            continue
        sil__gxpv = regex.search(miy__nus[i])
        if sil__gxpv:
            yogp__arn[i] = False
            unaih__vgncr = sil__gxpv.groups()
            for xrthn__qggc in range(n_cols):
                jdf__wiu[xrthn__qggc][i] = unaih__vgncr[xrthn__qggc]
        else:
            yogp__arn[i] = True
            for xrthn__qggc in range(n_cols):
                bodo.libs.array_kernels.setna(jdf__wiu[xrthn__qggc], i)
    for i in range(vzgu__ondhx):
        if yogp__arn[oawk__ddmwa[i]]:
            bodo.libs.array_kernels.setna(oawk__ddmwa, i)
    rfa__vsziv = [init_dict_arr(jdf__wiu[i], oawk__ddmwa.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return rfa__vsziv


def create_extractall_methods(is_multi_group):
    bkbjl__cqu = '_multi' if is_multi_group else ''
    kmjjo__mmwh = f"""def str_extractall{bkbjl__cqu}(arr, regex, n_cols, index_arr):
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
    uwo__nhpa = {}
    exec(kmjjo__mmwh, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, uwo__nhpa)
    return uwo__nhpa[f'str_extractall{bkbjl__cqu}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        bkbjl__cqu = '_multi' if is_multi_group else ''
        hupv__haow = create_extractall_methods(is_multi_group)
        hupv__haow = register_jitable(hupv__haow)
        globals()[f'str_extractall{bkbjl__cqu}'] = hupv__haow


_register_extractall_methods()
