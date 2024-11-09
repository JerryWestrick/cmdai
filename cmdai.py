import argparse
import platform
import subprocess

import call_llm

import sys

from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

import configparser
import os
import keyring

import asyncio

VERSION_NO = '0.9'

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


def execute_command(command: str) -> (bool, str) :
    if is_dangerous_command(command):
        console.print("[bold red]Error: Dangerous command detected![/bold red]")
        return False, "Dangerous Command"

    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        # console.print("[bold green]Command executed successfully![/bold green]")
        # console.print(result.stdout)
        return True, result.stdout

    except subprocess.CalledProcessError as e:
        console.print("[bold red]Command execution failed![/bold red]")
        console.print(f"[red]{e.stderr}[/red]")
        return False,e.stderr


def ask_to_execute_command(command: str, llm: dict) -> bool:
    response = Prompt.ask(
        f"{command} [bold blue]Yes/No[/]",default="No")

    return response[0].lower() == "y"


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

    if args.list:
        call_llm.print_models()
        sys.exit(0)

    if not args.question:
        console.print("[bold red]A question is required for this operation.[/bold red]")
        sys.exit(1)

    model = args.model

    if not model:  # if no model given use last one used...
        model = loaded_options['model']

    llm = call_llm.get_llm(model)
    if not llm:
        console.print(f"[bold red]Model {model} is not defined.[/bold red]")
        sys.exit(1)

    try:
        api_key = keyring.get_password('cmdai', username=llm['api_key'])
    except keyring.errors.PasswordDeleteError:
        console.print(f"[bold red]Error accessing keyring ('cmdai', username={llm['api_key']})[/bold red]")
        api_key = None

    if args.key:
        api_key = None

    if api_key is None:
        api_key = console.input(f"Please enter your {llm['company']} API key: ")
        keyring.set_password("cmdai", username=llm['api_key'], password=api_key)

    if not api_key:
        console.print("[bold red]API key cannot be empty.[/bold red]")
        sys.exit(1)

    llm['API_KEY'] = api_key
    llm['os_system'] = platform.platform(terse=True)
    llm['model'] = model
    llm['debug'] = args.debug

    # Example usage
    user_options = {'model': model}
    save_options(user_options)

    cmd = call_llm.send_request(llm, args.question)
    if not ask_to_execute_command(cmd, llm):
        console.print("skipping...")
        exit(0)

    rc, txt = execute_command(cmd)
    if rc:
        console.print(txt)
    else:
        console.print(f"[red]{txt}[/]")

