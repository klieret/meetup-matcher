import pandas as pd


class People:
    def __init__(self, df: pd.DataFrame):
        self._check_df(df)
        self.df = df

    def _check_df(self, df: pd.DataFrame):
        assert df.columns.tolist() == ["name", "email", "slack", "notwo"]
        assert df.notwo.isin([True, False]).all()

    def __len__(self):
        return len(self.df)
