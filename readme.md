# The Python program calling AI LLM for command line help
## aie.py

The python program aie.py is executed to translate the question into a shell command.
You give it the question as the first argument.
and -shell=_name_  where _name_ must be one of [cmd, powershell, or bash]
and it returns a command to do what you asked.

It requires a .env file in users home directory.
the contents are: 

    OPENAI_API_KEY=<Your open ai key>
    MISTRAL_API_KEY=<Your mistral ai key>
    LLM_MODEL='mistral-large-latest'
    # valid for LLM_MODEL:
    # OpenAI: gpt-4, gpt-4-turbo-preview, gpt-3.5-turbo
    # Mistral: open-mistral-7b, open-mixtral-8x7b, 
    #          mistral-small-latest, mistral-medium-latest, mistral-large-latest

## Operating system Integration.
Setting and maintaining a python environment on each installation machine was considered overkill.
In its stead the program pyinstaller is used to make a pseudo executable for each operating system.
the command "pyinstaller --onefile --console aie.py" must be run on each operating system.

I've setup Github actions to do this.  The executables are:


| **operating system** | **filename** | 
|----------------------|--------------|
| windows              | aie_win.exe  |
| linux                | aie_linux    |
| macos                | aie_mac      |


# Shell integration
## Linux Bash

### ai.sh

The ai.shell:
- prompts for question if none was given.
- Translates question to bash command via:
 
  OUTPUT=$(aie "$question" -shell=bash)
- uses xdotool type to insert command as if you had typed it.

### ~/.bashrc
to allow ai syntax sugar:

    ai "list open ports"
add following line in ~/.bashrc:

    alias ai='ai.sh'

## Windows Powershell

### ai.ps1

 the powershell script: ai.ps1: calls 
   - 'aie.exe "$question" -shell=powershell'  (to do the translation)
   - Then turns string $COMMAND into keystrokes (escaping special characters)
   - and then inserts the keystrokes into the commandline

### C:\Users\<username>\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1

To allow the syntax sugar: 

    ai 'list open ports' 

You need to add the following in the profile file:

    function Run-AIScript {
        param(
            [Parameter(Position=0, Mandatory=$false)]
            [string]$question
        )
        & 'ai.ps1' $question
    }
    Set-Alias -Name ai -Value Run-AIScript


# Windows Cmd.exe
Unfortunately, the Windows/Dos Cmd.exe is very limited.  Therefore, another 
approach was required, namely a prompt asking user to confirm execution on not.

  
    (.venv) C:\Users\Jerry\PycharmProjects\cmdai>ai "List open Ports"
    AI Cmd: [netstat -ano | findstr /i "listening"] execute? (y/n) y
      TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       960
      TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
      TCP    0.0.0.0:5040           0.0.0.0:0              LISTENING       592
      TCP    0.0.0.0:7680           0.0.0.0:0              LISTENING       1196
      TCP    0.0.0.0:49664          0.0.0.0:0              LISTENING       712
      TCP    0.0.0.0:49665          0.0.0.0:0              LISTENING       560
      TCP    0.0.0.0:49666          0.0.0.0:0              LISTENING       1200
      TCP    0.0.0.0:49667          0.0.0.0:0              LISTENING       1364
      TCP    0.0.0.0:49668          0.0.0.0:0              LISTENING       2632
      TCP    0.0.0.0:49669          0.0.0.0:0              LISTENING       704
      TCP    10.0.2.15:139          0.0.0.0:0              LISTENING       4
      TCP    127.0.0.1:52829        0.0.0.0:0              LISTENING       7436
      TCP    [::]:135               [::]:0                 LISTENING       960
      TCP    [::]:445               [::]:0                 LISTENING       4
      TCP    [::]:7680              [::]:0                 LISTENING       1196
      TCP    [::]:49664             [::]:0                 LISTENING       712
      TCP    [::]:49665             [::]:0                 LISTENING       560
      TCP    [::]:49666             [::]:0                 LISTENING       1200
      TCP    [::]:49667             [::]:0                 LISTENING       1364
      TCP    [::]:49668             [::]:0                 LISTENING       2632
      TCP    [::]:49669             [::]:0                 LISTENING       704
    
    (.venv) C:\Users\Jerry\PycharmProjects\cmdai>

Although less intuitive than bash or powershell integration, it is still useful.



# MacOS
