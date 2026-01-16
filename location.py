import os
import time

from sysadmin.bcolors import bcolors
from sysadmin.myshell import run, call

from myaq.myaqexceptions import NoSandboxException, SandboxNameTooLong


class Location(object):
    def __init__(self, name, category=None):
        """
        :category: domain | sandbox
        However, there are cases where we just need a "container" for the 
        attribute 'name', but we don't care if it is a Domain
        or a Sandbox. Example, the 'start' value for the command to create
        a Sandbox.  That's why we allow it to be "None".
        """
        self.name = name
        self.category = category

    def __repr__(self):
        return self.name


class Domain(Location):
    def __init__(self, name):
        super(Domain, self).__init__(name, "Domain")

    @property
    def hosts(self):
        from myaq.host import Host, HostList
        cmd = 'aq search_host --noauth --domain %s' %self.name
        results = run(cmd)
        name_l= results.out
        host_l = HostList()
        for name in name_l.split('\n'):
            host_l.append(Host(name))
        return host_l

    def manage(self, host_l):
        """
        manage a list of hosts into this sandbox
        """
        results_l = []
        for host in host_l:
            out = self._manage_host(host)
            results_l.append(out)
        return results_l

    def _manage_host(self, host):
        """
        manage a single Host into this domain 
        """
        if host.cluster:
            self._manage_cluster(host.cluster)
        else:
            cmd = 'aq manage --hostname %s --domain %s' %(host.name, self.name)
            results = run(cmd)
            if results.rc != 0:
               cmd += ' --force'
               results = run(cmd)
            return results

    def _manage_cluster(self, cluster):
        """
        manage all Host in a Cluster to this Domain
        """
        cmd = 'aq manage --cluster  %s --domain %s --force' %(cluster.name, self.name)
        results = run(cmd)
        if results.rc != 0:
            cmd += ' --force'
            results = run(cmd)
        return results


class DomainList(list):

    def set(self, name_l):
        for name in name_l:
            self.append(Domain(name))


# ============================================================================== 
# NOTE: under development / to be tested
# ============================================================================== 
class SandboxHandler(object):
    def create(self, name, start=None):
        """
        Tries to create a Sandbox, if it doesn't exist already
        :param start Sandbox: a Sandbox to create this one from. 
        """
        cmd = 'aq add_sandbox --sandbox %s' %name
        if start:
            cmd += '  --start %s' %start.name
        results = run(cmd)
        #return results
        if results.rc == 0:
            sandbox = Sandbox(name)
            return sandbox
        else:
            return None


