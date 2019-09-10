#!/bin/bash 
filename=recordings/raw/$(cat recordings/current.txt)
mediainfo --Output="General;%Duration/String3%" $filename
