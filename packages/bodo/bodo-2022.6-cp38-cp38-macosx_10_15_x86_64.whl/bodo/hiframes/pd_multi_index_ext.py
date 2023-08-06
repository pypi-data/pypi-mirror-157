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
        ulvx__yfe = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, ulvx__yfe)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[folc__vcvky].values) for
        folc__vcvky in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (hwnw__mfvq) for hwnw__mfvq in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    ckka__blp = c.context.insert_const_string(c.builder.module, 'pandas')
    kqmp__ybgxp = c.pyapi.import_module_noblock(ckka__blp)
    ild__romo = c.pyapi.object_getattr_string(kqmp__ybgxp, 'MultiIndex')
    rbd__ucp = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types), rbd__ucp.data
        )
    dwl__srxi = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        rbd__ucp.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), rbd__ucp.names)
    txul__owy = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        rbd__ucp.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, rbd__ucp.name)
    xzlf__aug = c.pyapi.from_native_value(typ.name_typ, rbd__ucp.name, c.
        env_manager)
    vvd__ahgf = c.pyapi.borrow_none()
    lyjau__haad = c.pyapi.call_method(ild__romo, 'from_arrays', (dwl__srxi,
        vvd__ahgf, txul__owy))
    c.pyapi.object_setattr_string(lyjau__haad, 'name', xzlf__aug)
    c.pyapi.decref(dwl__srxi)
    c.pyapi.decref(txul__owy)
    c.pyapi.decref(xzlf__aug)
    c.pyapi.decref(kqmp__ybgxp)
    c.pyapi.decref(ild__romo)
    c.context.nrt.decref(c.builder, typ, val)
    return lyjau__haad


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    cfqa__reqr = []
    oky__osb = []
    for folc__vcvky in range(typ.nlevels):
        amf__krmm = c.pyapi.unserialize(c.pyapi.serialize_object(folc__vcvky))
        dmy__mle = c.pyapi.call_method(val, 'get_level_values', (amf__krmm,))
        emmey__geh = c.pyapi.object_getattr_string(dmy__mle, 'values')
        c.pyapi.decref(dmy__mle)
        c.pyapi.decref(amf__krmm)
        tdz__ygqu = c.pyapi.to_native_value(typ.array_types[folc__vcvky],
            emmey__geh).value
        cfqa__reqr.append(tdz__ygqu)
        oky__osb.append(emmey__geh)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, cfqa__reqr)
    else:
        data = cgutils.pack_struct(c.builder, cfqa__reqr)
    txul__owy = c.pyapi.object_getattr_string(val, 'names')
    kvzt__ubw = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    snkc__fol = c.pyapi.call_function_objargs(kvzt__ubw, (txul__owy,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), snkc__fol
        ).value
    xzlf__aug = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, xzlf__aug).value
    rbd__ucp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rbd__ucp.data = data
    rbd__ucp.names = names
    rbd__ucp.name = name
    for emmey__geh in oky__osb:
        c.pyapi.decref(emmey__geh)
    c.pyapi.decref(txul__owy)
    c.pyapi.decref(kvzt__ubw)
    c.pyapi.decref(snkc__fol)
    c.pyapi.decref(xzlf__aug)
    return NativeValue(rbd__ucp._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    vuie__rpa = 'pandas.MultiIndex.from_product'
    rtwrq__aiafi = dict(sortorder=sortorder)
    uue__srnna = dict(sortorder=None)
    check_unsupported_args(vuie__rpa, rtwrq__aiafi, uue__srnna,
        package_name='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{vuie__rpa}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{vuie__rpa}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{vuie__rpa}: iterables and names must be of the same length.')


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
    bbqmz__wwrt = MultiIndexType(array_types, names_typ)
    pyjz__wqgja = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, pyjz__wqgja, bbqmz__wwrt)
    zogd__kipqe = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{pyjz__wqgja}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    buhql__ulzw = {}
    exec(zogd__kipqe, globals(), buhql__ulzw)
    dhvps__htrg = buhql__ulzw['impl']
    return dhvps__htrg


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        mnc__slio, rsao__mbhxx, inncd__xlur = args
        drxhk__yui = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        drxhk__yui.data = mnc__slio
        drxhk__yui.names = rsao__mbhxx
        drxhk__yui.name = inncd__xlur
        context.nrt.incref(builder, signature.args[0], mnc__slio)
        context.nrt.incref(builder, signature.args[1], rsao__mbhxx)
        context.nrt.incref(builder, signature.args[2], inncd__xlur)
        return drxhk__yui._getvalue()
    mvvlh__odg = MultiIndexType(data.types, names.types, name)
    return mvvlh__odg(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        xxypp__udbp = len(I.array_types)
        zogd__kipqe = 'def impl(I, ind):\n'
        zogd__kipqe += '  data = I._data\n'
        zogd__kipqe += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{folc__vcvky}][ind])' for
            folc__vcvky in range(xxypp__udbp))))
        buhql__ulzw = {}
        exec(zogd__kipqe, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, buhql__ulzw)
        dhvps__htrg = buhql__ulzw['impl']
        return dhvps__htrg


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    fkm__ovfwa, pik__upibg = sig.args
    if fkm__ovfwa != pik__upibg:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
