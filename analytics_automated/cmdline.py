from os import listdir
from os.path import isfile, join


def return_local_commands():
    cmd_paths = ['/bin', '/usr/bin', '/sbin', '/usr/sbin', '/usr/local/bin',
                 '/usr/local/sbin', '/opt']

    unix_commands = []
    for path in cmd_paths:
        unix_commands = unix_commands + [f for f in listdir(path)
                                         if isfile(join(path, f))]
    return(unix_commands)
