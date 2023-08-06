from sklearn.svm import SVC
from sklearn.svm import LinearSVC
import numpy as np


class NaivelyCalibratedLinearSVC(LinearSVC):
    """LinearSVC with `predict_proba` method that naively scales
    `decision_function` output."""

    name = "lscv"

    def fit(self, X, y):
        super().fit(X, y)
        df = self.decision_function(X)
        self.df_min_ = df.min()
        self.df_max_ = df.max()

    def predict_proba(self, X):
        """Min-max scale output of `decision_function` to [0,1]."""
        df = self.decision_function(X)
        calibrated_df = (df - self.df_min_) / (self.df_max_ - self.df_min_)
        proba_pos_class = np.clip(calibrated_df, 0, 1)
        proba_neg_class = 1 - proba_pos_class
        proba = np.c_[proba_neg_class, proba_pos_class]
        return proba


class NaivelyCalibratedSVC(SVC):
    """LinearSVC with `predict_proba` method that naively scales
    `decision_function` output."""

    name = "svc"
    hyperparameters = [{"kernel": ["rbf"], "gamma": ["scale", "auto"]}]

    def fit(self, X, y):
        super().fit(X, y)
        df = self.decision_function(X)
        self.df_min_ = df.min()
        self.df_max_ = df.max()

    def predict_proba(self, X):
        """Min-max scale output of `decision_function` to [0,1]."""
        df = self.decision_function(X)
        calibrated_df = (df - self.df_min_) / (self.df_max_ - self.df_min_)
        proba_pos_class = np.clip(calibrated_df, 0, 1)
        proba_neg_class = 1 - proba_pos_class
        proba = np.c_[proba_neg_class, proba_pos_class]
        return proba


NaivelyCalibratedSVCLinear = NaivelyCalibratedLinearSVC(C=1.0)
NaivelyCalibratedSVCRBF = NaivelyCalibratedSVC(kernel="rbf", gamma=0.7, C=1.0)
NaivelyCalibratedSVCRBF.name = "rbf_svc"
NaivelyCalibratedSVCPolynomial = NaivelyCalibratedSVC(kernel="poly", degree=5, C=1.0)
NaivelyCalibratedSVCPolynomial.name = "poly_svc"
