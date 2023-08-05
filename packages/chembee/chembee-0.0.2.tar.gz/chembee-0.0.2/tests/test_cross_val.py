import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chembee_actions.cross_validation import cross_validation_grid_search
from chembee_datasets.BioDegDataSet import BioDegDataSet
from chembee_actions import cross_validation
from chembee_preparation.processing import calculate_lipinski_desc
from chembee_config.calibration.random_forest import RandomForestClassifier


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
        "precision",
        "recall",
    ]  # need to specify the loss functions for the crosss validation
    DataSet = BioDegDataSet(
        split_ratio=split_ratio, data_set_path="tests/data/Biodeg.sdf", target=target
    )
    data = calculate_lipinski_desc(DataSet.data, DataSet.mols)
    data = DataSet.clean_data(DataSet.data)
    (
        DataSet.X_train,
        DataSet.X_test,
        DataSet.y_train,
        DataSet.y_test,
    ) = DataSet.make_train_test_split(
        data, split_ratio=split_ratio, y_col=target, shuffle=True
    )
    DataSet.data = DataSet.clean_data(DataSet.data)
    clf, report, best_parameters, best_index = cross_validation_grid_search(
        scores,
        RandomForestClassifier,
        DataSet.X_train,
        DataSet.X_test,
        DataSet.y_train,
        DataSet.y_test,
    )
    assert type(report) == type({})
