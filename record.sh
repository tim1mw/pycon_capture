#!/bin/bash

# -aspect 16:9

rm -rf live
mkdir live

prefix=video
suffix=$(date +%Y-%m-%d-%H_%M_%S)
filename=$prefix-$suffix.ts

rm -f recordings/current.txt

echo $filename > recordings/current.txt

ffmpeg -f v4l2 -framerate 25 \
 -i /dev/video1 \
 -f pulse -i default \
 -vcodec libx264 -vb 5000k -acodec aac \
 -x264-params keyint=25:scenecut=0 \
 -preset ultrafast \
 -vf scale=1280x720 \
 -ab 256k \
 -bsf:v h264_mp4toannexb \
 -movflags empty_moov+omit_tfhd_offset+frag_keyframe+default_base_moof \
 -segment_list_flags +live -hls_allow_cache 0  -hls_time 1  -hls_wrap 50 \
 -f tee  -map 0:0 -map 1:0 "live/video.m3u8|recordings/$filename"