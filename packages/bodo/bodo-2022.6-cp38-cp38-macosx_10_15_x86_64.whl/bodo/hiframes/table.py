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
            lvsq__ggjbq = 0
            ljemz__zaj = []
            for i in range(usecols[-1] + 1):
                if i == usecols[lvsq__ggjbq]:
                    ljemz__zaj.append(arrs[lvsq__ggjbq])
                    lvsq__ggjbq += 1
                else:
                    ljemz__zaj.append(None)
            for fynq__pmr in range(usecols[-1] + 1, num_arrs):
                ljemz__zaj.append(None)
            self.arrays = ljemz__zaj
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((aox__svg == uixtj__xlvrc).all() for aox__svg,
            uixtj__xlvrc in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        cdvnu__tofsj = len(self.arrays)
        owk__mfd = dict(zip(range(cdvnu__tofsj), self.arrays))
        df = pd.DataFrame(owk__mfd, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        ojkfu__qvsu = []
        fyg__kdxr = []
        sybo__paozu = {}
        apld__vennv = {}
        zmnx__gpink = defaultdict(int)
        qdap__uciu = defaultdict(list)
        if not has_runtime_cols:
            for i, nvfz__djb in enumerate(arr_types):
                if nvfz__djb not in sybo__paozu:
                    var__cnpwb = len(sybo__paozu)
                    sybo__paozu[nvfz__djb] = var__cnpwb
                    apld__vennv[var__cnpwb] = nvfz__djb
                fhk__csba = sybo__paozu[nvfz__djb]
                ojkfu__qvsu.append(fhk__csba)
                fyg__kdxr.append(zmnx__gpink[fhk__csba])
                zmnx__gpink[fhk__csba] += 1
                qdap__uciu[fhk__csba].append(i)
        self.block_nums = ojkfu__qvsu
        self.block_offsets = fyg__kdxr
        self.type_to_blk = sybo__paozu
        self.blk_to_type = apld__vennv
        self.block_to_arr_ind = qdap__uciu
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
            nmymj__hkoa = [(f'block_{i}', types.List(nvfz__djb)) for i,
                nvfz__djb in enumerate(fe_type.arr_types)]
        else:
            nmymj__hkoa = [(f'block_{fhk__csba}', types.List(nvfz__djb)) for
                nvfz__djb, fhk__csba in fe_type.type_to_blk.items()]
        nmymj__hkoa.append(('parent', types.pyobject))
        nmymj__hkoa.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, nmymj__hkoa)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    dwmhi__hyti = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    njhns__zwk = c.pyapi.make_none()
    ffo__ihscv = c.context.get_constant(types.int64, 0)
    twyff__xig = cgutils.alloca_once_value(c.builder, ffo__ihscv)
    for nvfz__djb, fhk__csba in typ.type_to_blk.items():
        qss__cwhx = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[fhk__csba]))
        fynq__pmr, ftu__mmjb = ListInstance.allocate_ex(c.context, c.
            builder, types.List(nvfz__djb), qss__cwhx)
        ftu__mmjb.size = qss__cwhx
        fakc__gtntl = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[fhk__csba],
            dtype=np.int64))
        galk__tevyq = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, fakc__gtntl)
        with cgutils.for_range(c.builder, qss__cwhx) as zak__rnu:
            i = zak__rnu.index
            hfbmu__mmmxd = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), galk__tevyq, i)
            xjpl__zbrg = c.pyapi.long_from_longlong(hfbmu__mmmxd)
            gas__ptshh = c.pyapi.object_getitem(dwmhi__hyti, xjpl__zbrg)
            fzpt__pnx = c.builder.icmp_unsigned('==', gas__ptshh, njhns__zwk)
            with c.builder.if_else(fzpt__pnx) as (lyu__dbt, wpg__vzk):
                with lyu__dbt:
                    mxjc__duo = c.context.get_constant_null(nvfz__djb)
                    ftu__mmjb.inititem(i, mxjc__duo, incref=False)
                with wpg__vzk:
                    cgu__dzbl = c.pyapi.call_method(gas__ptshh, '__len__', ())
                    kyyw__pka = c.pyapi.long_as_longlong(cgu__dzbl)
                    c.builder.store(kyyw__pka, twyff__xig)
                    c.pyapi.decref(cgu__dzbl)
                    arr = c.pyapi.to_native_value(nvfz__djb, gas__ptshh).value
                    ftu__mmjb.inititem(i, arr, incref=False)
            c.pyapi.decref(gas__ptshh)
            c.pyapi.decref(xjpl__zbrg)
        setattr(table, f'block_{fhk__csba}', ftu__mmjb.value)
    table.len = c.builder.load(twyff__xig)
    c.pyapi.decref(dwmhi__hyti)
    c.pyapi.decref(njhns__zwk)
    sfz__zgf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=sfz__zgf)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        yqa__ibn = c.context.get_constant(types.int64, 0)
        for i, nvfz__djb in enumerate(typ.arr_types):
            ljemz__zaj = getattr(table, f'block_{i}')
            lfgdb__rhe = ListInstance(c.context, c.builder, types.List(
                nvfz__djb), ljemz__zaj)
            yqa__ibn = c.builder.add(yqa__ibn, lfgdb__rhe.size)
        cyrik__emh = c.pyapi.list_new(yqa__ibn)
        kitnd__bsni = c.context.get_constant(types.int64, 0)
        for i, nvfz__djb in enumerate(typ.arr_types):
            ljemz__zaj = getattr(table, f'block_{i}')
            lfgdb__rhe = ListInstance(c.context, c.builder, types.List(
                nvfz__djb), ljemz__zaj)
            with cgutils.for_range(c.builder, lfgdb__rhe.size) as zak__rnu:
                i = zak__rnu.index
                arr = lfgdb__rhe.getitem(i)
                c.context.nrt.incref(c.builder, nvfz__djb, arr)
                idx = c.builder.add(kitnd__bsni, i)
                c.pyapi.list_setitem(cyrik__emh, idx, c.pyapi.
                    from_native_value(nvfz__djb, arr, c.env_manager))
            kitnd__bsni = c.builder.add(kitnd__bsni, lfgdb__rhe.size)
        oaw__snnlg = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        zmv__kiae = c.pyapi.call_function_objargs(oaw__snnlg, (cyrik__emh,))
        c.pyapi.decref(oaw__snnlg)
        c.pyapi.decref(cyrik__emh)
        c.context.nrt.decref(c.builder, typ, val)
        return zmv__kiae
    cyrik__emh = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    ftd__ewob = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for nvfz__djb, fhk__csba in typ.type_to_blk.items():
        ljemz__zaj = getattr(table, f'block_{fhk__csba}')
        lfgdb__rhe = ListInstance(c.context, c.builder, types.List(
            nvfz__djb), ljemz__zaj)
        fakc__gtntl = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[fhk__csba],
            dtype=np.int64))
        galk__tevyq = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, fakc__gtntl)
        with cgutils.for_range(c.builder, lfgdb__rhe.size) as zak__rnu:
            i = zak__rnu.index
            hfbmu__mmmxd = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), galk__tevyq, i)
            arr = lfgdb__rhe.getitem(i)
            irj__ezprj = cgutils.alloca_once_value(c.builder, arr)
            mxd__rkcs = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(nvfz__djb))
            is_null = is_ll_eq(c.builder, irj__ezprj, mxd__rkcs)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (lyu__dbt, wpg__vzk):
                with lyu__dbt:
                    njhns__zwk = c.pyapi.make_none()
                    c.pyapi.list_setitem(cyrik__emh, hfbmu__mmmxd, njhns__zwk)
                with wpg__vzk:
                    gas__ptshh = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, ftd__ewob)
                        ) as (jqwss__aonsr, lxj__fno):
                        with jqwss__aonsr:
                            weqy__sfqkf = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, table.parent,
                                hfbmu__mmmxd, nvfz__djb)
                            c.builder.store(weqy__sfqkf, gas__ptshh)
                        with lxj__fno:
                            c.context.nrt.incref(c.builder, nvfz__djb, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                nvfz__djb, arr, c.env_manager), gas__ptshh)
                    c.pyapi.list_setitem(cyrik__emh, hfbmu__mmmxd, c.
                        builder.load(gas__ptshh))
    oaw__snnlg = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    zmv__kiae = c.pyapi.call_function_objargs(oaw__snnlg, (cyrik__emh,))
    c.pyapi.decref(oaw__snnlg)
    c.pyapi.decref(cyrik__emh)
    c.context.nrt.decref(c.builder, typ, val)
    return zmv__kiae


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
        gwpc__lxznf = context.get_constant(types.int64, 0)
        for i, nvfz__djb in enumerate(table_type.arr_types):
            ljemz__zaj = getattr(table, f'block_{i}')
            lfgdb__rhe = ListInstance(context, builder, types.List(
                nvfz__djb), ljemz__zaj)
            gwpc__lxznf = builder.add(gwpc__lxznf, lfgdb__rhe.size)
        return gwpc__lxznf
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    fhk__csba = table_type.block_nums[col_ind]
    evafg__bzbc = table_type.block_offsets[col_ind]
    ljemz__zaj = getattr(table, f'block_{fhk__csba}')
    lfgdb__rhe = ListInstance(context, builder, types.List(arr_type),
        ljemz__zaj)
    arr = lfgdb__rhe.getitem(evafg__bzbc)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, fynq__pmr = args
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
    dot__ytl = list(ind_typ.instance_type.meta)
    flxu__qxc = defaultdict(list)
    for ind in dot__ytl:
        flxu__qxc[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, fynq__pmr = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for fhk__csba, bwv__nhv in flxu__qxc.items():
            arr_type = table_type.blk_to_type[fhk__csba]
            ljemz__zaj = getattr(table, f'block_{fhk__csba}')
            lfgdb__rhe = ListInstance(context, builder, types.List(arr_type
                ), ljemz__zaj)
            mxjc__duo = context.get_constant_null(arr_type)
            if len(bwv__nhv) == 1:
                evafg__bzbc = bwv__nhv[0]
                arr = lfgdb__rhe.getitem(evafg__bzbc)
                context.nrt.decref(builder, arr_type, arr)
                lfgdb__rhe.inititem(evafg__bzbc, mxjc__duo, incref=False)
            else:
                qss__cwhx = context.get_constant(types.int64, len(bwv__nhv))
                uumt__watkr = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(bwv__nhv, dtype=np
                    .int64))
                sxxf__jarq = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, uumt__watkr)
                with cgutils.for_range(builder, qss__cwhx) as zak__rnu:
                    i = zak__rnu.index
                    evafg__bzbc = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), sxxf__jarq, i)
                    arr = lfgdb__rhe.getitem(evafg__bzbc)
                    context.nrt.decref(builder, arr_type, arr)
                    lfgdb__rhe.inititem(evafg__bzbc, mxjc__duo, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    ffo__ihscv = context.get_constant(types.int64, 0)
    kjttj__mve = context.get_constant(types.int64, 1)
    xiefv__dyo = arr_type not in in_table_type.type_to_blk
    for nvfz__djb, fhk__csba in out_table_type.type_to_blk.items():
        if nvfz__djb in in_table_type.type_to_blk:
            slb__lywpw = in_table_type.type_to_blk[nvfz__djb]
            ftu__mmjb = ListInstance(context, builder, types.List(nvfz__djb
                ), getattr(in_table, f'block_{slb__lywpw}'))
            context.nrt.incref(builder, types.List(nvfz__djb), ftu__mmjb.value)
            setattr(out_table, f'block_{fhk__csba}', ftu__mmjb.value)
    if xiefv__dyo:
        fynq__pmr, ftu__mmjb = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), kjttj__mve)
        ftu__mmjb.size = kjttj__mve
        ftu__mmjb.inititem(ffo__ihscv, arr_arg, incref=True)
        fhk__csba = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{fhk__csba}', ftu__mmjb.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        fhk__csba = out_table_type.type_to_blk[arr_type]
        ftu__mmjb = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{fhk__csba}'))
        if is_new_col:
            n = ftu__mmjb.size
            uih__blyjj = builder.add(n, kjttj__mve)
            ftu__mmjb.resize(uih__blyjj)
            ftu__mmjb.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            zkidg__gne = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            ftu__mmjb.setitem(zkidg__gne, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            zkidg__gne = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = ftu__mmjb.size
            uih__blyjj = builder.add(n, kjttj__mve)
            ftu__mmjb.resize(uih__blyjj)
            context.nrt.incref(builder, arr_type, ftu__mmjb.getitem(zkidg__gne)
                )
            ftu__mmjb.move(builder.add(zkidg__gne, kjttj__mve), zkidg__gne,
                builder.sub(n, zkidg__gne))
            ftu__mmjb.setitem(zkidg__gne, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    hpyi__bgpvh = in_table_type.arr_types[col_ind]
    if hpyi__bgpvh in out_table_type.type_to_blk:
        fhk__csba = out_table_type.type_to_blk[hpyi__bgpvh]
        aamov__gzmbs = getattr(out_table, f'block_{fhk__csba}')
        hgex__jjl = types.List(hpyi__bgpvh)
        zkidg__gne = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        kxmzu__rch = hgex__jjl.dtype(hgex__jjl, types.intp)
        oxsk__bku = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), kxmzu__rch, (aamov__gzmbs, zkidg__gne))
        context.nrt.decref(builder, hpyi__bgpvh, oxsk__bku)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    bbdf__jfpo = list(table.arr_types)
    if ind == len(bbdf__jfpo):
        oerp__emqf = None
        bbdf__jfpo.append(arr_type)
    else:
        oerp__emqf = table.arr_types[ind]
        bbdf__jfpo[ind] = arr_type
    ppx__vey = TableType(tuple(bbdf__jfpo))
    dfxw__ablxn = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': ppx__vey}
    kmn__bgdaz = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    kmn__bgdaz += f'  T2 = init_table(out_table_typ, False)\n'
    kmn__bgdaz += f'  T2 = set_table_len(T2, len(table))\n'
    kmn__bgdaz += f'  T2 = set_table_parent(T2, table)\n'
    for typ, fhk__csba in ppx__vey.type_to_blk.items():
        if typ in table.type_to_blk:
            usuqg__qsjx = table.type_to_blk[typ]
            kmn__bgdaz += (
                f'  arr_list_{fhk__csba} = get_table_block(table, {usuqg__qsjx})\n'
                )
            kmn__bgdaz += f"""  out_arr_list_{fhk__csba} = alloc_list_like(arr_list_{fhk__csba}, {len(ppx__vey.block_to_arr_ind[fhk__csba])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[usuqg__qsjx]
                ) & used_cols:
                kmn__bgdaz += f'  for i in range(len(arr_list_{fhk__csba})):\n'
                if typ not in (oerp__emqf, arr_type):
                    kmn__bgdaz += (
                        f'    out_arr_list_{fhk__csba}[i] = arr_list_{fhk__csba}[i]\n'
                        )
                else:
                    pvtnu__svu = table.block_to_arr_ind[usuqg__qsjx]
                    oel__jopa = np.empty(len(pvtnu__svu), np.int64)
                    wgl__xrqgi = False
                    for pldw__voe, hfbmu__mmmxd in enumerate(pvtnu__svu):
                        if hfbmu__mmmxd != ind:
                            egsre__fuk = ppx__vey.block_offsets[hfbmu__mmmxd]
                        else:
                            egsre__fuk = -1
                            wgl__xrqgi = True
                        oel__jopa[pldw__voe] = egsre__fuk
                    dfxw__ablxn[f'out_idxs_{fhk__csba}'] = np.array(oel__jopa,
                        np.int64)
                    kmn__bgdaz += f'    out_idx = out_idxs_{fhk__csba}[i]\n'
                    if wgl__xrqgi:
                        kmn__bgdaz += f'    if out_idx == -1:\n'
                        kmn__bgdaz += f'      continue\n'
                    kmn__bgdaz += f"""    out_arr_list_{fhk__csba}[out_idx] = arr_list_{fhk__csba}[i]
