import subprocess

__termColors = {
    "red": subprocess.run(["tput", "setaf", "1", "bold"], capture_output = True).stdout.decode(),
    "green": subprocess.run(["tput", "setaf", "2", "bold"], capture_output = True).stdout.decode(),
    "yellow": subprocess.run(["tput", "setaf", "3", "bold"], capture_output = True).stdout.decode(),
    "blue": subprocess.run(["tput", "setaf", "4", "bold"], capture_output = True).stdout.decode(),
    "magenta": subprocess.run(["tput", "setaf", "5", "bold"], capture_output = True).stdout.decode(),
    "cyan": subprocess.run(["tput", "setaf", "6", "bold"], capture_output = True).stdout.decode(),
    "white": subprocess.run(["tput", "setaf", "7", "bold"], capture_output = True).stdout.decode()
}
__normalTermColor = subprocess.run(["tput", "sgr0"], capture_output = True).stdout.decode()

# args format: [str, color, str, color ...]
def colorPrint(*args):
    resultStr = ""
    for i in range(0, len(args), 2):
        resultStr += __termColors[args[i + 1]] + args[i] + __normalTermColor
    print(resultStr)
