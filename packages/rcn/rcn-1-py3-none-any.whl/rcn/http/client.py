import requests
import os
from pathlib import Path
import base64
import logging

from rcn.utils import loadyaml, configDir


# def saveToken(token, configDir=configDir):
#     path = os.path.join(configDir, "token")
#     if not os.path.exists(configDir):
#         os.makedirs(configDir)
#
#     with open(path, "w") as file:
#         file.write(base64.b64encode(token.encode()).decode())
#
# def loadToken(configDir=configDir):
#     path = os.path.join(configDir, "token")
#     with open(path, "r") as file:
#         token = base64.b64decode(file.read(), validate=True)
#     return token

class RCNHttpClient:
    def __init__(self, **kwargs):
        self.config = {
            "server": "http://localhost:8080/backend",
            **kwargs
        }
        if os.path.exists(os.path.join(configDir, "default.yml")):
            self.loadToken()

    def loadToken(self, profile='default'):
        rcnConfig = loadyaml(os.path.join(configDir, f"{profile}.yml"))
        self.setToken(rcnConfig['token'])

    def setToken(self, token):
        self.__token = token

    def login(self, credentials):
        response = requests.post(f"{self.config['server']}/login", json={
            "username": credentials['username'],
            "password": credentials['password']
        })
        responseData = response.json()
        if response.status_code == 200 and "jwt" in responseData:
            self.setToken(responseData['jwt'])

        return response

    def getDevices(self):
        response = requests.get(f"{self.config['server']}/auth/device/list", headers={
            "Authorization": f"Bearer {self.__token}"
        })

        return response.json()

    def getSingleDevice(self, id):
        response = requests.get(f"{self.config['server']}/auth/device/?id={id}", headers={
            "Authorization": f"Bearer {self.__token}"
        })
        return response.json()

    def getConfigJson(self, connectionId, deviceId):
        response = requests.get(f"{self.config['server']}/connections/getConfiguration?id={connectionId}&deviceId={deviceId}", headers={
            "Authorization": f"Bearer {self.__token}"
        })
        return response.text


    def getSupportedDevices(self):
        response = requests.get(f"{self.config['server']}/public/api/supported")
        return response.json()


    def getConnections(self):
        response = requests.get(f"{self.config['server']}/connections/list", headers={
            "Authorization": f"Bearer {self.__token}"
        })

        return response.json()