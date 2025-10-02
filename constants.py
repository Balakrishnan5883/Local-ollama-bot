from dataclasses import dataclass

from typing import ClassVar

MODEL_NAME = "gemma3n:e2b"


@dataclass(frozen=True)
class userTableInfo:
    tableName:ClassVar[str] =  "users"
    columnUserId = "user_id"
    columnUserName = 'user_name'


@dataclass(frozen=True)
class conversationTableInfo:
    tableName:ClassVar[str] = "conversations"
    columnConversationId = "conversation_id"
    columnUserId="user_id"
    columnConversationDescription = "conversation_description"
    columnTime = "time"
    columnDay = "day"
    columnMonth = "month"
    columnYear = "year" 
    


@dataclass(frozen=True)
class MessagesTableInfo:
    tableName:str = "messages"
    columnMessageId = "message_id"
    columnConversationId = "conversation_id"
    columnSender="sender"
    columnContent = "content"
