# syntax = docker/dockerfile:1.2

FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY VTServerList.py .

CMD [ "python", "./VTServerList.py" ]
