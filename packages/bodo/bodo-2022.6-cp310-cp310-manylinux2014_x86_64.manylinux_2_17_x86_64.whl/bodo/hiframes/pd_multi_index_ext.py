"""Support for MultiIndex type of Pandas
"""
import operator
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from bodo.utils.conversion import ensure_contig_if_np
from bodo.utils.typing import BodoError, check_unsupported_args, dtype_to_array_type, get_val_type_maybe_str_literal, is_overload_none


class MultiIndexType(types.ArrayCompatible):

    def __init__(self, array_types, names_typ=None, name_typ=None):
        names_typ = (types.none,) * len(array_types
            ) if names_typ is None else names_typ
        name_typ = types.none if name_typ is None else name_typ
        self.array_types = array_types
        self.names_typ = names_typ
        self.name_typ = name_typ
        super(MultiIndexType, self).__init__(name=
            'MultiIndexType({}, {}, {})'.format(array_types, names_typ,
            name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return MultiIndexType(self.array_types, self.names_typ, self.name_typ)

    @property
    def nlevels(self):
        return len(self.array_types)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(MultiIndexType)
class MultiIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        knwfy__siggx = [('data', types.Tuple(fe_type.array_types)), (
            'names', types.Tuple(fe_type.names_typ)), ('name', fe_type.
            name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, knwfy__siggx)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[wwfkh__uhw].values) for
        wwfkh__uhw in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (pcr__goeue) for pcr__goeue in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    oorz__sfi = c.context.insert_const_string(c.builder.module, 'pandas')
    zyy__njgvp = c.pyapi.import_module_noblock(oorz__sfi)
    qgcvu__wkdx = c.pyapi.object_getattr_string(zyy__njgvp, 'MultiIndex')
    baxp__tbxv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        baxp__tbxv.data)
    ksam__pcqqa = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        baxp__tbxv.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), baxp__tbxv.
        names)
    rxjr__ytf = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        baxp__tbxv.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, baxp__tbxv.name)
    afsvf__fovoe = c.pyapi.from_native_value(typ.name_typ, baxp__tbxv.name,
        c.env_manager)
    esedo__gmb = c.pyapi.borrow_none()
    voff__cat = c.pyapi.call_method(qgcvu__wkdx, 'from_arrays', (
        ksam__pcqqa, esedo__gmb, rxjr__ytf))
    c.pyapi.object_setattr_string(voff__cat, 'name', afsvf__fovoe)
    c.pyapi.decref(ksam__pcqqa)
    c.pyapi.decref(rxjr__ytf)
    c.pyapi.decref(afsvf__fovoe)
    c.pyapi.decref(zyy__njgvp)
    c.pyapi.decref(qgcvu__wkdx)
    c.context.nrt.decref(c.builder, typ, val)
    return voff__cat


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    ejlk__pxptb = []
    fiyk__ayxev = []
    for wwfkh__uhw in range(typ.nlevels):
        xjham__sukyl = c.pyapi.unserialize(c.pyapi.serialize_object(wwfkh__uhw)
            )
        yvd__kglg = c.pyapi.call_method(val, 'get_level_values', (
            xjham__sukyl,))
        whz__icmkv = c.pyapi.object_getattr_string(yvd__kglg, 'values')
        c.pyapi.decref(yvd__kglg)
        c.pyapi.decref(xjham__sukyl)
        qplzc__tewn = c.pyapi.to_native_value(typ.array_types[wwfkh__uhw],
            whz__icmkv).value
        ejlk__pxptb.append(qplzc__tewn)
        fiyk__ayxev.append(whz__icmkv)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, ejlk__pxptb)
    else:
        data = cgutils.pack_struct(c.builder, ejlk__pxptb)
    rxjr__ytf = c.pyapi.object_getattr_string(val, 'names')
    pjt__mkjf = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    pow__gltt = c.pyapi.call_function_objargs(pjt__mkjf, (rxjr__ytf,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), pow__gltt
        ).value
    afsvf__fovoe = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, afsvf__fovoe).value
    baxp__tbxv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    baxp__tbxv.data = data
    baxp__tbxv.names = names
    baxp__tbxv.name = name
    for whz__icmkv in fiyk__ayxev:
        c.pyapi.decref(whz__icmkv)
    c.pyapi.decref(rxjr__ytf)
    c.pyapi.decref(pjt__mkjf)
    c.pyapi.decref(pow__gltt)
    c.pyapi.decref(afsvf__fovoe)
    return NativeValue(baxp__tbxv._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    kprk__lbge = 'pandas.MultiIndex.from_product'
    agea__vdbax = dict(sortorder=sortorder)
    sol__knxfh = dict(sortorder=None)
    check_unsupported_args(kprk__lbge, agea__vdbax, sol__knxfh,
        package_name='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{kprk__lbge}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{kprk__lbge}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{kprk__lbge}: iterables and names must be of the same length.')


def from_product(iterable, sortorder=None, names=None):
    pass


@overload(from_product)
def from_product_overload(iterables, sortorder=None, names=None):
    from_product_error_checking(iterables, sortorder, names)
    array_types = tuple(dtype_to_array_type(iterable.dtype) for iterable in
        iterables)
    if is_overload_none(names):
        names_typ = tuple([types.none] * len(iterables))
    else:
        names_typ = names.types
    qdqya__skyep = MultiIndexType(array_types, names_typ)
    iybk__jdf = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, iybk__jdf, qdqya__skyep)
    gzhaq__ekv = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{iybk__jdf}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    prb__xyx = {}
    exec(gzhaq__ekv, globals(), prb__xyx)
    dcef__tjkm = prb__xyx['impl']
    return dcef__tjkm


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        qsmoo__oqe, audyn__vxrqv, vqlo__csrqo = args
        jpjtd__tzx = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        jpjtd__tzx.data = qsmoo__oqe
        jpjtd__tzx.names = audyn__vxrqv
        jpjtd__tzx.name = vqlo__csrqo
        context.nrt.incref(builder, signature.args[0], qsmoo__oqe)
        context.nrt.incref(builder, signature.args[1], audyn__vxrqv)
        context.nrt.incref(builder, signature.args[2], vqlo__csrqo)
        return jpjtd__tzx._getvalue()
    pwbfm__pzxr = MultiIndexType(data.types, names.types, name)
    return pwbfm__pzxr(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        kahc__wjlrb = len(I.array_types)
        gzhaq__ekv = 'def impl(I, ind):\n'
        gzhaq__ekv += '  data = I._data\n'
        gzhaq__ekv += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{wwfkh__uhw}][ind])' for wwfkh__uhw in
            range(kahc__wjlrb))))
        prb__xyx = {}
        exec(gzhaq__ekv, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, prb__xyx)
        dcef__tjkm = prb__xyx['impl']
        return dcef__tjkm


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    ycqpw__cqv, pqjwh__wiczb = sig.args
    if ycqpw__cqv != pqjwh__wiczb:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
