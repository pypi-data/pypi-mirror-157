import sys, os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from chembee_config.benchmark.svc import SVClassifier
from chembee_config.benchmark.svc_poly import SVCPolyClassifier
from chembee_config.benchmark.spectral_clustering import SpectralClusteringClassifier
from chembee_config.benchmark.random_forest import RandomForestClassifier
from chembee_config.benchmark.naive_bayes import NaiveBayesClassifier
from chembee_config.benchmark.logistic_regression import LogisticRegressionClassifier
from chembee_config.benchmark.linear_regression import LinearRegressionClassifier
from chembee_config.benchmark.kmeans import KMeansClassifier
from chembee_config.benchmark.knn import KNNClassifier
from chembee_config.benchmark.mlp_classifier import NeuralNetworkClassifier
from chembee_config.benchmark.restricted_bm import RBMClassifier

from chembee_plotting.graphics import plotting_map_comparison
from file_utils import save_json_to_file
import logging


logging.basicConfig(
    format="%(levelname)s:%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
    filename="chembee.log",
)

algorithms = [
    SVClassifier,
    SVCPolyClassifier,
    SpectralClusteringClassifier,
    RandomForestClassifier,
    NaiveBayesClassifier,
    LogisticRegressionClassifier,
    LinearRegressionClassifier,
    KMeansClassifier,
    KNNClassifier,
    NeuralNetworkClassifier,
    RBMClassifier,
]


def benchmark_standard(
    X,
    y,
    feature_names=["Feature 1", "Feature 2"],
    file_name="benchmark",
    prefix="plots/benchmarks",
    algorithms=algorithms,
    to_fit=True,
):

    metrics = {}
    for alg in algorithms:
        try:
            metric = benchmark_algorithm_standard(
                alg,
                X,
                y,
                plot_function=plotting_map_comparison[len(alg.algorithms)],
                file_name="benchmark_" + alg.name,
                prefix=prefix,
                feature_names=feature_names,
                response_method=alg._response_method,
                to_fit=to_fit,
            )
        except Exception as e:
            assert 1 == 2, str(e)
            logging.info("Could not fit classifier " + str(alg.name))
            logging.info(str(e))
            metric = None
        finally:
            continue
    save_json_to_file(metrics, file_name=file_name, prefix=prefix)
    return metrics


def benchmark_cv_algorithms(
    algorithms: list,
    names: list,
    X: np.ndarray,
    y: np.ndarray,
    plot_function=plotting_map_comparison[1],
    file_name: str = "after_cv_benchmark",
    prefix: str = "plots/benchmarks/",
    feature_names: list = ["Feature 1", "Feature 2"],
    response_method: str = "predict",
    to_fit=True,
):
    """
    The benchmark_cv_algorithms function takes a list of algorithms and fits them to the data.
    It then plots the results using plot_cv_algorithms function.

    :param algorithms:list: Used to Specify which algorithms to use in the benchmark.
    :param names:list: Used to Specify the names of the algorithms.
    :param X:np.ndarray: Used to Pass the data to be used for training and testing.
    :param y:np.ndarray: Used to Pass the target variable.
    :param file_name:str="benchmark": Used to Name the output file.
    :param prefix:str="benchmarks/": Used to Specify the path to the directory where all benchmark plots are saved.
    :param feature_names:list=["Feature1": Used to Label the x-axis of the plots.
    :param "Feature2"]: Used to Specify the name of the feature that is used for plotting.
    :param response_method:str="predict": Used to Determine which method is used to generate the response.
    :param to_fit=True: Used to Determine whether the model should be fitted before predicting or transforming.
    :param : Used to Determine the method used to obtain the response from the model.
    :return: A list of metrics for each model.

    :doc-author: Trelent
    """

    metrics_class = []
    models = []

    for i in range(len(algorithms)):

        clf = algorithms[i]
        name = names[i]
        file_name = "benchmark_" + name
        if to_fit:
            clf = clf.fit(X, y)
        models.append(clf)
        if response_method == "predict":
            y_pred = clf.predict(X)
        elif response_method == "fit_predict":
            y_pred = clf.fit_predict(X, y)
        if response_method == "transform":
            y_pred = clf.transform(X)
        logging.info("Fitted model: " + str(name))

        plot_function(
            clf=clf,
            X=X,
            y=y,
            file_name=file_name,
            prefix=prefix,
            feature_names=feature_names,
            response_method=response_method,
        )

    metrics = {k: v for k, v in zip(names, metrics_class)}
    return metrics


