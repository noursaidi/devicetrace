import datetime
import time
import subprocess
import json
import dateutil.parser
import argparse

SHELL_TEMPLATE = 'gcloud logging read "logName=projects/{}/logs/cloudiot.googleapis.com%2Fdevice_activity AND ({}) AND timestamp>=\\\"{}\\\"" --limit 1000 --format json'
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ" #timestamp >= "2016-11-29T23:00:00Z"

def parse_command_line_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('project_id', type=str,
    help='GCP Project ID')
  parser.add_argument('device_id', type=str,
    help='Device ID')
  return parser.parse_args()

args = parse_command_line_args()
target_devices = args.device_id.split(',')
project_id = args.project_id

device_filter = ' OR '.join([f'labels.device_id={target}' for target in target_devices])

dt = 10 # balance of speed and accuracy for ordering as some entries can be delayed by 10 seconds (or more!)
search_timestamp = datetime.datetime.utcnow() - datetime.timedelta(seconds=5)
next_timestamp = datetime.timedelta(seconds=dt)

seen = []

while True:
  try:
    shell_command = SHELL_TEMPLATE.format(project_id, device_filter, search_timestamp.strftime(TIMESTAMP_FORMAT) )
    output = subprocess.run(shell_command, capture_output=True, shell=True, check=True)

    data = json.loads(output.stdout)

    entries = []

    for entry in data:
      insert_id = entry['insertId']

      if insert_id in seen:
        continue

      seen.append(insert_id)

      event_type = entry['jsonPayload']['eventType']
      timestamp = entry['timestamp']
      registry_id = entry['resource']['labels']['device_registry_id']
      log_device_id = entry['labels']['device_id']
      metadata = ''

      if event_type == 'PUBLISH':
        metadata = entry['jsonPayload'].get('publishFromDeviceTopicType')
        publishToDeviceTopicType = entry['jsonPayload'].get('publishToDeviceTopicType')
        if publishToDeviceTopicType == 'CONFIG':
          event_type = 'CONFIG'
          metadata = ''
        elif not metadata and publishToDeviceTopicType:
          metadata = f'TO DEVICE {publishToDeviceTopicType}'

      if event_type == 'PUBACK':
        metadata = entry['jsonPayload']['publishToDeviceTopicType']

      if event_type == 'SUBSCRIBE':
        metadata =  entry['jsonPayload']['mqttTopic']

      if event_type == 'ATTACH_TO_GATEWAY':
        metadata = entry['jsonPayload']['gateway']['id']

      if event_type == 'DISCONNECT':
        metadata = entry['jsonPayload']['disconnectType']

      if entry['jsonPayload']['status'].get('code') != 0:
        metadata = f"{metadata} ({entry['jsonPayload']['status'].get('description')} {entry['jsonPayload']['status'].get('message', '')})"

      entries.append({'timestamp_obj': dateutil.parser.parse(timestamp),
              'timestamp': timestamp,
              'registry_id':registry_id,
              'event_type':event_type,
              'metadata':metadata,
              'device_id': log_device_id })

    entries.sort(key=lambda item: item['timestamp_obj'])

    for entry in entries:
      print(f"{entry['timestamp_obj']}  {entry['device_id']:<10} {entry['registry_id']:<15} {entry['event_type']} {entry['metadata']}")

    td = datetime.datetime.utcnow() - search_timestamp
    if td.total_seconds() > 180:
      # Use a 3 minute search window
      search_timestamp = search_timestamp + datetime.timedelta(seconds=(300 - td.total_seconds()))
  except Exception:
    pass
  finally:
    time.sleep(dt)
