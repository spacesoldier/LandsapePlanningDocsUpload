from typing import List, Callable
from pydantic import BaseModel
from decimal import Decimal


class MafCard(BaseModel):
    name: str
    catalogName: str
    vendor: str  # provider
    vendorCode: int
    analogSample: str
    sampleCode: str
    mafType: str  # type
    typeEquipment: str
    ageCategory: str
    units: str
    description: str
    dimensionStr: str  # dimensions as string
    dimensions: List[int]  # dimensions in millimeters as numbers
    price: Decimal
    territoryTypes: List[str]  # territoryType
    imageFileName: str  # image
    safetyZonesFileName: str  # safetyZones
    techDocFileName: str  # techDocumentation


fieldsMapping = {
    "image": "imageFileName",
    "catalogname": "catalogName",
    "vendorcode": "vendorCode",
    "analogsample": "analogSample",
    "samplecode": "sampleCode",
    # "dimensions": "dimensionStr",
    "description": "description",
    "price": "price",
    "name": "name",
    "provider": "vendor",
    "type": "mafType",
    "units": "units",
    "typeequipment": "typeEquipment",
    "safetyzones": "safetyZonesFileName",
    "techdocumentation": "techDocFileName",
    "agecategory": "ageCategory",
    # "territoryType":  "territoryTypes"
}


def fill_dimensions(map_to_fill: dict, dim_str_elem, splitter: Callable):
    text, dims = splitter(dim_str_elem)
    map_to_fill["dimensions"] = dims
    map_to_fill["dimensionStr"] = text


def fill_terr_types(map_to_fill: dict, ter_types_elem, ter_type_list_extractor: Callable):
    map_to_fill["territoryTypes"] = ter_type_list_extractor(ter_types_elem)


special_mapping = {
    "dimensions": fill_dimensions,
    "territorytype": fill_terr_types
}


def map_field(map_to_fill: dict, curr_field_name: str, field_value, value_transformer):
    if curr_field_name in fieldsMapping.keys():
        dict_name = fieldsMapping.get(curr_field_name)
        map_to_fill[dict_name] = field_value
    if curr_field_name in special_mapping:
        special_mapping[curr_field_name](map_to_fill, field_value, value_transformer)

    return map_to_fill
