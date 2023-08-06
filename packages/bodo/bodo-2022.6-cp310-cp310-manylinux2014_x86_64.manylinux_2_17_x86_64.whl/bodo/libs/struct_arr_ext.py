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
            .utils.is_array_typ(aadg__ypr, False) for aadg__ypr in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(aadg__ypr,
                str) for aadg__ypr in names) and len(names) == len(data)
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
        return StructType(tuple(jpyf__cap.dtype for jpyf__cap in self.data),
            self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(aadg__ypr) for aadg__ypr in d.keys())
        data = tuple(dtype_to_array_type(jpyf__cap) for jpyf__cap in d.values()
            )
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(aadg__ypr, False) for aadg__ypr in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        gxi__xhdlv = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, gxi__xhdlv)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        gxi__xhdlv = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, gxi__xhdlv)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    efhmc__qre = builder.module
    izg__dgqgi = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    ypxw__kju = cgutils.get_or_insert_function(efhmc__qre, izg__dgqgi, name
        ='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not ypxw__kju.is_declaration:
        return ypxw__kju
    ypxw__kju.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(ypxw__kju.append_basic_block())
    bvrp__sqg = ypxw__kju.args[0]
    yoqaw__tvry = context.get_value_type(payload_type).as_pointer()
    ypro__zix = builder.bitcast(bvrp__sqg, yoqaw__tvry)
    yfbg__fdt = context.make_helper(builder, payload_type, ref=ypro__zix)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), yfbg__fdt.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), yfbg__fdt
        .null_bitmap)
    builder.ret_void()
    return ypxw__kju


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    xtms__dzas = context.get_value_type(payload_type)
    qnc__ers = context.get_abi_sizeof(xtms__dzas)
    aeej__odtf = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    cwym__ubtjt = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, qnc__ers), aeej__odtf)
    qndzs__mvxrj = context.nrt.meminfo_data(builder, cwym__ubtjt)
    fwyrt__nitax = builder.bitcast(qndzs__mvxrj, xtms__dzas.as_pointer())
    yfbg__fdt = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    edm__pqd = 0
    for arr_typ in struct_arr_type.data:
        yakg__ysmb = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        pfgd__olp = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(edm__pqd, edm__pqd +
            yakg__ysmb)])
        arr = gen_allocate_array(context, builder, arr_typ, pfgd__olp, c)
        arrs.append(arr)
        edm__pqd += yakg__ysmb
    yfbg__fdt.data = cgutils.pack_array(builder, arrs) if types.is_homogeneous(
        *struct_arr_type.data) else cgutils.pack_struct(builder, arrs)
    fey__sqtk = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    fwqx__ixx = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [fey__sqtk])
    null_bitmap_ptr = fwqx__ixx.data
    yfbg__fdt.null_bitmap = fwqx__ixx._getvalue()
    builder.store(yfbg__fdt._getvalue(), fwyrt__nitax)
    return cwym__ubtjt, yfbg__fdt.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    iszny__ycemc = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        ywt__vtac = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            ywt__vtac)
        iszny__ycemc.append(arr.data)
    xom__pasjj = cgutils.pack_array(c.builder, iszny__ycemc
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, iszny__ycemc)
    qesof__kax = cgutils.alloca_once_value(c.builder, xom__pasjj)
    dct__ouoe = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(aadg__ypr.dtype)) for aadg__ypr in data_typ]
    qtsey__nbqy = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c
        .builder, dct__ouoe))
    jixil__nmvp = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, aadg__ypr) for aadg__ypr in
        names])
    slmvl__vxex = cgutils.alloca_once_value(c.builder, jixil__nmvp)
    return qesof__kax, qtsey__nbqy, slmvl__vxex


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    nvtxw__mrmct = all(isinstance(jpyf__cap, types.Array) and jpyf__cap.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for jpyf__cap in typ.data)
    if nvtxw__mrmct:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        qjtd__vvb = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            qjtd__vvb, i) for i in range(1, qjtd__vvb.type.count)], lir.
            IntType(64))
    cwym__ubtjt, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if nvtxw__mrmct:
        qesof__kax, qtsey__nbqy, slmvl__vxex = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        izg__dgqgi = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        ypxw__kju = cgutils.get_or_insert_function(c.builder.module,
            izg__dgqgi, name='struct_array_from_sequence')
        c.builder.call(ypxw__kju, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(qesof__kax, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(qtsey__nbqy,
            lir.IntType(8).as_pointer()), c.builder.bitcast(slmvl__vxex,
            lir.IntType(8).as_pointer()), c.context.get_constant(types.
            bool_, is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    lidjb__jued = c.context.make_helper(c.builder, typ)
    lidjb__jued.meminfo = cwym__ubtjt
    pzhr__hdqzm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(lidjb__jued._getvalue(), is_error=pzhr__hdqzm)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    awd__dleii = context.insert_const_string(builder.module, 'pandas')
    caj__gckn = c.pyapi.import_module_noblock(awd__dleii)
    uufb__qkurg = c.pyapi.object_getattr_string(caj__gckn, 'NA')
    with cgutils.for_range(builder, n_structs) as ymfz__sgtpo:
        ahuy__tprn = ymfz__sgtpo.index
        bmy__ipu = seq_getitem(builder, context, val, ahuy__tprn)
        set_bitmap_bit(builder, null_bitmap_ptr, ahuy__tprn, 0)
        for xap__dzvh in range(len(typ.data)):
            arr_typ = typ.data[xap__dzvh]
            data_arr = builder.extract_value(data_tup, xap__dzvh)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            npf__bqumm, dlvjf__akg = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, ahuy__tprn])
        lzy__dnkkb = is_na_value(builder, context, bmy__ipu, uufb__qkurg)
        uinw__lve = builder.icmp_unsigned('!=', lzy__dnkkb, lir.Constant(
            lzy__dnkkb.type, 1))
        with builder.if_then(uinw__lve):
            set_bitmap_bit(builder, null_bitmap_ptr, ahuy__tprn, 1)
            for xap__dzvh in range(len(typ.data)):
                arr_typ = typ.data[xap__dzvh]
                if is_tuple_array:
                    dyeo__picd = c.pyapi.tuple_getitem(bmy__ipu, xap__dzvh)
                else:
                    dyeo__picd = c.pyapi.dict_getitem_string(bmy__ipu, typ.
                        names[xap__dzvh])
                lzy__dnkkb = is_na_value(builder, context, dyeo__picd,
                    uufb__qkurg)
                uinw__lve = builder.icmp_unsigned('!=', lzy__dnkkb, lir.
                    Constant(lzy__dnkkb.type, 1))
                with builder.if_then(uinw__lve):
                    dyeo__picd = to_arr_obj_if_list_obj(c, context, builder,
                        dyeo__picd, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        dyeo__picd).value
                    data_arr = builder.extract_value(data_tup, xap__dzvh)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    npf__bqumm, dlvjf__akg = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, ahuy__tprn, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(bmy__ipu)
    c.pyapi.decref(caj__gckn)
    c.pyapi.decref(uufb__qkurg)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    lidjb__jued = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    qndzs__mvxrj = context.nrt.meminfo_data(builder, lidjb__jued.meminfo)
    fwyrt__nitax = builder.bitcast(qndzs__mvxrj, context.get_value_type(
        payload_type).as_pointer())
    yfbg__fdt = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(fwyrt__nitax))
    return yfbg__fdt


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    yfbg__fdt = _get_struct_arr_payload(c.context, c.builder, typ, val)
    npf__bqumm, length = c.pyapi.call_jit_code(lambda A: len(A), types.
        int64(typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), yfbg__fdt.null_bitmap).data
    nvtxw__mrmct = all(isinstance(jpyf__cap, types.Array) and jpyf__cap.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for jpyf__cap in typ.data)
    if nvtxw__mrmct:
        qesof__kax, qtsey__nbqy, slmvl__vxex = _get_C_API_ptrs(c, yfbg__fdt
            .data, typ.data, typ.names)
        izg__dgqgi = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        sejpp__lzw = cgutils.get_or_insert_function(c.builder.module,
            izg__dgqgi, name='np_array_from_struct_array')
        arr = c.builder.call(sejpp__lzw, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(qesof__kax, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            qtsey__nbqy, lir.IntType(8).as_pointer()), c.builder.bitcast(
            slmvl__vxex, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, yfbg__fdt.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    awd__dleii = context.insert_const_string(builder.module, 'numpy')
    irfea__pgyrw = c.pyapi.import_module_noblock(awd__dleii)
    ssnt__crlt = c.pyapi.object_getattr_string(irfea__pgyrw, 'object_')
    xggve__uzp = c.pyapi.long_from_longlong(length)
    fxx__qwk = c.pyapi.call_method(irfea__pgyrw, 'ndarray', (xggve__uzp,
        ssnt__crlt))
    jbza__ujega = c.pyapi.object_getattr_string(irfea__pgyrw, 'nan')
    with cgutils.for_range(builder, length) as ymfz__sgtpo:
        ahuy__tprn = ymfz__sgtpo.index
        pyarray_setitem(builder, context, fxx__qwk, ahuy__tprn, jbza__ujega)
        kfyb__jsqh = get_bitmap_bit(builder, null_bitmap_ptr, ahuy__tprn)
        jwwy__slb = builder.icmp_unsigned('!=', kfyb__jsqh, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(jwwy__slb):
            if is_tuple_array:
                bmy__ipu = c.pyapi.tuple_new(len(typ.data))
            else:
                bmy__ipu = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(jbza__ujega)
                    c.pyapi.tuple_setitem(bmy__ipu, i, jbza__ujega)
                else:
                    c.pyapi.dict_setitem_string(bmy__ipu, typ.names[i],
                        jbza__ujega)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                npf__bqumm, zyagk__jli = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, ahuy__tprn])
                with builder.if_then(zyagk__jli):
                    npf__bqumm, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, ahuy__tprn])
                    gnc__ktjv = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(bmy__ipu, i, gnc__ktjv)
                    else:
                        c.pyapi.dict_setitem_string(bmy__ipu, typ.names[i],
                            gnc__ktjv)
                        c.pyapi.decref(gnc__ktjv)
            pyarray_setitem(builder, context, fxx__qwk, ahuy__tprn, bmy__ipu)
            c.pyapi.decref(bmy__ipu)
    c.pyapi.decref(irfea__pgyrw)
    c.pyapi.decref(ssnt__crlt)
    c.pyapi.decref(xggve__uzp)
    c.pyapi.decref(jbza__ujega)
    return fxx__qwk


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    jrnxm__wpm = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if jrnxm__wpm == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for gjkw__lclhf in range(jrnxm__wpm)])
    elif nested_counts_type.count < jrnxm__wpm:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for gjkw__lclhf in range(
            jrnxm__wpm - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(jpyf__cap) for jpyf__cap in
            names_typ.types)
    ibcf__svo = tuple(jpyf__cap.instance_type for jpyf__cap in dtypes_typ.types
        )
    struct_arr_type = StructArrayType(ibcf__svo, names)

    def codegen(context, builder, sig, args):
        wzj__isaur, nested_counts, gjkw__lclhf, gjkw__lclhf = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        cwym__ubtjt, gjkw__lclhf, gjkw__lclhf = construct_struct_array(context,
            builder, struct_arr_type, wzj__isaur, nested_counts)
        lidjb__jued = context.make_helper(builder, struct_arr_type)
        lidjb__jued.meminfo = cwym__ubtjt
        return lidjb__jued._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(aadg__ypr, str) for
            aadg__ypr in names) and len(names) == len(data)
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
        gxi__xhdlv = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, gxi__xhdlv)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        gxi__xhdlv = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, gxi__xhdlv)


