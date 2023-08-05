import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from math import pi

from sklearn.inspection import DecisionBoundaryDisplay
from file_utils import prepare_file_name_saving

# set the standard parameters

plt.rcParams["font.size"] = "20"
plt.tight_layout()


def plot_comparison_4(
    models,
    titles,
    X,
    y,
    prefix=None,
    file_name="SVC_benchmark",
    feature_names=["Feature 1", "Feature 2"],
    response_method="predict",
):
    """
    The plot_comparision_4 function plots the decision boundaries for a set of models.
    It takes as input:
    - models: A list of scikit learn model objects.  Each model object must have a .predict method that takes in an array of features and returns predictions based on those features.  The plot_comparision_4 function uses these predictions to create the decision boundary for each model, and then plots them together in a single figure.
    - titles: A list with one element for each element in 'models'.  Each string is used to label the corresponding plot's legend, so make sure that they are unique!
    - X: An array containing feature values used to train/evaluate the models passed via 'models'.   These feature values should be scaled between 0 and 1 (if not already done).   The first two columns should correspond to x coordinates while the second two columns should correspond to y coordinates (i.e., this is an Nx4 matrix).  This argument corresponds directly with what you would pass into plt.scatter(...), so if you have already scaled your data, then just pass it here without re-scaling it!
    - y: An array containing labels corresponding with observations contained within X (i.e., this

    :param models: Used to Pass a list of models that should be compared.
    :param titles: Used to Give a name to each model in the plot.
    :param X: Used to Define the data that will be used for training and testing.
    :param y: Used to Define the target variable.
    :param prefix=None: Used to Define a string that will be added to the name of the file when it is saved.
    :param file_name="SVC_benchmark": Used to Save the plot as an image.
    :param feature_names=["Feature1": Used to Specify the labels for the x and y axis.
    :param "Feature2"]: Used to Specify which feature is used for the x-axis.
    :return: The subplot of the models.

    :doc-author: Trelent
    """

    fig, sub = plt.subplots(2, 2, figsize=(20, 13))
    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    make_comparison_plot(
        fig=fig,
        sub=sub,
        models=models,
        titles=titles,
        X=X,
        y=y,
        file_name=file_name,
        feature_names=feature_names,
        prefix=prefix,
        response_method=response_method,
    )


def plot_comparison_3(
    models,
    titles,
    X,
    y,
    prefix=None,
    file_name="SVC_benchmark",
    feature_names=["Feature 1", "Feature 2"],
    response_method="predict",
):
    fig, sub = plt.subplots(1, 3, figsize=(20, 13))
    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    make_comparison_plot(
        fig=fig,
        sub=sub,
        models=models,
        titles=titles,
        X=X,
        y=y,
        file_name=file_name,
        feature_names=feature_names,
        prefix=prefix,
        response_method=response_method,
    )


def plot_comparison_2():
    pass


def plot_comparison_1():
    pass


def make_comparison_plot(
    fig,
    sub,
    models,
    titles,
    X,
    y,
    prefix=None,
    file_name="SVC_benchmark",
    feature_names=["Feature 1", "Feature 2"],
    response_method="predict",
):
    """
    The make_comparison_plot function creates a plot comparing the decision boundaries of several models.
    It takes as input:
        - fig, a matplotlib figure object to be saved to file (figsize=(12,8))
        - sub, an array of axes objects on which plotting will occur (nrows=2, ncols=3)
        - models: an array of sklearn classifiers for which decision boundaries will be plotted.
            Note that these must have been fitted already with fit()!

        The function then creates plots comparing the decision boundary and prediction values for each model in turn.

        It returns nothing.

    :param fig: Used to Pass the figure object to which we want to plot.
    :param sub: Used to Create a subplot grid.
    :param models: Used to Pass the classifiers that will be used in the plot.
    :param titles: Used to Set the title of each subplot.
    :param X: Used to Pass the data to be plotted.
    :param y: Used to Specify the response variable.
    :param prefix=None: Used to Make sure that the file_name is saved in the current working directory.
    :param file_name="SVC_benchmark": Used to Create a file_name for the plot.
    :param feature_names=["Feature1": Used to Label the axes of the plot.
    :param "Feature2"]: Used to Specify the name of the x and y axis.
    :return: A plot of the decision boundaries for a set of classifiers.

    :doc-author: Trelent
    """

    X0, X1 = X[:, 0], X[:, 1]

    for clf, title, ax in zip(models, titles, sub.flatten()):
        disp = DecisionBoundaryDisplay.from_estimator(
            clf,
            X,
            response_method=response_method,
            cmap=plt.cm.coolwarm,
            alpha=0.7,
            ax=ax,
            xlabel=feature_names[0],
            ylabel=feature_names[1],
        )
        ax.scatter(X0, X1, c=y, cmap=plt.cm.coolwarm, s=20, edgecolors="k")
        ax.set_xticks(())
        ax.set_yticks(())
        ax.set_title(title)

    file_name = prepare_file_name_saving(
        prefix=prefix, file_name=file_name, ending=".png"
    )
    fig.savefig(file_name)


def plot_feature_importances():
    """ """


def save_fig(ax, name: str, save_path=None, dpi=300):
    """Frequently used snippet to save a plot

    Args:
        ax ([type]): Seaborn axis
        name (str): Name of the plot
        save_path ([type], optional): Where to save the plot. Defaults to None:str.
        dpi (int, optional): Resolution of the plot. Defaults to 300.

    Returns:
        (None)
    """
    if save_path is None:
        save_path = name
    else:
        save_path.joinpath(name)
    fig = ax.get_figure()
    fig.savefig(save_path, dpi=dpi)
    return None


plotting_map_comparison = {
    1: plot_comparison_1,
    2: plot_comparison_2,
    3: plot_comparison_3,
    4: plot_comparison_4,
}
if __name__ == "__main__":

    data = pd.read_csv("converted_data.csv")
    biodeg = data[data["ReadyBiodegradability"] == 1]
    n_biodeg = data[data["ReadyBiodegradability"] == 0]
    polar_plot(biodeg, name="BiodegPolar.png")
    polar_plot(n_biodeg, name="NBiodegPolar.png")
