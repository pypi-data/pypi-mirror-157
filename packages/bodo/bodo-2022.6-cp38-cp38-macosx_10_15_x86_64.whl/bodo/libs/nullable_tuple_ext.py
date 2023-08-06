"""
Wrapper class for Tuples that supports tracking null entries.
This is primarily used for maintaining null information for
Series values used in df.apply
"""
import operator
import numba
from numba.core import cgutils, types
from numba.extending import box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model


class NullableTupleType(types.IterableType):

    def __init__(self, tuple_typ, null_typ):
        self._tuple_typ = tuple_typ
        self._null_typ = null_typ
        super(NullableTupleType, self).__init__(name=
            f'NullableTupleType({tuple_typ}, {null_typ})')

    @property
    def tuple_typ(self):
        return self._tuple_typ

    @property
    def null_typ(self):
        return self._null_typ

    def __getitem__(self, i):
        return self._tuple_typ[i]

    @property
    def key(self):
        return self._tuple_typ

    @property
    def dtype(self):
        return self.tuple_typ.dtype

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def iterator_type(self):
        return self.tuple_typ.iterator_type

    def __len__(self):
        return len(self.tuple_typ)


@register_model(NullableTupleType)
class NullableTupleModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rciek__xjquo = [('data', fe_type.tuple_typ), ('null_values',
            fe_type.null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, rciek__xjquo)


make_attribute_wrapper(NullableTupleType, 'data', '_data')
make_attribute_wrapper(NullableTupleType, 'null_values', '_null_values')


@intrinsic
def build_nullable_tuple(typingctx, data_tuple, null_values):
    assert isinstance(data_tuple, types.BaseTuple
        ), "build_nullable_tuple 'data_tuple' argument must be a tuple"
    assert isinstance(null_values, types.BaseTuple
        ), "build_nullable_tuple 'null_values' argument must be a tuple"
    data_tuple = types.unliteral(data_tuple)
    null_values = types.unliteral(null_values)

    def codegen(context, builder, signature, args):
        data_tuple, null_values = args
        thkmp__wsamq = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        thkmp__wsamq.data = data_tuple
        thkmp__wsamq.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return thkmp__wsamq._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    zbui__xtmk = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, zbui__xtmk.data)
    c.context.nrt.incref(c.builder, typ.null_typ, zbui__xtmk.null_values)
    soe__ozl = c.pyapi.from_native_value(typ.tuple_typ, zbui__xtmk.data, c.
        env_manager)
    bngk__omy = c.pyapi.from_native_value(typ.null_typ, zbui__xtmk.
        null_values, c.env_manager)
    pvpln__mnfj = c.context.get_constant(types.int64, len(typ.tuple_typ))
    hcp__axp = c.pyapi.list_new(pvpln__mnfj)
    with cgutils.for_range(c.builder, pvpln__mnfj) as fvkt__mhmme:
        i = fvkt__mhmme.index
        kue__ckvy = c.pyapi.long_from_longlong(i)
        vkpw__sufxv = c.pyapi.object_getitem(bngk__omy, kue__ckvy)
        rxuwe__bzx = c.pyapi.to_native_value(types.bool_, vkpw__sufxv).value
        with c.builder.if_else(rxuwe__bzx) as (lwxw__kpcf, bhau__zamd):
            with lwxw__kpcf:
                c.pyapi.list_setitem(hcp__axp, i, c.pyapi.make_none())
            with bhau__zamd:
                puvia__vjke = c.pyapi.object_getitem(soe__ozl, kue__ckvy)
                c.pyapi.list_setitem(hcp__axp, i, puvia__vjke)
        c.pyapi.decref(kue__ckvy)
        c.pyapi.decref(vkpw__sufxv)
    krny__qcbz = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    wzje__cul = c.pyapi.call_function_objargs(krny__qcbz, (hcp__axp,))
    c.pyapi.decref(soe__ozl)
    c.pyapi.decref(bngk__omy)
    c.pyapi.decref(krny__qcbz)
    c.pyapi.decref(hcp__axp)
    c.context.nrt.decref(c.builder, typ, val)
    return wzje__cul


