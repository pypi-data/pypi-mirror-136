import pandas as pd


def get_correlated_features(X, threshold, consider_sign=False):
    """Calculates correlation between all feature pairs in the input data.
    Returns feature pairs having correlation higher than the threshold value.

    Parameters
    ----------
    X : pandas.DataFrame
        numeric feature set used for EDA analysis
    threshold : float
        threshold for correlation above which feature pairs will be returned
    consider_sign : boolean (optional)
        determines whether correlation value has to be checked for magnitude
        only or for sign (positive/ negative) also. Default checks only the magnitude.

    Returns
    -------
    pandas.DataFrame
       dataframe containing feature1, feature2, and corresponding correlation.

    Examples
    -------
    >>> import pandas as pd
    >>> X = pd.DataFrame({"age": [23, 13, 7, 45],
                          "height": [1.65, 1.23, 0.96, 1.55],
                          "income": [20, 120, 120, 25]})
    >>> get_correlated_features(X, threshold=0.7)
    """
    if not isinstance(X, pd.DataFrame):
        raise TypeError("Feature set (X) should be of pandas dataframe type!")

    if not isinstance(threshold, float):
        raise TypeError("Threshold value should be a floating point number!")

    features = list(X.columns)
    correlated_feat = pd.DataFrame(columns=["feature-1", "feature-2", "correlation"])

    for feat_1 in features:
        for feat_2 in features:
            corr_val = round(X[feat_1].corr(X[feat_2]), 2)
            if consider_sign is False:
                corr_val_abs = abs(corr_val)
            else:
                corr_val_abs = corr_val
            if feat_1 != feat_2 and corr_val_abs >= threshold:
                corr_element = pd.DataFrame(data=[[feat_1, feat_2, corr_val]],
                                            columns=["feature-1", "feature-2", "correlation"])
                correlated_feat = correlated_feat.append(corr_element)

    return correlated_feat