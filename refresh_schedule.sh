#!/bin/bash

rm -f recordings/schedule.json
wget -O recordings/schedule.json https://2018.hq.pyconuk.org/schedule/json/ 
