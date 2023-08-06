import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chembee_datasets.BreastCancer import BreastCancerDataset
from chembee_actions.evaluation import screen_classifier_for_metrics
from chembee_plotting.evaluation import plot_collection

from chembee_config.calibration.random_forest import RandomForestClassifier
from chembee_config.calibration.knn import KNNClassifier
from chembee_config.calibration.mlp_classifier import NeuralNetworkClassifierRELU
from chembee_config.calibration.svc import NaivelyCalibratedSVCRBF


def test_screen_classifier_for_metrics():

    DataSet = BreastCancerDataset(split_ratio=0.8)
    metrics = screen_classifier_for_metrics(
        X_train=DataSet.X_train,
        X_test=DataSet.X_test,
        y_train=DataSet.y_train,
        y_test=DataSet.y_test,
    )
    assert ["scalar", "array", "matrix"] == list(metrics.keys())
    plot_collection(
        metrics, file_name=DataSet.name + "_evaluation", prefix="plots/evaluation"
    )
    # Test for fitted classifiers
    clf_list = [
        RandomForestClassifier,
        KNNClassifier,
        NeuralNetworkClassifierRELU,
        NaivelyCalibratedSVCRBF,
    ]
    clf_result = []
    for clf in clf_list:
        clf.fit(DataSet.X_train, DataSet.y_train)
        clf_result.append(clf)
    metrics = screen_classifier_for_metrics(
        X_train=DataSet.X_train,
        X_test=DataSet.X_test,
        y_train=DataSet.y_train,
        y_test=DataSet.y_test,
        clf_list=clf_list,
    )
    assert ["scalar", "array", "matrix"] == list(metrics.keys())
