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
    zbu__gzacj = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    wyff__rqd = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    vrgk__djb = builder.gep(null_bitmap_ptr, [zbu__gzacj], inbounds=True)
    eejg__rsip = builder.load(vrgk__djb)
    yzxnw__vgg = lir.ArrayType(lir.IntType(8), 8)
    mpoh__hkkw = cgutils.alloca_once_value(builder, lir.Constant(yzxnw__vgg,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    wsju__ndev = builder.load(builder.gep(mpoh__hkkw, [lir.Constant(lir.
        IntType(64), 0), wyff__rqd], inbounds=True))
    if val:
        builder.store(builder.or_(eejg__rsip, wsju__ndev), vrgk__djb)
    else:
        wsju__ndev = builder.xor(wsju__ndev, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(eejg__rsip, wsju__ndev), vrgk__djb)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    zbu__gzacj = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    wyff__rqd = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    eejg__rsip = builder.load(builder.gep(null_bitmap_ptr, [zbu__gzacj],
        inbounds=True))
    yzxnw__vgg = lir.ArrayType(lir.IntType(8), 8)
    mpoh__hkkw = cgutils.alloca_once_value(builder, lir.Constant(yzxnw__vgg,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    wsju__ndev = builder.load(builder.gep(mpoh__hkkw, [lir.Constant(lir.
        IntType(64), 0), wyff__rqd], inbounds=True))
    return builder.and_(eejg__rsip, wsju__ndev)


def pyarray_check(builder, context, obj):
    qtq__hqeoj = context.get_argument_type(types.pyobject)
    ukqt__hstp = lir.FunctionType(lir.IntType(32), [qtq__hqeoj])
    cnstw__eztg = cgutils.get_or_insert_function(builder.module, ukqt__hstp,
        name='is_np_array')
    return builder.call(cnstw__eztg, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    qtq__hqeoj = context.get_argument_type(types.pyobject)
    kytc__aqb = context.get_value_type(types.intp)
    wsfa__gyra = lir.FunctionType(lir.IntType(8).as_pointer(), [qtq__hqeoj,
        kytc__aqb])
    xas__lkzt = cgutils.get_or_insert_function(builder.module, wsfa__gyra,
        name='array_getptr1')
    rjze__ccrsw = lir.FunctionType(qtq__hqeoj, [qtq__hqeoj, lir.IntType(8).
        as_pointer()])
    sjygb__bdvp = cgutils.get_or_insert_function(builder.module,
        rjze__ccrsw, name='array_getitem')
    icjit__fgkl = builder.call(xas__lkzt, [arr_obj, ind])
    return builder.call(sjygb__bdvp, [arr_obj, icjit__fgkl])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    qtq__hqeoj = context.get_argument_type(types.pyobject)
    kytc__aqb = context.get_value_type(types.intp)
    wsfa__gyra = lir.FunctionType(lir.IntType(8).as_pointer(), [qtq__hqeoj,
        kytc__aqb])
    xas__lkzt = cgutils.get_or_insert_function(builder.module, wsfa__gyra,
        name='array_getptr1')
    qkwm__zlf = lir.FunctionType(lir.VoidType(), [qtq__hqeoj, lir.IntType(8
        ).as_pointer(), qtq__hqeoj])
    jjge__xszu = cgutils.get_or_insert_function(builder.module, qkwm__zlf,
        name='array_setitem')
    icjit__fgkl = builder.call(xas__lkzt, [arr_obj, ind])
    builder.call(jjge__xszu, [arr_obj, icjit__fgkl, val_obj])


def seq_getitem(builder, context, obj, ind):
    qtq__hqeoj = context.get_argument_type(types.pyobject)
    kytc__aqb = context.get_value_type(types.intp)
    ypxz__jvgb = lir.FunctionType(qtq__hqeoj, [qtq__hqeoj, kytc__aqb])
    afde__ieij = cgutils.get_or_insert_function(builder.module, ypxz__jvgb,
        name='seq_getitem')
    return builder.call(afde__ieij, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    qtq__hqeoj = context.get_argument_type(types.pyobject)
    oiwkv__wwzpf = lir.FunctionType(lir.IntType(32), [qtq__hqeoj, qtq__hqeoj])
    cexar__vuwt = cgutils.get_or_insert_function(builder.module,
        oiwkv__wwzpf, name='is_na_value')
    return builder.call(cexar__vuwt, [val, C_NA])


def list_check(builder, context, obj):
    qtq__hqeoj = context.get_argument_type(types.pyobject)
    wpg__yaftc = context.get_value_type(types.int32)
    kcml__qtn = lir.FunctionType(wpg__yaftc, [qtq__hqeoj])
    egr__yfarg = cgutils.get_or_insert_function(builder.module, kcml__qtn,
        name='list_check')
    return builder.call(egr__yfarg, [obj])


def dict_keys(builder, context, obj):
    qtq__hqeoj = context.get_argument_type(types.pyobject)
    kcml__qtn = lir.FunctionType(qtq__hqeoj, [qtq__hqeoj])
    egr__yfarg = cgutils.get_or_insert_function(builder.module, kcml__qtn,
        name='dict_keys')
    return builder.call(egr__yfarg, [obj])


def dict_values(builder, context, obj):
    qtq__hqeoj = context.get_argument_type(types.pyobject)
    kcml__qtn = lir.FunctionType(qtq__hqeoj, [qtq__hqeoj])
    egr__yfarg = cgutils.get_or_insert_function(builder.module, kcml__qtn,
        name='dict_values')
    return builder.call(egr__yfarg, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    qtq__hqeoj = context.get_argument_type(types.pyobject)
    kcml__qtn = lir.FunctionType(lir.VoidType(), [qtq__hqeoj, qtq__hqeoj])
    egr__yfarg = cgutils.get_or_insert_function(builder.module, kcml__qtn,
        name='dict_merge_from_seq2')
    builder.call(egr__yfarg, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    cme__vfaxv = cgutils.alloca_once_value(builder, val)
    edt__yms = list_check(builder, context, val)
    fyb__aub = builder.icmp_unsigned('!=', edt__yms, lir.Constant(edt__yms.
        type, 0))
    with builder.if_then(fyb__aub):
        nzme__msfu = context.insert_const_string(builder.module, 'numpy')
        lkb__coa = c.pyapi.import_module_noblock(nzme__msfu)
        gopcc__xrp = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            gopcc__xrp = str(typ.dtype)
        pnf__idml = c.pyapi.object_getattr_string(lkb__coa, gopcc__xrp)
        pls__axdxh = builder.load(cme__vfaxv)
        she__eil = c.pyapi.call_method(lkb__coa, 'asarray', (pls__axdxh,
            pnf__idml))
        builder.store(she__eil, cme__vfaxv)
        c.pyapi.decref(lkb__coa)
        c.pyapi.decref(pnf__idml)
    val = builder.load(cme__vfaxv)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        dtwc__ymkgd = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        pmor__enjo, otnm__oiz = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [dtwc__ymkgd])
        context.nrt.decref(builder, typ, dtwc__ymkgd)
        return cgutils.pack_array(builder, [otnm__oiz])
    if isinstance(typ, (StructType, types.BaseTuple)):
        nzme__msfu = context.insert_const_string(builder.module, 'pandas')
        orzi__nyy = c.pyapi.import_module_noblock(nzme__msfu)
        C_NA = c.pyapi.object_getattr_string(orzi__nyy, 'NA')
        wux__nrxb = bodo.utils.transform.get_type_alloc_counts(typ)
        pvn__hau = context.make_tuple(builder, types.Tuple(wux__nrxb * [
            types.int64]), wux__nrxb * [context.get_constant(types.int64, 0)])
        rhcsk__cwy = cgutils.alloca_once_value(builder, pvn__hau)
        drdx__gdplh = 0
        owyvn__ssw = typ.data if isinstance(typ, StructType) else typ.types
        for pcf__qvr, t in enumerate(owyvn__ssw):
            jfgwf__esc = bodo.utils.transform.get_type_alloc_counts(t)
            if jfgwf__esc == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    pcf__qvr])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, pcf__qvr)
            ysuj__tblu = is_na_value(builder, context, val_obj, C_NA)
            slhq__lrpx = builder.icmp_unsigned('!=', ysuj__tblu, lir.
                Constant(ysuj__tblu.type, 1))
            with builder.if_then(slhq__lrpx):
                pvn__hau = builder.load(rhcsk__cwy)
                cof__wkof = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for pcf__qvr in range(jfgwf__esc):
                    evtmx__uostq = builder.extract_value(pvn__hau, 
                        drdx__gdplh + pcf__qvr)
                    lax__hxje = builder.extract_value(cof__wkof, pcf__qvr)
                    pvn__hau = builder.insert_value(pvn__hau, builder.add(
                        evtmx__uostq, lax__hxje), drdx__gdplh + pcf__qvr)
                builder.store(pvn__hau, rhcsk__cwy)
            drdx__gdplh += jfgwf__esc
        c.pyapi.decref(orzi__nyy)
        c.pyapi.decref(C_NA)
        return builder.load(rhcsk__cwy)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    nzme__msfu = context.insert_const_string(builder.module, 'pandas')
    orzi__nyy = c.pyapi.import_module_noblock(nzme__msfu)
    C_NA = c.pyapi.object_getattr_string(orzi__nyy, 'NA')
    wux__nrxb = bodo.utils.transform.get_type_alloc_counts(typ)
    pvn__hau = context.make_tuple(builder, types.Tuple(wux__nrxb * [types.
        int64]), [n] + (wux__nrxb - 1) * [context.get_constant(types.int64, 0)]
        )
    rhcsk__cwy = cgutils.alloca_once_value(builder, pvn__hau)
    with cgutils.for_range(builder, n) as izhz__cxsfy:
        kqboz__rtw = izhz__cxsfy.index
        vxigz__bam = seq_getitem(builder, context, arr_obj, kqboz__rtw)
        ysuj__tblu = is_na_value(builder, context, vxigz__bam, C_NA)
        slhq__lrpx = builder.icmp_unsigned('!=', ysuj__tblu, lir.Constant(
            ysuj__tblu.type, 1))
        with builder.if_then(slhq__lrpx):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                pvn__hau = builder.load(rhcsk__cwy)
                cof__wkof = get_array_elem_counts(c, builder, context,
                    vxigz__bam, typ.dtype)
                for pcf__qvr in range(wux__nrxb - 1):
                    evtmx__uostq = builder.extract_value(pvn__hau, pcf__qvr + 1
                        )
                    lax__hxje = builder.extract_value(cof__wkof, pcf__qvr)
                    pvn__hau = builder.insert_value(pvn__hau, builder.add(
                        evtmx__uostq, lax__hxje), pcf__qvr + 1)
                builder.store(pvn__hau, rhcsk__cwy)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                drdx__gdplh = 1
                for pcf__qvr, t in enumerate(typ.data):
                    jfgwf__esc = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if jfgwf__esc == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(vxigz__bam, pcf__qvr)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(vxigz__bam,
                            typ.names[pcf__qvr])
                    ysuj__tblu = is_na_value(builder, context, val_obj, C_NA)
                    slhq__lrpx = builder.icmp_unsigned('!=', ysuj__tblu,
                        lir.Constant(ysuj__tblu.type, 1))
                    with builder.if_then(slhq__lrpx):
                        pvn__hau = builder.load(rhcsk__cwy)
                        cof__wkof = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for pcf__qvr in range(jfgwf__esc):
                            evtmx__uostq = builder.extract_value(pvn__hau, 
                                drdx__gdplh + pcf__qvr)
                            lax__hxje = builder.extract_value(cof__wkof,
                                pcf__qvr)
                            pvn__hau = builder.insert_value(pvn__hau,
                                builder.add(evtmx__uostq, lax__hxje), 
                                drdx__gdplh + pcf__qvr)
                        builder.store(pvn__hau, rhcsk__cwy)
                    drdx__gdplh += jfgwf__esc
            else:
                assert isinstance(typ, MapArrayType), typ
                pvn__hau = builder.load(rhcsk__cwy)
                zor__ykdv = dict_keys(builder, context, vxigz__bam)
                bbt__khzds = dict_values(builder, context, vxigz__bam)
                mct__simg = get_array_elem_counts(c, builder, context,
                    zor__ykdv, typ.key_arr_type)
                sned__ifiqg = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for pcf__qvr in range(1, sned__ifiqg + 1):
                    evtmx__uostq = builder.extract_value(pvn__hau, pcf__qvr)
                    lax__hxje = builder.extract_value(mct__simg, pcf__qvr - 1)
                    pvn__hau = builder.insert_value(pvn__hau, builder.add(
                        evtmx__uostq, lax__hxje), pcf__qvr)
                hese__qhx = get_array_elem_counts(c, builder, context,
                    bbt__khzds, typ.value_arr_type)
                for pcf__qvr in range(sned__ifiqg + 1, wux__nrxb):
                    evtmx__uostq = builder.extract_value(pvn__hau, pcf__qvr)
                    lax__hxje = builder.extract_value(hese__qhx, pcf__qvr -
                        sned__ifiqg)
                    pvn__hau = builder.insert_value(pvn__hau, builder.add(
                        evtmx__uostq, lax__hxje), pcf__qvr)
                builder.store(pvn__hau, rhcsk__cwy)
                c.pyapi.decref(zor__ykdv)
                c.pyapi.decref(bbt__khzds)
        c.pyapi.decref(vxigz__bam)
    c.pyapi.decref(orzi__nyy)
    c.pyapi.decref(C_NA)
    return builder.load(rhcsk__cwy)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    yai__wvzw = n_elems.type.count
    assert yai__wvzw >= 1
    rkn__gxxr = builder.extract_value(n_elems, 0)
    if yai__wvzw != 1:
        peoeg__ocq = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, pcf__qvr) for pcf__qvr in range(1, yai__wvzw)])
        pdbl__qxpa = types.Tuple([types.int64] * (yai__wvzw - 1))
    else:
        peoeg__ocq = context.get_dummy_value()
        pdbl__qxpa = types.none
    knpv__lqd = types.TypeRef(arr_type)
    xnx__txfop = arr_type(types.int64, knpv__lqd, pdbl__qxpa)
    args = [rkn__gxxr, context.get_dummy_value(), peoeg__ocq]
    wmayo__bgbxh = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        pmor__enjo, hwm__aigga = c.pyapi.call_jit_code(wmayo__bgbxh,
            xnx__txfop, args)
    else:
        hwm__aigga = context.compile_internal(builder, wmayo__bgbxh,
            xnx__txfop, args)
    return hwm__aigga


def is_ll_eq(builder, val1, val2):
    saqtf__upt = val1.type.pointee
    zcqnj__hehgz = val2.type.pointee
    assert saqtf__upt == zcqnj__hehgz, 'invalid llvm value comparison'
    if isinstance(saqtf__upt, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(saqtf__upt.elements) if isinstance(saqtf__upt, lir.
            BaseStructType) else saqtf__upt.count
        phx__umh = lir.Constant(lir.IntType(1), 1)
        for pcf__qvr in range(n_elems):
            ydat__lqdlj = lir.IntType(32)(0)
            yqyx__pxopj = lir.IntType(32)(pcf__qvr)
            cniud__fgdy = builder.gep(val1, [ydat__lqdlj, yqyx__pxopj],
                inbounds=True)
            daaoj__zruxd = builder.gep(val2, [ydat__lqdlj, yqyx__pxopj],
                inbounds=True)
            phx__umh = builder.and_(phx__umh, is_ll_eq(builder, cniud__fgdy,
                daaoj__zruxd))
        return phx__umh
    ktff__usr = builder.load(val1)
    mfygr__fxc = builder.load(val2)
    if ktff__usr.type in (lir.FloatType(), lir.DoubleType()):
        ufs__btiqg = 32 if ktff__usr.type == lir.FloatType() else 64
        ktff__usr = builder.bitcast(ktff__usr, lir.IntType(ufs__btiqg))
        mfygr__fxc = builder.bitcast(mfygr__fxc, lir.IntType(ufs__btiqg))
    return builder.icmp_unsigned('==', ktff__usr, mfygr__fxc)