"""
            if typ == arr_type and not is_null:
                kmn__bgdaz += (
                    f'  out_arr_list_{fhk__csba}[{ppx__vey.block_offsets[ind]}] = arr\n'
                    )
        else:
            dfxw__ablxn[f'arr_list_typ_{fhk__csba}'] = types.List(arr_type)
            kmn__bgdaz += f"""  out_arr_list_{fhk__csba} = alloc_list_like(arr_list_typ_{fhk__csba}, 1, False)
"""
            if not is_null:
                kmn__bgdaz += f'  out_arr_list_{fhk__csba}[0] = arr\n'
        kmn__bgdaz += (
            f'  T2 = set_table_block(T2, out_arr_list_{fhk__csba}, {fhk__csba})\n'
            )
    kmn__bgdaz += f'  return T2\n'
    fsozy__ujw = {}
    exec(kmn__bgdaz, dfxw__ablxn, fsozy__ujw)
    return fsozy__ujw['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        qqkx__yyvjw = None
    else:
        qqkx__yyvjw = set(used_cols.instance_type.meta)
    iiwlr__namb = get_overload_const_int(ind)
    return generate_set_table_data_code(table, iiwlr__namb, arr, qqkx__yyvjw)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    iiwlr__namb = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        qqkx__yyvjw = None
    else:
        qqkx__yyvjw = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, iiwlr__namb, arr_type,
        qqkx__yyvjw, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    vie__kdd = args[0]
    if equiv_set.has_shape(vie__kdd):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            vie__kdd)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    vlucb__ohl = []
    for nvfz__djb, fhk__csba in table_type.type_to_blk.items():
        xlhra__woenp = len(table_type.block_to_arr_ind[fhk__csba])
        jbi__qivqf = []
        for i in range(xlhra__woenp):
            hfbmu__mmmxd = table_type.block_to_arr_ind[fhk__csba][i]
            jbi__qivqf.append(pyval.arrays[hfbmu__mmmxd])
        vlucb__ohl.append(context.get_constant_generic(builder, types.List(
            nvfz__djb), jbi__qivqf))
    qzvb__llc = context.get_constant_null(types.pyobject)
    hpptq__juwja = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(vlucb__ohl + [qzvb__llc, hpptq__juwja])


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
        for nvfz__djb, fhk__csba in out_table_type.type_to_blk.items():
            hnqhl__rqx = context.get_constant_null(types.List(nvfz__djb))
            setattr(table, f'block_{fhk__csba}', hnqhl__rqx)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    nnes__bcg = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        nnes__bcg[typ.dtype] = i
    dhudw__swhn = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(dhudw__swhn, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        ndp__qmq, fynq__pmr = args
        table = cgutils.create_struct_proxy(dhudw__swhn)(context, builder)
        for nvfz__djb, fhk__csba in dhudw__swhn.type_to_blk.items():
            idx = nnes__bcg[nvfz__djb]
            amx__eav = signature(types.List(nvfz__djb), tuple_of_lists_type,
                types.literal(idx))
            lxz__rogqt = ndp__qmq, idx
            bed__zcw = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, amx__eav, lxz__rogqt)
            setattr(table, f'block_{fhk__csba}', bed__zcw)
        return table._getvalue()
    sig = dhudw__swhn(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    fhk__csba = get_overload_const_int(blk_type)
    arr_type = None
    for nvfz__djb, uixtj__xlvrc in table_type.type_to_blk.items():
        if uixtj__xlvrc == fhk__csba:
            arr_type = nvfz__djb
            break
    assert arr_type is not None, 'invalid table type block'
    ntlri__vlnyy = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        ljemz__zaj = getattr(table, f'block_{fhk__csba}')
        return impl_ret_borrowed(context, builder, ntlri__vlnyy, ljemz__zaj)
    sig = ntlri__vlnyy(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, xqz__tmyb = args
        kgx__yseb = context.get_python_api(builder)
        iizym__kjy = used_cols_typ == types.none
        if not iizym__kjy:
            ekpb__lmcrr = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), xqz__tmyb)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for nvfz__djb, fhk__csba in table_type.type_to_blk.items():
            qss__cwhx = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[fhk__csba]))
            fakc__gtntl = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                fhk__csba], dtype=np.int64))
            galk__tevyq = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, fakc__gtntl)
            ljemz__zaj = getattr(table, f'block_{fhk__csba}')
            with cgutils.for_range(builder, qss__cwhx) as zak__rnu:
                i = zak__rnu.index
                hfbmu__mmmxd = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    galk__tevyq, i)
                fyhr__fzl = types.none(table_type, types.List(nvfz__djb),
                    types.int64, types.int64)
                awyf__ktx = table_arg, ljemz__zaj, i, hfbmu__mmmxd
                if iizym__kjy:
                    ensure_column_unboxed_codegen(context, builder,
                        fyhr__fzl, awyf__ktx)
                else:
                    lfwo__wcw = ekpb__lmcrr.contains(hfbmu__mmmxd)
                    with builder.if_then(lfwo__wcw):
                        ensure_column_unboxed_codegen(context, builder,
                            fyhr__fzl, awyf__ktx)
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
    table_arg, ayqf__uxzbm, edb__euze, yfzdm__jska = args
    kgx__yseb = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    ftd__ewob = cgutils.is_not_null(builder, table.parent)
    lfgdb__rhe = ListInstance(context, builder, sig.args[1], ayqf__uxzbm)
    ion__ywxvi = lfgdb__rhe.getitem(edb__euze)
    irj__ezprj = cgutils.alloca_once_value(builder, ion__ywxvi)
    mxd__rkcs = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, irj__ezprj, mxd__rkcs)
    with builder.if_then(is_null):
        with builder.if_else(ftd__ewob) as (lyu__dbt, wpg__vzk):
            with lyu__dbt:
                gas__ptshh = get_df_obj_column_codegen(context, builder,
                    kgx__yseb, table.parent, yfzdm__jska, sig.args[1].dtype)
                arr = kgx__yseb.to_native_value(sig.args[1].dtype, gas__ptshh
                    ).value
                lfgdb__rhe.inititem(edb__euze, arr, incref=False)
                kgx__yseb.decref(gas__ptshh)
            with wpg__vzk:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    fhk__csba = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, kkz__iie, fynq__pmr = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{fhk__csba}', kkz__iie)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, uwvl__fib = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = uwvl__fib
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        bmsfd__wifl, utu__aifgj = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, utu__aifgj)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, bmsfd__wifl)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    ntlri__vlnyy = list_type.instance_type if isinstance(list_type, types.
        TypeRef) else list_type
    assert isinstance(ntlri__vlnyy, types.List
        ), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        ntlri__vlnyy = types.List(to_str_arr_if_dict_array(ntlri__vlnyy.dtype))

    def codegen(context, builder, sig, args):
        mtrgi__guhtl = args[1]
        fynq__pmr, ftu__mmjb = ListInstance.allocate_ex(context, builder,
            ntlri__vlnyy, mtrgi__guhtl)
        ftu__mmjb.size = mtrgi__guhtl
        return ftu__mmjb.value
    sig = ntlri__vlnyy(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    gkr__sncn = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(gkr__sncn)

    def codegen(context, builder, sig, args):
        mtrgi__guhtl, fynq__pmr = args
        fynq__pmr, ftu__mmjb = ListInstance.allocate_ex(context, builder,
            list_type, mtrgi__guhtl)
        ftu__mmjb.size = mtrgi__guhtl
        return ftu__mmjb.value
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
        oqrdh__oqo = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(oqrdh__oqo)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    dfxw__ablxn = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        enfe__azdf = used_cols.instance_type
        mnp__cxmuc = np.array(enfe__azdf.meta, dtype=np.int64)
        dfxw__ablxn['used_cols_vals'] = mnp__cxmuc
        edujj__dtrd = set([T.block_nums[i] for i in mnp__cxmuc])
    else:
        mnp__cxmuc = None
    kmn__bgdaz = 'def table_filter_func(T, idx, used_cols=None):\n'
    kmn__bgdaz += f'  T2 = init_table(T, False)\n'
    kmn__bgdaz += f'  l = 0\n'
    if mnp__cxmuc is not None and len(mnp__cxmuc) == 0:
        kmn__bgdaz += f'  l = _get_idx_length(idx, len(T))\n'
        kmn__bgdaz += f'  T2 = set_table_len(T2, l)\n'
        kmn__bgdaz += f'  return T2\n'
        fsozy__ujw = {}
        exec(kmn__bgdaz, dfxw__ablxn, fsozy__ujw)
        return fsozy__ujw['table_filter_func']
    if mnp__cxmuc is not None:
        kmn__bgdaz += f'  used_set = set(used_cols_vals)\n'
    for fhk__csba in T.type_to_blk.values():
        kmn__bgdaz += (
            f'  arr_list_{fhk__csba} = get_table_block(T, {fhk__csba})\n')
        kmn__bgdaz += f"""  out_arr_list_{fhk__csba} = alloc_list_like(arr_list_{fhk__csba}, len(arr_list_{fhk__csba}), False)
