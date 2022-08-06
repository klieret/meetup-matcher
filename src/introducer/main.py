import argparse

import pandas as pd

from introducer.data import People
from introducer.mails import EmailGenerator
from introducer.matcher import ProblemStatement, pair_up, solve_numeric


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("input", help="Input csv file")
    args = parser.parse_args()
    people = People(pd.read_csv(args.input))
    partitions, remove = pair_up(
        solve_numeric(ProblemStatement(len(people), people.df.notwo.sum())),
        set(people.df.index[~people.df.notwo]),
        set(people.df.index[people.df.notwo]),
    )
    mails = EmailGenerator().generate_emails(people, partitions, remove)
    if args.dry_run:
        for mail in mails:
            print(mail.to, mail.subject, mail.content)
    else:
        raise NotImplementedError
