#!/usr/bin/env python3
import json
import os
import platform
import argparse
import ssl
from urllib import request, error

import certifi
from dotenv import load_dotenv


def ask_ai(question, shell):
    # print(f"environment['LLM_MODEL'] = {os.environ.get('LLM_MODEL').lower()[:7]}... ")
    # Get the home directory
    home_dir = os.path.expanduser("~")

    # Build the absolute path of the .env file
    env_file_path = os.path.join(home_dir, ".env")

    # Load the .env file
    load_dotenv(dotenv_path=env_file_path)

    model = os.environ.get('LLM_MODEL')
    if model is None:
        print(f"LLM_MODEL is not defined as environment variable")
        exit(1)

    if model.lower()[:7] == 'mistral':
        # print(f"mistral...")
        return ask_mistral(question, shell)
    else:
        # print("openai...")
        return ask_openai(question, shell)


def ask_mistral(question, shell):
    url = 'https://api.mistral.ai/v1/chat/completions'

    # Prepare the headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {os.environ.get("MISTRAL_API_KEY")}',
    }

    # Prepare the payload
    data = {
        "model": os.environ.get('LLM_MODEL'),
        "messages": [
            {"role": "system",
             "content": f"You will generate a command for {shell} system."},
            {"role": "system",
             "content": "DO NOT ADD EXPLANATIONS. DO NO ADD COMMENTS. DO NOT ADD NOTES. DO NOT GIVE OPTIONS."},
            {"role": "user", "content": f"{question}"}
        ]
    }

    # print(f"headers: {headers}")

    # Convert python dictionary to JSON, then encode it to byte
    payload = json.dumps(data).encode('utf-8')

    # Prepare the request
    context = ssl.create_default_context(cafile=certifi.where())
    req = request.Request(url, data=payload, headers=headers)


    # Send the request
    try:
        resp = request.urlopen(req, context=context)
    except error.HTTPError as e:
        print('HTTPError: {}'.format(e.reason))
    except error.URLError as e:
        print('URLError: {}'.format(e.reason))

    else:
        # Read and decode the response
        response = json.loads(resp.read().decode('utf-8'))
        return response['choices'][0]['message']['content']


def ask_openai(question):
    import urllib.request
    import json

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
    }
    data = {
        "model": os.environ.get('LLM_MODEL'),
        "messages": [
            {"role": "system",
             "content": f"You will generate a command for {shell} system."},
            {"role": "system",
             "content": f"Generate {platform.system()} executable commands, the commands only, no quotes no files. No User interaction. DO NOT EXPLAIN. Respond with one and only one command give only the command as to be executed"},
            {"role": "user", "content": f"{question}"}
        ]
    }

    payload = json.dumps(data).encode('utf-8')

    # Prepare the request
    context = ssl.create_default_context(cafile=certifi.where())
    req = request.Request(url, data=payload, headers=headers)


    # Send the request
    try:
        resp = request.urlopen(req, context=context)
    except error.HTTPError as e:
        print('HTTPError: {}'.format(e.reason))
    except error.URLError as e:
        print('URLError: {}'.format(e.reason))
    else:
        # Read and decode the response
        response = json.loads(resp.read().decode('utf-8'))
        return response['choices'][0]['message']['content']


if __name__ == "__main__":

    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('-shell', action='store', type=str, choices=['cmd', 'bash', 'powershell'])
    my_parser.add_argument('AI_question', nargs='?', default='AI Question: ')

    args = my_parser.parse_args()

    if args.shell:
        shell = f"{platform.system()}:{platform.version()} - {args.shell}"
    else:
        shell = ''

    if args.AI_question:
        question = args.AI_question
    else:
        question = input("AI Question: ")

    # print(f"using system: {shell}")
    answer = ask_ai(question, shell)
    if answer:
        if answer[0] in ['"', "'", '`']:
            answer = answer[1:-1]
    print(answer)
