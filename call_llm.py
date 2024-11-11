import os
import json
import requests
from rich.console import Console
from rich.table import Table
from jinja2 import Template
import threading
import time

models_json = '''
{
  "gpt-4o-mini":                {"company": "OpenAI",   "model": "gpt-4o-mini",               "input": 0.00000015,  "output": 0.0000006,  "context": 128000},
  "gpt-4o":                     {"company": "OpenAI",   "model": "gpt-4o",                    "input": 0.0000025,   "output": 0.00001,    "context": 128000},
  "gpt-4o-2024-05-13":          {"company": "OpenAI",   "model": "gpt-4o-2024-05-13",         "input": 0.000005,    "output": 0.000015,   "context": 128000},
  "gpt-4o-mini-2024-07-18":     {"company": "OpenAI",   "model": "gpt-4o-mini-2024-07-18",    "input": 0.00000015,  "output": 0.0000006,  "context": 128000},
  "gpt-4o-2024-08-06":          {"company": "OpenAI",   "model": "gpt-4o-2024-08-06",         "input": 0.0000025,   "output": 0.00001,    "context": 128000},
  "o1-preview":                 {"company": "OpenAI",   "model": "o1-preview",                "input": 0.000003,    "output": 0.000012,   "context": 128000},
  "o1-mini":                    {"company": "OpenAI",   "model": "o1-mini",                   "input": 0.0000006,   "output": 0.0000024,  "context": 128000},
  "mistral-large-2407":         {"company": "MistralAI","model": "mistral-large-2407",        "input": 0.000002,    "output": 0.000006,   "context": 128000},
  "mistral-small-2409":         {"company": "MistralAI","model": "mistral-small-2409",        "input": 0.0000002,   "output": 0.0000006,  "context": 128000},
  "codestral-2405":             {"company": "MistralAI","model": "codestral-2405",            "input": 0.0000002,   "output": 0.0000006,  "context": 32000},
  "ministral-8b-latest":        {"company": "MistralAI","model": "ministral-8b-latest",       "input": 0.0000001,   "output": 0.0000001,  "context": 128000},
  "ministral-3b-latest":        {"company": "MistralAI","model": "ministral-3b-latest",       "input": 0.00000004,  "output": 0.00000004, "context": 128000},
  "mistral-embed":              {"company": "MistralAI","model": "mistral-embed",             "input": 0.0000001,   "output": 0.0000001,  "context": 32000},
  "mistral-moderation-24-11":   {"company": "MistralAI","model": "mistral-moderation-24-11",  "input": 0.0000001,   "output": 0.0000001,  "context": 8000},
  "pixtral-12b":                {"company": "MistralAI","model": "pixtral-12b",               "input": 0.00000015,  "output": 0.00000015, "context": 128000},
  "mistral-nemo":               {"company": "MistralAI","model": "mistral-nemo",              "input": 0.00000015,  "output": 0.00000015, "context": 32000},
  "open-mistral-7b":            {"company": "MistralAI","model": "open-mistral-7b",           "input": 0.00000025,  "output": 0.00000025, "context": 32000},
  "open-mixtral-8x7b":          {"company": "MistralAI","model": "open-mixtral-8x7b",         "input": 0.0000007,   "output": 0.0000007,  "context": 32000},
  "open-mixtral-8x22b":         {"company": "MistralAI","model": "open-mixtral-8x22b",        "input": 0.000002,    "output": 0.000006,   "context": 32000},
  "claude-3-5-sonnet-20240620": {"company": "Anthropic","model": "claude-3-5-sonnet-20240620","input": 0.000003,    "output": 0.000015,   "context": 4096},
  "claude-3-opus-20240229":     {"company": "Anthropic","model": "claude-3-opus-20240229",    "input": 0.000015,    "output": 0.000075,   "context": 4096},
  "claude-3-sonnet-20240229":   {"company": "Anthropic","model": "claude-3-sonnet-20240229",  "input": 0.000003,    "output": 0.000015,   "context": 4096},
  "claude-3-haiku-20240307":    {"company": "Anthropic","model": "claude-3-haiku-20240307",   "input": 0.00000025,  "output": 0.00000125, "context": 4096},
  "claude-2.1":                 {"company": "Anthropic","model": "claude-2.1",                "input": 0.000008,    "output": 0.000024,   "context": 4096},
  "claude-2.0":                 {"company": "Anthropic","model": "claude-2.0",                "input": 0.000008,    "output": 0.000024,   "context": 1000},
  "claude-instant-1.2":         {"company": "Anthropic","model": "claude-instant-1.2",        "input": 0.0000008,   "output": 0.0000024,  "context": 1000},
  "llama3":                     {"company": "Ollama",   "model": "llama3",                    "input": 0.0,         "output": 0.0,        "context": 4096},
  "phi3":                       {"company": "Ollama",   "model": "phi3",                      "input": 0.0,         "output": 0.0,        "context": 4096},
  "llama3-70b-8192":            {"company": "Groq",     "model": "llama3-70b-8192",           "input": 0.00000059,  "output": 0.00000079, "context": 8192},
  "grok-beta":                  {"company": "XAI",      "model": "grok-beta",                 "input": 0.00000059,  "output": 0.00000079, "context": 8192}
}
'''
models_config: dict[str,any] = json.loads(models_json)



