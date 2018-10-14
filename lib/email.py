"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.
"""

import lib.kvpairs as kvpairs
import lib.log as log

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import smtplib
import imaplib


cfg = kvpairs.load(kvpairs.get_config_filename())

email_live = cfg['email.live']

email_server_smtp_host = cfg['email.server.smtp.host']
email_server_smtp_port = cfg['email.server.smtp.port']
email_server_smtp_username = cfg['email.server.smtp.username']
email_server_smtp_password = cfg['email.server.smtp.password']

email_server_imap_host = cfg['email.server.imap.host']
email_server_imap_username = cfg['email.server.imap.username']
email_server_imap_password = cfg['email.server.imap.password']

email_from = cfg['email.from']
email_to = cfg['email.to']


def send(to, subject, body_html):
    """
    Send an email using the configured email server.

    The email will be sent as both html and plain text, therefore making
    no assumptions about the user's email preferences.
    """

    try:

        smtp = smtplib.SMTP(email_server_smtp_host, email_server_smtp_port)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(email_server_smtp_username, email_server_smtp_password)

        msg = MIMEMultipart('alternative')

        text = 'text version of the email message'
        html = body_html

        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, body_html))

        msg['Subject'] = subject
        msg['From'] = email_from
        msg['To'] = to
        
        if email_live == 'true':
            smtp.sendmail(email_from, [to], msg.as_string())
            log.debug('email.py::send', 'sent email to: ' + to)
        else:
            log.debug('email.py::send', 'sent *MOCK* email to: ' + to)

        smtp.quit()

    except Exception as e:
        log.alert('email.py::send', 'Error attempting to send email: ' + str(e))


def create_mailto(security_ulid, to, subject, body):
    """
    Create email friendly mailto links in both html and plain text.
    """

    template = '<a href="mailto:{{to}}?subject={{subject}}&body=security%20id%3A%20{{security_ulid}}">{{body}}</a>'
    return template


def get_imap_messages():
    """
    Retrieve email messages from the configured IMAP inbox,
    yielding to the caller on each message.
    """

    try:

        imap = imaplib.IMAP4_SSL(email_server_imap_host)
        imap.login(email_server_imap_username, email_server_imap_password)
        imap.select('inbox')
        typ, data = imap.search(None, '(SUBJECT "test")')

        for num in data[0].split():

            data = imap.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT FROM TO)])')
            msg = data[1][0][1]
            yield msg

        print("DONE")

    except Exception as e:
        log.error(str(e))


def parse_message(email_message):
    """
    Initially, email message headers will look something like this:

        b'From: "Me" <me@example.com>\\r\\nTo: "Me" <me@example.com>\\r\\nSubject: test\\r\\n\\r\\n\\'

    This function will parse that mess and turn it into a dict that looks like this:

        {'from_name':'Me','from_email':'me@example.com', 'to_name':'Me', 'to_email':'me@example.com', 'subject':'test'}
    """

    details = {}

    msg = email_message.decode("utf-8")
    msg = msg.replace('\r\n', '|')
    msg =  msg.replace('||', '')

    msg_list = msg.split('|')

    for item in msg_list:

        if item.startswith('From: '):

            # email from looks like: 'From: "Me" <me@example.com>'
            regex = re.compile('From: ["](.*)["] [<](.*)[>]')
            name = regex.match(item).group(1)
            email = regex.match(item).group(2)

            details['from_name'] = name
            details['from_email'] = email

        elif item.startswith('To: '):

            # email to looks like: 'To: "Me" <me@example.com>'
            regex = re.compile('To: ["](.*)["] [<](.*)[>]')
            name = regex.match(item).group(1)
            email = regex.match(item).group(2)

            details['to_name'] = name
            details['to_email'] = email

        elif item.startswith('Subject: '):

            details['subject'] = item[9:]

    return details


def receive():
    """
    Fetch all email from the configured IMAP inbox.
    Return to the caller as a list of dict objects, each one with the contents of a single email.
    """

    email_list = []

    try:

        for msg in get_imap_messages():

            msg_dict = parse_message(msg)
            email_list.append(msg_dict)

    except Exception as e:
        log.alert('email.py::receive', str(e))

    return email_list
