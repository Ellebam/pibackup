FROM python:3.8-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y curl unzip && curl https://rclone.org/install.sh | bash \
    && mkdir -p ../tempbackups ../backups

CMD ["python", "backups.py"]
