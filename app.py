from backend.pinecone_utilis import create_pinecone_vectorstore,load_and_split_document, index_document_to_pinecone

file_path="InternTaskGenAI.pdf"

print(index_document_to_pinecone(file_path=file_path, file_id=1))
