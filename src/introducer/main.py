import argparse

import pandas as pd

from introducer.data import People
from introducer.matcher import ProblemStatement, pair_up, solve_numeric
from introducer.templating import EmailGenerator
from introducer.util.log import logger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("input", help="Input csv file")
    args = parser.parse_args()
    people = People(pd.read_csv(args.input))
    solution = solve_numeric(ProblemStatement(len(people), people.df.notwo.sum()))
    logger.info(f"Solution: {solution}")
    partitions, remove = pair_up(
        solution,
        set(people.df.index[~people.df.notwo]),
        set(people.df.index[people.df.notwo]),
    )
    mails = EmailGenerator().generate_emails(people, partitions, remove)
    if args.dry_run:
        for mail in mails:
            print(mail.to, mail.subject)
            print(mail.content)
            print("-" * 80)
    else:
        raise NotImplementedError


if __name__ == "__main__":
    main()
