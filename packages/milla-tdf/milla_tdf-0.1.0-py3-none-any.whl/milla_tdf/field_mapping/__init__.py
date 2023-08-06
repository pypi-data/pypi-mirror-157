from dataclasses import dataclass
from typing import Callable


@dataclass
class FieldMappingConfig:
    new_field_name:str
    function: Callable
    args:dict

def remap_data_value(kwargs):
    return kwargs['mapping_data'][kwargs['raw_value']]