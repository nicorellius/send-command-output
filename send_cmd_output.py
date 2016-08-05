#!/usr/bin/env python

# MIT License

# Copyright (c) 2016 Nick Vincent-Maloneyi <nick@nicorelli.us>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
 
# Requirements  : Python 2.7 or higher  
# Usage         : send_cmd_output.py [-h] email cmd

# Sends message with optional attachment containing stdout and stderr for any given command.

# Positional arguments
# email         the email address to send output to
# cmd           the command and arguments to execute. If you need arguments,
#               wrap the whole command in quotes.

# optional arguments:
# -h, --help  show this help message and exit

# Example usage for running rysnc:
# send_cmd_output.py email@example.com 'rsync -va --no-perms /stuff/to/backup /where/to/put/backup'            

import sys
import smtplib
import subprocess
import argparse
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

# These are examples/placeholders and should be replaced with your email server details.
# Recommend using an SMTP server.
from_email = 'email@example.com'
username = 'email@example.com'
password = 'somepassword'
smtp_server = 'smtp.gmail.com:587'

def call(cmd):
    # print("command: {0}".format(cmd))
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        shell=True
    )
    
    out, err = proc.communicate()
    
    return out, err, proc.returncode

def make_attachment(filename, content):
    
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(content)
    
    Encoders.encode_base64(attachment)
    
    attachment.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(filename))
    
    return attachment

def email_result(cmd, recipient):
    
    out, err, returncode = call(cmd)
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = recipient
    msg['Date'] = formatdate(localtime=True)
    
    if returncode == 0:
        msg['Subject'] = 'send command output script completed successfully'.format(cmd)
    else:
        msg['Subject'] = 'ERROR: script or system returned exit status {0}'.format(returncode) 
 
    # Note that if these attachments become too large, Gmail might not attach them.
    # Comment out the `msg.attach` lines for stdout/stderr if you don't want the attachments.
    msg.attach(MIMEText('{0}\nEXIT STATUS {1}'.format(cmd, str(returncode))))
    msg.attach(make_attachment('stdout.txt', out))
    msg.attach(make_attachment('stderr.txt', err))
    
    smtp = smtplib.SMTP(smtp_server)
    smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(from_email, recipient, msg.as_string())
    smtp.quit()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
            description='Sends stdout and stderr by email after running the command.')
    parser.add_argument('email', type=str,
            help='The email address that you want to receive the output.')
    parser.add_argument('cmd', type=str,
            help='The command and arguments to execute. If you need arguments, wrap the whole command in quotes.')
    
    args = parser.parse_args()
    
    email_result(args.cmd, args.email)
