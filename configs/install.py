import os
import sys
import subprocess
import logging
import pkg_resources

DIR = os.path.dirname(os.path.abspath(__file__))

PYTHON27 = "C:/Python27/python.exe"
PYTHON37 = "C:/Program Files/Python37/python.exe"

# Function to create a virtual environment
def create_virtualenv(dest, python="python.exe", venv="venv"):
    # Construct the command to create a virtual environment
    cmd = [
        python, "-m",
        venv,
    ]
    cmd.append(dest) 
    # Execute the command to create the virtual environment
    print(cmd)
    subprocess.check_call(cmd)

def create_setup_file(directory_requirements): 
    def display_dependency_paths(requirements_path):
        module_paths = []
        with open(requirements_path, 'r', encoding='utf-16') as file:
            requirements = [line.strip() for line in file if line.strip()]
        for requirement in requirements:
            try:
                if requirement.startswith("-e "):
                    path = requirement[3:].strip()
                    print(f"Editable Path from requirement files: {path}")
                    module_paths.append(path)
                else:
                    distribution = pkg_resources.get_distribution(requirement)
                    print(f"{distribution.project_name} ({distribution.version}): {distribution.location}")
            except pkg_resources.DistributionNotFound as e:
                print(f"Package not found: {e.req}")
        return module_paths
     
    def evaluate_variables_environnement(env_pah_module):
        # Recherche de motifs "${...}" dans le env_pah_module
        bg = 0
        while True:
            prefix_var = env_pah_module.find('${', bg)
            suffix_var = env_pah_module.find('}', prefix_var)
            
            if prefix_var == -1 or suffix_var == -1:
                break
            env_path = env_pah_module[prefix_var + 2:suffix_var]  
            valeur_variable = os.environ.get(env_path) 
            env_pah_module = env_pah_module[:prefix_var] + valeur_variable + env_pah_module[suffix_var + 1:]
            bg = suffix_var + 1

        return env_pah_module

    module_paths = display_dependency_paths(directory_requirements)
    for path_env_module in module_paths: 
        # Évaluer les variables d'environnement dans le env_pah_module
        path_env_module = evaluate_variables_environnement(path_env_module)
        path_module = os.path.join(path_env_module.replace("/", "\\"))
        path_module = path_module.replace("[ui]", "")
        print(f"Module path: {path_module}")
        if not os.path.exists(path_module):
            print(f"The directory {path_module} does not exist.")
            return 
        original_dir = os.getcwd()
        os.chdir(path_module)
        print(f"Current directory: {os.getcwd()}")
        subprocess.run('poetry2setup > setup.py', shell=True, check=True)
        os.chdir(original_dir)

# Function to check if a specific Python module is installed
def check_module(module, python="python"):
    # Use subprocess to run a Python script that imports the specified module
    p = subprocess.Popen([python, "-c", f"import {module}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    logging.info('Checking module: '+ module)
    
    # If the process returns a non-zero exit code, the module is missing
    if p.wait():
        # Print the error message to stderr
        sys.stderr.write(p.stdout.read().decode("utf-8"))
        # Raise an exception indicating the missing module
        raise Exception(f"Missing module {module} with python {repr(python)}")

# Function to check environment requirements
def check_requirements():
    # Check if the required Python 2.7 installation exists
    if not os.path.exists(PYTHON27):
        raise Exception(f"Missing required python installation {PYTHON27}")
    
    # Check for the presence of specific Python modules
    check_module("poetry")
    check_module("poetry2setup")
    check_module("venv")
    check_module("virtualenv", python=PYTHON27)

def install_requirements(prefix_path, requirements):
    # Installs the specified requirements using the given prefix.
    pip = os.path.join(prefix_path, "Scripts", "pip.exe")
    subprocess.check_call([pip, "install", "-r", requirements])
    
def main():
    logging.info('Application is ready to be launched')
    
    os.environ["FLOW_CONFIG_LOCATION"] = DIR
    if "FLOW_DEV_LOCATION" not in os.environ:
        os.environ["FLOW_DEV_LOCATION"] = os.path.dirname(DIR)

    # Configure the logging module
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
     
    check_requirements()
    os.environ["FLOW_DEV_LOCATION"] = os.environ["FLOW_DEV_LOCATION"].replace("\\", "/")
    venvs_directory = os.path.join(DIR, "venvs")
    desktop_venv = os.path.join(venvs_directory, "desktop")
    desktop_requirements = os.path.join(DIR ,"requirements" ,"desktop.requirements.dev.txt")

    if not os.path.exists(desktop_venv):
        create_virtualenv(desktop_venv, python=PYTHON37)
        logging.info('New virtual environnement "DESKTOP" created.')
    
    # Create setup.py file for preparing the installation requirements
    logging.info(f"Requirements Desktop Application: {desktop_requirements}")
    create_setup_file(desktop_requirements)
    install_requirements(desktop_venv, desktop_requirements)
    
if __name__ == "__main__":
    main()