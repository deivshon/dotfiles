import os
import subprocess
from matplotlib.colors import hex2color, hsv_to_rgb, rgb_to_hsv, rgb2hex

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

def whitelistChars(string, whitelist):
    return ''.join([char for char in string if char in whitelist])

def hex_to_hsv(hex):
    return rgb_to_hsv(hex2color(hex))

def hsv_to_hex(hsv):
    return rgb2hex(hsv_to_rgb(hsv))

def hex_to_divided_hsv(hex):
    hsv = rgb_to_hsv(hex2color(hex))
    return hsv[0], hsv[1], hsv[2]

def apply_hue(s, v, color):
    h = hex_to_hsv(color)[0]
    return hsv_to_hex((h, s, v))

def make_dirs(path):
    subprocess.run(["mkdir", "-p", path])

def get_last_node(path):
    return path[::-1][0:path[::-1].index("/")][::-1]

def get_wallpaper_path(wallpaperName):
    return f"{os.path.expanduser('~')}/Pictures/{wallpaperName}"

def sed_escape_path(str):
    return str.replace("/", "\/")
