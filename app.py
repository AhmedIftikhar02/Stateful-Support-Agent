import nest_asyncio
nest_asyncio.apply()  # Fixes Streamlit + LangGraph Event Loop Deadlock on Windows

import streamlit as st
import uuid
from langchain_core.messages import HumanMessage
from agent import agent_app

# Page configuration
st.set_page_config(page_title="AI Support Agent", page_icon="🤖", layout="wide")

st.title("🤖 Stateful Customer Support AI Agent")
st.caption("Powered by LangGraph, Gemini Flash, and Supabase PostgreSQL")

# Session State for Stateful Thread Memory Management
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Session Controls")
    st.write(f"**Current Thread ID:**\n`{st.session_state.thread_id}`")
    st.info("LangGraph is Thread ID ki madad se conversation state aur context ko Supabase/Memory saver me persistent rakhta hai.")
    
    if st.button("🔄 Reset Conversation / New Thread", type="primary"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Chat Input
user_input = st.chat_input("Poochhein... (e.g. Where is my order ORD-101?)")

if user_input:
    # 1. Display User Message in UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Config object pass karna jisme thread_id hoti hai
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    # 3. Streamlit Assistant Spinner while processing
    with st.chat_message("assistant"):
        with st.spinner("Agent execution & tool invocation in progress..."):
            try:
                # Agent invoke karein with message and state config
                response = agent_app.invoke(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=config
                )
                
                # Extract latest response message
                assistant_response = response["messages"][-1].content
                st.markdown(assistant_response)
                
                # Save assistant message to session history
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            except Exception as e:
                st.error(f"Error during agent execution: {str(e)}")