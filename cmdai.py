import argparse
import requests
import json
import keyring
import sys


def get_api_key(api_key_name='openai_api'):
    try:
        return keyring.get_password('cmdai', username=api_key_name)
    except keyring.errors.PasswordDeleteError:
        return None


def store_api_key(api_key_name="", api_key_value=""):
    keyring.set_password("cmdai", username=api_key_name, password=api_key_value)


def load_config(file_path='cmdai.json', company=None, model=None):

    if company is None or model is None:
        raise ValueError("Both company and model names must be provided")

    with open(file_path, 'r') as f:
        data = json.load(f)

    if company not in data:
        raise ValueError(f"Invalid company name: {company}")

    api_key = data[company]['key']
    url = data[company][model]['url']
    messages = data[company][model]['messages']

    return url, company, model, messages, api_key


def send_request(url, company, model, messages, user_input=None):
    if user_input:
        messages.append({"role": "user", "content": user_input})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "model": model,
        "messages": messages,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Print the response
    response_obj = json.loads(response.text)
    print(response_obj['choices'][0]['message']['content'])


def list_companies_and_models(file_path='cmdai.json'):
    with open(file_path, 'r') as f:
        data = json.load(f)
    for company, models in data.items():
        print(f'Company: {company}')
        for model in models:
            if model != 'key':
                print(f'\tModel: {model}')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--company', help='Name of the company')
    parser.add_argument('-m', '--model', help='Name of the model')
    parser.add_argument('-q', '--question', help='The user question')
    parser.add_argument('--list', action='store_true', help='List all companies and models')
    args = parser.parse_args()

    if args.list:
        list_companies_and_models()
        sys.exit(0)

    if not args.question:
        print("A question is required for this operation.")
        sys.exit(1)

    url, company, model, messages, api_key = load_config(company=args.company, model=args.model)

    API_KEY = get_api_key(api_key_name=api_key)
    if API_KEY is None:
        API_KEY = input(f"Please enter your {company} API key: ")
        store_api_key(api_key_name=api_key, api_key_value=API_KEY)

    if not API_KEY:
        print("API key cannot be empty.")
        sys.exit(1)

    user_input = args.question
    send_request(url, company, model, messages, user_input)
