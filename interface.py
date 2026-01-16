from sysadmin.bcolors import bcolors
from sysadmin.myshell import run


class Interface(object):
    def __init__(self, name, addr, ip, network_environment=None):
        self.name = name
        self.addr = addr
        self.ip = ip 
        self.network_environment = network_environment

    def __str__(self):
        out =         bcolors.WARNING + 'name:            ' + bcolors.ENDC + self.name
        out += '\n' + bcolors.WARNING + 'addr:            ' + bcolors.ENDC + self.addr
        out += '\n' + bcolors.WARNING + 'ip:              ' + bcolors.ENDC + self.ip
        out += '\n' + bcolors.WARNING + 'network env:     ' + bcolors.ENDC + self.network_environment
        out += '\n'
        return out

