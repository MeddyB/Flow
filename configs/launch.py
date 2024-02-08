import os
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT = "dev"

def main():
    os.environ["FLOW_CONFIG_LOCATION"] = DIR
    
    if "FLOW_DEV_LOCATION" not in os.environ:
        os.environ["FLOW_DEV_LOCATION"] = os.path.dirname(DIR)
    os.environ["FLOW_CORE_VENV_LOCATION"] = os.path.join(os.environ["FLOW_CONFIG_LOCATION"], "venvs", "desktop")
    
    PROJECTS_DIR = os.path.join(os.environ["FLOW_DEV_LOCATION"], "projects")
    os.environ["FLOW_PROJECTS_DIR"] = PROJECTS_DIR
    
    # Set Flow.exe in Environment PATH
    os.environ["PATH"] = os.path.join(os.environ["FLOW_CORE_VENV_LOCATION"], "Scripts") + os.path.pathsep + os.environ["PATH"]
    
    os.environ["PLUGIN_FOLDER"] = os.path.join(os.environ["FLOW_DEV_LOCATION"], "core", "core", "jeanpaulstartplugins")
    os.environ["FLOW_CURRENT_PROJECT"] = os.path.join(os.environ["FLOW_PROJECTS_DIR"], PROJECT)
    os.chdir(os.environ["FLOW_CURRENT_PROJECT"])
    
    # for element in os.environ:
    #     print(element, os.environ[element])
    
    p = subprocess.Popen(["flow"])
    return p.wait()
 
sys.exit(main())