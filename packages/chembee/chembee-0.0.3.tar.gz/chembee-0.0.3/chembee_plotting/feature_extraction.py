import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from file_utils import insert_string_in_file_name, prepare_file_name_saving


def plot_feature_importances(result_json: dict, file_name: str, prefix: str):
    """
    The plot_feature_importances function plots the feature importances of a random forest model.
    It takes three arguments:
        - forest_importances: The feature importances from the random forest model, as returned by sklearn's .feature_importance() method.
        - std: The standard deviation of the feature importances, as returned by sklearn's .std() method on a RandomForestRegressor or RandomForestClassifier object.  This is used to plot error bars for each importance value.  If no standard deviation is available (i.e., if you are using a DecisionTreeRegressor or DecisionTreeClassifier), set this to None (the default).
        - file_name: A string containing the name of your desired output file (e.g., "FeatureImportancePlot" will result in "FeatureImportancePlotRFModelNameHere").

    :param forest_importances: Used to pass the feature importances to the function.
    :param std: Used to plot the standard deviation of the feature importances.
    :param file_name:std: Used to pass the file name of the plot to be saved.
    :param prefix:std: Used to specify the prefix for the file name.
    :return: The feature importances of the forest.

    :doc-author: Trelent
    """
    importances = result_json["importances"]
    feature_indices = result_json["feature_indices"]
    std = result_json["std"]
    forest_importances = pd.Series(importances, index=feature_indices)
    file_name = insert_string_in_file_name(
        file_name, insertion="FeatureImportancesRF", ending=".png"
    )
    file_name = prepare_file_name_saving(
        prefix=prefix, file_name=file_name, ending=".png"
    )
    fig, ax = plt.subplots()
    forest_importances.plot.bar(yerr=std, ax=ax)
    ax.set_xlabel("Feature No.")
    ax.set_ylabel("Mean decrease in impurity")
    fig.tight_layout()
    fig.savefig(file_name, dpi=300)
