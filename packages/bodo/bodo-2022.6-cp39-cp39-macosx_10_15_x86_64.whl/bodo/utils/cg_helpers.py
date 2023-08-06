"""helper functions for code generation with llvmlite
"""
import llvmlite.binding as ll
from llvmlite import ir as lir
from numba.core import cgutils, types
import bodo
from bodo.libs import array_ext, hdist
ll.add_symbol('array_getitem', array_ext.array_getitem)
ll.add_symbol('seq_getitem', array_ext.seq_getitem)
ll.add_symbol('list_check', array_ext.list_check)
ll.add_symbol('dict_keys', array_ext.dict_keys)
ll.add_symbol('dict_values', array_ext.dict_values)
ll.add_symbol('dict_merge_from_seq2', array_ext.dict_merge_from_seq2)
ll.add_symbol('is_na_value', array_ext.is_na_value)


def set_bitmap_bit(builder, null_bitmap_ptr, ind, val):
    zdhi__yss = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    ejisl__evx = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    lunsx__bqvl = builder.gep(null_bitmap_ptr, [zdhi__yss], inbounds=True)
    yngjj__ubkc = builder.load(lunsx__bqvl)
    cokq__cez = lir.ArrayType(lir.IntType(8), 8)
    plj__difsg = cgutils.alloca_once_value(builder, lir.Constant(cokq__cez,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    dga__xjz = builder.load(builder.gep(plj__difsg, [lir.Constant(lir.
        IntType(64), 0), ejisl__evx], inbounds=True))
    if val:
        builder.store(builder.or_(yngjj__ubkc, dga__xjz), lunsx__bqvl)
    else:
        dga__xjz = builder.xor(dga__xjz, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(yngjj__ubkc, dga__xjz), lunsx__bqvl)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    zdhi__yss = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    ejisl__evx = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    yngjj__ubkc = builder.load(builder.gep(null_bitmap_ptr, [zdhi__yss],
        inbounds=True))
    cokq__cez = lir.ArrayType(lir.IntType(8), 8)
    plj__difsg = cgutils.alloca_once_value(builder, lir.Constant(cokq__cez,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    dga__xjz = builder.load(builder.gep(plj__difsg, [lir.Constant(lir.
        IntType(64), 0), ejisl__evx], inbounds=True))
    return builder.and_(yngjj__ubkc, dga__xjz)


def pyarray_check(builder, context, obj):
    aefsb__zjt = context.get_argument_type(types.pyobject)
    tzqb__elnzj = lir.FunctionType(lir.IntType(32), [aefsb__zjt])
    kpae__yik = cgutils.get_or_insert_function(builder.module, tzqb__elnzj,
        name='is_np_array')
    return builder.call(kpae__yik, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    aefsb__zjt = context.get_argument_type(types.pyobject)
    kzevj__tqu = context.get_value_type(types.intp)
    uej__dwi = lir.FunctionType(lir.IntType(8).as_pointer(), [aefsb__zjt,
        kzevj__tqu])
    qim__ypgb = cgutils.get_or_insert_function(builder.module, uej__dwi,
        name='array_getptr1')
    nllut__kppnv = lir.FunctionType(aefsb__zjt, [aefsb__zjt, lir.IntType(8)
        .as_pointer()])
    bov__kqd = cgutils.get_or_insert_function(builder.module, nllut__kppnv,
        name='array_getitem')
    wlan__esgzj = builder.call(qim__ypgb, [arr_obj, ind])
    return builder.call(bov__kqd, [arr_obj, wlan__esgzj])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    aefsb__zjt = context.get_argument_type(types.pyobject)
    kzevj__tqu = context.get_value_type(types.intp)
    uej__dwi = lir.FunctionType(lir.IntType(8).as_pointer(), [aefsb__zjt,
        kzevj__tqu])
    qim__ypgb = cgutils.get_or_insert_function(builder.module, uej__dwi,
        name='array_getptr1')
    uli__cnh = lir.FunctionType(lir.VoidType(), [aefsb__zjt, lir.IntType(8)
        .as_pointer(), aefsb__zjt])
    eydxi__orwym = cgutils.get_or_insert_function(builder.module, uli__cnh,
        name='array_setitem')
    wlan__esgzj = builder.call(qim__ypgb, [arr_obj, ind])
    builder.call(eydxi__orwym, [arr_obj, wlan__esgzj, val_obj])


def seq_getitem(builder, context, obj, ind):
    aefsb__zjt = context.get_argument_type(types.pyobject)
    kzevj__tqu = context.get_value_type(types.intp)
    ozl__wjauc = lir.FunctionType(aefsb__zjt, [aefsb__zjt, kzevj__tqu])
    smt__tzw = cgutils.get_or_insert_function(builder.module, ozl__wjauc,
        name='seq_getitem')
    return builder.call(smt__tzw, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    aefsb__zjt = context.get_argument_type(types.pyobject)
    qovii__zjig = lir.FunctionType(lir.IntType(32), [aefsb__zjt, aefsb__zjt])
    ajyh__oonx = cgutils.get_or_insert_function(builder.module, qovii__zjig,
        name='is_na_value')
    return builder.call(ajyh__oonx, [val, C_NA])


def list_check(builder, context, obj):
    aefsb__zjt = context.get_argument_type(types.pyobject)
    spira__engsw = context.get_value_type(types.int32)
    uzx__gbc = lir.FunctionType(spira__engsw, [aefsb__zjt])
    hjy__rhrn = cgutils.get_or_insert_function(builder.module, uzx__gbc,
        name='list_check')
    return builder.call(hjy__rhrn, [obj])


def dict_keys(builder, context, obj):
    aefsb__zjt = context.get_argument_type(types.pyobject)
    uzx__gbc = lir.FunctionType(aefsb__zjt, [aefsb__zjt])
    hjy__rhrn = cgutils.get_or_insert_function(builder.module, uzx__gbc,
        name='dict_keys')
    return builder.call(hjy__rhrn, [obj])


def dict_values(builder, context, obj):
    aefsb__zjt = context.get_argument_type(types.pyobject)
    uzx__gbc = lir.FunctionType(aefsb__zjt, [aefsb__zjt])
    hjy__rhrn = cgutils.get_or_insert_function(builder.module, uzx__gbc,
        name='dict_values')
    return builder.call(hjy__rhrn, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    aefsb__zjt = context.get_argument_type(types.pyobject)
    uzx__gbc = lir.FunctionType(lir.VoidType(), [aefsb__zjt, aefsb__zjt])
    hjy__rhrn = cgutils.get_or_insert_function(builder.module, uzx__gbc,
        name='dict_merge_from_seq2')
    builder.call(hjy__rhrn, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    cokp__hyhaz = cgutils.alloca_once_value(builder, val)
    oats__exs = list_check(builder, context, val)
    atx__frnf = builder.icmp_unsigned('!=', oats__exs, lir.Constant(
        oats__exs.type, 0))
    with builder.if_then(atx__frnf):
        odw__ayiq = context.insert_const_string(builder.module, 'numpy')
        uym__rrhuo = c.pyapi.import_module_noblock(odw__ayiq)
        nlio__bwr = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            nlio__bwr = str(typ.dtype)
        kubgy__kztvc = c.pyapi.object_getattr_string(uym__rrhuo, nlio__bwr)
        vvdc__xgg = builder.load(cokp__hyhaz)
        xvgqi__lgxps = c.pyapi.call_method(uym__rrhuo, 'asarray', (
            vvdc__xgg, kubgy__kztvc))
        builder.store(xvgqi__lgxps, cokp__hyhaz)
        c.pyapi.decref(uym__rrhuo)
        c.pyapi.decref(kubgy__kztvc)
    val = builder.load(cokp__hyhaz)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        gkdzu__hpe = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        ydpa__ygyf, czmsc__hcqb = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [gkdzu__hpe])
        context.nrt.decref(builder, typ, gkdzu__hpe)
        return cgutils.pack_array(builder, [czmsc__hcqb])
    if isinstance(typ, (StructType, types.BaseTuple)):
        odw__ayiq = context.insert_const_string(builder.module, 'pandas')
        pwr__runxt = c.pyapi.import_module_noblock(odw__ayiq)
        C_NA = c.pyapi.object_getattr_string(pwr__runxt, 'NA')
        zjqlb__mvmmo = bodo.utils.transform.get_type_alloc_counts(typ)
        isp__ygw = context.make_tuple(builder, types.Tuple(zjqlb__mvmmo * [
            types.int64]), zjqlb__mvmmo * [context.get_constant(types.int64,
            0)])
        zhrj__ufcwt = cgutils.alloca_once_value(builder, isp__ygw)
        iwff__uabq = 0
        fbkvu__etxea = typ.data if isinstance(typ, StructType) else typ.types
        for ttv__updu, t in enumerate(fbkvu__etxea):
            dskj__edlt = bodo.utils.transform.get_type_alloc_counts(t)
            if dskj__edlt == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    ttv__updu])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, ttv__updu)
            svv__qeciq = is_na_value(builder, context, val_obj, C_NA)
            ymyq__upjmj = builder.icmp_unsigned('!=', svv__qeciq, lir.
                Constant(svv__qeciq.type, 1))
            with builder.if_then(ymyq__upjmj):
                isp__ygw = builder.load(zhrj__ufcwt)
                cfesj__jshl = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for ttv__updu in range(dskj__edlt):
                    epi__bpvwl = builder.extract_value(isp__ygw, iwff__uabq +
                        ttv__updu)
                    zifv__gsqa = builder.extract_value(cfesj__jshl, ttv__updu)
                    isp__ygw = builder.insert_value(isp__ygw, builder.add(
                        epi__bpvwl, zifv__gsqa), iwff__uabq + ttv__updu)
                builder.store(isp__ygw, zhrj__ufcwt)
            iwff__uabq += dskj__edlt
        c.pyapi.decref(pwr__runxt)
        c.pyapi.decref(C_NA)
        return builder.load(zhrj__ufcwt)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    odw__ayiq = context.insert_const_string(builder.module, 'pandas')
    pwr__runxt = c.pyapi.import_module_noblock(odw__ayiq)
    C_NA = c.pyapi.object_getattr_string(pwr__runxt, 'NA')
    zjqlb__mvmmo = bodo.utils.transform.get_type_alloc_counts(typ)
    isp__ygw = context.make_tuple(builder, types.Tuple(zjqlb__mvmmo * [
        types.int64]), [n] + (zjqlb__mvmmo - 1) * [context.get_constant(
        types.int64, 0)])
    zhrj__ufcwt = cgutils.alloca_once_value(builder, isp__ygw)
    with cgutils.for_range(builder, n) as qjl__bifkz:
        kfc__dyafv = qjl__bifkz.index
        szp__sfnw = seq_getitem(builder, context, arr_obj, kfc__dyafv)
        svv__qeciq = is_na_value(builder, context, szp__sfnw, C_NA)
        ymyq__upjmj = builder.icmp_unsigned('!=', svv__qeciq, lir.Constant(
            svv__qeciq.type, 1))
        with builder.if_then(ymyq__upjmj):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                isp__ygw = builder.load(zhrj__ufcwt)
                cfesj__jshl = get_array_elem_counts(c, builder, context,
                    szp__sfnw, typ.dtype)
                for ttv__updu in range(zjqlb__mvmmo - 1):
                    epi__bpvwl = builder.extract_value(isp__ygw, ttv__updu + 1)
                    zifv__gsqa = builder.extract_value(cfesj__jshl, ttv__updu)
                    isp__ygw = builder.insert_value(isp__ygw, builder.add(
                        epi__bpvwl, zifv__gsqa), ttv__updu + 1)
                builder.store(isp__ygw, zhrj__ufcwt)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                iwff__uabq = 1
                for ttv__updu, t in enumerate(typ.data):
                    dskj__edlt = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if dskj__edlt == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(szp__sfnw, ttv__updu)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(szp__sfnw,
                            typ.names[ttv__updu])
                    svv__qeciq = is_na_value(builder, context, val_obj, C_NA)
                    ymyq__upjmj = builder.icmp_unsigned('!=', svv__qeciq,
                        lir.Constant(svv__qeciq.type, 1))
                    with builder.if_then(ymyq__upjmj):
                        isp__ygw = builder.load(zhrj__ufcwt)
                        cfesj__jshl = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for ttv__updu in range(dskj__edlt):
                            epi__bpvwl = builder.extract_value(isp__ygw, 
                                iwff__uabq + ttv__updu)
                            zifv__gsqa = builder.extract_value(cfesj__jshl,
                                ttv__updu)
                            isp__ygw = builder.insert_value(isp__ygw,
                                builder.add(epi__bpvwl, zifv__gsqa), 
                                iwff__uabq + ttv__updu)
                        builder.store(isp__ygw, zhrj__ufcwt)
                    iwff__uabq += dskj__edlt
            else:
                assert isinstance(typ, MapArrayType), typ
                isp__ygw = builder.load(zhrj__ufcwt)
                qbza__zrl = dict_keys(builder, context, szp__sfnw)
                iad__pmx = dict_values(builder, context, szp__sfnw)
                gex__gbzm = get_array_elem_counts(c, builder, context,
                    qbza__zrl, typ.key_arr_type)
                dnan__vah = bodo.utils.transform.get_type_alloc_counts(typ.
                    key_arr_type)
                for ttv__updu in range(1, dnan__vah + 1):
                    epi__bpvwl = builder.extract_value(isp__ygw, ttv__updu)
                    zifv__gsqa = builder.extract_value(gex__gbzm, ttv__updu - 1
                        )
                    isp__ygw = builder.insert_value(isp__ygw, builder.add(
                        epi__bpvwl, zifv__gsqa), ttv__updu)
                dksjq__ujdf = get_array_elem_counts(c, builder, context,
                    iad__pmx, typ.value_arr_type)
                for ttv__updu in range(dnan__vah + 1, zjqlb__mvmmo):
                    epi__bpvwl = builder.extract_value(isp__ygw, ttv__updu)
                    zifv__gsqa = builder.extract_value(dksjq__ujdf, 
                        ttv__updu - dnan__vah)
                    isp__ygw = builder.insert_value(isp__ygw, builder.add(
                        epi__bpvwl, zifv__gsqa), ttv__updu)
                builder.store(isp__ygw, zhrj__ufcwt)
                c.pyapi.decref(qbza__zrl)
                c.pyapi.decref(iad__pmx)
        c.pyapi.decref(szp__sfnw)
    c.pyapi.decref(pwr__runxt)
    c.pyapi.decref(C_NA)
    return builder.load(zhrj__ufcwt)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    jzf__lqff = n_elems.type.count
    assert jzf__lqff >= 1
    ipe__jfvaa = builder.extract_value(n_elems, 0)
    if jzf__lqff != 1:
        noly__hmeqq = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, ttv__updu) for ttv__updu in range(1, jzf__lqff)])
        aqlf__wxgn = types.Tuple([types.int64] * (jzf__lqff - 1))
    else:
        noly__hmeqq = context.get_dummy_value()
        aqlf__wxgn = types.none
    fdyf__tnl = types.TypeRef(arr_type)
    hcmqk__xozj = arr_type(types.int64, fdyf__tnl, aqlf__wxgn)
    args = [ipe__jfvaa, context.get_dummy_value(), noly__hmeqq]
    crb__gqzr = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        ydpa__ygyf, yqw__fpop = c.pyapi.call_jit_code(crb__gqzr,
            hcmqk__xozj, args)
    else:
        yqw__fpop = context.compile_internal(builder, crb__gqzr,
            hcmqk__xozj, args)
    return yqw__fpop


def is_ll_eq(builder, val1, val2):
    ahk__yjl = val1.type.pointee
    tmojn__vigrl = val2.type.pointee
    assert ahk__yjl == tmojn__vigrl, 'invalid llvm value comparison'
    if isinstance(ahk__yjl, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(ahk__yjl.elements) if isinstance(ahk__yjl, lir.
            BaseStructType) else ahk__yjl.count
        dnhxl__zyiq = lir.Constant(lir.IntType(1), 1)
        for ttv__updu in range(n_elems):
            yqhmd__lkqw = lir.IntType(32)(0)
            xuce__utrb = lir.IntType(32)(ttv__updu)
            qmevh__afz = builder.gep(val1, [yqhmd__lkqw, xuce__utrb],
                inbounds=True)
            xhn__lbnbn = builder.gep(val2, [yqhmd__lkqw, xuce__utrb],
                inbounds=True)
            dnhxl__zyiq = builder.and_(dnhxl__zyiq, is_ll_eq(builder,
                qmevh__afz, xhn__lbnbn))
        return dnhxl__zyiq
    lqow__chu = builder.load(val1)
    ogk__xicj = builder.load(val2)
    if lqow__chu.type in (lir.FloatType(), lir.DoubleType()):
        omg__obcn = 32 if lqow__chu.type == lir.FloatType() else 64
        lqow__chu = builder.bitcast(lqow__chu, lir.IntType(omg__obcn))
        ogk__xicj = builder.bitcast(ogk__xicj, lir.IntType(omg__obcn))
    return builder.icmp_unsigned('==', lqow__chu, ogk__xicj)
