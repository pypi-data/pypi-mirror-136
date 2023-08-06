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
from numba.core import types
from numba.extending import overload
import bodo
from bodo.io import csv_cpp
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.str_ext import unicode_to_utf8, unicode_to_utf8_and_len
from bodo.utils.typing import BodoError, BodoWarning
from bodo.utils.utils import check_java_installation
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
    """


def get_proxy_uri_from_env_vars():
    return os.environ.get('http_proxy', None) or os.environ.get('https_proxy',
        None) or os.environ.get('HTTP_PROXY', None) or os.environ.get(
        'HTTPS_PROXY', None)


def get_s3_fs(region=None, storage_options=None):
    from bodo.io.pyarrow_s3fs_fsspec_wrapper import PyArrowS3FS
    ynwuj__qjdlf = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    gga__xke = False
    ndifi__xdk = get_proxy_uri_from_env_vars()
    if storage_options:
        gga__xke = storage_options.get('anon', False)
    PyArrowS3FS.clear_instance_cache()
    fs = PyArrowS3FS(region=region, endpoint_override=ynwuj__qjdlf,
        anonymous=gga__xke, proxy_options=ndifi__xdk)
    return fs


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    ynwuj__qjdlf = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    gga__xke = False
    ndifi__xdk = get_proxy_uri_from_env_vars()
    if storage_options:
        gga__xke = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=ynwuj__qjdlf,
        anonymous=gga__xke, proxy_options=ndifi__xdk)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.hdfs import HadoopFileSystem as HdFS
    taydw__cen = urlparse(path)
    if taydw__cen.scheme in ('abfs', 'abfss'):
        mju__ebt = path
        if taydw__cen.port is None:
            zeel__hrvg = 0
        else:
            zeel__hrvg = taydw__cen.port
        lmpqe__kxfi = None
    else:
        mju__ebt = taydw__cen.hostname
        zeel__hrvg = taydw__cen.port
        lmpqe__kxfi = taydw__cen.username
    try:
        fs = HdFS(host=mju__ebt, port=zeel__hrvg, user=lmpqe__kxfi)
    except Exception as yeh__qbod:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            yeh__qbod))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        sbk__eaeo = fs.isdir(path)
    except gcsfs.utils.HttpError as yeh__qbod:
        raise BodoError(
            f'{yeh__qbod}. Make sure your google cloud credentials are set!')
    return sbk__eaeo


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [uqxo__sfwsx.split('/')[-1] for uqxo__sfwsx in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        taydw__cen = urlparse(path)
        xsbi__copfn = (taydw__cen.netloc + taydw__cen.path).rstrip('/')
        kmge__jzs = fs.get_file_info(xsbi__copfn)
        if kmge__jzs.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if not kmge__jzs.size and kmge__jzs.type == pa_fs.FileType.Directory:
            return True
        return False
    except (FileNotFoundError, OSError) as yeh__qbod:
        raise
    except BodoError as zmi__lmk:
        raise
    except Exception as yeh__qbod:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(yeh__qbod).__name__}: {str(yeh__qbod)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    qiaq__zjrh = None
    try:
        if s3_is_directory(fs, path):
            taydw__cen = urlparse(path)
            xsbi__copfn = (taydw__cen.netloc + taydw__cen.path).rstrip('/')
            yao__nvt = pa_fs.FileSelector(xsbi__copfn, recursive=False)
            upvqx__sdgmo = fs.get_file_info(yao__nvt)
            if upvqx__sdgmo and upvqx__sdgmo[0].path in [xsbi__copfn,
                f'{xsbi__copfn}/'] and int(upvqx__sdgmo[0].size or 0) == 0:
                upvqx__sdgmo = upvqx__sdgmo[1:]
            qiaq__zjrh = [ahgg__mpv.base_name for ahgg__mpv in upvqx__sdgmo]
    except BodoError as zmi__lmk:
        raise
    except Exception as yeh__qbod:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(yeh__qbod).__name__}: {str(yeh__qbod)}
{bodo_error_msg}"""
            )
    return qiaq__zjrh


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    taydw__cen = urlparse(path)
    tikkv__nrpwv = taydw__cen.path
    try:
        aqfza__vidla = HadoopFileSystem.from_uri(path)
    except Exception as yeh__qbod:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            yeh__qbod))
    oqlf__jezq = aqfza__vidla.get_file_info([tikkv__nrpwv])
    if oqlf__jezq[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not oqlf__jezq[0].size and oqlf__jezq[0].type == FileType.Directory:
        return aqfza__vidla, True
    return aqfza__vidla, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    qiaq__zjrh = None
    aqfza__vidla, sbk__eaeo = hdfs_is_directory(path)
    if sbk__eaeo:
        taydw__cen = urlparse(path)
        tikkv__nrpwv = taydw__cen.path
        yao__nvt = FileSelector(tikkv__nrpwv, recursive=True)
        try:
            upvqx__sdgmo = aqfza__vidla.get_file_info(yao__nvt)
        except Exception as yeh__qbod:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(tikkv__nrpwv, yeh__qbod))
        qiaq__zjrh = [ahgg__mpv.base_name for ahgg__mpv in upvqx__sdgmo]
    return aqfza__vidla, qiaq__zjrh


def abfs_is_directory(path):
    aqfza__vidla = get_hdfs_fs(path)
    try:
        oqlf__jezq = aqfza__vidla.info(path)
    except OSError as zmi__lmk:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if oqlf__jezq['size'] == 0 and oqlf__jezq['kind'].lower() == 'directory':
        return aqfza__vidla, True
    return aqfza__vidla, False


