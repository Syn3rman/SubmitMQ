import pika
from flask import Flask, render_template, request, redirect, url_for
import json
import hashlib
import datetime
import os
from pymongo import MongoClient
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

mongo_url = os.getenv("MONGO_URL")
client = MongoClient(mongo_url)

# Run a job for 10 minutes if timeout not provided
DEFAULT_TIME_TO_RUN = 600
PAGE_SIZE = 10


@app.route('/')
def upload_file():
    db = client.diss
    results = db.results
    data = {}
    data["count"] = results.count()
    return render_template('dashboard.html', data=data)

@app.route('/upload/<int:page_num>')
def submit(page_num):
    db = client.diss
    results = db.results

    skips = PAGE_SIZE * (page_num - 1)
    cursor = results.find().skip(skips).limit(PAGE_SIZE)

    res =  [x for x in cursor]
    print(res)
    return render_template('upload.html', docs=res)

@app.route('/jobs/<id>')
def job_info(id):
    db = client.diss
    results = db.results
    print(id)

    res = results.find_one({"id": id})
    print(res)

    return render_template('task_info.html', data=res)

@app.route('/uploader', methods=['POST'])
def upload():
    if request.method == 'POST':
        data = {}

    ts = datetime.datetime.now().timestamp()
    data["ts"] = ts

    language = request.form["language"]
    data["language"] = language
    f = request.files["file"]
    contents = f.read().decode("utf-8")
    data["content"] = contents
    timeout = request.form["timeout"] if request.form.get("timeout", None) else DEFAULT_TIME_TO_RUN
    data["timeout"] = timeout

    data["id"] = hashlib.sha1(contents.encode('utf-8')).hexdigest()
    data["status"] = "submitted"
    data["submittedBy"] = request.remote_addr

    db = client.diss
    results = db.results
    results.insert_one(data)


    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=os.getenv("RABBITMQ_SERVER")))
    channel = connection.channel()

    channel.exchange_declare(exchange='events', exchange_type='direct')

    channel.basic_publish(
                        exchange='events', routing_key=language, 
                        body=json.dumps({key: data[key] for key in ["content", "id", "language", "timeout"]}))

    connection.close()
    
    return redirect(url_for("upload_file"))


if __name__ == '__main__':
    app.run(debug=True)
