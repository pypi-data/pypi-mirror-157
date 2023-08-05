import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chembee_datasets.BreastCancer import BreastCancerDataset
from chembee_actions.evaluation import screen_classifier_for_metrics
from chembee_plotting.evaluation import plot_collection


def test_roc_screen():

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
