import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from sklearn.cluster import SpectralClustering


from chembee_config.benchmark.BenchmarkAlgorithm import BenchmarkAlgorithm


class SpectralClusteringClassifier(BenchmarkAlgorithm):

    name = "spectral-clustering"
    C = 1.0  # SVM regularization parameter
    algorithms = (
        SpectralClustering(
            n_clusters=3,
            eigen_tol=1e-7,
            assign_labels="kmeans",
            random_state=42,
        ),
        SpectralClustering(
            n_clusters=3,
            eigen_tol=1e-7,
            assign_labels="discretize",
            random_state=42,
        ),
        SpectralClustering(
            n_clusters=3,
            eigen_tol=1e-7,
            assign_labels="cluster_qr",
            random_state=42,
        ),
    )
    titles = (
        "k-means",
        "discretize method",
        "cluster_qr",
    )
    _response_method = "fit_predict"
