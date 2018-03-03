'''
Get data from sensors and write it to InfluxDB

Requires:
    influxdb - pip install influxdb


** Docker InfluxDB & Grafana guide **

Download container
$ docker pull samuelebistoletti/docker-statsd-influxdb-grafana

Create and start new container
$ docker run -d --name docker-statsd-influxdb-grafana -p 3003:3003 -p 3004:8083 -p 8086:8086 -p 22022:22 -p 8125:8125/udp samuelebistoletti/docker-statsd-influxdb-grafana:latest

Or start existing container
$ docker start docker-statsd-influxdb-grafana

InfluxDB: http://localhost:3004/

First create new table: CREATE TABLE tag_data
Query to return all tag data: SELECT * FROM ruuvitag
Remove all data: DROP SERIES FROM ruuvitag

Grafana: http://localhost:3003/ (root/root)

Add datasource (type: InfluxDB url: http://localhost:8086, database: tag_data)
Add new graph to dashboard
'''

from influxdb import InfluxDBClient
from ruuvitag_sensor.ruuvi import RuuviTagSensor

import requests
HEALTHCHECK_URL = "https://hchk.io/<your_healthcheck_id>"


def convert_to_influx(mac, payload):
    json_body = []
    for field in ['temperature', 'humidity', 'pressure', 'battery']:
        if field == 'battery':
            value = payload[field]/1000.0
            field = 'batteryVoltage'
        else:
            value = payload[field]
        json_body.append({
            "measurement": field,
            "tags": {
                "mac": mac,
                "protocolVersion": 3,
            },
            "fields": {
                "value": value
            }
        })

    return json_body

client = InfluxDBClient(host="localhost", port=8086, database="ruuvi")

while True:
    datas = RuuviTagSensor.get_data_for_sensors()
    json_body = []
    for mac, payload in datas.items():
        print("got",payload)
        json_body.extend(convert_to_influx(mac, payload))
    print("would write",json_body)
    client.write_points(json_body)
    try:
        requests.get(HEALTHCHECK_URL)
    except:
        pass

