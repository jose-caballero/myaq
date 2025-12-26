#!/usr/bin/env python

import getpass
import os
import subprocess
import sys


def run(cmd):
    subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = subproc.communicate()
    rc = subproc.returncode
    return out, err, rc 

def remote_run(cmd, host, user='root'):
    cmd = "ssh -oStrictHostKeyChecking=no -oCheckHostIP=no %s@%s '%s'" %(user, host, cmd)
    return run(cmd)


class SandboxCreationFailure(Exception):
    def __init__(self, sandbox_name):
        msg = "Attempt to create Sandbox {sandbox_name} failed."
        self.value = msg.format(sandbox_name=sandbox_name)
    def __str__(self):
        return repr(self.value)


class HostHandlingFailure(Exception):
    def __init__(self, host_name):
        msg = "Attempt to handle Host {host_name} failed."
        self.value = msg.format(host_name=host_name)
    def __str__(self):
        return repr(self.value)


class QuattorFailure(Exception):
    def __init__(self, hostname):
        msg = "Quattor failed on host {hostname}."
        self.value = msg.format(hostname=hostname)
    def __str__(self):
        return repr(self.value)


class GitCommitFailure(Exception):
    def __init__(self, err_msg):
        msg = "Attempt to git commit failed with error message: {error_msg}"
        self.value = msg.format(err_msg=err_msg)
    def __str__(self):
        return repr(self.value)


class Quattor(object):
    # FIXME
    # This implementation is crap !!
    # maybe check_quattor( ) should just be a function, returning a QuattorResults object
    # currently, there is no safe check to prevent calling n_errors, ... before calling check_quattor( )

    def __init__(self, hostname):
        self.hostname = hostname

    def check_quattor(self):

        #
        # NOTE: evaluate this option
        #
        #def check_quattor(self):
        #    cmd = 'pgrep ncm-ncd'

        print("   >>> checking quattor in host %s" %self.hostname)
        cmd = 'tail -1 /var/log/quattor/ncd.log | grep "executing configure$"'
        done = False
        while not done:
            time.sleep(10)
            results = remote_run(cmd, self.hostname)
            done = (  results.rc == 0 )
            if done:
                print("   >>> quattor has finished on host %s" %self.hostname)
            else:
                print("   >>> quattor still working on host %s" %self.hostname)
        print("   >>> check the latest entries in the quattor logs for host %s" %self.hostname)
        cmd = 'tail -5 /var/log/quattor/ncd.log'
        results = remote_run(cmd, self.hostname)
        for line in results.out.split('\n'):
            print("       %s" %line)
            self.last_ncd_log_line = line # because we keep overriding its value,
                                          # at the end of the loop,
                                          # self.last_ncd_log_line will contain
                                          # the very last line in ncd.log

    @property
    def n_errors(self):
        """
        Number of errors in the last line in Quattor ncd.log
        That line looks like this:
            2022/02/16-11:16:46 [OK]   0 errors, 0 warnings executing configure
        """
        n_errors = self.last_ncd_log_line.split()[2]
        return int(n_errors)

    @property
    def n_warnings(self):
        """
        Number of warnings in the last line in Quattor ncd.log
        That line looks like this:
            2022/02/16-11:16:46 [OK]   0 errors, 0 warnings executing configure
        """
        n_warnings  = self.last_ncd_log_line.split()[4]
        return int(n_warnings)

    @property
    def success(self):
        return n_errors == 0

class AquilonWorkflow(object):
    """
    base class to perform an atomic
    operation within Aquilon
    """

    def __init__(self):
        self.sandbox_name = None
        self.hostname_l = []
        self.check_quattor = False
        self.git_message = None

    def prolog(self):
        pass

    def create_sandbox(self):
        """
        if it does not exist yet, creates a Sandbox
        """
        print('Creating Sandbox with name %s' %self.sandbox_name)
        out, err, rc = run('aq add_sandbox --sandbox %s' %self.sandbox_name)
        if rc != 0:
            print('Failed creating Sandbox %s.' %self.sandbox_name)
            print('Error message = %s' %err)
            print('Aborting.')
            raise SandboxCreationFailure(self.sandbox_name)
        else:
            print('Sandbox with name %s created' %self.sandbox_name)

    def change(self):
        raise NotImplementedError

    def handle_host_l(self):
        """
        manage Hosts into the Sandbox and recompile them
        """
        print('Start handling Hosts')
        for hostname in self.hostname_l:
            rc = self._handle_host(hostname)
            if rc != 0:
                print('Handling Host %s failed. Aborting' %hostname)
                raise HostHandlingFailure(hostname)
        print('All Hosts handled')

    def _handle_host(self, hostname):
        """
        if it is in Domain 'prod',
        manage a single Host into the Sandbox and recompile it
        """
        print('Start handling Host %s' %hostname)
        print('Managing Host %s into Sandbox %s' %(hostname, self.sandbox_name))
        out, err, rc = run('aq manage --hostname %s --sandbox %s/%s' %(hostname, getpass.getuser(), self.sandbox_name))
        if rc != 0:
            print('Host %s is not in a Domain. Skipping it' %hostname)
        else:
            print('Host %s managed into Sandbox %s' %(hostname, self.sandbox_name))
            print('Compiling Host %s' %hostname)
            out, err, rc = run('aq make --hostname %s' %hostname)
            if rc == 0:
                print('Compiling Host %s succeeded' %hostname)
                self._quattor(hostname)
                return 0
            else:
                print('Compiling Host %s failed' %hostname)
                return 1

    def _quattor(self, hostname):
        """
        when requested, check if Quattor finished OK
        """
        if self.check_quattor:
            quattor = Quattor(hostname)
            quattor.check_quattor()
            if not quattor.success:
                raise QuattorFailure(hostname)

    def git_commit(self):
        """
        commit the changes
        """
        print('Commiting the changes with message: %s' %self.git_message)
        cmd = 'git commit -a -m "%s"' %self.git_message
        out, err, rc = run(cmd)
        if rc == 0:
            print('Changes committed successfully')
        else:
            print('Committing changes failed')
            print('Stdout:')
            print(out)
            print('Stderr:')
            print(err)
            print('Aborting')
            raise GitCommitFailure(err)

    def publish(self):
        print('Publishing Sandbox')
        cmd = 'cd ~/%s; aq publish --sandbox %s --rebase' %(self.sandbox_name, self.sandbox_name)
        out, err, rc = run(cmd)
        print('Sandbox published: http://aquilon.gridpp.rl.ac.uk/sandboxes/diff.php?sandbox=%s' %self.sandbox_name)

    def epilog(self):
        pass

    def run(self):
        self.prolog()
        self.create_sandbox()
        self.change()
        self.handle_host_l()
        self.git_commit()
        self.publish()
        self.epilog()

