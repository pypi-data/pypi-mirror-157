import pandas as pd
from milla_tdf.data_model.abstract import AbstractDataModel, AbstractMetaData


class AbstractStorage:
    @classmethod
    def load_config(cls, **kwargs):
        pass

    @classmethod
    def load_data(cls, data_model: AbstractDataModel, **kwargs) -> pd.DataFrame:
        pass

    @classmethod
    def load_metadata(cls,data_model: AbstractDataModel, **kwargs) -> AbstractMetaData:
        pass
