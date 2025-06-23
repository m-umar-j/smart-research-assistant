# 1. Auto-summarization prompt template
AUTO_SUMMARY_TEMPLATE = """
Summarize the following document in no more than 150 words. Focus on the main points and key findings. Do not include information not present in the document.

DOCUMENT:
{document}

SUMMARY:
"""

# 2. Question answering prompt template
QA_PROMPT_TEMPLATE = """
Answer the following question based only on the provided document. Your answer must be grounded in the document and include a specific reference to the text that supports your answer.

Document:
{document}

Question:
{question}

Answer:
"""

# 3. Logic-based question generation prompt template
LOGIC_QUESTION_GENERATION_TEMPLATE = """
Generate three logic-based or comprehension-focused questions about the following document. Each question should require understanding or reasoning about the document content, not just simple recall. Provide each question on a new line.

Document:
{document}

Questions:
"""

# 4. Answer evaluation prompt template
ANSWER_EVALUATION_TEMPLATE = """
Evaluate the following user answer to the question, using only the provided document as the source of truth. State whether the answer is correct or not, and provide a brief justification referencing the document.

Document:
{document}

Question:
{question}

User Answer:
{user_answer}

Evaluation:
"""

# 5. For memory/follow-up: Chat prompt template
CHAT_PROMPT_TEMPLATE = """
The following is a conversation between a user and an AI assistant about a document. The assistant answers questions and provides justifications based on the document. Use the conversation history and the document to answer the new question.

Document:
{document}

Conversation History:
{history}

Question:
{question}

Answer:
"""
