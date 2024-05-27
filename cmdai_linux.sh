#!/bin/bash
if [ -z "$1" ]; then
    read -r -p "AI Question: " question
else
    question="$1"
fi
OUTPUT=$(python cmdai.py "$question" -shell=bash)
echo -n "AI use cmd: "
xdotool type "$OUTPUT"
echo "\n"
