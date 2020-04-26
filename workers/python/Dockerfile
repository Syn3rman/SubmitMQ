FROM python:3.8.2-slim-buster

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    net-tools \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*


WORKDIR /worker_py

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . /worker_py

CMD ["python3", "/worker_py/worker_python.py"]