console = Console()
stop_event = threading.Event()  # Event to signal when to stop the thread


def print_dot():
    while not stop_event.is_set():
        console.print('.', end='')
        time.sleep(0.5)

company_config = {
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
        "response_keys": ["choices", 0, "message", "content"],
        "usage_keys": ["prompt_tokens", "completion_tokens"]
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
        "response_keys": ["choices", 0, "message", "content"],
        "usage_keys": ["prompt_tokens", "completion_tokens"]
    },
    "MistralAI": {
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
        "response_keys": ["choices", 0, "message", "content"],
        "usage_keys": ["prompt_tokens", "completion_tokens"]
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
        "response_keys": ["content", 0, "text"],
        "usage_keys": ["input_tokens", "output_tokens"]
    }
}

def get_llm(model: str) -> dict[str,any] | None:

    if model in models_config:
        if models_config[model]['company'] in company_config:
            return company_config[models_config[model]['company']]
    return None


def print_models():
    table = Table(title="Available Models")
    table.add_column("Company", style="cyan", no_wrap=True)
    table.add_column("Model", style="green")
    table.add_column("Max Token", style="magenta", justify="right")
    table.add_column("$/mT In", style="green", justify="right")
    table.add_column("$/mT Out", style="green", justify="right")

    # Sort by LLM name, then model.
    sortable_keys = [f"{models_config[model]['company']}:{model}" for model in models_config.keys()]
    sortable_keys.sort()

    last_company = ''
    for k in sortable_keys:
        company, model_name = k.split(':', maxsplit=1)
        model = models_config.get(model_name)
        if company != last_company:
            table.add_row(company,
                          model_name,
                          str(model['context']),
                          f"{model['input']*1_000_000:06.4f}",
                          f"{model['output']*1_000_000:06.4f}"
                          )
            last_company = company
        else:
            table.add_row("", model_name, str(model['context']), f"{model['input']*1_000_000:06.4f}",
                      f"{model['output']*1_000_000:06.4f}")

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
    elapsed_time = 0
    model = models_config[llm['model']]
    try:
        dot_thread.start()  # Start the thread
        response = requests.post(llm['url'], headers=hdr, data=data)
    finally:
        elapsed_time = time.time() - start_time
        stop_event.set()  # Signal the thread to stop
        dot_thread.join()  # Wait for the thread to finish
        # console.print(f" {elapsed_time:.2f} secs Tokens In={response.usage.prompt_tokens}, Out={response.usage.completion_tokens},")

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

    usage = response_obj['usage']
    toks_in = usage[llm['usage_keys'][0]]
    cost_in = toks_in * model['input']
    toks_out = usage[llm['usage_keys'][1]]
    cost_out = toks_out * model['output']
    total = cost_in + cost_out
    console.print(f" {elapsed_time:.2f} secs Tokens In={toks_in}(${cost_in:06.4f}), Out={toks_out}(${cost_out:06.4f}) Total=${total:06.4f}")

    if llm['debug']:
        console.print(f"[bold blue]Response from {llm['company']} API:[/bold blue]")
        console.print(response_obj)

    return_obj = response_obj
    for idx in llm['response_keys']:
        return_obj = return_obj[idx]

    return return_obj


