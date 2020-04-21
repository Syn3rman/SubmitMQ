from kafka import KafkaConsumer, KafkaProducer
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

consumer = KafkaConsumer("cpp",
                        bootstrap_servers=['localhost:9092'],
                        auto_offset_reset='earliest',
                        enable_auto_commit=True,
                        group_id='cpp',
                        value_deserializer=lambda x: json.loads(x.decode('utf-8')))


for messages in consumer:
    message = messages.value
    
    id = message["id"]
    timeout = [ str(message["timeout"]) ]

    with open("temp.cpp", "w+") as f:
        f.write(message["content"])
    
    command = ["timeout"] + timeout + ["g++", "temp.cpp"]

    res = Popen(command, stdout=PIPE, stderr=PIPE)
    out,err = res.communicate()
    gpp_retcode = res.returncode

    if gpp_retcode != 0:
        # job failed if compilation gives error
        status = "failed"
    else:
        res = Popen("./a.out", stdout=PIPE, stderr=PIPE)
        out,err = res.communicate()
        retcode = res.returncode
        
        if retcode == 0:
            status = "completed"
        else:
            # job fails if any runtime issues
            status = "failed"

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
