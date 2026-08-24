Markdown
# ML Model Deployment with FastAPI & Docker

This project serves a Scikit-Learn Machine Learning pipeline via a FastAPI web server, fully containerized using Docker. It supports running multiple API versions side-by-side.

## 1. Local Testing (Without Docker)

Test the API directly on your machine before containerizing:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --host 0.0.0.0 --port 8000
Visit http://localhost:8000/docs to view the Swagger UI and test the endpoints.


## 2. Docker Deployment: Version 1
Build and run the initial version of the API inside an isolated Docker container.

Bash
# Build the v1 image
docker build -t ml-deployment-docker:v1 .

# Run v1 on port 8000
docker run -p 8000:8000 ml-deployment-docker:v1

## 3. Deploying Version 2 (Side-by-Side)
To deploy a second version without overwriting the first, follow these steps:

Step A: Code Changes (app.py)
Change the FastAPI title or welcome message to explicitly say "Version 2".

Crucial: If you change the model loading path (e.g., joblib.load("models/v2/pipeline.pkl")), you must ensure that you have actually saved a new model in that exact folder. Otherwise, the app will crash with a FileNotFoundError.

Step B: Build and Run
Build the new image and map it to a different external port (e.g., 8001) so it doesn't conflict with v1.

Bash

# Build the v2 image

docker build -t ml-deployment-docker:v2 .

# Run v2 on port 8001 (Internal container port stays 8000)
docker run -p 8001:8000 ml-deployment-docker:v2
You can now access v1 at http://localhost:8000/docs and v2 at http://localhost:8001/docs simultaneously!



## ⚖️ 5. A/B Testing & Canary Deployments

This API supports dynamic traffic splitting between Version 1 and Version 2 models using deterministic hashing based on the `user_id`. 

We control the traffic split using the `CANARY_PCT` environment variable. **No code redeployment is required to change the split!**

```bash
# Build the unified A/B testing image
docker build -t ml-deployment-docker:latest .

# 🧪 CANARY DEPLOYMENT: Send 10% of users to v2, 90% to v1
docker run -p 8000:8000 -e CANARY_PCT=10 ml-deployment-docker:latest

# 🚀 FULL PROMOTION: Send 100% of users to v2
docker run -p 8000:8000 -e CANARY_PCT=100 ml-deployment-docker:latest

# 🛑 INSTANT ROLLBACK: Send 0% of users to v2 (100% to v1)
docker run -p 8000:8000 -e CANARY_PCT=0 ml-deployment-docker:latest