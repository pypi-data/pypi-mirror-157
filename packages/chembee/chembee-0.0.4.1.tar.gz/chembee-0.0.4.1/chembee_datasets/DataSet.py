from file_utils import prepare_file_name_saving


class DataSet:

    # raw data (don't touch)
    name = None
    data = None

    def load_data_set():
        raise NotImplementedError

    def make_train_test_split(self, data_set, split_ratio):
        raise NotImplementedError

    def get_split(self):

        return self.X_train, self.X_test, self.y_train, self.y_test

    def save_data_csv(self, file_name, prefix=None):

        file_name = prepare_file_name_saving(prefix=prefix, file_name=file_name)
        self.data.to_csv(file_name)
