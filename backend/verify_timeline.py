import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestration.timeline_engine import TimelineEngine
from llm.grok_client import GroqClient

async def run_tests():
    client = GroqClient()
    engine = TimelineEngine(client=client)
    
    test_cases = [
        {
            "name": "Explicit Deadline",
            "content": "We need the report by 2025-12-25 so we can review it."
        },
        {
            "name": "Relative Date",
            "content": "Please finish this by next Friday."
        },
        {
            "name": "High Urgency",
            "content": "ASAP! System is down, fix it immediately!"
        },
        {
            "name": "Conflict: Past Deadline",
            "content": "This was due on 2020-01-01. Why isn't it done?"
        },
        {
            "name": "Conflict: Multiple Deadlines",
            "content": "I need this done by tomorrow. Also, let's target next month for complection."
        }
    ]
    
    print(f"=== Running Timeline Engine Verification ({datetime.now().date()}) ===")
    
    for case in test_cases:
        print(f"\nTest: {case['name']}")
        print(f"Input: {case['content']}")
        
        try:
            result = await engine.analyze(case['content'])
            
            print("Events:")
            for event in result.events:
                print(f"  - [{event.date.normalized}] {event.description} (Urgency: {event.urgency_score})")
                
            print("Conflicts:")
            if result.conflicts:
                for conflict in result.conflicts:
                    print(f"  - [{conflict.severity.upper()}] {conflict.description}")
            else:
                print("  - None")
                
            print("Recommendations:")
            if result.recommendations:
                for rec in result.recommendations:
                    print(f"  - {rec}")
            else:
                print("  - None")
                
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