def define_struct_dtor(context, builder, struct_type, payload_type):
    efhmc__qre = builder.module
    izg__dgqgi = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    ypxw__kju = cgutils.get_or_insert_function(efhmc__qre, izg__dgqgi, name
        ='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not ypxw__kju.is_declaration:
        return ypxw__kju
    ypxw__kju.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(ypxw__kju.append_basic_block())
    bvrp__sqg = ypxw__kju.args[0]
    yoqaw__tvry = context.get_value_type(payload_type).as_pointer()
    ypro__zix = builder.bitcast(bvrp__sqg, yoqaw__tvry)
    yfbg__fdt = context.make_helper(builder, payload_type, ref=ypro__zix)
    for i in range(len(struct_type.data)):
        ppcb__vlfi = builder.extract_value(yfbg__fdt.null_bitmap, i)
        jwwy__slb = builder.icmp_unsigned('==', ppcb__vlfi, lir.Constant(
            ppcb__vlfi.type, 1))
        with builder.if_then(jwwy__slb):
            val = builder.extract_value(yfbg__fdt.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return ypxw__kju


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    qndzs__mvxrj = context.nrt.meminfo_data(builder, struct.meminfo)
    fwyrt__nitax = builder.bitcast(qndzs__mvxrj, context.get_value_type(
        payload_type).as_pointer())
    yfbg__fdt = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(fwyrt__nitax))
    return yfbg__fdt, fwyrt__nitax


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    awd__dleii = context.insert_const_string(builder.module, 'pandas')
    caj__gckn = c.pyapi.import_module_noblock(awd__dleii)
    uufb__qkurg = c.pyapi.object_getattr_string(caj__gckn, 'NA')
    tro__peqnt = []
    nulls = []
    for i, jpyf__cap in enumerate(typ.data):
        gnc__ktjv = c.pyapi.dict_getitem_string(val, typ.names[i])
        aahv__nmiw = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        zgorn__cuhti = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(jpyf__cap)))
        lzy__dnkkb = is_na_value(builder, context, gnc__ktjv, uufb__qkurg)
        jwwy__slb = builder.icmp_unsigned('!=', lzy__dnkkb, lir.Constant(
            lzy__dnkkb.type, 1))
        with builder.if_then(jwwy__slb):
            builder.store(context.get_constant(types.uint8, 1), aahv__nmiw)
            field_val = c.pyapi.to_native_value(jpyf__cap, gnc__ktjv).value
            builder.store(field_val, zgorn__cuhti)
        tro__peqnt.append(builder.load(zgorn__cuhti))
        nulls.append(builder.load(aahv__nmiw))
    c.pyapi.decref(caj__gckn)
    c.pyapi.decref(uufb__qkurg)
    cwym__ubtjt = construct_struct(context, builder, typ, tro__peqnt, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = cwym__ubtjt
    pzhr__hdqzm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=pzhr__hdqzm)


