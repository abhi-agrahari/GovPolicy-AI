FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir torch==2.14.1 \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
