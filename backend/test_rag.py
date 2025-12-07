import requests
import json

def test_rag():
    url = "http://127.0.0.1:8000/rag/chat"
    payload = {"question": "What does the Nion Orchestration Engine do?"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        print("Status:", response.status_code)
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print("Error during request:", e)

if __name__ == "__main__":
    test_rag()
