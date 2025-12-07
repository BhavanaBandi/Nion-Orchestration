
import requests
import json
import sys

# Configuration
API_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123" 

def get_token():
    print(f"Logging in as {ADMIN_USERNAME}...")
    try:
        response = requests.post(f"{API_URL}/token", data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            sys.exit(1)
        return response.json()["access_token"]
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to localhost:8000")
        sys.exit(1)

def test_rag():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    print("\nTesting RAG Chatbot Endpoint...")
    payload = {
        "question": "What is Nion?",
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{API_URL}/rag/chat",
            headers=headers,
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Failed!")
            print(f"Error Text: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_rag()
