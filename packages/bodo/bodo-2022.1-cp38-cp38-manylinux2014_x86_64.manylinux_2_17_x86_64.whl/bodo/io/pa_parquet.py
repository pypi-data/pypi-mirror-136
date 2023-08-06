import asyncio
import os
import threading
from collections import defaultdict
from concurrent import futures
import pyarrow.parquet as pq
from bodo.io.fs_io import get_s3_bucket_region_njit


def get_parquet_filesnames_from_deltalake(delta_lake_path):
    try:
        from deltalake import DeltaTable
    except Exception as zyics__csyuw:
        raise ImportError(
            "Bodo Error: please pip install the 'deltalake' package to read parquet from delta lake"
            )
    inh__tvyi = None
    vgmrh__mreor = delta_lake_path.rstrip('/')
    ldg__tlquc = 'AWS_DEFAULT_REGION' in os.environ
    wcj__gsc = os.environ.get('AWS_DEFAULT_REGION', '')
    sus__dudkw = False
    if delta_lake_path.startswith('s3://'):
        hqo__nojqs = get_s3_bucket_region_njit(delta_lake_path, parallel=False)
        if hqo__nojqs != '':
            os.environ['AWS_DEFAULT_REGION'] = hqo__nojqs
            sus__dudkw = True
    impd__rsv = DeltaTable(delta_lake_path)
    inh__tvyi = impd__rsv.files()
    inh__tvyi = [(vgmrh__mreor + '/' + pdgw__qrut) for pdgw__qrut in sorted
        (inh__tvyi)]
    if sus__dudkw:
        if ldg__tlquc:
            os.environ['AWS_DEFAULT_REGION'] = wcj__gsc
        else:
            del os.environ['AWS_DEFAULT_REGION']
    return inh__tvyi


def get_dataset_schema(dataset):
    if dataset.metadata is None and dataset.schema is None:
        if dataset.common_metadata is not None:
            dataset.schema = dataset.common_metadata.schema
        else:
            dataset.schema = dataset.pieces[0].get_metadata().schema
    elif dataset.schema is None:
        dataset.schema = dataset.metadata.schema
    fzd__rrlb = dataset.schema.to_arrow_schema()
    if dataset.partitions is not None:
        for eutsl__xje in dataset.partitions.partition_names:
            if fzd__rrlb.get_field_index(eutsl__xje) != -1:
                tdoqe__wefj = fzd__rrlb.get_field_index(eutsl__xje)
                fzd__rrlb = fzd__rrlb.remove(tdoqe__wefj)
    return fzd__rrlb


class VisitLevelThread(threading.Thread):

    def __init__(self, manifest):
        threading.Thread.__init__(self)
        self.manifest = manifest
        self.exc = None

    def run(self):
        try:
            manifest = self.manifest
            manifest.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(manifest.loop)
            manifest.loop.run_until_complete(manifest._visit_level(0,
                manifest.dirpath, []))
        except Exception as zyics__csyuw:
            self.exc = zyics__csyuw
        finally:
            if hasattr(manifest, 'loop') and not manifest.loop.is_closed():
                manifest.loop.close()

    def join(self):
        super(VisitLevelThread, self).join()
        if self.exc:
            raise self.exc


