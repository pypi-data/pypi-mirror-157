"""
Support for Series.str methods
"""
import operator
import re
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import StringIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.split_impl import get_split_view_data_ptr, get_split_view_index, string_array_split_view_type
from bodo.libs.array import get_search_regex
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.str_arr_ext import get_utf8_size, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import str_findall_count
from bodo.utils.typing import BodoError, create_unsupported_overload, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_str_len, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, is_str_arr_type, raise_bodo_error


class SeriesStrMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        tmra__axkh = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(tmra__axkh)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rohw__ndl = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, rohw__ndl)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        aljhp__dethl, = args
        hnbvg__shjs = signature.return_type
        ndnt__lwq = cgutils.create_struct_proxy(hnbvg__shjs)(context, builder)
        ndnt__lwq.obj = aljhp__dethl
        context.nrt.incref(builder, signature.args[0], aljhp__dethl)
        return ndnt__lwq._getvalue()
    return SeriesStrMethodType(obj)(obj), codegen


def str_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.UnicodeType) and not is_overload_constant_str(
        arg):
        raise_bodo_error(
            "Series.str.{}(): parameter '{}' expected a string object, not {}"
            .format(func_name, arg_name, arg))


def int_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.Integer) and not is_overload_constant_int(arg
        ):
        raise BodoError(
            "Series.str.{}(): parameter '{}' expected an int object, not {}"
            .format(func_name, arg_name, arg))


def not_supported_arg_check(func_name, arg_name, arg, defval):
    if arg_name == 'na':
        if not isinstance(arg, types.Omitted) and (not isinstance(arg,
            float) or not np.isnan(arg)):
            raise BodoError(
                "Series.str.{}(): parameter '{}' is not supported, default: np.nan"
                .format(func_name, arg_name))
    elif not isinstance(arg, types.Omitted) and arg != defval:
        raise BodoError(
            "Series.str.{}(): parameter '{}' is not supported, default: {}"
            .format(func_name, arg_name, defval))


def common_validate_padding(func_name, width, fillchar):
    if is_overload_constant_str(fillchar):
        if get_overload_const_str_len(fillchar) != 1:
            raise BodoError(
                'Series.str.{}(): fillchar must be a character, not str'.
                format(func_name))
    elif not isinstance(fillchar, types.UnicodeType):
        raise BodoError('Series.str.{}(): fillchar must be a character, not {}'
            .format(func_name, fillchar))
    int_arg_check(func_name, 'width', width)


@overload_attribute(SeriesType, 'str')
def overload_series_str(S):
    if not (is_str_arr_type(S.data) or S.data ==
        string_array_split_view_type or isinstance(S.data, ArrayItemArrayType)
        ):
        raise_bodo_error(
            'Series.str: input should be a series of string or arrays')
    return lambda S: bodo.hiframes.series_str_impl.init_series_str_method(S)


@overload_method(SeriesStrMethodType, 'len', inline='always', no_unliteral=True
    )
