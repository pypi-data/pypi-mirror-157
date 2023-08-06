import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, bound_function, infer_getattr, infer_global, signature
from numba.extending import intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_jitable, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_str, is_overload_constant_int, is_overload_constant_str


def unliteral_all(args):
    return tuple(types.unliteral(a) for a in args)


ll.add_symbol('del_str', hstr_ext.del_str)
ll.add_symbol('unicode_to_utf8', hstr_ext.unicode_to_utf8)
ll.add_symbol('memcmp', hstr_ext.memcmp)
ll.add_symbol('int_to_hex', hstr_ext.int_to_hex)
string_type = types.unicode_type


@numba.njit
def contains_regex(e, in_str):
    with numba.objmode(res='bool_'):
        res = bool(e.search(in_str))
    return res


@numba.generated_jit
def str_findall_count(regex, in_str):

    def _str_findall_count_impl(regex, in_str):
        with numba.objmode(res='int64'):
            res = len(regex.findall(in_str))
        return res
    return _str_findall_count_impl


utf8_str_type = types.ArrayCTypes(types.Array(types.uint8, 1, 'C'))


@intrinsic
def unicode_to_utf8_and_len(typingctx, str_typ):
    assert str_typ in (string_type, types.Optional(string_type)) or isinstance(
        str_typ, types.StringLiteral)
    dng__jdq = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        rqkn__szqy, = args
        ysz__zgff = cgutils.create_struct_proxy(string_type)(context,
            builder, value=rqkn__szqy)
        sfist__bjg = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        scidd__udkkp = cgutils.create_struct_proxy(dng__jdq)(context, builder)
        is_ascii = builder.icmp_unsigned('==', ysz__zgff.is_ascii, lir.
            Constant(ysz__zgff.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (qyg__rvkq, ulkw__mqy):
            with qyg__rvkq:
                context.nrt.incref(builder, string_type, rqkn__szqy)
                sfist__bjg.data = ysz__zgff.data
                sfist__bjg.meminfo = ysz__zgff.meminfo
                scidd__udkkp.f1 = ysz__zgff.length
            with ulkw__mqy:
                ualk__ifkb = lir.FunctionType(lir.IntType(64), [lir.IntType
                    (8).as_pointer(), lir.IntType(8).as_pointer(), lir.
                    IntType(64), lir.IntType(32)])
                nub__iomuo = cgutils.get_or_insert_function(builder.module,
                    ualk__ifkb, name='unicode_to_utf8')
                cdj__kow = context.get_constant_null(types.voidptr)
                fvws__uceae = builder.call(nub__iomuo, [cdj__kow, ysz__zgff
                    .data, ysz__zgff.length, ysz__zgff.kind])
                scidd__udkkp.f1 = fvws__uceae
                caiv__uvq = builder.add(fvws__uceae, lir.Constant(lir.
                    IntType(64), 1))
                sfist__bjg.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=caiv__uvq, align=32)
                sfist__bjg.data = context.nrt.meminfo_data(builder,
                    sfist__bjg.meminfo)
                builder.call(nub__iomuo, [sfist__bjg.data, ysz__zgff.data,
                    ysz__zgff.length, ysz__zgff.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    sfist__bjg.data, [fvws__uceae]))
        scidd__udkkp.f0 = sfist__bjg._getvalue()
        return scidd__udkkp._getvalue()
    return dng__jdq(string_type), codegen


def unicode_to_utf8(s):
    return s


@overload(unicode_to_utf8)
def overload_unicode_to_utf8(s):
    return lambda s: unicode_to_utf8_and_len(s)[0]


@overload(max)
def overload_builtin_max(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload(min)
def overload_builtin_min(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@intrinsic
def memcmp(typingctx, dest_t, src_t, count_t=None):

    def codegen(context, builder, sig, args):
        ualk__ifkb = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        jmz__izyxj = cgutils.get_or_insert_function(builder.module,
            ualk__ifkb, name='memcmp')
        return builder.call(jmz__izyxj, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    unct__nslyf = n(10)

    def impl(n):
        if n == 0:
            return 1
        sozn__xrb = 0
        if n < 0:
            n = -n
            sozn__xrb += 1
        while n > 0:
            n = n // unct__nslyf
            sozn__xrb += 1
        return sozn__xrb
    return impl


class StdStringType(types.Opaque):

    def __init__(self):
        super(StdStringType, self).__init__(name='StdStringType')


std_str_type = StdStringType()
register_model(StdStringType)(models.OpaqueModel)
del_str = types.ExternalFunction('del_str', types.void(std_str_type))
get_c_str = types.ExternalFunction('get_c_str', types.voidptr(std_str_type))
dummy_use = numba.njit(lambda a: None)


@overload(int)
def int_str_overload(in_str, base=10):
    if in_str == string_type:
        if is_overload_constant_int(base) and get_overload_const_int(base
            ) == 10:

            def _str_to_int_impl(in_str, base=10):
                val = _str_to_int64(in_str._data, in_str._length)
                dummy_use(in_str)
                return val
            return _str_to_int_impl

        def _str_to_int_base_impl(in_str, base=10):
            val = _str_to_int64_base(in_str._data, in_str._length, base)
            dummy_use(in_str)
            return val
        return _str_to_int_base_impl


@infer_global(float)
class StrToFloat(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        [uqnyd__mqq] = args
        if isinstance(uqnyd__mqq, StdStringType):
            return signature(types.float64, uqnyd__mqq)
        if uqnyd__mqq == string_type:
            return signature(types.float64, uqnyd__mqq)


ll.add_symbol('init_string_const', hstr_ext.init_string_const)
ll.add_symbol('get_c_str', hstr_ext.get_c_str)
ll.add_symbol('str_to_int64', hstr_ext.str_to_int64)
ll.add_symbol('str_to_uint64', hstr_ext.str_to_uint64)
ll.add_symbol('str_to_int64_base', hstr_ext.str_to_int64_base)
ll.add_symbol('str_to_float64', hstr_ext.str_to_float64)
ll.add_symbol('str_to_float32', hstr_ext.str_to_float32)
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('str_from_float32', hstr_ext.str_from_float32)
ll.add_symbol('str_from_float64', hstr_ext.str_from_float64)
get_std_str_len = types.ExternalFunction('get_str_len', signature(types.
    intp, std_str_type))
init_string_from_chars = types.ExternalFunction('init_string_const',
    std_str_type(types.voidptr, types.intp))
_str_to_int64 = types.ExternalFunction('str_to_int64', signature(types.
    int64, types.voidptr, types.int64))
_str_to_uint64 = types.ExternalFunction('str_to_uint64', signature(types.
    uint64, types.voidptr, types.int64))
_str_to_int64_base = types.ExternalFunction('str_to_int64_base', signature(
    types.int64, types.voidptr, types.int64, types.int64))


def gen_unicode_to_std_str(context, builder, unicode_val):
    ysz__zgff = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    ualk__ifkb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    xjb__ijsn = cgutils.get_or_insert_function(builder.module, ualk__ifkb,
        name='init_string_const')
    return builder.call(xjb__ijsn, [ysz__zgff.data, ysz__zgff.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        xggtt__srztg = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(xggtt__srztg._data, bodo.libs.str_ext
            .get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return xggtt__srztg
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    ysz__zgff = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return ysz__zgff.data


@intrinsic
def unicode_to_std_str(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_unicode_to_std_str(context, builder, args[0])
    return std_str_type(string_type), codegen


@intrinsic
def std_str_to_unicode(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_std_str_to_unicode(context, builder, args[0], True)
    return string_type(std_str_type), codegen


class RandomAccessStringArrayType(types.ArrayCompatible):

    def __init__(self):
        super(RandomAccessStringArrayType, self).__init__(name=
            'RandomAccessStringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    def copy(self):
        RandomAccessStringArrayType()


random_access_string_array = RandomAccessStringArrayType()


@register_model(RandomAccessStringArrayType)
class RandomAccessStringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pcgb__llgpy = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, pcgb__llgpy)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        zpaqu__ktpz, = args
        fohv__galr = types.List(string_type)
        xyee__ksm = numba.cpython.listobj.ListInstance.allocate(context,
            builder, fohv__galr, zpaqu__ktpz)
        xyee__ksm.size = zpaqu__ktpz
        uhmla__mgsch = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        uhmla__mgsch.data = xyee__ksm.value
        return uhmla__mgsch._getvalue()
    return random_access_string_array(types.intp), codegen


@overload(operator.getitem, no_unliteral=True)
def random_access_str_arr_getitem(A, ind):
    if A != random_access_string_array:
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]


@overload(operator.setitem)
def random_access_str_arr_setitem(A, idx, val):
    if A != random_access_string_array:
        return
    if isinstance(idx, types.Integer):
        assert val == string_type

        def impl_scalar(A, idx, val):
            A._data[idx] = val
        return impl_scalar


@overload(len, no_unliteral=True)
def overload_str_arr_len(A):
    if A == random_access_string_array:
        return lambda A: len(A._data)


@overload_attribute(RandomAccessStringArrayType, 'shape')
def overload_str_arr_shape(A):
    return lambda A: (len(A._data),)


def alloc_random_access_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_str_ext_alloc_random_access_string_array
    ) = alloc_random_access_str_arr_equiv
str_from_float32 = types.ExternalFunction('str_from_float32', types.void(
    types.voidptr, types.float32))
str_from_float64 = types.ExternalFunction('str_from_float64', types.void(
    types.voidptr, types.float64))


def float_to_str(s, v):
    pass


@overload(float_to_str)
def float_to_str_overload(s, v):
    assert isinstance(v, types.Float)
    if v == types.float32:
        return lambda s, v: str_from_float32(s._data, v)
    return lambda s, v: str_from_float64(s._data, v)


@overload(str)
def float_str_overload(v):
    if isinstance(v, types.Float):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(v):
            if v == 0:
                return '0.0'
            uye__bbe = 0
            vnkoq__bwlru = v
            if vnkoq__bwlru < 0:
                uye__bbe = 1
                vnkoq__bwlru = -vnkoq__bwlru
            if vnkoq__bwlru < 1:
                lef__ajqiz = 1
            else:
                lef__ajqiz = 1 + int(np.floor(np.log10(vnkoq__bwlru)))
            length = uye__bbe + lef__ajqiz + 1 + 6
            s = numba.cpython.unicode._malloc_string(kind, 1, length, True)
            float_to_str(s, v)
            return s
        return impl


@overload(format, no_unliteral=True)
def overload_format(value, format_spec=''):
    if is_overload_constant_str(format_spec) and get_overload_const_str(
        format_spec) == '':

        def impl_fast(value, format_spec=''):
            return str(value)
        return impl_fast

    def impl(value, format_spec=''):
        with numba.objmode(res='string'):
            res = format(value, format_spec)
        return res
    return impl


@lower_cast(StdStringType, types.float64)
def cast_str_to_float64(context, builder, fromty, toty, val):
    ualk__ifkb = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    xjb__ijsn = cgutils.get_or_insert_function(builder.module, ualk__ifkb,
        name='str_to_float64')
    res = builder.call(xjb__ijsn, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    ualk__ifkb = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    xjb__ijsn = cgutils.get_or_insert_function(builder.module, ualk__ifkb,
        name='str_to_float32')
    res = builder.call(xjb__ijsn, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.float64)
def cast_unicode_str_to_float64(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float64(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.float32)
def cast_unicode_str_to_float32(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float32(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.int64)
@lower_cast(string_type, types.int32)
@lower_cast(string_type, types.int16)
@lower_cast(string_type, types.int8)
def cast_unicode_str_to_int64(context, builder, fromty, toty, val):
    ysz__zgff = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    ualk__ifkb = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    xjb__ijsn = cgutils.get_or_insert_function(builder.module, ualk__ifkb,
        name='str_to_int64')
    res = builder.call(xjb__ijsn, (ysz__zgff.data, ysz__zgff.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    ysz__zgff = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    ualk__ifkb = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    xjb__ijsn = cgutils.get_or_insert_function(builder.module, ualk__ifkb,
        name='str_to_uint64')
    res = builder.call(xjb__ijsn, (ysz__zgff.data, ysz__zgff.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        dqyvc__mvx = ', '.join('e{}'.format(dkpt__mdmja) for dkpt__mdmja in
            range(len(args)))
        if dqyvc__mvx:
            dqyvc__mvx += ', '
        fcpre__xguc = ', '.join("{} = ''".format(a) for a in kws.keys())
        cthyf__kccxb = (
            f'def format_stub(string, {dqyvc__mvx} {fcpre__xguc}):\n')
        cthyf__kccxb += '    pass\n'
        ybfk__nvx = {}
        exec(cthyf__kccxb, {}, ybfk__nvx)
        bcmk__kool = ybfk__nvx['format_stub']
        vdl__jmoqz = numba.core.utils.pysignature(bcmk__kool)
        kpjy__luhca = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, kpjy__luhca).replace(pysig=vdl__jmoqz)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    aij__twew = pat is not None and len(pat) > 1
    if aij__twew:
        zqoiv__mne = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    xyee__ksm = len(arr)
    shczp__gado = 0
    eejx__uyar = 0
    for dkpt__mdmja in numba.parfors.parfor.internal_prange(xyee__ksm):
        if bodo.libs.array_kernels.isna(arr, dkpt__mdmja):
            continue
        if aij__twew:
            viwia__yubu = zqoiv__mne.split(arr[dkpt__mdmja], maxsplit=n)
        elif pat == '':
            viwia__yubu = [''] + list(arr[dkpt__mdmja]) + ['']
        else:
            viwia__yubu = arr[dkpt__mdmja].split(pat, n)
        shczp__gado += len(viwia__yubu)
        for s in viwia__yubu:
            eejx__uyar += bodo.libs.str_arr_ext.get_utf8_size(s)
    dsi__tcz = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        xyee__ksm, (shczp__gado, eejx__uyar), bodo.libs.str_arr_ext.
        string_array_type)
    wxkin__ttti = bodo.libs.array_item_arr_ext.get_offsets(dsi__tcz)
    fgc__ffin = bodo.libs.array_item_arr_ext.get_null_bitmap(dsi__tcz)
    qrt__dtfsx = bodo.libs.array_item_arr_ext.get_data(dsi__tcz)
    saq__rjnrr = 0
    for wabeg__cdsem in numba.parfors.parfor.internal_prange(xyee__ksm):
        wxkin__ttti[wabeg__cdsem] = saq__rjnrr
        if bodo.libs.array_kernels.isna(arr, wabeg__cdsem):
            bodo.libs.int_arr_ext.set_bit_to_arr(fgc__ffin, wabeg__cdsem, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(fgc__ffin, wabeg__cdsem, 1)
        if aij__twew:
            viwia__yubu = zqoiv__mne.split(arr[wabeg__cdsem], maxsplit=n)
        elif pat == '':
            viwia__yubu = [''] + list(arr[wabeg__cdsem]) + ['']
        else:
            viwia__yubu = arr[wabeg__cdsem].split(pat, n)
        alk__gzfw = len(viwia__yubu)
        for dns__rlt in range(alk__gzfw):
            s = viwia__yubu[dns__rlt]
            qrt__dtfsx[saq__rjnrr] = s
            saq__rjnrr += 1
    wxkin__ttti[xyee__ksm] = saq__rjnrr
    return dsi__tcz


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                fdwoc__wvfvq = '-0x'
                x = x * -1
            else:
                fdwoc__wvfvq = '0x'
            x = np.uint64(x)
            if x == 0:
                nmtg__kdub = 1
            else:
                nmtg__kdub = fast_ceil_log2(x + 1)
                nmtg__kdub = (nmtg__kdub + 3) // 4
            length = len(fdwoc__wvfvq) + nmtg__kdub
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, fdwoc__wvfvq._data,
                len(fdwoc__wvfvq), 1)
            int_to_hex(output, nmtg__kdub, len(fdwoc__wvfvq), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    jiesj__kgdoe = 0 if x & x - 1 == 0 else 1
    xkpqa__vnysq = [np.uint64(18446744069414584320), np.uint64(4294901760),
        np.uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    kbnqk__lkk = 32
    for dkpt__mdmja in range(len(xkpqa__vnysq)):
        adw__voitl = 0 if x & xkpqa__vnysq[dkpt__mdmja] == 0 else kbnqk__lkk
        jiesj__kgdoe = jiesj__kgdoe + adw__voitl
        x = x >> adw__voitl
        kbnqk__lkk = kbnqk__lkk >> 1
    return jiesj__kgdoe


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        cihba__esw = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        ualk__ifkb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        mtkya__xjhp = cgutils.get_or_insert_function(builder.module,
            ualk__ifkb, name='int_to_hex')
        wln__hzwe = builder.inttoptr(builder.add(builder.ptrtoint(
            cihba__esw.data, lir.IntType(64)), header_len), lir.IntType(8).
            as_pointer())
        builder.call(mtkya__xjhp, (wln__hzwe, out_len, int_val))
    return types.void(output, out_len, header_len, int_val), codegen


def alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    pass


@overload(alloc_empty_bytes_or_string_data)
def overload_alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    typ = typ.instance_type if isinstance(typ, types.TypeRef) else typ
    if typ == bodo.bytes_type:
        return lambda typ, kind, length, is_ascii=0: np.empty(length, np.uint8)
    if typ == string_type:
        return (lambda typ, kind, length, is_ascii=0: numba.cpython.unicode
            ._empty_string(kind, length, is_ascii))
    raise BodoError(
        f'Internal Error: Expected Bytes or String type, found {typ}')


def get_unicode_or_numpy_data(val):
    pass


@overload(get_unicode_or_numpy_data)
def overload_get_unicode_or_numpy_data(val):
    if val == string_type:
        return lambda val: val._data
    if isinstance(val, types.Array):
        return lambda val: val.ctypes
    raise BodoError(
        f'Internal Error: Expected String or Numpy Array, found {val}')
