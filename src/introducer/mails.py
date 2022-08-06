import importlib.resources
from dataclasses import dataclass

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from introducer.data import People


@dataclass
class Email:
    to: list[str]
    subject: str
    content: str


class EmailGenerator:
    def _generate_remove_email(self, row: pd.Series) -> Email:
        return Email(
            to=[row.email],
            subject="Postdoc tea-time pairing",
            content="",
        )

    def generate_emails(
        self, people: People, partitions: list[set[int]], remove: set[int]
    ) -> list[Email]:
        template_path = importlib.resources.path(__package__, "templates")
        environment = Environment(loader=FileSystemLoader(template_path))

        emails = []

        r_template = environment.get_template("removed.txt.jinja")
        for r in remove:
            person = people.df.loc[r]
            emails.append(
                Email(
                    to=[person.email],
                    subject="Tea-time pairing",
                    content=r_template.render(name=person["name"]),
                )
            )
        m_template = environment.get_template("matched.txt.jinja")
        for partition in partitions:
            group = people.df.loc[list(partition)]
            emails.append(
                Email(
                    to=group.email.tolist(),
                    subject="Tea-time pairing",
                    content=m_template.render(names=group.name.to_list(), people=group),
                )
            )
        return emails
