import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.neural_network import MLPClassifier

from chembee_config.benchmark.BenchmarkAlgorithm import BenchmarkAlgorithm


class NeuralNetworkClassifier(BenchmarkAlgorithm):

    name = "multilayer-perceptron"
    hidden_layer_sizes = (100, 20, 20, 100)
    max_iter = 10000
    algorithms = (
        MLPClassifier(
            hidden_layer_sizes=hidden_layer_sizes,
            activation="logistic",
            max_iter=max_iter,
        ),
        MLPClassifier(
            hidden_layer_sizes=hidden_layer_sizes, activation="tanh", max_iter=max_iter
        ),
        MLPClassifier(
            hidden_layer_sizes=hidden_layer_sizes, activation="relu", max_iter=max_iter
        ),
        MLPClassifier(
            hidden_layer_sizes=hidden_layer_sizes,
            activation="relu",
            solver="adam",
            max_iter=max_iter,
        ),
    )
    titles = (
        "Logistic with SGD",
        "Tanh with SGD",
        "RELU with SGD",
        "RELU with Adam",
    )
