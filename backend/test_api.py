"""Script to test FastAPI endpoints without the Angular frontend."""

import json
import requests

BASE = "http://localhost:8000"

print("=== Test 1: GET /health ===")
r = requests.get(f"{BASE}/health")
print(r.status_code, r.json())

print("\n=== Test 2: GET /tools ===")
r = requests.get(f"{BASE}/tools")
for tool in r.json():
    print(f"  - {tool['name']}: {tool['description']}")

print('\n=== Test 3: POST /chat ===')
payload = {
    "message": "Search the web for Python asyncio tutorial and save a summary to asyncio_notes.txt"
}
r = requests.post(f"{BASE}/chat", json=payload, stream=True)

session_id = None

for line in r.iter_lines(decode_unicode=True):
    if not line:
        continue
    if line.startswith("data: "):
        data = json.loads(line[6:])
        event_type = data["type"]

        if event_type == "tool_call":
            print(f"[TOOL] {data['tool']}: {data['input']}")
        elif event_type == "text":
            print(f"[RESPONSE] {data['content']}")
        elif event_type == "error":
            print(f"[ERROR] {data['message']}")
        elif event_type == "done":
            print("[DONE]")
            break

print(f"\nSession ID: {session_id}")
