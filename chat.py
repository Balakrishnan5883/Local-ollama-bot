from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain.agents import create_agent 
from langchain_core.messages import HumanMessage,BaseMessage
from pprint import pprint
from tools.fileManager import readFile,writeFile,listDirectoryContent,createFolder
import os

API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro",google_api_key=API_KEY)
localLlm = ChatOllama(model="gpt-oss:latest")
agent= create_agent(model=localLlm,tools=[readFile,writeFile,listDirectoryContent,createFolder]) 
messages:list[BaseMessage]= []
firstMessage = HumanMessage("Write a hello world program in Typescript to a file")

messages.append(firstMessage)
responseChunk = agent.stream({"messages":messages},stream_mode="messages") # pyright: ignore[reportUnknownMemberType]
for llmToken,metaData in responseChunk:
    print(llmToken.content)
    print(metaData)

""" for chunk in responseChunk:
    for step, data in chunk.items():
        print(f"step: {step}")
        print(f"content: {data['messages'][-1].content_blocks}") """


