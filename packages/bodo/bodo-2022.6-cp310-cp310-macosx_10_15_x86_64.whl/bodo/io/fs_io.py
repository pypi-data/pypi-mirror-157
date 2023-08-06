"""
S3 & Hadoop file system supports, and file system dependent calls
"""
import glob
import os
import warnings
from urllib.parse import urlparse
import llvmlite.binding as ll
import numba
import numpy as np
from fsspec.implementations.arrow import ArrowFile, ArrowFSWrapper, wrap_exceptions
from numba.core import types
from numba.extending import NativeValue, models, overload, register_model, unbox
import bodo
from bodo.io import csv_cpp
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.str_ext import unicode_to_utf8, unicode_to_utf8_and_len
from bodo.utils.typing import BodoError, BodoWarning, get_overload_constant_dict
from bodo.utils.utils import check_java_installation


def fsspec_arrowfswrapper__open(self, path, mode='rb', block_size=None, **
    kwargs):
    if mode == 'rb':
        try:
            qdo__jtskc = self.fs.open_input_file(path)
        except:
            qdo__jtskc = self.fs.open_input_stream(path)
    elif mode == 'wb':
        qdo__jtskc = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, qdo__jtskc, path, mode, block_size, **kwargs)


ArrowFSWrapper._open = wrap_exceptions(fsspec_arrowfswrapper__open)
_csv_write = types.ExternalFunction('csv_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.voidptr))
ll.add_symbol('csv_write', csv_cpp.csv_write)
bodo_error_msg = """
    Some possible causes:
        (1) Incorrect path: Specified file/directory doesn't exist or is unreachable.
        (2) Missing credentials: You haven't provided S3 credentials, neither through 
            environment variables, nor through a local AWS setup 
            that makes the credentials available at ~/.aws/credentials.
        (3) Incorrect credentials: Your S3 credentials are incorrect or do not have
            the correct permissions.
        (4) Wrong bucket region is used. Set AWS_DEFAULT_REGION variable with correct bucket region.
    """


def get_proxy_uri_from_env_vars():
    return os.environ.get('http_proxy', None) or os.environ.get('https_proxy',
        None) or os.environ.get('HTTP_PROXY', None) or os.environ.get(
        'HTTPS_PROXY', None)


def get_s3_fs(region=None, storage_options=None):
    from pyarrow.fs import S3FileSystem
    eumr__gen = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    yyic__pqtr = False
    ynbo__xbbus = get_proxy_uri_from_env_vars()
    if storage_options:
        yyic__pqtr = storage_options.get('anon', False)
    return S3FileSystem(anonymous=yyic__pqtr, region=region,
        endpoint_override=eumr__gen, proxy_options=ynbo__xbbus)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    eumr__gen = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    yyic__pqtr = False
    ynbo__xbbus = get_proxy_uri_from_env_vars()
    if storage_options:
        yyic__pqtr = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=eumr__gen, anonymous
        =yyic__pqtr, proxy_options=ynbo__xbbus)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    qzrc__gifv = urlparse(path)
    if qzrc__gifv.scheme in ('abfs', 'abfss'):
        sbac__vaz = path
        if qzrc__gifv.port is None:
            efu__mtc = 0
        else:
            efu__mtc = qzrc__gifv.port
        fxtu__fcb = None
    else:
        sbac__vaz = qzrc__gifv.hostname
        efu__mtc = qzrc__gifv.port
        fxtu__fcb = qzrc__gifv.username
    try:
        fs = HdFS(host=sbac__vaz, port=efu__mtc, user=fxtu__fcb)
    except Exception as lldfr__cjs:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            lldfr__cjs))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        rcax__qaqh = fs.isdir(path)
    except gcsfs.utils.HttpError as lldfr__cjs:
        raise BodoError(
            f'{lldfr__cjs}. Make sure your google cloud credentials are set!')
    return rcax__qaqh


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [pdwgo__ybi.split('/')[-1] for pdwgo__ybi in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        qzrc__gifv = urlparse(path)
        bge__kotui = (qzrc__gifv.netloc + qzrc__gifv.path).rstrip('/')
        bicy__khp = fs.get_file_info(bge__kotui)
        if bicy__khp.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if not bicy__khp.size and bicy__khp.type == pa_fs.FileType.Directory:
            return True
        return False
    except (FileNotFoundError, OSError) as lldfr__cjs:
        raise
    except BodoError as rgs__ebty:
        raise
    except Exception as lldfr__cjs:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(lldfr__cjs).__name__}: {str(lldfr__cjs)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    mfw__zoryu = None
    try:
        if s3_is_directory(fs, path):
            qzrc__gifv = urlparse(path)
            bge__kotui = (qzrc__gifv.netloc + qzrc__gifv.path).rstrip('/')
            eknu__lypzo = pa_fs.FileSelector(bge__kotui, recursive=False)
            dgm__qgyg = fs.get_file_info(eknu__lypzo)
            if dgm__qgyg and dgm__qgyg[0].path in [bge__kotui, f'{bge__kotui}/'
                ] and int(dgm__qgyg[0].size or 0) == 0:
                dgm__qgyg = dgm__qgyg[1:]
            mfw__zoryu = [coih__usuri.base_name for coih__usuri in dgm__qgyg]
    except BodoError as rgs__ebty:
        raise
    except Exception as lldfr__cjs:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(lldfr__cjs).__name__}: {str(lldfr__cjs)}
{bodo_error_msg}"""
            )
    return mfw__zoryu


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    qzrc__gifv = urlparse(path)
    kdxkq__pjqxe = qzrc__gifv.path
    try:
        mwauc__kod = HadoopFileSystem.from_uri(path)
    except Exception as lldfr__cjs:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            lldfr__cjs))
    itpyw__bqyk = mwauc__kod.get_file_info([kdxkq__pjqxe])
    if itpyw__bqyk[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not itpyw__bqyk[0].size and itpyw__bqyk[0].type == FileType.Directory:
        return mwauc__kod, True
    return mwauc__kod, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    mfw__zoryu = None
    mwauc__kod, rcax__qaqh = hdfs_is_directory(path)
    if rcax__qaqh:
        qzrc__gifv = urlparse(path)
        kdxkq__pjqxe = qzrc__gifv.path
        eknu__lypzo = FileSelector(kdxkq__pjqxe, recursive=True)
        try:
            dgm__qgyg = mwauc__kod.get_file_info(eknu__lypzo)
        except Exception as lldfr__cjs:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(kdxkq__pjqxe, lldfr__cjs))
        mfw__zoryu = [coih__usuri.base_name for coih__usuri in dgm__qgyg]
    return mwauc__kod, mfw__zoryu


def abfs_is_directory(path):
    mwauc__kod = get_hdfs_fs(path)
    try:
        itpyw__bqyk = mwauc__kod.info(path)
    except OSError as rgs__ebty:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if itpyw__bqyk['size'] == 0 and itpyw__bqyk['kind'].lower() == 'directory':
        return mwauc__kod, True
    return mwauc__kod, False


def abfs_list_dir_fnames(path):
    mfw__zoryu = None
    mwauc__kod, rcax__qaqh = abfs_is_directory(path)
    if rcax__qaqh:
        qzrc__gifv = urlparse(path)
        kdxkq__pjqxe = qzrc__gifv.path
        try:
            yql__fqvjt = mwauc__kod.ls(kdxkq__pjqxe)
        except Exception as lldfr__cjs:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(kdxkq__pjqxe, lldfr__cjs))
        mfw__zoryu = [fname[fname.rindex('/') + 1:] for fname in yql__fqvjt]
    return mwauc__kod, mfw__zoryu


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    uwk__gly = urlparse(path)
    fname = path
    fs = None
    tdsol__ipbzl = 'read_json' if ftype == 'json' else 'read_csv'
    attcu__lgcqj = (
        f'pd.{tdsol__ipbzl}(): there is no {ftype} file in directory: {fname}')
    shgz__kvz = directory_of_files_common_filter
    if uwk__gly.scheme == 's3':
        lwog__pxy = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        njc__seux = s3_list_dir_fnames(fs, path)
        bge__kotui = (uwk__gly.netloc + uwk__gly.path).rstrip('/')
        fname = bge__kotui
        if njc__seux:
            njc__seux = [(bge__kotui + '/' + pdwgo__ybi) for pdwgo__ybi in
                sorted(filter(shgz__kvz, njc__seux))]
            tzlzs__unnkk = [pdwgo__ybi for pdwgo__ybi in njc__seux if int(
                fs.get_file_info(pdwgo__ybi).size or 0) > 0]
            if len(tzlzs__unnkk) == 0:
                raise BodoError(attcu__lgcqj)
            fname = tzlzs__unnkk[0]
        xtac__ber = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        idyf__vnomd = fs._open(fname)
    elif uwk__gly.scheme == 'hdfs':
        lwog__pxy = True
        fs, njc__seux = hdfs_list_dir_fnames(path)
        xtac__ber = fs.get_file_info([uwk__gly.path])[0].size
        if njc__seux:
            path = path.rstrip('/')
            njc__seux = [(path + '/' + pdwgo__ybi) for pdwgo__ybi in sorted
                (filter(shgz__kvz, njc__seux))]
            tzlzs__unnkk = [pdwgo__ybi for pdwgo__ybi in njc__seux if fs.
                get_file_info([urlparse(pdwgo__ybi).path])[0].size > 0]
            if len(tzlzs__unnkk) == 0:
                raise BodoError(attcu__lgcqj)
            fname = tzlzs__unnkk[0]
            fname = urlparse(fname).path
            xtac__ber = fs.get_file_info([fname])[0].size
        idyf__vnomd = fs.open_input_file(fname)
    elif uwk__gly.scheme in ('abfs', 'abfss'):
        lwog__pxy = True
        fs, njc__seux = abfs_list_dir_fnames(path)
        xtac__ber = fs.info(fname)['size']
        if njc__seux:
            path = path.rstrip('/')
            njc__seux = [(path + '/' + pdwgo__ybi) for pdwgo__ybi in sorted
                (filter(shgz__kvz, njc__seux))]
            tzlzs__unnkk = [pdwgo__ybi for pdwgo__ybi in njc__seux if fs.
                info(pdwgo__ybi)['size'] > 0]
            if len(tzlzs__unnkk) == 0:
                raise BodoError(attcu__lgcqj)
            fname = tzlzs__unnkk[0]
            xtac__ber = fs.info(fname)['size']
            fname = urlparse(fname).path
        idyf__vnomd = fs.open(fname, 'rb')
    else:
        if uwk__gly.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {uwk__gly.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        lwog__pxy = False
        if os.path.isdir(path):
            yql__fqvjt = filter(shgz__kvz, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            tzlzs__unnkk = [pdwgo__ybi for pdwgo__ybi in sorted(yql__fqvjt) if
                os.path.getsize(pdwgo__ybi) > 0]
            if len(tzlzs__unnkk) == 0:
                raise BodoError(attcu__lgcqj)
            fname = tzlzs__unnkk[0]
        xtac__ber = os.path.getsize(fname)
        idyf__vnomd = fname
    return lwog__pxy, idyf__vnomd, xtac__ber, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    tptx__scbjm = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            mugxk__mfayz, egm__fgzwf = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = mugxk__mfayz.region
        except Exception as lldfr__cjs:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{lldfr__cjs}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = tptx__scbjm.bcast(bucket_loc)
    return bucket_loc


@numba.njit()
def get_s3_bucket_region_njit(s3_filepath, parallel):
    with numba.objmode(bucket_loc='unicode_type'):
        bucket_loc = ''
        if isinstance(s3_filepath, list):
            s3_filepath = s3_filepath[0]
        if s3_filepath.startswith('s3://'):
            bucket_loc = get_s3_bucket_region(s3_filepath, parallel)
    return bucket_loc


def csv_write(path_or_buf, D, is_parallel=False):
    return None


@overload(csv_write, no_unliteral=True)
def csv_write_overload(path_or_buf, D, is_parallel=False):

    def impl(path_or_buf, D, is_parallel=False):
        bgnzz__autq = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        dvxtv__hjelm, kttv__rysve = unicode_to_utf8_and_len(D)
        yjy__gphn = 0
        if is_parallel:
            yjy__gphn = bodo.libs.distributed_api.dist_exscan(kttv__rysve,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), dvxtv__hjelm, yjy__gphn,
            kttv__rysve, is_parallel, unicode_to_utf8(bgnzz__autq))
        bodo.utils.utils.check_and_propagate_cpp_exception()
    return impl


class StorageOptionsDictType(types.Opaque):

    def __init__(self):
        super(StorageOptionsDictType, self).__init__(name=
            'StorageOptionsDictType')


storage_options_dict_type = StorageOptionsDictType()
types.storage_options_dict_type = storage_options_dict_type
register_model(StorageOptionsDictType)(models.OpaqueModel)


@unbox(StorageOptionsDictType)
def unbox_storage_options_dict_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


def get_storage_options_pyobject(storage_options):
    pass


@overload(get_storage_options_pyobject, no_unliteral=True)
def overload_get_storage_options_pyobject(storage_options):
    oatiw__apr = get_overload_constant_dict(storage_options)
    qrp__kfvuy = 'def impl(storage_options):\n'
    qrp__kfvuy += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    qrp__kfvuy += f'    storage_options_py = {str(oatiw__apr)}\n'
    qrp__kfvuy += '  return storage_options_py\n'
    buzc__lcmj = {}
    exec(qrp__kfvuy, globals(), buzc__lcmj)
    return buzc__lcmj['impl']
