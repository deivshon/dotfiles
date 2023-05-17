import json

SETUP_STATUS = "./setup_status.json"
PACKAGES_INSTALLED = "packages-installed"
POST_INSTALL_OPS = "post-install-operations"
STYLE = "style"


def get():
    with open(SETUP_STATUS, "r") as f:
        status = json.loads(f.read())

    if PACKAGES_INSTALLED not in status:
        status[PACKAGES_INSTALLED] = False

    if POST_INSTALL_OPS not in status:
        status[POST_INSTALL_OPS] = False

    return status


def write(status):
    with open(SETUP_STATUS, "w") as f:
        f.write(json.dumps(status, indent=4) + "\n")


def new():
    status = {}
    status[PACKAGES_INSTALLED] = False
    status[POST_INSTALL_OPS] = False

    return status
