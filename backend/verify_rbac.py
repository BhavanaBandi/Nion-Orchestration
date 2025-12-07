import asyncio
import httpx
from termcolor import colored

BASE_URL = "http://localhost:8000"

async def get_token(username, password):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/token",
            data={"username": username, "password": password}
        )
        if response.status_code != 200:
            print(f"Login failed for {username}: {response.text}")
            return None
        return response.json()["access_token"]

async def test_orchestration(username, role_name):
    print(colored(f"\nTesting RBAC for {username} ({role_name})...", "cyan"))
    
    token = await get_token(username, "password123")
    if not token:
        return

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/orchestrate",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "content": "We need a landing page by next Friday.",
                "source": "api_test",
                "sender": {"name": username, "role": role_name}
            },
            timeout=60.0 # Increase timeout for orchestration
        )
        
        if response.status_code != 200:
            print(colored(f"Request failed: {response.text}", "red"))
            return

        data = response.json()
        
        # Check Visibility
        print("Response Keys:", list(data.keys()))
        
        if "orchestration_map" in data and "L1 Task Plan" in str(data["orchestration_map"]):
             print(colored("  [+] Can see Orchestration Map", "green"))
        elif "orchestration_map" in data and "REDACTED" in data["orchestration_map"]:
             print(colored("  [-] Orchestration Map is REDACTED", "yellow"))
        elif "customer_view" in data:
             print(colored("  [!] Received CUSTOMER SUMMARY (Sanitized)", "blue"))
             print(f"  Summary: {data.get('summary')}")
        else:
             print(colored("  [?] Unknown Response Format", "magenta"))

async def main():
    # 1. Test Admin (Project Manager)
    await test_orchestration("admin", "project_manager")
    
    # 2. Test Customer (Customer)
    await test_orchestration("customer_dave", "customer")
    
    # 3. Test Engineer (Engineer)
    # await test_orchestration("engineer_bob", "engineer")

if __name__ == "__main__":
    try:
        import termcolor
    except ImportError:
        import os
        os.system("pip install termcolor")
        
    asyncio.run(main())
