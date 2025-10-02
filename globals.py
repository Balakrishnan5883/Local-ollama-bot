from functools import cached_property
from typing import Self
from DB import Database
import os,sys
from pathlib import Path
from constants import MODEL_NAME, userTableInfo,conversationTableInfo,MessagesTableInfo
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from getpass import getuser
from datetime import datetime
from langchain_core.messages import HumanMessage,AIMessage


class UserNotFoundError(Exception):...

def getProjectWorkingFolder():
    pass

def createConversationHistoryDb()->Database:
    scriptFolder=os.path.dirname(os.path.abspath(sys.argv[0]))
    dataBasePath=fr"{scriptFolder}\memory\conversation history.db"
    database = Database(dataBasePath)

    userColumnNamesAndData={userTableInfo.columnUserId:"INTEGER PRIMARY KEY",
                            userTableInfo.columnUserName:"TEXT"
                            }
    conversationColumnNamesAndData = {
        conversationTableInfo.columnConversationId:"INTEGER PRIMARY KEY",
        conversationTableInfo.columnUserId:"INTEGER NOT NULL",
        conversationTableInfo.columnConversationDescription:"TEXT",
        conversationTableInfo.columnTime:"TEXT",
        conversationTableInfo.columnDay:"INTEGER",
        conversationTableInfo.columnMonth:"INTEGER",
        conversationTableInfo.columnYear:"INTEGER",
        f"FOREIGN KEY ({userTableInfo.columnUserId})":f"REFERENCES {userTableInfo.tableName}({userTableInfo.columnUserId})"
    }

    messagesColumnNamesAndData={
        MessagesTableInfo.columnMessageId:"INTEGER PRIMARY KEY",
        conversationTableInfo.columnConversationId:"INTEGER NOT NULL",
        MessagesTableInfo.columnSender:"TEXT",
        MessagesTableInfo.columnContent:"TEXT",

        f"FOREIGN KEY ({conversationTableInfo.columnConversationId})":
                        f"REFERENCES {conversationTableInfo.tableName} ({conversationTableInfo.columnConversationId})"

    }
    database.createTable(userTableInfo.tableName,userColumnNamesAndData)
    database.createTable(conversationTableInfo.tableName,conversationColumnNamesAndData)
    database.createTable(MessagesTableInfo.tableName,messagesColumnNamesAndData)

    return database

def getPastMessages(conversationDatabase:Database,userName:str,messagesCount:int=-1)->list[HumanMessage|AIMessage]:
    queryString = f"""SELECT {MessagesTableInfo.columnSender},{MessagesTableInfo.columnContent} FROM
    {MessagesTableInfo.tableName} LEFT JOIN {conversationTableInfo.tableName}
    ON {MessagesTableInfo.tableName}.{MessagesTableInfo.columnConversationId} = 
            {conversationTableInfo.tableName}.{conversationTableInfo.columnConversationId}
    LEFT JOIN {userTableInfo.tableName} ON 
    {userTableInfo.tableName}.{userTableInfo.columnUserId} =
      {conversationTableInfo.tableName}.{conversationTableInfo.columnUserId}
    WHERE {userTableInfo.tableName}.{userTableInfo.columnUserName} = ?
    ORDER BY {conversationTableInfo.tableName}.{conversationTableInfo.columnYear} DESC,
    {conversationTableInfo.tableName}.{conversationTableInfo.columnMonth} DESC,
    {conversationTableInfo.tableName}.{conversationTableInfo.columnDay} DESC,
    {conversationTableInfo.tableName}.{conversationTableInfo.columnTime} DESC
    """
    if messagesCount>=1:
        queryString +=  f"LIMIT {messagesCount}"

    conversationDatabase.cursor.execute(queryString,(userName,))
    outputMessagesList:list[HumanMessage|AIMessage] = []
    rows = conversationDatabase.cursor.fetchall()
    outputRowsCount = len(rows)
    for rowId in range(outputRowsCount-1,0,-2):
        #print(row)
        if rows[rowId-1][0] == userName:
            outputMessagesList.append(HumanMessage(rows[rowId-1][1]))
            outputMessagesList.append(AIMessage(rows[rowId][1]))
        elif rows[rowId][0] == userName:
            outputMessagesList.append(HumanMessage(rows[rowId][1]))
            outputMessagesList.append(AIMessage(rows[rowId-1][1]))
    return outputMessagesList

