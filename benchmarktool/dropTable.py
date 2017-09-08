from cdb import ddl

tbl  = ddl.Table("x_cdb_testperf",
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
tbl.drop()
