import pika
import json
import os
import datetime
import socket   
from subprocess import Popen, PIPE
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.getenv("MONGO_URL")
client = MongoClient(mongo_url)


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=os.getenv("RABBITMQ_SERVER")))
channel = connection.channel()

channel.exchange_declare(exchange='events', exchange_type='direct')

channel.queue_declare(queue='python_events')
channel.queue_bind(exchange='events', queue="python_events", routing_key="python")

def callback(ch, method, properties, message):
    message = json.loads(message.decode('utf-8'))
    
    id = message["id"]
    timeout = [ str(message["timeout"]) ]

    with open("temp.py", "w+") as f:
        f.write(message["content"])
    
    command = ["timeout"] + timeout + ["python3", "temp.py"]

    res = Popen(command, stdout=PIPE, stderr=PIPE)
    out,err = res.communicate()
    retcode = res.returncode

    status = "completed" if retcode == 0 else "failed"
    ts = datetime.datetime.now().timestamp()
    
    db = client.diss
    results = db.results
    
    results.find_one_and_update({"id":id}, {"$set": {"status": status,
                                                    "returnCode": retcode,
                                                     "output": out.decode('utf-8'),
                                                     "err": err.decode('utf-8'), 
                                                     "completedAt": ts,
                                                     "completedBy": socket.gethostbyname(socket.gethostname())}
                                                     })


channel.basic_consume(
    queue="python_events", on_message_callback=callback, auto_ack=True)

channel.start_consuming()
