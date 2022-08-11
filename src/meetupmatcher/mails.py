from __future__ import annotations

import getpass
import time

import yagmail

from meetupmatcher.templating import Email
from meetupmatcher.util.log import logger


def send_mails(mails: list[Email]) -> None:
    username = input("Gmail username: ")
    pwd = getpass.getpass("Gmail password: ")
    yag = yagmail.SMTP(username, pwd)
    for mail in mails:
        logger.debug(f"Sending email to {mail.to}")
        yag.send(to=mail.to, subject=mail.subject, contents=mail.content)
        logger.debug("Sending done. Sleeping for 1 second")
        time.sleep(1)
