from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import START, StateGraph
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from typing import List
from typing_extensions import List, TypedDict
from langchain_core.documents import Document
import os
from backend.pinecone_utilis import vectorstore
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(
    model='gpt-4.1',
    api_key=OPENAI_API_KEY
)
output_parser = StrOutputParser()

contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Use the following context to answer the user's question."),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

class State(TypedDict):
    messages: List[BaseMessage]
    


# Define application steps
def retrieve(query: str):
    retrieved_docs = vectorstore.similarity_search(query)
    return  retrieved_docs


def generate_response(query: str, state: State)->State:
    retrieved_docs=retrieve(query=query)
    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)
    system_message = SystemMessage(
        content="You are a helpful AI assistant. Answer the user's question using ONLY the information provided below. "
                "If the answer is not in the context, say 'I don't know.' Do not make up information. "
                f"Context: {docs_content}"
    )

    state['messages'].append(system_message)
    state['messages'].append(HumanMessage(content=query))

    response = llm.invoke(state["messages"])
    state['messages'].append(AIMessage(content=response.content))
    return state



