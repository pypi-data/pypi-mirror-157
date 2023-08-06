from chembee_datasets.DataSet import DataSet
from sklearn import datasets
from sklearn.model_selection import train_test_split

from file_utils import prepare_file_name_saving


class BreastCancerDataset(DataSet):

    name = "breast-cancer"

    def __init__(self, split_ratio):

        self.data = self.load_data_set()
        self.split_ratio = split_ratio
        (
            self.X_train,
            self.X_test,
            self.y_train,
            self.y_test,
        ) = self.make_train_test_split(self.data, self.split_ratio)

    def load_data_set(self):
        """
        The load_data_set function loads the data from the csv file and creates a list of lists.
        The function also removes any rows with missing values, as well as any columns that have all zeros.
        The function returns a tuple containing two elements: (data_set, target)

        :param self: Used to Reference the class object.
        :return: The cancer_data dataframe.

        :doc-author: Trelent
        """

        cancer_data = datasets.load_breast_cancer()
        return cancer_data

    def make_train_test_split(self, data, split_ratio, shuffle=True):
        """
        The make_train_test_split function splits the data into training and testing sets.

        Parameters:
            data (object): The dataset to be split.

            split_ratio (float): The ratio of the number of training samples to total number of samples in the dataset.

            shuffle (bool, optional): Whether or not to shuffle the input before splitting it into train and test sets. Defaults to True if not specified otherwise.

        :param self: Used to Reference the class instance.
        :param data: Used to Pass the data set to be split.
        :param split_ratio: Used to determine the ratio of samples used for training.
        :param shuffle=True: Used to shuffle the data before splitting it into train and test sets.
        :return: The following:.

        :doc-author: Trelent
        """

        X = data.data[:, :2]
        y = data.target
        train_samples = int(split_ratio * len(X))
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            shuffle=shuffle,
            test_size=len(X) - train_samples,
        )
        return X_train, X_test, y_train, y_test

    def save_data_npy(self, data, file_name, prefix=None):
        import numpy as np

        file_name = prepare_file_name_saving(
            prefix=prefix, file_name=file_name, ending=".npy"
        )
        np.save(file_name, data)
