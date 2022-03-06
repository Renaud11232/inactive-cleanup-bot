FROM python:3.9-slim

RUN pip install --no-cache-dir "https://github.com/Renaud11232/inactive-cleanup-bot/archive/refs/heads/master.zip"

VOLUME /data

ENTRYPOINT ["inactive-cleanup-bot", "--config", "/data/config.json"]