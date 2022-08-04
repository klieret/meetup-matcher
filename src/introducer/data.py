import pandas as pd


class People:
    allowed_preference = [2, 3]

    def __init__(self, df: pd.DataFrame):
        self._check_df(df)
        self.df = df

    def _check_df(self, df: pd.DataFrame):
        assert df.columns.tolist() == ["name", "email", "slack", "preference", "fixed"]
        assert df.preference.isin(self.allowed_preference).all()
        assert df.fixed.isin([True, False]).all()

    def __len__(self):
        return len(self.df)

    def n_preference(self, pref):
        assert pref in self.allowed_preference
        return len(self.df.query(f"preference == {pref}"))

    def n_preference_fixed(self, pref=None):
        assert pref in [None, *self.allowed_preference]
        if pref is None:
            return len(self.df.query("fixed == True"))
        return len(self.df.query(f"preference == {pref} & fixed == True"))
