from sqlite3 import connect, Row

class Databasehelper:
    def __init__(self)->None:
        self.database = 'students.db'

    def getdb_connection(self):
        connection = connect(self.database)
        return connection
    
    def getprocess(self,sql:str):
        connection = self.getdb_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.row_factory = Row
        data:list = cursor.fetchall()
        cursor.close()
        connection.close()
        return data

    def postprocess(self,sql:str):
        connection = self.getdb_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close() 
        return True if cursor.rowcount > 0 else False

    def getall_records(self,table)->list:
        query = f"SELECT * FROM {table}"
        users:list = self.getprocess(query)
        return users
    
    def find_record(self,table,idno:str):
        sql:str = f"SELECT * FROM {table} WHERE `idno` = {idno}"
        return self.getprocess(sql)
    
    def add_record(self,table,**kwargs):
        keys:list = kwargs.keys()
        values:list=kwargs.values()
        columns:str = ",".join(keys)
        formatted_values = ",".join([f"'{v}'" if isinstance(v, str) else str(v) for v in values])
        sql:str = f"INSERT INTO {table} ({columns}) VALUES({formatted_values})"
        return self.postprocess(sql)
    
    def update_record(self,table,**kwargs):
        keys:list = list(kwargs.keys())
        values:list = list(kwargs.values())
        flds:list = []
        # join both keys and values as an element in a list
        for i in range(1, len(keys)):
            flds.append(f"`{keys[i]}` = '{values[i]}'")
        #transform the list of string with "," as delimiter
        fld:str = ",".join(flds)
        #create sql statement
        sql:str = f"UPDATE `{table}` SET {fld} WHERE `{keys[0]}`= '{values[0]}'"
        return self.postprocess(sql)
    
    def delete_record(self,table,**kwargs)->list:
        keys:list = list(kwargs.keys())
        values:list = list(kwargs.values())
        sql:str = f"DELETE FROM `{table}` WHERE `{keys[0]}` = '{values[0]}'"
        return self.postprocess(sql)
    