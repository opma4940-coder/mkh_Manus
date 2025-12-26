FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn pydantic celery redis
COPY . .
CMD ["python", "main.py"]
