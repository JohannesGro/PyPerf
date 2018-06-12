#!c:\csall\trunk\sqlite\bin\powerscript.exe
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""Measure insert and select performance via CONTACT Elements sqlapi

An new independent Table will be created and filled with n Records. Afterwards,
all Records will be read at once, and then they will be read row by row.
"""

import collections
import logging
import sys
import time
from random import choice
from string import lowercase

from pyperf.bench import Bench
from pyperf.timer import Timer
from cdb import cdbtime, ddl, misc, rte, sqlapi, transaction

logger = logging.getLogger("[" + __name__ + " - SqlApiBenchmark]")


class SqlApiBenchmark(Bench):
    """

    """
    def setUpClass(self):
        rte.ensure_run_level(rte.USER_IMPERSONATED, prog="", user="caddok")
        self.warmup(self.args['tablename'])
        self.create_table(self.args['tablename'])

    def tearDownClass(self):
        self.cleanup(self.args['tablename'])

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def tabledef(self, name):
        # Use a wide table, so we use a copy of zeichung
        return ddl.Table(name,
                         ddl.Char("z_nummer", 20, 1),
                         ddl.Char("z_index", 10, 1),
                         ddl.Char("teilenummer", 20),
                         ddl.Char("t_index", 10),
                         ddl.Integer("z_status"),
                         ddl.Char("z_status_txt", 64),
                         ddl.Char("z_art", 64),
                         ddl.Char("z_bemerkung", 80),
                         ddl.Char("erzeug_system", 64),
                         ddl.Char("blattnr", 5),
                         ddl.Char("z_format", 20),
                         ddl.Char("z_format_gruppe", 20),
                         ddl.Char("massstab", 15),
                         ddl.Char("zeichner", 64),
                         ddl.Date("anlegetag"),
                         ddl.Char("ersatz_fuer", 20),
                         ddl.Char("pruefer", 64),
                         ddl.Date("pruef_datum"),
                         ddl.Char("norm_pruefer", 20),
                         ddl.Char("dateiname", 128),
                         ddl.Char("auftragsnr", 10),
                         ddl.Char("ersatz_durch", 20),
                         ddl.Char("ursprungs_z", 40),
                         ddl.Char("z_band", 20),
                         ddl.Char("verteiler", 20),
                         ddl.Char("cdb_aacl_entry", 20),
                         ddl.Integer("schriftkopf_ok"),
                         ddl.Integer("vorlagen_kz"),
                         ddl.Integer("share_status"),
                         ddl.Char("blattanz", 5),
                         ddl.Char("cad_release", 15),
                         ddl.Char("ident", 20),
                         ddl.Char("cdb_lock", 20),
                         ddl.Char("cdb_cpersno", 20),
                         ddl.Date("cdb_cdate"),
                         ddl.Char("cdb_mpersno", 20),
                         ddl.Date("cdb_mdate"),
                         ddl.Char("cdb_m2persno", 20),
                         ddl.Date("cdb_m2date"),
                         ddl.Char("titel", 80),
                         ddl.Char("keywords", 80),
                         ddl.Char("autoren", 255),
                         ddl.Char("z_bereich", 20),
                         ddl.Char("src_name", 40),
                         ddl.Date("src_cdate"),
                         ddl.Date("src_rdate"),
                         ddl.Char("src_fname", 100),
                         ddl.Char("src_number", 40),
                         ddl.Char("src_index", 10),
                         ddl.Char("cdb_project_id", 20),
                         ddl.Char("z_categ1", 20),
                         ddl.Char("z_categ2", 20),
                         ddl.Char("z_language", 10),
                         ddl.Char("cdb_ec_id", 20),
                         ddl.Char("wsp_filename", 255),
                         ddl.Integer("cdb_obsolete"),
                         ddl.Char("wsp_lock_id", 64),
                         ddl.Char("cdb_object_id", 40, 1),
                         ddl.Char("cdb_classname", 32),
                         ddl.Char("bom_method", 64),
                         ddl.Char("wsm_is_cad", 1, default="'0'"),
                         ddl.Integer("standard_library"),
                         ddl.Char("generated_from", 255),
                         ddl.PrimaryKey('z_nummer', 'z_index'))

    def create_table(self, name):
        """ Create the tables holding the data related to the migration.
        """
        logger.info("Create table '%s'", name)
        with Timer() as t:
            try:
                tbl = self.tabledef(name)
                if tbl.exists():
                    raise RuntimeError("Table '%s' already exists" % name)
                logger.debug("Test Table Definition:\n%s", tbl.stmt())
                tbl.create()
            except Exception as exc:
                logger.exception("Error while creating table '%s': %s", name, exc)
                raise
        self.storeResult(t.elapsed.total_seconds(), name="Create Table")

    def cleanup(self, name):
        """ Delete the tables holding the data related to the migration.
        """
        tbl = self.tabledef(name)
        if tbl.exists():
            tbl.drop()
            logger.debug("Table dropped  '%s'", tbl.name)

    def do_single_insert(self, table, rec):
        sqlapi.SQLinsert("into %s" % table
                         + """
        (z_nummer, z_index, teilenummer, t_index, z_status, z_status_txt, z_art,
        z_bemerkung, erzeug_system, blattnr, z_format,
        z_format_gruppe, massstab, zeichner, anlegetag,
        ersatz_fuer, pruefer, pruef_datum, norm_pruefer, dateiname,
        auftragsnr, ersatz_durch, ursprungs_z, z_band, verteiler,
        cdb_aacl_entry, schriftkopf_ok, vorlagen_kz, share_status,
        blattanz, cad_release, ident, cdb_lock, cdb_cpersno,
        cdb_cdate, cdb_mpersno, cdb_mdate, cdb_m2persno,
        cdb_m2date, titel, keywords, autoren, z_bereich, src_name,
        src_cdate, src_rdate, src_fname, src_number, src_index,
        cdb_project_id, z_categ1, z_categ2, z_language, cdb_ec_id,
        wsp_filename, cdb_obsolete, wsp_lock_id, cdb_object_id,
        cdb_classname, bom_method, wsm_is_cad, standard_library,
        generated_from) VALUES (
        %(z_nummer)s, %(z_index)s, %(teilenummer)s, %(t_index)s, %(z_status)s,
        %(z_status_txt)s, %(z_art)s, %(z_bemerkung)s, %(erzeug_system)s,
        %(blattnr)s, %(z_format)s, %(z_format_gruppe)s, %(massstab)s,
        %(zeichner)s, %(anlegetag)s, %(ersatz_fuer)s, %(pruefer)s,
        %(pruef_datum)s, %(norm_pruefer)s, %(dateiname)s, %(auftragsnr)s,
        %(ersatz_durch)s, %(ursprungs_z)s, %(z_band)s, %(verteiler)s,
        %(cdb_aacl_entry)s, %(schriftkopf_ok)s, %(vorlagen_kz)s, %(share_status)s,
        %(blattanz)s, %(cad_release)s, %(ident)s, %(cdb_lock)s, %(cdb_cpersno)s,
        %(cdb_cdate)s, %(cdb_mpersno)s, %(cdb_mdate)s, %(cdb_m2persno)s,
        %(cdb_m2date)s, %(titel)s, %(keywords)s, %(autoren)s, %(z_bereich)s,
        %(src_name)s, %(src_cdate)s, %(src_rdate)s, %(src_fname)s, %(src_number)s,
        %(src_index)s, %(cdb_project_id)s, %(z_categ1)s, %(z_categ2)s,
        %(z_language)s, %(cdb_ec_id)s, %(wsp_filename)s, %(cdb_obsolete)s,
        %(wsp_lock_id)s, %(cdb_object_id)s, %(cdb_classname)s, %(bom_method)s,
        %(wsm_is_cad)s, %(standard_library)s, %(generated_from)s)""" % rec)

    def do_inserts(self, rows, table):
        def _quote(val):
            return "'%s'" % val
        logger.info("\nCreating %d Records", rows)
        rec = collections.defaultdict(lambda: _quote(""))
        rec["z_status"] = 10
        rec["z_status_txt"] = _quote("in Arbeit")
        rec["z_bemerkung"] = _quote(80 * "#")
        rec["erzeug_system"] = _quote("Papier")
        rec["massstab"] = _quote("A0")
        rec["zeichner"] = _quote("caddok")
        rec["anlegetag"] = sqlapi.SQLdbms_date(cdbtime.localtime())
        rec["pruefer"] = _quote("caddok")
        rec["pruef_datum"] = sqlapi.SQLdbms_date(cdbtime.localtime())
        rec["norm_pruefer"] = _quote("pruefer")
        rec["dateiname"] = _quote("c:/temp/foo")
        rec["vorlagen_kz"] = 1
        rec["share_status"] = 10
        rec["blattanz"] = _quote("1")
        rec["cad_release"] = _quote("17.2")
        rec["cdb_lock"] = _quote("1")
        rec["cdb_cpersno"] = _quote("caddok")
        rec["cdb_cdate"] = sqlapi.SQLdbms_date(cdbtime.localtime())
        rec["cdb_mpersno"] = _quote("caddok")
        rec["cdb_mdate"] = sqlapi.SQLdbms_date(cdbtime.localtime())
        rec["cdb_m2persno"] = _quote("caddok")
        rec["cdb_m2date"] = sqlapi.SQLdbms_date(cdbtime.localtime())
        rec["titel"] = _quote(5 * "Ein Titel ")
        rec["keywords"] = _quote("Key words are mostly used as tags")
        rec["autoren"] = _quote("caddok, koddac")
        rec["src_name"] = _quote("D000001.pdf")
        rec["src_cdate"] = sqlapi.SQLdbms_date(cdbtime.localtime())
        rec["src_rdate"] = sqlapi.SQLdbms_date(cdbtime.localtime())
        rec["src_fname"] = _quote("ein anderer Pfad koennte hier stehen")
        rec["cdb_obsolete"] = 0
        rec["cdb_object_id"] = _quote(misc.UUID(1))
        rec["standard_library"] = 0
        rec["schriftkopf_ok"] = 1

        res = []
        for i in range(rows):
            rec["z_nummer"] = _quote("%d" % i)
            # rec["z_index"] = _quote("%d" % i)
            with Timer() as t:
                self.do_single_insert(table, rec)
            res.append(t.elapsed.total_seconds())
        # logger.info(u"Stmts / second: %.2f stmts", rows / t.elapsed.total_seconds())
        self.storeResult(res, type="time_series", name="Inserts")

    def do_select_one_by_one(self, rows, table):
        logger.info("\nSelect row by row for %d rows", rows)
        res = []
        for i in range(rows):
            with Timer() as t:
                sqlapi.SQLselect("* from %s where z_nummer='%d'" % (table, i))
            res.append(t.elapsed.total_seconds())
        # logger.info(u"Stmts / second: %.2f stmts", rows / t.elapsed.total_seconds())
        self.storeResult(res, type="time_series", name="Selects")

    def do_select_in_one_statement(self, table):
        logger.info("\nGet all with one statement")
        with Timer() as t:
            sqlapi.SQLselect("* from %s" % table)
        self.storeResult(t.elapsed.total_seconds(), name="Select all statement")

    def do_PKs_select_in_one_statement(self, table):
        logger.info("\nGet all PKs with one statement")
        with Timer() as t:
            sqlapi.SQLselect("z_nummer, z_index from %s" % table)
        self.storeResult(t.elapsed.total_seconds(), name="Select all PKs statement")

    def update_one_by_one(self, rows, table):
        logger.info("\nUpdate row by row for %d rows", rows)
        res = []
        for i in range(rows):
            with Timer() as t:
                sqlapi.SQLupdate("%s set z_status=20 where z_nummer='%d'"
                                 % (table, i))
            res.append(t.elapsed.total_seconds())
        # logger.info(u"Stmts / second: %.2f stmts", rows / t.elapsed.total_seconds())
        self.storeResult(res, type="time_series", name="Updates")

    def warmup(self, table, cycles=10):
        """Do some warmup, to avoid flickering from cold FS caches
        """
        logger.info("Warming up")
        prevlog = logger.level
        logger.setLevel(logging.ERROR)
        self.namespace = "warmup_"
        with Timer() as t:
            for i in range(cycles):
                self.create_table(table)
                self.test_run(table, self.args["warmup"])
                self.cleanup(table)
        self.discard(self.namespace)
        self.namespace = ""
        self.storeResult(t.elapsed.total_seconds(), name="Warmup")
        logger.setLevel(prevlog)

    def test_run(self, table, rows):
        self.do_inserts(rows, table)
        self.update_one_by_one(rows, table)
        self.do_PKs_select_in_one_statement(table)
        self.do_select_in_one_statement(table)
        self.do_select_one_by_one(rows, table)
        self.select_cdbkeys(rows / 10)
        self.nope_statement(rows)

    def bench_main(self):
        logger.info("Bench_main")
        res = self.test_run(self.args['tablename'], self.args['rows'])

    def select_cdbkeys(self, rows):
        """cdb_keys is a view based on system tables/views and through some
         circumstances this view is sometimes very slow."""
        logger.info("\nselect %d times from cdb_keys" % rows)
        with Timer() as t:
            for i in range(rows):
                sqlapi.SQLselect("table_name, column_name FROM cdb_keys ORDER BY table_name, keyno")
        logger.info("Stmts / second: %.2f stmts", rows / t.elapsed.total_seconds())
        self.storeResult(t.elapsed.total_seconds(), name="Select cdbKeys")

    def nope_statement(self, rows):
        logger.info("\nRun a nope SQL statement, %d times", rows)
        if sqlapi.SQLdbms() == sqlapi.DBMS_SQLITE:
            logger.info("\nSkipped with SQLite")
            return
        with transaction.Transaction():
            if sqlapi.SQLdbms() == sqlapi.DBMS_MSSQL:
                # Because of weired tx handling we need at least one real select
                # stmt with mssql
                sqlapi.SQL("select 1 from angestellter where 1=2")
            with Timer() as t:
                for i in range(rows):
                    if sqlapi.SQLdbms() == sqlapi.DBMS_ORACLE:
                        sqlapi.SQLselect("1 from DUAL")
                    elif sqlapi.SQLdbms() == sqlapi.DBMS_MSSQL:
                            sqlapi.SQLselect("1")
        logger.info("Stmts / second: %.2f stmts", rows / t.elapsed.total_seconds())
        self.storeResult(t.elapsed.total_seconds(), name="Nope statement")

if __name__ == "__main__":
    print(SqlApiBenchmark().run({"rows": 1000, "iterations": 10, "tablename": "x_cdb_testperf", "warmup": 100}))
