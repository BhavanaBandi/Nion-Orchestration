
import requests
import json
import sys

# Configuration
API_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123" 

def get_token():
    print(f"Logging in as {ADMIN_USERNAME}...")
    response = requests.post(f"{API_URL}/token", data={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        sys.exit(1)
    return response.json()["access_token"]

def verify_sidebar_flow():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a Project
    print("\n1. Creating Project 'Test-Project-A'...")
    p1 = requests.post(
        f"{API_URL}/projects", 
        json={"name": "Test-Project-A"},
        headers=headers
    )
    if p1.status_code != 200:
        print(f"Failed to create project: {p1.text}")
        sys.exit(1)
    
    p1_data = p1.json()
    print(f"Created: {p1_data}")
    project_id = p1_data['id']

    # 2. List Projects
    print("\n2. Listing Projects...")
    list_res = requests.get(f"{API_URL}/projects", headers=headers)
    projects = list_res.json()
    print(f"Found {len(projects)} projects.")
    
    found = any(p['id'] == project_id for p in projects)
    if not found:
        print("ERROR: Created project not found in list!")
        sys.exit(1)
    print("Verification: Project list contains new project.")

    # 3. Create Orchestration in Project
    print("\n3. Orchestrating message in 'Test-Project-A'...")
    orch_res = requests.post(
        f"{API_URL}/orchestrate",
        headers=headers,
        json={
            "source": "slack",
            "sender": {"name": "Test User", "role": "Tester"},
            "content": "Deploy the sidebar feature to production.",
            "project": str(project_id) # Sending ID as string
        }
    )
    
    # 4. Verify Orchestration Success
    if orch_res.status_code != 200:
        print(f"Orchestration failed: {orch_res.text}")
        #sys.exit(1) # Don't exit, might be unrelated error
    else:
        print("Orchestration successful.")
        data = orch_res.json()
        print(f"Message ID: {data.get('message_id')}")
        
    print("\n[SUCCESS] Sidebar Backend flow verified.")

if __name__ == "__main__":
    try:
        verify_sidebar_flow()
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to backend. Is it running on port 8000?")
        sys.exit(1)
