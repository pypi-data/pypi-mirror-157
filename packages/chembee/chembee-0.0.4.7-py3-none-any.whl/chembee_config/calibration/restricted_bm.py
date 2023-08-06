from sklearn.neural_network import BernoulliRBM

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


RBMClassifier = BernoulliRBM(n_components=612, learning_rate=0.0001)
