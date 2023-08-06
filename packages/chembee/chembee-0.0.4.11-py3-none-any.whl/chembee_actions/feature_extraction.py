# want to do the random forest extraction and give out the features as JSON
from sklearn.ensemble import RandomForestClassifier
import numpy as np


def filter_importance_by_std(result_json, cut_off=0.01):
    """
    The filter_importance_by_std function takes a JSON object containing feature names, indices, importances and standard deviations
    and filters out features with low importance. The cut_off parameter is used to determine the minimum importance level for a feature
    to be included in the output. For example, if cut_off = 0.01 then only features with an importance greater than 1% will be included
    in the output.

    :param result_json: Used to pass the result of a sklearn.
    :param cut_off=0.01: Used to filter out the features with low importance.
    :return: A dictionary with the following keys:.

    :doc-author: Julian M. Kleber
    """
    feature_names = np.array(result_json["feature_names"])
    feature_indices = np.array(result_json["feature_indices"])
    importances = np.array(result_json["importances"])
    std = np.array(result_json["std"])
    indices = std > cut_off
    result_json = {
        "feature_names": feature_names[indices].tolist(),
        "feature_indices": feature_indices[indices].tolist(),
        "importances": importances[indices].tolist(),
        "std": std[indices].tolist(),
    }
    return result_json


def get_feature_importances(
    X_data: np.ndarray, y_data: np.ndarray, feature_names: list
) -> dict:
    """
    The get_feature_importances function accepts three arguments:
        1. X_data - a numpy array of the features in the dataset
        2. y_data - a numpy array of the labels in the dataset
        3. feature_names - an optional list containing names for each feature

    The function returns a dictionary with two keys:
        1) "feature_names" which contains all of the feature names passed to this function, and
        2) "importances", which is another dictionary where each key is a column name from X data, and its value is that column's importance as determined by sklearn's RandomForestClassifier algorithm.

    :param X_data:np.ndarray: Used to Pass the data.
    :param y_data:np.ndarray: Used to Pass the target variable.
    :param feature_names:list: Used to Get the names of the features.
    :return: A dictionary with the following keys:.

    :doc-author: Trelent
    """
    assert type(X_data) == type(np.zeros((1, 1))) and type(y_data) == type(
        np.zeros((1, 1))
    )

    # Split the dataset in two equal parts

    feature_indices = np.linspace(1, X_data.shape[1], X_data.shape[1]).astype(np.int32)
    forest = RandomForestClassifier(random_state=0)  # algorithm
    forest.fit(X_data, y_data)
    importances = forest.feature_importances_
    std = np.std([tree.feature_importances_ for tree in forest.estimators_], axis=0)
    result_json = {
        "feature_names": feature_names,
        "feature_indices": feature_indices.tolist(),
        "importances": importances.tolist(),
        "std": std.tolist(),
    }
    return result_json
