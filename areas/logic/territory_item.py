from pydantic import BaseModel
from typing import List, Callable


class TerritoryItem(BaseModel):
    terr_id: str                # id территории = uid внешнего контура
    district: str               # Округ
    address: str                # Адрес
    area_type: str              # Тип площадки
    surface: float              # Площадь
    ods_sys_addr: str           # Адрес АСУ ОДС
    ods_sys_id: int             # АСУ ОДС Идентификатор
    dkr_address: str            # Адрес ДКР
    sok_sys_name: str           # СОК.Благоустройство Наименование
    area_class: str
    contain_areas: list
    contour: dict
    geo_data_all: dict


