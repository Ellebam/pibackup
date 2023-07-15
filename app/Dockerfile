FROM python:3.8-slim

WORKDIR /app

COPY backups.py .
COPY serviceaccount.json .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "backups.py"]
