import configparser
import os
from partdb import *
from datetime import datetime


###############################
###   Config File Reading   ###
###############################

class Singleton(object):
    instances = {}

    def __init__(self, cls):
        self.__dict__['cls'] = cls

    def __call__(self):
        if self.cls not in self.instances:
            self.instances[self.cls] = self.cls()
        return self.instances[self.cls]

    def __getattr__(self, attr):
        return getattr(self.__dict__['cls'], attr)

    def __setattr__(self, attr, value):
        return setattr(self.__dict__['cls'], attr, value)


@Singleton
class Config:
    CFG_ENV_VAR = "PARTLOCATER_CFG"
    MAP_FILENAME = "../assets/map.cfg"
    TS_FORMAT = "%d/%m/%y %H:%M:%S "
    REVISION = "v1.0.1-beta"

    def __init__(self):
        self.loaded_db = None
        self.loaded_metadb = None
        self.client_id = None
        self.client_secret = None
        self.customer_id = None
        self.redirect_uri = None
        self.cfg_file = None
        self.map_file = None
        self.db_list = []
        self.access_token_string = ""
        self.exclude = {}
        self.include = {}
        self.library = {}
        self.bom = {}
        self.parameter = {}
        self.libref = {}
        self.pref = {}
        self.tables = []
        self.status = None
        self.log_filename = None
        self.cfg_filename = os.environ.get(self.CFG_ENV_VAR)
        if self.cfg_filename is None:
            raise Exception("Environment Variable " + self.CFG_ENV_VAR + " is not set")
        try:
            self.cfg_file = open(self.cfg_filename, "r")
        except Exception as e:
            raise e
        try:
            self.map_file = open(self.MAP_FILENAME, "r")
        except Exception as e:
            raise e
        self.loaded_db = None
        self.loaded_metadb = None

    def load_database(self, database, meta_database):
        self.loaded_db = database
        self.loaded_metadb = meta_database
        self.access_token_string = ""
        self.tables = []
        
    def parse_file(self):
        config = configparser.ConfigParser(allow_no_value=False, interpolation=None)
        config.optionxform = str
        try:
            config.readfp(self.cfg_file)
        except Exception as e:
            raise e
        mapconfig = configparser.ConfigParser(allow_no_value=True)
        mapconfig.optionxform = str
        try:
            mapconfig.readfp(self.map_file)
        except Exception as e:
            raise e
        for entry in config.sections():
            if entry[0:8] == "database":
                db_dict = dict(config.items(entry))
                if not validate_identifier(db_dict['database']):
                    raise "Bad database name - must be identifier"
                self.db_list.append([MariaDB(database_id=entry, host=db_dict['host'], user=db_dict['username'],
                                             password=db_dict['password'], database_name=db_dict['database']),
                                     MariaDB(database_id=entry, host=db_dict['host'], user=db_dict['username'],
                                             password=db_dict['password'],
                                             database_name=db_dict['database'] + "_metadata")])
                if 'export' in db_dict:
                    self.db_list[-1][0].export_cmd = db_dict['export']
                if 'import' in db_dict:
                    self.db_list[-1][0].import_cmd = db_dict['import']
            if entry == "authentication":
                auth_dict = dict(config.items(entry))
                self.client_id = auth_dict['client_id']
                self.customer_id = auth_dict['customer']
                self.redirect_uri = auth_dict['redirect_uri']
                self.client_secret = auth_dict['client_secret']
            if entry == "preferences":
                self.pref = dict(config.items(entry))
        for entry in mapconfig.sections():      
            if entry == "library":
                self.library = dict(mapconfig.items(entry))
            if entry == "parameter":
                self.parameter = dict(mapconfig.items(entry))
            if entry == "exclude":
                self.exclude = dict(mapconfig.items(entry))
            if entry == "include":
                self.include = dict(mapconfig.items(entry))
            if entry == "reference":
                self.libref = dict(mapconfig.items(entry))
            if entry == "BOM":
                self.bom = dict(mapconfig.items(entry))
        if 'log' in self.pref:
            self.log_filename = self.pref['log']
            self.log_write("---------- Application Started")
            self.log_write("Config File %s", self.cfg_filename)
            for db in self.db_list:
                self.log_write("ID %s Host %s User %s Database %s", db[0].id, db[0].host, db[0].user, db[0].name)
            for item in self.library.values():
                if not validate_identifier(item):
                    self.log_write("In map.cfg library section, %s is an invalid identifier " % item)
                    exit()

    def get_client_id(self):
        return self.client_id
       
    def entry_exists(self, part_id, table):
        if not self.loaded_db.table_exists(table):
            return False
        try:
            result = self.loaded_db.query(
                "SELECT * FROM `" + table + "` WHERE `" + self.parameter['DigiKeyPartNumber'] + "` = '" + part_id + "'")
        except Exception as e:
            return False
        if result == []:
            return False
        return True

    def update_part(self, table, data_dict):
        self.loaded_db.add_columns(table, data_dict)
        query_string = "UPDATE `" + table + "` SET " + ",".join(
            ["`" + str(k) + "`='" + str(v) + "'" for (k, v) in list(data_dict.items())]) + " WHERE `" + \
                       self.parameter['DigiKeyPartNumber'] + "`='" \
                       + data_dict[self.parameter['DigiKeyPartNumber']] + "'"
        self.loaded_db.query(query_string)

    def insert_part(self, table, data_dict):
        rv = False
        if not self.loaded_db.table_exists(table):
            self.loaded_db.query("CREATE TABLE `" + table + "` (" + self.parameter['Category'] + " VARCHAR(255))")
            rv = True
        self.loaded_db.add_columns(table, data_dict)
        query_string = "INSERT INTO `" + table + "` (`" + "`, `".join(list(data_dict.keys())) + "`) VALUES (" + \
                       ("%s, " * len(data_dict))[:-2] + ")"
        self.loaded_db.query(query_string, *(list(data_dict.values())))
        return rv

    def log_write(self, format, *args):
        if self.log_filename is not None:
            with open(self.log_filename, 'a') as f:
                f.write(datetime.now().strftime(self.TS_FORMAT) + str(format) % args + "\n")
