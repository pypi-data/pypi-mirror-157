from sklearn.neural_network import MLPClassifier


class MLPClassifierAlgorithm(MLPClassifier):
    name = "mlp"
    hyperparameters = [
        {
            "alpha": [0.0001, 0.00005, 0.00001, 0.0000001],
            "learning_rate": ["constant", "inv_scaling", "adaptive"],
            "early_stopping": [True, False],
        }
    ]


hidden_layer_sizes = (100, 20, 20, 100)
max_iter = 10000
NeuralNetworkClassifierRELU = MLPClassifierAlgorithm(
    hidden_layer_sizes=hidden_layer_sizes,
    activation="relu",
    solver="adam",
    max_iter=max_iter,
)
NeuralNetworkClassifierRELU.name = "mlpra"

NeuralNetworkClassifierTanh = MLPClassifierAlgorithm(
    hidden_layer_sizes=hidden_layer_sizes,
    activation="tanh",
    solver="adam",
    max_iter=max_iter,
)
NeuralNetworkClassifierTanh.name = "mlpta"
