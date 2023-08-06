from chembee_config.calibration.logistic_regression import LogisticRegressionClassifier
from chembee_config.calibration.naive_bayes import NaiveBayesClassifier
from chembee_config.calibration.svc import NaivelyCalibratedSVCRBF
from chembee_config.calibration.svc import NaivelyCalibratedSVCPolynomial
from chembee_config.calibration.random_forest import RandomForestClassifier
from chembee_config.calibration.knn import KNNClassifier
from chembee_config.calibration.mlp_classifier import NeuralNetworkClassifierRELU
from chembee_config.calibration.mlp_classifier import NeuralNetworkClassifierTanh


clf_list = [
    LogisticRegressionClassifier,
    NaiveBayesClassifier,
    NaivelyCalibratedSVCRBF,
    NaivelyCalibratedSVCPolynomial,
    RandomForestClassifier,
    KNNClassifier,
    NeuralNetworkClassifierRELU,
    NeuralNetworkClassifierTanh,
]
