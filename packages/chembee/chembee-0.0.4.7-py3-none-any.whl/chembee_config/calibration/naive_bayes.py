from sklearn.naive_bayes import GaussianNB


class GaussianNBAlgorithm(GaussianNB):
    name = "gnb"


NaiveBayesClassifier = GaussianNBAlgorithm()
