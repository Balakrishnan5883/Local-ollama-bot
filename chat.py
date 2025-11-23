from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain.agents import create_agent 
from langchain_core.messages import HumanMessage,BaseMessage,AIMessageChunk,ToolMessage,message_to_dict
from pprint import pprint
from tools.fileManager import readFile,writeFile,listDirectoryContent,createFolder
from typing import Any
import os

API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro",google_api_key=API_KEY)
localLlm = ChatOllama(model=r"qwen3-coder:latest")
agent= create_agent(model=localLlm,tools=[readFile,writeFile,listDirectoryContent,createFolder]) 
messages:list[BaseMessage]= []
firstMessage = HumanMessage("write me some sample UI in Pyside6 with dynamic check boxes and text boxes that appears based on user input selection." \
"Also Add good stying to the user interface")

messages.append(firstMessage)
responseChunk = agent.stream({"messages":messages},stream_mode="messages") # pyright: ignore[reportUnknownMemberType]
for chunk in responseChunk:
    responseChunk = chunk[0]
    langGraphInfoChunk = chunk[1]

    contentChunk:Any = responseChunk.content
    
    if hasattr(responseChunk,"tool_calls") and len(responseChunk.tool_calls)>0:
        toolInfo = responseChunk.tool_calls[0]
        print("")
        print("Calling Tool")
        print(f"Tool Name: {toolInfo["name"]}")
        print(f"Tool Args: ")
        pprint(toolInfo["args"])
    if isinstance(responseChunk,ToolMessage):
        print(f"Tool Message : {contentChunk}")


    if isinstance(responseChunk,AIMessageChunk):
        if isinstance(contentChunk,str) :
            if contentChunk.strip()=="":
                continue
            else:
                print(contentChunk,end ="")
        elif isinstance(contentChunk,list) and len(contentChunk)>0:
            data = contentChunk[0]
            if isinstance(data,dict) :
                #print(f"output data type :{data.get("type")}")
                print(f"{data.get("text")}",end="")
        
    

