FROM python:3.11-slim

WORKDIR /app

COPY ../../apps /app/apps
COPY ../../shared /app/shared
COPY apps/scripts/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8015

CMD ["python", "apps/scripts/src/main.py"]
