import os
from ..config import Config

# import copy
# from threading import Thread

# DEFAULT_RESOLVE_ENV_KEYS = [
#     "FLOW_PROJECTS_DIR",
#     "FLOW_CONFIG_LOCATION",
#     "FLOW_CURRENT_PROJECT",
#     "FLOW_DEV_LOCATION",
#     "CGRU_LOCATION",
#     "MAYA_COMPONENT_NODES_LOCATION",
# ]

# def software_launch_in_thread(name, **kwarg):
#     """
#     Run a software in a separate thread for non blocking operations.
    
#     Args:
#         name (str): name of the launcher.
#         kwargs (dict): keywords arguments to pass to software_launch
    
#     Returns:
#         Thread: The thread running the process
#     """
#     results = []
#     def worker(*args, **kwargs):
#         exit_code = software_launch(*args, **kwargs)
#         results.append(exit_code)
#     t = Thread(
#         target=worker,
#         args=(name,),
#         kwargs=kwargs
#     )
#     t.results = results
#     t.daemon = True
#     t.start()
#     return t

# def get_software_batch(name):
#     """
#     Get Jean Paul Start Batch from software launcher name.
    
#     Args:
#         name (str): name of the launcher.
    
#     Returns:
#         jeanpaulstart.batch.Batch: Jean Paul Start Batch instance
#     """
#     import jeanpaulstart.batch
#     config = Config.get_instance()
#     path = os.path.join(config.path, "softwares", name + ".yml")
#     return jeanpaulstart.batch.Batch(filepath=path)

# def get_software_command(name):
#     """
#     Get command from software launcher name.
#     Only the last raw command is returned.
    
#     Args:
#         name (str): name of the launcher.
    
#     Returns:
#         str: Launcher command
#     """
#     batch = get_software_batch(name)
#     command = None
#     for task in batch.tasks:
#         if task.command_name == "raw":
#             command = task.arguments["command"]
#     return command

# def recursive_expandvars(value):
#     while "$" in value or "%" in value:
#         prev = value
#         value = os.path.expandvars(value)
#         if value == prev:
#             break
#     return value

# def get_software_environment(name, inherit=False, resolve=False, source_env=None):
#     """
#     Get Environment Variables from software launcher name.
    
#     Args:
#         name (str): name of the launcher.
#         inherit (bool): Inherit current process environment variables.
#         resolve (bool): Resolve environment variables using recursive_expandvars
#         source_env (dict): Alternate environment variables for resolution.
    
#     Returns:
#         dict: Environment Variables Key/Value
#     """
#     batch = get_software_batch(name)
#     environ_backup = copy.deepcopy(dict(**os.environ))
#     try:
#         if not inherit:
#             os.environ.clear()
#         if source_env:
#             os.environ.clear()
#             os.environ.update(source_env)
#         for key in DEFAULT_RESOLVE_ENV_KEYS:
#             if key not in environ_backup:
#                 continue
#             os.environ[key] = environ_backup[key]
#         for task in batch.tasks:
#             if task.command_name == "environment":
#                 value = task.arguments["value"]
#                 if isinstance(value, list):
#                     value = os.pathsep.join(value)
#                 os.environ[task.arguments["name"]] = str(value)
#         if resolve:
#             for key, value in os.environ.items():
#                 os.environ[key] = recursive_expandvars(value)
#         env = dict(**os.environ)
#     finally:
#         os.environ.clear()
#         os.environ.update(environ_backup)
#     return env

def run_batch(batch):
    """
    Run a JeanPaulStart Batch using our custom FLOWExecutor.
    
    Args:
        batch (jeanpaulstart.batch.Batch): Jean Paul Start Batch instance.
        startup_script (str): set the FLOW_STARTUP_SCRIPT to execute a script on engine startup.
    
    Returns:
        int: Exit code
    """
    import jeanpaulstart
    from .executor import FlowExecutor
    jeanpaulstart.load_plugins()
    if not isinstance(batch, jeanpaulstart.Batch):
        batch = jeanpaulstart.Batch(filepath=batch)
    if batch.load_status != jeanpaulstart.OK:
        return batch.load_status
    
    executor = FlowExecutor(batch)
    registered_status, messages, executor_status = executor.run_all()
    if executor.success:
        return registered_status

    return executor_status

def software_launch(name, startup_file=None, startup_script=None):
    """
    Launch a software using Jean Paul Start.
    
    Args:
        name (str): name of the launcher.
        startup_file (str): set the FLOW_STARTUP_FILE to open a file on engine startup.
        startup_script (str): set the FLOW_STARTUP_SCRIPT to execute a script on engine startup.
    
    Returns:
        int: Exit code
    """
    import jeanpaulstart
    config = Config.get_instance()
    os.environ["FLOW_CURRENT_CONTEXT"] = os.getcwd().replace("\\", "/")
    software_config = os.path.join(config.path, "softwares", "{name}.yml".format(**locals()))
    if startup_file:
        os.environ["FLOW_STARTUP_SCENE"] = startup_file
    if startup_script:
        os.environ["FLOW_STARTUP_SCRIPT"] = startup_script
    
    status = run_batch(software_config)
    
    if status == jeanpaulstart.BATCH_NO_DATA:
        exit_code = 2  # No such file or directory
    elif status in (jeanpaulstart.BATCH_NOT_NORMALIZED, jeanpaulstart.BATCH_NOT_VALID):
        exit_code = 3
    elif status in (jeanpaulstart.OK, jeanpaulstart.TASK_ERROR_IGNORED):
        exit_code = 0  # Success
    else:
        exit_code = status
    os.environ.pop("FLOW_STARTUP_SCENE", None)
    os.environ.pop("FLOW_STARTUP_SCRIPT", None)
    return exit_code

def list_softwares():
    """
    List available softwares launchers
    
    Returns:
        list: List of available softwares names.
    """
    softwares = []
    config = Config.get_instance()
    for p in os.listdir(os.path.join(config.path, "softwares")):
        name, ext = os.path.splitext(p)
        if ext != ".yml":
            continue
        softwares.append(name)
    return softwares