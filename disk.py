import os
import re
import time

from sysadmin.myshell import run


class Disk(object):
    def __init__(self, name):
        self.name = name

    def remove(self, machine):
        cmd = 'aq del_disk --disk %s --machine %s' %(self.name, machine.name)
        results = run(cmd)
        return results

