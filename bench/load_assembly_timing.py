#!c:\ce\trunk\sqlite\bin\powerscript.exe
# -*- coding: iso-8859-1 -*-
from optparse import OptionParser
import logging
import time

from cs.documents import Document
import bench

logger = logging.getLogger("[" + __name__ + " - LoadAssemblyTiming]")


class LoadAssemblyTiming(Bench):
    """ Zu einer gegebenen Dokumentnummer die Referenzstruktur ermitteln, und alle
        Hauptdateien aus dem BlobStore laden.
        Die Daten landen nicht auf der Platte, sondern nur im Speicher.
        Es wird dreimal der Dateiinhalt geholt, um Caching-Effekte zu sehen.
    """

    def setUpClass(self):
        logger.info("Get Document %s-%s" % (self.args['z_nummer'], self.args['z_index']))
        self.doc = Document.ByKeys(self.args['z_nummer'], self.args['z_index'])
        if not self.doc:
            logger.error("Document %s-%s not found" % (self.args['z_nummer'], self.args['z_index']))
            exit(1)
            # raise Exception("Document %s-%s not found" % (self.args['z_nummer'], self.args['z_index']))

    def bench_load(self):
        logger.info("bench_load")
        result = {}
        logger.info("Get reference structure")
        t1 = time.time()
        ref_docs = doc.getAllRefDocs()
        t2 = time.time()
        logger.debug("--> Reference structure consists of %d documents, %.4f secs. for query"
                     % (len(ref_docs), t2 - t1))
        result['refDocs'] = {"numDocs": len(ref_docs), "time": {"val": t2 - t1, "unit": "seconds"}}

        logger.info("Get files")
        t1 = time.time()
        file_list = []
        for d in ref_docs:
            file_list.extend(d.PrimaryFiles)
        t2 = time.time()
        logger.debug("--> Documents have %d primary files, %.4f secs. for query"
                     % (len(file_list), t2 - t1))
        result['primaryFiles'] = {"numPrimaryFiles": len(file_list), "time": {"val": t2 - t1, "unit": "seconds"}}

        logger.info("load files")
        loadingFiles = []
        for i in range(self.args['loops']):
            time.sleep(10)
            logger.debug("Load file content - %d/%d" % (i + 1, self.args['loops']))
            t1 = time.time()
            dlen = 0
            bs = blob.getBlobStore('main')
            for f in file_list:
                # reader = f._get_blob_reader(False)
                meta_start = time.time()
                reader = bs.Download(f.cdbf_blob_id, only_metadata=True)
                meta_end = time.time()
                logger.debug("----> Fetching metadata for blob %s took %.4f secs" % (f.cdbf_blob_id, (meta_end - meta_start)))
                result['fetchingMetadata'] = {"blob_id": f.cdbf_blob_id, "time": {"val": meta_end - meta_start, "unit": "seconds"}}
                # could use 'print reader.meta' to have a look at the metadata dictionary
                while 1:
                    dummy = reader.read(1024 * 1024)
                    dlen += len(dummy)
                    if not dummy:
                        break
                meta_data = time.time()
                logger.debug("----> Fetching data of blob %s ( %d bytes) took %.4f secs. (%.4f KBytes/sec)" % (
                    f.cdbf_blob_id, len(reader), (meta_data - meta_end), len(reader) / ((meta_data - meta_end) * 1024)))
                result['fetchingBlobData'] = {"blob_id": f.cdbf_blob_id, "bytes": len(reader), "time": {"val": meta_data - meta_end, "unit": "seconds"}}

            t2 = time.time()
            logger.debug("--> Loading of %d files / %d bytes took %.4f secs. (%.4f KBytes/sec)"
                         % (len(file_list), dlen, t2 - t1, dlen / ((t2 - t1) * 1024)))
            loadingFiles.append({"bytes": dlen, "time": {"val": t2 - t1, "unit": "seconds"}})
        result['loadingFiles'] = loadingFiles
        return result


if __name__ == '__main__':
    LoadAssemblyTiming().run()
