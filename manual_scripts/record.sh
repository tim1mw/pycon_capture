#!/bin/bash

# -aspect 16:9

ffmpeg -f v4l2 \
 -framerate 25 -video_size 720x576 \
 -i /dev/video1 \
 -f pulse -i default \
 -vcodec h264 -vb 2000k -acodec libmp3lame \
 -vf scale=1024x576 \
 -ab 256k \
 -async 1 -vsync 1 \
 $1