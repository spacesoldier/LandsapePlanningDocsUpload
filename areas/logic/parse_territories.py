import openpyxl as xl
import uuid
import json
from shapely.geometry import Polygon

from areas.logic.territory_item import TerritoryItem


def combine_points(mggt, wgs84):
    polygon_uuid = str(uuid.uuid4())
    output = {
        "uid": polygon_uuid,
        "mggt": mggt,
        "wgs84": wgs84
    }
    return output


SUPER_AREA_TYPE_NAME = "super_area"
REGULAR_AREA_TYPE_NAME = "area"


def parse_territory_list(excel_content):
    terr_xl = xl.load_workbook(excel_content)
    first_page_name = terr_xl.sheetnames[0]
    plan_page = terr_xl[first_page_name]
    first_row = True

    territory_drafts = []
    terr_drafts_index = {}
    terrs_to_calc_class = []

    territory_types = set()
    terr_type_classes = {
                            "super": set(),
                            "regular": set()
                        }

    terr_model_cards = []

    territories = {
        "geo_cards": territory_drafts,
        "territory_model_cards": terr_model_cards,
        "area_types": territory_types,
        "area_types_classes": terr_type_classes
    }

    row_counter = 0
    actual_count = 0
    for row in plan_page.rows:
        if first_row:
            first_row = False
            wgs84_title = row[-1].value
            for cell in row:
                print(f"{cell.value}")

        else:

            row_counter += 1

            wgs84_str = row[-1].value
            wgs84 = []

            try:
                wgs84 = json.loads(wgs84_str)
            except Exception:
                print("row has no wgs84 data")

            mggt_points_str = row[-2].value
            mggt_points = []
            try:
                mggt_points = json.loads(mggt_points_str)
            except Exception:
                print("row has no mggt data")

            terr_surface = row[4].value

            if isinstance(terr_surface, str):
                terr_surface = terr_surface.strip().replace(" ", "").replace(",", ".")

            sok_sys_name = row[8].value
            if not isinstance(sok_sys_name, str):
                sok_sys_name = ""

            dkr_name = row[7].value
            if not isinstance(dkr_name, str):
                dkr_name = ""

            territory_draft = {
                "district": row[1].value,
                "address": row[2].value,
                "area_type": row[3].value,
                "surface": terr_surface,
                "ods_sys_addr": row[5].value,
                "ods_sys_id": row[6].value,
                "dkr_address": dkr_name,
                "sok_sys_name": sok_sys_name,
                "mggt": mggt_points,
                "wgs84": wgs84,
                "polygons": {},
                "terr_info_full": " ---- ".join(map(lambda x: str(x.value), row[1:-2])),
            }

            if len(mggt_points) > 0 and len(wgs84) > 0:

                polys_zip = list(map(combine_points, mggt_points, wgs84[0]))

                for poly in polys_zip:
                    new_polygon = Polygon(poly["wgs84"])
                    poly["geo_pd"] = new_polygon

                    territory_draft["polygons"][poly["uid"]] = poly

                wgs84_polygons_marked = territory_draft["polygons"]


                #TODO: check if the case is still actual
                # given the provided xlsx file with WGS84 data
                # we have to swap lat and lon to obtain correct coordinates
                for poly_key in wgs84_polygons_marked:
                    poly_wgs84 = wgs84_polygons_marked[poly_key]["wgs84"]
                    for point in poly_wgs84:
                        point.reverse()
                    print("meep")

                if len(wgs84_polygons_marked.keys()) > 1:
                    for poly_id in wgs84_polygons_marked.keys():
                        # print(f"check polygon {poly_id} has holes")
                        contains_all = True
                        for p_id in wgs84_polygons_marked.keys():
                            if p_id != poly_id:
                                current_poly = wgs84_polygons_marked[poly_id]["geo_pd"]
                                poly_to_check = wgs84_polygons_marked[p_id]["geo_pd"]
                                if not current_poly.contains(poly_to_check):
                                    contains_all = False
                        if contains_all:
                            territory_draft["terr_id"] = poly_id
                else:
                    if len(wgs84_polygons_marked.keys()) == 1:
                        poly_id = list(wgs84_polygons_marked)[0]
                        territory_draft["terr_id"] = poly_id
                    else:
                        empty_terr_id = str(uuid.uuid4())
                        territory_draft["terr_id"] = empty_terr_id
                        territory_draft["polygons"][territory_draft["terr_id"]] = {
                            "uid": empty_terr_id,
                            "wgs84": [],
                            "mggt": []
                        }

                territory_draft["contour"] = {
                    "type": "Polygon",
                    "coordinates": [territory_draft["polygons"][territory_draft["terr_id"]]["wgs84"]]
                }

                territory_draft["contour_geo_pd"] = territory_draft["polygons"][territory_draft["terr_id"]]["geo_pd"]

                territory_draft["geo_data_all"] = {
                    "type": "Polygon",
                    "coordinates": territory_draft["wgs84"]
                }

                territory_drafts.append(territory_draft)
                terr_drafts_index[territory_draft["terr_id"]] = territory_draft
                actual_count += 1
            else:
                new_terr_id = str(uuid.uuid4())
                territory_draft["terr_id"] = new_terr_id
                territory_draft["geo_data_all"] = {
                    "type": "Polygon",
                    "coordinates": []
                }

                territory_draft["contour"] = {
                    "type": "Polygon",
                    "coordinates": []
                }

                territory_drafts.append(territory_draft)
                terr_drafts_index[new_terr_id] = territory_draft
                terrs_to_calc_class.append(new_terr_id)
                actual_count += 1
                print(f"persist area with no geo data provided, terr_id ={new_terr_id}")

    for terr in territories["geo_cards"]:
        curr_terr_id = terr["terr_id"]
        territory_contains = []
        # respect the areas with no geo data provided
        if "contour_geo_pd" in terr:
            curr_geo_pd_contour = terr["contour_geo_pd"]
            if curr_geo_pd_contour is not None:
                for terr_to_check in territories["geo_cards"]:
                    check_terr_id = terr_to_check["terr_id"]
                    if check_terr_id != curr_terr_id:
                        # respect the areas with no geo data provided
                        if "contour_geo_pd" in terr_to_check:
                            geo_pd_contour_to_check = terr_to_check["contour_geo_pd"]
                            if geo_pd_contour_to_check is not None:
                                if curr_geo_pd_contour.contains(geo_pd_contour_to_check):
                                    territory_contains.append(check_terr_id)
        else:
            print(f"cannot perform class check for area {curr_terr_id}")

        terr["contain_areas"] = territory_contains

        area_type = terr["area_type"]
        territory_types.add(area_type)
        if len(territory_contains) > 0:
            terr["area_class"] = SUPER_AREA_TYPE_NAME
            terr_type_classes["super"].add(area_type)
        else:
            terr["area_class"] = REGULAR_AREA_TYPE_NAME
            if area_type not in terr_type_classes["super"]:
                terr_type_classes["regular"].add(area_type)

        terr["contains"] = territory_contains

    print(f"analyzed {actual_count} of {row_counter} rows")

    for restore_card_id in terrs_to_calc_class:
        card = terr_drafts_index[restore_card_id]
        if card["area_class"] is None:
            card["area_class"] = ""
        area_type = card["area_type"]
        if area_type in terr_type_classes["super"]:
            card["area_class"] = SUPER_AREA_TYPE_NAME
        if area_type in terr_type_classes["regular"]:
            card["area_class"] = REGULAR_AREA_TYPE_NAME
        print(f"area {restore_card_id} is {card['area_class']}")

    for terr_card in territories["geo_cards"]:
        try:
            model_data = {
                    "terr_id": terr_card["terr_id"],
                    "district": terr_card["district"],
                    "address": terr_card["address"],
                    "area_type": terr_card["area_type"],
                    "surface": terr_card["surface"],
                    "ods_sys_addr": terr_card["ods_sys_addr"],
                    "ods_sys_id": terr_card["ods_sys_id"],
                    "dkr_address": terr_card["dkr_address"],
                    "sok_sys_name": terr_card["sok_sys_name"],
                    "area_class": terr_card["area_class"],
                    "contain_areas": terr_card["contain_areas"],
                    "contour": terr_card["contour"],
                    "geo_data_all": {
                        "mggt": terr_card["mggt"],
                        "wgs84": terr_card["wgs84"]
                }
            }
        except Exception as ex:
            print(f"problem with geo card")

        try:
            terr_model_cards.append(TerritoryItem(**model_data))
        except Exception as ex:
                print(f"something wrong with the model data")

    return territories


