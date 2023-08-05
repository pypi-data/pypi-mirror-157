import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from sklearn.linear_model import LogisticRegression


from chembee_config.benchmark.BenchmarkAlgorithm import BenchmarkAlgorithm


class LogisticRegressionClassifier(BenchmarkAlgorithm):
    name = "logistic-regression"

    algorithms = (
        LogisticRegression(penalty="l1", solver="saga", max_iter=1000),
        LogisticRegression(penalty="l2", solver="saga", max_iter=1000),
        LogisticRegression(
            penalty="elasticnet", solver="saga", l1_ratio=0.5, max_iter=1000
        ),
    )

    titles = (
        "l1",
        "l2",
        "elasticnet with $\chi(\mathrm{L!}) = 0.5$",
    )
