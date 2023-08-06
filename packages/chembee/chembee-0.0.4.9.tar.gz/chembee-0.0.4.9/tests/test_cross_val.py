import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chembee_actions.cross_validation import (
    screen_cross_validation_grid_search,
)
from chembee_datasets.BioDegDataSet import BioDegDataSet
from chembee_preparation.processing import calculate_lipinski_desc
from chembee_config.calibration.random_forest import RandomForestClassifier
from chembee_config.calibration.knn import KNNClassifier


def test_cross_validation():

    """
    The benchmark tests cross validation on the random forest classifier based on
    parameters defined in the configuration file of the algorithm
    """

    file_name = "test"
    prefix = "tests/plots"
    target = "ReadyBiodegradability"
    split_ratio = 0.7
    scores = [
        "precision_macro",
        "recall_macro",
        "accuracy",
    ]  # need to specify the loss functions for the crosss validation
    DataSet = BioDegDataSet(
        split_ratio=split_ratio, data_set_path="tests/data/Biodeg.sdf", target=target
    )
    data = calculate_lipinski_desc(DataSet.data, DataSet.mols)
    data = DataSet.clean_data(data)
    (
        DataSet.X_train,
        DataSet.X_test,
        DataSet.y_train,
        DataSet.y_test,
    ) = DataSet.make_train_test_split(
        data, split_ratio=split_ratio, y_col=target, shuffle=True
    )
    DataSet.data = DataSet.clean_data(DataSet.data)
    names = ["rf", "knn", "NeuralNetworkClassifier", "NaivelyCalibratedSVCRBF"]
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
