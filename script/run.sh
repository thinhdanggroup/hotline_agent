echo "VITE_API_URL=${VITE_API_URL}" > src/ui/.env

echo "Starting the server... with VITE_API_URL=${VITE_API_URL}"
make build
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port ${PORT:-8000}
