"""
Implements array kernels that are specific to BodoSQL
"""
import numba
import numpy as np
from numba.core import types
from numba.extending import overload
import bodo
from bodo.utils.typing import raise_bodo_error


def gen_vectorized(arg_names, arg_types, propogate_null, scalar_text,
    constructor_text, arg_string=None):
    qgu__czgkk = [bodo.utils.utils.is_array_typ(qgdds__mvifx, True) for
        qgdds__mvifx in arg_types]
    ilqa__xftn = not any(qgu__czgkk)
    otuh__kdcf = any([propogate_null[i] for i in range(len(arg_types)) if 
        arg_types[i] == bodo.none])
    ans__mdt = scalar_text.splitlines()[0]
    sqo__kow = len(ans__mdt) - len(ans__mdt.lstrip())
    if arg_string == None:
        arg_string = ', '.join(arg_names)
    zdmop__sis = f'def impl({arg_string}):\n'
    if ilqa__xftn:
        if otuh__kdcf:
            zdmop__sis += '   return None'
        else:
            for i in range(len(arg_names)):
                zdmop__sis += f'   arg{i} = {arg_names[i]}\n'
            for uszh__heg in scalar_text.splitlines():
                zdmop__sis += ' ' * 3 + uszh__heg[sqo__kow:].replace('res[i] ='
                    , 'answer =') + '\n'
            zdmop__sis += '   return answer'
    else:
        xwee__pus = False
        for i in range(len(arg_names)):
            if qgu__czgkk[i]:
                if not xwee__pus:
                    giz__emqlx = f'len({arg_names[i]})'
                    xwee__pus = True
                if not bodo.utils.utils.is_array_typ(arg_types[i], False):
                    zdmop__sis += f"""   {arg_names[i]} = bodo.hiframes.pd_series_ext.get_series_data({arg_names[i]})
"""
        zdmop__sis += f'   n = {giz__emqlx}\n'
        zdmop__sis += f'   res = {constructor_text}\n'
        zdmop__sis += '   for i in range(n):\n'
        if otuh__kdcf:
            zdmop__sis += f'      bodo.libs.array_kernels.setna(res, i)\n'
        else:
            for i in range(len(arg_names)):
                if qgu__czgkk[i]:
                    if propogate_null[i]:
                        zdmop__sis += (
                            f'      if bodo.libs.array_kernels.isna({arg_names[i]}, i):\n'
                            )
                        zdmop__sis += (
                            '         bodo.libs.array_kernels.setna(res, i)\n')
                        zdmop__sis += '         continue\n'
            for i in range(len(arg_names)):
                if qgu__czgkk[i]:
                    zdmop__sis += f'      arg{i} = {arg_names[i]}[i]\n'
                else:
                    zdmop__sis += f'      arg{i} = {arg_names[i]}\n'
            for uszh__heg in scalar_text.splitlines():
                zdmop__sis += ' ' * 6 + uszh__heg[sqo__kow:] + '\n'
        zdmop__sis += (
            '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, n, 1), None)'
            )
    keu__utbp = {}
    exec(zdmop__sis, {'bodo': bodo, 'numba': numba, 'np': np}, keu__utbp)
    impl = keu__utbp['impl']
    return impl


def unopt_argument(func_name, arg_names, i):
    rlfhj__gzh = [(arg_names[htt__ocw] if htt__ocw != i else 'None') for
        htt__ocw in range(len(arg_names))]
    kya__dnzxt = [(arg_names[htt__ocw] if htt__ocw != i else
        f'bodo.utils.indexing.unoptional({arg_names[htt__ocw]})') for
        htt__ocw in range(len(arg_names))]
    zdmop__sis = f"def impl({', '.join(arg_names)}):\n"
    zdmop__sis += f'   if {arg_names[i]} is None:\n'
    zdmop__sis += f"      return {func_name}({', '.join(rlfhj__gzh)})\n"
    zdmop__sis += f'   else:\n'
    zdmop__sis += f"      return {func_name}({', '.join(kya__dnzxt)})"
    keu__utbp = {}
    exec(zdmop__sis, {'bodo': bodo, 'numba': numba}, keu__utbp)
    impl = keu__utbp['impl']
    return impl


def lpad(arr, length, padstr):
    return


def rpad(arr, length, padstr):
    return


def lpad_util(arr, length, padstr):
    return


def rpad_util(arr, length, padstr):
    return


@overload(lpad)
def overload_lpad(arr, length, padstr):
    args = [arr, length, padstr]
    for i in range(3):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.lpad', [
                'arr', 'length', 'padstr'], i)

    def impl(arr, length, padstr):
        return lpad_util(arr, length, padstr)
    return impl


@overload(rpad)
def overload_rpad(arr, length, padstr):
    args = [arr, length, padstr]
    for i in range(3):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.rpad', [
                'arr', 'length', 'padstr'], i)

    def impl(arr, length, padstr):
        return rpad_util(arr, length, padstr)
    return impl


def create_lpad_rpad_util_overload(func_name):

    def overload_lpad_rpad_util(arr, length, pad_string):
        if arr not in (types.none, types.unicode_type) and not (bodo.utils.
            utils.is_array_typ(arr, True) and arr.dtype == types.unicode_type):
            raise_bodo_error(
                f'{func_name} can only be applied to strings, string columns, or null'
                )
        if length not in (types.none, *types.integer_domain) and not (bodo.
            utils.utils.is_array_typ(length, True) and length.dtype in
            types.integer_domain):
            raise_bodo_error(
                f'{func_name} length argument must be an integer, integer column, or null'
                )
        if pad_string not in (types.none, types.unicode_type) and not (bodo
            .utils.utils.is_array_typ(pad_string, True) and pad_string.
            dtype == types.unicode_type):
            raise_bodo_error(
                f'{func_name} {func_name.lower()}_string argument must be a string, string column, or null'
                )
        if func_name == 'LPAD':
            rpqw__fqqq = f'(arg2 * quotient) + arg2[:remainder] + arg0'
        elif func_name == 'RPAD':
            rpqw__fqqq = f'arg0 + (arg2 * quotient) + arg2[:remainder]'
        arg_names = ['arr', 'length', 'pad_string']
        arg_types = [arr, length, pad_string]
        propogate_null = [True] * 3
        scalar_text = f"""            if arg1 <= 0:
                res[i] =  ''
            elif len(arg2) == 0:
                res[i] = arg0
            elif len(arg0) >= arg1:
                res[i] = arg0[:arg1]
            else:
                quotient = (arg1 - len(arg0)) // len(arg2)
                remainder = (arg1 - len(arg0)) % len(arg2)
                res[i] = {rpqw__fqqq}"""
        constructor_text = (
            'bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)')
        return gen_vectorized(arg_names, arg_types, propogate_null,
            scalar_text, constructor_text)
    return overload_lpad_rpad_util


def _install_lpad_rpad_overload():
    for rpues__okd, func_name in zip((lpad_util, rpad_util), ('LPAD', 'RPAD')):
        zbp__ovvh = create_lpad_rpad_util_overload(func_name)
        overload(rpues__okd)(zbp__ovvh)


_install_lpad_rpad_overload()
