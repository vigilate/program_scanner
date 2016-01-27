#!/usr/bin/python3

import requests
import json
import subprocess
import platform

# this config var will be move with all the config of this scanner
url_backend = "http://127.0.0.1/api/uprog/submit_programs/"
user = "vigilate"
mdp = "vigilate"

# prog_list has to be a list like that :
# [{"program" : "program1_name", "version" : "version_prog1"},
#  {"program" : "program2_name", "version" : "version_prog2"}, ...]
def send_data(prog_list):
    data = json.dumps({"programs_list" : prog_list})
    headers = {'Accept': 'application/json; indent=4', 'content-type': 'application/x-www-form-urlencoded'}
    print(data)
    r = requests.post(url_backend, data="query="+data, auth=(user, mdp), headers=headers)
    print(r.text)
    if not r.ok:
        return False
    return True

def get_pacman_progs():
    #pacman -Q
    return []

def get_pkg_progs():
    #pkg_info
    return []

def get_dpkg_progs():
    try:
        p = subprocess.run(['dpkg', '-l'], stdout=subprocess.PIPE)
    except FileNotFoundError:
        return []

    output = p.stdout.decode().split('\n')
    while not output[0].endswith("==="):
        output.pop(0)

    progs = []
    for l in output[1:-1]:
        prog = list(filter(None, l.split(' ')))
        progs.append({"program_name" : prog[1], "program_version" : prog[2]})
        
    return progs

def get_rpm_progs():
    #rpm -qa
    return []

def main():
    progs = {"programs_list" : []}

    if platform.system() == "Linux":
        progs["programs_list"] += get_pacman_progs()
        progs["programs_list"] += get_pkg_progs()
        progs["programs_list"] += get_dpkg_progs()
        progs["programs_list"] += get_rpm_progs()
    print(send_data(progs))

if __name__ == '__main__':
    main()

# progs = [{"program_name" : "program1_name", "program_version" : "version_prog1"},
#          {"program_name" : "program2_name", "program_version" : "version_prog2"},
#          {"program_name" : "program3_name", "program_version" : "version_prog3"},
#          {"program_name" : "program4_name", "program_version" : "version_prog4"}]

# send_data(progs)
