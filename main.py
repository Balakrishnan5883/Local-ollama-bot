from typing import  TypedDict, Union
from langchain_core.messages import HumanMessage,  AIMessage,BaseMessage
from langgraph.graph import StateGraph, START, END
from datetime import datetime
from constants import MODEL_NAME, MessagesTableInfo
from globals import GlobalVariables,getPastMessages


gv = GlobalVariables()


class AgentState(TypedDict):
    shortConversationHistory: list[Union[HumanMessage, AIMessage]]

def getCurrentTime():
    return f"The current time is {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")} in format %d/%m/%Y, %H:%M:%S."

def buildLlmPrompt (state: AgentState,newHumanMessage:HumanMessage) -> list[str|BaseMessage]:
    return[gv.systemPrompt,
        *state["shortConversationHistory"],
           getCurrentTime(),
           newHumanMessage]

def updateShortConversationHistory(state:AgentState,newHumanMessage:HumanMessage,newAiMessage:AIMessage)->AgentState:
    conversationHistory = state["shortConversationHistory"]
    conversationHistory.append(newHumanMessage)
    conversationHistory.append(newAiMessage)

    if len(conversationHistory)>12:
        conversationHistory = conversationHistory[-12:]

    return state
   
def recordConversationInDb(humanMessage:HumanMessage,aiMessage:AIMessage):
    
    
    messageInfo:dict[str,int|str] = {MessagesTableInfo.columnConversationId:gv.conversationId, # pyright: ignore[reportUnknownVariableType]
                                     MessagesTableInfo.columnSender:gv.userName,
                                     MessagesTableInfo.columnContent:humanMessage.content} # pyright: ignore[reportAssignmentType, reportUnknownMemberType]

    gv.conversationHistoryDB.insertData(MessagesTableInfo.tableName,messageInfo)
    messageInfo[MessagesTableInfo.columnSender] = MODEL_NAME
    messageInfo[MessagesTableInfo.columnContent] = aiMessage.content # type: ignore
    gv.conversationHistoryDB.insertData(MessagesTableInfo.tableName,messageInfo,True)


def chatToLlm(state: AgentState) -> AgentState:
    currentUserInput = input("Enter your input: ")
    if currentUserInput.lower()=='exit':
        state["shortConversationHistory"].append(HumanMessage("exit"))
        return state
    currentHumanMessage = HumanMessage(content=currentUserInput)
    currentPrompt = buildLlmPrompt(state,currentHumanMessage)
    responseStream = gv.model.stream(currentPrompt)
    
    stringResponseList:list[str] = []
    for chunk in responseStream:
        if isinstance(chunk.content, str): # pyright: ignore[reportUnknownMemberType]
            piece: str = chunk.content  
        else: 
            raise TypeError(f"stream returned unknown datatype")

        print(piece,end="",flush=True)
        stringResponseList.append(piece)
    print()
    fullResponse = AIMessage(content="".join(stringResponseList))
    recordConversationInDb(currentHumanMessage,fullResponse)
    updatedState = updateShortConversationHistory(state,currentHumanMessage,fullResponse)

    
    return updatedState


def isEndLoop (state:AgentState)->bool:
    conversation=state["shortConversationHistory"]
    if isinstance(conversation[-1],HumanMessage):
        if conversation[-1].content=='exit' : # pyright: ignore[reportUnknownMemberType]
            state["shortConversationHistory"].pop()
            return True
    return False



graph = StateGraph(state_schema=AgentState)

graph.add_node(chatToLlm.__name__, chatToLlm) # pyright: ignore[reportUnknownMemberType]
graph.add_node(isEndLoop.__name__,isEndLoop) # pyright: ignore[reportUnknownMemberType]

graph.add_edge(start_key=START, end_key=chatToLlm.__name__)
graph.add_conditional_edges(chatToLlm.__name__,isEndLoop,path_map={True:END,False:chatToLlm.__name__})


compiledGraph = graph.compile() # pyright: ignore[reportUnknownMemberType]


initialState = AgentState(
    shortConversationHistory=getPastMessages(gv.conversationHistoryDB,gv.userName,10)
)


compiledGraph.invoke(initialState)