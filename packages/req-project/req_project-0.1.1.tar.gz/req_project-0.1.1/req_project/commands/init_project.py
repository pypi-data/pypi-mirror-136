import os
import shutil
from pathlib import Path
from black import json
import git
import json
from git import Repo
from markupsafe import string
#internal tools
from tools.configuration import Configuration


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.
    
    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

class InitProject:
    @staticmethod
    def execute(projectname, workspace=None):
        #set configuration path to relativ folder path if not given
        if workspace is None:
            workspace = Path(__file__).parent.parent.parent.parent.absolute()

        path = os.path.join(workspace, projectname)
        #print(path)
        if os.path.exists(path): #project path exists
            #return warning 
            print("Warning: project exists already please delete it before initiate!")
            exit()
        else: #project path does not exist so create prototype project
            print(path)
            try: 
                os.mkdir(path) 
                if os.path.exists(path):
                    #Clone draft project from repro locally
                    git_url = "https://github.com/mnaderhirn/req_draft.git"
                    print("Cloning draft project from GIT URL: " + git_url + " into path " + path)
                    Repo.clone_from(git_url, path)
                    #delete all uncessary information in folder
                    shutil.rmtree(path + "\\.git", onerror=onerror)
                    #Write initial configuration file
                    print(workspace)
                    config = Configuration(projectname, str(workspace))
                    config.write_configfile()
                    print("project folder successful created")
                else:
                    print("something went wrong, project folder not created!")
            except OSError as error: 
                print(error)

        