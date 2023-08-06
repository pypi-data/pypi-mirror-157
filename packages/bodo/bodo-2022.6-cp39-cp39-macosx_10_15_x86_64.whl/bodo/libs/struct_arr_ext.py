"""Array implementation for structs of values.
Corresponds to Spark's StructType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Struct arrays: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in contiguous data arrays; one array per field. For example:
A:             ["AA", "B", "C"]
B:             [1, 2, 4]
"""
import operator
import llvmlite.binding as ll
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
from numba.typed.typedobjectutils import _cast
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.typing import BodoError, dtype_to_array_type, get_overload_const_int, get_overload_const_str, is_list_like_index_type, is_overload_constant_int, is_overload_constant_str, is_overload_none
ll.add_symbol('struct_array_from_sequence', array_ext.
    struct_array_from_sequence)
ll.add_symbol('np_array_from_struct_array', array_ext.
    np_array_from_struct_array)


class StructArrayType(types.ArrayCompatible):

    def __init__(self, data, names=None):
        assert isinstance(data, tuple) and len(data) > 0 and all(bodo.utils
            .utils.is_array_typ(hqugu__dki, False) for hqugu__dki in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(hqugu__dki,
                str) for hqugu__dki in names) and len(names) == len(data)
        else:
            names = tuple('f{}'.format(i) for i in range(len(data)))
        self.data = data
        self.names = names
        super(StructArrayType, self).__init__(name=
            'StructArrayType({}, {})'.format(data, names))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return StructType(tuple(afa__tai.dtype for afa__tai in self.data),
            self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(hqugu__dki) for hqugu__dki in d.keys())
        data = tuple(dtype_to_array_type(afa__tai) for afa__tai in d.values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(hqugu__dki, False) for hqugu__dki in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wtu__jcdvf = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, wtu__jcdvf)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        wtu__jcdvf = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, wtu__jcdvf)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    qnb__gxvqm = builder.module
    opw__kvs = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    mmy__vxtt = cgutils.get_or_insert_function(qnb__gxvqm, opw__kvs, name=
        '.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not mmy__vxtt.is_declaration:
        return mmy__vxtt
    mmy__vxtt.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(mmy__vxtt.append_basic_block())
    ctz__hgwc = mmy__vxtt.args[0]
    fjeza__punc = context.get_value_type(payload_type).as_pointer()
    tknye__ogg = builder.bitcast(ctz__hgwc, fjeza__punc)
    kwk__ryhqr = context.make_helper(builder, payload_type, ref=tknye__ogg)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), kwk__ryhqr.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        kwk__ryhqr.null_bitmap)
    builder.ret_void()
    return mmy__vxtt


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    wlwas__qbm = context.get_value_type(payload_type)
    fge__lkey = context.get_abi_sizeof(wlwas__qbm)
    xxy__btfx = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    hrh__rybaz = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, fge__lkey), xxy__btfx)
    bejx__qvatk = context.nrt.meminfo_data(builder, hrh__rybaz)
    ptik__yyoxm = builder.bitcast(bejx__qvatk, wlwas__qbm.as_pointer())
    kwk__ryhqr = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    fjunn__rsiqm = 0
    for arr_typ in struct_arr_type.data:
        qjrjl__oixkm = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype
            )
        hwc__unyq = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(fjunn__rsiqm, 
            fjunn__rsiqm + qjrjl__oixkm)])
        arr = gen_allocate_array(context, builder, arr_typ, hwc__unyq, c)
        arrs.append(arr)
        fjunn__rsiqm += qjrjl__oixkm
    kwk__ryhqr.data = cgutils.pack_array(builder, arrs
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, arrs)
    oav__idhx = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    rwa__zlkll = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [oav__idhx])
    null_bitmap_ptr = rwa__zlkll.data
    kwk__ryhqr.null_bitmap = rwa__zlkll._getvalue()
    builder.store(kwk__ryhqr._getvalue(), ptik__yyoxm)
    return hrh__rybaz, kwk__ryhqr.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    coxh__bry = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        ednl__zfi = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            ednl__zfi)
        coxh__bry.append(arr.data)
    lokp__idaxj = cgutils.pack_array(c.builder, coxh__bry
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, coxh__bry)
    ohuim__nhsu = cgutils.alloca_once_value(c.builder, lokp__idaxj)
    sczc__xqhaa = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(hqugu__dki.dtype)) for hqugu__dki in data_typ]
    otl__ebc = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c.
        builder, sczc__xqhaa))
    jji__rjol = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, hqugu__dki) for hqugu__dki in
        names])
    puywz__ljarv = cgutils.alloca_once_value(c.builder, jji__rjol)
    return ohuim__nhsu, otl__ebc, puywz__ljarv


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    wxse__bpfj = all(isinstance(afa__tai, types.Array) and afa__tai.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        afa__tai in typ.data)
    if wxse__bpfj:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        ept__sjcvn = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            ept__sjcvn, i) for i in range(1, ept__sjcvn.type.count)], lir.
            IntType(64))
    hrh__rybaz, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if wxse__bpfj:
        ohuim__nhsu, otl__ebc, puywz__ljarv = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        opw__kvs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        mmy__vxtt = cgutils.get_or_insert_function(c.builder.module,
            opw__kvs, name='struct_array_from_sequence')
        c.builder.call(mmy__vxtt, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(ohuim__nhsu, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(otl__ebc, lir
            .IntType(8).as_pointer()), c.builder.bitcast(puywz__ljarv, lir.
            IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    iqh__hrt = c.context.make_helper(c.builder, typ)
    iqh__hrt.meminfo = hrh__rybaz
    mdnyd__zhyrw = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(iqh__hrt._getvalue(), is_error=mdnyd__zhyrw)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    icf__ukxq = context.insert_const_string(builder.module, 'pandas')
    ccfz__lhcnr = c.pyapi.import_module_noblock(icf__ukxq)
    zbn__xsxbp = c.pyapi.object_getattr_string(ccfz__lhcnr, 'NA')
    with cgutils.for_range(builder, n_structs) as zjyp__baqr:
        rcc__hclv = zjyp__baqr.index
        cjyp__nzztt = seq_getitem(builder, context, val, rcc__hclv)
        set_bitmap_bit(builder, null_bitmap_ptr, rcc__hclv, 0)
        for cjk__bopc in range(len(typ.data)):
            arr_typ = typ.data[cjk__bopc]
            data_arr = builder.extract_value(data_tup, cjk__bopc)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            xkdsy__vdu, wdmge__xkvwg = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, rcc__hclv])
        cdal__dptd = is_na_value(builder, context, cjyp__nzztt, zbn__xsxbp)
        dum__hjsuj = builder.icmp_unsigned('!=', cdal__dptd, lir.Constant(
            cdal__dptd.type, 1))
        with builder.if_then(dum__hjsuj):
            set_bitmap_bit(builder, null_bitmap_ptr, rcc__hclv, 1)
            for cjk__bopc in range(len(typ.data)):
                arr_typ = typ.data[cjk__bopc]
                if is_tuple_array:
                    ebwfp__hrh = c.pyapi.tuple_getitem(cjyp__nzztt, cjk__bopc)
                else:
                    ebwfp__hrh = c.pyapi.dict_getitem_string(cjyp__nzztt,
                        typ.names[cjk__bopc])
                cdal__dptd = is_na_value(builder, context, ebwfp__hrh,
                    zbn__xsxbp)
                dum__hjsuj = builder.icmp_unsigned('!=', cdal__dptd, lir.
                    Constant(cdal__dptd.type, 1))
                with builder.if_then(dum__hjsuj):
                    ebwfp__hrh = to_arr_obj_if_list_obj(c, context, builder,
                        ebwfp__hrh, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        ebwfp__hrh).value
                    data_arr = builder.extract_value(data_tup, cjk__bopc)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    xkdsy__vdu, wdmge__xkvwg = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, rcc__hclv, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(cjyp__nzztt)
    c.pyapi.decref(ccfz__lhcnr)
    c.pyapi.decref(zbn__xsxbp)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    iqh__hrt = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    bejx__qvatk = context.nrt.meminfo_data(builder, iqh__hrt.meminfo)
    ptik__yyoxm = builder.bitcast(bejx__qvatk, context.get_value_type(
        payload_type).as_pointer())
    kwk__ryhqr = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(ptik__yyoxm))
    return kwk__ryhqr


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    kwk__ryhqr = _get_struct_arr_payload(c.context, c.builder, typ, val)
    xkdsy__vdu, length = c.pyapi.call_jit_code(lambda A: len(A), types.
        int64(typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), kwk__ryhqr.null_bitmap).data
    wxse__bpfj = all(isinstance(afa__tai, types.Array) and afa__tai.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        afa__tai in typ.data)
    if wxse__bpfj:
        ohuim__nhsu, otl__ebc, puywz__ljarv = _get_C_API_ptrs(c, kwk__ryhqr
            .data, typ.data, typ.names)
        opw__kvs = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        jhm__kef = cgutils.get_or_insert_function(c.builder.module,
            opw__kvs, name='np_array_from_struct_array')
        arr = c.builder.call(jhm__kef, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(ohuim__nhsu, lir
            .IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            otl__ebc, lir.IntType(8).as_pointer()), c.builder.bitcast(
            puywz__ljarv, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, kwk__ryhqr.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    icf__ukxq = context.insert_const_string(builder.module, 'numpy')
    ljeke__odhh = c.pyapi.import_module_noblock(icf__ukxq)
    euu__fjgb = c.pyapi.object_getattr_string(ljeke__odhh, 'object_')
    qrnz__cfxu = c.pyapi.long_from_longlong(length)
    ajwt__cxrt = c.pyapi.call_method(ljeke__odhh, 'ndarray', (qrnz__cfxu,
        euu__fjgb))
    isg__gotb = c.pyapi.object_getattr_string(ljeke__odhh, 'nan')
    with cgutils.for_range(builder, length) as zjyp__baqr:
        rcc__hclv = zjyp__baqr.index
        pyarray_setitem(builder, context, ajwt__cxrt, rcc__hclv, isg__gotb)
        lahz__mnl = get_bitmap_bit(builder, null_bitmap_ptr, rcc__hclv)
        todu__dcy = builder.icmp_unsigned('!=', lahz__mnl, lir.Constant(lir
            .IntType(8), 0))
        with builder.if_then(todu__dcy):
            if is_tuple_array:
                cjyp__nzztt = c.pyapi.tuple_new(len(typ.data))
            else:
                cjyp__nzztt = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(isg__gotb)
                    c.pyapi.tuple_setitem(cjyp__nzztt, i, isg__gotb)
                else:
                    c.pyapi.dict_setitem_string(cjyp__nzztt, typ.names[i],
                        isg__gotb)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                xkdsy__vdu, swem__heuoj = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, rcc__hclv])
                with builder.if_then(swem__heuoj):
                    xkdsy__vdu, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, rcc__hclv])
                    nmwto__ono = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(cjyp__nzztt, i, nmwto__ono)
                    else:
                        c.pyapi.dict_setitem_string(cjyp__nzztt, typ.names[
                            i], nmwto__ono)
                        c.pyapi.decref(nmwto__ono)
            pyarray_setitem(builder, context, ajwt__cxrt, rcc__hclv,
                cjyp__nzztt)
            c.pyapi.decref(cjyp__nzztt)
    c.pyapi.decref(ljeke__odhh)
    c.pyapi.decref(euu__fjgb)
    c.pyapi.decref(qrnz__cfxu)
    c.pyapi.decref(isg__gotb)
    return ajwt__cxrt


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    aiw__pqy = bodo.utils.transform.get_type_alloc_counts(struct_arr_type) - 1
    if aiw__pqy == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for cltg__tjjow in range(aiw__pqy)])
    elif nested_counts_type.count < aiw__pqy:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for cltg__tjjow in range(
            aiw__pqy - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(afa__tai) for afa__tai in
            names_typ.types)
    ywhv__dyhgm = tuple(afa__tai.instance_type for afa__tai in dtypes_typ.types
        )
    struct_arr_type = StructArrayType(ywhv__dyhgm, names)

    def codegen(context, builder, sig, args):
        xvd__yfkxr, nested_counts, cltg__tjjow, cltg__tjjow = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        hrh__rybaz, cltg__tjjow, cltg__tjjow = construct_struct_array(context,
            builder, struct_arr_type, xvd__yfkxr, nested_counts)
        iqh__hrt = context.make_helper(builder, struct_arr_type)
        iqh__hrt.meminfo = hrh__rybaz
        return iqh__hrt._getvalue()
    return struct_arr_type(num_structs_typ, nested_counts_typ, dtypes_typ,
        names_typ), codegen


