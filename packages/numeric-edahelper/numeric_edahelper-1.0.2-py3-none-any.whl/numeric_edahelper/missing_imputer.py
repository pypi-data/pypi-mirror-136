import pandas as pd
import numpy as np


def missing_imputer(data, method="mean"):

    """
    Impute the missing values using the method selected
    
    Parameters
    ----------
    data : pandas.DataFrame
        A Pandas Dataframe for which the missing values need to be replaced or dropped
    method : str, default = "mean"
        The method used for imputing numerical missing values
        Options: "drop", "mean", "median"
    
    Returns
    -------
    pandas.DataFrame
        An imputed dataframe
    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> from numeric_edahelper.missing_imputer import missing_imputer
    >>> df = pd.DataFrame({'a':[1,2,np.nan],'b':[np.nan,1,0]})
    >>> missing_imputer(df, method="median")
         a	    b
    0	1.0	   0.5
    1	2.0    1.0
    2   1.5    0.0
    """
    # check if data type is pd.DataFrame
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Data type is not pandas.DataFrame")
    
    # check if all the dataframe elements are numeric
    if not data.shape[1] == data.select_dtypes(include=np.number).shape[1]:
        raise TypeError("Some of the columns in the data are not numeric")
    
    # check if method is one of the options
    if method not in ["drop", "mean", "median"]:
        raise ValueError("method should be one of the options: 'drop', 'mean', 'median'")
    
    df = data.copy()

    if method == "drop":
        df = df.dropna(axis=0)
    elif method == "mean":
        for col in df.columns:
            df[col] = df[col].replace(np.nan, df[col].mean())
    else:
        for col in df.columns:
            df[col] = df[col].replace(np.nan, df[col].median())
    
    return df.reset_index(drop=True)