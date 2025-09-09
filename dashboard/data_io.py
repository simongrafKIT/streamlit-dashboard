import pandas as pd
from dashboard.constants import SHEET_NAME_1, SHEET_NAME_2

def load_data(file_obj):
    """Read required sheets and minimal columns; add LEVEL afterwards."""
    df1 = pd.read_excel(file_obj, sheet_name=SHEET_NAME_1, usecols="C:J", skiprows=2).copy().sort_values(by="NUMBER | 编号").reset_index(drop=True)
    df1["LEVEL"] = ((df1.index % 4) + 1)
    df3 = pd.read_excel(file_obj, sheet_name=SHEET_NAME_2, usecols="C:N", skiprows=1).copy()
    return df1, df3
