import os
import subprocess
import sys
import logging


DIR = os.path.dirname(os.path.abspath(__file__))

PYTHON27 = "C:/Python27/python.exe"
PYTHON37 = "C:/Program Files/Python37/python.exe"

# create logger
logger = logging.getLogger('Installation virtual environment and dependencies')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


def test_module(module, python="python"):
    process = subprocess.Popen([python, "-c", f"import {module}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    logger.info("Checking module '{}'".format(module))
    if process.wait():
        sys.stderr.write(p.stdout.read().decode("utf-8"))
        logger.warning("Need to install module '{}'".format(module))
        raise Exception(f"Missing module {module} with python {repr(python)}")
    
def check_requirements():
    if not "DEV_LOCATION" in os.environ:
        logger.warning("Need to create environment variable DEV_LOCATION")
        raise Exception("Missing environment variable DEV_LOCATION.")
    if not os.path.exists(PYTHON27):
        logger.warning("Need to install PYTHON27")
        raise Exception(f"Missing required python installation {PYTHON27}")
    test_module("poetry")
    test_module("poetry2setup")
    test_module("venv")
    test_module("virtualenv", python=PYTHON27)

def create_virtualenv(dest, python="python.exe", venv="venv"):
    cmd = [
        python, "-m",
        venv,
    ]
    cmd.append(dest)
    subprocess.check_call(cmd)

def install_requirements(prefix, requirements):
    pip = os.path.join(prefix, "Scripts", "pip.exe")
    subprocess.check_call([pip, "install", "-r", requirements])
   
def main():
    os.environ["CONFIG_LOCATION"] = DIR
    if "DEV_LOCATION" not in os.environ:
        os.environ["DEV_LOCATION"] = os.path.dirname(os.path.dirname(DIR))
    check_requirements()
    
    # Replace "\"" by "/" as pip requirement doesn't support "\"
    os.environ["DEV_LOCATION"] = os.environ["DEV_LOCATION"].replace("\\", "/")
    
    # CREATE VIRTUAL ENVIRONMENTS
    venvs_directory = os.path.join(DIR, "venvs")
    desktop_venv = os.path.join(venvs_directory, "desktop")
    maya2020_venv = os.path.join(venvs_directory, "maya2020")
    
    if not os.path.exists(desktop_venv):
        create_virtualenv(desktop_venv, python=PYTHON37)     
    
    if not os.path.exists(maya2020_venv):
        create_virtualenv(maya2020_venv, python=PYTHON27, venv="virtualenv")
    
    # INSTALL DEPENDENCIES
    desktop_requirements = os.path.join(DIR, "requirements", "desktop.requirements.dev.txt")
    install_requirements(desktop_venv, desktop_requirements)
    
if __name__ == "__main__":
    main()
