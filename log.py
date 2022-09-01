from importlib.metadata import entry_points
import datetime
import time
import subprocess
import json
import dateutil.parser
import argparse

# project, device_id, timestamp
#SHELL_TEMPLATE_SINGLE = 'gcloud logging read "logName=projects/{}/logs/cloudiot.googleapis.com%2Fdevice_activity AND labels.device_id={} AND timestamp>=\\\"{}\\\"" --limit 1000 --format json'
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

# [file_from_json_ref(ref) for ref in refs]
device_filter = ' OR '.join([f'labels.device_id={target}' for target in target_devices])

timestamp = datetime.datetime.utcnow()
dt = 20 # balance of speed and accuracy  
next_timestamp = timestamp - datetime.timedelta(seconds=dt)


while True:
    if datetime.datetime.utcnow() > next_timestamp:
        shell_command = SHELL_TEMPLATE.format(project_id, device_filter, timestamp.strftime(TIMESTAMP_FORMAT) )
        output = subprocess.run(shell_command, capture_output=True, shell=True)

        data = json.loads(output.stdout)

        entries = []

        for entry in data:
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
            
            if event_type == 'PUBACK':
                metadata = entry['jsonPayload']['publishToDeviceTopicType']

            if event_type == 'SUBSCRIBE':
                metadata =  entry['jsonPayload']['mqttTopic']
            
            entries.append({'timestamp_obj': dateutil.parser.parse(timestamp), 
                            'timestamp': timestamp, 
                            'registry_id':registry_id, 
                            'event_type':event_type, 
                            'metadata':metadata,
                            'device_id': log_device_id })
            
        entries.sort(key=lambda item: item['timestamp_obj'])
        
        for entry in entries:
            print(f"{entry['timestamp_obj']}  {entry['device_id']:<10} {entry['registry_id']:<15} {entry['event_type']} {entry['metadata']}")
        
        timestamp = datetime.datetime.utcnow()
        next_timestamp = timestamp + datetime.timedelta(seconds=dt)
     
    time.sleep(0.1)