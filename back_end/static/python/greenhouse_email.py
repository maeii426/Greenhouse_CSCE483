#!/usr/bin/env python

# ---------------------------------------------------------------------------- #
# Developer: Andrew Kirfman                                                    #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./email.py                                                             #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Standard Library Includes                                                    #
# ---------------------------------------------------------------------------- #

import logging
from email.mime.text import MIMEText

# ---------------------------------------------------------------------------- #
# Console/File Logger                                                          #
# ---------------------------------------------------------------------------- #

print_logger = logging.getLogger(__name__)
print_logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------- #
# Email Interface                                                              #
# ---------------------------------------------------------------------------- #

# Our account login information
# Address: greenhouse.reporter@gmail.com
# Password: TeamGreenThumb (case sensitive)

def send_email(subject, message, recepient):
    msg = MIMEText(str(message))

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = subject
    msg['From'] = "greenhouse.reporter@gmail.com"
    msg['To'] = str(recepient)

    # Send the message via our own SMTP server, but don't include the
    # envelope header
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.ehlo()
    s.starttls()
    s.login("greenhouse.reporter", "TeamGreenThumb")
    s.sendmail("greenhouse.reporter@gmail.com", [str(recepient)], msg.as_string())
    s.quit()