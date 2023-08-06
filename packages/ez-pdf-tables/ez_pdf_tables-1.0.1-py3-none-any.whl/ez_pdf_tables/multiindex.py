import os
import pandas as pd
from typing import Union
from .tables import df_columns_to_text


# Updates index on a dataframe to multiple
def _make_multiindex(
    df: pd.DataFrame,
    indices: list
) -> pd.DataFrame:
    if not isinstance(indices, list) or len(indices) == 0:
        raise ValueError('Indices must be a non-empty list.')
    df.set_index(indices, inplace=True)
    df.sort_index(inplace=True)
    return df

'''
    Set a multiindex df to be printable exactly as it looks,
    with empty values below top value such that the console printable
    multiindex is exportable to file.
'''
def multiindex_as_is(
    source: Union[str, pd.DataFrame],
    make_multiindex_with_indices: list
) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        df = source
        if isinstance(df.index, pd.MultiIndex):
            msg = (
                'The dataframe already contains a multiindex, this would truncate'
                ' additional indices. Pass the dataframe with a single index and'
                ' supply the multiindex values to "make_multiindex_with_indices".'
            )
            raise ValueError(msg)
    elif os.path.isfile(os.path.abspath(source)):
        df = pd.read_csv(source)
    else:
        raise ValueError('Source must be a dataframe object or csv file path.')
    mdf_dict = df.to_dict('list')
    # Headers
    mdf_keys = list(mdf_dict.keys())
    # Column values
    mdf_vals = list(mdf_dict.values())
    # Starting position is 0 for column lengths
    column_lengths = [0,] #len(str(len(mdf_vals[0]) + 1)), ]
    # Insert header into beginning of each column list
    for i, j in enumerate(mdf_vals):
        j.insert(0, mdf_keys[i])
    # loop through the list of columns
    for i, column in enumerate(mdf_vals):
        # Set initial length for each list to 0
        length = 0
        for cell in column:
            # If the length of the current item in the list is
            # longer, update the max length
            if len(str(cell)) > length:
                length = len(str(cell))
        # Set the pad to account for spaces in df str
        if i == 0:
            pad = 0
        else:
            pad = 1
        length += column_lengths[-1] + pad
        column_lengths.append(length)
    # Increase the final column length by an additional 1
    column_lengths[-1] = column_lengths[-1] + 1
    # Convert the df to multiindex
    df = _make_multiindex(df, make_multiindex_with_indices)
    # Convert all columns to text to prevent spacing issues
    df = df_columns_to_text(df, df.columns.tolist())
    mdf_str_list = str(df).split('\n')
    # Delete non-indexed header and indexed header
    mdf_str_list.pop(1)
    mdf_str_list.pop(0)
    # Cut each row into cells based on the 2 bounds it is within
    for i, v in enumerate(mdf_str_list):
        mdf_str_list[i] = [
            v[j:k] for j, k in zip(column_lengths, column_lengths[1:])
        ]
    # Pass the header (mdf_keys) to df
    return pd.DataFrame(mdf_str_list, columns=mdf_keys)
