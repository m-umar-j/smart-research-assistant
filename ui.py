import streamlit as st
import requests

# Set the FastAPI backend URL
FASTAPI_URL = "http://localhost:8000"

st.title("Smart Research Assistant")

# Document Upload Section
uploaded_file = st.file_uploader("Upload a PDF or TXT document", type=["pdf", "txt"])
if uploaded_file:
    files = {"file": uploaded_file}
    response = requests.post(f"{FASTAPI_URL}/upload-doc", files=files)
    if response.status_code == 200:
        result = response.json()
        st.success(result["message"])
        file_id = result["file_id"]
        # Here you would also call a summary endpoint if implemented
        # For demo, assume summary is returned in the upload response
        # st.write("Summary: ", result.get("summary", "Summary not available"))
    else:
        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# List Documents (optional)
if st.button("List Documents"):
    response = requests.get(f"{FASTAPI_URL}/list-docs")
    if response.status_code == 200:
        documents = response.json()
        st.write("Available Documents:")
        for doc in documents:
            st.write(f"- {doc['filename']} (ID: {doc['file_id']})")
    else:
        st.error("Failed to list documents")

# Interaction Modes
mode = st.radio("Choose Mode", ["Ask Anything", "Challenge Me"])

if mode == "Ask Anything":
    question = st.text_input("Ask a question about the document")
    if question and st.button("Submit"):
        payload = {
            "question": question,
            "session_id": "user123",  # Replace with actual session management
            "model": "default"        # Replace with your model selection
        }
        response = requests.post(f"{FASTAPI_URL}/chat", json=payload)
        if response.status_code == 200:
            result = response.json()
            st.write("Answer:", result["answer"])
            # If your backend returns a source snippet, display it:
            # st.write("Source:", result.get("source", ""))
        else:
            st.error("Failed to get answer")

# elif mode == "Challenge Me":
#     if st.button("Generate Challenge Questions"):
        
#         # Assume your backend has a `/generate-questions` endpoint
#         # response = requests.post(f"{FASTAPI_URL}/generate-questions", json={"file_id": file_id})
#         # if response.status_code == 200:
#         #     questions
