from kafka import KafkaProducer
from flask import Flask, render_template, request, redirect, url_for
import json
import hashlib
import datetime
import socket
import os
from pymongo import MongoClient
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                        value_serializer=lambda v: json.dumps(v).encode('utf-8')
                        )

mongo_url = os.getenv("MONGO_URL")
client = MongoClient(mongo_url)

# Run a job for 10 minutes if timeout not provided
DEFAULT_TIME_TO_RUN = 600


@app.route('/')
def upload_file():
   return render_template('index.html')


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
    data["submittedBy"] = socket.gethostbyname(socket.gethostname())

    db = client.diss
    results = db.results
    results.insert_one(data)

    producer.send(language, value={key: data[key] for key in ["content", "id", "language", "timeout"]})

    return redirect(url_for("upload_file"))


if __name__ == '__main__':
    app.run(debug=True)