def pre_alloc_struct_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_struct_arr_ext_pre_alloc_struct_array
    ) = pre_alloc_struct_array_equiv


class StructType(types.Type):

    def __init__(self, data, names):
        assert isinstance(data, tuple) and len(data) > 0
        assert isinstance(names, tuple) and all(isinstance(hqugu__dki, str) for
            hqugu__dki in names) and len(names) == len(data)
        self.data = data
        self.names = names
        super(StructType, self).__init__(name='StructType({}, {})'.format(
            data, names))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple)
        self.data = data
        super(StructPayloadType, self).__init__(name=
            'StructPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructPayloadType)
class StructPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wtu__jcdvf = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, wtu__jcdvf)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        wtu__jcdvf = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, wtu__jcdvf)


def define_struct_dtor(context, builder, struct_type, payload_type):
    qnb__gxvqm = builder.module
    opw__kvs = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    mmy__vxtt = cgutils.get_or_insert_function(qnb__gxvqm, opw__kvs, name=
        '.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not mmy__vxtt.is_declaration:
        return mmy__vxtt
    mmy__vxtt.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(mmy__vxtt.append_basic_block())
    ctz__hgwc = mmy__vxtt.args[0]
    fjeza__punc = context.get_value_type(payload_type).as_pointer()
    tknye__ogg = builder.bitcast(ctz__hgwc, fjeza__punc)
    kwk__ryhqr = context.make_helper(builder, payload_type, ref=tknye__ogg)
    for i in range(len(struct_type.data)):
        vfg__brhj = builder.extract_value(kwk__ryhqr.null_bitmap, i)
        todu__dcy = builder.icmp_unsigned('==', vfg__brhj, lir.Constant(
            vfg__brhj.type, 1))
        with builder.if_then(todu__dcy):
            val = builder.extract_value(kwk__ryhqr.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return mmy__vxtt


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    bejx__qvatk = context.nrt.meminfo_data(builder, struct.meminfo)
    ptik__yyoxm = builder.bitcast(bejx__qvatk, context.get_value_type(
        payload_type).as_pointer())
    kwk__ryhqr = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(ptik__yyoxm))
    return kwk__ryhqr, ptik__yyoxm


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    icf__ukxq = context.insert_const_string(builder.module, 'pandas')
    ccfz__lhcnr = c.pyapi.import_module_noblock(icf__ukxq)
    zbn__xsxbp = c.pyapi.object_getattr_string(ccfz__lhcnr, 'NA')
    pphcq__xor = []
    nulls = []
    for i, afa__tai in enumerate(typ.data):
        nmwto__ono = c.pyapi.dict_getitem_string(val, typ.names[i])
        gog__jyd = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        yyhm__jeo = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(afa__tai)))
        cdal__dptd = is_na_value(builder, context, nmwto__ono, zbn__xsxbp)
        todu__dcy = builder.icmp_unsigned('!=', cdal__dptd, lir.Constant(
            cdal__dptd.type, 1))
        with builder.if_then(todu__dcy):
            builder.store(context.get_constant(types.uint8, 1), gog__jyd)
            field_val = c.pyapi.to_native_value(afa__tai, nmwto__ono).value
            builder.store(field_val, yyhm__jeo)
        pphcq__xor.append(builder.load(yyhm__jeo))
        nulls.append(builder.load(gog__jyd))
    c.pyapi.decref(ccfz__lhcnr)
    c.pyapi.decref(zbn__xsxbp)
    hrh__rybaz = construct_struct(context, builder, typ, pphcq__xor, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = hrh__rybaz
    mdnyd__zhyrw = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=mdnyd__zhyrw)


