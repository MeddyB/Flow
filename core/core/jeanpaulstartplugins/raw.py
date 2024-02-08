import jeanpaulstart.tasks.raw
from jeanpaulstart.tasks.raw import *

def validate(user_data):
    return jeanpaulstart.tasks.raw.validate(user_data)

def normalize_after_split(splitted):
    normalized = dict(splitted)
    normalized['arguments']['async_'] = splitted['arguments'].get('async', True)
    normalized['arguments']['open_terminal'] = splitted['arguments'].get('open_terminal', False)
    normalized['arguments']['capture_output'] = splitted['arguments'].get('capture_output', False)
    return normalized

def apply_(async_, command, open_terminal, capture_output):
    import shlex
    from subprocess import Popen, call, PIPE, STDOUT
    from jeanpaulstart.constants import OK
    import sys
    # if no_shell:
    #     p = Popen(shlex.split(command), shell=True, stdout=PIPE, stderr=STDOUT)
    #     output = ""
    #     while p.poll() is None:
    #         output += p.stdout.read(1024)
    #         parts = output.split("\n")
    #         for line in parts[:-1]:
    #             print("  > {}".format(line))
    #             sys.stdout.flush()
    #         output = parts[-1]
    #     exit_code = p.returncode
    #     output += p.stdout.read()
    #     for line in output.split("\n"):
    #         print("  > {}".format(line))
    #         sys.stdout.flush()
    #     return exit_code
    
    if open_terminal:
        args = shlex.split(command)
        executable = args[0]
        args = args[1:]
        command = ["powershell", "-Command", "start powershell"]
        command[-1] += "  -ArgumentList \"-Command &'{}' {}\"".format(executable, " ".join(args))
    # else:
    #     cmd = ["powershell", "-windowstyle", "hidden", "-Command", "&\"{}\"".format(executable)]
    #     if len(args):
    #         cmd += args
    if async_:
        Popen(command, shell=False, close_fds=True)
        return OK
    else:
        if not capture_output:
            exit_code = call(command, shell=True)
        else:
            # Run process
            if sys.version_info[0] == 2:
                p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
            elif sys.version_info[0] == 3:
                p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT, encoding='utf-8', errors='ignore')
            
            # Read Output
            output = ""
            while p.poll() is None:
                if sys.version_info[0] == 2:
                    output += p.stdout.read(1024)
                elif sys.version_info[0] == 3:
                    output += p.stdout.readline()
                parts = output.split("\n")
                for line in parts[:-1]:
                    if line.endswith("\r"):
                        line = line[:-1]
                    print("  > {}".format(line))
                    sys.stdout.flush()
                output = parts[-1]
            exit_code = p.returncode

            if sys.version_info[0] == 2:
                output += p.stdout.read()
            elif sys.version_info[0] == 3:
                output += p.stdout.readline()
            for line in output.split("\n"):
                if line.endswith("\r"):
                    line = line[:-1]
                print("  > {}".format(line))
                sys.stdout.flush()
            print("  >>> Finished with exit code {}".format(exit_code))
        if not exit_code:
            return OK
        return exit_code
