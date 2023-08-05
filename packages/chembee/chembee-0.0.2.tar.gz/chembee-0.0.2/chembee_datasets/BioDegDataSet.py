from chembee_datasets.DataSet import DataSet
import pandas as pd
from sklearn.model_selection import train_test_split
from rdkit import Chem
from rdkit.Chem import (
    Descriptors,
    Descriptors3D,
    rdMolDescriptors,
    PandasTools,
)

from file_utils import prepare_file_name_saving


class BioDegDataSet(DataSet):

    """
    The split ration is set to 0.7 for the feature extraction
    """

    name = "biodeg"

    def __init__(self, data_set_path, target, split_ratio=0.7):

        self.data, self.mols = self.load_data_set(data_set_path)
        self.split_ratio = split_ratio
        (
            self.X_train,
            self.X_test,
            self.y_train,
            self.y_test,
        ) = self.make_train_test_split(self.data, self.split_ratio, y_col=target)

        self.feature_names = self.get_feature_names(self.data, target=target)

    def clean_data(self, data):

        data = data.drop(columns=["SMILES", "Dataset", "CASRN", "ID"])
        data = data.convert_dtypes()
        bad_types = data.select_dtypes(
            exclude=["string", "int64", "float64"]
        ).columns.to_list()
        data = data.drop(columns=bad_types)
        return data

    def load_data_set(self, file_name: str):
        """
        The load_data function loads the data from a sdf file and returns it as a Pandas DataFrame.

        :param file_path:str: Used to Specify the location of the.
        :return: A dataframe with the following columns:.

        :doc-author: Trelent
        """
        mols = Chem.SDMolSupplier(file_name)
        frame = PandasTools.LoadSDF(
            file_name,
            smilesName="SMILES",
            molColName="Molecule",
            includeFingerprints=True,
            removeHs=False,
            strictParsing=True,
        )
        return frame, mols

    def load_data_set_from_csv(self, file_name: str) -> pd.DataFrame:

        return pd.from_csv(file_name)

    def make_train_test_split(self, data, split_ratio: float, y_col: str, shuffle=True):

        X = data.drop([y_col], axis=1)
        y = data[y_col]
        train_samples = int(split_ratio * len(X))
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            shuffle=shuffle,
            test_size=len(X) - train_samples,
        )
        return X_train, X_test, y_train, y_test

    def save_data_csv(self, data: pd.DataFrame, file_name, prefix):

        assert type(data) == type(pd.DataFrame()), "Data must be a pandas.DataFrame"
        file_name = prepare_file_name_saving(
            prefix=prefix, file_name=file_name, ending=".csv"
        )
        data.to_csv(file_name)

    def save_data_sdf(self, data, file_name, prefix, molColName="Molecule"):

        file_name = prepare_file_name_saving(
            prefix=prefix, file_name=file_name, ending=".sdf"
        )
        PandasTools.WriteSDF(
            data, file_name, molColName="Molecule", properties=list(data.columns)
        )

    def get_feature_names(self, data, target):

        if not target:
            data = data.drop(columns=[target])
        return data.columns.to_list()
