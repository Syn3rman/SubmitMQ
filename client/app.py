from kafka import KafkaProducer
from flask import Flask, render_template, request, redirect, url_for
import json
import hashlib
import datetime
import socket
from pymongo import MongoClient
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                        value_serializer=lambda v: json.dumps(v).encode('utf-8'))

mongo_url = os.getenv("MONGO_URL")
client = MongoClient(mongo_url)

@app.route('/')
def upload_file():
   return render_template('index.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload():
   if request.method == 'POST':
      f = request.files['file']
      data = {}

      contents = f.read().decode("utf-8")
      data["content"] = contents
      data["id"] = hashlib.sha1(file.encode('utf-8')).hexdigest()
      data["language"] = "python3"
      
      ts = datetime.datetime.now().timestamp()
      print(data)
      
      producer.send("python", value=data)
      
      data["ts"] = ts
      data["status"] = "submitted"
      data["submittedBy"] = socket.gethostbyname(socket.gethostname())
      
      db = client.diss
      results = db.results
      results.insert_one(data)
      
      return redirect(url_for("upload_file"))
		
if __name__ == '__main__':
   app.run(debug = True)