@box(StructType)
def box_struct(typ, val, c):
    hdk__lrmw = c.pyapi.dict_new(len(typ.data))
    kwk__ryhqr, cltg__tjjow = _get_struct_payload(c.context, c.builder, typ,
        val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(hdk__lrmw, typ.names[i], c.pyapi.
            borrow_none())
        vfg__brhj = c.builder.extract_value(kwk__ryhqr.null_bitmap, i)
        todu__dcy = c.builder.icmp_unsigned('==', vfg__brhj, lir.Constant(
            vfg__brhj.type, 1))
        with c.builder.if_then(todu__dcy):
            ubr__dwnr = c.builder.extract_value(kwk__ryhqr.data, i)
            c.context.nrt.incref(c.builder, val_typ, ubr__dwnr)
            ebwfp__hrh = c.pyapi.from_native_value(val_typ, ubr__dwnr, c.
                env_manager)
            c.pyapi.dict_setitem_string(hdk__lrmw, typ.names[i], ebwfp__hrh)
            c.pyapi.decref(ebwfp__hrh)
    c.context.nrt.decref(c.builder, typ, val)
    return hdk__lrmw


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(afa__tai) for afa__tai in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, abd__mjaw = args
        payload_type = StructPayloadType(struct_type.data)
        wlwas__qbm = context.get_value_type(payload_type)
        fge__lkey = context.get_abi_sizeof(wlwas__qbm)
        xxy__btfx = define_struct_dtor(context, builder, struct_type,
            payload_type)
        hrh__rybaz = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, fge__lkey), xxy__btfx)
        bejx__qvatk = context.nrt.meminfo_data(builder, hrh__rybaz)
        ptik__yyoxm = builder.bitcast(bejx__qvatk, wlwas__qbm.as_pointer())
        kwk__ryhqr = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        kwk__ryhqr.data = data
        kwk__ryhqr.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for cltg__tjjow in range(len(
            data_typ.types))])
        builder.store(kwk__ryhqr._getvalue(), ptik__yyoxm)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = hrh__rybaz
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        kwk__ryhqr, cltg__tjjow = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            kwk__ryhqr.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        kwk__ryhqr, cltg__tjjow = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            kwk__ryhqr.null_bitmap)
    nnns__qslpg = types.UniTuple(types.int8, len(struct_typ.data))
    return nnns__qslpg(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, cltg__tjjow, val = args
        kwk__ryhqr, ptik__yyoxm = _get_struct_payload(context, builder,
            struct_typ, struct)
        tnvh__fzgly = kwk__ryhqr.data
        boxyk__conj = builder.insert_value(tnvh__fzgly, val, field_ind)
        cwf__jgpw = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, cwf__jgpw, tnvh__fzgly)
        context.nrt.incref(builder, cwf__jgpw, boxyk__conj)
        kwk__ryhqr.data = boxyk__conj
        builder.store(kwk__ryhqr._getvalue(), ptik__yyoxm)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    tgdh__peex = get_overload_const_str(ind)
    if tgdh__peex not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            tgdh__peex, struct))
    return struct.names.index(tgdh__peex)


