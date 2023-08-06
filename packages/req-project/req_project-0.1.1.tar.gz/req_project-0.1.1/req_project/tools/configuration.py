from importlib.resources import path
import os
from pathlib import Path

from black import json
import git
import json

class Configuration:
    # init method or constructor   
    def __init__(self, projectname=None, workspace=None):  
        if projectname==None:
            self.projectname = "draft_project"
        else:
            self.projectname = projectname

        if workspace==None:
            self.workspace = "."
        else:   
            self.workspace = workspace

        self.config = "/config"
        self.config_file = "/config.json"
        self.capella = "/capella"
        self.sdoc = "/sdoc"
        self.src = "/src"
        self.docu = "/docu"

    def change_projectname(self, projectname):
        self.projectname = projectname

    def change_projectpath(self, workspace):
        self.workspace = workspace

    def checkfor_configfile(self):
        try:
            with open("config.json", "r") as jsonfile:
                data = json.load(jsonfile)
                print(data)
            return True
        except FileNotFoundError:
            print('Configuration file is not present.')
            return False

    def write_configfile(self):
        myJSON = json.dumps(self.__dict__)
        filename = self.workspace + "/" + self.projectname + self.config + self.config_file
        print(filename)
        with open(filename, "w") as jsonfile:
            jsonfile.write(myJSON)
            print("Write successful")