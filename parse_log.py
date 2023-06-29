import time
import pymongo
from datetime import datetime

from _secrets import connection_string

log_file = 'output.txt'

connection = pymongo.MongoClient(connection_string)
database = connection['iot']
try:
  ts_collection = database.create_collection("macbook_ts", timeseries={
    "timeField": "timestamp",
  })
except pymongo.errors.CollectionInvalid:
  ts_collection = database["macbook_ts"]
  print("Collection already exists")

doc_collection = database['macbook_doc']
bucket_collection = database['macbook_bucket']

while True:

  new_lines = []
  while len(new_lines) < 400:
    with open(log_file, 'r') as file:
        new_lines = file.readlines()

  timestamp_line = next((i for i, line in enumerate(new_lines) if "*** Sampled system activity" in line), None)
  if timestamp_line is not None:
    
    dict = {}
    
    print(new_lines[timestamp_line].rstrip())
    line = new_lines[timestamp_line]
    split = line.split(' ')
    date_string = ' '.join(split[5:10])
    timestamp = datetime.strptime(date_string, "%b %d %H:%M:%S %Y %z)")
    dict['timestamp'] = timestamp
   
    fanspeed_line = next((i for i, line in enumerate(new_lines) if "Fan:" in line), None)
    if fanspeed_line is not None:
       
       for i in range(0, 3):
        line = new_lines[fanspeed_line+i]
        split = line.split(' ')
        if i == 0:
          key = 'fan'
          value = float(split[1])
        elif i == 1:
          key = 'cpu_temp'
          value = float(split[3])
        else:
          key = 'gpu_temp'
          value = float(split[3])
        
        dict[key] = value

    ts_collection.insert_one(dict)
    doc_collection.insert_one(dict)

    minute = datetime(
      year=timestamp.year,
      month=timestamp.month,
      day=timestamp.day,
      hour=timestamp.hour,
      minute=timestamp.minute
    )
    bucket_collection.update_one(
      {"timestamp": minute}, 
      {
        "$set": {
          "timestamp": minute
        },
        "$push": {
          "readings": dict
        }
      },
      upsert=True
    )

  time.sleep(6)
