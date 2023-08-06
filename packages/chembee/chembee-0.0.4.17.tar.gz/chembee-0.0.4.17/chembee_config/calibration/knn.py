from sklearn.neighbors import KNeighborsClassifier


class KNeighborsClassifierAlgorithm(KNeighborsClassifier):
    name = "knn"
    hyperparameters = [
        {
            "n_neighbors": [1, 2, 3, 4, 5, 6, 7, 8],
            "weights": ["uniform", "distance"],
            "p": [1, 2, 3, 4],
        }
    ]


KNNClassifier = KNeighborsClassifierAlgorithm()
