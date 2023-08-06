from urllib.parse import urlparse
import pyarrow.fs as pa_fs
from fsspec import AbstractFileSystem
from pyarrow.fs import S3FileSystem


class PyArrowS3FS(AbstractFileSystem):
    protocol = 's3'

    def __init__(self, *, access_key=None, secret_key=None, session_token=
        None, anonymous=False, region=None, scheme=None, endpoint_override=
        None, background_writes=True, role_arn=None, session_name=None,
        external_id=None, load_frequency=900, proxy_options=None, **kwargs):
        super().__init__(self, **kwargs)
        self.pa_s3fs = S3FileSystem(access_key=access_key, secret_key=
            secret_key, session_token=session_token, anonymous=anonymous,
            region=region, scheme=scheme, endpoint_override=
            endpoint_override, background_writes=background_writes,
            role_arn=role_arn, session_name=session_name, external_id=
            external_id, load_frequency=load_frequency, proxy_options=
            proxy_options)

    def __getattribute__(self, name: str):
        if name == '__class__':
            return PyArrowS3FS
        if name in ['__init__', '__getattribute__', '_open', 'open', 'ls',
            'isdir', 'isfile']:
            return lambda *args, **kw: getattr(PyArrowS3FS, name)(self, *
                args, **kw)
        qbcym__grbcr = object.__getattribute__(self, '__dict__')
        ziuf__lxtrb = qbcym__grbcr.get('pa_s3fs', None)
        if name == 'pa_s3fs':
            return ziuf__lxtrb
        if ziuf__lxtrb is not None and hasattr(ziuf__lxtrb, name):
            return getattr(ziuf__lxtrb, name)
        return super().__getattribute__(name)

    def _open(self, path, mode='rb', block_size=None, autocommit=True,
        cache_options=None, **kwargs):
        iww__djudu = urlparse(path)
        efgr__lewm = iww__djudu.netloc + iww__djudu.path
        return self.pa_s3fs.open_input_file(efgr__lewm)

    def ls(self, path, detail=True, **kwargs):
        iww__djudu = urlparse(path)
        efgr__lewm = (iww__djudu.netloc + iww__djudu.path).rstrip('/')
        gpgu__vbn = pa_fs.FileSelector(efgr__lewm, recursive=False)
        ovi__dvea = self.pa_s3fs.get_file_info(gpgu__vbn)
        if len(ovi__dvea) == 0:
            if self.isfile(path):
                if detail:
                    return [{'type': 'file', 'name': efgr__lewm}]
                else:
                    return [efgr__lewm]
            return []
        if ovi__dvea and ovi__dvea[0].path in [efgr__lewm, f'{efgr__lewm}/'
            ] and int(ovi__dvea[0].size or 0) == 0:
            ovi__dvea = ovi__dvea[1:]
        gjnnz__ooo = []
        if detail:
            for jvaw__ykqi in ovi__dvea:
                rfuoh__fhsmi = {}
                if jvaw__ykqi.type == pa_fs.FileType.Directory:
                    rfuoh__fhsmi['type'] = 'directory'
                elif jvaw__ykqi.type == pa_fs.FileType.File:
                    rfuoh__fhsmi['type'] = 'file'
                else:
                    rfuoh__fhsmi['type'] = 'unknown'
                rfuoh__fhsmi['name'] = jvaw__ykqi.base_name
                gjnnz__ooo.append(rfuoh__fhsmi)
        else:
            gjnnz__ooo = [jvaw__ykqi.base_name for jvaw__ykqi in ovi__dvea]
        return gjnnz__ooo

    def isdir(self, path):
        iww__djudu = urlparse(path)
        efgr__lewm = (iww__djudu.netloc + iww__djudu.path).rstrip('/')
        vwyei__vcqya = self.pa_s3fs.get_file_info(efgr__lewm)
        return (not vwyei__vcqya.size and vwyei__vcqya.type == pa_fs.
            FileType.Directory)

    def isfile(self, path):
        iww__djudu = urlparse(path)
        efgr__lewm = (iww__djudu.netloc + iww__djudu.path).rstrip('/')
        vwyei__vcqya = self.pa_s3fs.get_file_info(efgr__lewm)
        return vwyei__vcqya.type == pa_fs.FileType.File