def is_field_value_null(s, field_name):
    pass


@overload(is_field_value_null, no_unliteral=True)
def overload_is_field_value_null(s, field_name):
    field_ind = _get_struct_field_ind(s, field_name, 'element access (getitem)'
        )
    return lambda s, field_name: get_struct_null_bitmap(s)[field_ind] == 0


@overload(operator.getitem, no_unliteral=True)
def struct_getitem(struct, ind):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'element access (getitem)')
    return lambda struct, ind: get_struct_data(struct)[field_ind]


@overload(operator.setitem, no_unliteral=True)
def struct_setitem(struct, ind, val):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'item assignment (setitem)')
    field_typ = struct.data[field_ind]
    return lambda struct, ind, val: set_struct_data(struct, field_ind,
        _cast(val, field_typ))


@overload(len, no_unliteral=True)
def overload_struct_arr_len(struct):
    if isinstance(struct, StructType):
        num_fields = len(struct.data)
        return lambda struct: num_fields


def construct_struct(context, builder, struct_type, values, nulls):
    payload_type = StructPayloadType(struct_type.data)
    wlwas__qbm = context.get_value_type(payload_type)
    fge__lkey = context.get_abi_sizeof(wlwas__qbm)
    xxy__btfx = define_struct_dtor(context, builder, struct_type, payload_type)
    hrh__rybaz = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, fge__lkey), xxy__btfx)
    bejx__qvatk = context.nrt.meminfo_data(builder, hrh__rybaz)
    ptik__yyoxm = builder.bitcast(bejx__qvatk, wlwas__qbm.as_pointer())
    kwk__ryhqr = cgutils.create_struct_proxy(payload_type)(context, builder)
    kwk__ryhqr.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    kwk__ryhqr.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(kwk__ryhqr._getvalue(), ptik__yyoxm)
    return hrh__rybaz


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    lmcm__srjgm = tuple(d.dtype for d in struct_arr_typ.data)
    mme__nfpt = StructType(lmcm__srjgm, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        ofx__yxvo, ind = args
        kwk__ryhqr = _get_struct_arr_payload(context, builder,
            struct_arr_typ, ofx__yxvo)
        pphcq__xor = []
        chk__xgazs = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            ednl__zfi = builder.extract_value(kwk__ryhqr.data, i)
            orf__edxx = context.compile_internal(builder, lambda arr, ind: 
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [ednl__zfi,
                ind])
            chk__xgazs.append(orf__edxx)
            gpr__vhwq = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            todu__dcy = builder.icmp_unsigned('==', orf__edxx, lir.Constant
                (orf__edxx.type, 1))
            with builder.if_then(todu__dcy):
                knos__rxcts = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    ednl__zfi, ind])
                builder.store(knos__rxcts, gpr__vhwq)
            pphcq__xor.append(builder.load(gpr__vhwq))
        if isinstance(mme__nfpt, types.DictType):
            hti__rlx = [context.insert_const_string(builder.module,
                bot__kyq) for bot__kyq in struct_arr_typ.names]
            ivfn__rgny = cgutils.pack_array(builder, pphcq__xor)
            khvtt__bff = cgutils.pack_array(builder, hti__rlx)

            def impl(names, vals):
                d = {}
                for i, bot__kyq in enumerate(names):
                    d[bot__kyq] = vals[i]
                return d
            ecr__zeap = context.compile_internal(builder, impl, mme__nfpt(
                types.Tuple(tuple(types.StringLiteral(bot__kyq) for
                bot__kyq in struct_arr_typ.names)), types.Tuple(lmcm__srjgm
                )), [khvtt__bff, ivfn__rgny])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                lmcm__srjgm), ivfn__rgny)
            return ecr__zeap
        hrh__rybaz = construct_struct(context, builder, mme__nfpt,
            pphcq__xor, chk__xgazs)
        struct = context.make_helper(builder, mme__nfpt)
        struct.meminfo = hrh__rybaz
        return struct._getvalue()
    return mme__nfpt(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        kwk__ryhqr = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            kwk__ryhqr.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        kwk__ryhqr = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            kwk__ryhqr.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(afa__tai) for afa__tai in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, rwa__zlkll, abd__mjaw = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        wlwas__qbm = context.get_value_type(payload_type)
        fge__lkey = context.get_abi_sizeof(wlwas__qbm)
        xxy__btfx = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        hrh__rybaz = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, fge__lkey), xxy__btfx)
        bejx__qvatk = context.nrt.meminfo_data(builder, hrh__rybaz)
        ptik__yyoxm = builder.bitcast(bejx__qvatk, wlwas__qbm.as_pointer())
        kwk__ryhqr = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        kwk__ryhqr.data = data
        kwk__ryhqr.null_bitmap = rwa__zlkll
        builder.store(kwk__ryhqr._getvalue(), ptik__yyoxm)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, rwa__zlkll)
        iqh__hrt = context.make_helper(builder, struct_arr_type)
        iqh__hrt.meminfo = hrh__rybaz
        return iqh__hrt._getvalue()
    return struct_arr_type(data_typ, null_bitmap_typ, names_typ), codegen


