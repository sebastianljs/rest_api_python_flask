FROM python:3.6.4-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    make \
    gcc \
    python3-dev \
    mongodb

RUN mkdir /opt/pets-api
WORKDIR /opt/pets-api
ADD . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD python pets_api/manage.py run-server

