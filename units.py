from concurrent import futures
import json
import dateutil.parser
import argparse
import os
import traceback

from google import auth
from google.cloud import pubsub_v1

def parse_command_line_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('project_id', type=str,
      help='GCP Project ID')
  parser.add_argument('subscription', type=str,
      help='Pub/Sub Subscription Name')
  return parser.parse_args()


def print_unit(point_name, unit):
  print(f'\t\t {point_name:<15} {unit}')

def print_device(units_result, points_result, registry_id, device_id):
  print(f'{units_result:<3} {points_result:<3} {registry_id:<10} {device_id:<15}')


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
  global devices_seen
  if message.attributes['deviceId'] in devices_seen:
    message.ack()
    return

  try:
    if message.attributes.get('subType') != 'state' \
      and message.attributes.get('subFolder') != 'update':
      message.ack()
      return

    device_id = message.attributes['deviceId']
    registry_id = message.attributes['deviceRegistryId']
    state = json.loads(message.data)

    try:
      points = state['pointset']['points']
    except:
      points = {}
    
    has_units = False
    for point_name, value in points.items():
      if value.get('units'):
        has_units = True

    has_points = True if len(points) > 0 else False

    units_result = 'YES' if has_units else 'NO'
    points_result = 'YES' if has_points else 'NO'

    print_device(units_result, points_result, registry_id, device_id)

    for point_name, value in points.items():
      if value.get('units'):
        print(value.get('units'))
        print(point_name)
        print_unit(point_name, value.get('units'))
    

  except Exception as e:
    traceback.print_exc()
  finally:
    message.ack()
    


devices_seen = []
args = parse_command_line_args()
index = 0

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
