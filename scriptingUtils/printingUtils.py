import subprocess

# args format: [str, color, str, color ...]
def printCol(*args):
    def printColAux(s, col):
        if(col == "cyan"):
            colCode = subprocess.run(["tput", "setaf", "6", "bold"], capture_output = True).stdout.decode()
        elif(col == "red"):
            colCode = subprocess.run(["tput", "setaf", "1", "bold"], capture_output = True).stdout.decode()
        elif(col == "green"):
            colCode = subprocess.run(["tput", "setaf", "2", "bold"], capture_output = True).stdout.decode()
        elif(col == "yellow"):
            colCode = subprocess.run(["tput", "setaf", "3", "bold"], capture_output = True).stdout.decode()
        elif(col == "white"):
            colCode = subprocess.run(["tput", "setaf", "7", "bold"], capture_output = True).stdout.decode()
        else:
            return s

        normal = subprocess.run(["tput", "sgr0"], capture_output = True).stdout.decode()
        return colCode + s + normal

    resultStr = ""
    for i in range(0, len(args), 2):
        resultStr += printColAux(args[i], args[i + 1])
    print(resultStr)

