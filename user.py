import os
import re

from sysadmin.myshell import run
from myaq.host import Host, HostList

# ============================================================================== 
#   NOTE: in development. Not tested
# ============================================================================== 
class User(object):
    def __init__(self, name=None):
        if not self.name:
            self.name = os.getlogin()
        else:
            self.name = name

    def __str__(self):
        return self.name

    @property
    def hosts(self):
        """
        list of Hosts this User currently has in Sandboxes
        """
        cmd = '/opt/aquilon/bin/aq.py search_host --sandbox_author %s' %self.name
        results = run(cmd)
        host_l = HostList()
        for name in results.out.split():
            host = Host(name)
            host_l.append(host)
        return host_l


