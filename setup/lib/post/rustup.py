import subprocess


def trigger():
    subprocess.run(["rustup", "default", "stable"])
