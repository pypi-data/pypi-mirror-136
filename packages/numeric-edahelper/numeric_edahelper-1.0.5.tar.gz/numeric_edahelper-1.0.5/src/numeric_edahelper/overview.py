import numpy as np
import pandas as pd

def overview(data, quiet=False):
    """Gives a statistical overview of the input data.
    Returns a `pandas.DataFrame` of descriptive statistical values.
    
    Parameters
    ----------
    data : `pandas.DataFrame`
        Input data to be summarized.
    quiet : `bool`, default 'False'
        Boolean value corresponding to showing output of 
        the function. Used for acquiring variables.
        
    Returns
    -------
    `pandas.DataFrame`
        DataFrame holding all calculated values.

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> overview(dataframe, quiet=False)
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input data must be `pandas.DataFrame` object")

    if not isinstance(quiet, bool):
        raise TypeError('Parameter "quiet" must be of `boolean` type.')

    means = []
    stds = []
    variances = []
    medians = []
    stat_vals = [means, stds, variances, medians]
    stat_names = ['mean_', 'std_', 'var_', 
                 'median_']
    for col in range(len(data.columns)):
        pd.to_numeric(data[data.columns[col]], errors='raise')
        means.append(np.mean(data[data.columns[col]]))
        medians.append(np.median(data[data.columns[col]]))
        stds.append(np.std(data[data.columns[col]]))
        variances.append(np.var(data[data.columns[col]]))

    if quiet:
        for i in range(4):
            globals()[stat_names[i]] = stat_vals[i]
            print("Global variable '{}' created.".format(stat_names[i]))

    else:
        return pd.DataFrame(data = stat_vals,
                        columns=data.columns, index=stat_names)