def benchmark_algorithm_standard(
    algorithm: list,
    X: np.ndarray,
    y: np.ndarray,
    plot_function: object(),
    file_name: str = "benchmark",
    prefix: str = "benchmarks/",
    feature_names: list = ["Feature 1", "Feature 2"],
    response_method: str = "predict",
    to_fit=True,
) -> dict:
    """
    The benchmark_algorithm_standard function takes a list of algorithms,
    a list of names for the algorithms, and a dataset (X and y),
    and returns an array of metrics. The function also plots the results.

    :param algorithm:list: Used to Store the algorithms that will be used in the benchmark.
    :param names:list: Used to Pass the names of the algorithms that will be used in the plot.
    :param X:np.ndarray: Used to Pass the data to the benchmark_algorithm_standard function.
    :param y:np.ndarray: Used to Pass the target variable to the plot_roc_curve function.
    :param plot_function:object(): Used to Pass a function to the benchmark_algorithm_standard function.
    :param file_name:str="benchmark": Used to Define the name of the file that will be saved.
    :param prefix:str="benchmarks/": Used to Specify the path where the plots will be saved.
    :param feature_names:list=["Feature1": Used to Label the x-axis of the plot.
    :param "Feature2"]: Used to Specify the name of the feature that is used in the plot.
    :param response_method:str="predict": Used to Determine the method used to generate a response from the model.
    :param to_fit=True: Used to Tell the algorithm to fit the model before predicting.
    :param : Used to Define the type of plot to be created.
    :return: A dictionary of metrics.

    :doc-author: Trelent"""

    name = algorithm.name
    algorithms = algorithm.algorithms
    file_name = "benchmark_" + name
    metrics_class = []
    models = []
    for i in range(len(algorithm.titles)):

        clf = algorithms[i]
        if to_fit:
            clf = clf.fit(X, y)
        models.append(clf)
        if response_method == "predict":
            y_pred = clf.predict(X)
        elif response_method == "fit_predict":
            y_pred = clf.fit_predict(X, y)
        if response_method == "transform":
            y_pred = clf.transform(X)
        logging.info("Fitted model: " + str(algorithm.titles[i]))

    plot_function(
        models=models,
        titles=algorithm.titles,
        X=X,
        y=y,
        file_name=file_name,
        prefix=prefix,
        feature_names=feature_names,
        response_method=response_method,
    )

    metrics = {k: v for k, v in zip(algorithm.titles, metrics_class)}
    return metrics


# should refactor the above functions
def benchmark_algorithm(
    algorithms: list,
    X: np.ndarray,
    y: np.ndarray,
    plot_function: object(),
    file_name: str = "benchmark",
    prefix: str = "benchmarks/",
    feature_names: list = ["Feature 1", "Feature 2"],
    response_method: str = "predict",
    to_fit=True,
) -> dict:
    """
    The benchmark_algorithm function is used to benchmark the performance of a given algorithm.
    It takes as input an algorithm, and returns a dictionary containing the metrics for that algorithm.
    The function is designed to be called within a loop, so that it can be used to compare multiple algorithms at once.

    :param algorithm: Used to Specify the algorithm to use.
    :param X:np.ndarray: Used to Pass the data to be used for training and testing.
    :param y:np.ndarray: Used to Pass the target variable to the plot_roc_curve function.
    :param plot_function:object(): Used to Pass a function that plots the results.
    :param file_name:str="benchmark": Used to Name the plot file.
    :param prefix:str="benchmarks/": Used to Specify the path to store the generated plots.
    :param feature_names:list=["Feature1": Used to Name the columns of the dataframe.
    :param "Feature2"]: Used to Specify the names of the features in your dataset.
    :param response_method:str="predict": Used to Determine whether the models should be used to predict the response or transform it.
    :param to_fit=True: Used to Fit the model to the data.
    :param : Used to Specify the name of the file to which we want to save our plots.
    :return: A dictionary with the following keys:.

    :doc-author: Trelent
    """

    clf = algorithms[i]
    if to_fit:
        clf = clf.fit(X, y)
    models.append(clf)
    if response_method == "predict":
        y_pred = clf.predict(X)
    elif response_method == "fit_predict":
        y_pred = clf.fit_predict(X, y)
    if response_method == "transform":
        y_pred = clf.transform(X)
    logging.info("Fitted model: " + str(algorithm.titles[i]))

    metrics = {k: v for k, v in zip(algorithm.titles, metrics_class)}
    return metrics
