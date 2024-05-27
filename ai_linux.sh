#!/bin/bash
if [ -z "$1" ]; then
    read -r -p "AI Question: " question
else
    question="$1"
fi
OUTPUT=$(~/.local/bin/cmdai/aie_linux "$question" -shell=bash)
echo -n "AI use cmd: "
xdotool type "$OUTPUT"
echo "\n"
