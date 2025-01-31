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

# Copy UI files and build
COPY src/ui/ src/ui/
RUN cd src/ui && npm install && npm run build

# Copy Python source code and assets
COPY src/ src/

# Expose the port used by FastAPI
EXPOSE 8000

# Run the FastAPI application
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