"""
        if mnp__cxmuc is None or fhk__csba in edujj__dtrd:
            dfxw__ablxn[f'arr_inds_{fhk__csba}'] = np.array(T.
                block_to_arr_ind[fhk__csba], dtype=np.int64)
            kmn__bgdaz += f'  for i in range(len(arr_list_{fhk__csba})):\n'
            kmn__bgdaz += (
                f'    arr_ind_{fhk__csba} = arr_inds_{fhk__csba}[i]\n')
            if mnp__cxmuc is not None:
                kmn__bgdaz += (
                    f'    if arr_ind_{fhk__csba} not in used_set: continue\n')
            kmn__bgdaz += f"""    ensure_column_unboxed(T, arr_list_{fhk__csba}, i, arr_ind_{fhk__csba})
"""
            kmn__bgdaz += f"""    out_arr_{fhk__csba} = ensure_contig_if_np(arr_list_{fhk__csba}[i][idx])
"""
            kmn__bgdaz += f'    l = len(out_arr_{fhk__csba})\n'
            kmn__bgdaz += (
                f'    out_arr_list_{fhk__csba}[i] = out_arr_{fhk__csba}\n')
        kmn__bgdaz += (
            f'  T2 = set_table_block(T2, out_arr_list_{fhk__csba}, {fhk__csba})\n'
            )
    kmn__bgdaz += f'  T2 = set_table_len(T2, l)\n'
    kmn__bgdaz += f'  return T2\n'
    fsozy__ujw = {}
    exec(kmn__bgdaz, dfxw__ablxn, fsozy__ujw)
    return fsozy__ujw['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    php__dzpj = list(idx.instance_type.meta)
    bbdf__jfpo = tuple(np.array(T.arr_types, dtype=object)[php__dzpj])
    ppx__vey = TableType(bbdf__jfpo)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    fqrt__fjvg = is_overload_true(copy_arrs)
    dfxw__ablxn = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': ppx__vey}
    if not is_overload_none(used_cols):
        zug__fguyf = used_cols.instance_type.meta
        whpa__hfvuw = set(zug__fguyf)
        dfxw__ablxn['kept_cols'] = np.array(zug__fguyf, np.int64)
        lccs__yaohe = True
    else:
        lccs__yaohe = False
    lrja__huhbq = {i: c for i, c in enumerate(php__dzpj)}
    kmn__bgdaz = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    kmn__bgdaz += f'  T2 = init_table(out_table_typ, False)\n'
    kmn__bgdaz += f'  T2 = set_table_len(T2, len(T))\n'
    if lccs__yaohe and len(whpa__hfvuw) == 0:
        kmn__bgdaz += f'  return T2\n'
        fsozy__ujw = {}
        exec(kmn__bgdaz, dfxw__ablxn, fsozy__ujw)
        return fsozy__ujw['table_subset']
    if lccs__yaohe:
        kmn__bgdaz += f'  kept_cols_set = set(kept_cols)\n'
    for typ, fhk__csba in ppx__vey.type_to_blk.items():
        usuqg__qsjx = T.type_to_blk[typ]
        kmn__bgdaz += (
            f'  arr_list_{fhk__csba} = get_table_block(T, {usuqg__qsjx})\n')
        kmn__bgdaz += f"""  out_arr_list_{fhk__csba} = alloc_list_like(arr_list_{fhk__csba}, {len(ppx__vey.block_to_arr_ind[fhk__csba])}, False)
