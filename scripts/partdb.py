import mysql.connector as maria_db
from datetime import timedelta, datetime
from configReader import *
from tkinter import filedialog
import json
import re

def validate(str):
    pattern = re.compile(r'[\'\"\`]')
    if isinstance(str, list):
        for item in str:
            if pattern.findall(item) != []:
                return False
        return True
    else:
        return True if pattern.findall(str) == [] else False


def validate_identifier(string):
    pattern = re.compile('^[a-zA-Z][a-zA-Z0-9_]*$')
    return True if pattern.findall(string) else False


def sanitize(string):
    pattern = re.compile('[`\\]\\[;\\(\\)\'\"+]`')
    string = pattern.sub('', string)
    return string

###############################
###     Parts Database     ###
###############################


class MariaDB:
    SAVED_TOKENS = 5
    def __init__(self, database_id, host, user, password, database_name):
        self.id = database_id
        self.host = host
        self.user = user
        self.password = password
        self.name = database_name
        self.connector = None
        self.export_cmd = None
        self.import_cmd = None
        self.datatype = 1;

    def close(self):
        if self.connector is None:
            return
        self.connector.close()        

    def connect(self):
        try:
            self.connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password, db=self.name)
        except Exception as e:
            raise e        

    def get_connector_version(self):
        return maria_db.__version__

    def find_default_datatype(self):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password)
            my_cursor = connector.cursor(dictionary=True)
            my_cursor.execute("SELECT COUNT(*) from `information_schema`.`COLUMNS` "
                              "WHERE (TABLE_SCHEMA = 'altium') AND (DATA_TYPE = 'text')")
            rv = my_cursor.fetchall()
            connector.close()
            if rv[0]['COUNT(*)'] == 0:
                self.datatype = 0;
            return 
        except Exception:
            raise Exception("Unable to query information_schema")

    def get_default_datatype(self):
        return ["VARCHAR(255)", "TEXT"][self.datatype]
        
    def get_database_version(self):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password)
            my_cursor = connector.cursor(dictionary=True)
            my_cursor.execute("SELECT VARIABLE_VALUE FROM `information_schema`.GLOBAL_VARIABLES WHERE VARIABLE_"
                              "NAME = 'INNODB_VERSION'")
            rv = my_cursor.fetchall()
            connector.close()
            return rv[0]['VARIABLE_VALUE']
        except Exception:
            raise Exception("Unable to query information_schema")

    def query(self, query, *vars):
        result = []
        if self.connector is None or query == "":
            return
        try:
            my_cursor = self.connector.cursor(dictionary=True)
            my_cursor.execute(query, vars)
            try:
                my_result = my_cursor.fetchall()
            except Exception as e:
                self.connector.commit()
                return None
            else:
                for r in my_result:
                    result.append(r)
        except Exception as e:
            raise e
        return result

    def get_tables(self):
        connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password)
        my_cursor = connector.cursor(dictionary=True)
        my_cursor.execute("SELECT TABLE_NAME FROM `information_schema`.TABLES WHERE TABLE_SCHEMA = %s", (self.name, ))
        rv = my_cursor.fetchall()
        tables = []
        for t0 in rv:
            tables.append(list(t0.values())[0])
        return tables

    def get_count(self):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password)
            my_cursor = connector.cursor(dictionary=True)
            my_cursor.execute("SELECT SUM(TABLE_ROWS) FROM `information_schema`.TABLES WHERE TABLE_SCHEMA = %s", (self.name, ))
            rows = my_cursor.fetchall()[0]['SUM(TABLE_ROWS)']
            if rows is None:
                rows = 0
            my_cursor.execute("SELECT COUNT(TABLE_NAME) FROM `information_schema`.TABLES WHERE TABLE_SCHEMA = %s", (self.name, ))
            tables = my_cursor.fetchall()[0]['COUNT(TABLE_NAME)']
            if tables is None:
                tables = 0
            connector.close()
            return [tables, rows]
        except Exception as e:
            raise e
    ###############################
    ###     Query Wrappers      ###
    ###############################

    def add_columns(self, table, part_dict, types_dict):
        table_col = list(part_dict.keys())
        db_columns = self.query("SHOW COLUMNS FROM `" + table + "`")
        db_columns = [i['Field'] for i in db_columns]
        delta_list = list(set(table_col) - set(db_columns))
        if delta_list == []:
            return
        column_list = []
        for item in delta_list:
            cleanitem = sanitize(item)
            column_list.append('`' + cleanitem + '` ' + (
                               sanitize(types_dict[cleanitem]) if cleanitem in types_dict else self.get_default_datatype()))
        self.query("ALTER TABLE `" + table + "` ADD COLUMN (" + ", ".join(column_list) + ")")

    def table_exists(self, table):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password)
            my_cursor = connector.cursor(dictionary=True)
            my_cursor.execute("SELECT * FROM `information_schema`.TABLES WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s",
                              (self.name, table))
            rv = len(my_cursor.fetchall())
            connector.close()     
            if rv > 0:
                return True
            else:
                return False 
        except Exception:
            raise Exception("Unable to query information_schema")
 
    def database_exists(self):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password)
            my_cursor = connector.cursor(dictionary=True)
            my_cursor.execute("SELECT * FROM `information_schema`.SCHEMATA WHERE SCHEMA_NAME = %s", (self.name,))
            rv = len(my_cursor.fetchall())
            connector.close()     
            if rv > 0:
                return True
            else:
                return False 
        except Exception:
            raise Exception("Unable to query information_schema")

    def create_database(self):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password)
            my_cursor = connector.cursor(dictionary=True)
            my_cursor.execute("CREATE DATABASE IF NOT EXISTS `" + self.name + "`")
            connector.commit()
            connector.close()     
        except Exception as e:
            raise e
  
    def get_priceinfo(self, tables, view_db, supplier, part_list):
        result = []
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password)
            my_cursor = connector.cursor(dictionary=True)
            price_list = "`" + view_db + "`.price_list"
            qry = "CREATE VIEW " + price_list + " AS "
            qry += " UNION ".join("(SELECT `Supplier Part Number 1`,`Supplier Stock 1`,`Pricing 1` FROM %s.%s WHERE "
                                  "`Supplier 1` = '%s')"%(self.name, table, supplier) for table in tables)
            my_cursor.execute(qry)
            connector.commit()
            qry = "SELECT * FROM " + price_list + " WHERE `Supplier Part Number 1` IN ('"
            qry += "','".join(part[0] for part in part_list)
            qry += "')"
            my_cursor.execute(qry)
            rv = my_cursor.fetchall()
            my_cursor.execute("DROP VIEW " + price_list)
            connector.commit()
            for r in rv:
                result.append(r)
            return result
        except Exception as e:
            raise e

    def update_priceinfo(self, table, pricing, stock, part):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password)
            my_cursor = connector.cursor(dictionary=True)
            table_name = "`" + self.name + "`.`" + table + "`"
            my_cursor.execute("UPDATE " + table_name + " SET `Pricing 1` = '%s', `Supplier Stock 1` = '%s' WHERE "
                                                       "`Supplier Part Number 1` = '%s'", pricing, str(stock), part)
            connector.commit()
            connector.close()
        except Exception as e:
            raise e
            
    def get_latest_token(self):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password, db=self.name)
            my_cursor = connector.cursor(dictionary=True)
            my_cursor.execute("SELECT * FROM token WHERE timestamp = (SELECT max(timestamp) FROM token)")
            rv = my_cursor.fetchall()
            connector.close()
            return rv[0]    
        except Exception as e:
            raise Exception("Unable to query token", e)

    def set_token(self, token):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password, db=self.name)
            cursor = connector.cursor(dictionary=True)
            cursor.execute("SELECT count(*) FROM token")
            count = cursor.fetchall()[0]['count(*)'] - (self.SAVED_TOKENS - 1)
            if count > 0:
                cursor.execute("DELETE FROM token ORDER BY timestamp ASC LIMIT %s", (count,))
                connector.commit() 
            query = (
                'INSERT INTO `token` (`access_token`, `refresh_token`, `token_type`, `expires_in`, `refresh_token_expires_in`, `timestamp`) '
                'VALUES (%(access_token)s, %(refresh_token)s, %(token_type)s, %(expires_in)s, %(refresh_token_expires_in)s, %(timestamp)s)'
                )
            cursor.execute(query, token)
            connector.commit()
            connector.close()
        except Exception as e:
            raise Exception("Unable to set token", e)
    
    def parse_command(self, string, hide=False):
        now = datetime.now()
        if (string[0] == '"' and string[-1] == '"') or (string[0] == "'" and string[-1] == "'"):
            string = string[1:-1]            
        string = re.sub(r'\%\(date\)', now.strftime("%m%d%Y"), string)
        string = re.sub(r'\%\(time\)', now.strftime("%H%M"), string)
        string = re.sub(r'\%\(database\)', self.name, string)
        string = re.sub(r'\%\(username\)', self.user, string)
        string = re.sub(r'\%\(password\)', self.password if not hide else "xxxxxxxx", string)
        string = re.sub(r'\%\(host\)', self.host, string)
        if re.search(r'\%\(openfile\)', string):
            infile = filedialog.askopenfilename(initialdir=".", title="Open .sql file", filetypes=
                (("sql files", "*.sql"), ("all files", "*.*")))
            if not infile:
                return None
            string = re.sub(r'\%\(openfile\)', '"' + infile + '"', string)
        if re.search(r'\%\(savefile\)', string):
            outfile = filedialog.asksaveasfilename(initialdir=".", title="Save database", filetypes=
                (("sql file", "*.sql"), ("all files", "*.*")))
            if not outfile:
                return ""
            if not outfile.lower().endswith('.sql'):
                outfile += '.sql'
            string = re.sub(r'\%\(savefile\)', '"' + outfile + '"', string)
        return string
