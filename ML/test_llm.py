from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_analyze():
    print("Testing /llm/analyze...")
    payload = {
        "jd_text": "Looking for a seasoned Full Stack Engineer with strong experience in Python, FastAPI, React, and MongoDB. AWS is a plus.",
        "resume_text": "I am a software developer with 4 years of experience building web applications using JavaScript, React, and Node.js. I have also used Python for a few small scripts."
    }
    try:
        response = client.post("/llm/analyze", json=payload)
        response.raise_for_status()
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Details: {response.text}")

def test_chat():
    print("\nTesting /llm/chat...")
    payload = {
        "resume_text": "I am a software developer with 4 years of experience building web applications using JavaScript, React, and Node.js. I have also used Python for a few small scripts.",
        "question": "Does this candidate have backend experience?"
    }
    try:
        response = client.post("/llm/chat", json=payload)
        response.raise_for_status()
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Details: {response.text}")

if __name__ == "__main__":
    test_analyze()
    test_chat()

