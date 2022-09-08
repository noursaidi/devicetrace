# [START pubsub_v1_generated_Subscriber_StreamingPull_sync]

from concurrent import futures
import json
import dateutil.parser
import argparse
import os

from google import auth
from google.cloud import pubsub_v1


def parse_command_line_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('project_id', type=str,
      help='GCP Project ID')
  parser.add_argument('subscription', type=str,
      help='Pub/Sub Subscription Name')
  parser.add_argument('device_id', type=str,
      help='Device ID')
  parser.add_argument('directory', type=str,
      help='Directory to store trace')
  return parser.parse_args()


def store_payload(directory, timestamp, index, device_id, registry_id, message_type, payload):
  timestamp = timestamp.strftime('%H:%M:%S')
  file_name = f'{index}_{timestamp}_{device_id}_{registry_id}_{message_type}.txt'
  file_path = os.path.join(directory, file_name)
  with open(file_path, 'x') as f:
    f.write(payload)


def print_log(timestamp, device_id, registry_id, message_type):
  print(f'{timestamp}  {device_id:<10} {registry_id:<15} {message_type}')


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
  global index
  try:
    if message.attributes['deviceId'] not in target_device_ids:
      message.ack()
      return

    if message.attributes['subType'] == 'state':
      if message.attributes['subFolder'] != 'update':
        message.ack()
        return
      message_type = 'state'
    elif message.attributes['subType'] == 'config':
      message_type = 'config'
    else:
      message_type = f'event_{message.attributes["subFolder"]}'
    device_id = message.attributes['deviceId']
    registry_id = message.attributes['deviceRegistryId']
    timestamp = message.publish_time
    index = index + 1

    # try to pretty print
    try:
      message_json = json.loads(message.data)
      payload = json.dumps(message_json, indent=4)
    except Exception:
      payload = message.data.decode('utf-8')

    store_payload(trace_directory, timestamp, index, device_id, registry_id, message_type, payload)
    print_log(timestamp, device_id, registry_id, message_type)
  except Exception as e:
    print(e)
  finally:
    message.ack()


args = parse_command_line_args()
target_device_ids = args.device_id.split(',')
trace_directory = args.directory
index = 0

if not os.path.isdir(trace_directory):
  print(f'{trace_directory} is not an existing. Exiting..')
  exit

subscription_id = f'projects/{args.project_id}/subscriptions/{args.subscription}'
credentials, project_id = auth.default()
sub_client = pubsub_v1.SubscriberClient(credentials=credentials)
future = sub_client.subscribe(subscription_id, callback)
print('Listening to pubsub, please wait ...')

while True:
  try:
    future.result(timeout=5)
  except futures.TimeoutError:
    continue
  except (futures.CancelledError, KeyboardInterrupt):
    future.cancel()
  except Exception as e: 
    print(f'PubSub subscription failed with error: {e}')
    future.cancel()
    break