import configparser
import os
from partdb import *
from datetime import datetime


###############################
###   Config File Reading   ###
###############################


class singleton(object):
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


@singleton
class Config:
    CFG_ENV_VAR = "PARTLOCATER_CFG"
    MAP_FILENAME = "../assets/map.cfg"
    TS_FORMAT = "%d/%m/%y %H:%M:%S "

    def __init__(self):
        self.loaded_db = None
        self.loaded_metadb = None
        self.client_id = None
        self.client_secret = None
        self.customer_id = None
        self.cfg_file = None
        self.map_file = None
        self.db_list = []
        self.access_token_string = ""
        self.exclude = {}
        self.include = {}
        self.library = {}
        self.parameter = {}
        self.libref = {}
        self.pref = {}
        self.tables = []
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
        config = configparser.ConfigParser(allow_no_value=False)
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
                self.db_list.append([MariaDB(database_id=entry, host=db_dict['host'], user=db_dict['username'],
                                             password=db_dict['password'], database_name=db_dict['database']),
                                     MariaDB(database_id=entry, host=db_dict['host'], user=db_dict['username'],
                                             password=db_dict['password'],
                                             database_name=db_dict['database'] + "_metadata")])
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
        if ('log' in self.pref):
            self.log_filename = self.pref['log']
            self.log_write("---------- Application Started")
            self.log_write("Config File %s", self.cfg_filename)
            for db in self.db_list:
                self.log_write("ID %s Host %s User %s Database %s", db[0].id, db[0].host, db[0].user, db[0].name)

    def get_client_id(self):
        return self.client_id

#deprecated
    def load_current_token_info(self):
        if (self.loaded_metadb.connector is None):
            raise (self.loaded_metadb.host + " not connected")
        token_info = self.loaded_metadb.query("SELECT * FROM Token WHERE timestamp = (SELECT max(timestamp) FROM Token)")[0]
        try:
            self.access_token_string = token_info['access_token']
            return token_info
        except Exception:
            raise Exception("No token found.")
#deprecated
    def refresh_token(self, new_token_info):
        saved_tokens = 5
        try:
            new_token_info = json.loads(new_token_info)  # Remove/Merge
            row_count = self.loaded_metadb.query("SELECT count(*) FROM Token")[0]['count(*)']
            self.loaded_metadb.query("DELETE FROM Token ORDER BY timestamp ASC LIMIT %s",
                                     max(row_count - saved_tokens, 0))
            self.loaded_metadb.query(
                "INSERT INTO Token (access_token, refresh_token, token_type, timestamp, expires_in)" +
                " VALUES (%s, %s, %s, NOW() ,%s)",
                new_token_info['access_token'], new_token_info['refresh_token'],
                new_token_info['token_type'], new_token_info['expires_in'])
            self.access_token_string = new_token_info['access_token']
            return new_token_info
        except Exception as e:
            return None

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
                       self.parameter['DigiKeyPartNumber'] + "`='" + data_dict[
                           self.parameter['DigiKeyPartNumber']] + "'"
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
        if (self.log_filename is not None):
            with open(self.log_filename, 'a') as f:
                f.write(datetime.now().strftime(self.TS_FORMAT) + str(format) % args + "\n");