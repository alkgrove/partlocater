import mysql.connector as maria_db
from datetime import timedelta, datetime
from tkinter import filedialog
import json
import re

def validate(str):
    pattern = re.compile('[\'\"\`]')
    if (isinstance(str, list)):
        for item in str:
            if pattern.findall(item) != []:
                return False
        return True
    else:
        return True if pattern.findall(str) == [] else False
    
def sanitize(str):
    pattern = re.compile('[`\]\[;\(\)\'\"+]`')
    str = pattern.sub('', str)
    return str

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

    def get_database_version(self):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password)
            my_cursor = connector.cursor(dictionary=True)
            my_cursor.execute("SELECT VARIABLE_VALUE FROM `information_schema`.GLOBAL_VARIABLES WHERE VARIABLE_NAME = 'INNODB_VERSION'")
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
            except Exception:
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
            if (rows is None):
                rows = 0
            my_cursor.execute("SELECT COUNT(TABLE_NAME) FROM `information_schema`.TABLES WHERE TABLE_SCHEMA = %s", (self.name, ))
            tables = my_cursor.fetchall()[0]['COUNT(TABLE_NAME)']
            if (tables is None):
                tables = 0
            connector.close()
            return [tables, rows]
        except Exception as e:
            raise e

    ###############################
    ###     Query Wrappers      ###
    ###############################
    def add_columns(self, table, part_dict):
        table_col = list(part_dict.keys())
        db_columns = self.query("SHOW COLUMNS FROM `" + table + "`")
        db_columns = [i['Field'] for i in db_columns]
        minus_list = list(set(table_col) - set(db_columns))
        if minus_list == []:
            return
        to_add = ['`' + sanitize(i) + '`' for i in minus_list]
        to_add_str = ((' VARCHAR(255), '.join(to_add)) + ' VARCHAR(255)')
        self.query("ALTER TABLE `" + table + "` ADD COLUMN (" + to_add_str + ")")

    def table_exists(self, table):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password)
            my_cursor = connector.cursor(dictionary=True)
            my_cursor.execute("SELECT * FROM `information_schema`.TABLES WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s", (self.name,table))
            rv = len(my_cursor.fetchall())
            connector.close()     
            if (rv > 0):
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
            if (rv > 0):
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

    def get_latest_token(self):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password, db=self.name)
            my_cursor = connector.cursor(dictionary=True)
            my_cursor.execute("SELECT * FROM Token WHERE timestamp = (SELECT max(timestamp) FROM Token)")
            rv = my_cursor.fetchall()
            connector.close()
            return rv[0]    
        except Exception as e:
            raise Exception("Unable to query token", e)

    def set_token(self, token):
        try:
            connector = maria_db.connect(host=self.host, user=self.user, passwd=self.password, db=self.name)
            cursor = connector.cursor(dictionary=True)
            cursor.execute("SELECT count(*) FROM Token")
            count = cursor.fetchall()[0]['count(*)'] - (self.SAVED_TOKENS - 1)
            if (count > 0):
                cursor.execute("DELETE FROM Token ORDER BY timestamp ASC LIMIT %s", (count,))
                connector.commit() 
            query = (
                'INSERT INTO `Token` (`access_token`, `refresh_token`, `token_type`, `expires_in`, `timestamp`) '
                'VALUES (%(access_token)s, %(refresh_token)s, %(token_type)s, %(expires_in)s, %(timestamp)s)'
                )
            cursor.execute(query, token)
            connector.commit()
            connector.close()
        except Exception as e:
            raise Exception("Unable to set token", e)
    
    def parseCommand(self, str):
        now = datetime.now()
        str = re.sub(r'\%\(date\)', now.strftime("%m%d%Y"),str)
        str = re.sub(r'\%\(time\)', now.strftime("%H%M"),str)
        str = re.sub(r'\%\(database\)', self.name, str)
        str = re.sub(r'\%\(username\)', self.user, str)
        str = re.sub(r'\%\(password\)', self.password, str)
        str = re.sub(r'\%\(host\)', self.host, str)
        if (re.search(r'\%\(openfile\)', str)):
            infile = filedialog.askopenfilename(initialdir = ".",title = "Open .sql file",filetypes = (("sql files","*.sql"),("all files","*.*")))
            if not infile:
                return None
            str = re.sub(r'\%\(openfile\)', '"' + infile + '"', str)
        if (re.search(r'\%\(savefile\)', str)):
            outfile = filedialog.asksaveasfilename(initialdir = ".",title = "Save database",filetypes = (("sql file","*.sql"),("all files","*.*")))
            if not outfile:
                return ""
            if not outfile.lower().endswith('.sql'):
                outfile += '.sql'
            str = re.sub(r'\%\(savefile\)', '"'+ outfile + '"', str)
        return str
