"""
Array of intervals corresponding to IntervalArray of Pandas.
Used for IntervalIndex, which is necessary for Series.value_counts() with 'bins'
argument.
"""
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo


class IntervalType(types.Type):

    def __init__(self):
        super(IntervalType, self).__init__('IntervalType()')


class IntervalArrayType(types.ArrayCompatible):

    def __init__(self, arr_type):
        self.arr_type = arr_type
        self.dtype = IntervalType()
        super(IntervalArrayType, self).__init__(name=
            f'IntervalArrayType({arr_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntervalArrayType(self.arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(IntervalArrayType)
class IntervalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hwosp__dobdk = [('left', fe_type.arr_type), ('right', fe_type.arr_type)
            ]
        models.StructModel.__init__(self, dmm, fe_type, hwosp__dobdk)


make_attribute_wrapper(IntervalArrayType, 'left', '_left')
make_attribute_wrapper(IntervalArrayType, 'right', '_right')


@typeof_impl.register(pd.arrays.IntervalArray)
def typeof_interval_array(val, c):
    arr_type = bodo.typeof(val._left)
    return IntervalArrayType(arr_type)


@intrinsic
def init_interval_array(typingctx, left, right=None):
    assert left == right, 'Interval left/right array types should be the same'

    def codegen(context, builder, signature, args):
        aon__rlbit, xwky__vjxrh = args
        xyxkn__fdz = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        xyxkn__fdz.left = aon__rlbit
        xyxkn__fdz.right = xwky__vjxrh
        context.nrt.incref(builder, signature.args[0], aon__rlbit)
        context.nrt.incref(builder, signature.args[1], xwky__vjxrh)
        return xyxkn__fdz._getvalue()
    akvj__wtl = IntervalArrayType(left)
    ipmp__lqvdx = akvj__wtl(left, right)
    return ipmp__lqvdx, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    cxoes__trxw = []
    for esd__njk in args:
        gpqb__whqer = equiv_set.get_shape(esd__njk)
        if gpqb__whqer is not None:
            cxoes__trxw.append(gpqb__whqer[0])
    if len(cxoes__trxw) > 1:
        equiv_set.insert_equiv(*cxoes__trxw)
    left = args[0]
    if equiv_set.has_shape(left):
        return ArrayAnalysis.AnalyzeResult(shape=left, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_libs_interval_arr_ext_init_interval_array
    ) = init_interval_array_equiv


def alias_ext_init_interval_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_interval_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_interval_array


@box(IntervalArrayType)
def box_interval_arr(typ, val, c):
    xyxkn__fdz = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, xyxkn__fdz.left)
    rwfu__xvi = c.pyapi.from_native_value(typ.arr_type, xyxkn__fdz.left, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, xyxkn__fdz.right)
    yjgn__nixb = c.pyapi.from_native_value(typ.arr_type, xyxkn__fdz.right,
        c.env_manager)
    vgy__djzm = c.context.insert_const_string(c.builder.module, 'pandas')
    wbooq__aznh = c.pyapi.import_module_noblock(vgy__djzm)
    wivfe__wiu = c.pyapi.object_getattr_string(wbooq__aznh, 'arrays')
    urcg__cgd = c.pyapi.object_getattr_string(wivfe__wiu, 'IntervalArray')
    zctn__ymjli = c.pyapi.call_method(urcg__cgd, 'from_arrays', (rwfu__xvi,
        yjgn__nixb))
    c.pyapi.decref(rwfu__xvi)
    c.pyapi.decref(yjgn__nixb)
    c.pyapi.decref(wbooq__aznh)
    c.pyapi.decref(wivfe__wiu)
    c.pyapi.decref(urcg__cgd)
    c.context.nrt.decref(c.builder, typ, val)
    return zctn__ymjli


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    rwfu__xvi = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, rwfu__xvi).value
    c.pyapi.decref(rwfu__xvi)
    yjgn__nixb = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, yjgn__nixb).value
    c.pyapi.decref(yjgn__nixb)
    xyxkn__fdz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xyxkn__fdz.left = left
    xyxkn__fdz.right = right
    zrtt__zgl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xyxkn__fdz._getvalue(), is_error=zrtt__zgl)


@overload(len, no_unliteral=True)
def overload_interval_arr_len(A):
    if isinstance(A, IntervalArrayType):
        return lambda A: len(A._left)


@overload_attribute(IntervalArrayType, 'shape')
def overload_interval_arr_shape(A):
    return lambda A: (len(A._left),)


@overload_attribute(IntervalArrayType, 'ndim')
def overload_interval_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntervalArrayType, 'nbytes')
def overload_interval_arr_nbytes(A):
    return lambda A: A._left.nbytes + A._right.nbytes


@overload_method(IntervalArrayType, 'copy', no_unliteral=True)
def overload_interval_arr_copy(A):
    return lambda A: bodo.libs.interval_arr_ext.init_interval_array(A._left
        .copy(), A._right.copy())
