from mac_notifications import client
from time import sleep
from datetime import datetime, timedelta
import pymongo

from _secrets import connection_string

connection = pymongo.MongoClient(connection_string)
collection = connection['iot']['macbook_ts']


def notify(temp):
  client.create_notification(
    title="Macbook IoT",
    subtitle="Thermal Throttling Imminent",
    text=f"CPU Temperature: {temp}°C",
    icon="/Users/peter.fitch/macbook_temperatures/thermometer.png",
  )


def get_average_temp(window):
  from_time = datetime.now() - timedelta(seconds=window) - timedelta(hours=1)
  res = list(collection.aggregate([{
    '$match': {
      'timestamp': { '$gte': from_time }
    },
  }, {
    '$group': {
      '_id': None,
      'avg_temp': {'$avg': '$cpu_temp'}
    }
  }]))
  if len(res) > 0:
    return round(res[0]['avg_temp'], 2)
  else:
    return 0

window = 300
threshold = 95

# Loop forever
if __name__ == '__main__':
  while True:
    temp = get_average_temp(window)
    print(f"{datetime.now()} - CPU temperature: {temp}°C")

    if get_average_temp(window) > threshold:
      print(f"{datetime.now()} - Temperature high, checking again in 1 minute")
      sleep(60)
      temp = get_average_temp(window)

      if temp > threshold:
        print(f"{datetime.now()} - Temperature still high, sending notification")
        notify(temp)
        sleep(window)
      else:
        print(f"{datetime.now()} - Temperature has dropped, skipping notification")
        sleep(window)

    else:
      sleep(window)
    