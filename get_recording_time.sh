#!/bin/bash 
filename=recordings/$(cat recordings/current.txt)
mediainfo --Output="General;%Duration/String3%" $filename