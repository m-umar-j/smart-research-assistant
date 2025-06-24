
import requests

# Set the FastAPI backend URL
BASE_URL = "http://localhost:8000"


# with open("neural computing cwsi.pdf", "rb") as f:
#     files = {"file": ("neural computing cwsi.pdf", f, "text/plain")}
#     upload_response = requests.post(f"{BASE_URL}/upload-doc", files=files)
# # print("Upload Response:", upload_response.json())

# file_id = upload_response.json().get("summary")

# print(file_id)

chat_data = {"question": "What is the main topic?", "model": "gpt-4o-mini"}
chat_response = requests.post(f"{BASE_URL}/chat", json=chat_data)
print("Chat Response:", chat_response.json())

# delete_data={"file_id": 1}

# delete_response = requests.post(f"{BASE_URL}/delete-doc", json=delete_data)

# print("Delete Response:", delete_response.json())