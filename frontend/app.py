import streamlit as st
import requests
import uuid
from datetime import datetime

# Backend URL configuration
BACKEND_URL = "http://localhost:8000"  

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "current_file" not in st.session_state:
    st.session_state.current_file = None
if "challenge_questions" not in st.session_state:
    st.session_state.challenge_questions = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# Page setup
st.set_page_config(page_title="Research Assistant", layout="wide")
st.title("📚 Smart Research Assistant")

# Document management sidebar
with st.sidebar:
    st.header("Document Management")
    
    # Document upload
    uploaded_file = st.file_uploader("Upload Document (PDF/TXT)", type=["pdf", "txt"])
    if uploaded_file:
        if st.button("Upload Document"):
            response = requests.post(
                f"{BACKEND_URL}/upload-doc",
                files={"file": (uploaded_file.name, uploaded_file, "application/octet-stream")},
                data={"session_id": st.session_state.session_id}
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.current_file = data["file_id"]
                st.success(f"Document uploaded successfully! ID: {data['file_id']}")
                with st.expander("Document Summary"):
                    st.write(data["summary"])
            else:
                st.error("Failed to upload document")
    
    # List documents
    st.subheader("Uploaded Documents")
    try:
        documents = requests.get(f"{BACKEND_URL}/list-docs", params={"session_id": st.session_state.session_id}).json()
        for doc in documents:
            doc_id = doc["id"]
            with st.container(border=True):
                st.write(f"**{doc['filename']}**")
                st.caption(f"Uploaded: {datetime.fromisoformat(doc['upload_timestamp']).strftime('%Y-%m-%d %H:%M')}")
                st.caption(f"ID: {doc_id}")
                
                # Document selection
                if st.button(f"Select", key=f"select_{doc_id}"):
                    st.session_state.current_file = doc_id
                
                # Document deletion
                if st.button(f"Delete", key=f"del_{doc_id}"):
                    del_response = requests.post(
                        f"{BACKEND_URL}/delete-doc",
                        json={"file_id": doc_id}
                    )
                    if del_response.status_code == 200:
                        st.rerun()
                    else:
                        st.error("Deletion failed")
    except:
        st.warning("No documents available")

# Main interaction tabs
ask_tab, challenge_tab = st.tabs(["Ask Anything", "Challenge Me"])

with ask_tab:
    st.subheader("Document Chat")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if st.session_state.current_file:
        # Display chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**Assistant:** {msg['content']}")

        # Chat input
        user_question = st.text_input("Type your question and press Enter:", key="chat_input")
        send = st.button("Send", key="send_chat")
        if send and user_question.strip():
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_question})

            # Send to backend
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={
                    "question": user_question,
                    "session_id": st.session_state.session_id,
                    "model": "gpt-4o-mini"
                }
            )
            if response.status_code == 200:
                data = response.json()
                # Add assistant response to history
                st.session_state.chat_history.append({"role": "assistant", "content": data["answer"]})
                st.experimental_rerun()
            else:
                st.error("Failed to get response")
    else:
        st.warning("Please select a document first")

with challenge_tab:
    st.subheader("Document Comprehension Challenge")
    
    if st.session_state.current_file:
        # Generate questions
        if st.button("Generate Challenge Questions"):
            response = requests.post(
                f"{BACKEND_URL}/challenge-me",
                json={"file_id": st.session_state.current_file}
            )
            if response.status_code == 200:
                st.session_state.challenge_questions = response.json()
            else:
                st.error("Failed to generate questions")
        
        # Display questions and answer inputs
        if st.session_state.challenge_questions:
            for i, question in enumerate(st.session_state.challenge_questions):
                st.subheader(f"Question {i+1}")
                st.write(question)
                
                user_answer = st.text_input(
                    f"Your answer for question {i+1}:",
                    key=f"answer_{i}"
                )
                
                # Store answers
                st.session_state.user_answers[i] = user_answer
                
                # Evaluate answer
                if st.button(f"Evaluate Answer {i+1}", key=f"eval_{i}"):
                    response = requests.post(
                        f"{BACKEND_URL}/evaluate-response",
                        json={
                            "file_id": st.session_state.current_file,
                            "question": question,
                            "user_answer": user_answer
                        }
                    )
                    if response.status_code == 200:
                        feedback = response.json()
                        st.session_state.feedback[i] = feedback
                        st.success("Answer evaluated!")
                    else:
                        st.error("Evaluation failed")
                
                # Show feedback
                if i in st.session_state.feedback:
                    with st.expander(f"Feedback for Question {i+1}"):
                        st.write(st.session_state.feedback[i]["feedback"])
    else:
        st.warning("Please select a document first")

# Session info
st.sidebar.divider()
st.sidebar.caption(f"Session ID: `{st.session_state.session_id}`")
