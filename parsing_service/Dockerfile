FROM python:3.8-slim

WORKDIR /parsing_service
COPY ./requirements.txt /parsing_service/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /parsing_service

CMD ["python", "parsing_service.py"]