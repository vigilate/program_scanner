#!/usr/bin/env python3

import requests
import json
import subprocess
import platform

if "windows" in platform.system().lower():
    import wmi
    import winreg

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

def get_mac_progs():
    try:
        p = subprocess.check_output(['system_profiler', 'SPApplicationsDataType'])
    except FileNotFoundError:
        return []

    output = p.decode().split('\n\n    ')[1:]
    output = [output[off*2:off*2+2] for off in range(int(len(output) / 2))]

    progs = []
    for prog in filter(lambda x: "Version:" in x[1], output):
        progs.append({"program_name" : prog[0], "program_version" : prog[1].split('Version:')[1].split('\n')[0].strip()})

    return progs

def get_windows_progs():
    progs = []

    for prog in wmi.WMI().Win32_Product():
        prog = str(prog).split("\n")
        progs.append({"program_name" : prog[12].split('"')[-2], "program_version" : prog[-4].split('"')[-2]})

    r = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key = winreg.OpenKey(r, "Software\microsoft\Windows\CurrentVersion\\Uninstall")
    (nb_subKey, useless, useless) = winreg.QueryInfoKey(key)

    already = [p["program_name"] for p in progs]

    for idx in range(nb_subKey):
        key_name = winreg.EnumKey(key, idx)
        sub_key = winreg.OpenKey(key, key_name)
        try :
            (prog_name, useless) = winreg.QueryValueEx(sub_key, "DisplayName")
            (version, useless) = winreg.QueryValueEx(sub_key, "DisplayVersion")
        except FileNotFoundError:
            continue
        if prog_name not in already:
            progs.append({"program_name" : prog_name, "program_version" : version})
        winreg.CloseKey(sub_key)
    winreg.CloseKey(key)

    key = winreg.OpenKey(r, "Software\Wow6432Node\microsoft\Windows\CurrentVersion\\Uninstall")
    (nb_subKey, useless, useless) = winreg.QueryInfoKey(key)

    already = [p["program_name"] for p in progs]

    for idx in range(nb_subKey):
        key_name = winreg.EnumKey(key, idx)
        sub_key = winreg.OpenKey(key, key_name)
        try :
            (prog_name, useless) = winreg.QueryValueEx(sub_key, "DisplayName")
            (version, useless) = winreg.QueryValueEx(sub_key, "DisplayVersion")
        except FileNotFoundError:
            continue
        if prog_name not in already:
            progs.append({"program_name" : prog_name, "program_version" : version})
        winreg.CloseKey(sub_key)
    winreg.CloseKey(key)
    r.Close()
    return progs

def main():
    progs = []


    if platform.system() == "Linux":
        progs += get_pacman_progs()
        progs += get_dpkg_progs()
        progs += get_rpm_progs()
    elif "bsd" in platform.system().lower():
        progs += get_pkg_progs()
    elif "darwin" in platform.system().lower():
        progs += get_mac_progs()
    elif "windows" in platform.system().lower():
        progs += get_windows_progs()

    print(send_data(progs))

if __name__ == '__main__':
    main()

# progs = [{"program_name" : "program1_name", "program_version" : "version_prog1"},
#          {"program_name" : "program2_name", "program_version" : "version_prog2"},
#          {"program_name" : "program3_name", "program_version" : "version_prog3"},
#          {"program_name" : "program4_name", "program_version" : "version_prog4"}]

# send_data(progs)
