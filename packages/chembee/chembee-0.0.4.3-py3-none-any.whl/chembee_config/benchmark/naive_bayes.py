import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB, ComplementNB

from chembee_config.benchmark.BenchmarkAlgorithm import BenchmarkAlgorithm


class NaiveBayesClassifier(BenchmarkAlgorithm):
    name = "naive-bayes"

    algorithms = (
        GaussianNB(),
        MultinomialNB(),
        BernoulliNB(),
        ComplementNB(),
    )

    titles = ("Gaussian", "Multinomial", "Bernoulli", "Complement")
