from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from typing import List
from langchain_core.documents import Document
import os
from dotenv import load_dotenv
load_dotenv()

# API keys
PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")



# text splitter and embedding function
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1024, api_key=OPENAI_API_KEY)

# Pinecone vector store
pc = Pinecone(api_key=PINECONE_API_KEY)

def load_and_split_document(file_path: str) -> List[Document]:
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.txt'):
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    documents = loader.load()
    return text_splitter.split_documents(documents)

INDEX_NAME = "smart-research-assistant"

def create_pinecone_vectorstore()-> PineconeVectorStore:
    try:
        if not pc.has_index(INDEX_NAME):
            pc.create_index(
                name=INDEX_NAME,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        index = pc.Index(INDEX_NAME)
        return PineconeVectorStore(index=index, embedding=embeddings)

    except Exception as e:
        print(f"Index initialization failed: {e}")
        raise


vectorstore=create_pinecone_vectorstore()

def index_document_to_pinecone(file_path: str, file_id: int) -> bool:
    try:
        splits = load_and_split_document(file_path)

        # Add metadata to each split
        for split in splits:
            split.metadata['file_id'] = file_id

        vectorstore.add_documents(splits)
        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False
    
def delete_doc_from_pinecone(file_id: int):
    try:
        index = pc.Index(INDEX_NAME)
        # Query for all vectors with file_id metadata
        query_result = index.query(
            vector=[0.0]*1024,  
            filter={"file_id": {"$eq": str(file_id)}},
            top_k=10000,  
            include_metadata=True
        )
        ids = [match["id"] for match in query_result["matches"]]
        if ids:
            index.delete(ids=ids)
        return True
    except Exception as e:
        print(f"Error deleting from Pinecone: {str(e)}")
        return False

