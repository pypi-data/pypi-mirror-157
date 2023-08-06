import argparse

from rcn.http.client import RCNHttpClient, configDir
from yaml import SafeLoader, load, dump, SafeDumper
import os
from getpass import getpass
import rcn.profile_func


def profile(actions):
    if actions[0] == "ls":
        rcn.profile_func.ls()
    elif actions[0] == "set-default":
        rcn.profile_func.setDefault(actions[1])
    elif actions[0] == "configure":
        rcn.profile_func.configure(actions[1])
    elif actions[0] == "delete":
        rcn.profile_func.delete(actions[1])

def configure(profile, username=None):
    server_url = "http://localhost:8080/backend"
    x = input(f"Server Url({server_url}): ")
    if x.strip() != "":
        server_url = x
    username = input("Username: ")
    password = getpass()

    kwargs = {
        "server": server_url
    }
    client = RCNHttpClient(**kwargs)
    response = client.login({
        "username": username,
        "password": password
    }).json()

    data = {
        "server": server_url,
        "token": response['jwt'],
        "profile": profile
    }
    absPath = os.path.join(configDir, f"{profile}.yml")
    with open(absPath, "w") as file:
        dump(data, file)