from __future__ import annotations

import sys
import time

import click
import pandas as pd

from meetupmatcher.config import Config
from meetupmatcher.data import People
from meetupmatcher.matcher import NoSolution, ProblemStatement, pair_up, solve_numeric
from meetupmatcher.pseudorandom import get_rng_from_option
from meetupmatcher.templating import EmailGenerator
from meetupmatcher.util.log import logger


@click.command()
@click.argument("inputfile")
@click.option("-n", "--dry-run", is_flag=True, help="Don't send emails")
@click.option("-c", "--config", help="Configuration file", default=None, type=str)
@click.option(
    "-s", "--seed", type=str, help="Seed for random number generator", default="week"
)
@click.option(
    "-t", "--templates", help="Path to template directory", default=None, type=str
)
def main(inputfile: str, dry_run: bool, config: str, seed: str, templates: str) -> None:
    rng = get_rng_from_option(seed)
    logger.debug(f"Reading from {inputfile}")
    people = People(pd.read_csv(inputfile), config=Config(config))
    try:
        solution = solve_numeric(ProblemStatement(len(people), people.df.notwo.sum()))
    except NoSolution as e:
        logger.critical(f"No solution could be found: {e}")
        sys.exit(1)

    logger.info(f"Solution: {solution}")
    paired_up = pair_up(
        solution,
        set(people.df.index[~people.df.notwo]),
        set(people.df.index[people.df.notwo]),
        rng=rng,
    )
    mails = list(
        EmailGenerator(template_path=templates).generate_emails(people, paired_up)
    )
    if dry_run:
        print(("\n" + "-" * 80 + "\n").join([mail.to_str() for mail in mails]))
    else:
        import getpass

        import yagmail

        logger.warning(f"About to send {len(mails)} emails. This is NOT a dry-run.")
        username = input("Gmail username: ")
        pwd = getpass.getpass("Gmail password: ")
        yag = yagmail.SMTP(username, pwd)
        for mail in mails:
            logger.debug(f"Sending email to {mail.to}")
            yag.send(to=mail.to, subject=mail.subject, contents=mail.content)
            logger.debug("Sending done. Sleeping for 1 second")
            time.sleep(1)


if __name__ == "__main__":
    main()
