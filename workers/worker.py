from io import StringIO
from kafka import KafkaConsumer, KafkaProducer
import json
import os
import datetime
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.getenv("MONGO_URL")
client = MongoClient(mongo_url)

consumer = KafkaConsumer("python",
                        bootstrap_servers=['localhost:9092'],
                        auto_offset_reset='earliest',
                        enable_auto_commit=True,
                        group_id='python',
                        value_deserializer=lambda x: json.loads(x.decode('utf-8')))


for messages in consumer:
    message = messages.value
    id = message.id

    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()

    try:
        # ** DO NOT USE EXEC IF YOU DO NOT TRUST THE INPUT **
        # If you must do it, consider reading blog at: http://lybniz2.sourceforge.net/safeeval.html
        exec(message["content"])
    
    except:
        raise 
    
    finally: 
        sys.stdout = old_stdout

    output = redirected_output.getvalue()
    ts = datetime.datetime.now().timestamp()
    