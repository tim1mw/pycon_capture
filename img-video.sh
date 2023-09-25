#!/bin/bash

ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -loop 1 -i $1 -t 5 -framerate 25 -vcodec libx264 -vb 12000k -acodec aac -ab 256k $2
