import os
import re
import time

from sysadmin.myshell import run


class Machine(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    @property
    def sid(self):
        # System ID
        # it is the N digits at the end of the machine name
        m = re.match('system(?P<sid>([0-9]*))$', self.name, re.I)
        return m.groupdict()['sid']

    @property
    def host(self):
        """
        returns the Host associated to this Machine
        """
        from myaq.host import Host

        cmd = 'aq search_host --machine %s' %self.name
        results = run(cmd)
        try:
            hostname = results.out
            host = Host(hostname)
            return host
        except:
            return None

    def remove(self):
        """
        remove this Machine
        """
        cmd = 'aq del_machine --machine %s' %self.name
        results = run(cmd)
        return results

    def remove_interface_address(self, interface):
        """
        remove the interface IP address from this machine
        """
        cmd = 'aq del_interface_address --machine %s --interface %s --ip %s' %(self.name, interface.name, interface.ip)
        results = run(cmd)
        return results

    def remove_interface(self, interface):
        """
        remove the interface from this machine
        """
        cmd = 'aq del_interface --machine %s --interface %s' %(self.name, interface.name)
        results = run(cmd)
        return results



class MachineList(list):

    def __str__(self):
        out = ""
        for m in self.__iter__():
            out += str(m)
            out += '\n'
        return out
