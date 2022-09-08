# devicetrace

## Requirements
- Python modules in `requirements.txt` installed
- `gcloud` CLI installed and authenticated for both CLI and application default credentials (`gcloud auth login` and `gloud auth application-default login`) with IAM permissions for required **Pub/Sub Subscription**, **IoT Registry**, and **Cloud Logging**
- Cloud logging enabled 

## Usage

### Config Updates
Update device config (and publish to topic so it's in the traces)
`python3 config.py PROJECT_ID AHU-1 ZZ-TRI-FECTA  us-central1 udmi_target config1.json`

### Message Traces
View PUB/SUB Message log and store messages for given device ID's (will match ANY device with the device ID)
`python3 trace.py PROJECT_ID gama2 AHU-1 `
`python3 trace.py PROJECT_ID gama2 GAT-100,ACT-1 .`

```
2022-09-01 14:03:29.407000+00:00  GAT-100    ZZ-TRI-FECTA    event_pointset
2022-09-01 14:03:34.529000+00:00  GAT-100    ZZ-TRI-FECTA    event_system
2022-09-01 14:03:39.788000+00:00  GAT-100    ZZ-TRI-FECTA    state
2022-09-01 14:03:44.798000+00:00  ACT-1      ZZ-TRI-FECTA    event_pointset
2022-09-01 14:03:49.811000+00:00  ACT-1      ZZ-TRI-FECTA    event_system
2022-09-01 14:03:54.936000+00:00  ACT-1      ZZ-TRI-FECTA    state
2022-09-01 14:04:00.220000+00:00  GAT-100    ZZ-TRI-FECTA    event_pointset
2022-09-01 14:04:05.312000+00:00  GAT-100    ZZ-TRI-FECTA    event_system
```

### GCP Device Logs (Cloud Logging)
View GCP Logs for given device ID's (refreshes every 10 seconds to try and keep items in order, but not always possible. Will match any device with the given device ID)
`python3 log.py daq1-273309 GAT-100,ACT-1`

```
2022-09-01 14:34:57.540163+00:00  GAT-100    ZZ-TRI-FECTA    PUBLISH EVENTS
2022-09-01 14:35:02.654997+00:00  GAT-100    ZZ-TRI-FECTA    PUBLISH EVENTS
2022-09-01 14:35:07.496057+00:00  GAT-100    ZZ-TRI-FECTA    PUBACK CONFIG
2022-09-01 14:35:07.496122+00:00  GAT-100    ZZ-TRI-FECTA    CONFIG 
2022-09-01 14:35:07.626950+00:00  GAT-100    ZZ-TRI-FECTA    PUBLISH STATE
2022-09-01 14:35:07.677668+00:00  GAT-100    ZZ-TRI-FECTA    PUBLISH STATE (RESOURCE_EXHAUSTED The device "2582332477650079" could not be updated. Device state can be updated only once every 1s.)
2022-09-01 14:35:07.679536+00:00  GAT-100    ZZ-TRI-FECTA    DISCONNECT  (RESOURCE_EXHAUSTED The device "2582332477650079" could not be updated. Device state can be updated only once every 1s.)
2022-09-01 14:35:19.115078+00:00  GAT-100    ZZ-TRI-FECTA    CONNECT 
2022-09-01 14:35:23.637210+00:00  GAT-100    ZZ-TRI-FECTA    SUBSCRIBE /devices/GAT-100/config
2022-09-01 14:35:23.653924+00:00  GAT-100    ZZ-TRI-FECTA    SUBSCRIBE /devices/GAT-100/commands/#
2022-09-01 14:35:23.654129+00:00  GAT-100    ZZ-TRI-FECTA    SUBSCRIBE /devices/GAT-100/errors
2022-09-01 14:35:24.491455+00:00  GAT-100    ZZ-TRI-FECTA    PUBACK CONFIG
2022-09-01 14:35:24.491506+00:00  GAT-100    ZZ-TRI-FECTA    CONFIG 
2022-09-01 14:35:24.632056+00:00  GAT-100    ZZ-TRI-FECTA    PUBLISH STATE
2022-09-01 14:35:25.094994+00:00  ACT-1      ZZ-TRI-FECTA    ATTACH_TO_GATEWAY GAT-100
```