"""Table data type for storing dataframe column arrays. Supports storing many columns
(e.g. >10k) efficiently.
"""
import operator
from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.ir_utils import guard
from numba.core.typing.templates import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_getattr, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from numba.np.arrayobj import _getitem_array_single_int
from numba.parfors.array_analysis import ArrayAnalysis
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, get_overload_const_int, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_none, is_overload_true, raise_bodo_error, to_str_arr_if_dict_array
from bodo.utils.utils import is_whole_slice


class Table:

    def __init__(self, arrs, usecols=None, num_arrs=-1):
        if usecols is not None:
            assert num_arrs != -1, 'num_arrs must be provided if usecols is not None'
            moe__swwu = 0
            ehr__laigk = []
            for i in range(usecols[-1] + 1):
                if i == usecols[moe__swwu]:
                    ehr__laigk.append(arrs[moe__swwu])
                    moe__swwu += 1
                else:
                    ehr__laigk.append(None)
            for hukow__ztloa in range(usecols[-1] + 1, num_arrs):
                ehr__laigk.append(None)
            self.arrays = ehr__laigk
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((cfayh__pvhf == odm__gvcjs).all() for 
            cfayh__pvhf, odm__gvcjs in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        aeml__nfmz = len(self.arrays)
        mcz__kol = dict(zip(range(aeml__nfmz), self.arrays))
        df = pd.DataFrame(mcz__kol, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        tbgz__ckqbo = []
        oehro__qrylw = []
        xgyj__ovr = {}
        mrmyr__fio = {}
        dek__uckh = defaultdict(int)
        vyxfj__bpom = defaultdict(list)
        if not has_runtime_cols:
            for i, kvqo__lmt in enumerate(arr_types):
                if kvqo__lmt not in xgyj__ovr:
                    ayct__ipmq = len(xgyj__ovr)
                    xgyj__ovr[kvqo__lmt] = ayct__ipmq
                    mrmyr__fio[ayct__ipmq] = kvqo__lmt
                mytjk__vsfnk = xgyj__ovr[kvqo__lmt]
                tbgz__ckqbo.append(mytjk__vsfnk)
                oehro__qrylw.append(dek__uckh[mytjk__vsfnk])
                dek__uckh[mytjk__vsfnk] += 1
                vyxfj__bpom[mytjk__vsfnk].append(i)
        self.block_nums = tbgz__ckqbo
        self.block_offsets = oehro__qrylw
        self.type_to_blk = xgyj__ovr
        self.blk_to_type = mrmyr__fio
        self.block_to_arr_ind = vyxfj__bpom
        super(TableType, self).__init__(name=
            f'TableType({arr_types}, {has_runtime_cols})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return self.arr_types, self.has_runtime_cols

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(Table)
def typeof_table(val, c):
    return TableType(tuple(numba.typeof(arr) for arr in val.arrays))


@register_model(TableType)
class TableTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        if fe_type.has_runtime_cols:
            tunyt__aad = [(f'block_{i}', types.List(kvqo__lmt)) for i,
                kvqo__lmt in enumerate(fe_type.arr_types)]
        else:
            tunyt__aad = [(f'block_{mytjk__vsfnk}', types.List(kvqo__lmt)) for
                kvqo__lmt, mytjk__vsfnk in fe_type.type_to_blk.items()]
        tunyt__aad.append(('parent', types.pyobject))
        tunyt__aad.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, tunyt__aad)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    eivb__efkx = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    arbc__lyyj = c.pyapi.make_none()
    iqmf__uhkk = c.context.get_constant(types.int64, 0)
    gfyk__suc = cgutils.alloca_once_value(c.builder, iqmf__uhkk)
    for kvqo__lmt, mytjk__vsfnk in typ.type_to_blk.items():
        pnqs__pnlrx = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[mytjk__vsfnk]))
        hukow__ztloa, owtr__gpvh = ListInstance.allocate_ex(c.context, c.
            builder, types.List(kvqo__lmt), pnqs__pnlrx)
        owtr__gpvh.size = pnqs__pnlrx
        hiqe__zwu = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            mytjk__vsfnk], dtype=np.int64))
        oaih__tam = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, hiqe__zwu)
        with cgutils.for_range(c.builder, pnqs__pnlrx) as shlrp__oyy:
            i = shlrp__oyy.index
            zav__wufk = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), oaih__tam, i)
            rmj__ozh = c.pyapi.long_from_longlong(zav__wufk)
            ldum__fuhd = c.pyapi.object_getitem(eivb__efkx, rmj__ozh)
            lehsy__xww = c.builder.icmp_unsigned('==', ldum__fuhd, arbc__lyyj)
            with c.builder.if_else(lehsy__xww) as (npj__vywsj, uhzw__qls):
                with npj__vywsj:
                    mbqor__evgs = c.context.get_constant_null(kvqo__lmt)
                    owtr__gpvh.inititem(i, mbqor__evgs, incref=False)
                with uhzw__qls:
                    wcr__tsyj = c.pyapi.call_method(ldum__fuhd, '__len__', ())
                    omn__xco = c.pyapi.long_as_longlong(wcr__tsyj)
                    c.builder.store(omn__xco, gfyk__suc)
                    c.pyapi.decref(wcr__tsyj)
                    arr = c.pyapi.to_native_value(kvqo__lmt, ldum__fuhd).value
                    owtr__gpvh.inititem(i, arr, incref=False)
            c.pyapi.decref(ldum__fuhd)
            c.pyapi.decref(rmj__ozh)
        setattr(table, f'block_{mytjk__vsfnk}', owtr__gpvh.value)
    table.len = c.builder.load(gfyk__suc)
    c.pyapi.decref(eivb__efkx)
    c.pyapi.decref(arbc__lyyj)
    xdcea__ntxpy = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=xdcea__ntxpy)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        dxazs__pyd = c.context.get_constant(types.int64, 0)
        for i, kvqo__lmt in enumerate(typ.arr_types):
            ehr__laigk = getattr(table, f'block_{i}')
            khga__kellk = ListInstance(c.context, c.builder, types.List(
                kvqo__lmt), ehr__laigk)
            dxazs__pyd = c.builder.add(dxazs__pyd, khga__kellk.size)
        crx__cpsjc = c.pyapi.list_new(dxazs__pyd)
        yvtn__str = c.context.get_constant(types.int64, 0)
        for i, kvqo__lmt in enumerate(typ.arr_types):
            ehr__laigk = getattr(table, f'block_{i}')
            khga__kellk = ListInstance(c.context, c.builder, types.List(
                kvqo__lmt), ehr__laigk)
            with cgutils.for_range(c.builder, khga__kellk.size) as shlrp__oyy:
                i = shlrp__oyy.index
                arr = khga__kellk.getitem(i)
                c.context.nrt.incref(c.builder, kvqo__lmt, arr)
                idx = c.builder.add(yvtn__str, i)
                c.pyapi.list_setitem(crx__cpsjc, idx, c.pyapi.
                    from_native_value(kvqo__lmt, arr, c.env_manager))
            yvtn__str = c.builder.add(yvtn__str, khga__kellk.size)
        ncl__bxit = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        tocj__qwj = c.pyapi.call_function_objargs(ncl__bxit, (crx__cpsjc,))
        c.pyapi.decref(ncl__bxit)
        c.pyapi.decref(crx__cpsjc)
        c.context.nrt.decref(c.builder, typ, val)
        return tocj__qwj
    crx__cpsjc = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    kns__xak = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for kvqo__lmt, mytjk__vsfnk in typ.type_to_blk.items():
        ehr__laigk = getattr(table, f'block_{mytjk__vsfnk}')
        khga__kellk = ListInstance(c.context, c.builder, types.List(
            kvqo__lmt), ehr__laigk)
        hiqe__zwu = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            mytjk__vsfnk], dtype=np.int64))
        oaih__tam = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, hiqe__zwu)
        with cgutils.for_range(c.builder, khga__kellk.size) as shlrp__oyy:
            i = shlrp__oyy.index
            zav__wufk = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), oaih__tam, i)
            arr = khga__kellk.getitem(i)
            xohhi__vvdh = cgutils.alloca_once_value(c.builder, arr)
            ragsk__kcgcd = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(kvqo__lmt))
            is_null = is_ll_eq(c.builder, xohhi__vvdh, ragsk__kcgcd)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (npj__vywsj, uhzw__qls):
                with npj__vywsj:
                    arbc__lyyj = c.pyapi.make_none()
                    c.pyapi.list_setitem(crx__cpsjc, zav__wufk, arbc__lyyj)
                with uhzw__qls:
                    ldum__fuhd = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, kns__xak)
                        ) as (qui__qpzgt, cit__smek):
                        with qui__qpzgt:
                            hql__ebid = get_df_obj_column_codegen(c.context,
                                c.builder, c.pyapi, table.parent, zav__wufk,
                                kvqo__lmt)
                            c.builder.store(hql__ebid, ldum__fuhd)
                        with cit__smek:
                            c.context.nrt.incref(c.builder, kvqo__lmt, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                kvqo__lmt, arr, c.env_manager), ldum__fuhd)
                    c.pyapi.list_setitem(crx__cpsjc, zav__wufk, c.builder.
                        load(ldum__fuhd))
    ncl__bxit = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    tocj__qwj = c.pyapi.call_function_objargs(ncl__bxit, (crx__cpsjc,))
    c.pyapi.decref(ncl__bxit)
    c.pyapi.decref(crx__cpsjc)
    c.context.nrt.decref(c.builder, typ, val)
    return tocj__qwj


