import json
import sys

import requests
from rich.console import Console
from rich.table import Table

from jinja2 import Template
import threading
import time

console = Console()
stop_event = threading.Event()  # Event to signal when to stop the thread

def print_dot():
    while not stop_event.is_set():
        console.print('.', end='')
        time.sleep(0.5)

llm_config = {
    "OpenAI": {
        "company": "OpenAI",
        "url": "https://api.openai.com/v1/chat/completions",
        "api_key": "OPENAI_API_KEY",
        "response_text_is_json": True,
        "tplHeader": '''{"Content-Type": "application/json", "Authorization": "Bearer {{ API_KEY }}"}''',
        "tplData": '''{ "model": "{{ model }}","messages":
        [   {% if model == "o1-preview" or model == "o1-mini" %}
                {"role": "user",
                 "content": "Return a command for {{ os_system }} that can be executed by the user. JUST COMMAND. NO COMMENTS, NO EXPLANATIONS, NO QUOTES. For example 'Change directory to my home dir'"},
            {% else %}
                {"role": "system",
                 "content": "Help the user working on {{ os_system }} create a command. JUST COMMAND. NO COMMENTS, NO EXPLANATIONS."},
                {"role": "user", "content": "Change directory to my home dir"},
            {% endif %}
            {"role": "assistant", "content": "cd"},
            {"role": "user", "content": "{{ user_input }}"}
        ]}''',
        "models": ["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini", "gpt-4-turbo"],
        'response_keys': ['choices', 0, 'message', 'content']
    },
    "XAI": {
        "company": "XAI",
        "url": "https://api.x.ai/v1/chat/completions",
        "api_key": "X_AI_API_KEY",
        "response_text_is_json": False,
        "tplHeader": '''{"Content-Type": "application/json","Authorization": "Bearer {{ API_KEY }}"}''',
        "tplData": '''{ "model": "{{ model }}",
                "messages":[
                    {"role": "system",
                     "content": "Help the user working on {{ os_system }} create a command. JUST COMMAND. NO COMMENTS, NO EXPLANATIONS."},
                    {"role": "user", "content": "Change directory to my home dir"},
                    {"role": "assistant", "content": "cd"},
                    {"role": "user", "content": "{{ user_input }}"}
                ]}''',
        "models": ["grok-beta"],
        'response_keys': ['choices', 0, 'message', 'content']
    },
    "Mistralai": {
        "company": "Mistralai",
        "url": "https://api.mistral.ai/v1/chat/completions",
        "api_key": "MISTRAL_API_KEY",
        "response_text_is_json": True,
        "tplHeader": '''{"Content-Type": "application/json", "Accept": "application/json", "Authorization": "Bearer {{ API_KEY }}"}''',
        "tplData": '''{ "model": "{{ model }}",
            "messages":
              [ {"role": "system","content": "You are helping a user on {{ os_system }} execute commands. Return the command only. NO QUOTES, NO COMMENTS, NO EXPLANATIONS"},
                {"role": "user","content": "{{ user_input }}"}
              ]}''',
        "models": ["mistral-large-latest", "mistral-small-latest", "mistral-large-2407",
                   "mistral-small-2409", "codestral-2405", "mistral-embed", "ministral-3b-latest", "ministral-8b-latest",
                   "pixtral-12b", "mistral-nemo", "open-mistral-7b", "open-mixtral-8x7b", "open-mixtral-8x22b"
                   ],
        'response_keys': ['choices', 0, 'message', 'content']
    },
    "Anthropic": {
        "company": "Anthropic",
        "url": "https://api.anthropic.com/v1/messages",
        "api_key": "ANTHROPIC_API_KEY",
        "response_text_is_json": True,
        "tplHeader": '''{"x-api-key": "{{ API_KEY }}", "Content-Type": "application/json","anthropic-version": "2023-06-01"}''',
        "tplData": '''{ "model": "{{ model }}",
             "system": "You are an operator working on {{ os_system }}. List a single command that the user can execute.",
             "max_tokens": 1024,
             "messages":
              [ {"role": "user","content": "Change directory to my home dir"},
                {"role": "assistant","content": "cd"},
                {"role": "user","content": "{{ user_input }}"}
              ]}''',
        "models": ["claude-3-5-sonnet-latest", "claude-3-opus-latest", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        'response_keys': ['content', 0, 'text']
    }
}

def get_llm(model: str) -> dict[str,any] | None:
    for company_name, company in llm_config.items():
        if model in company['models']:
            return company
    return None

def print_models():
    table = Table(title="Available Models")
    table.add_column("Company", style="cyan", no_wrap=True)
    table.add_column("Model", style="magenta")

    models = {}
    for company_name, company in llm_config.items():
        for model in company['models']:
            models[model] = company_name

    last_company = ''
    for model, company_name in models.items():
        if company_name == last_company:
            table.add_row("", model)
        else:
            table.add_row(company_name, model)
        last_company = company_name

    console.print(table)


def send_request(llm, question: str):
    llm['user_input'] = question
    header_template = Template(llm['tplHeader'])
    hdr_str = header_template.render(llm)
    hdr = json.loads(hdr_str)

    data_template = Template(llm['tplData'])
    data = data_template.render(llm)

    if llm['debug']:
        console.print(f"[bold blue]Data to be sent to {llm['company']} API:[/bold blue]")
        console.print(data)

    console.print(f"[bold blue]asking {llm['company']}::{llm['model']}", end='')
    # Create a thread to run the print_dot function
    dot_thread = threading.Thread(target=print_dot)
    start_time = time.time()
    try:

        dot_thread.start()  # Start the thread
        response = requests.post(llm['url'], headers=hdr, data=data)
    finally:
        elapsed_time = time.time() - start_time
        stop_event.set()  # Signal the thread to stop
        dot_thread.join()  # Wait for the thread to finish
        console.print(f" {elapsed_time:.2f} secs")

    if response.status_code != 200:
        console.print(f"[bold red]Error calling {llm['company']}::{llm['model']} API: {response.status_code} {response.reason}[/bold red]")
        console.print(f"url: {llm['url']}")
        console.print("header: ", hdr)
        console.print("data: ", data)

        if llm['response_text_is_json']:
            err = json.loads(response.text)
            console.print(f"[bold red]{err}[/bold red]")
        else:
            console.print(f"[bold blue]Response from {llm['company']} API:[/bold blue]")
            console.print(response.text)

        exit(1)

    try:
        response_obj = json.loads(response.text)
    except KeyError as err:
        console.print(f"[bold red]Json Error from {llm['company']} API:[/bold red]")
        console.print(response.text)
        exit(1)

    if llm['debug']:
        console.print(f"[bold blue]Response from {llm['company']} API:[/bold blue]")
        console.print(response_obj)

    return_obj = response_obj
    for idx in llm['response_keys']:
        return_obj = return_obj[idx]

    return return_obj


