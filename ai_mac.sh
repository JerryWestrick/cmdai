#!/bin/bash
if [ -z "$1" ]; then
    read -r -p "AI Question: " question
else
    question="$1"
fi
OUTPUT=$(~/.local/bin/cmdai/aie_mac "$question" -shell=bash)

echo "AI use cmd: $OUTPUT"

# Use AppleScript to simulate typing
echo "set the clipboard to \"$OUTPUT\"" | osascript -
osascript -e 'tell application "System Events" to keystroke "v" using command down'
