from chembee_datasets.BreastCancer import BreastCancerDataset
from sklearn import datasets


class IrisDataSet(BreastCancerDataset):

    name = "iris-dataset"

    def load_data_set(self):

        iris_data = datasets.load_iris()
        return iris_data
