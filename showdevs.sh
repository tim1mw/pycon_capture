#!/bin/bash

v4l2-ctl --list-devices

ffmpeg -f v4l2 -list_formats all -i /dev/video2

arecord -l
