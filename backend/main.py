from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from backend.pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest, ChallengeRequest, EvaluateAnswer
from backend.langchain_utils import generate_response, retrieve
from backend.db_utils import insert_application_logs, get_chat_history, get_all_documents, insert_document_record, delete_document_record, get_file_content
from backend.pinecone_utilis import index_document_to_pinecone, delete_doc_from_pinecone, load_and_split_document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
import os
import uuid
import logging
import shutil

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()

@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    session_id = query_input.session_id or str(uuid.uuid4())
    logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}")
    chat_history = get_chat_history(session_id)
    print(chat_history)
    state={"messages"chat_history} # test
    messages_state = generate_response(query=query_input.question, state=state)
    answer=messages_state["messages"][-1].content

    insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
    logging.info(f"Session ID: {session_id}, AI Response: {answer}")
    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)

@app.post('/challenge-me', response_model=list[str])
def challenge_me(request: ChallengeRequest):
    file_id = request.file_id
    
    content = get_file_content(file_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Document not found")

    
    llm = ChatOpenAI(
        model='gpt-4.1',
        api_key=OPENAI_API_KEY
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant. Generate three logic-based or comprehension-focused questions about the following document. Each question should require understanding or reasoning about the document content, not just simple recall. Provide each question on a new line."),
        ("human", "Document: {context}\n\nQuestions:")
    ])
    chain = prompt | llm | StrOutputParser()
    questions_str = chain.invoke({"context": content})
    questions = [q.strip() for q in questions_str.split('\n') if q.strip()][:3]

    return questions



@app.post('/evaluate-response')
def evaluate_response(request: EvaluateAnswer):
    # get the file ralated to answers
    file_id = request.file_id
    question = request.question
    user_answer=request.user_answer

    # evaluate the useranswer according to the research paper

    llm = ChatOpenAI(
        model='gpt-4.1',
        api_key=OPENAI_API_KEY
    )
    # get the context from doc
    retrieved_docs=retrieve(query=question)
    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)


    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant. Your task is to evaluate the user's answer to a question, using ONLY the information below as reference. If the answer is not correct, explain why and provide the correct answer with justification from the document. Do not make up information."),
        ("system", "Context: {context}"),
        ("human", "Question: {question}\nUser Answer: {user_answer}\nEvaluation:")
    ])

    chain = prompt | llm | StrOutputParser()
    evaluation = chain.invoke({
        "context": docs_content,
        "question": question,
        "user_answer": user_answer
    })

    return {
        "feedback": evaluation,
        "file_id": file_id
    }



@app.post("/upload-doc")
def upload_and_index_document(file: UploadFile = File(...), session_id: str = Form(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    allowed_extensions = ['.pdf', '.txt']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")

    temp_file_path = f"temp_{file.filename}"

    try:
        # Save the uploaded file to a temporary file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        docs = load_and_split_document(temp_file_path)
        docs_content = "\n\n".join(doc.page_content for doc in docs)
        file_id = insert_document_record(session_id, file.filename, docs_content)
        success = index_document_to_pinecone(temp_file_path, file_id)

        if success:
            # generate summary

            llm = ChatOpenAI(
                model='gpt-4.1',
                api_key=OPENAI_API_KEY
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant. Summarize the following document in no more than 150 words. Focus on the main points and key findings. Do not include information not present in the document."),
                ("human", "{document}")
            ])
            chain = prompt | llm | StrOutputParser()
            summary = chain.invoke({"document": docs_content})
            return {
                "message": f"File {file.filename} has been successfully uploaded and indexed.",
                "file_id": file_id,
                "summary": summary
            }
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
    finally:
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/list-docs", response_model=list[DocumentInfo])
def list_documents(session_id: str):
    return get_all_documents(session_id)

@app.post("/delete-doc")
def delete_document(request: DeleteFileRequest):
    pinecone_delete_success = delete_doc_from_pinecone(request.file_id)

    if pinecone_delete_success:
        db_delete_success = delete_document_record(request.file_id)
        if db_delete_success:
            return {"message": f"Successfully deleted document with file_id {request.file_id} from the system."}
        else:
            return {"error": f"Deleted from pinecone but failed to delete document with file_id {request.file_id} from the database."}
    else:
        return {"error": f"Failed to delete document with file_id {request.file_id} from pinecone."}
