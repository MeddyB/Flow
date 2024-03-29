import argparse
import os
import getpass
import json
import sys

from core.logging.logger import init_logging, logging
init_logging()
log = logging.getLogger(__name__)

def start_ui():
    from Qt5 import QtWidgets, QtCore, QtGui
    from jeanpaulstartui.launcher import Launcher
    
    print("Launch Flow UI Application")
    
    app = QtWidgets.QApplication([])
    batches = [os.path.join(os.environ["FLOW_CONFIG_LOCATION"], "softwares")]
    if os.environ.get("FLOW_TAG_LOCATION") is not None:
        tags = os.path.join(os.environ["FLOW_TAG_LOCATION"], "tags.yml")
    else:
        tags = os.path.join(os.environ["FLOW_CONFIG_LOCATION"], "tags/tags.yml")

    launcher = Launcher()
    launcher.batch_directories = batches
    launcher.tags_filepath = tags
    launcher.username = getpass.getuser()
    launcher.version = "0.01.00"
    launcher.update()
    launcher._view.setWindowFlags(
        # QtCore.Qt.CustomizeWindowHint |
        QtCore.Qt.Dialog |
        QtCore.Qt.WindowCloseButtonHint |
        QtCore.Qt.WindowMinimizeButtonHint |
        QtCore.Qt.WindowSystemMenuHint
    )
    launcher._view.setWindowTitle("Flow Pipeline - Hello Flow Dream !")
    # launcher._view.window_icon = QtGui.QIcon(FLOW_ICON)
    launcher._view.setWindowIcon(launcher._view.window_icon)
    launcher._view.tray.setIcon(launcher._view.window_icon)
    launcher.show()
    app.exec_()
    

def main():
    log.setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")
    #--------------------------------------------------------------------#
    context_parser = subparsers.add_parser("context")
    context_subparsers = context_parser.add_subparsers(dest="context_action")
    context_create_parser = context_subparsers.add_parser("create")
    context_create_parser.add_argument("entity_type", help="Entity Type to create")
    context_create_parser.add_argument("entity_name", help="Entity Name to create")
    context_create_parser.add_argument("path")
    context_create_parser.add_argument("--property", "-p", nargs=2, action="append", help="Entity Properties")
    context_list_parser = context_subparsers.add_parser("list")
    context_list_parser.add_argument("path", nargs="?", default=os.getcwd())
    context_get_parser = context_subparsers.add_parser("get")
    context_get_parser.add_argument("path")
    #--------------------------------------------------------------------#
    software_parser = subparsers.add_parser("software")
    software_subparsers = software_parser.add_subparsers(dest="software_action")
    software_list_parser = software_subparsers.add_parser("list")
    software_launch_parser = software_subparsers.add_parser("launch")
    software_launch_parser.add_argument("name", help="Software name to launch")
    software_launch_parser.add_argument("--startup-file", "-f", help="Startup Scene")
    software_launch_parser.add_argument("--startup-script", "-s", help="Startup Script")
    #--------------------------------------------------------------------#
    action_parser = subparsers.add_parser("action", help="Engine actions")
    action_subparsers = action_parser.add_subparsers(dest="action_action")
    action_list = action_subparsers.add_parser("list")
    action_exec = action_subparsers.add_parser("exec")
    action_exec.add_argument("name")
    #--------------------------------------------------------------------#
    args = parser.parse_args()
    from core.config import Config
    config = Config.get_instance()
    
    # from pprint import pprint
    # for entity in config._entities:
    #     print('*'*50)
    #     print('entity -->')
    #     pprint(entity)
    #     print('tasks -->')
    #     pprint(config._entities[entity].tasks)
    #     print('root_template -->')
    #     pprint(config._entities[entity].root_template)
    #     print('entity_type -->')
    #     pprint(config._entities[entity].entity_type)
    #     print('*'*50)
    
    if args.action is None:
        logging.info("- Launch Application 'Flow' by default -")
        start_ui()
        
    elif args.action == "context":
        
        if args.context_action == "create":
            properties = dict(args.property or [])
            context = config.create_context(args.entity_type, args.entity_name, args.path, properties=properties)
            logging.info("Creating context {}".format(context))
        elif args.context_action == "create_step":
            context = config.get_context(args.path)
            context.create_step(args.name)
            logging.info("Context list :")
        elif args.context_action == "list":
            contexts = config.list_contexts(args.path, recursive=True)
            logging.info("Context list :")
            for context in contexts:
                logging.info(context)                            
        elif args.context_action == "get":
            from .context import Context
            logging.info("Get Fields from path :")
            context = Context(config, args.path)
            print(json.dumps(context.fields, indent=2, sort_keys=True))
                        
    elif args.action == "software":
       
        if args.software_action == "list":
            from .softwares import list_softwares
            logging.info("Softwares list :")
            for software in list_softwares(): 
                logging.info(software)
        elif args.software_action == "launch":
            from .softwares import software_launch
            exit_code = software_launch(args.name, startup_file=args.startup_file, startup_script=args.startup_script)
            logging.info("Exit code is '{}'".format(exit_code))
            sys.exit(exit_code)

    elif args.action == "action":
        
        from .engine import load_engine
        engine = load_engine()
        print(engine)
    
if __name__ == "__main__":
    main()
