#!/usr/bin/env python


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
