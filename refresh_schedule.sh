#!/bin/bash

mkdir -p recordings
rm -f data/schedule.json
wget -O data/schedule.json https://pretalx.com/pyconuk-2019/schedule/export/schedule.json
if [ $? -ne 0 ]; then
    echo "FAILED TO UPDATE SCHEDULE"
fi
