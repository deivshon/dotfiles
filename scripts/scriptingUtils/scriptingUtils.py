import subprocess

def pipeline(commandList, printLastOutput = False, printError = True):
    currentCommand = 0
    for i in range(0, len(commandList)):
        if(i == 0):
            currentCommand = subprocess.Popen(commandList[i], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        else:
            currentCommand = subprocess.Popen(commandList[i], stdin = currentCommand.stdout, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        currentCommand.wait()
        err = currentCommand.stderr.read().decode()
        if(err != ""):
            if(printError):
                print("A error occurred:\n" + err)
            return False
    result = currentCommand.stdout.read().decode()
    if(printLastOutput):
        print(result)
    return result
