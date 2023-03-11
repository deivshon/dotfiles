import sys

RED =       "r"
GREEN =     "g"
YELLOW =    "y"
BLUE =      "b"
MAGENTA =   "m"
CYAN =      "c"
WHITE =     "w"

__termColors = {
    RED:        "\033[1m\033[31m",
    GREEN:      "\033[1m\033[32m",
    YELLOW:     "\033[1m\033[33m",
    BLUE:       "\033[1m\033[34m",
    MAGENTA:    "\033[1m\033[35m",
    CYAN:       "\033[1m\033[36m",
    WHITE:      "\033[1m\033[37m"
}

__normalTermColor = "\033[0m\033[37m"

# args format: [str, color, str, color ...]
def colorPrint(*args):
    resultStr = ""
    for i in range(0, len(args), 2):
        if args[i + 1] not in __termColors:
            sys.exit(f"Unrecognized color: {args[i + 1]}")

        resultStr += __termColors[args[i + 1]] + args[i] + __normalTermColor

    print(resultStr)
