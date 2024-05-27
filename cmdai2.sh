#!/bin/bash

# Defining initial variables
USER_CMD="$1"
MODEL="${2:-mistral-large-latest}"
COMPANY="${3:-mistralai}"

# Checking if USER_CMD is provided
if [ -z "$USER_CMD" ]; then
  echo "Usage: $0 <command> [<model>] [<company>]"
  exit 1
fi

# Get the Linux version
LINUX_VERSION=$(uname -a)

# Defining default API URL, key and changing them if necessary
API_URL="https://api.mistral.ai/v1/chat/completions"
API_KEY=$MISTRAL_API_KEY

if [ "$COMPANY" = "openai" ]; then
  API_URL="https://api.openai.com/v1/chat/completions"
  API_KEY=$OPENAI_API_KEY
fi

# Preparing the JSON data for POST request
json_data=$(jq -n \
               --arg cmd "$USER_CMD" \
               --arg mdl "$MODEL" \
               --arg LinuxVersion "$LINUX_VERSION" \
               '{
                  "model": $mdl,
                  "messages": [
                    { "role": "system", "content": ("You will return only a json list of commands + explanations for " + $LinuxVersion)},
                    {"role": "user", "content": ("a command that: " + $cmd)}
                  ]
                 }')

# Making the POST request
response=$(curl --location "$API_URL" \
               --header 'Content-Type: application/json' \
               --header 'Accept: application/json' \
               --header "Authorization: Bearer $API_KEY" \
               --data "$json_data")

# Extracting the command from the response
command=$(echo "$response" | jq -r '.choices[0].message.content')

if [ "$command" = "null" ]; then
  command="$response"
fi

# Showing a confirmation prompt to the user
dialog --title "$MODEL Command" \
       --yesno "AI: ------------\n $command \n-------------\n\nDo you want to execute it?" 10 60

response=$?

# Executing the command if the user confirmed
case $response in
  0)
    clear
    stty -echo
    xdotool type "$command"
    stty echo
    ;;
  1)
    clear
    echo "$command"
    ;;
esac
