from typing import Any
import sqlite3
import re
from resql.core.errors import PydbInvalidTableName

regex = re.compile("[A-z0-9]+")

class ReSql:
    default_row:str = "DEFAULT_RESQL_TABLE"

    def __init__(self, path:str=":memory:", props:dict={}):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS DEFAULT_RESQL_TABLE (ID TEXT, value TEXT)")
        self.cursor.close()

    def insert(self,key:str,value:Any, table:str=default_row):
        self.cursor = self.connection.cursor()
        self.cursor.execute(f"INSERT INTO {table} (ID, value) VALUES (?, ?)", (key, value))
        self.cursor.close()
        return {"status":"success"}

    def find(self,key:str, table:str=default_row):
        self.cursor = self.connection.cursor()
        self.cursor.execute(f"SELECT * FROM {table} WHERE ID = ?", (key,))
        resp = self.cursor.fetchone()
        self.cursor.close()
        return resp[1] if resp != None else None

    def get(self,key:str, table:str=default_row):
        self.cursor = self.connection.cursor()
        self.cursor.execute(f"SELECT * FROM {table} WHERE ID = ?", (key,))
        resp = self.cursor.fetchone()
        self.cursor.close()
        return resp[1] if resp != None else None

    def all(self, table:str=default_row):
        self.cursor = self.connection.cursor()
        self.cursor.execute(f"SELECT * FROM {table}")
        resp = self.cursor.fetchall()
        self.cursor.close()
        return resp if resp != None else None

    def wipe(self, table:str=default_row):
        self.cursor = self.connection.cursor()
        self.cursor.execute(f"delete from {table}")
        self.cursor.close()
        return {"status":"success"}

    def delete(self,key:str, table:str=default_row):
        self.cursor = self.connection.cursor()
        self.cursor.execute(f"DELETE FROM {table} WHERE ID = ?", (key,))
        self.cursor.close()
        return {"status":"success"}

    def create_table(self,name:str):
        self.cursor = self.connection.cursor()
        if regex.match(name) != None and regex.match(name)[0] == name:
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {name} (ID TEXT, value TEXT)")
            self.cursor.close()
        else:
            raise PydbInvalidTableName("Invalid table name")
        return {"status":"success","table":name}

    def run(self,sql:str):
        self.cursor = self.connection.cursor()
        self.cursor.execute(sql)
        return self.cursor
    
    def cursor(self):
        self.cursor = self.connection.cursor()
        return self.cursor
