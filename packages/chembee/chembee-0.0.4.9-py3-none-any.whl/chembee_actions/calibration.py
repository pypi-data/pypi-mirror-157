##Calibration for binary classification
import sys, os, logging
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.calibration import CalibrationDisplay

# own modules

from chembee_actions.classifier_fit import clf_fit
from chembee_actions.clf_list import clf_list

from chembee_plotting.calibration import plot_calibration


logging.basicConfig(
    format="%(levelname)s:%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
    filename=os.getenv("LOGFILE"),
)


def screen_calibration(
    X_train,
    X_test,
    y_train,
    y_test,
    clf_list=clf_list,
    grid=(6, 2),
    file_name="calibration",
    prefix="plots/benchmarks",
):
    """clf_fit(X_train, y_train, name
    The screen_calibration function takes in a training and test set, as well as
    the name of the output file. It then plots calibration curves for each model
    in the list of models. The function returns nothing.

    :param X_train: Used to Provide the training data for the calibration algorithm.
    :param X_test: Used to Plot the test data.
    :param y_train: Used to Pass the labels of the training data.
    :param y_test: Used to Store the true values of the test set.
    :param out_name="benchmark": Used to Name the output file.
    :param prefix="plots/benchmarks": Used to Specify the location where all plots will be saved.
    :return: A dictionary with the following keys:.

    :doc-author: Trelent
    """
    fig = plt.figure(figsize=(30, 30))
    grid_spec = GridSpec(grid[0], grid[1])

    colors = plt.cm.get_cmap("Dark2")
    ax_calibration_curve = fig.add_subplot(grid_spec[:2, :2])

    ax_calibration_curve.grid()
    ax_calibration_curve.set_title("Calibration plots")

    calibration_displays = get_calibration_displays(
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        clf_list=clf_list,
        ax_calibration_curve=ax_calibration_curve,
        colors=colors,
    )
    plot_calibration(
        fig=fig,
        clf_list=clf_list,
        grid=grid,
        grid_spec=grid_spec,
        colors=colors,
        ax_calibration_curve=ax_calibration_curve,
        calibration_displays=calibration_displays,
        file_name=file_name,
        prefix=prefix,
    )


def get_calibration_displays(
    X_train, y_train, X_test, y_test, colors, clf_list: list, ax_calibration_curve
) -> dict:

    """
    The get_calibration_displays function fits a list of classifiers to the training data and plots calibration
    curves for each one. The function takes no arguments, but it does require that the X_train, y_train, X_test
    and y_test variables be defined in the global namespace. It returns nothing.

    :return: A dictionary of calibration displays.

    :doc-author: Julian M. Kleber
    """

    calibration_displays = {}
    fitted_classifier = []
    for i, (clf, name) in enumerate(clf_list):
        clf = clf_fit(clf, X_train, y_train, name)
        display = CalibrationDisplay.from_estimator(
            clf,
            X_test,
            y_test,
            n_bins=100,
            name=name,
            ax=ax_calibration_curve,
            color=colors(i),
        )
        calibration_displays[name] = display

    return calibration_displays
