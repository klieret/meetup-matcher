import argparse

import pandas as pd

from meetupmatcher.data import People
from meetupmatcher.matcher import ProblemStatement, pair_up, solve_numeric
from meetupmatcher.pseudorandom import get_rng_from_option
from meetupmatcher.templating import EmailGenerator
from meetupmatcher.util.log import logger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("input", help="Input csv file")
    parser.add_argument(
        "--seed", type=str, help="Set the seed for the RNG", default="week"
    )
    args = parser.parse_args()
    rng = get_rng_from_option(args.seed)
    people = People(pd.read_csv(args.input))
    solution = solve_numeric(ProblemStatement(len(people), people.df.notwo.sum()))
    logger.info(f"Solution: {solution}")
    partitions, remove = pair_up(
        solution,
        set(people.df.index[~people.df.notwo]),
        set(people.df.index[people.df.notwo]),
        rng=rng,
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