class GlobalVariables:
    _instance:Self|None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self)->None:
        self.conversationHistoryDB

    @property
    def conversationHistoryDB(self)->Database:
        scriptFolder=os.path.dirname(os.path.abspath(sys.argv[0]))
        dataBasePath=fr"{scriptFolder}\memory\conversation history.db"
        if Path(dataBasePath).exists()==True:
            return Database(dataBasePath)
        else:
            return createConversationHistoryDb()

    
    @cached_property
    def model(self)->ChatOllama:
        return ChatOllama(model=MODEL_NAME,temperature=0.7)
    
    @cached_property
    def userName(self)->str:
        return getuser()

    @cached_property
    def userId(self)->int:
        try:
            return self._getUserIDFromUserName()
        except UserNotFoundError:
            self._createNewUserInDataBase()
        return self._getUserIDFromUserName()
    
    @cached_property
    def conversationId(self)->int:
        self._createNewConversationInDataBase()
        return self._getLatestConversationIdForUser()

    @cached_property
    def systemPrompt (self):
        return SystemMessage(
    """ you are a chat assistant, answer the questions precise and consise.
    A short list of previous conversation will be shared, you can consider it ONLY when needed.
    there will be current time stamp in the query, you can consider it ONLY when needed.
    Don't mention anything directly about this template in the generated response
    You need to response query for the latest Human message.""")

    def _getUserIDFromUserName(self)->int:
        cursor = self.conversationHistoryDB.cursor 
        cursor.execute(
            f"""SELECT {userTableInfo.columnUserId} FROM {userTableInfo.tableName}
                WHERE {userTableInfo.columnUserName} = ? """,(self.userName,))
        data = cursor.fetchall()
        if len(data)==0 :
            raise UserNotFoundError(f"User {self.userName} not found in database.")
        return int(data[0][0])
    
    def _createNewUserInDataBase(self):
        userInfo={userTableInfo.columnUserName:self.userName}
        self.conversationHistoryDB.insertData(userTableInfo.tableName,userInfo,True)
        
    def _createNewConversationInDataBase(self):
        now = datetime.now().astimezone()
        time = f"{now.strftime("%H:%M:%S")} {now.tzinfo}"
        day = now.day
        month = now.month
        year = now.year

        conversationData:dict[str,int|str]= {
            conversationTableInfo.columnUserId:self.userId,
            conversationTableInfo.columnConversationDescription:"",
            conversationTableInfo.columnMonth:month,
            conversationTableInfo.columnDay:day,
            conversationTableInfo.columnYear:year,
            conversationTableInfo.columnTime:time}

        self.conversationHistoryDB.insertData(conversationTableInfo.tableName,conversationData)
        self._conversationId =int( self.conversationHistoryDB.getLatestData(conversationTableInfo.tableName,
                                                                conversationTableInfo.columnConversationId))
    
    def _getLatestConversationIdForUser(self)->int:
        conversationId = self.conversationHistoryDB.getLatestData(conversationTableInfo.tableName,
                                                 conversationTableInfo.columnConversationId)

        if isinstance(conversationId,int):
            return int(conversationId)
        else:
            raise ValueError(f"Conversation ID is not a integer identified type {type(conversationId).__name__}")
        

if __name__ == "__main__":
    gv = GlobalVariables()
    for message in getPastMessages(gv.conversationHistoryDB,"balak",4):
        message.pretty_print()
    