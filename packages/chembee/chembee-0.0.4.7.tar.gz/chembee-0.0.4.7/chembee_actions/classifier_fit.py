import logging

LOGGER = logging.getLogger(__name__)


def clf_fit(clf, X_train, y_train, name):
    """
    The clf_fit function fits the classifier to the training data.

    :param X_train: Used to Pass the x_train dataset to the clf.
    :param y_train: Used to Fit the model to the training data.
    :param name: Used to Name the classifier.
    :return: The fitted model.

    :doc-author: Trelent
    """

    LOGGER.info("Fitting %s" % (name))
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_train)
    return clf
