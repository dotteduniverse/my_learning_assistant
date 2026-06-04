import streamlit as st
import json
import os
import subprocess
from core.stack_manager import load_stack, update_topic_status, save_stack
from core.interview import generate_interview_questions, load_interview_questions

st.set_page_config(page_title="AI Learning Assistant Dashboard", layout="wide")
st.title("📚 AI Learning Assistant – Progress Dashboard")

# Sidebar: Info
st.sidebar.header("About")
st.sidebar.info(
    "This dashboard tracks your learning progress.\n\n"
    "Use the CLI assistant for conversation and quizzes.\n"
    "Status changes here are saved immediately."
)

# Load current stack
stack = load_stack()

# Display topics in expandable cards
st.subheader("📖 Your Tech Stack Progress")

for idx, topic in enumerate(stack['topics']):
    with st.expander(f"### {topic['name']} – *{topic['status']}*"):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write("**Subtopics:**")
            for sub in topic['subtopics']:
                st.write(f"- {sub}")
            st.text_area("Personal notes", value=topic.get('notes', ''), key=f"notes_{idx}", height=100)
        
        with col2:
            new_status = st.selectbox(
                "Status",
                options=["not_started", "discussing", "interview_ready", "completed"],
                index=["not_started","discussing","interview_ready","completed"].index(topic['status']),
                key=f"status_{idx}"
            )
            if new_status != topic['status']:
                update_topic_status(topic['name'], new_status)
                st.rerun()
        
        with col3:
            if st.button(f"📝 Generate Interview Q&A", key=f"gen_{idx}"):
                with st.spinner(f"Generating interview for {topic['name']}..."):
                    result = generate_interview_questions(topic['name'])
                st.success(result)
            
            qa_text = load_interview_questions(topic['name'])
            if qa_text:
                if st.button(f"📖 Show Interview Q&A", key=f"show_{idx}"):
                    st.text_area("Interview Questions & Answers", qa_text, height=300)
            else:
                st.info("No interview Q&A yet. Click 'Generate'.")

# Add new topic section
st.subheader("➕ Add a New Topic")
with st.form("new_topic_form"):
    new_name = st.text_input("Topic name")
    new_subtopics = st.text_input("Subtopics (comma separated)", placeholder="e.g., LLMOps, Prompt Flow")
    submitted = st.form_submit_button("Add Topic")
    if submitted and new_name:
        from core.stack_manager import add_topic
        subs = [s.strip() for s in new_subtopics.split(",")] if new_subtopics else []
        add_topic(new_name, subs)
        st.success(f"Topic '{new_name}' added. Refresh the page to see it.")
        st.rerun()

# Export Mermaid diagram
st.sidebar.subheader("📤 Export")
if st.sidebar.button("Export current stack to Mermaid"):
    from core.stack_manager import load_stack
    stack = load_stack()
    lines = ["graph TD"]
    for t in stack['topics']:
        node_id = t['name'].replace(" ", "_")
        lines.append(f"    {node_id}[\"{t['name']}\"]")
    with open("exported_stack.mmd", "w") as f:
        f.write("\n".join(lines))
    st.sidebar.success("Exported to exported_stack.mmd")

# Option to open CLI assistant (note: CLI must be run separately)
st.sidebar.markdown("---")
st.sidebar.info("💬 **Conversation & Quizzes**\nRun the CLI assistant in a terminal:\n```bash\npython assistant.py\n```")