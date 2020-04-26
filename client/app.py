import pika
from flask import Flask, render_template, request, redirect, url_for, jsonify
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

def get_task_info(id):
    """Find document by id

    :param id: id of the task who's details are requested

    :returns: Requested document
    """
    db = client.diss
    results = db.results
    print(id)

    res = results.find_one({"id": id})
    return res

def history(page_num, page_size):
    """Paginate results to fetch limited documents from the db.
    This needs to be done when there are a lot of documents in the db.

    :param page_num: The page number/offset from UI
    :param page_size: Number of documents to be fetched (displayed/page)

    :returns: page_size number of documents starting at page_num

    While using this with the api, you would ideally set
    page_num = 1 and page_size as the number of documents you want. 
    """
    db = client.diss
    results = db.results

    skips = page_size * (page_num - 1)
    cursor = results.find().skip(skips).limit(page_size)

    res =  [x for x in cursor]

    return res

@app.route('/')
def dashboard():
    """Path for dashboard
    """

    db = client.diss
    results = db.results
    data = {}
    data["count"] = results.count()
    return render_template('dashboard.html', data=data)

@app.route('/upload/<int:page_num>', methods=['GET'])
def tasks(page_num):
    """View all submitted tasks and upload new task 
    """

    res = history(page_num, PAGE_SIZE)
    print(res)
    return render_template('upload.html', docs=res)


@app.route('/upload/<int:page_num>', methods=['POST'])
def task_info(page_num):
    """Get details for all tasks
    """

    page_size = request.form["page_size"]
    res = history(page_num, page_size)
    print(res)
    return jsonify(res)

@app.route('/jobs/<id>', methods=['GET'])
def tasks_info(id):
    """View info for particular task
    """

    res = get_task_info(id)
    return render_template('task_info.html', data=res)

@app.route('/jobs/<id>', methods=['POST'])
def return_info(id):
    """Get info for a particular task

    Returns:

    ts: Timestamp at which task was submitted
    language: Python/C++
    content: Code
    timeout: Timeout to kill program if it does not terminate
    id: id of the file
    status: submitted/completed/failed
    submittedBy: IP address of machine that created the task
    completedAt: Time at which execution was finished
    completedBy: IP address of machine that completed the task
    err: Errors encountered
    output: Output generated
    """

    res = get_task_info(id)
    return jsonify(res), 200

@app.route('/uploader', methods=['GET', 'POST'])
def upload():
    """Upload file to server

    :param language: Python/C++
    :param timeout: Timeout to kill program if it does not terminate
    :param file: File uploaded by user
    """
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
                        body=json.dumps({key: data[key] for key in ["content", "id", "language", "timeout"]}),
                        properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))

    connection.close()
    
    return redirect(url_for("dashboard"))


if __name__ == '__main__':
    app.run(debug=True)
