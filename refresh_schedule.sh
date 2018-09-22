#!/bin/bash

mkdir -p recordings
rm -f recordings/schedule.json
wget -O recordings/schedule.json https://2018.hq.pyconuk.org/schedule/json/
if [ $? -ne 0 ]; then
    echo "FAILED TO UPDATE SCHEDULE"
fi
