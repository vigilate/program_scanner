#!/usr/bin/python3

import requests
import json

# this config var will be move with all the config of this scanner
url_backend = "127.0.0.1"

# prog_list has to be a list like that :
# [{"program" : "program1_name", "version" : "version_prog1"},
#  {"program" : "program2_name", "version" : "version_prog2"}, ...]
def send_datas(prog_list):
    data = json.dumps(prog_list)
    r = requests.post(url_backend, data)

    if not r.ok:
        return False
    return True