def overload_str_method_len(S_str):
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_len_dict_impl(S_str):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_len(uprfc__zmt)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_len_dict_impl

    def impl(S_str):
        S = S_str._obj
        uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(uprfc__zmt, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return impl


@overload_method(SeriesStrMethodType, 'split', inline='always',
    no_unliteral=True)
def overload_str_method_split(S_str, pat=None, n=-1, expand=False):
    if not is_overload_none(pat):
        str_arg_check('split', 'pat', pat)
    int_arg_check('split', 'n', n)
    not_supported_arg_check('split', 'expand', expand, False)
    if is_overload_constant_str(pat) and len(get_overload_const_str(pat)
        ) == 1 and get_overload_const_str(pat).isascii(
        ) and is_overload_constant_int(n) and get_overload_const_int(n
        ) == -1 and S_str.stype.data == string_array_type:

        def _str_split_view_impl(S_str, pat=None, n=-1, expand=False):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(uprfc__zmt,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(uprfc__zmt, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    fspx__xuwoe = S_str.stype.data
    if (fspx__xuwoe != string_array_split_view_type and not is_str_arr_type
        (fspx__xuwoe)) and not isinstance(fspx__xuwoe, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(fspx__xuwoe, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(uprfc__zmt, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_get_array_impl
    if fspx__xuwoe == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(uprfc__zmt)
            icqus__juomj = 0
            for qqiu__aylz in numba.parfors.parfor.internal_prange(n):
                gjn__axbi, gjn__axbi, kibpc__bkgk = get_split_view_index(
                    uprfc__zmt, qqiu__aylz, i)
                icqus__juomj += kibpc__bkgk
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, icqus__juomj)
            for xxvh__yyb in numba.parfors.parfor.internal_prange(n):
                zkb__xdo, hcwk__zcmep, kibpc__bkgk = get_split_view_index(
                    uprfc__zmt, xxvh__yyb, i)
                if zkb__xdo == 0:
                    bodo.libs.array_kernels.setna(out_arr, xxvh__yyb)
                    ymsy__vdo = get_split_view_data_ptr(uprfc__zmt, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr, xxvh__yyb
                        )
                    ymsy__vdo = get_split_view_data_ptr(uprfc__zmt, hcwk__zcmep
                        )
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    xxvh__yyb, ymsy__vdo, kibpc__bkgk)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_get_split_impl
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_get_dict_impl(S_str, i):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_get(uprfc__zmt, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_get_dict_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(uprfc__zmt)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for xxvh__yyb in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(uprfc__zmt, xxvh__yyb) or not len(
                uprfc__zmt[xxvh__yyb]) > i >= -len(uprfc__zmt[xxvh__yyb]):
                out_arr[xxvh__yyb] = ''
                bodo.libs.array_kernels.setna(out_arr, xxvh__yyb)
            else:
                out_arr[xxvh__yyb] = uprfc__zmt[xxvh__yyb][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    fspx__xuwoe = S_str.stype.data
    if (fspx__xuwoe != string_array_split_view_type and fspx__xuwoe !=
        ArrayItemArrayType(string_array_type) and not is_str_arr_type(
        fspx__xuwoe)):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(anxwf__hed)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for xxvh__yyb in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(anxwf__hed, xxvh__yyb):
                out_arr[xxvh__yyb] = ''
                bodo.libs.array_kernels.setna(out_arr, xxvh__yyb)
            else:
                eycxg__eba = anxwf__hed[xxvh__yyb]
                out_arr[xxvh__yyb] = sep.join(eycxg__eba)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return impl


@overload_method(SeriesStrMethodType, 'replace', inline='always',
    no_unliteral=True)
def overload_str_method_replace(S_str, pat, repl, n=-1, case=None, flags=0,
    regex=True):
    not_supported_arg_check('replace', 'n', n, -1)
    not_supported_arg_check('replace', 'case', case, None)
    str_arg_check('replace', 'pat', pat)
    str_arg_check('replace', 'repl', repl)
    int_arg_check('replace', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_replace_dict_impl(S_str, pat, repl, n=-1, case=None, flags
            =0, regex=True):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_replace(uprfc__zmt, pat,
                repl, flags, regex)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_replace_dict_impl
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            cjjcx__cszn = re.compile(pat, flags)
            smc__lfp = len(uprfc__zmt)
            out_arr = pre_alloc_string_array(smc__lfp, -1)
            for xxvh__yyb in numba.parfors.parfor.internal_prange(smc__lfp):
                if bodo.libs.array_kernels.isna(uprfc__zmt, xxvh__yyb):
                    out_arr[xxvh__yyb] = ''
                    bodo.libs.array_kernels.setna(out_arr, xxvh__yyb)
                    continue
                out_arr[xxvh__yyb] = cjjcx__cszn.sub(repl, uprfc__zmt[
                    xxvh__yyb])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        smc__lfp = len(uprfc__zmt)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(smc__lfp, -1)
        for xxvh__yyb in numba.parfors.parfor.internal_prange(smc__lfp):
            if bodo.libs.array_kernels.isna(uprfc__zmt, xxvh__yyb):
                out_arr[xxvh__yyb] = ''
                bodo.libs.array_kernels.setna(out_arr, xxvh__yyb)
                continue
            out_arr[xxvh__yyb] = uprfc__zmt[xxvh__yyb].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return _str_replace_noregex_impl


@numba.njit
def series_contains_regex(S, pat, case, flags, na, regex):
    with numba.objmode(out_arr=bodo.boolean_array):
        out_arr = S.array._str_contains(pat, case, flags, na, regex)
    return out_arr


def is_regex_unsupported(pat):
    mkfdm__pxhh = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(yaag__kffc in pat) for yaag__kffc in mkfdm__pxhh])
    else:
        return True


@overload_method(SeriesStrMethodType, 'contains', no_unliteral=True)
def overload_str_method_contains(S_str, pat, case=True, flags=0, na=np.nan,
    regex=True):
    not_supported_arg_check('contains', 'na', na, np.nan)
    str_arg_check('contains', 'pat', pat)
    int_arg_check('contains', 'flags', flags)
    if not is_overload_constant_bool(regex):
        raise BodoError(
            "Series.str.contains(): 'regex' argument should be a constant boolean"
            )
    if not is_overload_constant_bool(case):
        raise BodoError(
            "Series.str.contains(): 'case' argument should be a constant boolean"
            )
    vodu__rhl = re.IGNORECASE.value
    dtl__sjori = 'def impl(\n'
    dtl__sjori += '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n'
    dtl__sjori += '):\n'
    dtl__sjori += '  S = S_str._obj\n'
    dtl__sjori += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    dtl__sjori += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    dtl__sjori += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    dtl__sjori += '  l = len(arr)\n'
    dtl__sjori += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            if S_str.stype.data == bodo.dict_str_arr_type:
                dtl__sjori += """  out_arr = bodo.libs.dict_arr_ext.str_series_contains_regex(arr, pat, case, flags, na, regex)
"""
            else:
                dtl__sjori += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            dtl__sjori += """  get_search_regex(arr, case, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        dtl__sjori += (
            '  out_arr = bodo.libs.dict_arr_ext.str_contains_non_regex(arr, pat, case)\n'
            )
    else:
        dtl__sjori += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            dtl__sjori += '  upper_pat = pat.upper()\n'
        dtl__sjori += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        dtl__sjori += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        dtl__sjori += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        dtl__sjori += '      else: \n'
        if is_overload_true(case):
            dtl__sjori += '          out_arr[i] = pat in arr[i]\n'
        else:
            dtl__sjori += (
                '          out_arr[i] = upper_pat in arr[i].upper()\n')
    dtl__sjori += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    cpnky__cakpv = {}
    exec(dtl__sjori, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': vodu__rhl, 'get_search_regex':
        get_search_regex}, cpnky__cakpv)
    impl = cpnky__cakpv['impl']
    return impl


@overload_method(SeriesStrMethodType, 'cat', no_unliteral=True)
def overload_str_method_cat(S_str, others=None, sep=None, na_rep=None, join
    ='left'):
    if not isinstance(others, DataFrameType):
        raise_bodo_error(
            "Series.str.cat(): 'others' must be a DataFrame currently")
    if not is_overload_none(sep):
        str_arg_check('cat', 'sep', sep)
    if not is_overload_constant_str(join) or get_overload_const_str(join
        ) != 'left':
        raise_bodo_error("Series.str.cat(): 'join' not supported yet")
    dtl__sjori = (
        "def impl(S_str, others=None, sep=None, na_rep=None, join='left'):\n")
    dtl__sjori += '  S = S_str._obj\n'
    dtl__sjori += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    dtl__sjori += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    dtl__sjori += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    dtl__sjori += '  l = len(arr)\n'
    for i in range(len(others.columns)):
        dtl__sjori += f"""  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(others, {i})
"""
    if S_str.stype.data == bodo.dict_str_arr_type and all(kep__ffk == bodo.
        dict_str_arr_type for kep__ffk in others.data):
        hhv__mzjbr = ', '.join(f'data{i}' for i in range(len(others.columns)))
        dtl__sjori += (
            f'  out_arr = bodo.libs.dict_arr_ext.cat_dict_str((arr, {hhv__mzjbr}), sep)\n'
            )
    else:
        gzp__xqh = ' or '.join(['bodo.libs.array_kernels.isna(arr, i)'] + [
            f'bodo.libs.array_kernels.isna(data{i}, i)' for i in range(len(
            others.columns))])
        dtl__sjori += (
            '  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)\n'
            )
        dtl__sjori += '  numba.parfors.parfor.init_prange()\n'
        dtl__sjori += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        dtl__sjori += f'      if {gzp__xqh}:\n'
        dtl__sjori += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        dtl__sjori += '          continue\n'
        vcdz__uqn = ', '.join(['arr[i]'] + [f'data{i}[i]' for i in range(
            len(others.columns))])
        pdg__otwc = "''" if is_overload_none(sep) else 'sep'
        dtl__sjori += f'      out_arr[i] = {pdg__otwc}.join([{vcdz__uqn}])\n'
    dtl__sjori += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    cpnky__cakpv = {}
    exec(dtl__sjori, {'bodo': bodo, 'numba': numba}, cpnky__cakpv)
    impl = cpnky__cakpv['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_count_dict_impl(S_str, pat, flags=0):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_count(uprfc__zmt, pat, flags)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_count_dict_impl

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        cjjcx__cszn = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        smc__lfp = len(anxwf__hed)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(smc__lfp, np.int64)
        for i in numba.parfors.parfor.internal_prange(smc__lfp):
            if bodo.libs.array_kernels.isna(anxwf__hed, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(cjjcx__cszn, anxwf__hed[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return impl


@overload_method(SeriesStrMethodType, 'find', inline='always', no_unliteral
    =True)
def overload_str_method_find(S_str, sub, start=0, end=None):
    str_arg_check('find', 'sub', sub)
    int_arg_check('find', 'start', start)
    if not is_overload_none(end):
        int_arg_check('find', 'end', end)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_find_dict_impl(S_str, sub, start=0, end=None):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_find(uprfc__zmt, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_find_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        smc__lfp = len(anxwf__hed)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(smc__lfp, np.int64)
        for i in numba.parfors.parfor.internal_prange(smc__lfp):
            if bodo.libs.array_kernels.isna(anxwf__hed, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = anxwf__hed[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return impl


@overload_method(SeriesStrMethodType, 'rfind', inline='always',
    no_unliteral=True)
def overload_str_method_rfind(S_str, sub, start=0, end=None):
    str_arg_check('rfind', 'sub', sub)
    if start != 0:
        int_arg_check('rfind', 'start', start)
    if not is_overload_none(end):
        int_arg_check('rfind', 'end', end)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_rfind_dict_impl(S_str, sub, start=0, end=None):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rfind(uprfc__zmt, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_rfind_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        smc__lfp = len(anxwf__hed)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(smc__lfp, np.int64)
        for i in numba.parfors.parfor.internal_prange(smc__lfp):
            if bodo.libs.array_kernels.isna(anxwf__hed, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = anxwf__hed[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return impl


@overload_method(SeriesStrMethodType, 'slice_replace', inline='always',
    no_unliteral=True)
def overload_str_method_slice_replace(S_str, start=0, stop=None, repl=''):
    int_arg_check('slice_replace', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice_replace', 'stop', stop)
    str_arg_check('slice_replace', 'repl', repl)

    def impl(S_str, start=0, stop=None, repl=''):
        S = S_str._obj
        anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        smc__lfp = len(anxwf__hed)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(smc__lfp, -1)
        for xxvh__yyb in numba.parfors.parfor.internal_prange(smc__lfp):
            if bodo.libs.array_kernels.isna(anxwf__hed, xxvh__yyb):
                bodo.libs.array_kernels.setna(out_arr, xxvh__yyb)
            else:
                if stop is not None:
                    hmt__vsqq = anxwf__hed[xxvh__yyb][stop:]
                else:
                    hmt__vsqq = ''
                out_arr[xxvh__yyb] = anxwf__hed[xxvh__yyb][:start
                    ] + repl + hmt__vsqq
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):
        if S_str.stype.data == bodo.dict_str_arr_type:

            def _str_repeat_int_dict_impl(S_str, repeats):
                S = S_str._obj
                uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
                hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
                tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
                out_arr = bodo.libs.dict_arr_ext.str_repeat_int(uprfc__zmt,
                    repeats)
                return bodo.hiframes.pd_series_ext.init_series(out_arr,
                    hnw__saoa, tmra__axkh)
            return _str_repeat_int_dict_impl

        def impl(S_str, repeats):
            S = S_str._obj
            anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            smc__lfp = len(anxwf__hed)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(smc__lfp, -1
                )
            for xxvh__yyb in numba.parfors.parfor.internal_prange(smc__lfp):
                if bodo.libs.array_kernels.isna(anxwf__hed, xxvh__yyb):
                    bodo.libs.array_kernels.setna(out_arr, xxvh__yyb)
                else:
                    out_arr[xxvh__yyb] = anxwf__hed[xxvh__yyb] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return impl
    elif is_overload_constant_list(repeats):
        dmaj__qdt = get_overload_const_list(repeats)
        ymily__zqs = all([isinstance(kcjic__aybrm, int) for kcjic__aybrm in
            dmaj__qdt])
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        ymily__zqs = True
    else:
        ymily__zqs = False
    if ymily__zqs:

        def impl(S_str, repeats):
            S = S_str._obj
            anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            hgi__cgoe = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            smc__lfp = len(anxwf__hed)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(smc__lfp, -1
                )
            for xxvh__yyb in numba.parfors.parfor.internal_prange(smc__lfp):
                if bodo.libs.array_kernels.isna(anxwf__hed, xxvh__yyb):
                    bodo.libs.array_kernels.setna(out_arr, xxvh__yyb)
                else:
                    out_arr[xxvh__yyb] = anxwf__hed[xxvh__yyb] * hgi__cgoe[
                        xxvh__yyb]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


def create_ljust_rjust_center_overload(func_name):
    dtl__sjori = f"""def dict_impl(S_str, width, fillchar=' '):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr, width, fillchar)
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
def impl(S_str, width, fillchar=' '):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    numba.parfors.parfor.init_prange()
    l = len(str_arr)
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
    for j in numba.parfors.parfor.internal_prange(l):
        if bodo.libs.array_kernels.isna(str_arr, j):
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}(width, fillchar)
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    cpnky__cakpv = {}
    mezy__utwn = {'bodo': bodo, 'numba': numba}
    exec(dtl__sjori, mezy__utwn, cpnky__cakpv)
    impl = cpnky__cakpv['impl']
    xxa__ndxmm = cpnky__cakpv['dict_impl']

    def overload_ljust_rjust_center_method(S_str, width, fillchar=' '):
        common_validate_padding(func_name, width, fillchar)
        if S_str.stype.data == bodo.dict_str_arr_type:
            return xxa__ndxmm
        return impl
    return overload_ljust_rjust_center_method


def _install_ljust_rjust_center():
    for xtek__bqws in ['ljust', 'rjust', 'center']:
        impl = create_ljust_rjust_center_overload(xtek__bqws)
        overload_method(SeriesStrMethodType, xtek__bqws, inline='always',
            no_unliteral=True)(impl)


_install_ljust_rjust_center()


@overload_method(SeriesStrMethodType, 'pad', no_unliteral=True)
def overload_str_method_pad(S_str, width, side='left', fillchar=' '):
    common_validate_padding('pad', width, fillchar)
    if is_overload_constant_str(side):
        if get_overload_const_str(side) not in ['left', 'right', 'both']:
            raise BodoError('Series.str.pad(): Invalid Side')
    else:
        raise BodoError('Series.str.pad(): Invalid Side')
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_pad_dict_impl(S_str, width, side='left', fillchar=' '):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            if side == 'left':
                out_arr = bodo.libs.dict_arr_ext.str_rjust(uprfc__zmt,
                    width, fillchar)
            elif side == 'right':
                out_arr = bodo.libs.dict_arr_ext.str_ljust(uprfc__zmt,
                    width, fillchar)
            elif side == 'both':
                out_arr = bodo.libs.dict_arr_ext.str_center(uprfc__zmt,
                    width, fillchar)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_pad_dict_impl

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        smc__lfp = len(anxwf__hed)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(smc__lfp, -1)
        for xxvh__yyb in numba.parfors.parfor.internal_prange(smc__lfp):
            if bodo.libs.array_kernels.isna(anxwf__hed, xxvh__yyb):
                out_arr[xxvh__yyb] = ''
                bodo.libs.array_kernels.setna(out_arr, xxvh__yyb)
            elif side == 'left':
                out_arr[xxvh__yyb] = anxwf__hed[xxvh__yyb].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[xxvh__yyb] = anxwf__hed[xxvh__yyb].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[xxvh__yyb] = anxwf__hed[xxvh__yyb].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_zfill_dict_impl(S_str, width):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_zfill(uprfc__zmt, width)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_zfill_dict_impl

    def impl(S_str, width):
        S = S_str._obj
        anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        smc__lfp = len(anxwf__hed)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(smc__lfp, -1)
        for xxvh__yyb in numba.parfors.parfor.internal_prange(smc__lfp):
            if bodo.libs.array_kernels.isna(anxwf__hed, xxvh__yyb):
                out_arr[xxvh__yyb] = ''
                bodo.libs.array_kernels.setna(out_arr, xxvh__yyb)
            else:
                out_arr[xxvh__yyb] = anxwf__hed[xxvh__yyb].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return impl


@overload_method(SeriesStrMethodType, 'slice', no_unliteral=True)
def overload_str_method_slice(S_str, start=None, stop=None, step=None):
    if not is_overload_none(start):
        int_arg_check('slice', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice', 'stop', stop)
    if not is_overload_none(step):
        int_arg_check('slice', 'step', step)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_slice_dict_impl(S_str, start=None, stop=None, step=None):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_slice(uprfc__zmt, start,
                stop, step)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_slice_dict_impl

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        smc__lfp = len(anxwf__hed)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(smc__lfp, -1)
        for xxvh__yyb in numba.parfors.parfor.internal_prange(smc__lfp):
            if bodo.libs.array_kernels.isna(anxwf__hed, xxvh__yyb):
                out_arr[xxvh__yyb] = ''
                bodo.libs.array_kernels.setna(out_arr, xxvh__yyb)
            else:
                out_arr[xxvh__yyb] = anxwf__hed[xxvh__yyb][start:stop:step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_startswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_startswith(uprfc__zmt, pat, na
                )
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_startswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        smc__lfp = len(anxwf__hed)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(smc__lfp)
        for i in numba.parfors.parfor.internal_prange(smc__lfp):
            if bodo.libs.array_kernels.isna(anxwf__hed, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = anxwf__hed[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_endswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
            hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
            tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_endswith(uprfc__zmt, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hnw__saoa, tmra__axkh)
        return _str_endswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        anxwf__hed = bodo.hiframes.pd_series_ext.get_series_data(S)
        tmra__axkh = bodo.hiframes.pd_series_ext.get_series_name(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        smc__lfp = len(anxwf__hed)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(smc__lfp)
        for i in numba.parfors.parfor.internal_prange(smc__lfp):
            if bodo.libs.array_kernels.isna(anxwf__hed, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = anxwf__hed[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hnw__saoa,
            tmra__axkh)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_str_method_getitem(S_str, ind):
    if not isinstance(S_str, SeriesStrMethodType):
        return
    if not isinstance(types.unliteral(ind), (types.SliceType, types.Integer)):
        raise BodoError(
            'index input to Series.str[] should be a slice or an integer')
    if isinstance(ind, types.SliceType):
        return lambda S_str, ind: S_str.slice(ind.start, ind.stop, ind.step)
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda S_str, ind: S_str.get(ind)


@overload_method(SeriesStrMethodType, 'extract', inline='always',
    no_unliteral=True)
def overload_str_method_extract(S_str, pat, flags=0, expand=True):
    if not is_overload_constant_bool(expand):
        raise BodoError(
            "Series.str.extract(): 'expand' argument should be a constant bool"
            )
    mchgr__qyhj, regex = _get_column_names_from_regex(pat, flags, 'extract')
    maxk__hape = len(mchgr__qyhj)
    if S_str.stype.data == bodo.dict_str_arr_type:
        dtl__sjori = 'def impl(S_str, pat, flags=0, expand=True):\n'
        dtl__sjori += '  S = S_str._obj\n'
        dtl__sjori += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        dtl__sjori += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        dtl__sjori += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        dtl__sjori += f"""  out_arr_list = bodo.libs.dict_arr_ext.str_extract(arr, pat, flags, {maxk__hape})
"""
        for i in range(maxk__hape):
            dtl__sjori += f'  out_arr_{i} = out_arr_list[{i}]\n'
    else:
        dtl__sjori = 'def impl(S_str, pat, flags=0, expand=True):\n'
        dtl__sjori += '  regex = re.compile(pat, flags=flags)\n'
        dtl__sjori += '  S = S_str._obj\n'
        dtl__sjori += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        dtl__sjori += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        dtl__sjori += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        dtl__sjori += '  numba.parfors.parfor.init_prange()\n'
        dtl__sjori += '  n = len(str_arr)\n'
        for i in range(maxk__hape):
            dtl__sjori += (
                '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                .format(i))
        dtl__sjori += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        dtl__sjori += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        for i in range(maxk__hape):
            dtl__sjori += "          out_arr_{}[j] = ''\n".format(i)
            dtl__sjori += (
                '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
                format(i))
        dtl__sjori += '      else:\n'
        dtl__sjori += '          m = regex.search(str_arr[j])\n'
        dtl__sjori += '          if m:\n'
        dtl__sjori += '            g = m.groups()\n'
        for i in range(maxk__hape):
            dtl__sjori += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
        dtl__sjori += '          else:\n'
        for i in range(maxk__hape):
            dtl__sjori += "            out_arr_{}[j] = ''\n".format(i)
            dtl__sjori += (
                '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'
                .format(i))
    if is_overload_false(expand) and regex.groups == 1:
        tmra__axkh = "'{}'".format(list(regex.groupindex.keys()).pop()) if len(
            regex.groupindex.keys()) > 0 else 'name'
        dtl__sjori += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(tmra__axkh))
        cpnky__cakpv = {}
        exec(dtl__sjori, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, cpnky__cakpv)
        impl = cpnky__cakpv['impl']
        return impl
    xomp__nbh = ', '.join('out_arr_{}'.format(i) for i in range(maxk__hape))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(dtl__sjori,
        mchgr__qyhj, xomp__nbh, 'index', extra_globals={'get_utf8_size':
        get_utf8_size, 're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    mchgr__qyhj, gjn__axbi = _get_column_names_from_regex(pat, flags,
        'extractall')
    maxk__hape = len(mchgr__qyhj)
    wtj__fqx = isinstance(S_str.stype.index, StringIndexType)
    gzbw__rsva = maxk__hape > 1
    ilp__bkmtt = '_multi' if gzbw__rsva else ''
    if S_str.stype.data == bodo.dict_str_arr_type:
        dtl__sjori = 'def impl(S_str, pat, flags=0):\n'
        dtl__sjori += '  S = S_str._obj\n'
        dtl__sjori += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        dtl__sjori += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        dtl__sjori += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        dtl__sjori += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        dtl__sjori += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        dtl__sjori += '  regex = re.compile(pat, flags=flags)\n'
        dtl__sjori += '  out_ind_arr, out_match_arr, out_arr_list = '
        dtl__sjori += f'bodo.libs.dict_arr_ext.str_extractall{ilp__bkmtt}(\n'
        dtl__sjori += f'arr, regex, {maxk__hape}, index_arr)\n'
        for i in range(maxk__hape):
            dtl__sjori += f'  out_arr_{i} = out_arr_list[{i}]\n'
        dtl__sjori += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        dtl__sjori += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    else:
        dtl__sjori = 'def impl(S_str, pat, flags=0):\n'
        dtl__sjori += '  regex = re.compile(pat, flags=flags)\n'
        dtl__sjori += '  S = S_str._obj\n'
        dtl__sjori += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        dtl__sjori += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        dtl__sjori += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        dtl__sjori += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        dtl__sjori += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        dtl__sjori += '  numba.parfors.parfor.init_prange()\n'
        dtl__sjori += '  n = len(str_arr)\n'
        dtl__sjori += '  out_n_l = [0]\n'
        for i in range(maxk__hape):
            dtl__sjori += '  num_chars_{} = 0\n'.format(i)
        if wtj__fqx:
            dtl__sjori += '  index_num_chars = 0\n'
        dtl__sjori += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if wtj__fqx:
            dtl__sjori += (
                '      index_num_chars += get_utf8_size(index_arr[i])\n')
        dtl__sjori += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
        dtl__sjori += '          continue\n'
        dtl__sjori += '      m = regex.findall(str_arr[i])\n'
        dtl__sjori += '      out_n_l[0] += len(m)\n'
        for i in range(maxk__hape):
            dtl__sjori += '      l_{} = 0\n'.format(i)
        dtl__sjori += '      for s in m:\n'
        for i in range(maxk__hape):
            dtl__sjori += '        l_{} += get_utf8_size(s{})\n'.format(i, 
                '[{}]'.format(i) if maxk__hape > 1 else '')
        for i in range(maxk__hape):
            dtl__sjori += '      num_chars_{0} += l_{0}\n'.format(i)
        dtl__sjori += (
            '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
            )
        for i in range(maxk__hape):
            dtl__sjori += (
                """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
                .format(i))
        if wtj__fqx:
            dtl__sjori += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
        else:
            dtl__sjori += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
        dtl__sjori += '  out_match_arr = np.empty(out_n, np.int64)\n'
        dtl__sjori += '  out_ind = 0\n'
        dtl__sjori += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        dtl__sjori += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        dtl__sjori += '          continue\n'
        dtl__sjori += '      m = regex.findall(str_arr[j])\n'
        dtl__sjori += '      for k, s in enumerate(m):\n'
        for i in range(maxk__hape):
            dtl__sjori += (
                """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
                .format(i, '[{}]'.format(i) if maxk__hape > 1 else ''))
        dtl__sjori += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
        dtl__sjori += """        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)
"""
        dtl__sjori += '        out_ind += 1\n'
        dtl__sjori += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        dtl__sjori += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    xomp__nbh = ', '.join('out_arr_{}'.format(i) for i in range(maxk__hape))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(dtl__sjori,
        mchgr__qyhj, xomp__nbh, 'out_index', extra_globals={'get_utf8_size':
        get_utf8_size, 're': re})
    return impl


def _get_column_names_from_regex(pat, flags, func_name):
    if not is_overload_constant_str(pat):
        raise BodoError(
            "Series.str.{}(): 'pat' argument should be a constant string".
            format(func_name))
    if not is_overload_constant_int(flags):
        raise BodoError(
            "Series.str.{}(): 'flags' argument should be a constant int".
            format(func_name))
    pat = get_overload_const_str(pat)
    flags = get_overload_const_int(flags)
    regex = re.compile(pat, flags=flags)
    if regex.groups == 0:
        raise BodoError(
            'Series.str.{}(): pattern {} contains no capture groups'.format
            (func_name, pat))
    dfy__qbv = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    mchgr__qyhj = [dfy__qbv.get(1 + i, i) for i in range(regex.groups)]
    return mchgr__qyhj, regex


def create_str2str_methods_overload(func_name):
    zvr__nekl = func_name in ['lstrip', 'rstrip', 'strip']
    dtl__sjori = f"""def f({'S_str, to_strip=None' if zvr__nekl else 'S_str'}):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    str_arr = decode_if_dict_array(str_arr)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    numba.parfors.parfor.init_prange()
    n = len(str_arr)
    num_chars = {'-1' if zvr__nekl else 'num_total_chars(str_arr)'}
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)
    for j in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(str_arr, j):
            out_arr[j] = ""
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}({'to_strip' if zvr__nekl else ''})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    dtl__sjori += f"""def _dict_impl({'S_str, to_strip=None' if zvr__nekl else 'S_str'}):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}({'arr, to_strip' if zvr__nekl else 'arr'})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    cpnky__cakpv = {}
    exec(dtl__sjori, {'bodo': bodo, 'numba': numba, 'num_total_chars': bodo
        .libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size, 'decode_if_dict_array': bodo.utils.
        typing.decode_if_dict_array}, cpnky__cakpv)
    whqrs__glpe = cpnky__cakpv['f']
    kwsj__tdd = cpnky__cakpv['_dict_impl']
    if zvr__nekl:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            if S_str.stype.data == bodo.dict_str_arr_type:
                return kwsj__tdd
            return whqrs__glpe
        return overload_strip_method
    else:

        def overload_str_method_dict_supported(S_str):
            if S_str.stype.data == bodo.dict_str_arr_type:
                return kwsj__tdd
            return whqrs__glpe
        return overload_str_method_dict_supported


def create_str2bool_methods_overload(func_name):
    dtl__sjori = 'def dict_impl(S_str):\n'
    dtl__sjori += '    S = S_str._obj\n'
    dtl__sjori += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    dtl__sjori += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    dtl__sjori += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    dtl__sjori += (
        f'    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr)\n')
    dtl__sjori += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    dtl__sjori += 'def impl(S_str):\n'
    dtl__sjori += '    S = S_str._obj\n'
    dtl__sjori += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    dtl__sjori += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    dtl__sjori += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    dtl__sjori += '    numba.parfors.parfor.init_prange()\n'
    dtl__sjori += '    l = len(str_arr)\n'
    dtl__sjori += '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    dtl__sjori += '    for i in numba.parfors.parfor.internal_prange(l):\n'
    dtl__sjori += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
    dtl__sjori += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
    dtl__sjori += '        else:\n'
    dtl__sjori += ('            out_arr[i] = np.bool_(str_arr[i].{}())\n'.
        format(func_name))
    dtl__sjori += '    return bodo.hiframes.pd_series_ext.init_series(\n'
    dtl__sjori += '      out_arr,index, name)\n'
    cpnky__cakpv = {}
    exec(dtl__sjori, {'bodo': bodo, 'numba': numba, 'np': np}, cpnky__cakpv)
    impl = cpnky__cakpv['impl']
    xxa__ndxmm = cpnky__cakpv['dict_impl']

    def overload_str2bool_methods(S_str):
        if S_str.stype.data == bodo.dict_str_arr_type:
            return xxa__ndxmm
        return impl
    return overload_str2bool_methods


def _install_str2str_methods():
    for olixd__thvft in bodo.hiframes.pd_series_ext.str2str_methods:
        qvana__huxth = create_str2str_methods_overload(olixd__thvft)
        overload_method(SeriesStrMethodType, olixd__thvft, inline='always',
            no_unliteral=True)(qvana__huxth)


def _install_str2bool_methods():
    for olixd__thvft in bodo.hiframes.pd_series_ext.str2bool_methods:
        qvana__huxth = create_str2bool_methods_overload(olixd__thvft)
        overload_method(SeriesStrMethodType, olixd__thvft, inline='always',
            no_unliteral=True)(qvana__huxth)


_install_str2str_methods()
_install_str2bool_methods()


@overload_attribute(SeriesType, 'cat')
def overload_series_cat(s):
    if not isinstance(s.dtype, bodo.hiframes.pd_categorical_ext.
        PDCategoricalDtype):
        raise BodoError('Can only use .cat accessor with categorical values.')
    return lambda s: bodo.hiframes.series_str_impl.init_series_cat_method(s)


class SeriesCatMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        tmra__axkh = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(tmra__axkh)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rohw__ndl = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, rohw__ndl)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        aljhp__dethl, = args
        qpd__zxno = signature.return_type
        vkc__kqw = cgutils.create_struct_proxy(qpd__zxno)(context, builder)
        vkc__kqw.obj = aljhp__dethl
        context.nrt.incref(builder, signature.args[0], aljhp__dethl)
        return vkc__kqw._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        uprfc__zmt = bodo.hiframes.pd_series_ext.get_series_data(S)
        hnw__saoa = bodo.hiframes.pd_series_ext.get_series_index(S)
        tmra__axkh = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(uprfc__zmt),
            hnw__saoa, tmra__axkh)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for trdk__yfau in unsupported_cat_attrs:
        hxe__hnv = 'Series.cat.' + trdk__yfau
        overload_attribute(SeriesCatMethodType, trdk__yfau)(
            create_unsupported_overload(hxe__hnv))
    for pyb__zrps in unsupported_cat_methods:
        hxe__hnv = 'Series.cat.' + pyb__zrps
        overload_method(SeriesCatMethodType, pyb__zrps)(
            create_unsupported_overload(hxe__hnv))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for pyb__zrps in unsupported_str_methods:
        hxe__hnv = 'Series.str.' + pyb__zrps
        overload_method(SeriesStrMethodType, pyb__zrps)(
            create_unsupported_overload(hxe__hnv))


_install_strseries_unsupported()
