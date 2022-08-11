from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Iterator

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from meetupmatcher.data import People
from meetupmatcher.matcher import PairUpResult
from meetupmatcher.util.compat_resource import resources


@dataclass
class Email:
    to: list[str]
    subject: str
    content: str

    def to_str(self) -> str:
        return f"To: {', '.join(self.to)}\nSubject: {self.subject}\n\n{self.content}"


class EmailGenerator:
    def __init__(self, template_path: str | None | PurePath = None):
        if template_path is None:
            template_path = Path(
                resources.files("meetupmatcher.templates")  # type: ignore
            )
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
        self, people: People, paired_up: PairUpResult
    ) -> Iterator[Email]:
        for r in paired_up.removed:
            person = people.df.loc[r]
            yield self._generate_remove_email(person)
        for partition in paired_up.segmentation:
            group = people.df.loc[list(partition)]
            yield self._generate_pair_email(group)
