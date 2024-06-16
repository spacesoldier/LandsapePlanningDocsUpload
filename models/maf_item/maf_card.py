from typing import List
from pydantic import BaseModel
from decimal import Decimal


class MafItem(BaseModel):
    name: str
    catalogName: str
    vendor: str                     # provider
    vendorCode: int
    analogSample: str
    sampleCode: str
    mafType: str                    # type
    typeEquipment: str
    ageCategory: str
    units: str
    description: str
    dimensionStr: str               # dimensions as string
    dimensions: List[int]           # dimensions in millimeters as numbers
    price: Decimal
    territoryTypes: List[str]
    imageFileName: str
    safetyZonesFileName: str
    techDocFileName: str


