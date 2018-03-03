#!/bin/sh
cd `dirname $0`
sudo hciconfig hci0 down
sleep 5
sudo hciconfig hci0 up
sleep 5
pipenv run python examples/post_to_influxdb.deploy.py
echo "exiting..."
