# Command Line AI Assistance
## usage


![](Screenshot.png)

## cmdai

cmdai is an executable built from the python program cmdai.py. 
You give it a question and it returns the appropriate shell command.

    jerry@desktop:~$ cmdai --help
    usage: cmdai [-h] [-m MODEL] [-l] [-k] [-d] [-v] [question]
    
    positional arguments:
      question              The user question
    
    options:
      -h, --help            show this help message and exit
      -m MODEL, --model MODEL
                            Name of the model
      -l, --list            List all companies and models
      -k, --key             Ask for (new) Company Key
      -d, --debug           Print message to LLM, for debugging purposes.
      -v, --version         show program's version number and exit
    

## Version
    jerry@desktop:~$ cmdai --version
    cmdai 1.0


## Supported LLms:

### Available Models
![](ListModels.png)

### Select LLM
Select your llm with the ***--model gpt-4o-mini*** <-- Use this model

Once a model is selected it will be used until you select a different model.

## API KEYs
The program requires an API_KEY from each company to access the LLM.

You will be Screenshotprompted for the api key the first time you use an LLM of a company 
or when you specify --key option to set new key.  
Keys are securely stored on your machine, using python keyring package.


    $ cmdai "list the current values of my temperature sensors" -k
    Please enter your OpenAI API key: [paste your key here]
    asking OpenAI::gpt-4o-mini...execute? 
    sensors Yes/No (No): n
    $ 


## Operating System Integration.
I've built (or plan to build) executables for 3 operating systems

| **operating system** | **filename**  | 
|----------------------|---------------|
| windows              | win/cmdai.exe |
| linux                | lin/cmdai     |
| macos                | mac/cmdai     |

### Linux
1. Copy the file lin/cmdai to the directory ~/.local/bin/
2. make sure ~./local/bin is in your executable path.

### Windows
1. Copy the file win/cmdai.exe to the directory ???
2. make sure ??? is in your executable path.

## MacOs
1. Copy the file mac/cmdai to the directory ???
2. make sure ??? is in your executable path.


## Building Executables
executables are built using the pyinstaller command: 

`bash
pyinstaller --onefile cmdai.py
`
This command will create an executable called cmdai (cmdai.exe on windows)
This file will be in the dist\ directory.
You need to copy it to the correct os directory:

| **operating system** | **filename**  | 
|----------------------|---------------|
| windows              | win/cmdai.exe |
| linux                | lin/cmdai     |
| macos                | mac/cmdai     |



# Eh Th-Th-Th-Th-Th-Th-That is all Folks!
enjoy