FROM python:3.8.2-slim-buster

RUN apt-get update && apt-get install build-essential -y

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    net-tools \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*


WORKDIR /worker_cpp

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . /worker_cpp

CMD ["python3", "/worker_cpp/worker_cpp.py"]