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
    equod__rpwq = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    kcck__ghcs = False
    jckq__mcfv = get_proxy_uri_from_env_vars()
    if storage_options:
        kcck__ghcs = storage_options.get('anon', False)
    PyArrowS3FS.clear_instance_cache()
    fs = PyArrowS3FS(region=region, endpoint_override=equod__rpwq,
        anonymous=kcck__ghcs, proxy_options=jckq__mcfv)
    return fs


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    equod__rpwq = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    kcck__ghcs = False
    jckq__mcfv = get_proxy_uri_from_env_vars()
    if storage_options:
        kcck__ghcs = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=equod__rpwq,
        anonymous=kcck__ghcs, proxy_options=jckq__mcfv)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.hdfs import HadoopFileSystem as HdFS
    kmq__tzac = urlparse(path)
    if kmq__tzac.scheme in ('abfs', 'abfss'):
        boa__fms = path
        if kmq__tzac.port is None:
            olg__tccxf = 0
        else:
            olg__tccxf = kmq__tzac.port
        fpd__dsz = None
    else:
        boa__fms = kmq__tzac.hostname
        olg__tccxf = kmq__tzac.port
        fpd__dsz = kmq__tzac.username
    try:
        fs = HdFS(host=boa__fms, port=olg__tccxf, user=fpd__dsz)
    except Exception as jzgcs__lxi:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            jzgcs__lxi))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        yik__lpuye = fs.isdir(path)
    except gcsfs.utils.HttpError as jzgcs__lxi:
        raise BodoError(
            f'{jzgcs__lxi}. Make sure your google cloud credentials are set!')
    return yik__lpuye


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [rbpzu__xdq.split('/')[-1] for rbpzu__xdq in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        kmq__tzac = urlparse(path)
        cej__lque = (kmq__tzac.netloc + kmq__tzac.path).rstrip('/')
        jmc__osb = fs.get_file_info(cej__lque)
        if jmc__osb.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if not jmc__osb.size and jmc__osb.type == pa_fs.FileType.Directory:
            return True
        return False
    except (FileNotFoundError, OSError) as jzgcs__lxi:
        raise
    except BodoError as nstqw__dtioy:
        raise
    except Exception as jzgcs__lxi:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(jzgcs__lxi).__name__}: {str(jzgcs__lxi)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    nkwif__njwig = None
    try:
        if s3_is_directory(fs, path):
            kmq__tzac = urlparse(path)
            cej__lque = (kmq__tzac.netloc + kmq__tzac.path).rstrip('/')
            ths__mqjf = pa_fs.FileSelector(cej__lque, recursive=False)
            kle__ptaw = fs.get_file_info(ths__mqjf)
            if kle__ptaw and kle__ptaw[0].path in [cej__lque, f'{cej__lque}/'
                ] and int(kle__ptaw[0].size or 0) == 0:
                kle__ptaw = kle__ptaw[1:]
            nkwif__njwig = [dyy__txro.base_name for dyy__txro in kle__ptaw]
    except BodoError as nstqw__dtioy:
        raise
    except Exception as jzgcs__lxi:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(jzgcs__lxi).__name__}: {str(jzgcs__lxi)}
{bodo_error_msg}"""
            )
    return nkwif__njwig


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    kmq__tzac = urlparse(path)
    daqc__xii = kmq__tzac.path
    try:
        evs__ncn = HadoopFileSystem.from_uri(path)
    except Exception as jzgcs__lxi:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            jzgcs__lxi))
    czs__slv = evs__ncn.get_file_info([daqc__xii])
    if czs__slv[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not czs__slv[0].size and czs__slv[0].type == FileType.Directory:
        return evs__ncn, True
    return evs__ncn, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    nkwif__njwig = None
    evs__ncn, yik__lpuye = hdfs_is_directory(path)
    if yik__lpuye:
        kmq__tzac = urlparse(path)
        daqc__xii = kmq__tzac.path
        ths__mqjf = FileSelector(daqc__xii, recursive=True)
        try:
            kle__ptaw = evs__ncn.get_file_info(ths__mqjf)
        except Exception as jzgcs__lxi:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(daqc__xii, jzgcs__lxi))
        nkwif__njwig = [dyy__txro.base_name for dyy__txro in kle__ptaw]
    return evs__ncn, nkwif__njwig


def abfs_is_directory(path):
    evs__ncn = get_hdfs_fs(path)
    try:
        czs__slv = evs__ncn.info(path)
    except OSError as nstqw__dtioy:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if czs__slv['size'] == 0 and czs__slv['kind'].lower() == 'directory':
        return evs__ncn, True
    return evs__ncn, False


def abfs_list_dir_fnames(path):
    nkwif__njwig = None
    evs__ncn, yik__lpuye = abfs_is_directory(path)
    if yik__lpuye:
        kmq__tzac = urlparse(path)
        daqc__xii = kmq__tzac.path
        try:
            bhoqz__anhkz = evs__ncn.ls(daqc__xii)
        except Exception as jzgcs__lxi:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(daqc__xii, jzgcs__lxi))
        nkwif__njwig = [fname[fname.rindex('/') + 1:] for fname in bhoqz__anhkz
            ]
    return evs__ncn, nkwif__njwig


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype):
    from urllib.parse import urlparse
    bdo__qduc = urlparse(path)
    fname = path
    fs = None
    xoqi__czrml = 'read_json' if ftype == 'json' else 'read_csv'
    idjbz__wmmf = (
        f'pd.{xoqi__czrml}(): there is no {ftype} file in directory: {fname}')
    cxsa__ltmun = directory_of_files_common_filter
    if bdo__qduc.scheme == 's3':
        iwp__uxhvi = True
        fs = get_s3_fs_from_path(path)
        kdr__wjpky = s3_list_dir_fnames(fs, path)
        cej__lque = (bdo__qduc.netloc + bdo__qduc.path).rstrip('/')
        fname = cej__lque
        if kdr__wjpky:
            kdr__wjpky = [(cej__lque + '/' + rbpzu__xdq) for rbpzu__xdq in
                sorted(filter(cxsa__ltmun, kdr__wjpky))]
            hhj__eys = [rbpzu__xdq for rbpzu__xdq in kdr__wjpky if int(fs.
                get_file_info(rbpzu__xdq).size or 0) > 0]
            if len(hhj__eys) == 0:
                raise BodoError(idjbz__wmmf)
            fname = hhj__eys[0]
        lfot__kaq = int(fs.get_file_info(fname).size or 0)
        aywwd__yvs = fs.open_input_file(fname)
    elif bdo__qduc.scheme == 'hdfs':
        iwp__uxhvi = True
        fs, kdr__wjpky = hdfs_list_dir_fnames(path)
        lfot__kaq = fs.get_file_info([bdo__qduc.path])[0].size
        if kdr__wjpky:
            path = path.rstrip('/')
            kdr__wjpky = [(path + '/' + rbpzu__xdq) for rbpzu__xdq in
                sorted(filter(cxsa__ltmun, kdr__wjpky))]
            hhj__eys = [rbpzu__xdq for rbpzu__xdq in kdr__wjpky if fs.
                get_file_info([urlparse(rbpzu__xdq).path])[0].size > 0]
            if len(hhj__eys) == 0:
                raise BodoError(idjbz__wmmf)
            fname = hhj__eys[0]
            fname = urlparse(fname).path
            lfot__kaq = fs.get_file_info([fname])[0].size
        aywwd__yvs = fs.open_input_file(fname)
    elif bdo__qduc.scheme in ('abfs', 'abfss'):
        iwp__uxhvi = True
        fs, kdr__wjpky = abfs_list_dir_fnames(path)
        lfot__kaq = fs.info(fname)['size']
        if kdr__wjpky:
            path = path.rstrip('/')
            kdr__wjpky = [(path + '/' + rbpzu__xdq) for rbpzu__xdq in
                sorted(filter(cxsa__ltmun, kdr__wjpky))]
            hhj__eys = [rbpzu__xdq for rbpzu__xdq in kdr__wjpky if fs.info(
                rbpzu__xdq)['size'] > 0]
            if len(hhj__eys) == 0:
                raise BodoError(idjbz__wmmf)
            fname = hhj__eys[0]
            lfot__kaq = fs.info(fname)['size']
            fname = urlparse(fname).path
        aywwd__yvs = fs.open(fname, 'rb')
    else:
        if bdo__qduc.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {bdo__qduc.scheme}. Please refer to https://docs.bodo.ai/latest/source/file_io.html'
                )
        iwp__uxhvi = False
        if os.path.isdir(path):
            bhoqz__anhkz = filter(cxsa__ltmun, glob.glob(os.path.join(os.
                path.abspath(path), '*')))
            hhj__eys = [rbpzu__xdq for rbpzu__xdq in sorted(bhoqz__anhkz) if
                os.path.getsize(rbpzu__xdq) > 0]
            if len(hhj__eys) == 0:
                raise BodoError(idjbz__wmmf)
            fname = hhj__eys[0]
        lfot__kaq = os.path.getsize(fname)
        aywwd__yvs = fname
    return iwp__uxhvi, aywwd__yvs, lfot__kaq, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    buzqi__npu = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            dkl__jkpsd, kqm__rxew = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = dkl__jkpsd.region
        except Exception as jzgcs__lxi:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{jzgcs__lxi}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = buzqi__npu.bcast(bucket_loc)
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
        bjkp__msvkn = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        tap__sspzc, bheg__ukc = unicode_to_utf8_and_len(D)
        rxghw__nrf = 0
        if is_parallel:
            rxghw__nrf = bodo.libs.distributed_api.dist_exscan(bheg__ukc,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), tap__sspzc, rxghw__nrf,
            bheg__ukc, is_parallel, unicode_to_utf8(bjkp__msvkn))
        bodo.utils.utils.check_and_propagate_cpp_exception()
    return impl
