from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

MODEL_NAME = "gemma3n:e2b"

<<<<<<< HEAD
WORKING_DIRECTORY = r"C:\Users\Bala krishnan\OneDrive\Documents\code projects\Python\Local-ollama-bot"
=======
WORKING_DIRECTORY = r"C:\Users\balak\OneDrive\Documents\Code projects\Python\Local-chat-bot"
>>>>>>> 3c1dd19130ae14a18177d80d49e9977de9383a1b
MAX_CHARS_READ_LIMIT = 10000
aiWorkingDirectory = Path(WORKING_DIRECTORY).joinpath("AI")

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
