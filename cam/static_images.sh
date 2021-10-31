#!/usr/bin/env bash

TIME=$(date +"%Y-%m-%d_%H%M")
# 0= sunday, 6 = saturday
WEEKDAY=$(date +%w)


raspistill -vf -hf -o cam/$WEEKDAY/$TIME.jpg