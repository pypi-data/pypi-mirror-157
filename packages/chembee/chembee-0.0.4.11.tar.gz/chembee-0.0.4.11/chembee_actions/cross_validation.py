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


def screen_cross_validation_grid_search(
    scores, clf_list, X_train, X_test, y_train, y_test, refit
):

    fitted_clf = {}
    result_clf = []
    for alg in clf_list:
        logging.info("Performing Grid search CV for" + str(alg.name))
        clf, report, best_parameters, best_index = cross_validation_grid_search(
            scores, alg, X_train, X_test, y_train, y_test, refit=refit
        )
        result = {
            "report": report,
            "best_parameters": best_parameters,
            "best_index": best_index,
        }
        fitted_clf[alg.name] = result
        result_clf.append(clf)
    return fitted_clf, result_clf


def cross_validation_grid_search(
    scores: list, clf, X_train, X_test, y_train, y_test, refit
):

    # is property of algorithm

    clf = GridSearchCV(clf, clf.hyperparameters, scoring=scores, n_jobs=-1, refit=refit)
    clf.fit(X_train, y_train)

    return clf, clf.cv_results_, clf.best_params_, clf.best_index_