def abfs_list_dir_fnames(path):
    qiaq__zjrh = None
    aqfza__vidla, sbk__eaeo = abfs_is_directory(path)
    if sbk__eaeo:
        taydw__cen = urlparse(path)
        tikkv__nrpwv = taydw__cen.path
        try:
            wvnd__apkk = aqfza__vidla.ls(tikkv__nrpwv)
        except Exception as yeh__qbod:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(tikkv__nrpwv, yeh__qbod))
        qiaq__zjrh = [fname[fname.rindex('/') + 1:] for fname in wvnd__apkk]
    return aqfza__vidla, qiaq__zjrh


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype):
    from urllib.parse import urlparse
    anzdh__ywffv = urlparse(path)
    fname = path
    fs = None
    ivrt__tyc = 'read_json' if ftype == 'json' else 'read_csv'
    oeggq__rct = (
        f'pd.{ivrt__tyc}(): there is no {ftype} file in directory: {fname}')
    oxs__ppbd = directory_of_files_common_filter
    if anzdh__ywffv.scheme == 's3':
        sxpis__scsav = True
        fs = get_s3_fs_from_path(path)
        bqfmb__ajn = s3_list_dir_fnames(fs, path)
        xsbi__copfn = (anzdh__ywffv.netloc + anzdh__ywffv.path).rstrip('/')
        fname = xsbi__copfn
        if bqfmb__ajn:
            bqfmb__ajn = [(xsbi__copfn + '/' + uqxo__sfwsx) for uqxo__sfwsx in
                sorted(filter(oxs__ppbd, bqfmb__ajn))]
            xwf__wkftc = [uqxo__sfwsx for uqxo__sfwsx in bqfmb__ajn if int(
                fs.get_file_info(uqxo__sfwsx).size or 0) > 0]
            if len(xwf__wkftc) == 0:
                raise BodoError(oeggq__rct)
            fname = xwf__wkftc[0]
        tikj__osx = int(fs.get_file_info(fname).size or 0)
        fefym__aebz = fs.open_input_file(fname)
    elif anzdh__ywffv.scheme == 'hdfs':
        sxpis__scsav = True
        fs, bqfmb__ajn = hdfs_list_dir_fnames(path)
        tikj__osx = fs.get_file_info([anzdh__ywffv.path])[0].size
        if bqfmb__ajn:
            path = path.rstrip('/')
            bqfmb__ajn = [(path + '/' + uqxo__sfwsx) for uqxo__sfwsx in
                sorted(filter(oxs__ppbd, bqfmb__ajn))]
            xwf__wkftc = [uqxo__sfwsx for uqxo__sfwsx in bqfmb__ajn if fs.
                get_file_info([urlparse(uqxo__sfwsx).path])[0].size > 0]
            if len(xwf__wkftc) == 0:
                raise BodoError(oeggq__rct)
            fname = xwf__wkftc[0]
            fname = urlparse(fname).path
            tikj__osx = fs.get_file_info([fname])[0].size
        fefym__aebz = fs.open_input_file(fname)
    elif anzdh__ywffv.scheme in ('abfs', 'abfss'):
        sxpis__scsav = True
        fs, bqfmb__ajn = abfs_list_dir_fnames(path)
        tikj__osx = fs.info(fname)['size']
        if bqfmb__ajn:
            path = path.rstrip('/')
            bqfmb__ajn = [(path + '/' + uqxo__sfwsx) for uqxo__sfwsx in
                sorted(filter(oxs__ppbd, bqfmb__ajn))]
            xwf__wkftc = [uqxo__sfwsx for uqxo__sfwsx in bqfmb__ajn if fs.
                info(uqxo__sfwsx)['size'] > 0]
            if len(xwf__wkftc) == 0:
                raise BodoError(oeggq__rct)
            fname = xwf__wkftc[0]
            tikj__osx = fs.info(fname)['size']
            fname = urlparse(fname).path
        fefym__aebz = fs.open(fname, 'rb')
    else:
        if anzdh__ywffv.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {anzdh__ywffv.scheme}. Please refer to https://docs.bodo.ai/latest/source/file_io.html'
                )
        sxpis__scsav = False
        if os.path.isdir(path):
            wvnd__apkk = filter(oxs__ppbd, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            xwf__wkftc = [uqxo__sfwsx for uqxo__sfwsx in sorted(wvnd__apkk) if
                os.path.getsize(uqxo__sfwsx) > 0]
            if len(xwf__wkftc) == 0:
                raise BodoError(oeggq__rct)
            fname = xwf__wkftc[0]
        tikj__osx = os.path.getsize(fname)
        fefym__aebz = fname
    return sxpis__scsav, fefym__aebz, tikj__osx, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    rjvuu__srp = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            sexy__xmjf, ocwog__ghv = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = sexy__xmjf.region
        except Exception as yeh__qbod:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{yeh__qbod}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = rjvuu__srp.bcast(bucket_loc)
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
        srno__gyq = get_s3_bucket_region_njit(path_or_buf, parallel=is_parallel
            )
        xoz__oxgz, mru__qwbd = unicode_to_utf8_and_len(D)
        xybz__miahx = 0
        if is_parallel:
            xybz__miahx = bodo.libs.distributed_api.dist_exscan(mru__qwbd,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), xoz__oxgz, xybz__miahx,
            mru__qwbd, is_parallel, unicode_to_utf8(srno__gyq))
        bodo.utils.utils.check_and_propagate_cpp_exception()
    return impl
