#!/bin/bash

# -aspect 16:9

rm -rf live
mkdir live

prefix=test
suffix=$(date +%Y-%m-%d-%H:%M:%S)
filename=$prefix.$suffix.ts

ffmpeg -f v4l2 \
 -i /dev/video1 \
 -f pulse -i default \
 -vcodec libx264 -vb 4000k -acodec aac \
 -x264-params keyint=50:scenecut=0 \
 -preset superfast \
 -vf scale=1280x720 \
 -ab 256k \
 -movflags empty_moov+omit_tfhd_offset+frag_keyframe+default_base_moof \
 -async 1 -vsync 1 \
 -segment_list_flags +live -hls_allow_cache 0  -hls_time 2  -hls_wrap 50 \
 -f tee  -map 0:0 "live/video.m3u8|recordings/$filename"