#!c:\ce\trunk\sqlite\bin\powerscript.exe
# -*- coding: iso-8859-1 -*-
import logging
from optparse import OptionParser
import os
import time

from cs.documents import Document
from cdb.storage import blob

import bench

logger = logging.getLogger("[" + __name__ + " - WriteAssemblyTiming]")


class WriteAssemblyTiming(Bench):
    """ Zu einer gegebenen Dokumentnummer die Referenzstruktur ermitteln, und alle
        Hauptdateien aus dem BlobStore laden.

        Die Blob-Daten auf der lokalen Platte cachen, dann unter neuen Blob-IDs in
        den Blobstore schreiben.

        Nach dem Lauf die geschriebenen neuen Blobs wieder entfernen.
    """
    def setUpClass(self):
        logger.info("Getting Document %s-%s" % (self.args['z_nummer'], self.args['z_index']))
        doc = Document.ByKeys(self.args['z_nummer'], self.args['z_index'])
        if not doc:
            logger.error("Document %s-%s not found" % (self.args['z_nummer'], self.args['z_index']))
            exit(1)
            # raise Exception("Document %s-%s not found" % (self.args['z_nummer'], self.args['z_index']))

    def bench_prepare(self):
        logger.info("bench_prepare")
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

        logger.info("Load file content")
        t1 = time.time()
        dlen = 0
        filenames = []
        for num, f in enumerate(file_list):
            fpath = os.path.join(self.args['tmpdir'], "blob%d" % num)
            f.checkout_file(fpath)
            dlen += os.stat(fpath).st_size
            filenames.append(fpath)
        t2 = time.time()
        logger.debug("--> Loading of %d files / %d bytes took %.4f secs. (%.4f KBytes/sec)"
                     % (len(file_list), dlen, t2 - t1, dlen / ((t2 - t1) * 1024)))
        result['loadFileContent'] = {"bytes": dlen, "time": {"val": t2 - t1, "unit": "seconds"}}
        result['save'] = save(filenames)
        result['cleanUpFiles'] = cleanup_files(filenames)
        return result

    def write_file_to_bs(self, writer, from_path, blocksize=None):
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

    def save(self, sourcefiles):
        result = {}
        writingBlobs = []

        for fn in sourcefiles:
            if not os.path.isfile(fn):
                raise RuntimeError("Source file %s does not exist" % fn)

        all_blob_ids = []
        for i in xrange(self.args['loops']):
            logger.debug("Save: Starting to write blobs %d/%d" % (i + 1, self.args['loops']))
            t1 = time.time()
            dlen = 0
            blob_ids = []
            for fn in sourcefiles:
                size = os.stat(fn).st_size
                ul = blob.uploader('main', size, {})
                blob_id = write_file_to_bs(ul, fn)
                dlen += size
                blob_ids.append(blob_id)
            t2 = time.time()
            logger.debug("--> Writing of %d files / %d bytes took %.4f secs. (%.4f KBytes/sec)"
                         % (len(blob_ids), dlen, t2 - t1, dlen / ((t2 - t1) * 1024)))
            writingBlobs.append({"numFiles": len(blob_ids), "bytes": dlen, "time": {"val": t2 - t1, "unit": "seconds"}})
            all_blob_ids.extend(blob_ids)

            result["writingBlobs"] = writingBlobs
            result["deletingBlobs"] = cleanup_blobs(all_blob_ids)
        return result

    def cleanup_blobs(self, blob_ids):
        logger.info("Cleanup: Removing %d blobs" % len(blob_ids))
        t1 = time.time()
        bs = blob.getBlobStore('main')
        for blob_id in blob_ids:
            # nuke it completely, do not move to trash area
            bs.delete(blob_id, True)
        t2 = time.time()
        logger.debug("-> Deletion of %d blobs took %.4f secs. (%.4f blobs/sec)"
                     % (len(blob_ids), t2 - t1, (len(blob_ids) / (t2 - t1))))
        return {"numFiles": len(blob_ids), "time": {"val": t2 - t1, "unit": "seconds"}}

    def cleanup_files(self, sourcefiles):
        logger.info("Cleanup: Removing %d temporary files" % len(sourcefiles))
        t1 = time.time()
        for fn in sourcefiles:
            os.unlink(fn)
        t2 = time.time()
        logger.debug("-> Deletion of %d files took %.4f secs. (%.4f files/sec)"
                     % (len(sourcefiles), t2 - t1, (len(sourcefiles) / (t2 - t1))))
        return {"numFiles": len(sourcefiles), "time": {"val": t2 - t1, "unit": "seconds"}}

if __name__ == '__main__':
    WriteAssemblyTiming().run()
