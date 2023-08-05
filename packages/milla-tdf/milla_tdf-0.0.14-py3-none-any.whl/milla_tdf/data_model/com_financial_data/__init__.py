from dataclasses import dataclass, field

from milla_tdf.data_model.abstract import AbstractDataModel, AbstractMetaData

@dataclass
class ComFinancialMetaData(AbstractMetaData):
    symbols: list[str]
    updated: list[str]

@dataclass
class ComFinancialData(AbstractDataModel):
    Symbol:str
    yearReport: float
    lengthReport: float
    bsa1: float = field(init=False)
    bsa2: float
    bsa5: float
    bsa8: float
    bsa10: float
    bsa15: float
    bsa18: float
    bsa23: float
    bsa24: float
    bsa27: float
    bsa29: float
    bsa43: float
    bsa49: float
    bsa50: float
    bsa53: float
    bsa54: float
    bsa55: float
    bsa56: float
    bsa58: float
    bsa67: float
    bsa71: float
    bsa78: float
    bsa79: float
    bsa80: float
    bsa86: float
    bsa90: float
    bsa96: float
    bsa159: float
    bsa162: float
    bsa173: float
    bsa175: float
    bsa209: float
    cashCycle: float
    cfa21: float
    cfa22: float
    comTypeCode: str
    icbCode: str
    isa22: float
    
    lengthReportCal: float
    organCode: str
    rev: float
    rqq72: float
    ryd3: float
    ryd7: float
    ryd11: float
    ryd14: float
    ryd21: float
    ryd25: float
    ryd26: float
    ryd28: float
    ryd30: float
    ryq1: float
    ryq2: float
    ryq3: float
    ryq6: float
    ryq10: float
    ryq12: float
    ryq14: float
    ryq16: float
    ryq18: float
    ryq20: float
    ryq25: float
    ryq27: float
    ryq29: float
    ryq31: float
    ryq34: float
    ryq39: float
    ryq71: float
    ryq76: float
    ryq77: float
    ryq91: float
    
    yearReportCal: float
