# Load environment variables from .env file
foreach ($line in Get-Content .\.env) {
    if ($line -match '^\s*#') { continue }  # skip comment lines
    if ($line -match '^\s*$') { continue }  # skip blank lines
    $var, $value = $line.Split("=", 2)
    [Environment]::SetEnvironmentVariable($var, $value)
}
# Read command line argument or user input
if($args.Length -gt 0){
    $question = $args[0]
} else {
    $question = Read-Host -Prompt 'AI Question'
}
# Call the python script and store the output
$COMMAND = c:\Users\jerry\PycharmProjects\cmdai\.venv\Scripts\python.exe C:\Users\Jerry\PycharmProjects\cmdai\ai.py $question -shell=powershell
#Write $COMMAND
# Load the assembly required for sending keystrokes
Add-Type -AssemblyName System.Windows.Forms

# Example of sending keystrokes; this will type 'Hello, World!' in the active window
$escapedCommand = $COMMAND -replace '([+^%~(){}])', '{$1}'
[System.Windows.Forms.SendKeys]::SendWait($escapedCommand)