@box(StructType)
def box_struct(typ, val, c):
    jzmpu__bmezy = c.pyapi.dict_new(len(typ.data))
    yfbg__fdt, gjkw__lclhf = _get_struct_payload(c.context, c.builder, typ, val
        )
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(jzmpu__bmezy, typ.names[i], c.pyapi.
            borrow_none())
        ppcb__vlfi = c.builder.extract_value(yfbg__fdt.null_bitmap, i)
        jwwy__slb = c.builder.icmp_unsigned('==', ppcb__vlfi, lir.Constant(
            ppcb__vlfi.type, 1))
        with c.builder.if_then(jwwy__slb):
            uja__dtjp = c.builder.extract_value(yfbg__fdt.data, i)
            c.context.nrt.incref(c.builder, val_typ, uja__dtjp)
            dyeo__picd = c.pyapi.from_native_value(val_typ, uja__dtjp, c.
                env_manager)
            c.pyapi.dict_setitem_string(jzmpu__bmezy, typ.names[i], dyeo__picd)
            c.pyapi.decref(dyeo__picd)
    c.context.nrt.decref(c.builder, typ, val)
    return jzmpu__bmezy


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(jpyf__cap) for jpyf__cap in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, xkv__txg = args
        payload_type = StructPayloadType(struct_type.data)
        xtms__dzas = context.get_value_type(payload_type)
        qnc__ers = context.get_abi_sizeof(xtms__dzas)
        aeej__odtf = define_struct_dtor(context, builder, struct_type,
            payload_type)
        cwym__ubtjt = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, qnc__ers), aeej__odtf)
        qndzs__mvxrj = context.nrt.meminfo_data(builder, cwym__ubtjt)
        fwyrt__nitax = builder.bitcast(qndzs__mvxrj, xtms__dzas.as_pointer())
        yfbg__fdt = cgutils.create_struct_proxy(payload_type)(context, builder)
        yfbg__fdt.data = data
        yfbg__fdt.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for gjkw__lclhf in range(len(
            data_typ.types))])
        builder.store(yfbg__fdt._getvalue(), fwyrt__nitax)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = cwym__ubtjt
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        yfbg__fdt, gjkw__lclhf = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            yfbg__fdt.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        yfbg__fdt, gjkw__lclhf = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            yfbg__fdt.null_bitmap)
    ljnjv__ilrdm = types.UniTuple(types.int8, len(struct_typ.data))
    return ljnjv__ilrdm(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, gjkw__lclhf, val = args
        yfbg__fdt, fwyrt__nitax = _get_struct_payload(context, builder,
            struct_typ, struct)
        zgai__urr = yfbg__fdt.data
        xdm__rez = builder.insert_value(zgai__urr, val, field_ind)
        ftft__zdcgu = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, ftft__zdcgu, zgai__urr)
        context.nrt.incref(builder, ftft__zdcgu, xdm__rez)
        yfbg__fdt.data = xdm__rez
        builder.store(yfbg__fdt._getvalue(), fwyrt__nitax)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    ftvzl__rbbxf = get_overload_const_str(ind)
    if ftvzl__rbbxf not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            ftvzl__rbbxf, struct))
    return struct.names.index(ftvzl__rbbxf)


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
    xtms__dzas = context.get_value_type(payload_type)
    qnc__ers = context.get_abi_sizeof(xtms__dzas)
    aeej__odtf = define_struct_dtor(context, builder, struct_type, payload_type
        )
    cwym__ubtjt = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, qnc__ers), aeej__odtf)
    qndzs__mvxrj = context.nrt.meminfo_data(builder, cwym__ubtjt)
    fwyrt__nitax = builder.bitcast(qndzs__mvxrj, xtms__dzas.as_pointer())
    yfbg__fdt = cgutils.create_struct_proxy(payload_type)(context, builder)
    yfbg__fdt.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    yfbg__fdt.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(yfbg__fdt._getvalue(), fwyrt__nitax)
    return cwym__ubtjt


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    tvq__osr = tuple(d.dtype for d in struct_arr_typ.data)
    ofb__ogspt = StructType(tvq__osr, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        rtbj__zmxl, ind = args
        yfbg__fdt = _get_struct_arr_payload(context, builder,
            struct_arr_typ, rtbj__zmxl)
        tro__peqnt = []
        thtbe__xrty = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            ywt__vtac = builder.extract_value(yfbg__fdt.data, i)
            qydka__yblv = context.compile_internal(builder, lambda arr, ind:
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [ywt__vtac,
                ind])
            thtbe__xrty.append(qydka__yblv)
            nhhji__ddezq = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            jwwy__slb = builder.icmp_unsigned('==', qydka__yblv, lir.
                Constant(qydka__yblv.type, 1))
            with builder.if_then(jwwy__slb):
                qse__mhj = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    ywt__vtac, ind])
                builder.store(qse__mhj, nhhji__ddezq)
            tro__peqnt.append(builder.load(nhhji__ddezq))
        if isinstance(ofb__ogspt, types.DictType):
            etfbn__avptp = [context.insert_const_string(builder.module,
                xfym__kiltz) for xfym__kiltz in struct_arr_typ.names]
            dys__pgj = cgutils.pack_array(builder, tro__peqnt)
            ubd__zxhd = cgutils.pack_array(builder, etfbn__avptp)

            def impl(names, vals):
                d = {}
                for i, xfym__kiltz in enumerate(names):
                    d[xfym__kiltz] = vals[i]
                return d
            ecn__atdul = context.compile_internal(builder, impl, ofb__ogspt
                (types.Tuple(tuple(types.StringLiteral(xfym__kiltz) for
                xfym__kiltz in struct_arr_typ.names)), types.Tuple(tvq__osr
                )), [ubd__zxhd, dys__pgj])
            context.nrt.decref(builder, types.BaseTuple.from_types(tvq__osr
                ), dys__pgj)
            return ecn__atdul
        cwym__ubtjt = construct_struct(context, builder, ofb__ogspt,
            tro__peqnt, thtbe__xrty)
        struct = context.make_helper(builder, ofb__ogspt)
        struct.meminfo = cwym__ubtjt
        return struct._getvalue()
    return ofb__ogspt(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        yfbg__fdt = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            yfbg__fdt.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        yfbg__fdt = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            yfbg__fdt.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(jpyf__cap) for jpyf__cap in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, fwqx__ixx, xkv__txg = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        xtms__dzas = context.get_value_type(payload_type)
        qnc__ers = context.get_abi_sizeof(xtms__dzas)
        aeej__odtf = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        cwym__ubtjt = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, qnc__ers), aeej__odtf)
        qndzs__mvxrj = context.nrt.meminfo_data(builder, cwym__ubtjt)
        fwyrt__nitax = builder.bitcast(qndzs__mvxrj, xtms__dzas.as_pointer())
        yfbg__fdt = cgutils.create_struct_proxy(payload_type)(context, builder)
        yfbg__fdt.data = data
        yfbg__fdt.null_bitmap = fwqx__ixx
        builder.store(yfbg__fdt._getvalue(), fwyrt__nitax)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, fwqx__ixx)
        lidjb__jued = context.make_helper(builder, struct_arr_type)
        lidjb__jued.meminfo = cwym__ubtjt
        return lidjb__jued._getvalue()
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
    gcuh__lfzf = len(arr.data)
    bot__gjg = 'def impl(arr, ind):\n'
    bot__gjg += '  data = get_data(arr)\n'
    bot__gjg += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        bot__gjg += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        bot__gjg += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        bot__gjg += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    bot__gjg += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(gcuh__lfzf)), ', '.join("'{}'".format(xfym__kiltz) for
        xfym__kiltz in arr.names)))
    jgwoc__zpov = {}
    exec(bot__gjg, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, jgwoc__zpov)
    impl = jgwoc__zpov['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        gcuh__lfzf = len(arr.data)
        bot__gjg = 'def impl(arr, ind, val):\n'
        bot__gjg += '  data = get_data(arr)\n'
        bot__gjg += '  null_bitmap = get_null_bitmap(arr)\n'
        bot__gjg += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(gcuh__lfzf):
            if isinstance(val, StructType):
                bot__gjg += "  if is_field_value_null(val, '{}'):\n".format(arr
                    .names[i])
                bot__gjg += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                bot__gjg += '  else:\n'
                bot__gjg += "    data[{}][ind] = val['{}']\n".format(i, arr
                    .names[i])
            else:
                bot__gjg += "  data[{}][ind] = val['{}']\n".format(i, arr.
                    names[i])
        jgwoc__zpov = {}
        exec(bot__gjg, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, jgwoc__zpov)
        impl = jgwoc__zpov['impl']
        return impl
    if isinstance(ind, types.SliceType):
        gcuh__lfzf = len(arr.data)
        bot__gjg = 'def impl(arr, ind, val):\n'
        bot__gjg += '  data = get_data(arr)\n'
        bot__gjg += '  null_bitmap = get_null_bitmap(arr)\n'
        bot__gjg += '  val_data = get_data(val)\n'
        bot__gjg += '  val_null_bitmap = get_null_bitmap(val)\n'
        bot__gjg += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(gcuh__lfzf):
            bot__gjg += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        jgwoc__zpov = {}
        exec(bot__gjg, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, jgwoc__zpov)
        impl = jgwoc__zpov['impl']
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
    bot__gjg = 'def impl(A):\n'
    bot__gjg += '  total_nbytes = 0\n'
    bot__gjg += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        bot__gjg += f'  total_nbytes += data[{i}].nbytes\n'
    bot__gjg += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    bot__gjg += '  return total_nbytes\n'
    jgwoc__zpov = {}
    exec(bot__gjg, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, jgwoc__zpov)
    impl = jgwoc__zpov['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        fwqx__ixx = get_null_bitmap(A)
        nxtde__jjdf = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        knw__wkbr = fwqx__ixx.copy()
        return init_struct_arr(nxtde__jjdf, knw__wkbr, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(aadg__ypr.copy() for aadg__ypr in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    ffea__zds = arrs.count
    bot__gjg = 'def f(arrs):\n'
    bot__gjg += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.format
        (i) for i in range(ffea__zds)))
    jgwoc__zpov = {}
    exec(bot__gjg, {}, jgwoc__zpov)
    impl = jgwoc__zpov['f']
    return impl
