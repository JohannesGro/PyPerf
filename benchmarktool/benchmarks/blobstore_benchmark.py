#!demoLauncher.cmd
# -*- coding: iso-8859-1 -*-
import glob
import logging
import os
import time
import sys


from benchmarktool.bench import Bench
from cdb import rte
from cdb.storage import blob
from cs.documents import Document
from benchmarktool.timer import Timer

logger = logging.getLogger("[" + __name__ + " - BlobstoreBenchmark]")


class BlobstoreTiming(Bench):
    """ Die Blob-Daten von der lokalen Platte unter neuen Blob-IDs in
        den Blobstore schreiben. Dieser Vorgang wird mehrmals wiederholt.
        Anschließend diese runterladen.

        Nach dem Lauf die geschriebenen neuen Blobs wieder entfernen.
    """

    def setUPClass(self):
        rte.ensure_run_level(rte.USER_IMPERSONATED, prog="", user="caddok")

    def bench_main(self):
        outfiles = self.prepare()
        all_blob_ids = self.saveFilesIntoBlobStore(outfiles)
        self.downloadBlobs(all_blob_ids)
        self.cleanupBlobs(all_blob_ids)
        logger.debug(self.results)

    def prepare(self):
        logger.info("prepare")
        files = glob.glob(self.args['blobfolder'])
        if files == []:
            raise IOError("Blobs not found")
        return files

    def writeFileToWriter(self, writer, from_path, blocksize=None):
        """ Write the content of a file to ``writer``
        """
        blocksize = blocksize or (256 * 1024)
        with open(from_path, 'rb') as fd:
            while True:
                mybuf = fd.read(blocksize)
                if not mybuf or len(mybuf) == 0:
                    break
                writer.write(mybuf)
        # return the blob_id
        return writer.close()

    def downloadBlobs(self, blob_ids):
        logger.info("downloadBlobs")

        meta_values = []
        blob_values = []
        for i in range(self.args['loops']):
            self.namespace = "(Loops#:{})".format(i)
            time.sleep(10)
            logger.debug("Load file content - %d/%d" % (i + 1, self.args['loops']))

            dlen = 0
            bs = blob.getBlobStore('main')
            blobs_per_loop = len(blob_ids) / self.args['loops']
            start_index = i * blobs_per_loop
            stop_index = start_index + blobs_per_loop
            for blob_id in blob_ids[start_index:stop_index]:

                with Timer() as t_meta:
                    reader = bs.Download(blob_id, only_metadata=True)
                meta_values.append(t_meta.elapsed.total_seconds())
                logger.debug("----> Fetching metadata for blob %s took %.4f secs" % (blob_id, t_meta.elapsed.total_seconds()))
                # could use 'print reader.meta' to have a look at the metadata dictionary
                with Timer() as t_blob:
                    while 1:
                        dummy = reader.read(1024 * 1024)
                        dlen += len(dummy)
                        if not dummy:
                            break
                blob_values.append(t_blob.elapsed.total_seconds())
                logger.debug("----> Fetching data of blob %s ( %d bytes) took %.4f secs. (%.4f KBytes/sec)" % (
                    blob_id, len(reader), t_blob.elapsed.total_seconds(), len(reader) / (t_blob.elapsed.total_seconds() * 1024)))
            self.storeResult(meta_values, name="fetching_metadata", type="time_series")
            self.storeResult(blob_values, name="fetching_blob_data", type="time_series")
        self.namespace = ""

    def saveFilesIntoBlobStore(self, sourcefiles):

        timeWritingBlobs = []

        for fn in sourcefiles:
            if not os.path.isfile(fn):
                raise RuntimeError("Source file %s does not exist" % fn)

        all_blob_ids = []
        for i in xrange(self.args['loops']):
            self.namespace = "(Loop#:{})".format(i)
            logger.debug("saveFilesIntoBlobStore: Starting to write blobs %d/%d" % (i + 1, self.args['loops']))
            dlen = 0
            blob_ids = []
            for fn in sourcefiles:
                size = os.stat(fn).st_size
                with Timer() as t:
                    ul = blob.uploader('main', size, {})
                    blob_id = self.writeFileToWriter(ul, fn)
                dlen += size
                blob_ids.append(blob_id)
                logger.debug("--> Writing of blob %s (%d bytes) took %.4f secs. (%.4f KBytes/sec)"
                             % (blob_id, dlen, t.elapsed.total_seconds(), dlen / ((t.elapsed.total_seconds()) * 1024)))
                # store numFiles, dlen, kb/s ?
                timeWritingBlobs.append(t.elapsed.total_seconds())
                self.storeResult(timeWritingBlobs, type="time_series")
            all_blob_ids.extend(blob_ids)
        self.namespace = ""
        return all_blob_ids

    def cleanupBlobs(self, blob_ids):
        logger.info("Cleanup: Removing %d blobs" % len(blob_ids))
        with Timer() as t:
            bs = blob.getBlobStore('main')
            for blob_id in blob_ids:
                # nuke it completely, do not move to trash area
                bs.delete(blob_id, True)
        logger.debug("-> Deletion of %d blobs took %.4f secs. (%.4f blobs/sec)"
                     % (len(blob_ids), t.elapsed.total_seconds(), (len(blob_ids) / (t.elapsed.total_seconds()))))
        self.storeResult(t.elapsed.total_seconds())

    def cleanupFiles(self, sourcefiles):
        logger.info("Cleanup: Removing %d temporary files" % len(sourcefiles))
        with Timer() as t:
            for fn in sourcefiles:
                os.unlink(fn)
        logger.debug("-> Deletion of %d files took %.4f secs. (%.4f files/sec)"
                     % (len(sourcefiles), t.elapsed.total_seconds(), (len(sourcefiles) / (t.elapsed.total_seconds()))))
        self.storeResult(t.elapsed.total_seconds())


if __name__ == '__main__':
    BlobstoreTiming().run({"loops": 2, "blobfolder": u"./benchmarktool/blobdata/blobs/*"})
