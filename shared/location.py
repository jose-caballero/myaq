#!/usr/bin/env python

import argparse
import os
import shutil
import sys

from bcolors import bcolors, colorprint
from myaq.location import SandboxHandler, Location
from sysadmin.myshell import call

# ==============================================================================

class CreateSandbox(object):
    def __init__(self, name, start, description):
        """
        :name string:
        :start string:
        :description string:
        """
        self.name = name
        self.start = Location(start)
        self.description = description

    def _check_length(self):
        if len(self.name) > 32:
            msg = 'The length of the sandbox is too long (limit = 32 chars)'
            colorprint((msg, bcolors.FAIL))
            sys.exit(1)
    
    def _check_name(self, check_name):
        if check_name:
            colorprint(('Remember, for developement, I like sandbox name starting with dev_', bcolors.WARNING))
            colorprint(('Am I OK with the name I am proposing? [y/n]', bcolors.WARNING))
            answer = raw_input()
            if answer.lower() in ['n', 'no']:
                sys.exit(1)
    
    def _create_sandbox(self):
        """
        :sandox_name string:
        :start Location:
        """
        sandbox = SandboxHandler().create(self.name, self.start)
        return sandbox
    
    def _exclude_zeromq(self):
        if self.name.startswith('dev_'):
            colorprint(('This is a development sandbox. Excluding zeromq from openstack train yum repo file', bcolors.WARNING))
            train = '/var/quattor/templates/wup22514/' + self.name + '/shared/repository/openstack/train-el7-x86_64.pan'
            f_train = open(train)
            train_tmp = train + '_tmp'
            f_train_tmp = open(train_tmp, 'w')
            for line in f_train.readlines():
                f_train_tmp.write(line)
                if 'excludepkgs' in line:
                    f_train_tmp.write("    'zeromq',\n")
            shutil.move(train_tmp, train)
    
    def _create_link(self):
        link_name = '/var/quattor/templates/wup22514/sandboxes/%s' %self.name
        dest = '/var/quattor/templates/wup22514/%s' %self.name
        os.symlink(dest, link_name)
    
    def _add_to_catalog(self):
        catalog = '/var/quattor/templates/wup22514/sandboxes/.sandboxes'
        f_catalog = open(catalog, 'a')
        # check if description is multiline
        description_lines = self.description.split('\\n')
        line = self.name
        line += ' ' * (36 - len(line))
        line += self.start.name
        line += ' ' * (72 - len(line))
        line += description_lines[0]
        line += '\n'
        for i in description_lines[1:]:
            line += ' ' * 72
            line += i
            line += '\n'
        line += '\n'
        f_catalog.write(line)
    
    def _touch_sandbox(self):
        cmd = 'touch %s' %self.name
        call(cmd)

    def create(self, check_name=True):
        self._check_length()
        self._check_name(check_name)
        sandbox = self._create_sandbox()
        if not sandbox:
            sys.exit(1)
        self._exclude_zeromq()
        self._create_link()
        self._add_to_catalog()
        self._touch_sandbox()
        return sandbox

