import os
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve, auc

from chembee_actions.classifier_fit import clf_fit
from chembee_actions.clf_list import clf_list  # load classifiers

import logging

logging.basicConfig(
    format="%(levelname)s:%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
    filename=os.getenv("chembee.log"),
)


def screen_classifier_for_metrics(
    X_train,
    y_train,
    X_test,
    y_test,
    file_name="evaluation",
    prefix="plots/evaluation",
    clf_list: list = clf_list,
    to_fit=True,
) -> dict:
    """
    The screen_classifier_for_metrics function takes a list of classifiers and fits them to the training data.
    It then predicts the test data using each classifier, calculates metrics for each prediction, and stores all
    of this information in a dictionary. The function returns this dictionary.

    :param clf:list=clf_list: Used to Pass the classifiers to be evaluated.
    :param X_train: Used to Pass the training data set.
    :param y_train: Used to Train the classifier.
    :param name: Used to Create a folder where the plots will be stored.
    :param X_test: Used to Test the classifier on a set of data.
    :param y_test: Used to Calculate the metrics.
    :param file_name="evaluation": Used to Specify the name of the file where all metrics will be saved.
    :param prefix="plots/evaluation": Used to Set the path where the plots will be saved.
    :return: A dictionary of metrics for each classifier.

    :doc-author: Trelent
    """

    fitted_classifier = []
    metrics_collection = {}
    metrics_collection["scalar"] = {}
    metrics_collection["array"] = {}
    metrics_collection["matrix"] = {}

    for i in range(len(clf_list)):
        clf = clf_list[i]
        name = clf.name
        if to_fit:
            clf = clf_fit(clf, X_train, y_train, name)
        y_pred = clf.predict(X_test)
        fitted_classifier.append(clf)
        metric_scalar, metric_array, metric_matrix = calculate_metrics_classifier(
            clf, X_test, y_test, y_pred
        )
        metrics_collection["scalar"][clf.name] = metric_scalar
        metrics_collection["array"][clf.name] = metric_array
        metrics_collection["matrix"][clf.name] = metric_matrix

    return metrics_collection


def calculate_metrics_classifier(clf, X_test, y_test, y_pred):
    """
    The calculate_metrics_classifier function calculates the accuracy, average precision, precision and recall of a classifier.
    It takes as input two lists: y_test and y_pred. The function returns a dictionary with four keys: 'accuracy', 'average_precision',
    'precision' and 'recall'. Each key contains the corresponding value for each metric.

    :param y_test: Used to define the true labels of the test data.
    :param y_pred: Used to Calculate the metrics.
    :return: A dictionary with the following keys: accuracy, avgerage_preciscion, precision, and roc_auc.

    :doc-author: Julian M. Kleber
    """
    cf_matrix = confusion_matrix(y_test, y_pred)
    true_neg, false_pos, false_neg, true_pos = cf_matrix.ravel()
    acc = calculate_metric(y_test, y_pred, accuracy_score)
    prec = precision(true_pos, false_pos)
    rec = recall(true_pos, false_neg)
    spec = specificity(true_neg, false_pos)
    f_sc = f_score(prec, rec)
    fpr, tpr, thresholds = calculate_roc_curve(clf, X_test, y_test)
    auc_score = auc(1 - fpr, 1 - tpr)
    logging.info("Calculated metrics for %s" % clf.name)
    result_scalar = make_result(
        accuracy=acc,
        precision=prec,
        recall=rec,
        specificity=spec,
        f_score=f_sc,
    )
    result_array = make_result(
        fpr=fpr,
        tpr=tpr,
        roc_auc=auc_score,  # not an array but necessary for roc-auc plot
        thresholds=thresholds,
    )
    result_matrix = make_result(confusion_matrix=cf_matrix)
    return result_scalar, result_array, result_matrix


def calculate_metric(y_test, y_pred, metric):
    """
    The calculate_metric function takes as input the true labels and predicted labels
    and returns the specified metric. The available metrics are: accuracy, precision, recall, fscore.

    :param y_test: Used to Pass the actual values of y.
    :param y_pred: Used to Calculate the metric.
    :param metric: Used to Specify the function that should be used to calculate the metric.
    :return: The result of the metric function.

    :doc-author: Trelent
    """

    try:
        res = metric(y_test, y_pred)
    except:
        res = None
    return res


def make_result(**kwargs):
    """
    The make_result function takes in the accuracy, average precision, precision and roc_auc score of a model.
    It then returns a dictionary with these four values.

    :param acc: Used to Store the accuracy of the model.
    :param avg_prec: Used to Store the average precision score of the model.
    :param prec: Used to Store the precision for each class.
    :param rac: Used to Calculate the area under the curve.
    :return: A dictionary with four keys: accuracy, avgerage_preciscion, precision, and roc_auc.

    :doc-author: Trelent
    """
    return kwargs


def calculate_roc_curve(classifier, X_test, y_test):
    """
    The calculate_roc_curve function calculates the false positive rate and true positive rate for a given classifier.
    It returns these values as numpy arrays.

    :param classifier: Used to Pass the classifier object.
    :param X_test: Used to Test the model.
    :param y_test: Used to Calculate the true positive rate and false positive rate.
    :return: The false positive rate, true positive rate and thresholds.

    :doc-author: Trelent
    """

    probs = classifier.predict_proba(X_test)
    # Reading probabilities of the first class can extend it to all classes.
    probs = probs[:, 0]
    fpr, tpr, thresholds = roc_curve(y_test, probs)
    return fpr, tpr, thresholds


def precision(true_pos, false_pos):

    """
    The precision function takes two parameters: true_pos and false_pos.
    It returns the precision of the classifier, which is defined as
    the ratio of true positives (true_pos) to the sum of true positives and false positives (true_pos + false_pos).

    :param true_pos: Used to Calculate the precision.
    :param false_pos: Used to Calculate the precision.
    :return: A value between 0 and 1.

    :doc-author: Trelent
    """

    return true_pos / (true_pos + false_pos)


def recall(true_pos, false_neg):

    """
    The recall function takes two inputs: true positives and false negatives.
    It returns the recall of those values as a percentage.

    :param true_pos: Used to Calculate the recall.
    :param false_neg: Used to Calculate the recall.
    :return: The ratio of true positives to the sum of true positives and false negatives.

    :doc-author: Trelent
    """

    return true_pos / (true_pos + false_neg)


def specificity(true_neg, false_pos):

    """
    The specificity function takes in the number of true negatives and false positives,
    and returns the specificity score for a given classifier

    :param true_neg: Used to Calculate the specificity.
    :param false_pos: Used to Calculate the specificity.
    :return: The proportion of negatives that are correctly identified as such (e.

    :doc-author: Trelent
    """

    return true_neg / (true_neg + false_pos)


def f_score(precision, recall):
    """
    The f_score function computes the harmonic mean of precision and recall.

    Args:
        precision (float): The number of true positives divided by all positive predictions.

        recall (float): The number of true positives divided by the number of positive values in the dataset.

    Returns:
        float: The f_score or accuracy for this prediction and target value, given as a floating point value between 0 and 1.

    :param precision: Used to Control the number of false positives.
    :param recall: Used to Avoid false positives.
    :return: The f_score of the precision and recall.

    :doc-author: Trelent
    """

    return 2 * (precision * recall) / (precision + recall)
