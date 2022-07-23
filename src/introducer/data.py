import pandas as pd


class People:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    def __len__(self):
        return len(self._df)

    def n_preference(self, pref):
        assert pref in [1, 2]
        return len(self._df.query(f"preference == {pref}"))

    def n_preference_fixed(self, pref=None):
        assert pref in [None, 1, 2]
        if pref is None:
            return len(self._df.query("fixed == True"))
        return len(self._df.query(f"preference == {pref} & fixed == True"))
