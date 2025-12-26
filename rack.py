from sysadmin.myshell import run

from bcolors import bcolors


class Rack(object):
    def __init__(self, name):
        self.name = name
        self.info = None

    def __str__(self):
        out =  bcolors.WARNING + 'name:            ' + bcolors.ENDC + self.name
        out += '\n' + bcolors.WARNING + 'row:             ' + bcolors.ENDC + self.row
        out += '\n' + bcolors.WARNING + 'column:          ' + bcolors.ENDC + self.column
        out += '\n'
        return out

    @property
    def hosts(self):
        from myaq.host import Host, HostList
        cmd = '/opt/aquilon/bin/aq.py search_host --rack  %s' %self.name
        results = run(cmd)
        host_l = HostList()
        for name in results.out.split():
            host = Host(name)
            host_l.append(host)
        return host_l

    @property
    def row(self):
        if not self.info:
            self._show_rack()
        for line in self.info.split('\n'):
            if 'Row:' in line:
                return line.split()[-1]

    @property
    def column(self):
        if not self.info:
            self._show_rack()
        for line in self.info.split('\n'):
            if 'Column:' in line:
                return line.split()[-1]

    def _show_rack(self):
        cmd = "/opt/aquilon/bin/aq.py show_rack --rack %s" %self.name
        results = run(cmd)
        self.info = results.out
        return self.info


class RackList(list):

    def __str__(self):
        out = ""
        for r in self.__iter__():
            out += str(r)
            out += '\n'
        return out

    def set(self, name_l):
        for name in name_l:
            self.append(Rack(name))

    @property
    def hosts(self):
        from myaq.host import Host, HostList
        host_l = HostList()
        for rack in self.__iter__():
            host_l += rack.hosts
        return host_l
