from pydantic import BaseModel


class AreaDemography(BaseModel):
    demography_id: str      # uid записи в бд
    area_id: int            # Идентификатор родительского объекта
    district: str           # Адресат (АО)
    address: str            # Адрес
    ods_address: str        # Адрес (АСУ ОДС)
    total_people: int       # Всего жителей проживающих по адресу, чел.
    apt_count: int          # Всего квартир по адресу, шт.
    men_percent: float      # Из них доля мужского пола,%
    women_percent: float    # Из них доля женского пола,%
    people_by_age: dict     # Распределение по возрастным группам

