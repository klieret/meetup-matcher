import argparse
import time

import pandas as pd

from meetupmatcher.data import People
from meetupmatcher.matcher import NoSolution, ProblemStatement, pair_up, solve_numeric
from meetupmatcher.pseudorandom import get_rng_from_option
from meetupmatcher.templating import EmailGenerator
from meetupmatcher.util.log import logger


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("input", help="Input csv file")
    parser.add_argument(
        "--seed", type=str, help="Set the seed for the RNG", default="week"
    )
    args = parser.parse_args(args=args)
    rng = get_rng_from_option(args.seed)
    logger.debug(f"Reading from {args.input}")
    people = People(pd.read_csv(args.input))
    try:
        solution = solve_numeric(ProblemStatement(len(people), people.df.notwo.sum()))
    except NoSolution as e:
        logger.critical(f"No solution could be found: {e}")

    logger.info(f"Solution: {solution}")
    paired_up = pair_up(
        solution,
        set(people.df.index[~people.df.notwo]),
        set(people.df.index[people.df.notwo]),
        rng=rng,
    )
    mails = list(EmailGenerator().generate_emails(people, paired_up))
    if args.dry_run:
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
