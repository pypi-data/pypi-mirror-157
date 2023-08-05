import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet


from chembee_config.benchmark.BenchmarkAlgorithm import BenchmarkAlgorithm


class LinearRegressionClassifier(BenchmarkAlgorithm):

    name = "linear-regression"

    algorithms = (LinearRegression(), Ridge(), Lasso(), ElasticNet())
    titles = (
        "Ordinary Least Squares",
        "Ridge",
        "Lasso",
        "Elastic net",
    )
