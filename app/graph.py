import os
from typing import Callable
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.configuration import supervisor_model
from app.src.nodes.agents import coder_node, retriver_node, torrent_node
from app.src.nodes.supervisor import SupervisorNodeCreator


supervisor_llm = ChatOpenAI(temperature=0, model=supervisor_model)
members = ["data_retriever", "python_functions", "torrent_download_client"]
supervisor_node: Callable = SupervisorNodeCreator(supervisor_llm, members=members)

builder = StateGraph(MessagesState)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("data_retriever", retriver_node)
builder.add_node("python_functions", coder_node)
builder.add_node("torrent_download_client", torrent_node)

use_checkpointer = os.environ.get("WITH_CHECKPOINTER") == "true"
checkpointer = MemorySaver() if use_checkpointer else None
agent: CompiledStateGraph = builder.compile(checkpointer=checkpointer)
agent.name = "Multi-agent supervisor"