import requests
from collections import Counter

# Make sure your Docker container is running on port 8000!
url = "http://localhost:8000/predict"

print("Simulating 100 different users hitting the API...")
results = []

for i in range(100):
    # Generate 100 unique users
    payload = {
        "features": [0.0] * 10,  # 10 dummy features
        "user_id": f"user_{i}"
    }

    # Send the request to your Docker API
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        # Extract which model served the request
        version_used = response.json().get("model_version")
        results.append(version_used)
    else:
        print(f"Error on user_{i}: {response.text}")

# Count the results
counts = Counter(results)
print("\n" + "="*30)
print("🚦 TRAFFIC SPLIT RESULTS 🚦")
print("="*30)
print(f"Total Requests: {len(results)}")
print(f"Routed to v1: {counts.get('v1', 0)}")
print(f"Routed to v2: {counts.get('v2', 0)}")
print("="*30)
