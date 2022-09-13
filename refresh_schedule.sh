#!/bin/bash

mkdir -p recordings
rm -f data/schedule.json
wget -O data/schedule.json https://pretalx.com/pycon-uk-2022/schedule/export/schedule.json
if [ $? -ne 0 ]; then
    echo "FAILED TO UPDATE SCHEDULE"
fi
