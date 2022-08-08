import sys
from dataclasses import dataclass
from typing import Iterator

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from meetupmatcher.data import People

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources


@dataclass
class Email:
    to: list[str]
    subject: str
    content: str


class EmailGenerator:
    def __init__(self):
        template_path = resources.files("meetupmatcher") / "templates"
        self.environment = Environment(
            loader=FileSystemLoader(template_path)  # type: ignore
        )

    def _generate_remove_email(self, person: pd.Series) -> Email:
        template = self.environment.get_template("removed.txt.jinja")
        return Email(
            to=[person.email],
            subject="Tea-time pairing",
            content=template.render(name=person["name"]),
        )

    def _generate_pair_email(self, group: pd.DataFrame) -> Email:
        template = self.environment.get_template("matched.txt.jinja")
        return Email(
            to=group.email.tolist(),
            subject="Tea-time pairing",
            content=template.render(names=group.name.to_list(), people=group),
        )

    def generate_emails(
        self, people: People, partitions: list[set[int]], remove: set[int]
    ) -> Iterator[Email]:
        for r in remove:
            person = people.df.loc[r]
            yield self._generate_remove_email(person)
        for partition in partitions:
            group = people.df.loc[list(partition)]
            yield self._generate_pair_email(group)
