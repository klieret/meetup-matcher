from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from meetupmatcher.config import Config
from meetupmatcher.util.log import logger


class People:
    required_cols = {"name", "email", "slack", "notwo"}

    def __init__(self, df: pd.DataFrame, config: Config):
        self.config = config
        self._availability_product_cols: list[str] = []
        self._check_df(self._prepare_df(df, config))
        self.df = df
        logger.info(
            f"Loaded {len(self.df)} people. {self.df.notwo.sum()} people "
            f"do not want to be in groups of two"
        )

    def _prepare_df(self, df: pd.DataFrame, config: Config) -> pd.DataFrame:
        if "columns" in self.config:
            for target, source in self.config["columns"].items():
                df.rename(columns={source: target}, inplace=True)
        if "notwo_truthy" in config:
            df.notwo = df.notwo == config["notwo_truthy"]
        if "name" not in df.columns:
            df["name"] = df.email.apply(lambda x: x.split("@")[0])
        if "slack" not in df.columns:
            df["slack"] = ""
        df.slack = df.slack.fillna("")
        if "notwo" not in df.columns:
            df["notwo"] = False
        else:
            df.notwo = df.notwo.fillna(False)
        availability_cols = config.get("availabilities", {}).get("columns", [])
        if availability_cols:
            logger.debug("Found availability columns: %s", availability_cols)
            availability_values = set()
            for col in availability_cols:
                df[col] = df[col].fillna("")
                _vals = (
                    df[col].apply(lambda x: [a.strip() for a in x.split(",")]).tolist()
                )
                _vals_merged = list(itertools.chain.from_iterable(_vals))
                availability_values |= set(_vals_merged)
            if not availability_values:
                raise ValueError("Availability columns specified but no values found")
            logger.debug(
                "Found availability values: %s", ", ".join(availability_values)
            )
            for col in availability_cols:
                for value in availability_values:
                    col_name = f"{col} {value}"
                    # todo: This could be done cleaner...
                    df[col_name] = df[col].str.contains(value)
                    self._availability_product_cols.append(col_name)
            logger.debug(
                "Availability product columns: %s",
                ", ".join(self._availability_product_cols),
            )
        return df

    def _check_df(self, df: pd.DataFrame):
        cols = set(df.columns)
        if not df.email.is_unique:
            raise ValueError("Emails not unique. Do you have duplicates?")
        if not df.slack.replace({"": np.nan}).dropna().is_unique:
            logger.warning("Not all slacks unique.")
        if not df.name.is_unique:
            logger.warning("Not all names unique.")
        if not self.required_cols.issubset(cols):
            raise ValueError(
                f"Columns appear to be missing. "
                f"Expected: {self.required_cols}, got: {cols}"
            )
        assert df.notwo.isin([True, False]).all()

    def __len__(self):
        return len(self.df)
