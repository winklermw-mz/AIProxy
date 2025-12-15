docker build -t winklermw-mz/aiproxy .
docker run -d --name AIProxy --env-file .env --network my-local-net -v $(pwd)/.env:/app/.env:ro -p 8001:8001 winklermw-mz/aiproxy
