import argparse
import os
import getpass

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")
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
    
    action_parser = subparsers.add_parser("action", help="Engine actions")
    action_subparsers = action_parser.add_subparsers(dest="action_action")
    #--------------------------------------------------------------------#
    action_list = action_subparsers.add_parser("list")
    #--------------------------------------------------------------------#
    action_exec = action_subparsers.add_parser("exec")
    action_exec.add_argument("name")
    
    args = parser.parse_args()
    if args.action is None:
        #Launch Application 'Flow' by default
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
        
    if args.action == "context":
        if args.context_action == "create":
            print("Creating context {}".format())
        elif args.context_action == "list":
            print("Context list :")
        elif args.context_action == "get":
            print("Context get metadatas:")
                    
    elif args.action == "software": 
        if args.software_action == "list":
            print("Softwares list :")
        elif args.software_action == "launch":
            print("Exit code is '{}'".format())
               
    elif args.action == "action":
        print("Engine list actions:")

         
if __name__ == "__main__":
    main()
