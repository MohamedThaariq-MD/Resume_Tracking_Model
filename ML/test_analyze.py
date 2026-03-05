import requests

url = "http://127.0.0.1:8000/analyze_resume"
file_path = "d:\\ResumeTracker\\Backend API\\uploads\\1772449471168.pdf"

with open(file_path, "rb") as f:
    files = {"file": (file_path, f, "application/pdf")}
    response = requests.post(url, files=files)

print("Status Code:", response.status_code)
print("Response Text:", response.text)
