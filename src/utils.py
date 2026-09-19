"""
GulfMart Retail Inventory Analytics
------------------------------------

General-purpose utility functions shared across the project.
"""

import pandas as pd


def downcast_dtypes(df, verbose=True):
    """
    Downcast numeric columns to the smallest safe dtype.

    Integer columns are downcast using pd.to_numeric's
    integer inference (e.g. int64 -> int32 -> int16 -> int8,
    whichever is the smallest dtype that safely holds every
    value in the column).

    Float columns are downcast the same way for floats
    (float64 -> float32).

    Boolean, object, category, and datetime columns are left
    untouched, since downcasting does not apply to them.

    This does NOT reduce CSV file size, since CSV stores
    every value as plain text regardless of the underlying
    dtype. It reduces in-memory (RAM) usage — useful both
    while writing a large DataFrame to disk, and again after
    reading a CSV back in, since pd.read_csv() re-infers
    dtypes from scratch and will not remember any downcasting
    applied before the file was written.

    Parameters
    ----------
    df : pd.DataFrame
    verbose : bool
        If True, print memory usage before and after.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with downcast dtypes. The original
        DataFrame is not modified.
    """

    df = df.copy()

    start_mem = df.memory_usage(deep=True).sum() / 1024**2

    for column in df.columns:
        column_dtype = df[column].dtype

        if pd.api.types.is_bool_dtype(column_dtype):
            # Booleans are already 1 byte; nothing to downcast.
            continue

        elif pd.api.types.is_integer_dtype(column_dtype):
            df[column] = pd.to_numeric(df[column], downcast="integer")

        elif pd.api.types.is_float_dtype(column_dtype):
            df[column] = pd.to_numeric(df[column], downcast="float")

        # object / category / datetime columns are left as-is.

    end_mem = df.memory_usage(deep=True).sum() / 1024**2

    if verbose:
        reduction_pct = (start_mem - end_mem) / start_mem * 100 if start_mem > 0 else 0

        print(
            f"Memory usage: {start_mem:.2f} MB -> {end_mem:.2f} MB "
            f"({reduction_pct:.1f}% reduction)"
        )

    return df
