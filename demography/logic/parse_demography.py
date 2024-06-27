import openpyxl as xl
import uuid

from demography.logic.area_demography import AreaDemography


def parse_area_demography(excel_content):
    dem_xl = xl.load_workbook(excel_content)
    data_page_name = dem_xl.sheetnames[1]
    plan_page = dem_xl[data_page_name]

    dem_records = []
    demography_cards = []

    dem_data_parsed = {
        "parsed_records": dem_records,
        "demography_cards": demography_cards
    }

    reading_header = True
    row_counter = 0
    for row in plan_page.rows:
        if reading_header:
            if row_counter > 0:
                reading_header = False
            else:
                row_counter += 1
        else:

            rec_uid = str(uuid.uuid4())

            ods_addr = row[3].value
            if ods_addr is None:
                ods_addr = ""

            apt_count = row[5].value
            if apt_count is None:
                apt_count = -1

            total_ppl = row[6].value
            if total_ppl is None:
                total_ppl = -1

            men_percent = row[7].value
            if men_percent is None:
                men_percent = 0.0

            women_percent = row[8].value
            if women_percent is None:
                women_percent = 0.0

            cat_1d_age_count = row[9].value
            if cat_1d_age_count is None:
                cat_1d_age_count = 0

            cat_2d_age_count = row[10].value
            if cat_2d_age_count is None:
                cat_2d_age_count = 0

            cat_3d_age_count = row[11].value
            if cat_3d_age_count is None:
                cat_3d_age_count = 0

            cat_4v_age_count = row[12].value
            if cat_4v_age_count is None:
                cat_4v_age_count = 0

            cat_5v_age_count = row[13].value
            if cat_5v_age_count is None:
                cat_5v_age_count = 0

            cat_6v_age_count = row[14].value
            if cat_6v_age_count is None:
                cat_6v_age_count = 0

            dem_data = {
                "demography_id": rec_uid,
                "area_id": row[2].value,            # Идентификатор родительского объекта
                "district": row[0].value,           # Адресат (АО)
                "address": row[1].value,            # Адрес
                "ods_address": ods_addr,            # Адрес (АСУ ОДС)
                "total_people": total_ppl,          # Всего жителей проживающих по адресу, чел.
                "apt_count": apt_count,             # Всего квартир по адресу, шт.
                "men_percent": men_percent,         # Из них доля мужского пола,%
                "women_percent": women_percent,     # Из них доля женского пола,%
                "people_by_age": {
                                    "age_rec_uid": str(uuid.uuid4()),
                                    "1d_age": {
                                        "age_from": 0,
                                        "age_to": 7,
                                        "count": cat_1d_age_count
                                    },
                                    "2d_age": {
                                        "age_from": 8,
                                        "age_to": 12,
                                        "count": cat_2d_age_count
                                    },
                                    "3d_age": {
                                        "age_from": 13,
                                        "age_to": 18,
                                        "count": cat_3d_age_count
                                    },
                                    "4v_age": {
                                        "age_from": 19,
                                        "age_to": 30,
                                        "count": cat_4v_age_count
                                    },
                                    "5v_age": {
                                        "age_from": 31,
                                        "age_to": 55,
                                        "count": cat_5v_age_count
                                    },
                                    "6v_age": {
                                        "age_from": 56,
                                        "age_to": 110,
                                        "count": cat_6v_age_count
                                    }
                                 }                  # Распределение по возрастным группам
            }

            dem_records.append(dem_data)
    for record in dem_records:
        try:
            new_demography = AreaDemography(**record)
            demography_cards.append(new_demography)
        except Exception as ex:
            print(f"wrong data {ex}")
    return dem_data_parsed


