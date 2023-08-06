import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from sklearn.cluster import KMeans


from chembee_config.benchmark.BenchmarkAlgorithm import BenchmarkAlgorithm


class KMeansClassifier(BenchmarkAlgorithm):

    name = "kmeans"

    algorithms = (
        KMeans(
            n_clusters=3,
            init="k-means++",
            n_init=10,
            max_iter=300,
            tol=0.0001,
            verbose=0,
            random_state=None,
            copy_x=True,
            algorithm="lloyd",
        ),
        KMeans(
            n_clusters=3,
            init="random",
            n_init=10,
            max_iter=300,
            tol=0.0001,
            verbose=0,
            random_state=None,
            copy_x=True,
            algorithm="lloyd",
        ),
        KMeans(
            n_clusters=3,
            init="k-means++",
            n_init=10,
            max_iter=300,
            tol=0.0001,
            verbose=0,
            random_state=None,
            copy_x=True,
            algorithm="lloyd",
        ),
        KMeans(
            n_clusters=3,
            init="k-means++",
            n_init=10,
            max_iter=300,
            tol=0.0001,
            verbose=0,
            random_state=None,
            copy_x=True,
            algorithm="elkan",
        ),
    )

    titles = (
        "k-means++ initialization",
        "random initialization",
        "Lloyd method",
        "Elkan method",
    )