class Sandbox(Location):

    def __init__(self, name=None):
        # let's check first the length of the name
        if name and len(name.split('/')[-1]) > 32:
            raise SandboxNameTooLong(name)
        # if everything is fine....
        self.user = os.getlogin() # default
        if not name:
            name = self.get()
        if '/' in name:
            self.user = name.split('/')[0]
            self.name = name
        else:
            self.name = '%s/%s' %(self.user, name)
        self.info = None
        super(Sandbox, self).__init__(self.name, "Sandbox")

    def __str__(self):
        """
        Human friendly representation of this Sandbox
        """
        out = ""
        out += '\n' + bcolors.WARNING + 'name:   ' + bcolors.ENDC + self.name
        out += '\n' + bcolors.WARNING + 'owner:  ' + bcolors.ENDC + self.owner
        out += '\n' + bcolors.WARNING + 'path:   ' + bcolors.ENDC + self.path
        return out

    # FIXME: most probably this should be called by __init__
    def _show_sandbox(self):
        cmd = "/opt/aquilon/bin/aq.py show_sandbox --sandbox %s" %self.name
        results = run(cmd)
        self.info = results.out
        return self.info

    @property
    def shortname(self):
        return self.name.split('/')[1]

    @property
    def owner(self):
        if not self.info:
            self._show_sandbox()
        for line in self.info.split('\n'):
            if 'Owner:' in line:
                owner = line.split(':')[1].strip().split('@')[0]
                return owner

    @property
    def path(self):
        if not self.info:
            self._show_sandbox()
        for line in self.info.split('\n'):
            if 'Path:' in line:
                path = line.split(':')[1].strip()
                return path

    @property
    def exists(self):
        if self.path:
            # FIXME?
            # probably is not needed to check if isdir(), 
            # just the fact that is exists may be enough.
            return os.path.isdir(self.path)
        else:
            return False

    @property
    def page(self):
        return 'http://aquilon.gridpp.rl.ac.uk/sandboxes/diff.php?sandbox=%s' %self.shortname

    def get(self):
        """
        get the name of the sandbox the process it is
        unless it is already set
        """
        cmd = 'git rev-parse --abbrev-ref HEAD'
        results = run(cmd)
        if results.rc:
            raise NoSandboxException
        else:
            return results.out

    @property
    def hosts(self):
        from myaq.host import Host, HostList
        host_l = HostList()
        cmd = 'aq search_host --noauth --sandbox %s' %self.name
        results = run(cmd)
        if results.rc == 0:
            name_l= results.out
            for name in name_l.split('\n'):
                if name != "":
                    host_l.append(Host(name))
            return host_l
        else:
            # returns an empty list 
            return host_l

    def create(self, start=None):
        """
        Tries to create a Sandbox, if it doesn't exist already
        :param start Sandbox: a Sandbox to create this one from. 
        """
        cmd = 'aq add_sandbox --sandbox %s' %self.name
        if start:
            cmd += '  --start %s' %start.name
        results = run(cmd)
        return results

    def rebase(self):
        # FIXME
        # check for Exceptions, and return the entire out's, err's, and rc's.
        os.chdir(self.path)
        results = run('git fetch && git rebase origin/prod')
        return results

    def force_rebase(self):
        # FIXME
        # check for Exceptions, and return the entire out's, err's, and rc's.
        pop = True
        results = run('git stash')
        if results.rc != 0:
            pop = False
        results = self.rebase()
        if results.rc != 0:
            return results
        if pop:
            results = run('git stash pop')
            return results

    def publish(self):
        cmd = 'cd %s; aq publish --sandbox %s --rebase' %(self.path, self.shortname)
        results = run(cmd)
        return results

    def deploy(self):
        cmd = 'aq deploy --source %s --target prod' %(self.shortname)
        results = run(cmd)
        return results

    def delete(self):
        """
        delete this Sandbox
        """
        cmd = 'aq del_sandbox --sandbox %s' %self.name
        results = run(cmd)
        return results

    def remove(self):
        ###cmd = 'rm -rf /var/quattor/templates/%s/%s' %(self.user, self.shortname)
        # instead of deleting the directory, let's move it to a backup location, just in case
        cmd = 'mv /var/quattor/templates/%s/%s /var/quattor/templates/%s/backup_sandboxes/%s-%s' %(self.user, self.shortname, self.user, int(time.time()), self.shortname)
        results = run(cmd)
        return results

    def restore_hosts(self, domain_name='prod'):
        """
        manage all hosts back to a given Domain
        """
        host_l = self.hosts
        domain = Domain(domain_name)
        domain.manage_list(host_l)

    def manage(self, host_l):
        """
        manage a list of hosts into this sandbox
        """
        results_l = []
        for host in host_l:
            out = self._manage_host(host)
            results_l.append(out)
        return results_l

    def _manage_host(self, host):
        """
        manage a single Host into this sandbox
        """
        if host.cluster:
            results = self._manage_cluster(host.cluster)
        else:
            cmd = 'aq manage --hostname %s --sandbox %s --force' %(host.name, self.name)
            results = run(cmd)
        return results

    def _manage_cluster(self, cluster):
        """
        manage all Hosts in a Cluster into this Sandbox
        """
        cmd = 'aq manage --cluster  %s --sandbox %s --force' %(cluster.name, self.name)
        results = run(cmd)
        return results

    def diff(self):
        """
        print the diff between current Sandbox and master branch
        """
        MASTER="/var/quattor/domains/prod/"
        cmd = 'diff -r --exclude=\.git %s %s' %(self.path, MASTER)
        results = run(cmd)
        return results



class SandboxList(list):

    @property
    def hosts(self):
        from myaq.host import HostList
        host_l = HostList()
        for sandbox in self.__iter__():
            host_l += sandbox.hosts
        return host_l

    def set(self, name_l):
        for name in name_l:
            self.append(Sandbox(name))

    def rebase(self):
        results_l = []
        for sandbox in self.__iter__():
            results = sandbox.rebase()
            results_l.append(results)
        return results_l

    def force_rebase(self):
        results_l = []
        for sandbox in self.__iter__():
            results = sandbox.force_rebase()
            results_l.append(results)
        return results_l


