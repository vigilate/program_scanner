#!/usr/bin/env python3

import requests
import json
import subprocess
import platform

if "windows" in platform.system().lower():
    import wmi
    import winreg

# this config var will be move with all the config of this scanner
url_backend = "DEFAULT_SCHEME://DEFAULT_URL/api/v1/uprog/"
user = "DEFAULT_USER"
token = "DEFAULT_TOKEN"
station = "DEFAULT_ID"

def get_format_progs(progs):
    ret = []
    for prog in progs.keys():
        ret.append({"program_name" : prog, "program_version" : progs[prog]})
    return ret

def add_raw_prog(progs, name, version):
    if name in progs:
        if not version in progs[name]:
            progs[name].append(version)
    else:
        progs[name] = [version]

def send_data(prog_list):
    data = json.dumps({"programs_list" : get_format_progs(prog_list), "poste" : station})
    headers = {'Accept': 'application/json; indent=4', 'content-type': 'application/x-www-form-urlencoded'}

    r = requests.post(url_backend, data=data, auth=(user, token), headers=headers)
    
    if not r.ok:
        return False
    return True

def get_pacman_progs(progs):
    try:
        p = subprocess.check_output(['pacman', '-Q'])
    except FileNotFoundError:
        return []
    output = p.decode().split('\n')

    for l in filter(None, output):
        add_raw_prog(progs, l.split(' ')[0], l.split(' ')[1].split('-')[0])

def get_pkg_progs(progs):
    try:
        p = subprocess.check_output(['pkg', 'info'])
    except FileNotFoundError:
        return []

    output = [prog.split(' ')[0].split('_')[0] for prog in p.decode().split('\n')]

    for prog in filter(None, output):
        add_raw_prog(progs, ''.join(prog.split('-')[:-1]), prog.split('-')[-1])

def get_dpkg_progs(progs):
    try:
        p = subprocess.check_output(['dpkg', '-l'])
    except FileNotFoundError:
        return []

    output = p.decode()
    if not "===" in output:
        return []

    output = output.split('\n')
    while not output[0].endswith("==="):
        output.pop(0)

    for l in filter(None, output[1:]):
        prog = list(filter(None, l.split(' ')))
        add_raw_prog(progs, prog[1], prog[2].split('-')[0])

def get_rpm_progs(progs):
    try:
        p = subprocess.check_output(['rpm', '-qia'])
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

    output = [':'.join(prog.split('\n')[:3]).split(':')[1::2] for prog in p.decode().split('Name')]

    for prog in output[1:]:
        add_raw_prog(progs, prog[0], '-'.join([p.strip() for p in prog[1:-1]]))

def get_mac_progs(progs):
    try:
        p = subprocess.check_output(['system_profiler', 'SPApplicationsDataType'])
    except FileNotFoundError:
        return []

    output = p.decode().split('\n\n    ')[1:]
    output = [output[off*2:off*2+2] for off in range(int(len(output) / 2))]

    for prog in filter(lambda x: "Version:" in x[1], output):
        add_raw_prog(progs, prog[0][:-1], prog[1].split('Version:')[1].split('\n')[0].strip())

def get_windows_progs(progs):
    for prog in wmi.WMI().Win32_Product():
        add_raw_prog(progs, prog.wmi_property("Name").value, prog.wmi_property("Version").value)

    r = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key = winreg.OpenKey(r, "Software\microsoft\Windows\CurrentVersion\\Uninstall")
    (nb_subKey, useless, useless) = winreg.QueryInfoKey(key)

    already = list(progs.keys())

    for idx in range(nb_subKey):
        key_name = winreg.EnumKey(key, idx)
        sub_key = winreg.OpenKey(key, key_name)
        try :
            (prog_name, useless) = winreg.QueryValueEx(sub_key, "DisplayName")
            (version, useless) = winreg.QueryValueEx(sub_key, "DisplayVersion")
        except FileNotFoundError:
            continue
        if prog_name not in already:
            add_raw_prog(progs, prog_name, version)
        winreg.CloseKey(sub_key)
    winreg.CloseKey(key)

    key = winreg.OpenKey(r, "Software\Wow6432Node\microsoft\Windows\CurrentVersion\\Uninstall")
    (nb_subKey, useless, useless) = winreg.QueryInfoKey(key)

    already = list(progs.keys())

    for idx in range(nb_subKey):
        key_name = winreg.EnumKey(key, idx)
        sub_key = winreg.OpenKey(key, key_name)
        try :
            (prog_name, useless) = winreg.QueryValueEx(sub_key, "DisplayName")
            (version, useless) = winreg.QueryValueEx(sub_key, "DisplayVersion")
        except FileNotFoundError:
            continue
        if prog_name not in already:
            add_raw_prog(progs, prog_name, version)
        winreg.CloseKey(sub_key)
    winreg.CloseKey(key)

    key = winreg.OpenKey(r, "Software\Microsoft\Internet Explorer");
    if key:
        add_raw_prog(progs, "Internet Explorer", winreg.QueryValueEx(key, "Version")[0])

    r.Close()

def main():
    progs = {}


    if platform.system() == "Linux":
        get_pacman_progs(progs)
        get_dpkg_progs(progs)
        get_rpm_progs(progs)
    elif "bsd" in platform.system().lower():
        get_pkg_progs(progs)
    elif "darwin" in platform.system().lower():
        get_mac_progs(progs)
    elif "windows" in platform.system().lower():
        get_windows_progs(progs)

    print(send_data(progs))

if __name__ == '__main__':
    main()
