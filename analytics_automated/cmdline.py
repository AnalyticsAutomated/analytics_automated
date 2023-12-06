from os import listdir
from os.path import isfile, join, isdir


def return_local_commands():
    cmd_paths = ['/bin', '/usr/bin', '/sbin', '/usr/sbin', '/usr/local/bin',
                 '/usr/local/sbin', '/opt']

    unix_commands = []
    for path in cmd_paths:
        if isdir(path):
            try:
                unix_commands = unix_commands + [f for f in listdir(path)
                                                 if isfile(join(path, f))]
            except Exception as e:
                print("command dir error "+str(e))
                raise str(e)

    return (unix_commands)
