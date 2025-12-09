FROM python:3.9-slim

WORKDIR /app

COPY app.py .

RUN mkdir /data

CMD ["python", "app.py"]
