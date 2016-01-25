#!/usr/bin/python3

import requests
import json

# this config var will be move with all the config of this scanner
url_backend = "http://127.0.0.1/api/uprog/submit_programs/"
user = "vigilate"
mdp = "vigilate"

# prog_list has to be a list like that :
# [{"program" : "program1_name", "version" : "version_prog1"},
#  {"program" : "program2_name", "version" : "version_prog2"}, ...]
def send_data(prog_list):
    data = json.dumps({"programs_list" : prog_list})
#    headers = {'content-type': 'application/json'}
    headers = {'Accept': 'application/json; indent=4', 'content-type': 'application/x-www-form-urlencoded'}
    print(data)
    r = requests.post(url_backend, data="query="+data, auth=(user, mdp), headers=headers)
    print(r.text)
    if not r.ok:
        return False
    return True


progs = [{"program_name" : "program1_name", "program_version" : "version_prog1"},
         {"program_name" : "program2_name", "program_version" : "version_prog2"},
         {"program_name" : "program3_name", "program_version" : "version_prog3"},
         {"program_name" : "program4_name", "program_version" : "version_prog4"}]

send_data(progs)
