import pandas as pd

from teatimematcher.util.log import logger


class People:
    cols = {"name", "email", "slack", "notwo"}

    def __init__(self, df: pd.DataFrame):
        self._check_df(df)
        self.df = df
        logger.info(
            f"Loaded {len(self.df)} people. {self.df.notwo.sum()} people "
            f"do not want to be in groups of two"
        )

    def _check_df(self, df: pd.DataFrame):
        cols = set(df.columns)
        if not self.cols.issubset(cols):
            raise ValueError(
                f"Columns appear to be missing. Expected: {self.cols}, got: {cols}"
            )
        assert df.notwo.isin([True, False]).all()

    def __len__(self):
        return len(self.df)
