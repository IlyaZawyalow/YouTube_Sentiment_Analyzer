FROM python:3.11-slim

WORKDIR /ml_service
COPY ./requirements.txt /ml_service/requirements.txt
RUN apt-get update \
    && apt-get install -y build-essential python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
COPY . /ml_service

CMD ["python", "ml_service.py"]