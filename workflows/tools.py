#!/usr/bin/python3

import os.path
import shutil
import sys

def replace_line_in_file(dirpath, input_filename, pattern, newline):
    """
    replace a given line in a file.
    :param str dirpath: directory with the file to be updated
    :param str input_filename: name of the file to be updated
    :param str pattern: pattern to identify the line to be modified
    :param str newline: new content of the line
    """
    input_filename = os.path.join(dirpath, input_filename)
    input_f = open(input_filename)
    out_filename = '%s.new' %input_filename
    output_filename = os.path.join(dirpath, out_filename)
    output_f = open(output_filename, 'w')

    for line in input_f.readlines():
        if line.startswith(pattern):
            line = newline
            if not line.endswith('\n'):
                line += '\n'
        output_f.write(line)

    shutil.move(output_filename, input_filename)


import socket
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    sender = 'sandbox-autodeploy@%s' %socket.gethostname()
    to = 'ESCPSCSGridServicesteam@stfc.ac.uk'
    message = MIMEText(body)
    message['subject'] = subject
    message['From'] = sender
    message['To'] = to
    to = [to]
    server = smtplib.SMTP()
    server.connect()
    server.sendmail(sender, to, message.as_string())
    server.close()


def ask_if_deploy():
    if sys.version_info.major == 3:
        x = input('\nShould the Sandbox be auto-deployed? [y]/n: ')
    else:
        x = raw_input('\nShould the Sandbox be auto-deployed? [y]/n: ')
    if x == "":
        return True
    else:
        return  x == 'y'

