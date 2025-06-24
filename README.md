---
title: Smart Research Assistant
emoji: 👁
colorFrom: yellow
colorTo: red
sdk: docker
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# smart-research-assistant

## TODO:
- [] pinecone utilis
- [] RAG component using langchain/langgraph
- [] database setup
- [] backend using FastAPI
- [] frontend using streamlit
## Deliverabilities
- Answer questions that require comprehension and inference
- Pose logic-based questions to users and evaluate their responses
- Justify every answer with a reference from the document
### Functional Requirements
- Input file (pdf/txt)
- 2 modes (a) Ask anything (b) challenge me
- Auto summary after document upload
- Streamlit + FastAPI (current stack)
- Bonus features i.e. state management and context highlighting