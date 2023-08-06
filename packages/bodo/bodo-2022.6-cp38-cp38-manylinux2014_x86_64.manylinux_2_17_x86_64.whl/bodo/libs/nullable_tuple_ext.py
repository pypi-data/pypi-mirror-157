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
        ulxll__bjoz = [('data', fe_type.tuple_typ), ('null_values', fe_type
            .null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, ulxll__bjoz)


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
        oexk__mrw = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        oexk__mrw.data = data_tuple
        oexk__mrw.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return oexk__mrw._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    fnq__sguuf = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, fnq__sguuf.data)
    c.context.nrt.incref(c.builder, typ.null_typ, fnq__sguuf.null_values)
    ufuz__ostqb = c.pyapi.from_native_value(typ.tuple_typ, fnq__sguuf.data,
        c.env_manager)
    ychs__jay = c.pyapi.from_native_value(typ.null_typ, fnq__sguuf.
        null_values, c.env_manager)
    qtgt__bgk = c.context.get_constant(types.int64, len(typ.tuple_typ))
    keqp__jbeo = c.pyapi.list_new(qtgt__bgk)
    with cgutils.for_range(c.builder, qtgt__bgk) as fpbe__lpnmz:
        i = fpbe__lpnmz.index
        glrsy__mxx = c.pyapi.long_from_longlong(i)
        lgmcw__etk = c.pyapi.object_getitem(ychs__jay, glrsy__mxx)
        wheam__qdwf = c.pyapi.to_native_value(types.bool_, lgmcw__etk).value
        with c.builder.if_else(wheam__qdwf) as (tfe__iyh, wnblz__szta):
            with tfe__iyh:
                c.pyapi.list_setitem(keqp__jbeo, i, c.pyapi.make_none())
            with wnblz__szta:
                pedf__leiid = c.pyapi.object_getitem(ufuz__ostqb, glrsy__mxx)
                c.pyapi.list_setitem(keqp__jbeo, i, pedf__leiid)
        c.pyapi.decref(glrsy__mxx)
        c.pyapi.decref(lgmcw__etk)
    clown__fkt = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    mzlp__jja = c.pyapi.call_function_objargs(clown__fkt, (keqp__jbeo,))
    c.pyapi.decref(ufuz__ostqb)
    c.pyapi.decref(ychs__jay)
    c.pyapi.decref(clown__fkt)
    c.pyapi.decref(keqp__jbeo)
    c.context.nrt.decref(c.builder, typ, val)
    return mzlp__jja


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
    oexk__mrw = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (oexk__mrw.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    ntz__twfqy = 'def impl(val1, val2):\n'
    ntz__twfqy += '    data_tup1 = val1._data\n'
    ntz__twfqy += '    null_tup1 = val1._null_values\n'
    ntz__twfqy += '    data_tup2 = val2._data\n'
    ntz__twfqy += '    null_tup2 = val2._null_values\n'
    xfytp__zmq = val1._tuple_typ
    for i in range(len(xfytp__zmq)):
        ntz__twfqy += f'    null1_{i} = null_tup1[{i}]\n'
        ntz__twfqy += f'    null2_{i} = null_tup2[{i}]\n'
        ntz__twfqy += f'    data1_{i} = data_tup1[{i}]\n'
        ntz__twfqy += f'    data2_{i} = data_tup2[{i}]\n'
        ntz__twfqy += f'    if null1_{i} != null2_{i}:\n'
        ntz__twfqy += '        return False\n'
        ntz__twfqy += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        ntz__twfqy += f'        return False\n'
    ntz__twfqy += f'    return True\n'
    mwixu__xyxz = {}
    exec(ntz__twfqy, {}, mwixu__xyxz)
    impl = mwixu__xyxz['impl']
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
    ntz__twfqy = 'def impl(nullable_tup):\n'
    ntz__twfqy += '    data_tup = nullable_tup._data\n'
    ntz__twfqy += '    null_tup = nullable_tup._null_values\n'
    ntz__twfqy += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    ntz__twfqy += '    acc = _PyHASH_XXPRIME_5\n'
    xfytp__zmq = nullable_tup._tuple_typ
    for i in range(len(xfytp__zmq)):
        ntz__twfqy += f'    null_val_{i} = null_tup[{i}]\n'
        ntz__twfqy += f'    null_lane_{i} = hash(null_val_{i})\n'
        ntz__twfqy += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        ntz__twfqy += '        return -1\n'
        ntz__twfqy += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        ntz__twfqy += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        ntz__twfqy += '    acc *= _PyHASH_XXPRIME_1\n'
        ntz__twfqy += f'    if not null_val_{i}:\n'
        ntz__twfqy += f'        lane_{i} = hash(data_tup[{i}])\n'
        ntz__twfqy += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        ntz__twfqy += f'            return -1\n'
        ntz__twfqy += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        ntz__twfqy += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        ntz__twfqy += '        acc *= _PyHASH_XXPRIME_1\n'
    ntz__twfqy += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    ntz__twfqy += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    ntz__twfqy += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    ntz__twfqy += '    return numba.cpython.hashing.process_return(acc)\n'
    mwixu__xyxz = {}
    exec(ntz__twfqy, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, mwixu__xyxz)
    impl = mwixu__xyxz['impl']
    return impl