@lower_builtin(len, TableType)
def table_len_lower(context, builder, sig, args):
    impl = table_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def table_len_overload(T):
    if not isinstance(T, TableType):
        return

    def impl(T):
        return T._len
    return impl


@lower_getattr(TableType, 'shape')
def lower_table_shape(context, builder, typ, val):
    impl = table_shape_overload(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def table_shape_overload(T):
    if T.has_runtime_cols:

        def impl(T):
            return T._len, compute_num_runtime_columns(T)
        return impl
    ncols = len(T.arr_types)
    return lambda T: (T._len, types.int64(ncols))


@intrinsic
def compute_num_runtime_columns(typingctx, table_type):
    assert isinstance(table_type, TableType)

    def codegen(context, builder, sig, args):
        table_arg, = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        hmzo__sotx = context.get_constant(types.int64, 0)
        for i, kvqo__lmt in enumerate(table_type.arr_types):
            ehr__laigk = getattr(table, f'block_{i}')
            khga__kellk = ListInstance(context, builder, types.List(
                kvqo__lmt), ehr__laigk)
            hmzo__sotx = builder.add(hmzo__sotx, khga__kellk.size)
        return hmzo__sotx
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    mytjk__vsfnk = table_type.block_nums[col_ind]
    gbymw__nftb = table_type.block_offsets[col_ind]
    ehr__laigk = getattr(table, f'block_{mytjk__vsfnk}')
    khga__kellk = ListInstance(context, builder, types.List(arr_type),
        ehr__laigk)
    arr = khga__kellk.getitem(gbymw__nftb)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, hukow__ztloa = args
        arr = get_table_data_codegen(context, builder, table_arg, col_ind,
            table_type)
        return impl_ret_borrowed(context, builder, arr_type, arr)
    sig = arr_type(table_type, ind_typ)
    return sig, codegen


@intrinsic
def del_column(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType
        ), 'Can only delete columns from a table'
    assert isinstance(ind_typ, types.TypeRef) and isinstance(ind_typ.
        instance_type, MetaType), 'ind_typ must be a typeref for a meta type'
    fxv__qsa = list(ind_typ.instance_type.meta)
    nvpek__uqfdx = defaultdict(list)
    for ind in fxv__qsa:
        nvpek__uqfdx[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, hukow__ztloa = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for mytjk__vsfnk, iox__djiy in nvpek__uqfdx.items():
            arr_type = table_type.blk_to_type[mytjk__vsfnk]
            ehr__laigk = getattr(table, f'block_{mytjk__vsfnk}')
            khga__kellk = ListInstance(context, builder, types.List(
                arr_type), ehr__laigk)
            mbqor__evgs = context.get_constant_null(arr_type)
            if len(iox__djiy) == 1:
                gbymw__nftb = iox__djiy[0]
                arr = khga__kellk.getitem(gbymw__nftb)
                context.nrt.decref(builder, arr_type, arr)
                khga__kellk.inititem(gbymw__nftb, mbqor__evgs, incref=False)
            else:
                pnqs__pnlrx = context.get_constant(types.int64, len(iox__djiy))
                tdjye__ekk = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(iox__djiy, dtype=
                    np.int64))
                gvsz__cpv = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, tdjye__ekk)
                with cgutils.for_range(builder, pnqs__pnlrx) as shlrp__oyy:
                    i = shlrp__oyy.index
                    gbymw__nftb = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), gvsz__cpv, i)
                    arr = khga__kellk.getitem(gbymw__nftb)
                    context.nrt.decref(builder, arr_type, arr)
                    khga__kellk.inititem(gbymw__nftb, mbqor__evgs, incref=False
                        )
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    iqmf__uhkk = context.get_constant(types.int64, 0)
    yfjgi__hym = context.get_constant(types.int64, 1)
    feel__mqnc = arr_type not in in_table_type.type_to_blk
    for kvqo__lmt, mytjk__vsfnk in out_table_type.type_to_blk.items():
        if kvqo__lmt in in_table_type.type_to_blk:
            qkru__okmkw = in_table_type.type_to_blk[kvqo__lmt]
            owtr__gpvh = ListInstance(context, builder, types.List(
                kvqo__lmt), getattr(in_table, f'block_{qkru__okmkw}'))
            context.nrt.incref(builder, types.List(kvqo__lmt), owtr__gpvh.value
                )
            setattr(out_table, f'block_{mytjk__vsfnk}', owtr__gpvh.value)
    if feel__mqnc:
        hukow__ztloa, owtr__gpvh = ListInstance.allocate_ex(context,
            builder, types.List(arr_type), yfjgi__hym)
        owtr__gpvh.size = yfjgi__hym
        owtr__gpvh.inititem(iqmf__uhkk, arr_arg, incref=True)
        mytjk__vsfnk = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{mytjk__vsfnk}', owtr__gpvh.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        mytjk__vsfnk = out_table_type.type_to_blk[arr_type]
        owtr__gpvh = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{mytjk__vsfnk}'))
        if is_new_col:
            n = owtr__gpvh.size
            ltom__vcox = builder.add(n, yfjgi__hym)
            owtr__gpvh.resize(ltom__vcox)
            owtr__gpvh.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            xqt__pwlke = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            owtr__gpvh.setitem(xqt__pwlke, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            xqt__pwlke = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = owtr__gpvh.size
            ltom__vcox = builder.add(n, yfjgi__hym)
            owtr__gpvh.resize(ltom__vcox)
            context.nrt.incref(builder, arr_type, owtr__gpvh.getitem(
                xqt__pwlke))
            owtr__gpvh.move(builder.add(xqt__pwlke, yfjgi__hym), xqt__pwlke,
                builder.sub(n, xqt__pwlke))
            owtr__gpvh.setitem(xqt__pwlke, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    ivk__xubk = in_table_type.arr_types[col_ind]
    if ivk__xubk in out_table_type.type_to_blk:
        mytjk__vsfnk = out_table_type.type_to_blk[ivk__xubk]
        imwf__hrgm = getattr(out_table, f'block_{mytjk__vsfnk}')
        obz__rmx = types.List(ivk__xubk)
        xqt__pwlke = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        sduo__kvis = obz__rmx.dtype(obz__rmx, types.intp)
        hmq__hnp = context.compile_internal(builder, lambda lst, i: lst.pop
            (i), sduo__kvis, (imwf__hrgm, xqt__pwlke))
        context.nrt.decref(builder, ivk__xubk, hmq__hnp)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    gijl__lrj = list(table.arr_types)
    if ind == len(gijl__lrj):
        axer__kbfep = None
        gijl__lrj.append(arr_type)
    else:
        axer__kbfep = table.arr_types[ind]
        gijl__lrj[ind] = arr_type
    xhti__ojp = TableType(tuple(gijl__lrj))
    klsca__jnnt = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': xhti__ojp}
    ehr__fweb = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    ehr__fweb += f'  T2 = init_table(out_table_typ, False)\n'
    ehr__fweb += f'  T2 = set_table_len(T2, len(table))\n'
    ehr__fweb += f'  T2 = set_table_parent(T2, table)\n'
    for typ, mytjk__vsfnk in xhti__ojp.type_to_blk.items():
        if typ in table.type_to_blk:
            ejegl__camb = table.type_to_blk[typ]
            ehr__fweb += (
                f'  arr_list_{mytjk__vsfnk} = get_table_block(table, {ejegl__camb})\n'
                )
            ehr__fweb += f"""  out_arr_list_{mytjk__vsfnk} = alloc_list_like(arr_list_{mytjk__vsfnk}, {len(xhti__ojp.block_to_arr_ind[mytjk__vsfnk])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[ejegl__camb]
                ) & used_cols:
                ehr__fweb += (
                    f'  for i in range(len(arr_list_{mytjk__vsfnk})):\n')
                if typ not in (axer__kbfep, arr_type):
                    ehr__fweb += f"""    out_arr_list_{mytjk__vsfnk}[i] = arr_list_{mytjk__vsfnk}[i]
"""
                else:
                    acmzc__rlly = table.block_to_arr_ind[ejegl__camb]
                    zxwb__klv = np.empty(len(acmzc__rlly), np.int64)
                    jxgxl__ynrb = False
                    for bjp__lytqb, zav__wufk in enumerate(acmzc__rlly):
                        if zav__wufk != ind:
                            koxeu__dds = xhti__ojp.block_offsets[zav__wufk]
                        else:
                            koxeu__dds = -1
                            jxgxl__ynrb = True
                        zxwb__klv[bjp__lytqb] = koxeu__dds
                    klsca__jnnt[f'out_idxs_{mytjk__vsfnk}'] = np.array(
                        zxwb__klv, np.int64)
                    ehr__fweb += f'    out_idx = out_idxs_{mytjk__vsfnk}[i]\n'
                    if jxgxl__ynrb:
                        ehr__fweb += f'    if out_idx == -1:\n'
                        ehr__fweb += f'      continue\n'
                    ehr__fweb += f"""    out_arr_list_{mytjk__vsfnk}[out_idx] = arr_list_{mytjk__vsfnk}[i]
"""
            if typ == arr_type and not is_null:
                ehr__fweb += f"""  out_arr_list_{mytjk__vsfnk}[{xhti__ojp.block_offsets[ind]}] = arr
"""
        else:
            klsca__jnnt[f'arr_list_typ_{mytjk__vsfnk}'] = types.List(arr_type)
            ehr__fweb += f"""  out_arr_list_{mytjk__vsfnk} = alloc_list_like(arr_list_typ_{mytjk__vsfnk}, 1, False)
"""
            if not is_null:
                ehr__fweb += f'  out_arr_list_{mytjk__vsfnk}[0] = arr\n'
        ehr__fweb += (
            f'  T2 = set_table_block(T2, out_arr_list_{mytjk__vsfnk}, {mytjk__vsfnk})\n'
            )
    ehr__fweb += f'  return T2\n'
    zwe__bjk = {}
    exec(ehr__fweb, klsca__jnnt, zwe__bjk)
    return zwe__bjk['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        hrx__htajg = None
    else:
        hrx__htajg = set(used_cols.instance_type.meta)
    cfc__mvtxv = get_overload_const_int(ind)
    return generate_set_table_data_code(table, cfc__mvtxv, arr, hrx__htajg)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    cfc__mvtxv = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        hrx__htajg = None
    else:
        hrx__htajg = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, cfc__mvtxv, arr_type,
        hrx__htajg, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    xfeo__orzby = args[0]
    if equiv_set.has_shape(xfeo__orzby):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            xfeo__orzby)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    wsqd__xbaow = []
    for kvqo__lmt, mytjk__vsfnk in table_type.type_to_blk.items():
        kyn__vvjsn = len(table_type.block_to_arr_ind[mytjk__vsfnk])
        lzttv__zse = []
        for i in range(kyn__vvjsn):
            zav__wufk = table_type.block_to_arr_ind[mytjk__vsfnk][i]
            lzttv__zse.append(pyval.arrays[zav__wufk])
        wsqd__xbaow.append(context.get_constant_generic(builder, types.List
            (kvqo__lmt), lzttv__zse))
    fdmmw__hpve = context.get_constant_null(types.pyobject)
    xppoa__pabi = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(wsqd__xbaow + [fdmmw__hpve, xppoa__pabi]
        )


@intrinsic
def init_table(typingctx, table_type, to_str_if_dict_t):
    out_table_type = table_type.instance_type if isinstance(table_type,
        types.TypeRef) else table_type
    assert isinstance(out_table_type, TableType
        ), 'table type or typeref expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        out_table_type = to_str_arr_if_dict_array(out_table_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(out_table_type)(context, builder)
        for kvqo__lmt, mytjk__vsfnk in out_table_type.type_to_blk.items():
            rvrq__cjz = context.get_constant_null(types.List(kvqo__lmt))
            setattr(table, f'block_{mytjk__vsfnk}', rvrq__cjz)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    cci__vrobn = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        cci__vrobn[typ.dtype] = i
    tjsj__omkjm = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(tjsj__omkjm, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        gepcp__qxm, hukow__ztloa = args
        table = cgutils.create_struct_proxy(tjsj__omkjm)(context, builder)
        for kvqo__lmt, mytjk__vsfnk in tjsj__omkjm.type_to_blk.items():
            idx = cci__vrobn[kvqo__lmt]
            gxwvr__apbzq = signature(types.List(kvqo__lmt),
                tuple_of_lists_type, types.literal(idx))
            xjyj__wzuow = gepcp__qxm, idx
            zkjs__zfn = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, gxwvr__apbzq, xjyj__wzuow)
            setattr(table, f'block_{mytjk__vsfnk}', zkjs__zfn)
        return table._getvalue()
    sig = tjsj__omkjm(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    mytjk__vsfnk = get_overload_const_int(blk_type)
    arr_type = None
    for kvqo__lmt, odm__gvcjs in table_type.type_to_blk.items():
        if odm__gvcjs == mytjk__vsfnk:
            arr_type = kvqo__lmt
            break
    assert arr_type is not None, 'invalid table type block'
    yovz__rmswi = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        ehr__laigk = getattr(table, f'block_{mytjk__vsfnk}')
        return impl_ret_borrowed(context, builder, yovz__rmswi, ehr__laigk)
    sig = yovz__rmswi(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, cwdv__yuh = args
        fbj__qtqy = context.get_python_api(builder)
        ewykd__mrn = used_cols_typ == types.none
        if not ewykd__mrn:
            fbkny__jyxga = numba.cpython.setobj.SetInstance(context,
                builder, types.Set(types.int64), cwdv__yuh)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for kvqo__lmt, mytjk__vsfnk in table_type.type_to_blk.items():
            pnqs__pnlrx = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[mytjk__vsfnk]))
            hiqe__zwu = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                mytjk__vsfnk], dtype=np.int64))
            oaih__tam = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, hiqe__zwu)
            ehr__laigk = getattr(table, f'block_{mytjk__vsfnk}')
            with cgutils.for_range(builder, pnqs__pnlrx) as shlrp__oyy:
                i = shlrp__oyy.index
                zav__wufk = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'), oaih__tam, i
                    )
                cncw__jkyya = types.none(table_type, types.List(kvqo__lmt),
                    types.int64, types.int64)
                rnnyx__rqp = table_arg, ehr__laigk, i, zav__wufk
                if ewykd__mrn:
                    ensure_column_unboxed_codegen(context, builder,
                        cncw__jkyya, rnnyx__rqp)
                else:
                    fhhw__ldp = fbkny__jyxga.contains(zav__wufk)
                    with builder.if_then(fhhw__ldp):
                        ensure_column_unboxed_codegen(context, builder,
                            cncw__jkyya, rnnyx__rqp)
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, used_cols_typ)
    return sig, codegen


@intrinsic
def ensure_column_unboxed(typingctx, table_type, arr_list_t, ind_t, arr_ind_t):
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, arr_list_t, ind_t, arr_ind_t)
    return sig, ensure_column_unboxed_codegen


def ensure_column_unboxed_codegen(context, builder, sig, args):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table_arg, neq__yxir, geme__ufmkw, ehcj__lipg = args
    fbj__qtqy = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    kns__xak = cgutils.is_not_null(builder, table.parent)
    khga__kellk = ListInstance(context, builder, sig.args[1], neq__yxir)
    nmtw__eflp = khga__kellk.getitem(geme__ufmkw)
    xohhi__vvdh = cgutils.alloca_once_value(builder, nmtw__eflp)
    ragsk__kcgcd = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, xohhi__vvdh, ragsk__kcgcd)
    with builder.if_then(is_null):
        with builder.if_else(kns__xak) as (npj__vywsj, uhzw__qls):
            with npj__vywsj:
                ldum__fuhd = get_df_obj_column_codegen(context, builder,
                    fbj__qtqy, table.parent, ehcj__lipg, sig.args[1].dtype)
                arr = fbj__qtqy.to_native_value(sig.args[1].dtype, ldum__fuhd
                    ).value
                khga__kellk.inititem(geme__ufmkw, arr, incref=False)
                fbj__qtqy.decref(ldum__fuhd)
            with uhzw__qls:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    mytjk__vsfnk = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, msyw__ljv, hukow__ztloa = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{mytjk__vsfnk}', msyw__ljv)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, fzf__jpas = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = fzf__jpas
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        cjrfo__pyhrt, kbpwn__fqc = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, kbpwn__fqc)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, cjrfo__pyhrt)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    yovz__rmswi = list_type.instance_type if isinstance(list_type, types.
        TypeRef) else list_type
    assert isinstance(yovz__rmswi, types.List), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        yovz__rmswi = types.List(to_str_arr_if_dict_array(yovz__rmswi.dtype))

    def codegen(context, builder, sig, args):
        mfp__xsrdd = args[1]
        hukow__ztloa, owtr__gpvh = ListInstance.allocate_ex(context,
            builder, yovz__rmswi, mfp__xsrdd)
        owtr__gpvh.size = mfp__xsrdd
        return owtr__gpvh.value
    sig = yovz__rmswi(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    znp__pjr = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(znp__pjr)

    def codegen(context, builder, sig, args):
        mfp__xsrdd, hukow__ztloa = args
        hukow__ztloa, owtr__gpvh = ListInstance.allocate_ex(context,
            builder, list_type, mfp__xsrdd)
        owtr__gpvh.size = mfp__xsrdd
        return owtr__gpvh.value
    sig = list_type(size_typ, data_typ)
    return sig, codegen


def _get_idx_length(idx):
    pass


@overload(_get_idx_length)
def overload_get_idx_length(idx, n):
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        return lambda idx, n: idx.sum()
    assert isinstance(idx, types.SliceType), 'slice index expected'

    def impl(idx, n):
        oeah__uewi = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(oeah__uewi)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    klsca__jnnt = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        lxc__tssbu = used_cols.instance_type
        zcx__tsmq = np.array(lxc__tssbu.meta, dtype=np.int64)
        klsca__jnnt['used_cols_vals'] = zcx__tsmq
        oejps__zgjmf = set([T.block_nums[i] for i in zcx__tsmq])
    else:
        zcx__tsmq = None
    ehr__fweb = 'def table_filter_func(T, idx, used_cols=None):\n'
    ehr__fweb += f'  T2 = init_table(T, False)\n'
    ehr__fweb += f'  l = 0\n'
    if zcx__tsmq is not None and len(zcx__tsmq) == 0:
        ehr__fweb += f'  l = _get_idx_length(idx, len(T))\n'
        ehr__fweb += f'  T2 = set_table_len(T2, l)\n'
        ehr__fweb += f'  return T2\n'
        zwe__bjk = {}
        exec(ehr__fweb, klsca__jnnt, zwe__bjk)
        return zwe__bjk['table_filter_func']
    if zcx__tsmq is not None:
        ehr__fweb += f'  used_set = set(used_cols_vals)\n'
    for mytjk__vsfnk in T.type_to_blk.values():
        ehr__fweb += (
            f'  arr_list_{mytjk__vsfnk} = get_table_block(T, {mytjk__vsfnk})\n'
            )
        ehr__fweb += f"""  out_arr_list_{mytjk__vsfnk} = alloc_list_like(arr_list_{mytjk__vsfnk}, len(arr_list_{mytjk__vsfnk}), False)
"""
        if zcx__tsmq is None or mytjk__vsfnk in oejps__zgjmf:
            klsca__jnnt[f'arr_inds_{mytjk__vsfnk}'] = np.array(T.
                block_to_arr_ind[mytjk__vsfnk], dtype=np.int64)
            ehr__fweb += f'  for i in range(len(arr_list_{mytjk__vsfnk})):\n'
            ehr__fweb += (
                f'    arr_ind_{mytjk__vsfnk} = arr_inds_{mytjk__vsfnk}[i]\n')
            if zcx__tsmq is not None:
                ehr__fweb += (
                    f'    if arr_ind_{mytjk__vsfnk} not in used_set: continue\n'
                    )
            ehr__fweb += f"""    ensure_column_unboxed(T, arr_list_{mytjk__vsfnk}, i, arr_ind_{mytjk__vsfnk})
"""
            ehr__fweb += f"""    out_arr_{mytjk__vsfnk} = ensure_contig_if_np(arr_list_{mytjk__vsfnk}[i][idx])
"""
            ehr__fweb += f'    l = len(out_arr_{mytjk__vsfnk})\n'
            ehr__fweb += (
                f'    out_arr_list_{mytjk__vsfnk}[i] = out_arr_{mytjk__vsfnk}\n'
                )
        ehr__fweb += (
            f'  T2 = set_table_block(T2, out_arr_list_{mytjk__vsfnk}, {mytjk__vsfnk})\n'
            )
    ehr__fweb += f'  T2 = set_table_len(T2, l)\n'
    ehr__fweb += f'  return T2\n'
    zwe__bjk = {}
    exec(ehr__fweb, klsca__jnnt, zwe__bjk)
    return zwe__bjk['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    six__zamy = list(idx.instance_type.meta)
    gijl__lrj = tuple(np.array(T.arr_types, dtype=object)[six__zamy])
    xhti__ojp = TableType(gijl__lrj)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    zlwr__ewi = is_overload_true(copy_arrs)
    klsca__jnnt = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': xhti__ojp}
    if not is_overload_none(used_cols):
        ofgeo__obivo = used_cols.instance_type.meta
        lxf__rjmx = set(ofgeo__obivo)
        klsca__jnnt['kept_cols'] = np.array(ofgeo__obivo, np.int64)
        wmzj__ina = True
    else:
        wmzj__ina = False
    jqc__dupqu = {i: c for i, c in enumerate(six__zamy)}
    ehr__fweb = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    ehr__fweb += f'  T2 = init_table(out_table_typ, False)\n'
    ehr__fweb += f'  T2 = set_table_len(T2, len(T))\n'
    if wmzj__ina and len(lxf__rjmx) == 0:
        ehr__fweb += f'  return T2\n'
        zwe__bjk = {}
        exec(ehr__fweb, klsca__jnnt, zwe__bjk)
        return zwe__bjk['table_subset']
    if wmzj__ina:
        ehr__fweb += f'  kept_cols_set = set(kept_cols)\n'
    for typ, mytjk__vsfnk in xhti__ojp.type_to_blk.items():
        ejegl__camb = T.type_to_blk[typ]
        ehr__fweb += (
            f'  arr_list_{mytjk__vsfnk} = get_table_block(T, {ejegl__camb})\n')
        ehr__fweb += f"""  out_arr_list_{mytjk__vsfnk} = alloc_list_like(arr_list_{mytjk__vsfnk}, {len(xhti__ojp.block_to_arr_ind[mytjk__vsfnk])}, False)
"""
        giixf__malqe = True
        if wmzj__ina:
            walpn__tbuep = set(xhti__ojp.block_to_arr_ind[mytjk__vsfnk])
            inyw__brgj = walpn__tbuep & lxf__rjmx
            giixf__malqe = len(inyw__brgj) > 0
        if giixf__malqe:
            klsca__jnnt[f'out_arr_inds_{mytjk__vsfnk}'] = np.array(xhti__ojp
                .block_to_arr_ind[mytjk__vsfnk], dtype=np.int64)
            ehr__fweb += (
                f'  for i in range(len(out_arr_list_{mytjk__vsfnk})):\n')
            ehr__fweb += (
                f'    out_arr_ind_{mytjk__vsfnk} = out_arr_inds_{mytjk__vsfnk}[i]\n'
                )
            if wmzj__ina:
                ehr__fweb += (
                    f'    if out_arr_ind_{mytjk__vsfnk} not in kept_cols_set: continue\n'
                    )
            wndf__zwgdq = []
            gefyj__ofo = []
            for zkkt__lspln in xhti__ojp.block_to_arr_ind[mytjk__vsfnk]:
                zoll__sio = jqc__dupqu[zkkt__lspln]
                wndf__zwgdq.append(zoll__sio)
                agxbt__izr = T.block_offsets[zoll__sio]
                gefyj__ofo.append(agxbt__izr)
            klsca__jnnt[f'in_logical_idx_{mytjk__vsfnk}'] = np.array(
                wndf__zwgdq, dtype=np.int64)
            klsca__jnnt[f'in_physical_idx_{mytjk__vsfnk}'] = np.array(
                gefyj__ofo, dtype=np.int64)
            ehr__fweb += (
                f'    logical_idx_{mytjk__vsfnk} = in_logical_idx_{mytjk__vsfnk}[i]\n'
                )
            ehr__fweb += (
                f'    physical_idx_{mytjk__vsfnk} = in_physical_idx_{mytjk__vsfnk}[i]\n'
                )
            ehr__fweb += f"""    ensure_column_unboxed(T, arr_list_{mytjk__vsfnk}, physical_idx_{mytjk__vsfnk}, logical_idx_{mytjk__vsfnk})
"""
            cwngs__kly = '.copy()' if zlwr__ewi else ''
            ehr__fweb += f"""    out_arr_list_{mytjk__vsfnk}[i] = arr_list_{mytjk__vsfnk}[physical_idx_{mytjk__vsfnk}]{cwngs__kly}
"""
        ehr__fweb += (
            f'  T2 = set_table_block(T2, out_arr_list_{mytjk__vsfnk}, {mytjk__vsfnk})\n'
            )
    ehr__fweb += f'  return T2\n'
    zwe__bjk = {}
    exec(ehr__fweb, klsca__jnnt, zwe__bjk)
    return zwe__bjk['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    xfeo__orzby = args[0]
    if equiv_set.has_shape(xfeo__orzby):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=xfeo__orzby, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (xfeo__orzby)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    xfeo__orzby = args[0]
    if equiv_set.has_shape(xfeo__orzby):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            xfeo__orzby)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    ehr__fweb = 'def impl(T):\n'
    ehr__fweb += f'  T2 = init_table(T, True)\n'
    ehr__fweb += f'  l = len(T)\n'
    klsca__jnnt = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for mytjk__vsfnk in T.type_to_blk.values():
        klsca__jnnt[f'arr_inds_{mytjk__vsfnk}'] = np.array(T.
            block_to_arr_ind[mytjk__vsfnk], dtype=np.int64)
        ehr__fweb += (
            f'  arr_list_{mytjk__vsfnk} = get_table_block(T, {mytjk__vsfnk})\n'
            )
        ehr__fweb += f"""  out_arr_list_{mytjk__vsfnk} = alloc_list_like(arr_list_{mytjk__vsfnk}, len(arr_list_{mytjk__vsfnk}), True)
"""
        ehr__fweb += f'  for i in range(len(arr_list_{mytjk__vsfnk})):\n'
        ehr__fweb += (
            f'    arr_ind_{mytjk__vsfnk} = arr_inds_{mytjk__vsfnk}[i]\n')
        ehr__fweb += f"""    ensure_column_unboxed(T, arr_list_{mytjk__vsfnk}, i, arr_ind_{mytjk__vsfnk})
"""
        ehr__fweb += f"""    out_arr_{mytjk__vsfnk} = decode_if_dict_array(arr_list_{mytjk__vsfnk}[i])
"""
        ehr__fweb += (
            f'    out_arr_list_{mytjk__vsfnk}[i] = out_arr_{mytjk__vsfnk}\n')
        ehr__fweb += (
            f'  T2 = set_table_block(T2, out_arr_list_{mytjk__vsfnk}, {mytjk__vsfnk})\n'
            )
    ehr__fweb += f'  T2 = set_table_len(T2, l)\n'
    ehr__fweb += f'  return T2\n'
    zwe__bjk = {}
    exec(ehr__fweb, klsca__jnnt, zwe__bjk)
    return zwe__bjk['impl']


@overload(operator.getitem, no_unliteral=True, inline='always')
def overload_table_getitem(T, idx):
    if not isinstance(T, TableType):
        return
    return lambda T, idx: table_filter(T, idx)


@intrinsic
def init_runtime_table_from_lists(typingctx, arr_list_tup_typ, nrows_typ=None):
    assert isinstance(arr_list_tup_typ, types.BaseTuple
        ), 'init_runtime_table_from_lists requires a tuple of list of arrays'
    if isinstance(arr_list_tup_typ, types.UniTuple):
        if arr_list_tup_typ.dtype.dtype == types.undefined:
            return
        mlcy__spvkd = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        mlcy__spvkd = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            mlcy__spvkd.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        yxaf__msqj, aab__cnvf = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = aab__cnvf
        wsqd__xbaow = cgutils.unpack_tuple(builder, yxaf__msqj)
        for i, ehr__laigk in enumerate(wsqd__xbaow):
            setattr(table, f'block_{i}', ehr__laigk)
            context.nrt.incref(builder, types.List(mlcy__spvkd[i]), ehr__laigk)
        return table._getvalue()
    table_type = TableType(tuple(mlcy__spvkd), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen
