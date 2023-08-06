from pathlib import Path

import ruamel.yaml
from yaml import load, SafeLoader, dump, SafeDumper
import os


configDir = f"{Path.home()}/.rcn/"
if not os.path.exists(configDir):
    os.makedirs(configDir)

yaml = ruamel.yaml.YAML()


class RCNFilters(object):
    def __init__(self, name = None, configuration = None):
        self.name = name
        self.configuration = configuration


class RCNConfig(object):
    def __init__(self):
        self.credentials = None
        self.clientJson = []
        self.token = None
        self.filters = [RCNFilters(name="ior_research.utils.filterchains.RControlNetMessageFilter")]
        self.streamer = None

    def dumpasfile(self, profile, filename="default"):
        if not os.path.exists(os.path.join(configDir, profile)):
            os.makedirs(os.path.join(configDir, profile))

        filePath = os.path.join(configDir, profile, f"{filename}.yml")
        with open(filePath, "w") as stream:
            yaml.dump(self, stream)

yaml.register_class(RCNFilters)
yaml.register_class(RCNConfig)

def loadYamlAsClass(filePath):
    with open(filePath, "r") as stream:
        return yaml.load(stream)

def loadyaml(filePath):
    with open(filePath, "r") as stream:
        return load(stream, Loader=SafeLoader)
