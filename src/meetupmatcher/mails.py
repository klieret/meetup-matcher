from __future__ import annotations

import getpass
import time
from abc import ABC, abstractmethod
from pathlib import Path, PurePath

import yagmail

from meetupmatcher.templating import Email
from meetupmatcher.util.log import logger


class MailSender(ABC):
    def __init__(self, dry_run: bool = True, dump_file: str | PurePath | None = None):
        """

        Args:
            dry_run:
            dump_file: If dry run, dump into this file instead of printing
        """
        self.dry_run = dry_run
        self.dump_file = Path(dump_file) if dump_file is not None else None

    def send(self, emails: list[Email]) -> None:
        if self.dry_run:
            self.send_dry_run(emails)
        else:
            logger.warning(
                f"About to send {len(emails)} emails. This is NOT a dry-run."
            )
            self._send(emails)

    @abstractmethod
    def _send(self, emails: list[Email]) -> None:
        pass

    def send_dry_run(self, emails: list[Email]) -> None:
        dump = ("\n" + "-" * 80 + "\n").join([mail.to_str() for mail in emails])
        if self.dump_file:
            with self.dump_file.open("w") as f:
                f.write(dump)
        else:
            print(dump)


class YagmailSender(MailSender):
    def _send(self, emails: list[Email]) -> None:
        username = input("Gmail username: ")
        pwd = getpass.getpass("Gmail password: ")
        yag = yagmail.SMTP(username, pwd)
        for mail in emails:
            logger.debug(f"Sending email to {mail.to}")
            yag.send(to=mail.to, subject=mail.subject, contents=mail.content)
            logger.debug("Sending done. Sleeping for 1 second")
            time.sleep(1)
