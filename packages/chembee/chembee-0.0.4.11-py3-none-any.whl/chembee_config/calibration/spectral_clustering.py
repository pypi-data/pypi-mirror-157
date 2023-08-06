from sklearn.cluster import SpectralClustering


class NaivlyCalibratedSpectralClustering(SpectralClustering):

    name = "spc"

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


SpectralClusteringClassifier = NaivlyCalibratedSpectralClustering(
    n_clusters=3,
    eigen_tol=1e-7,
    assign_labels="kmeans",
    random_state=42,
)
