# want to do with ROC check: https://scikit-learn.org/stable/auto_examples/model_selection/plot_roc_crossval.html#sphx-glr-auto-examples-model-selection-plot-roc-crossval-py
# making own scoring: https://scikit-learn.org/stable/modules/cross_validation.html
# Want to do Stratified k-fold
from sklearn.model_selection import GridSearchCV

# algorithm

# cross validation parameters
import logging


logging.basicConfig(
    format="%(levelname)s:%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
    filename="chembee_actions.log",
)


def cross_validation_grid_search(scores: list, clf, X_train, X_test, y_train, y_test):

    # is property of algorithm

    for score in scores:

        clf = GridSearchCV(
            clf, clf.hyperparameters, scoring="%s_macro" % score, n_jobs=-1
        )
        clf.fit(X_train, y_train)
        y_true, y_pred = y_test, clf.predict(X_test)

        return clf, clf.cv_results_, clf.best_params_, clf.best_index_