"""
        kvh__ediw = True
        if lccs__yaohe:
            qmbz__psbnw = set(ppx__vey.block_to_arr_ind[fhk__csba])
            arj__urqvo = qmbz__psbnw & whpa__hfvuw
            kvh__ediw = len(arj__urqvo) > 0
        if kvh__ediw:
            dfxw__ablxn[f'out_arr_inds_{fhk__csba}'] = np.array(ppx__vey.
                block_to_arr_ind[fhk__csba], dtype=np.int64)
            kmn__bgdaz += f'  for i in range(len(out_arr_list_{fhk__csba})):\n'
            kmn__bgdaz += (
                f'    out_arr_ind_{fhk__csba} = out_arr_inds_{fhk__csba}[i]\n')
            if lccs__yaohe:
                kmn__bgdaz += (
                    f'    if out_arr_ind_{fhk__csba} not in kept_cols_set: continue\n'
                    )
            cdmh__pod = []
            mbek__xsoqo = []
            for lewsy__ymqtz in ppx__vey.block_to_arr_ind[fhk__csba]:
                eks__lllth = lrja__huhbq[lewsy__ymqtz]
                cdmh__pod.append(eks__lllth)
                qif__wtff = T.block_offsets[eks__lllth]
                mbek__xsoqo.append(qif__wtff)
            dfxw__ablxn[f'in_logical_idx_{fhk__csba}'] = np.array(cdmh__pod,
                dtype=np.int64)
            dfxw__ablxn[f'in_physical_idx_{fhk__csba}'] = np.array(mbek__xsoqo,
                dtype=np.int64)
            kmn__bgdaz += (
                f'    logical_idx_{fhk__csba} = in_logical_idx_{fhk__csba}[i]\n'
                )
            kmn__bgdaz += (
                f'    physical_idx_{fhk__csba} = in_physical_idx_{fhk__csba}[i]\n'
                )
            kmn__bgdaz += f"""    ensure_column_unboxed(T, arr_list_{fhk__csba}, physical_idx_{fhk__csba}, logical_idx_{fhk__csba})
