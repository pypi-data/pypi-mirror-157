import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from sklearn import svm

from chembee_config.benchmark.BenchmarkAlgorithm import BenchmarkAlgorithm


class SVClassifier(BenchmarkAlgorithm):

    name = "svc"
    C = 1.0  # SVM regularization parameter
    algorithms = (
        svm.SVC(kernel="linear", C=C),
        svm.LinearSVC(C=C, max_iter=10000),
        svm.SVC(kernel="rbf", gamma=0.7, C=C),
        svm.SVC(kernel="poly", degree=3, gamma="auto", C=C),
    )
    titles = (
        "SVC with linear kernel",
        "LinearSVC (linear kernel)",
        "SVC with RBF kernel",
        "SVC with polynomial (degree 3) kernel",
    )
