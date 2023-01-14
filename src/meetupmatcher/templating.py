from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Iterator

import numpy as np
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
            subject="Coffee meetup",
            content=template.render(name=person["name"]),
        )

    def _generate_pair_email(
        self,
        group: pd.DataFrame,
        av_cols: list[str] | None = None,
        av: np.ndarray | None = None,
    ) -> Email:
        if av_cols:
            availability_strs = sorted(
                av_cols[i] for i in range(len(av_cols)) if av[i]  # type: ignore
            )
        else:
            availability_strs = None
        template = self.environment.get_template("matched.txt.jinja")
        return Email(
            to=group.email.tolist(),
            subject="Coffee meetup: You have been matched to your group",
            content=template.render(
                names=[n.strip() for n in group.name.to_list()],
                people=group,
                availabilities=availability_strs,
            ),
        )

    def generate_emails(
        self, people: People, paired_up: PairUpResult
    ) -> Iterator[Email]:
        for r in paired_up.removed:
            person = people.df.loc[r]
            yield self._generate_remove_email(person)
        for i, partition in enumerate(paired_up.segmentation):
            group = people.df.loc[sorted(partition)]
            yield self._generate_pair_email(
                group,
                av_cols=people._availability_product_cols,
                av=paired_up.joint_availabilities[i],
            )
