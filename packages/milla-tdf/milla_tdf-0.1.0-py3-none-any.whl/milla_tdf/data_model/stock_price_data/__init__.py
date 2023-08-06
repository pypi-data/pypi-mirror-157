from dataclasses import dataclass, field

from dataclasses_json import dataclass_json

from milla_tdf.data_model.abstract import AbstractDataModel, AbstractMetaData
from datetime import datetime

@dataclass
class StockPriceMetaData(AbstractMetaData):
    symbols: list[str]
    updated: list[str]
    keys:list[str] = field(default_factory=lambda: ['Symbol','Time'])

@dataclass
class StockPriceData(AbstractDataModel):
    Symbol:str
    Time: datetime
    Open: float
    High: float
    Low: float
    Close: float
    Volume: float
