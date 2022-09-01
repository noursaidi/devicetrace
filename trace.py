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


def store_payload(directory, timestamp, registry_id, message_type, payload):
  timestamp = timestamp.strftime("%H:%M:%S.%f")
  file_name = f'{timestamp}_{registry_id}_{message_type}.txt'
  file_path = os.path.join(directory, file_name)
  with open(file_path, 'x') as f:
    f.write(payload)


def print_log(timestamp, registry_id, message_type):
  print(f'{timestamp} {registry_id} {message_type}')


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
  try:
    #print(f'message receieved {message.attributes["deviceId"]}')
    if message.attributes['deviceId'] != target_device_id:
      message.ack()
      return

    if message.attributes['subType'] == "state":
      message_type = "state"
    elif message.attributes['subType'] == 'config':
      message_type = "config"
    else:
      message_type = f"event_{message.attributes['subFolder']}"
    
    registry_id = message.attributes['deviceRegistryId']
    timestamp = message.publish_time

    # try to pretty print
    try:
      message_json = json.loads(message.data)
      payload = json.dumps(message_json, indent=4)
    except Exception:
      payload = message.data.decode('utf-8')

    store_payload(trace_directory, timestamp, registry_id, message_type, payload)
    print_log(timestamp, registry_id, message_type)
  except Exception as e:
    print(e)
  finally:
    message.ack()


args = parse_command_line_args()
target_device_id = args.device_id
trace_directory = args.directory

if not os.path.isdir(trace_directory):
  print(f'{trace_directory} is not an existing. Exiting..')
  exit

subscription_id = f'projects/{args.project_id}/subscriptions/{args.subscription}'
credentials, project_id = auth.default()
sub_client = pubsub_v1.SubscriberClient(credentials=credentials)
future = sub_client.subscribe(subscription_id, callback)
print("Listening to pubsub, please wait ...")

while True:
  try:
    future.result(timeout=5)
  except futures.TimeoutError:
    continue
  except (futures.CancelledError, KeyboardInterrupt):
    future.cancel()
  except Exception as e: 
    print(f"PubSub subscription failed with error: {e}")
    future.cancel()
    break