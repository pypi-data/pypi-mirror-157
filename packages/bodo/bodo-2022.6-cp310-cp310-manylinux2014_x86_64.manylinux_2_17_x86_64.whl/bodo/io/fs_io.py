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
            cjzbi__rek = self.fs.open_input_file(path)
        except:
            cjzbi__rek = self.fs.open_input_stream(path)
    elif mode == 'wb':
        cjzbi__rek = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, cjzbi__rek, path, mode, block_size, **kwargs)


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
    rlg__lqsn = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    wymac__pfcq = False
    qcdu__ngg = get_proxy_uri_from_env_vars()
    if storage_options:
        wymac__pfcq = storage_options.get('anon', False)
    return S3FileSystem(anonymous=wymac__pfcq, region=region,
        endpoint_override=rlg__lqsn, proxy_options=qcdu__ngg)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    rlg__lqsn = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    wymac__pfcq = False
    qcdu__ngg = get_proxy_uri_from_env_vars()
    if storage_options:
        wymac__pfcq = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=rlg__lqsn, anonymous
        =wymac__pfcq, proxy_options=qcdu__ngg)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    bdhx__iimp = urlparse(path)
    if bdhx__iimp.scheme in ('abfs', 'abfss'):
        zdu__luowy = path
        if bdhx__iimp.port is None:
            wbo__mwzo = 0
        else:
            wbo__mwzo = bdhx__iimp.port
        rlnl__tgf = None
    else:
        zdu__luowy = bdhx__iimp.hostname
        wbo__mwzo = bdhx__iimp.port
        rlnl__tgf = bdhx__iimp.username
    try:
        fs = HdFS(host=zdu__luowy, port=wbo__mwzo, user=rlnl__tgf)
    except Exception as jbsg__ilbr:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            jbsg__ilbr))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        lybpg__wgan = fs.isdir(path)
    except gcsfs.utils.HttpError as jbsg__ilbr:
        raise BodoError(
            f'{jbsg__ilbr}. Make sure your google cloud credentials are set!')
    return lybpg__wgan


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [toj__uoe.split('/')[-1] for toj__uoe in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        bdhx__iimp = urlparse(path)
        ful__cqcd = (bdhx__iimp.netloc + bdhx__iimp.path).rstrip('/')
        qrih__ndyhc = fs.get_file_info(ful__cqcd)
        if qrih__ndyhc.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown
            ):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if (not qrih__ndyhc.size and qrih__ndyhc.type == pa_fs.FileType.
            Directory):
            return True
        return False
    except (FileNotFoundError, OSError) as jbsg__ilbr:
        raise
    except BodoError as kllg__tsfa:
        raise
    except Exception as jbsg__ilbr:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(jbsg__ilbr).__name__}: {str(jbsg__ilbr)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    ltqpy__wnv = None
    try:
        if s3_is_directory(fs, path):
            bdhx__iimp = urlparse(path)
            ful__cqcd = (bdhx__iimp.netloc + bdhx__iimp.path).rstrip('/')
            eov__dsguw = pa_fs.FileSelector(ful__cqcd, recursive=False)
            acn__hgzms = fs.get_file_info(eov__dsguw)
            if acn__hgzms and acn__hgzms[0].path in [ful__cqcd, f'{ful__cqcd}/'
                ] and int(acn__hgzms[0].size or 0) == 0:
                acn__hgzms = acn__hgzms[1:]
            ltqpy__wnv = [qjc__ammz.base_name for qjc__ammz in acn__hgzms]
    except BodoError as kllg__tsfa:
        raise
    except Exception as jbsg__ilbr:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(jbsg__ilbr).__name__}: {str(jbsg__ilbr)}
{bodo_error_msg}"""
            )
    return ltqpy__wnv


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    bdhx__iimp = urlparse(path)
    kvk__ehv = bdhx__iimp.path
    try:
        nydjc__xcij = HadoopFileSystem.from_uri(path)
    except Exception as jbsg__ilbr:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            jbsg__ilbr))
    linum__aok = nydjc__xcij.get_file_info([kvk__ehv])
    if linum__aok[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not linum__aok[0].size and linum__aok[0].type == FileType.Directory:
        return nydjc__xcij, True
    return nydjc__xcij, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    ltqpy__wnv = None
    nydjc__xcij, lybpg__wgan = hdfs_is_directory(path)
    if lybpg__wgan:
        bdhx__iimp = urlparse(path)
        kvk__ehv = bdhx__iimp.path
        eov__dsguw = FileSelector(kvk__ehv, recursive=True)
        try:
            acn__hgzms = nydjc__xcij.get_file_info(eov__dsguw)
        except Exception as jbsg__ilbr:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(kvk__ehv, jbsg__ilbr))
        ltqpy__wnv = [qjc__ammz.base_name for qjc__ammz in acn__hgzms]
    return nydjc__xcij, ltqpy__wnv


def abfs_is_directory(path):
    nydjc__xcij = get_hdfs_fs(path)
    try:
        linum__aok = nydjc__xcij.info(path)
    except OSError as kllg__tsfa:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if linum__aok['size'] == 0 and linum__aok['kind'].lower() == 'directory':
        return nydjc__xcij, True
    return nydjc__xcij, False


def abfs_list_dir_fnames(path):
    ltqpy__wnv = None
    nydjc__xcij, lybpg__wgan = abfs_is_directory(path)
    if lybpg__wgan:
        bdhx__iimp = urlparse(path)
        kvk__ehv = bdhx__iimp.path
        try:
            rpf__utrl = nydjc__xcij.ls(kvk__ehv)
        except Exception as jbsg__ilbr:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(kvk__ehv, jbsg__ilbr))
        ltqpy__wnv = [fname[fname.rindex('/') + 1:] for fname in rpf__utrl]
    return nydjc__xcij, ltqpy__wnv


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    ntgy__msy = urlparse(path)
    fname = path
    fs = None
    jdly__pwyh = 'read_json' if ftype == 'json' else 'read_csv'
    jzyct__jis = (
        f'pd.{jdly__pwyh}(): there is no {ftype} file in directory: {fname}')
    wahvw__ytyd = directory_of_files_common_filter
    if ntgy__msy.scheme == 's3':
        hit__otue = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        adt__detyx = s3_list_dir_fnames(fs, path)
        ful__cqcd = (ntgy__msy.netloc + ntgy__msy.path).rstrip('/')
        fname = ful__cqcd
        if adt__detyx:
            adt__detyx = [(ful__cqcd + '/' + toj__uoe) for toj__uoe in
                sorted(filter(wahvw__ytyd, adt__detyx))]
            hku__ndk = [toj__uoe for toj__uoe in adt__detyx if int(fs.
                get_file_info(toj__uoe).size or 0) > 0]
            if len(hku__ndk) == 0:
                raise BodoError(jzyct__jis)
            fname = hku__ndk[0]
        mbid__fsjgy = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        xoxwq__yjofb = fs._open(fname)
    elif ntgy__msy.scheme == 'hdfs':
        hit__otue = True
        fs, adt__detyx = hdfs_list_dir_fnames(path)
        mbid__fsjgy = fs.get_file_info([ntgy__msy.path])[0].size
        if adt__detyx:
            path = path.rstrip('/')
            adt__detyx = [(path + '/' + toj__uoe) for toj__uoe in sorted(
                filter(wahvw__ytyd, adt__detyx))]
            hku__ndk = [toj__uoe for toj__uoe in adt__detyx if fs.
                get_file_info([urlparse(toj__uoe).path])[0].size > 0]
            if len(hku__ndk) == 0:
                raise BodoError(jzyct__jis)
            fname = hku__ndk[0]
            fname = urlparse(fname).path
            mbid__fsjgy = fs.get_file_info([fname])[0].size
        xoxwq__yjofb = fs.open_input_file(fname)
    elif ntgy__msy.scheme in ('abfs', 'abfss'):
        hit__otue = True
        fs, adt__detyx = abfs_list_dir_fnames(path)
        mbid__fsjgy = fs.info(fname)['size']
        if adt__detyx:
            path = path.rstrip('/')
            adt__detyx = [(path + '/' + toj__uoe) for toj__uoe in sorted(
                filter(wahvw__ytyd, adt__detyx))]
            hku__ndk = [toj__uoe for toj__uoe in adt__detyx if fs.info(
                toj__uoe)['size'] > 0]
            if len(hku__ndk) == 0:
                raise BodoError(jzyct__jis)
            fname = hku__ndk[0]
            mbid__fsjgy = fs.info(fname)['size']
            fname = urlparse(fname).path
        xoxwq__yjofb = fs.open(fname, 'rb')
    else:
        if ntgy__msy.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {ntgy__msy.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        hit__otue = False
        if os.path.isdir(path):
            rpf__utrl = filter(wahvw__ytyd, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            hku__ndk = [toj__uoe for toj__uoe in sorted(rpf__utrl) if os.
                path.getsize(toj__uoe) > 0]
            if len(hku__ndk) == 0:
                raise BodoError(jzyct__jis)
            fname = hku__ndk[0]
        mbid__fsjgy = os.path.getsize(fname)
        xoxwq__yjofb = fname
    return hit__otue, xoxwq__yjofb, mbid__fsjgy, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    cdpl__ilp = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            iqu__cran, eyyn__jzt = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = iqu__cran.region
        except Exception as jbsg__ilbr:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{jbsg__ilbr}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = cdpl__ilp.bcast(bucket_loc)
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
        olmiq__kbq = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        zlfqk__smvm, thims__oaqx = unicode_to_utf8_and_len(D)
        cjt__gnp = 0
        if is_parallel:
            cjt__gnp = bodo.libs.distributed_api.dist_exscan(thims__oaqx,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), zlfqk__smvm, cjt__gnp,
            thims__oaqx, is_parallel, unicode_to_utf8(olmiq__kbq))
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
    lent__kzjnr = get_overload_constant_dict(storage_options)
    kdbxy__kfow = 'def impl(storage_options):\n'
    kdbxy__kfow += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    kdbxy__kfow += f'    storage_options_py = {str(lent__kzjnr)}\n'
    kdbxy__kfow += '  return storage_options_py\n'
    bfpx__nps = {}
    exec(kdbxy__kfow, globals(), bfpx__nps)
    return bfpx__nps['impl']
