import subprocess


def trigger():
    subprocess.run(["sudo", "systemctl", "enable", "reflector.service"])
