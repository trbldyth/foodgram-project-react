FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]
