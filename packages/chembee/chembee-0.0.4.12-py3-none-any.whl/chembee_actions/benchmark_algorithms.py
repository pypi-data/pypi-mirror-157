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
            metric = benchmark_algorithm(
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


def benchmark_algorithm(
    algorithm,
    X: np.ndarray,
    y: np.ndarray,
    plot_function: object(),
    file_name: str = "benchmark",
    prefix: str = "benchmarks/",
    feature_names: list = ["Feature 1", "Feature 2"],
    response_method: str = "predict",
    to_fit=True,
) -> dict:
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
