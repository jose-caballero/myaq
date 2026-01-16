#!/usr/bin/env python

import os
import sys

from sysadmin.bcolors import printerror, printwarning
from myaq.location import Sandbox
from myaq.host import Host
from myaq.workflows import exceptions
from sysadmin.myshell import run
from myquattor.quattorlib import Quattor
from myaq.workflows.tools import send_email, ask_if_deploy


class AquilonWorkflow(object):
    """
    base class to perform an atomic
    operation within Aquilon
    """

    def __init__(self):
        self.sandbox_name = None
        self.sandbox = None
        self.hostname_l = []
        self.host_l = []
        self.check_quattor = False
        self.git_message = None
        self.to_deploy = ask_if_deploy()

    def prolog(self):
        """
        if needed, actions to be done before starting
        to be reimplemented by the clients 
        """
        pass

    def create_sandbox(self):
        """
        if it does not exist yet, creates a Sandbox
        """
        # FIXME
        # -- handle when the name of the Sandbox is too long
        # -- when creating the Sandbox fails, prints out the error
        

        self.sandbox = Sandbox(self.sandbox_name)
        printwarning('Creating Sandbox with name %s' %self.sandbox.shortname)
        if self.sandbox.exists:
            printerror('Sandbox %s already exists. Aborting' %self.sandbox.shortname)
            raise exceptions.SandboxCreationFailure(self.sandbox.shortname)
        else:
            self.sandbox.create()
            printwarning('Sandbox with name %s created' %self.sandbox.shortname)

    def change(self):
        """
        specific actions to implement a give Workflow
        Must be implemented by the clients 
        """
        raise NotImplementedError

    def handle_host_l(self):
        """
        manage Hosts into the Sandbox and recompile them
        """
        printwarning('Start handling Hosts')
        for hostname in self.hostname_l:
            host = Host(hostname)
            self.host_l.append(host)
            rc = self._handle_host(host)
            if rc != 0:
                print('Compilation for Host %s failed. Aborting' %host.name)
                raise exceptions.HostHandlingFailure(host.name)
        printwarning('All Hosts handled')

    def _handle_host(self, host):
        """
        if it is in Domain 'prod',
        manage a single Host into the Sandbox and recompile it
        """
        printwarning('Start handling Host %s' %host.name)
        if host.location.name == 'prod':
            printwarning('Managing Host %s into Sandbox %s' %(host.name, self.sandbox.shortname))
            self.sandbox._manage_host(host)
            printwarning('Host %s managed into Sandbox %s' %(host.name, self.sandbox.shortname))
            printwarning('Compiling Host %s' %host.name)
            results = host.make()
            if results.rc == 0:
                printwarning('Compiling Host %s succeeded' %host.name)
                self._quattor(host)
                return 0
            else:
                printerror('Compiling Host %s failed' %host.name)
                # FIXME
                # print the error
                return 1
        else:
            printerror('Host %s is not in Domain prod. Skipping it' %host.name)
        printwarning('Handling Host %s complete' %host.name)

    def _quattor(self, host):
        """
        when requested, check if Quattor finished OK
        """
        if self.check_quattor:
            quattor = Quattor(host.name)
            quattor.check_quattor()
            if not quattor.success:
                raise exceptions.QuattorFailure(host.name)

    def git_commit(self):
        """
        commit the changes
        """
        printwarning('Commiting the changes with message: %s' %self.git_message)
        path = '~/%s' %self.sandbox_name
        path = os.path.expanduser(path)
        cmd = 'cd %s; git commit -a -m "%s"' %(path, self.git_message)
        results = run(cmd)
        if results.rc == 0:
            printwarning('Changes committed successfully')
        else:
            printerror('Committing changes failed')
            printerror('Stdout:')
            printerror(results.out)
            printerror('Stderr:')
            printerror(results.err)
            printerror('Aborting')
            raise exceptions.GitCommitFailure(results.err)

    def publish(self):
        printwarning('Publishing Sandbox')
        self.sandbox.publish()
        printwarning('Sandbox published: %s' %self.sandbox.page)

    @property
    def commit_id(self):
        f = '/var/quattor/templates/wup22514/%s/.git/refs/heads/%s' %(self.sandbox_name, self.sandbox_name)
        id = open(f).read().strip()
        return id

    @property
    def commit_url(self):
        url = 'http://phabricator.gridpp.rl.ac.uk/rAQ%s' %self.commit_id
        return url

    def deploy(self):
        if self.to_deploy:
            sandbox = Sandbox(self.sandbox_name)
            printwarning('Deploying Sandbox: %s' %cmd)
            sandbox.deploy()
            printwarning('Sandbox deployed')

            printwarning('Sending email to GST requesting the audit of the commit')
            subject = '[pre-published Sandbox requires audit] %s' %self.commit_id
            body = 'A Sandbox has been pre-published by script. The commit needs to be audited: \n\n %s \n\n' %self.commit_url
            send_email(subject, body)
            printwarning('email sent')

            printwarning('Deleting Sandbox: %s' %cmd)
            sandox.delete()
            printwarning('Sandbox deleted')


    def epilog(self):
        """
        if needed, actions to be done before starting
        to be reimplemented by the clients 
        """
        pass

    def run(self):
        try:
            self.prolog()
            self.create_sandbox()
            self.change()
            self.handle_host_l()
            self.git_commit()
            self.publish()
            self.deploy()
            self.epilog()
        except Exception as ex:
            printerror(ex) 