class ParquetManifest:

    def __init__(self, dirpath, open_file_func=None, filesystem=None,
        pathsep='/', partition_scheme='hive', metadata_nthreads=1):
        filesystem, dirpath = pq._get_filesystem_and_path(filesystem, dirpath)
        self.filesystem = filesystem
        self.open_file_func = open_file_func
        self.pathsep = pathsep
        self.dirpath = pq._stringify_path(dirpath)
        self.partition_scheme = partition_scheme
        self.partitions = pq.ParquetPartitions()
        self.pieces = []
        self._metadata_nthreads = metadata_nthreads
        self._thread_pool = futures.ThreadPoolExecutor(max_workers=
            metadata_nthreads)
        self.common_metadata_path = None
        self.metadata_path = None
        self.delta_lake_filter = set()
        self.partition_vals = defaultdict(set)
        wfni__hapa = VisitLevelThread(self)
        wfni__hapa.start()
        wfni__hapa.join()
        for fyrbk__dpov in self.partition_vals.keys():
            self.partition_vals[fyrbk__dpov] = sorted(self.partition_vals[
                fyrbk__dpov])
        for uxmz__dbt in self.partitions.levels:
            uxmz__dbt.keys = sorted(uxmz__dbt.keys)
        for zrvn__ismf in self.pieces:
            if zrvn__ismf.partition_keys is not None:
                zrvn__ismf.partition_keys = [(tnv__xsca, self.
                    partition_vals[tnv__xsca].index(zhidw__mxgu)) for 
                    tnv__xsca, zhidw__mxgu in zrvn__ismf.partition_keys]
        self.pieces.sort(key=lambda piece: piece.path)
        if self.common_metadata_path is None:
            self.common_metadata_path = self.metadata_path
        self._thread_pool.shutdown()

    async def _visit_level(self, qosjv__iipk, base_path, dufzq__memx):
        fs = self.filesystem
        vwh__lui, vqqs__acrkz, wozpm__qfs = await self.loop.run_in_executor(
            self._thread_pool, lambda fs, base_bath: next(fs.walk(base_path
            )), fs, base_path)
        if qosjv__iipk == 0 and '_delta_log' in vqqs__acrkz:
            self.delta_lake_filter = set(get_parquet_filesnames_from_deltalake
                (base_path))
        hli__sclwj = []
        for vgmrh__mreor in wozpm__qfs:
            if vgmrh__mreor == '':
                continue
            pcbi__tsmlj = self.pathsep.join((base_path, vgmrh__mreor))
            if vgmrh__mreor.endswith('_common_metadata'):
                self.common_metadata_path = pcbi__tsmlj
            elif vgmrh__mreor.endswith('_metadata'):
                self.metadata_path = pcbi__tsmlj
            elif self._should_silently_exclude(vgmrh__mreor):
                continue
            elif self.delta_lake_filter and pcbi__tsmlj not in self.delta_lake_filter:
                continue
            else:
                hli__sclwj.append(pcbi__tsmlj)
        pneys__qvmi = [self.pathsep.join((base_path, odxx__klp)) for
            odxx__klp in vqqs__acrkz if not pq._is_private_directory(odxx__klp)
            ]
        hli__sclwj.sort()
        pneys__qvmi.sort()
        if len(hli__sclwj) > 0 and len(pneys__qvmi) > 0:
            raise ValueError('Found files in an intermediate directory: {}'
                .format(base_path))
        elif len(pneys__qvmi) > 0:
            await self._visit_directories(qosjv__iipk, pneys__qvmi, dufzq__memx
                )
        else:
            self._push_pieces(hli__sclwj, dufzq__memx)

    async def _visit_directories(self, qosjv__iipk, vqqs__acrkz, dufzq__memx):
        nwksc__usdk = []
        for vgmrh__mreor in vqqs__acrkz:
            dhq__raz, gkl__naee = pq._path_split(vgmrh__mreor, self.pathsep)
            tnv__xsca, emj__vbzw = pq._parse_hive_partition(gkl__naee)
            psv__ykr = self.partitions.get_index(qosjv__iipk, tnv__xsca,
                emj__vbzw)
            self.partition_vals[tnv__xsca].add(emj__vbzw)
            hfula__qiql = dufzq__memx + [(tnv__xsca, emj__vbzw)]
            nwksc__usdk.append(self._visit_level(qosjv__iipk + 1,
                vgmrh__mreor, hfula__qiql))
        await asyncio.wait(nwksc__usdk)


ParquetManifest._should_silently_exclude = (pq.ParquetManifest.
    _should_silently_exclude)
ParquetManifest._parse_partition = pq.ParquetManifest._parse_partition
ParquetManifest._push_pieces = pq.ParquetManifest._push_pieces
pq.ParquetManifest = ParquetManifest


def pieces(self):
    return self._pieces


pq.ParquetDataset.pieces = property(pieces)


def partitions(self):
    return self._partitions


pq.ParquetDataset.partitions = property(partitions)
