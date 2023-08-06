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
    kmbzn__vdc = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        vdez__lsoc, = args
        xwf__lvsda = cgutils.create_struct_proxy(string_type)(context,
            builder, value=vdez__lsoc)
        krasg__wme = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        atgu__ccvft = cgutils.create_struct_proxy(kmbzn__vdc)(context, builder)
        is_ascii = builder.icmp_unsigned('==', xwf__lvsda.is_ascii, lir.
            Constant(xwf__lvsda.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (hddju__ylido, tsz__lsvga):
            with hddju__ylido:
                context.nrt.incref(builder, string_type, vdez__lsoc)
                krasg__wme.data = xwf__lvsda.data
                krasg__wme.meminfo = xwf__lvsda.meminfo
                atgu__ccvft.f1 = xwf__lvsda.length
            with tsz__lsvga:
                tvgo__usdy = lir.FunctionType(lir.IntType(64), [lir.IntType
                    (8).as_pointer(), lir.IntType(8).as_pointer(), lir.
                    IntType(64), lir.IntType(32)])
                uiki__hnwe = cgutils.get_or_insert_function(builder.module,
                    tvgo__usdy, name='unicode_to_utf8')
                abse__grena = context.get_constant_null(types.voidptr)
                bmw__nenq = builder.call(uiki__hnwe, [abse__grena,
                    xwf__lvsda.data, xwf__lvsda.length, xwf__lvsda.kind])
                atgu__ccvft.f1 = bmw__nenq
                pgn__ivz = builder.add(bmw__nenq, lir.Constant(lir.IntType(
                    64), 1))
                krasg__wme.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=pgn__ivz, align=32)
                krasg__wme.data = context.nrt.meminfo_data(builder,
                    krasg__wme.meminfo)
                builder.call(uiki__hnwe, [krasg__wme.data, xwf__lvsda.data,
                    xwf__lvsda.length, xwf__lvsda.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    krasg__wme.data, [bmw__nenq]))
        atgu__ccvft.f0 = krasg__wme._getvalue()
        return atgu__ccvft._getvalue()
    return kmbzn__vdc(string_type), codegen


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
        tvgo__usdy = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        vmi__ebpxj = cgutils.get_or_insert_function(builder.module,
            tvgo__usdy, name='memcmp')
        return builder.call(vmi__ebpxj, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    kxjzv__wifn = n(10)

    def impl(n):
        if n == 0:
            return 1
        dhmf__qzjyr = 0
        if n < 0:
            n = -n
            dhmf__qzjyr += 1
        while n > 0:
            n = n // kxjzv__wifn
            dhmf__qzjyr += 1
        return dhmf__qzjyr
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
        [hut__imy] = args
        if isinstance(hut__imy, StdStringType):
            return signature(types.float64, hut__imy)
        if hut__imy == string_type:
            return signature(types.float64, hut__imy)


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
    xwf__lvsda = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    tvgo__usdy = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    ueoes__udbkb = cgutils.get_or_insert_function(builder.module,
        tvgo__usdy, name='init_string_const')
    return builder.call(ueoes__udbkb, [xwf__lvsda.data, xwf__lvsda.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        mdud__gfwft = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(mdud__gfwft._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return mdud__gfwft
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    xwf__lvsda = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return xwf__lvsda.data


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
        gwn__slb = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, gwn__slb)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        ytql__xan, = args
        dluxh__dkv = types.List(string_type)
        zifw__fphro = numba.cpython.listobj.ListInstance.allocate(context,
            builder, dluxh__dkv, ytql__xan)
        zifw__fphro.size = ytql__xan
        llua__mucn = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        llua__mucn.data = zifw__fphro.value
        return llua__mucn._getvalue()
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
            ebw__psmmj = 0
            pmuy__zhz = v
            if pmuy__zhz < 0:
                ebw__psmmj = 1
                pmuy__zhz = -pmuy__zhz
            if pmuy__zhz < 1:
                tqek__kspw = 1
            else:
                tqek__kspw = 1 + int(np.floor(np.log10(pmuy__zhz)))
            length = ebw__psmmj + tqek__kspw + 1 + 6
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
    tvgo__usdy = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    ueoes__udbkb = cgutils.get_or_insert_function(builder.module,
        tvgo__usdy, name='str_to_float64')
    res = builder.call(ueoes__udbkb, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    tvgo__usdy = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    ueoes__udbkb = cgutils.get_or_insert_function(builder.module,
        tvgo__usdy, name='str_to_float32')
    res = builder.call(ueoes__udbkb, (val,))
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
    xwf__lvsda = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    tvgo__usdy = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    ueoes__udbkb = cgutils.get_or_insert_function(builder.module,
        tvgo__usdy, name='str_to_int64')
    res = builder.call(ueoes__udbkb, (xwf__lvsda.data, xwf__lvsda.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    xwf__lvsda = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    tvgo__usdy = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    ueoes__udbkb = cgutils.get_or_insert_function(builder.module,
        tvgo__usdy, name='str_to_uint64')
    res = builder.call(ueoes__udbkb, (xwf__lvsda.data, xwf__lvsda.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        aom__dnpma = ', '.join('e{}'.format(pfs__ypa) for pfs__ypa in range
            (len(args)))
        if aom__dnpma:
            aom__dnpma += ', '
        ktias__uzrpf = ', '.join("{} = ''".format(a) for a in kws.keys())
        lbg__bby = f'def format_stub(string, {aom__dnpma} {ktias__uzrpf}):\n'
        lbg__bby += '    pass\n'
        jtfyd__ipaty = {}
        exec(lbg__bby, {}, jtfyd__ipaty)
        yfb__mwly = jtfyd__ipaty['format_stub']
        hrqyu__bdj = numba.core.utils.pysignature(yfb__mwly)
        utii__lwoe = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, utii__lwoe).replace(pysig=hrqyu__bdj)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    rbgw__uqh = pat is not None and len(pat) > 1
    if rbgw__uqh:
        ofiih__ifbr = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    zifw__fphro = len(arr)
    vfnp__zppei = 0
    phnvv__oxfao = 0
    for pfs__ypa in numba.parfors.parfor.internal_prange(zifw__fphro):
        if bodo.libs.array_kernels.isna(arr, pfs__ypa):
            continue
        if rbgw__uqh:
            ern__gob = ofiih__ifbr.split(arr[pfs__ypa], maxsplit=n)
        elif pat == '':
            ern__gob = [''] + list(arr[pfs__ypa]) + ['']
        else:
            ern__gob = arr[pfs__ypa].split(pat, n)
        vfnp__zppei += len(ern__gob)
        for s in ern__gob:
            phnvv__oxfao += bodo.libs.str_arr_ext.get_utf8_size(s)
    lbt__bteyi = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        zifw__fphro, (vfnp__zppei, phnvv__oxfao), bodo.libs.str_arr_ext.
        string_array_type)
    slnl__shmvx = bodo.libs.array_item_arr_ext.get_offsets(lbt__bteyi)
    qlnc__pewnw = bodo.libs.array_item_arr_ext.get_null_bitmap(lbt__bteyi)
    wltkm__qkc = bodo.libs.array_item_arr_ext.get_data(lbt__bteyi)
    ujws__yhv = 0
    for gaxdl__zqb in numba.parfors.parfor.internal_prange(zifw__fphro):
        slnl__shmvx[gaxdl__zqb] = ujws__yhv
        if bodo.libs.array_kernels.isna(arr, gaxdl__zqb):
            bodo.libs.int_arr_ext.set_bit_to_arr(qlnc__pewnw, gaxdl__zqb, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(qlnc__pewnw, gaxdl__zqb, 1)
        if rbgw__uqh:
            ern__gob = ofiih__ifbr.split(arr[gaxdl__zqb], maxsplit=n)
        elif pat == '':
            ern__gob = [''] + list(arr[gaxdl__zqb]) + ['']
        else:
            ern__gob = arr[gaxdl__zqb].split(pat, n)
        brrjx__qyjbu = len(ern__gob)
        for iojsz__str in range(brrjx__qyjbu):
            s = ern__gob[iojsz__str]
            wltkm__qkc[ujws__yhv] = s
            ujws__yhv += 1
    slnl__shmvx[zifw__fphro] = ujws__yhv
    return lbt__bteyi


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                uquw__dmft = '-0x'
                x = x * -1
            else:
                uquw__dmft = '0x'
            x = np.uint64(x)
            if x == 0:
                ufxnt__czu = 1
            else:
                ufxnt__czu = fast_ceil_log2(x + 1)
                ufxnt__czu = (ufxnt__czu + 3) // 4
            length = len(uquw__dmft) + ufxnt__czu
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, uquw__dmft._data,
                len(uquw__dmft), 1)
            int_to_hex(output, ufxnt__czu, len(uquw__dmft), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    bsu__rol = 0 if x & x - 1 == 0 else 1
    ibq__jafgc = [np.uint64(18446744069414584320), np.uint64(4294901760),
        np.uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    cxjvc__xvme = 32
    for pfs__ypa in range(len(ibq__jafgc)):
        ftnv__gbama = 0 if x & ibq__jafgc[pfs__ypa] == 0 else cxjvc__xvme
        bsu__rol = bsu__rol + ftnv__gbama
        x = x >> ftnv__gbama
        cxjvc__xvme = cxjvc__xvme >> 1
    return bsu__rol


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        eryg__saoit = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        tvgo__usdy = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        gzs__gjmf = cgutils.get_or_insert_function(builder.module,
            tvgo__usdy, name='int_to_hex')
        aju__ydsv = builder.inttoptr(builder.add(builder.ptrtoint(
            eryg__saoit.data, lir.IntType(64)), header_len), lir.IntType(8)
            .as_pointer())
        builder.call(gzs__gjmf, (aju__ydsv, out_len, int_val))
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
