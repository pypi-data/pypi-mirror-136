import pandas as pd
import numpy as np

def flag_outliers(df, threshold=0.2):
    """Takes a dataframe and returns numeric variables (column names) containing outliers exceeding
    user-specified threshold, as well as their respective percentage of outliers as defind by IQR

    Parameters
    ----------
    df : pandas.DataFrame
        dataset used for EDA analysis
    threshold : float (optional)
        minimum percentage threshold for the proportion of outliers, above which will have variables flagged

    Returns
    -------
    dict
       a dictionary containing the name of variables with high outliers and its respective percentage of outliers 
    
    Examples
    -------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'col1': [-100,-200, 1,2,3,4,5,6,7,8,9,10, 1000], 
                   'col2': [1,2,3,4,5,6,7,8,9,10,11,12,13],
                   'col3': [-50, 1,2,3,4,5,6,7,8,9,10,11,50000]})
    >>> flag_outliers(df, threshold=0.2)
    {'col1': 0.23076923076923078} 
    """

    if not isinstance(df, pd.DataFrame): 
        raise TypeError("Input parameter should be of pandas dataframe type!")

    if not isinstance(threshold, float): 
        raise TypeError("Threshold should be a floating point number!")

    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3-Q1
    lower = Q1 - (1.5 * IQR)
    upper = Q3 + (1.5 * IQR)

    props = df[(df<lower) | (df>upper)].count()/len(df)
    props = props.to_dict()

    results = { key:value for (key,value) in props.items() if value > threshold}
    return results
    