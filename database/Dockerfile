# Use a slim Python base image to keep the container small
FROM python:3.12-slim

WORKDIR /app

# Copy and install dependencies first - Docker caches this layer
# so it won't reinstall packages on every code change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . .

# uvicorn is the server that runs FastAPI
# 0.0.0.0 makes it reachable from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5555"]