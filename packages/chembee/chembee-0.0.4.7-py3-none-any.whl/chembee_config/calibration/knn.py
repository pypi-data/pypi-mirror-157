from sklearn.neighbors import KNeighborsClassifier


class KNeighborsClassifierAlgorithm(KNeighborsClassifier):
    name = "knn"


KNNClassifier = KNeighborsClassifierAlgorithm()
