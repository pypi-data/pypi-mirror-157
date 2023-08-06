import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chembee_datasets.BreastCancer import BreastCancerDataset
from chembee_actions.calibration import screen_calibration


def test_calibration():

    DataSet = BreastCancerDataset(split_ratio=0.8)
    screen_calibration(
        DataSet.X_train,
        DataSet.X_test,
        DataSet.y_train,
        DataSet.y_test,
        file_name="breast_cancer_calibration",
        prefix="plots/calibration",
    )
