---
title: Smart Research Assistant
emoji: 👁
colorFrom: yellow
colorTo: red
sdk: docker
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# Smart Research Assistant

A document-aware AI assistant for research summarization, question-answering, and logic-based question generation, built with FastAPI (backend) and Streamlit (frontend), deployed as a single Docker container.

Huggingface spaces link: https://huggingface.co/spaces/umar-100/smart-research-assistant

Loom demo link: https://www.loom.com/share/0a5302faa01e422394cda7a760c172f6?sid=b60a82e0-796b-416d-bc28-bad526a60fc5

---

## Features

- **Document Upload:** Upload PDF or TXT documents for processing.
- **Auto Summary:** Generate concise (≤150 words) summaries of uploaded documents.
- **Ask Anything:** Ask free-form questions and receive answers grounded in the uploaded document.
- **Challenge Me:** Generate three logic-based or comprehension-focused questions from the document.
- **Evaluate Responses:** Evaluate user answers to logic-based questions with feedback and justification.
- **Session Management:** Each user session is tracked for document and interaction history.
- **Vector Database Integration:** Uses Pinecone for semantic search and retrieval.
- **Clean UI:** Intuitive web interface for uploading, querying, and interacting with documents.

---

## Architecture

- **Backend:** FastAPI (Python)
  - Handles document upload, storage, and retrieval.
  - Implements endpoints for Q&A, question generation, and answer evaluation.
  - Uses SQLite for session/document management and Pinecone for vector search.
- **Frontend:** Streamlit (Python)
  - Provides a web interface for users to upload documents, ask questions, and receive feedback.
  - Communicates with the backend via HTTP requests.
- **Vector Database:** Pinecone
  - Stores document embeddings for semantic search and retrieval.
- **Deployment:** Single Docker container with both backend and frontend services.
  - FastAPI runs on port 8000 (internal).
  - Streamlit runs on port 7860 (exposed to users).
  - No Nginx or reverse proxy required for minimal setup.

---

## Setup

### Requirements

- **Docker**
- **Pinecone API key** (for vector search)
- **OpenAI API key** (for LLM inference)

---

### 1. Clone the Repository

```
git clone https://github.com/m-umar-j/smart-research-assistant.git
cd smart-research-assistant
```

---

### 2. Environment Variables

Create a `.env` file in the project root with the following variables:

```
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
```


---

### 3. Build and Run with Docker

docker build -t smart-research-assistant .
docker run -p 7860:7860 --env-file .env smart-research-assistant


- **Port 7860** is exposed for Streamlit.
- **Port 8000** is used internally for FastAPI.

---

### 4. Access the Application

Open your browser to:

http://localhost:7860


---

## Commands

- **Start Streamlit and FastAPI (via `start.sh`):**

```
cd /app && uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
cd /app && streamlit run frontend/app.py --server.port=7860 --server.address=0.0.0.0 --browser.gatherUsageStats=false --server.enableXsrfProtection=false
```


---

## Technical Details

### Backend

- **FastAPI endpoints:**
- `/upload-doc`: Upload and index documents (PDF/TXT).
- `/list-docs`: List documents by session.
- `/chat`: Answer questions based on uploaded documents.
- `/challenge-me`: Generate logic-based questions.
- `/evaluate-response`: Evaluate user answers to logic-based questions.
- **Database:** SQLite (`research_assistant.db`) for session/document storage.
- **Vector Database:** Pinecone for document embeddings and semantic retrieval.

### Frontend

- **Streamlit UI:**
- Upload documents.
- Display summaries.
- Ask questions and view answers.
- Generate and answer logic-based questions.
- View feedback on answers.

### Data Flow

1. **User uploads a document.**
2. **Document is split, embedded, and indexed in Pinecone.**
3. **User asks questions or requests logic-based questions.**
4. **Backend retrieves relevant document chunks and generates answers/feedback.**
5. **Frontend displays results to the user.**

---

## Known Issues & Workarounds

- **File uploads on Hugging Face Spaces:**  
- Disable XSRF protection in Streamlit (`--server.enableXsrfProtection=false`).
- File uploads may still be restricted by platform security policies.
- **Database permissions:**  
- Ensure `/app` is writable in Docker (handled by `chmod -R 777 /app` in Dockerfile).
- **Pinecone indexing:**  
- Ensure Pinecone index exists and API key is valid.

---

## Folder Structure

```
smart-research-assistant/
├── backend/           # FastAPI backend code
│   └── ...            
├── frontend/          # Streamlit frontend code
│   └── ...            
├── .env               # Environment variables
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker build file
├── start.sh           # Startup script
└── README.md          # This file

```


---

## Additional Notes

- **Session management:** Each user session is tracked with a unique ID.
- **Vector search:** Chunks of uploaded documents are embedded and indexed in Pinecone for semantic retrieval.
- **LLM integration:** Uses OpenAI's GPT-4 for question-answering and feedback generation.

---

