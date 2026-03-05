import requests
import json

url = "http://127.0.0.1:8000/calculate_ats"

req_data = json.dumps({
    "title": "Software Engineer",
    "description": "Looking for a software engineer with python.",
    "required_skills": ["python", "machine learning"]
})

payload = {
    'req': req_data,
    'resume_text': "I am a software engineer with 5 years experience in python and machine learning."
}

try:
    response = requests.post(url, data=payload)
    print(response.status_code)
    print(response.text)
except Exception as e:
    print(e)
