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
        srtp__vqu = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, srtp__vqu)


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
        bxa__uyooe, mtyhe__ftf = args
        fzp__qkf = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        fzp__qkf.left = bxa__uyooe
        fzp__qkf.right = mtyhe__ftf
        context.nrt.incref(builder, signature.args[0], bxa__uyooe)
        context.nrt.incref(builder, signature.args[1], mtyhe__ftf)
        return fzp__qkf._getvalue()
    hvg__nxkbh = IntervalArrayType(left)
    mmi__zqh = hvg__nxkbh(left, right)
    return mmi__zqh, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    urb__exe = []
    for qwgd__ara in args:
        hbav__vgoye = equiv_set.get_shape(qwgd__ara)
        if hbav__vgoye is not None:
            urb__exe.append(hbav__vgoye[0])
    if len(urb__exe) > 1:
        equiv_set.insert_equiv(*urb__exe)
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
    fzp__qkf = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, fzp__qkf.left)
    kmylx__htq = c.pyapi.from_native_value(typ.arr_type, fzp__qkf.left, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, fzp__qkf.right)
    krx__cxuoi = c.pyapi.from_native_value(typ.arr_type, fzp__qkf.right, c.
        env_manager)
    pnybx__wyq = c.context.insert_const_string(c.builder.module, 'pandas')
    nthv__qfok = c.pyapi.import_module_noblock(pnybx__wyq)
    gdrq__kbsf = c.pyapi.object_getattr_string(nthv__qfok, 'arrays')
    dphqx__oklcv = c.pyapi.object_getattr_string(gdrq__kbsf, 'IntervalArray')
    yvts__hxx = c.pyapi.call_method(dphqx__oklcv, 'from_arrays', (
        kmylx__htq, krx__cxuoi))
    c.pyapi.decref(kmylx__htq)
    c.pyapi.decref(krx__cxuoi)
    c.pyapi.decref(nthv__qfok)
    c.pyapi.decref(gdrq__kbsf)
    c.pyapi.decref(dphqx__oklcv)
    c.context.nrt.decref(c.builder, typ, val)
    return yvts__hxx


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    kmylx__htq = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, kmylx__htq).value
    c.pyapi.decref(kmylx__htq)
    krx__cxuoi = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, krx__cxuoi).value
    c.pyapi.decref(krx__cxuoi)
    fzp__qkf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    fzp__qkf.left = left
    fzp__qkf.right = right
    xhjph__bcstk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(fzp__qkf._getvalue(), is_error=xhjph__bcstk)


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
