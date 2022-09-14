from __future__ import annotations

import pickle
import sys

import click
import pandas as pd

from meetupmatcher.config import Config
from meetupmatcher.data import People
from meetupmatcher.mails import YagmailSender
from meetupmatcher.matcher import NoSolution, ProblemStatement, pair_up, solve_numeric
from meetupmatcher.pseudorandom import get_rng_from_option
from meetupmatcher.templating import EmailGenerator
from meetupmatcher.util.log import logger


@click.command()
@click.argument("inputfile")
@click.option("-n", "--dry-run", is_flag=True, help="Don't send emails")
@click.option("-c", "--config", help="Configuration file", default=None, type=str)
@click.option("--matching-stats", help="Export statistics from matching process")
@click.option(
    "-s",
    "--seed",
    type=str,
    help="Seed for random number generator. Supported are 'week', an integer, "
    "or anything that can be interpreted as a date",
    default="week",
    show_default=True,
)
@click.option(
    "-t", "--templates", help="Path to template directory", default=None, type=str
)
def main(
    inputfile: str,
    dry_run: bool,
    config: str,
    seed: str,
    templates: str,
    matching_stats="",
) -> None:
    rng = get_rng_from_option(seed)
    logger.debug(f"Reading from {inputfile}")
    people = People(pd.read_csv(inputfile), config=Config(config))
    try:
        solution = solve_numeric(ProblemStatement(len(people), people.df.notwo.sum()))
    except NoSolution as e:
        logger.critical(f"No solution could be found: {e}")
        sys.exit(1)
    logger.info(f"Solution: {solution}")
    if people._availability_product_cols:
        availabilities = people.df[people._availability_product_cols].to_numpy()
    else:
        availabilities = None
    paired_up, statistics = pair_up(
        solution,
        people.df.index.to_numpy(),
        people.df.notwo.to_numpy(),
        availabilities=availabilities,
        rng=rng,
    )
    logger.info(f"Best cost function: {statistics.best}")
    if matching_stats:
        with open(matching_stats, "wb") as f:
            pickle.dump(statistics, f)
    logger.info(paired_up)
    mails = list(
        EmailGenerator(template_path=templates).generate_emails(people, paired_up)
    )
    YagmailSender(dry_run).send(mails)


if __name__ == "__main__":
    main()
