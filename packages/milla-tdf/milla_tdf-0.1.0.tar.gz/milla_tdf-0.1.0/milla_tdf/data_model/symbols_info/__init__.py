from dataclasses import dataclass, field

from dataclasses_json import dataclass_json

from milla_tdf.data_model.abstract import AbstractDataModel


@dataclass
class SymbolInfoData(AbstractDataModel):
    Symbol:str
    OrganCode:str
    Board:str
    ComTypeCode:str

@dataclass_json
@dataclass
class SymbolInfoMetaData():
    updated:str
    keys:list[str] = field(default_factory=lambda: ['Symbol'])
