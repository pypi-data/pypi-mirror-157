from sklearn.neural_network import MLPClassifier


class MLPClassifierAlgorithm(MLPClassifier):
    name = "mlp"


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
