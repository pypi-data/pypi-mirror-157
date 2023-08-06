from sklearn.ensemble import RandomForestClassifier


class RandomForestClassifierAlgorithm(RandomForestClassifier):

    name = "rfc"
    hyperparameters = [
        {
            "n_estimators": [100, 70, 60, 40, 20, 10],
            "max_depth": [None, 20, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        }
    ]


RandomForestClassifier = RandomForestClassifierAlgorithm()