@overload(operator.getitem)
def overload_getitem(A, idx):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A, idx: A._data[idx]


@overload(len)
def overload_len(A):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A: len(A._data)


@lower_builtin('getiter', NullableTupleType)
def nullable_tuple_getiter(context, builder, sig, args):
    thkmp__wsamq = cgutils.create_struct_proxy(sig.args[0])(context,
        builder, value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (thkmp__wsamq.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    vkqnn__ujmuz = 'def impl(val1, val2):\n'
    vkqnn__ujmuz += '    data_tup1 = val1._data\n'
    vkqnn__ujmuz += '    null_tup1 = val1._null_values\n'
    vkqnn__ujmuz += '    data_tup2 = val2._data\n'
    vkqnn__ujmuz += '    null_tup2 = val2._null_values\n'
    usmkx__lpzd = val1._tuple_typ
    for i in range(len(usmkx__lpzd)):
        vkqnn__ujmuz += f'    null1_{i} = null_tup1[{i}]\n'
        vkqnn__ujmuz += f'    null2_{i} = null_tup2[{i}]\n'
        vkqnn__ujmuz += f'    data1_{i} = data_tup1[{i}]\n'
        vkqnn__ujmuz += f'    data2_{i} = data_tup2[{i}]\n'
        vkqnn__ujmuz += f'    if null1_{i} != null2_{i}:\n'
        vkqnn__ujmuz += '        return False\n'
        vkqnn__ujmuz += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        vkqnn__ujmuz += f'        return False\n'
    vkqnn__ujmuz += f'    return True\n'
    emln__ygi = {}
    exec(vkqnn__ujmuz, {}, emln__ygi)
    impl = emln__ygi['impl']
    return impl


@overload_method(NullableTupleType, '__hash__')
def nullable_tuple_hash(val):

    def impl(val):
        return _nullable_tuple_hash(val)
    return impl


_PyHASH_XXPRIME_1 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_2 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_5 = numba.cpython.hashing._PyHASH_XXPRIME_1


@numba.generated_jit(nopython=True)
def _nullable_tuple_hash(nullable_tup):
    vkqnn__ujmuz = 'def impl(nullable_tup):\n'
    vkqnn__ujmuz += '    data_tup = nullable_tup._data\n'
    vkqnn__ujmuz += '    null_tup = nullable_tup._null_values\n'
    vkqnn__ujmuz += (
        '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n')
    vkqnn__ujmuz += '    acc = _PyHASH_XXPRIME_5\n'
    usmkx__lpzd = nullable_tup._tuple_typ
    for i in range(len(usmkx__lpzd)):
        vkqnn__ujmuz += f'    null_val_{i} = null_tup[{i}]\n'
        vkqnn__ujmuz += f'    null_lane_{i} = hash(null_val_{i})\n'
        vkqnn__ujmuz += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        vkqnn__ujmuz += '        return -1\n'
        vkqnn__ujmuz += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        vkqnn__ujmuz += (
            '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        vkqnn__ujmuz += '    acc *= _PyHASH_XXPRIME_1\n'
        vkqnn__ujmuz += f'    if not null_val_{i}:\n'
        vkqnn__ujmuz += f'        lane_{i} = hash(data_tup[{i}])\n'
        vkqnn__ujmuz += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        vkqnn__ujmuz += f'            return -1\n'
        vkqnn__ujmuz += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        vkqnn__ujmuz += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        vkqnn__ujmuz += '        acc *= _PyHASH_XXPRIME_1\n'
    vkqnn__ujmuz += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    vkqnn__ujmuz += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    vkqnn__ujmuz += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    vkqnn__ujmuz += '    return numba.cpython.hashing.process_return(acc)\n'
    emln__ygi = {}
    exec(vkqnn__ujmuz, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, emln__ygi)
    impl = emln__ygi['impl']
    return impl
