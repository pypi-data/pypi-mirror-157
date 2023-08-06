import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from chembee_config.benchmark.BenchmarkAlgorithm import BenchmarkAlgorithm


class GridSearchCVClassifier(BenchmarkAlgorithm):

    name = "grid_search_cv"

    def __init__(self, clf_list: list, names: list):
        if len(names) != len(clf_list):
            raise ValueError("Len of classifiers and the name list must be equal.")
        self.algorithms = clf_list
        self.titles = names
