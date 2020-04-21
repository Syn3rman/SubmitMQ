FROM python:3

WORKDIR /worker_py

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . /worker_py

CMD ["python3", "worker_python.py"]