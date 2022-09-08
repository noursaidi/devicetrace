import json
import argparse
import datetime
from google.cloud import iot_v1
from google.cloud import pubsub_v1

def parse_command_line_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('project_id', type=str,
      help='GCP Project ID')
  parser.add_argument('device_id', type=str,
      help='Device ID')
  parser.add_argument('registry_id', type=str,
      help='registry_id')
  parser.add_argument('region', type=str,
      help='region')
  parser.add_argument('topic', type=str,
      help='pubsub topic to republish config')
  parser.add_argument('config_file', type=str,
      help='pubsub topic to republish config')
  return parser.parse_args()

args = parse_command_line_args()
device_id = args.device_id
registry_id = args.registry_id
cloud_region = args.region
project_id = args.project_id
topic_id = args.topic

# Read config
with open(args.config_file) as f:
  config_json = json.load(f)

# Update the timestamp so it's current
timestamp = datetime.datetime.utcnow().isoformat()
config_json['timestamp'] = timestamp

config = json.dumps(config_json)

# update
client = iot_v1.DeviceManagerClient()

device_path = client.device_path(project_id, cloud_region, registry_id, device_id)
data = config.encode('utf-8')

# Exception in error
client.modify_cloud_to_device_config(
    request={'name': device_path, 'binary_data': data, 'version_to_update': 0}
)

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# When you publish a message, the client returns a future.
future = publisher.publish( topic_path,
                            data,
                            deviceId = device_id,
                            deviceRegistryId = registry_id,
                            subType = 'config',
                            subFolder = 'update')
print(future.result())
