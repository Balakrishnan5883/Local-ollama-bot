import sqlite3
import os
import sys
from typing import Any, Callable, Union,TypeVar,ParamSpec
from functools import wraps
import inspect


class TableNotFoundError(Exception):
    pass
class ColumnNotFoundError(Exception):
    pass
class ArgumentError(Exception):
    pass

P = ParamSpec("P")
R = TypeVar("R")

class Database:
    def __init__(self,dataBasePath:str,TableName:str="",columnsAndDataTypes:dict[str,str]={}) -> None:
        os.makedirs(os.path.dirname(dataBasePath), exist_ok=True) 
        self.tableAndColumnsDict:dict[str, list[str]]={}
        self.connection=sqlite3.connect(f"{dataBasePath}"
                                        ,detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cursor=self.connection.cursor()
        if TableName=="" or len(columnsAndDataTypes.keys())==0:
            self.connection.commit()
        else:
            self.createTable(TableName, columnsAndDataTypes)
            self.tableAndColumnsDict[TableName]=list(columnsAndDataTypes.keys())

    @property
    def tableNames(self)->list[str]:
        self.cursor.execute("SELECT name FROM sqlite_master where type='table';")
        tables=self.cursor.fetchall()
        tableNamesList=list(str(table[0]) for table in tables)
        return tableNamesList
    

    def isTableExists(self,tableName:str)->bool:
        tablesList = self.tableNames
        if tableName not in tablesList:
            return False
        return True
    
    def isColumnExists(self,tableName:str,columnName:str)->bool:
        if self.isTableExists(tableName) ==False:
            raise TableNotFoundError(f"Table Name {tableName} not found in database.")
        columnsList = self.getColumns(tableName)
        if columnName not in columnsList:
            return False
        return True
             
    @staticmethod
    def _checkTableExists(method:Callable[P,R]) -> Callable[P,R] :
        signature = inspect.signature(method)
        @wraps(method)
        def wrapper(*args:P.args, **kwargs:P.kwargs)->R:
            bound = signature.bind(*args,**kwargs)
            bound.apply_defaults()
            tableName:str|Any = bound.arguments.get("tableName")
            dataBase:"Database"|Any= bound.arguments.get("self")
            if tableName is None:
                raise ArgumentError(f"function {method.__name__} doesn't have parameter tableName")
            if dataBase is None:
                raise ArgumentError(f"Self argument is none in function {method.__name__}")
            
            if isinstance(tableName,str) == False:
                raise ValueError(f"tableName argument is not string")
            if isinstance(dataBase,Database) == False:
                raise ValueError(f"self is not Database object")
            
            if tableName not in dataBase.tableNames:
                raise TableNotFoundError(f"Table {tableName} not found")
            return method(*args,**kwargs)
        return wrapper
    

    @staticmethod
    def _checkColumnExists(method:Callable[P,R])-> Callable[P,R] :
        signature = inspect.signature(method)
        @wraps(method)
        def wrapper(*args:P.args, **kwargs:P.kwargs)->R:
            bound = signature.bind(*args,**kwargs)
            bound.apply_defaults()
            tableName:str|Any = bound.arguments.get("tableName")
            dataBase:"Database"|Any= bound.arguments.get("self")
            columnName:str|Any=bound.arguments.get("columnName")
            columnAndValue:dict[str,Any]|Any = bound.arguments.get("columnAndValue")

            if tableName is None:
                raise ArgumentError(f"function {method.__name__} doesn't have parameter tableName")
            if dataBase is None:
                raise ArgumentError(f"Self argument is none in function {method.__name__}")
            if columnName is None and columnAndValue is None:
                raise ArgumentError(f"both column names arguments is none in function {method.__name__}")

            if isinstance(tableName,str) == False:
                raise ValueError(f"tableName argument is not string")
            if isinstance(dataBase,Database) == False:
                raise ValueError(f"self is not Database object")

            columnsInTable = dataBase.getColumns(tableName)

            if columnAndValue is not None:
                columnsInInput=list(columnAndValue.keys())
                for column in columnsInInput:
                    if column not in columnsInTable:
                        raise ColumnNotFoundError(f"Column {column} not found in the table {tableName}")
            elif columnName not in columnsInTable:
                    raise ColumnNotFoundError(f"Column {columnName} not found in the table {tableName}")
                
            return method(*args, **kwargs)
            
        return wrapper


    def getColumns(self, tableName:str)->list[str]:
        if self.isTableExists(tableName) == False:
            raise TableNotFoundError(f"Table name {tableName} not found in database")
        self.cursor.execute(f"PRAGMA table_info('{tableName}')")
        columnsInfoList:list[tuple[str]]=self.cursor.fetchall()

        columnNames:list[str]=list(str(columnInfo[1]) for columnInfo in columnsInfoList
                                   if len(columnInfo)>1)
        return columnNames

    def createTable(self,tableName:str, columnsAndDataTypes:dict[str, str]) -> None:
        if self.isTableExists(tableName):
            raise ValueError(f"Table name {tableName} already exists in database")
        
        columnAndDataTypesString=",".join([f"{column} {dataType}" 
                                           for column, dataType in columnsAndDataTypes.items()])
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS '{tableName}' ({columnAndDataTypesString})")    

    @_checkTableExists
    def insertColumn(self, tableName:str, columnName:str, columnDataType:str) -> None:
        self.cursor.execute(f"ALTER TABLE '{tableName}' ADD COLUMN '{columnName}' {columnDataType}")

    @_checkColumnExists
    def insertData(self, tableName: str, columnAndValue: dict[str, Any], saveChanges: bool = False) -> None:
        """
        Inserts data in an existing table.
        columnAndValue - column name and value to be added in column as key value pair
        """
        columns = ", ".join(columnAndValue.keys())              
        placeholders = ", ".join("?" for _ in columnAndValue)   
        values = tuple(columnAndValue.values())                 

        query = f"INSERT INTO {tableName} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)

        if saveChanges:
            self.connection.commit()

    @_checkTableExists
    def getAllData(self,tableName:str)->list[tuple[Any]] :
        self.cursor.execute(f"SELECT * FROM '{tableName}'")
        rows:list[Any]|None=self.cursor.fetchall()
        return rows
    
    @_checkTableExists
    def clearAllData(self,tableName:str):
        self.cursor.execute(f"DELETE FROM '{tableName}'")

    @_checkTableExists
    def getLatestRow(self,tableName:str)->list[Any]:
        self.cursor.execute(f"SELECT * FROM '{tableName}' ORDER BY id DESC LIMIT 1")
        row=self.cursor.fetchone()
        if row is None:
            return []

        return list(row)
    
    @_checkTableExists
    @_checkColumnExists
    def getLatestData(self, tableName:str, columnName:str)->Union[str,int]:

        self.cursor.execute(f'SELECT "{columnName}" FROM "{tableName}" ORDER BY {columnName} DESC LIMIT 1')
        row=self.cursor.fetchone()
        if row is None:
            raise ValueError("Cursor returned None")
        return row[0]
    
    @_checkTableExists
    @_checkColumnExists
    def changeLatestData(self, tableName:str, columnName:str, value:Any):
        if self.getLatestRow(tableName)==[]:
            print(f"Table {tableName} is empty")
            return
        tempValue=str(value)
        latestRowID=self.getLatestRow(tableName)[0]
        self.cursor.execute(f"""UPDATE '{tableName}'
                               SET '{columnName}' = ?
                               WHERE id = ?
                            """,(tempValue,latestRowID))

    @_checkTableExists
    def printTable(self, tableName:str):
        self.cursor.execute(f"PRAGMA table_info('{tableName}')")
        columns=self.cursor.fetchall()
        columnsList=list(column[1] for column in columns)
        rows=self.getAllData(tableName)
        print (columnsList)
        for row in rows:
            print(row)
        
    def disconnect(self,saveChanges:bool):
        if saveChanges==True:
            self.connection.commit()
        self.connection.close()

def test():      
    columnsAndDataTypes:dict[str,str]={"id" :"INTEGER PRIMARY KEY",
                                    "A": "TEXT"
                                    ,"B":"TEXT"
                                    ,"C":"TEXT"
                                    ,"D":"TEXT"
                                    ,"E":"TEXT"
                                    ,"F":"TEXT"
                                    ,"G":"INTEGER"
                                    ,"H":"TEXT"}


    data1:dict[str,str|int]={"A": "A1","B":"B1","C":"C1",
                        "D":"D1","E":"E1","F":"F1","G":"44"}
    data2:dict[str,str|int]={"A": "A2","B":"B2","C":"C2",
                        "D":"D2","E":"E2","F":"F2","G":"23","H":"H2"}
    

    scriptFolder=os.path.dirname(os.path.abspath(sys.argv[0]))
    db1=Database(dataBasePath=fr"{scriptFolder}\log\test.db")
    
    print("printing tables in database")
    print (db1.tableNames)
    print("+++++++++++++++++++++++++++++++++")

    db1.createTable("TestTable", columnsAndDataTypes)
    db1.insertData(tableName="TestTable",columnAndValue= data1)
    db1.insertData(tableName="TestTable", columnAndValue=data2)

    print("printing latest row in table")
    print(db1.getLatestRow(tableName="TestTable"))
    print("+++++++++++++++++++++++++++++++++")

    db1.changeLatestData(tableName="TestTable",columnName="H", value=100)
    print("+++++++++++++++++++++++++++++++++")

    print("getting latest data of column A from table")
    try:
        print(db1.getLatestData("TestTable",columnName="A"))
    except ValueError:
        print("No data found in TestTable on Column A")
    print("+++++++++++++++++++++++++++++++++")

    print("printing columns in table")
    print(db1.getColumns("TestTable"))
    print("+++++++++++++++++++++++++++++++++")

    print("Printing entire table")
    db1.printTable("TestTable")
    db1.disconnect(saveChanges=True)



if __name__=="__main__":
    
    pass
