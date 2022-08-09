from __future__ import annotations

import pandas as pd

from meetupmatcher.config import Config
from meetupmatcher.util.log import logger


class People:
    cols = {"name", "email", "slack", "notwo"}

    def __init__(self, df: pd.DataFrame, config: Config):
        self.config = config
        self._check_df(self._prepare_df(df))
        df.slack = df.slack.fillna("")
        self.df = df
        logger.info(
            f"Loaded {len(self.df)} people. {self.df.notwo.sum()} people "
            f"do not want to be in groups of two"
        )

    def _prepare_df(self, df: pd.DataFrame) -> pd.DataFrame:
        if "columns" in self.config:
            for target, source in self.config["columns"].items():
                df.rename(columns={source: target}, inplace=True)
        if "name" not in df.columns:
            df["name"] = df.email.apply(lambda x: x.split("@")[0])
        return df

    def _check_df(self, df: pd.DataFrame):
        cols = set(df.columns)
        if not df.email.is_unique:
            raise ValueError("Emails not unique. Do you have duplicates?")
        if not df.slack.dropna().is_unique:
            logger.warning("Not all slacks unique.")
        if not df.name.is_unique:
            logger.warning("Not all names unique.")
        if not self.cols.issubset(cols):
            raise ValueError(
                f"Columns appear to be missing. Expected: {self.cols}, got: {cols}"
            )
        assert df.notwo.isin([True, False]).all()

    def __len__(self):
        return len(self.df)
