import argparse
import os

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
        print("Lauch Flow {}".format())
        
    if args.action == "context":
        if args.context_action == "create":
            print("Creating context {}".format())
        elif args.context_action == "list":
            print("Context list :")
        elif args.context_action == "get":
            print("Context get :")
                    
    elif args.action == "software": 
        if args.software_action == "list":
            print("Softwares list :")
        elif args.software_action == "launch":
            print("Exit code is '{}'".format())
               
    elif args.action == "action":
        print("Engine list actions:")

         
if __name__ == "__main__":
    main()
