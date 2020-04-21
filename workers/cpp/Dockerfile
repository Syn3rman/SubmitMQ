FROM python:3

WORKDIR /worker_cpp

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . /worker_cpp

CMD ["python3", "worker_python.py"]