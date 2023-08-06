from sklearn.linear_model import LogisticRegression


class LogisticRegressionClassifierAlgorithm(LogisticRegression):

    name = "logr"


LogisticRegressionClassifier = LogisticRegressionClassifierAlgorithm(
    multi_class="multinomial"
)