"""
            znyr__pcqba = '.copy()' if fqrt__fjvg else ''
            kmn__bgdaz += f"""    out_arr_list_{fhk__csba}[i] = arr_list_{fhk__csba}[physical_idx_{fhk__csba}]{znyr__pcqba}
"""
        kmn__bgdaz += (
            f'  T2 = set_table_block(T2, out_arr_list_{fhk__csba}, {fhk__csba})\n'
            )
    kmn__bgdaz += f'  return T2\n'
    fsozy__ujw = {}
    exec(kmn__bgdaz, dfxw__ablxn, fsozy__ujw)
    return fsozy__ujw['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    vie__kdd = args[0]
    if equiv_set.has_shape(vie__kdd):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=vie__kdd, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (vie__kdd)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    vie__kdd = args[0]
    if equiv_set.has_shape(vie__kdd):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            vie__kdd)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    kmn__bgdaz = 'def impl(T):\n'
    kmn__bgdaz += f'  T2 = init_table(T, True)\n'
    kmn__bgdaz += f'  l = len(T)\n'
    dfxw__ablxn = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for fhk__csba in T.type_to_blk.values():
        dfxw__ablxn[f'arr_inds_{fhk__csba}'] = np.array(T.block_to_arr_ind[
            fhk__csba], dtype=np.int64)
        kmn__bgdaz += (
            f'  arr_list_{fhk__csba} = get_table_block(T, {fhk__csba})\n')
        kmn__bgdaz += f"""  out_arr_list_{fhk__csba} = alloc_list_like(arr_list_{fhk__csba}, len(arr_list_{fhk__csba}), True)
