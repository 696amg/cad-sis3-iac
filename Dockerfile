FROM --platform=linux/amd64 python:3.12-slim
RUN pip install --no-cache-dir boto3
WORKDIR /app
COPY app.py .
EXPOSE 8080
CMD ["python", "app.py"]
