import argparse
import platform
import subprocess

import requests
import json
import keyring
import sys
from jinja2 import Template
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from config import config
from rich.console import Console
from rich.table import Table

import configparser
import os

VERSION_NO = '0.9.8'

# Dangerous commands list
DANGEROUS_COMMANDS = [
    "rm", "del", "mkfs", "dd", "shutdown", "poweroff", "reboot", "format"
]

def get_options_file_path(filename='cmdai.ini'):
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, filename)


def save_options(options, filename='cmdai.ini'):
    conf = configparser.ConfigParser()
    conf['DEFAULT'] = options
    with open(get_options_file_path(filename), 'w') as configfile:
        conf.write(configfile)


def load_options(filename='cmdai.ini'):
    config = configparser.ConfigParser()
    config.read(get_options_file_path(filename))
    return config['DEFAULT']


console = Console()


def is_dangerous_command(command: str) -> bool:
    # Split the command to get the base command
    base_command = command.split()[0]
    return base_command in DANGEROUS_COMMANDS


def execute_command(command: str):
    if is_dangerous_command(command):
        console.print("[bold red]Error: Dangerous command detected![/bold red]")
        return "Error", "Dangerous Command"

    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        # console.print("[bold green]Command executed successfully![/bold green]")
        console.print(result.stdout)
        return 'success', result.stdout

    except subprocess.CalledProcessError as e:
        console.print("[bold red]Command execution failed![/bold red]")
        console.print(f"[red]{e.stderr}[/red]")
        return 'error',e.stderr


def ask_to_execute_command(command: str, llm: dict):
    response = Prompt.ask(
        f"{command} [bold blue]Yes/No[/]",default="No")

    if response[0].lower() == "y":
        # console.print("[bold green]Executing the command...[/bold green]")
        rc, txt = execute_command(command)
        return rc, txt
    else:
        return "Ignored", command



def send_request(llm):
    console.print( f"[bold blue]asking {llm['company']}::{llm['model']}...",end='')
    header_template = Template(llm['tplHeader'])
    hdr_str = header_template.render(llm)
    hdr = json.loads(hdr_str)

    data_template = Template(llm['tplData'])
    data = data_template.render(llm)

    if llm['debug']:
        console.print(f"[bold blue]Data to be sent to {llm['company']} API:[/bold blue]")
        console.print(data)

    response = requests.post(llm['url'], headers=hdr, data=data)

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

    console.print(f"[bold blue]execute? [/]")


    return return_obj



def print_models(models:dict):
    table = Table(title="Available Models")
    table.add_column("Company", style="cyan", no_wrap=True)
    table.add_column("Model", style="magenta")

    last_company = ''
    for model, company_name in models.items():
        if company_name == last_company:
            table.add_row("", model)
        else:
            table.add_row(company_name, model)
        last_company = company_name

    console.print(table)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', help='Name of the model')
    # parser.add_argument('-q', '--question', help='The user question')
    parser.add_argument('question', nargs='?', help='The user question')
    parser.add_argument('-l', '--list', action='store_true', help='List all companies and models')
    parser.add_argument('-k', '--key', action='store_true', help='Ask for (new) Company Key')
    parser.add_argument('-d', '--debug', action='store_true', help='Print message to LLM, for debugging purposes.')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION_NO}')
    args = parser.parse_args()

    loaded_options = load_options()
    # print(dict(loaded_options))

    models = {}
    for company_name, company in config.items():
        for model in company['models']:
            models[model] = company_name

    if args.list:
        print_models(models)
        sys.exit(0)

    if not args.question:
        console.print("[bold red]A question is required for this operation.[/bold red]")
        sys.exit(1)

    model = args.model
    if not model:
        model = loaded_options['model']

    if model not in models:
        console.print(f"[bold red]Model {model} is not defined.[/bold red]")
        sys.exit(1)

    company_name = models[model]
    llm = config[company_name]

    try:
        API_KEY = keyring.get_password('cmdai', username=llm['api_key'])
    except keyring.errors.PasswordDeleteError:
        console.print(f"[bold red]Error accessing keyring ('cmdai', username={llm['api_key']})[/bold red]")
        API_KEY = None

    if args.key:
        API_KEY = None

    if API_KEY is None:
        API_KEY = console.input(f"Please enter your {company_name} API key: ")
        keyring.set_password("cmdai", username=llm['api_key'], password=API_KEY)

    if not API_KEY:
        console.print("[bold red]API key cannot be empty.[/bold red]")
        sys.exit(1)

    llm['API_KEY'] = API_KEY
    llm['user_input'] = args.question
    llm['os_system'] = platform.platform(terse=True)
    llm['model'] = model
    llm['company'] = company_name
    llm['debug'] = args.debug

    # Example usage
    user_options = {'model': model}
    save_options(user_options)

    cmd = send_request(llm)
    # console.print(cmd)
    return_code, result = ask_to_execute_command(cmd, llm)

