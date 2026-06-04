import streamlit as st
from core.llm_client import call_groq
from core.memory import MemoryStore
from core.stack_manager import load_stack, update_topic_status
from core.interview import generate_interview_questions, load_interview_questions

# Initialize memory (persists across Streamlit reruns)
if "memory" not in st.session_state:
    st.session_state.memory = MemoryStore()
if "current_topic" not in st.session_state:
    st.session_state.current_topic = "RAG"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Page config
st.set_page_config(page_title="AI Learning Assistant", layout="wide")
st.title("🧠 AI Learning Assistant – Chat Interface")

# Sidebar for controls
with st.sidebar:
    st.header("📚 Learning Controls")
    
    # Topic selection
    stack = load_stack()
    topic_names = [t["name"] for t in stack["topics"]]
    selected_topic = st.selectbox("Current Topic", topic_names, index=topic_names.index(st.session_state.current_topic) if st.session_state.current_topic in topic_names else 0)
    if selected_topic != st.session_state.current_topic:
        st.session_state.current_topic = selected_topic
        st.session_state.messages.append({"role": "assistant", "content": f"Switched to topic: {selected_topic}. Ask me anything about it!"})
    
    # Progress update
    current_status = next((t["status"] for t in stack["topics"] if t["name"] == st.session_state.current_topic), "not_started")
    new_status = st.selectbox("Update Progress", ["not_started", "discussing", "interview_ready", "completed"], index=["not_started","discussing","interview_ready","completed"].index(current_status))
    if new_status != current_status:
        update_topic_status(st.session_state.current_topic, new_status)
        st.success(f"Marked {st.session_state.current_topic} as {new_status}")
    
    # Generate interview Q&A
    if st.button("📝 Generate Interview Q&A"):
        with st.spinner("Generating..."):
            result = generate_interview_questions(st.session_state.current_topic)
        st.success(result)
    
    # Show interview Q&A if exists
    qa_text = load_interview_questions(st.session_state.current_topic)
    if qa_text:
        with st.expander("📖 Saved Interview Q&A"):
            st.markdown(qa_text)
    else:
        st.info("No interview Q&A yet. Click 'Generate' above.")
    
    st.divider()
    st.caption("All data stays on your laptop. Uses Groq for LLM.")

# Chat interface
st.header(f"💬 Discussing: {st.session_state.current_topic}")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
if prompt := st.chat_input("Ask your question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Retrieve similar past conversation (optional)
    past = st.session_state.memory.retrieve_similar(prompt, n_results=2)
    context = "\n".join(past) if past else ""
    
    # Build prompt for Groq
    system = f"You are a friendly tutor. Current topic: {st.session_state.current_topic}. Use the following context if relevant:\n{context}"
    full_prompt = f"User: {prompt}\nAssistant:"
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = call_groq(full_prompt, system=system)
        st.markdown(response)
    
    # Save to memory and chat history
    st.session_state.memory.add_chat_message(prompt, response, st.session_state.current_topic)
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to update UI (automatically handled by Streamlit)
    st.rerun()