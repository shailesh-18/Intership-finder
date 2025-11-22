import requests

url = "http://127.0.0.1:5000/recommend"

payload = {
    "skills": ["python", "flask", "web scraping"],
    "interests": "backend development, APIs, data engineering",
    "location_preference": "remote or Bangalore",
    "experience_level": "beginner",
    "top_k": 5
}

response = requests.post(url, json=payload)

print("Status:", response.status_code)
print("Response JSON:")
print(response.json())
