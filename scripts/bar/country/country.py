#!/bin/python3

import os
import requests

def update():
    data = requests.get('https://am.i.mullvad.net/json').json()
    with open(auxFilePath, "w") as fp:
        if(data["mullvad_exit_ip"]):
            if "wireguard" in data["mullvad_exit_ip_hostname"]:
                data["mullvad_exit_ip_hostname"] = data["mullvad_exit_ip_hostname"].replace("wireguard", "wg")
            fp.write(data["mullvad_exit_ip_hostname"] + " - " + data["city"] + "\n0\n")
            print(data["mullvad_exit_ip_hostname"] + " - " + data["city"])
        else:
            fp.write("N/C - " + data["country"] + "\n0\n")
            print("N/C - " + data["country"])

auxFilePath = "/tmp/countryData"
freq = 60

if(os.path.exists(auxFilePath)):
    with open(auxFilePath, "r") as fp:
        content = fp.read().splitlines()
        if(content == []):
            update()
            quit()
    if(int(content[1]) < freq):
        print(content[0])
        content[1] = int(content[1]) + 1
        with open(auxFilePath, "w") as fp:
            fp.write(content[0] + "\n" + str(content[1]) + "\n")      
    else:
        update() 
else:
    update()