@overload(operator.getitem, no_unliteral=True)
def struct_arr_getitem(arr, ind):
    if not isinstance(arr, StructArrayType):
        return
    if isinstance(ind, types.Integer):

        def struct_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            return struct_array_get_struct(arr, ind)
        return struct_arr_getitem_impl
    qph__kgnl = len(arr.data)
    jhxio__oexot = 'def impl(arr, ind):\n'
    jhxio__oexot += '  data = get_data(arr)\n'
    jhxio__oexot += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        jhxio__oexot += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        jhxio__oexot += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        jhxio__oexot += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    jhxio__oexot += (
        '  return init_struct_arr(({},), out_null_bitmap, ({},))\n'.format(
        ', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for i in
        range(qph__kgnl)), ', '.join("'{}'".format(bot__kyq) for bot__kyq in
        arr.names)))
    kbqg__ovmd = {}
    exec(jhxio__oexot, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, kbqg__ovmd)
    impl = kbqg__ovmd['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        qph__kgnl = len(arr.data)
        jhxio__oexot = 'def impl(arr, ind, val):\n'
        jhxio__oexot += '  data = get_data(arr)\n'
        jhxio__oexot += '  null_bitmap = get_null_bitmap(arr)\n'
        jhxio__oexot += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(qph__kgnl):
            if isinstance(val, StructType):
                jhxio__oexot += ("  if is_field_value_null(val, '{}'):\n".
                    format(arr.names[i]))
                jhxio__oexot += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                jhxio__oexot += '  else:\n'
                jhxio__oexot += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                jhxio__oexot += "  data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
        kbqg__ovmd = {}
        exec(jhxio__oexot, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, kbqg__ovmd)
        impl = kbqg__ovmd['impl']
        return impl
    if isinstance(ind, types.SliceType):
        qph__kgnl = len(arr.data)
        jhxio__oexot = 'def impl(arr, ind, val):\n'
        jhxio__oexot += '  data = get_data(arr)\n'
        jhxio__oexot += '  null_bitmap = get_null_bitmap(arr)\n'
        jhxio__oexot += '  val_data = get_data(val)\n'
        jhxio__oexot += '  val_null_bitmap = get_null_bitmap(val)\n'
        jhxio__oexot += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(qph__kgnl):
            jhxio__oexot += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        kbqg__ovmd = {}
        exec(jhxio__oexot, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, kbqg__ovmd)
        impl = kbqg__ovmd['impl']
        return impl
    raise BodoError(
        'only setitem with scalar/slice index is currently supported for struct arrays'
        )


@overload(len, no_unliteral=True)
def overload_struct_arr_len(A):
    if isinstance(A, StructArrayType):
        return lambda A: len(get_data(A)[0])


@overload_attribute(StructArrayType, 'shape')
def overload_struct_arr_shape(A):
    return lambda A: (len(get_data(A)[0]),)


@overload_attribute(StructArrayType, 'dtype')
def overload_struct_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(StructArrayType, 'ndim')
def overload_struct_arr_ndim(A):
    return lambda A: 1


@overload_attribute(StructArrayType, 'nbytes')
def overload_struct_arr_nbytes(A):
    jhxio__oexot = 'def impl(A):\n'
    jhxio__oexot += '  total_nbytes = 0\n'
    jhxio__oexot += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        jhxio__oexot += f'  total_nbytes += data[{i}].nbytes\n'
    jhxio__oexot += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    jhxio__oexot += '  return total_nbytes\n'
    kbqg__ovmd = {}
    exec(jhxio__oexot, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, kbqg__ovmd)
    impl = kbqg__ovmd['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        rwa__zlkll = get_null_bitmap(A)
        tqg__lhlsl = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        dxbdj__ldvi = rwa__zlkll.copy()
        return init_struct_arr(tqg__lhlsl, dxbdj__ldvi, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(hqugu__dki.copy() for hqugu__dki in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    dzdvn__vpbzi = arrs.count
    jhxio__oexot = 'def f(arrs):\n'
    jhxio__oexot += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(dzdvn__vpbzi)))
    kbqg__ovmd = {}
    exec(jhxio__oexot, {}, kbqg__ovmd)
    impl = kbqg__ovmd['f']
    return impl