"""
        kmn__bgdaz += f'  for i in range(len(arr_list_{fhk__csba})):\n'
        kmn__bgdaz += f'    arr_ind_{fhk__csba} = arr_inds_{fhk__csba}[i]\n'
        kmn__bgdaz += f"""    ensure_column_unboxed(T, arr_list_{fhk__csba}, i, arr_ind_{fhk__csba})
"""
        kmn__bgdaz += (
            f'    out_arr_{fhk__csba} = decode_if_dict_array(arr_list_{fhk__csba}[i])\n'
            )
        kmn__bgdaz += (
            f'    out_arr_list_{fhk__csba}[i] = out_arr_{fhk__csba}\n')
        kmn__bgdaz += (
            f'  T2 = set_table_block(T2, out_arr_list_{fhk__csba}, {fhk__csba})\n'
            )
    kmn__bgdaz += f'  T2 = set_table_len(T2, l)\n'
    kmn__bgdaz += f'  return T2\n'
    fsozy__ujw = {}
    exec(kmn__bgdaz, dfxw__ablxn, fsozy__ujw)
    return fsozy__ujw['impl']


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
        auj__qlsc = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        auj__qlsc = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            auj__qlsc.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        mgziy__mufav, vnw__ndd = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = vnw__ndd
        vlucb__ohl = cgutils.unpack_tuple(builder, mgziy__mufav)
        for i, ljemz__zaj in enumerate(vlucb__ohl):
            setattr(table, f'block_{i}', ljemz__zaj)
            context.nrt.incref(builder, types.List(auj__qlsc[i]), ljemz__zaj)
        return table._getvalue()
    table_type = TableType(tuple(auj__qlsc), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen
