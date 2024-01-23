FROM ubuntu:latest
LABEL authors="LKS"

ENTRYPOINT ["top", "-b"]

RUN apt-get update

RUN apt-get install -y python3
RUN apt-get install -y python3-pip

COPY pyproject.toml .

RUN pip install celery

COPY src/ .

CMD [ "python", "./main.py" ]