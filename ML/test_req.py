import requests
res = requests.post('http://localhost:8000/calculate_ats', data={'req': '{"title": "Engineer", "description": "Python, React, SQL", "required_skills": ["python", "react", "sql"]}', 'resume_text': 'I am a python react sql engineer.'})
print(res.json())
