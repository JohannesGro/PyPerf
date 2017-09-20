#!demoLauncher.cmd
# -*- coding: iso-8859-1 -*-
import logging
import time
import sys

from bench import Bench
from cdb import rte
from cdb.storage import blob
from cs.documents import Document
from timer import Timer

logger = logging.getLogger("[" + __name__ + " - LoadAssemblyTiming]")


class LoadAssemblyTiming(Bench):
    """ Zu einer gegebenen Dokumentnummer die Referenzstruktur ermitteln, und alle
        Hauptdateien aus dem BlobStore laden.
        Die Daten landen nicht auf der Platte, sondern nur im Speicher.
        Es wird dreimal der Dateiinhalt geholt, um Caching-Effekte zu sehen.
    """

    def setUpClass(self):
        rte.ensure_run_level(rte.USER_IMPERSONATED, prog="", user="caddok")
        self.loadDocument(self.args['z_nummer'], self.args['z_index'])

    def loadDocument(self, z_nummer, z_index):
        logger.info("Getting Document %s-%s" % (z_nummer, z_index))
        self.doc = Document.ByKeys(z_nummer, z_index)
        if not self.doc:
            logger.error("Document %s-%s not found" % (z_nummer, z_index))
            raise Exception("Document %s-%s not found" % (z_nummer, z_index))

    def getAllRefDocs(self):
        logger.info("Get reference structure")

        with Timer() as t:
            ref_docs = self.doc.getAllRefDocs()
        self.storeResult(t.elapsed.total_seconds())
        logger.debug("--> Reference structure consists of %d documents, %.4f secs. for query"
                     % (len(ref_docs), t.elapsed.total_seconds()))
        return ref_docs

    def getPrimaryFiles(self, ref_docs):
        logger.info("Get files")
        with Timer() as t:
            file_list = []
            for d in ref_docs:
                file_list.extend(d.PrimaryFiles)
        self.storeResult(t.elapsed.total_seconds())
        logger.debug("--> Documents have %d primary files, %.4f secs. for query"
                     % (len(file_list), t.elapsed.total_seconds()))
        return file_list

    def bench_load(self):
        logger.info("benchLoad")
        ref_docs = self.getAllRefDocs()

        file_list = self.getPrimaryFiles(ref_docs)

        logger.info("load files")
        meta_values = []
        blob_values = []
        for i in range(self.args['loops']):
            time.sleep(10)
            logger.debug("Load file content - %d/%d" % (i + 1, self.args['loops']))

            dlen = 0
            bs = blob.getBlobStore('main')

            for f in file_list:
                with Timer() as t_meta:
                    reader = bs.Download(f.cdbf_blob_id, only_metadata=True)
                meta_values.append(t_meta.elapsed.total_seconds())
                logger.debug("----> Fetching metadata for blob %s took %.4f secs" % (f.cdbf_blob_id, t_meta.elapsed.total_seconds()))
                # could use 'print reader.meta' to have a look at the metadata dictionary
                with Timer() as t_blob:
                    while 1:
                        dummy = reader.read(1024 * 1024)
                        dlen += len(dummy)
                        if not dummy:
                            break
                blob_values.append(t_blob.elapsed.total_seconds())
                logger.debug("----> Fetching data of blob %s ( %d bytes) took %.4f secs. (%.4f KBytes/sec)" % (
                    f.cdbf_blob_id, len(reader), t_blob.elapsed.total_seconds(), len(reader) / (t_blob.elapsed.total_seconds() * 1024)))
        self.storeResult(meta_values, name="fetching_metadata", type="time_series")
        self.storeResult(blob_values, name="fetching_blob_data", type="time_series")


if __name__ == '__main__':
    print LoadAssemblyTiming().run({"z_nummer": "000073-1", "z_index": "", "loops": 10})
