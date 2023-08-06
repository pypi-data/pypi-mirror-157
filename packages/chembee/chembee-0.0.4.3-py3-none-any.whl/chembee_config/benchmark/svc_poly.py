import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from sklearn import svm


from chembee_config.benchmark.BenchmarkAlgorithm import BenchmarkAlgorithm


class SVCPolyClassifier(BenchmarkAlgorithm):

    name = "svc_polys"
    C = 1.0
    algorithms = (
        svm.SVC(kernel="poly", degree=1, gamma="auto", C=C),
        svm.SVC(kernel="poly", degree=3, gamma="auto", C=C),
        svm.SVC(kernel="poly", degree=6, gamma="auto", C=C),
    )

    titles = (
        "Polynomial (degree 1) kernel",
        "Polynomial (degree 3) kernel",
        "Polynomial (degree 6) kernel",
    )
