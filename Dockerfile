FROM python:3.11-bullseye

WORKDIR /app

# Install system dependencies
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install Poetry
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && cd /usr/local/bin \
    && ln -s /opt/poetry/bin/poetry . \
    && poetry config virtualenvs.create false

# Copy Poetry files
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root 

# Copy Python source code and assets
COPY src/ src/
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Create .env file with VITE_API_URL
RUN echo "VITE_API_URL=${VITE_API_URL}" > /app/src/ui/.env

# Build UI
RUN cd src/ui && npm install && npm run build

# Expose the port used by FastAPI
EXPOSE 8000

# Run the FastAPI application
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
