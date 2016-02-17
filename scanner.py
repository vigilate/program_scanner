#!/usr/bin/python3
# shebang issue with freebsd: /usr/local/bin/python3 instead of /usr/bin/python3

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

    r = requests.post(url_backend, data="query="+data, auth=(user, mdp), headers=headers)
    
    if not r.ok:
        return False
    return True

def get_pacman_progs():
    try:
        p = subprocess.check_output(['pacman', '-Q'])
    except FileNotFoundError:
        return []
    output = p.decode().split('\n')

    progs = []
    for l in filter(None, output):
        progs.append({"program1_name" : l.split(' ')[0], "program_version" : l.split(' ')[1]})

    return progs

def get_pkg_progs():
    try:
        p = subprocess.check_output(['pkg', 'info'])
    except FileNotFoundError:
        return []

    output = [prog.split(' ')[0] for prog in p.decode().split('\n')]

    progs = []
    for prog in filter(None, output):
        progs.append({"program_name" : ''.join(prog.split('-')[:-1]), "program_version" : prog.split('-')[-1]})
    print(progs)
    return progs

def get_dpkg_progs():
    try:
        p = subprocess.check_output(['dpkg', '-l'])
    except FileNotFoundError:
        return []

    output = p.decode().split('\n')
    while not output[0].endswith("==="):
        output.pop(0)

    progs = []
    for l in filter(None, output[1:]):
        prog = list(filter(None, l.split(' ')))
        progs.append({"program_name" : prog[1], "program_version" : prog[2]})
        
    return progs

def get_rpm_progs():
    try:
        p = subprocess.check_output(['rpm', '-qia'])
    except FileNotFoundError:
        return []

    output = [':'.join(prog.split('\n')[:3]).split(':')[1::2] for prog in p.decode().split('Name')]

    progs = []
    for prog in output[1:]:
        progs.append({"program_name" : prog[0], "program_version" : '-'.join([p.strip() for p in prog[1:]])})

    return progs

def main():
    progs = []


    if platform.system() == "Linux":
        progs += get_pacman_progs()
        progs += get_dpkg_progs()
        progs += get_rpm_progs()
    elif "bsd" in platform.system().lower():
        progs += get_pkg_progs()
        
    print(send_data(progs))

if __name__ == '__main__':
    main()

# progs = [{"program_name" : "program1_name", "program_version" : "version_prog1"},
#          {"program_name" : "program2_name", "program_version" : "version_prog2"},
#          {"program_name" : "program3_name", "program_version" : "version_prog3"},
#          {"program_name" : "program4_name", "program_version" : "version_prog4"}]

# send_data(progs)
