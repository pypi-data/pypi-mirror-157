import sys, os
from sklearn import datasets

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import prepare_data_decicion_lib
from chembee_actions.benchmark_algorithms import benchmark_standard


def test_benchmarking():

    iris = datasets.load_iris()
    X, y = prepare_data_decicion_lib(iris)
    benchmark_standard(
        X,
        y,
        feature_names=iris.feature_names[:2],
    )
