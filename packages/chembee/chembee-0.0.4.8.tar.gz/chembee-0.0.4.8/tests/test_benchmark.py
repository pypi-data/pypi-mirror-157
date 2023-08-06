import sys, os
from sklearn import datasets

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import prepare_data_decicion_lib
from chembee_actions.benchmark_algorithms import benchmark_standard
from chembee_actions.cross_validation import screen_cross_validation_grid_search

from chembee_config.calibration.random_forest import RandomForestClassifier
from chembee_config.calibration.knn import KNNClassifier
from chembee_config.benchmark.grid_search_cv import GridSearchCVClassifier

from chembee_datasets.IrisDataSet import IrisDataSet


def test_benchmarking():

    # Data Definition
    DataSet = IrisDataSet(split_ratio=0.8)
    # Grid search
    scores = ["precision_macro", "recall_macro", "accuracy"]
    names = ["rf", "knn"]
    clf_list = [KNNClassifier, RandomForestClassifier]

    fitted_clf, result_clf = screen_cross_validation_grid_search(
        scores=scores,
        clf_list=clf_list,
        X_train=DataSet.X_train,
        X_test=DataSet.X_test,
        y_train=DataSet.y_train,
        y_test=DataSet.y_test,
        refit="accuracy",
    )

    GridSearchCV = GridSearchCVClassifier(clf_list, names)
    iris = datasets.load_iris()
    X, y = prepare_data_decicion_lib(iris)
    benchmark_standard(
        X,
        y,
        feature_names=iris.feature_names[:2],
        algorithms=[GridSearchCV],
        to_fit=False,
    )

    # Standard screen

    benchmark_standard(
        X,
        y,
        feature_names=iris.feature_names[:2],
    )
