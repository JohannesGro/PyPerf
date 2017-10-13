#!demoLauncher.cmd
# -*- coding: iso-8859-1 -*-
import logging
import os
import sys
import time

from benchmarktool.bench import Bench
from benchmarktool.timer import Timer
from cdb import rte
from cdb.storage import blob
from cs.documents import Document

logger = logging.getLogger("[" + __name__ + " - WriteAssemblyTiming]")


class WriteAssemblyTiming(Bench):
    """ Zu einer gegebenen Dokumentnummer die Referenzstruktur ermitteln, und alle
        Hauptdateien aus dem BlobStore laden.

        Die Blob-Daten auf der lokalen Platte cachen, dann unter neuen Blob-IDs in
        den Blobstore schreiben.

        Nach dem Lauf die geschriebenen neuen Blobs wieder entfernen.
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

    def bench_main(self):
        outfiles = self.prepare()
        all_blob_ids = self.saveFilesIntoBlobStore(outfiles)
        self.cleanupBlobs(all_blob_ids)
        self.cleanupFiles(outfiles)

    def getAllRefDocs(self):
        logger.info("Get reference structure")

        with Timer() as t:
            ref_docs = self.doc.getAllRefDocs()
        self.storeResult(t.elapsed.total_seconds(), name="Get all doc. refs.")
        logger.debug("--> Reference structure consists of %d documents, %.4f secs. for query"
                     % (len(ref_docs), t.elapsed.total_seconds()))
        return ref_docs

    def getPrimaryFiles(self, ref_docs):
        logger.info("Get files")
        with Timer() as t:
            file_list = []
            for d in ref_docs:
                file_list.extend(d.PrimaryFiles)
        self.storeResult(t.elapsed.total_seconds(), name="Get primary files")
        logger.debug("--> Documents have %d primary files, %.4f secs. for query"
                     % (len(file_list), t.elapsed.total_seconds()))
        return file_list

    def loadFileContent(self, file_list):
        logger.info("Load file content")
        if not os.path.exists(self.args['tmpdir']):
            os.makedirs(self.args['tmpdir'])
        with Timer() as t:
            dlen = 0
            filenames = []
            for num, f in enumerate(file_list):
                fpath = os.path.join(self.args['tmpdir'], "blob%d" % num)
                f.checkout_file(fpath)
                dlen += os.stat(fpath).st_size
                filenames.append(fpath)

        logger.debug("--> Loading of %d files / %d bytes took %.4f secs. (%.4f KBytes/sec)"
                     % (len(file_list), dlen, t.elapsed.total_seconds(), dlen / ((t.elapsed.total_seconds()) * 1024)))
        # store dlen or kb/s ?
        self.storeResult(t.elapsed.total_seconds(), name="Load file content")
        return filenames

    def prepare(self):
        logger.info("bench_prepare")

        ref_docs = self.getAllRefDocs()

        file_list = self.getPrimaryFiles(ref_docs)

        filenames = self.loadFileContent(file_list)

        return filenames

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

    def saveFilesIntoBlobStore(self, sourcefiles):

        timeWritingBlobs = []

        for fn in sourcefiles:
            if not os.path.isfile(fn):
                raise RuntimeError("Source file %s does not exist" % fn)

        all_blob_ids = []
        for i in xrange(self.args['loops']):
            logger.debug("saveFilesIntoBlobStore: Starting to write blobs %d/%d" % (i + 1, self.args['loops']))
            with Timer() as t:
                dlen = 0
                blob_ids = []
                for fn in sourcefiles:
                    size = os.stat(fn).st_size
                    ul = blob.uploader('main', size, {})
                    blob_id = self.writeFileToWriter(ul, fn)
                    dlen += size
                    blob_ids.append(blob_id)
            logger.debug("--> Writing of %d files / %d bytes took %.4f secs. (%.4f KBytes/sec)"
                         % (len(blob_ids), dlen, t.elapsed.total_seconds(), dlen / ((t.elapsed.total_seconds()) * 1024)))
            # store numFiles, dlen, kb/s ?
            timeWritingBlobs.append(t.elapsed.total_seconds())
            all_blob_ids.extend(blob_ids)
        self.storeResult(timeWritingBlobs, type="time_series", name="Save files into blobstore")
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
        self.storeResult(t.elapsed.total_seconds(), name="Clean up blobs")

    def cleanupFiles(self, sourcefiles):
        logger.info("Cleanup: Removing %d temporary files" % len(sourcefiles))
        with Timer() as t:
            for fn in sourcefiles:
                os.unlink(fn)
        logger.debug("-> Deletion of %d files took %.4f secs. (%.4f files/sec)"
                     % (len(sourcefiles), t.elapsed.total_seconds(), (len(sourcefiles) / (t.elapsed.total_seconds()))))
        self.storeResult(t.elapsed.total_seconds(), name="clean up files")
        os.rmdir(self.args['tmpdir'])

if __name__ == '__main__':
    print WriteAssemblyTiming().run({"z_nummer": "9502656-1", "z_index": "", "loops": 3,
                                    "tmpdir": u"tmpDir"})
