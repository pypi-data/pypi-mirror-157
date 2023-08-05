from dataclasses import dataclass

from dataclasses_json import dataclass_json

from milla_tdf.data_model.abstract import AbstractDataModel, AbstractMetaData

@dataclass
class StockPriceMetaData(AbstractMetaData):
    symbols: list[str]
    updated: list[str]
  

@dataclass
class StockPriceData(AbstractDataModel):
    Symbol:str
    Time: str
    Open: float
    High: float
    Low: float
    Close: float
    Volume: float
