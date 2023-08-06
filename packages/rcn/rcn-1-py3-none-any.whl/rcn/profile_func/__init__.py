import os
from shutil import copyfile
from pick import pick

from rcn import configDir, RCNHttpClient
from rcn.utils import loadyaml, RCNConfig
import shutil

def ls():
    profiles = list(filter(lambda x: x.endswith(".yml"), os.listdir(configDir)))
    for i, profile in enumerate(profiles):
        print(f"{i+1}: {profile[:-4]}")

def setDefault(profile):
    src = os.path.join(configDir, f"{profile}.yml")
    dst = os.path.join(configDir, f"default.yml")

    copyfile(src, dst)

def delete(profile_name):
    src = os.path.join(configDir, f"{profile_name}.yml")
    rcnData = loadyaml(src)
    dirName = os.path.join(configDir, rcnData['profile'])

    if os.path.exists(dirName):
        shutil.rmtree(dirName)

    if os.path.exists(src):
        os.remove(src)


def configure(profile_name):
    src = os.path.join(configDir, f"{profile_name}.yml")
    if not os.path.exists(src):
        raise FileNotFoundError(f"RCN Profile not found at: {src}")

    rcnData = loadyaml(src)
    dirName = os.path.join(configDir, rcnData['profile'])

    if not os.path.exists(dirName):
        os.makedirs(dirName)

    token = input("RCN Unique Token: ")
    videoServer = input("Video Server Host (192.168.66.5): ")
    if videoServer.strip() == "":
        videoServer = "192.168.66.5"

    httpClient = RCNHttpClient(server=rcnData['server'])
    httpClient.setToken(rcnData['token'])

    connectionList = httpClient.getConnections()
    connection, connectionIndex = pick(title="Select Connection", options = list(map(lambda x: x['id'], connectionList)))
    _ = list(map(lambda x: connectionList[0][x], ['deviceFrom', 'deviceTo']))
    devices = []
    deviceMap = {}

    for device in _:
        if isinstance(device, list):
            devices.append(device[0]['deviceId'])
            deviceMap[device[0]['deviceId']] = device[0]['id']
        elif isinstance(device, dict):
            devices.append(device['deviceId'])
            deviceMap[device['deviceId']] = device['id']

    device, deviceIndex = pick(title="Select Device", options = devices)

    connectionId = connectionList[connectionIndex]['id']
    deviceId = deviceMap[device]

    data = httpClient.getConfigJson(connectionId, deviceId)
    clientJson = os.path.join(dirName, f"{connectionId}-{deviceId}.json")
    with open(clientJson, "w") as file:
        file.write(data)

    rcnConfig = RCNConfig()
    rcnConfig.clientJson.append(clientJson)
    rcnConfig.token = token
    rcnConfig.streamer = {
        "serverPath": f"https://{videoServer}/#/stream?host={videoServer}",
        "video": True,
        "audio": True
    }
    rcnConfig.credentials = {
        "username": "admin",
        "password": "admin"
    }

    rcnConfig.dumpasfile(profile=rcnData['profile'])