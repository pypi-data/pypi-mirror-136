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
    except Exception as jbv__celkr:
        raise ImportError(
            "Bodo Error: please pip install the 'deltalake' package to read parquet from delta lake"
            )
    eqj__jzp = None
    ycj__pas = delta_lake_path.rstrip('/')
    qwyc__fpwe = 'AWS_DEFAULT_REGION' in os.environ
    xrv__cnpm = os.environ.get('AWS_DEFAULT_REGION', '')
    hxwuw__akr = False
    if delta_lake_path.startswith('s3://'):
        smd__vak = get_s3_bucket_region_njit(delta_lake_path, parallel=False)
        if smd__vak != '':
            os.environ['AWS_DEFAULT_REGION'] = smd__vak
            hxwuw__akr = True
    mmmau__slbiv = DeltaTable(delta_lake_path)
    eqj__jzp = mmmau__slbiv.files()
    eqj__jzp = [(ycj__pas + '/' + vdl__jnr) for vdl__jnr in sorted(eqj__jzp)]
    if hxwuw__akr:
        if qwyc__fpwe:
            os.environ['AWS_DEFAULT_REGION'] = xrv__cnpm
        else:
            del os.environ['AWS_DEFAULT_REGION']
    return eqj__jzp


def get_dataset_schema(dataset):
    if dataset.metadata is None and dataset.schema is None:
        if dataset.common_metadata is not None:
            dataset.schema = dataset.common_metadata.schema
        else:
            dataset.schema = dataset.pieces[0].get_metadata().schema
    elif dataset.schema is None:
        dataset.schema = dataset.metadata.schema
    hmgqr__npx = dataset.schema.to_arrow_schema()
    if dataset.partitions is not None:
        for ondy__agxb in dataset.partitions.partition_names:
            if hmgqr__npx.get_field_index(ondy__agxb) != -1:
                air__dqzqh = hmgqr__npx.get_field_index(ondy__agxb)
                hmgqr__npx = hmgqr__npx.remove(air__dqzqh)
    return hmgqr__npx


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
        except Exception as jbv__celkr:
            self.exc = jbv__celkr
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
        nqadi__sho = VisitLevelThread(self)
        nqadi__sho.start()
        nqadi__sho.join()
        for lxw__cthyy in self.partition_vals.keys():
            self.partition_vals[lxw__cthyy] = sorted(self.partition_vals[
                lxw__cthyy])
        for wgrio__szk in self.partitions.levels:
            wgrio__szk.keys = sorted(wgrio__szk.keys)
        for oyrx__xrvh in self.pieces:
            if oyrx__xrvh.partition_keys is not None:
                oyrx__xrvh.partition_keys = [(qlxvn__hzdx, self.
                    partition_vals[qlxvn__hzdx].index(bljl__ewcyy)) for 
                    qlxvn__hzdx, bljl__ewcyy in oyrx__xrvh.partition_keys]
        self.pieces.sort(key=lambda piece: piece.path)
        if self.common_metadata_path is None:
            self.common_metadata_path = self.metadata_path
        self._thread_pool.shutdown()

    async def _visit_level(self, wmbm__xsfn, base_path, vleb__abrxt):
        fs = self.filesystem
        mvbb__wdf, zen__hwaj, tykyk__syxxc = await self.loop.run_in_executor(
            self._thread_pool, lambda fs, base_bath: next(fs.walk(base_path
            )), fs, base_path)
        if wmbm__xsfn == 0 and '_delta_log' in zen__hwaj:
            self.delta_lake_filter = set(get_parquet_filesnames_from_deltalake
                (base_path))
        wazps__ppwpu = []
        for ycj__pas in tykyk__syxxc:
            if ycj__pas == '':
                continue
            lox__gwn = self.pathsep.join((base_path, ycj__pas))
            if ycj__pas.endswith('_common_metadata'):
                self.common_metadata_path = lox__gwn
            elif ycj__pas.endswith('_metadata'):
                self.metadata_path = lox__gwn
            elif self._should_silently_exclude(ycj__pas):
                continue
            elif self.delta_lake_filter and lox__gwn not in self.delta_lake_filter:
                continue
            else:
                wazps__ppwpu.append(lox__gwn)
        puayz__cyf = [self.pathsep.join((base_path, ilbd__vqhk)) for
            ilbd__vqhk in zen__hwaj if not pq._is_private_directory(ilbd__vqhk)
            ]
        wazps__ppwpu.sort()
        puayz__cyf.sort()
        if len(wazps__ppwpu) > 0 and len(puayz__cyf) > 0:
            raise ValueError('Found files in an intermediate directory: {}'
                .format(base_path))
        elif len(puayz__cyf) > 0:
            await self._visit_directories(wmbm__xsfn, puayz__cyf, vleb__abrxt)
        else:
            self._push_pieces(wazps__ppwpu, vleb__abrxt)

    async def _visit_directories(self, wmbm__xsfn, zen__hwaj, vleb__abrxt):
        smmu__ibf = []
        for ycj__pas in zen__hwaj:
            nno__ucbqk, vpxga__wcolx = pq._path_split(ycj__pas, self.pathsep)
            qlxvn__hzdx, undn__lto = pq._parse_hive_partition(vpxga__wcolx)
            lfdh__trjy = self.partitions.get_index(wmbm__xsfn, qlxvn__hzdx,
                undn__lto)
            self.partition_vals[qlxvn__hzdx].add(undn__lto)
            zqr__yieom = vleb__abrxt + [(qlxvn__hzdx, undn__lto)]
            smmu__ibf.append(self._visit_level(wmbm__xsfn + 1, ycj__pas,
                zqr__yieom))
        await asyncio.wait(smmu__ibf)


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
