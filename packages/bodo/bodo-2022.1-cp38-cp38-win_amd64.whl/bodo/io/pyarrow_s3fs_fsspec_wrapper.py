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
        zit__edgq = object.__getattribute__(self, '__dict__')
        ssc__vvn = zit__edgq.get('pa_s3fs', None)
        if name == 'pa_s3fs':
            return ssc__vvn
        if ssc__vvn is not None and hasattr(ssc__vvn, name):
            return getattr(ssc__vvn, name)
        return super().__getattribute__(name)

    def _open(self, path, mode='rb', block_size=None, autocommit=True,
        cache_options=None, **kwargs):
        wlepx__kqfco = urlparse(path)
        ldsf__hfk = wlepx__kqfco.netloc + wlepx__kqfco.path
        return self.pa_s3fs.open_input_file(ldsf__hfk)

    def ls(self, path, detail=True, **kwargs):
        wlepx__kqfco = urlparse(path)
        ldsf__hfk = (wlepx__kqfco.netloc + wlepx__kqfco.path).rstrip('/')
        xcvqv__dxy = pa_fs.FileSelector(ldsf__hfk, recursive=False)
        nunxs__mwt = self.pa_s3fs.get_file_info(xcvqv__dxy)
        if len(nunxs__mwt) == 0:
            if self.isfile(path):
                if detail:
                    return [{'type': 'file', 'name': ldsf__hfk}]
                else:
                    return [ldsf__hfk]
            return []
        if nunxs__mwt and nunxs__mwt[0].path in [ldsf__hfk, f'{ldsf__hfk}/'
            ] and int(nunxs__mwt[0].size or 0) == 0:
            nunxs__mwt = nunxs__mwt[1:]
        ryiu__hub = []
        if detail:
            for bozw__msi in nunxs__mwt:
                brsem__nwpep = {}
                if bozw__msi.type == pa_fs.FileType.Directory:
                    brsem__nwpep['type'] = 'directory'
                elif bozw__msi.type == pa_fs.FileType.File:
                    brsem__nwpep['type'] = 'file'
                else:
                    brsem__nwpep['type'] = 'unknown'
                brsem__nwpep['name'] = bozw__msi.base_name
                ryiu__hub.append(brsem__nwpep)
        else:
            ryiu__hub = [bozw__msi.base_name for bozw__msi in nunxs__mwt]
        return ryiu__hub

    def isdir(self, path):
        wlepx__kqfco = urlparse(path)
        ldsf__hfk = (wlepx__kqfco.netloc + wlepx__kqfco.path).rstrip('/')
        qsck__gslcg = self.pa_s3fs.get_file_info(ldsf__hfk)
        return (not qsck__gslcg.size and qsck__gslcg.type == pa_fs.FileType
            .Directory)

    def isfile(self, path):
        wlepx__kqfco = urlparse(path)
        ldsf__hfk = (wlepx__kqfco.netloc + wlepx__kqfco.path).rstrip('/')
        qsck__gslcg = self.pa_s3fs.get_file_info(ldsf__hfk)
        return qsck__gslcg.type == pa_fs.FileType.File
