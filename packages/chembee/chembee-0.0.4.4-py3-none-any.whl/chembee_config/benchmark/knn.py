import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from sklearn.neighbors import KNeighborsClassifier


from chembee_config.benchmark.BenchmarkAlgorithm import BenchmarkAlgorithm


class KNNClassifier(BenchmarkAlgorithm):

    name = "knn"
    n_neighbors = 15
    algorithms = (
        KNeighborsClassifier(n_neighbors=n_neighbors, algorithm="ball_tree"),
        KNeighborsClassifier(n_neighbors=n_neighbors, algorithm="kd_tree"),
        KNeighborsClassifier(n_neighbors=n_neighbors, algorithm="brute"),
    )
    titles = (
        " Ball tree algorithm",
        "KD tree algorithm",
        "Brute force",
    )
