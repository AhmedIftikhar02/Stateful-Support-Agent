import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from tools import fetch_order_details, create_escalation_ticket

# Load environment variables
load_dotenv()

# 1. State Definition
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 2. Tools List
tools = [fetch_order_details, create_escalation_ticket]

# 3. LLM Setup (Groq Verified Model)
llm = ChatGroq(
    model_name="qwen/qwen3.8-27b",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2
)

# Tool binding
llm_with_tools = llm.bind_tools(tools)

# 4. System Prompt Definition
SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are an intelligent Customer Support AI Agent. "
        "Your job is to help customers check their order details and handle complaints. "
        "Always use the `fetch_order_details` tool when a user asks about an order ID (e.g. ORD-101). "
        "If a user is asking for a refund, cancellation, or has an unresolved issue, "
        "use the `create_escalation_ticket` tool to escalate it for human supervisor review. "
        "Be polite, professional, and concise."
    )
)

# 5. Assistant Node Function
def assistant_node(state: AgentState):
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 6. Graph Construction
builder = StateGraph(AgentState)

builder.add_node("assistant", assistant_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

# 7. Checkpointer for Stateful Memory
memory = MemorySaver()

# Compile Graph with Memory Persistence
agent_app = builder.compile(checkpointer=memory)