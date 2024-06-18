from pydantic import BaseModel
from typing import List, Callable


class TerritoryItem(BaseModel):
    terr_id: str                # id территории = uid внешнего контура
    district: str               # Округ
    address: str                # Адрес
    area_type: str              # Тип площадки
    surface: str                # Площадь
    ods_sys_addr: str           # Адрес АСУ ОДС
    ods_sys_id: str             # АСУ ОДС Идентификатор
    dkr_address: str            # Адрес ДКР
    sok_sys_name: str           # СОК.Благоустройство Наименование
    polygonPoints: List         # Полигоны в АСУ ОДС(план - схемы)
    wgs84: List                 # Координаты wgs84
    polygons: dict

