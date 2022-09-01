# devicetrace

Update device config (and publish to topic so it's in the traces)
`python3 config.py PROJECT_ID AHU-1 ZZ-TRI-FECTA  us-central1 udmi_target config1.json`

View PUB/SUB Message log and store messages for given device ID's (will match ANY device with the device ID)
`python3 trace.py PROJECT_ID gama2 AHU-1 `
`python3 trace.py PROJECT_ID gama2 GAT-100,ACT-1 .`

View GCP Logs for given device ID's (refreshes every 10 seconds to try and keep items in order, but not always possible. Will match any device with the given device ID)
`python3 log.py daq1-273309 GAT-100,ACT-1`