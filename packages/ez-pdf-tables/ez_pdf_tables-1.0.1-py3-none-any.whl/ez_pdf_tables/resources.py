import pandas as pd
from typing import Any


# Convert a value to text
def as_text(value: Any, remove_decimal: bool = False) -> str:
    if value is None:
        return ""
    if remove_decimal:
        value = str(value).split('.')[0]
    return str(value)

# Convert specified df columns to text
def df_columns_to_text(
    df: pd.DataFrame,
    column_list: list,
    remove_decimal: bool = False
) -> pd.DataFrame:
    for column_name in column_list:
        # Fill NaN values with a space to prevent NaN being made into text
        df[column_name].fillna(' ', inplace=True)
        df[column_name] = df.apply(
            lambda row: as_text(
                row[column_name],
                remove_decimal=remove_decimal
            ),
            axis=1
        )
    return df
