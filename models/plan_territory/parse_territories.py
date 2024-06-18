import openpyxl as xl
import uuid
import json
import geopandas as geo
from shapely.geometry import Polygon


def combine_points(mggt, wgs84):
    polygon_uuid = str(uuid.uuid4())
    output = {
        "uid": polygon_uuid,
        "mggt": mggt,
        "wgs84": wgs84
    }
    return output


def parse_territory_list(excel_content):
    terr_xl = xl.load_workbook(excel_content)
    first_page_name = terr_xl.sheetnames[0]
    plan_page = terr_xl[first_page_name]
    first_row = True

    territory_drafts = []

    territory_types = set()

    territories = {
        "geo_cards": territory_drafts,
        "area_types": territory_types
    }



    for row in plan_page.rows:
        if first_row:
            first_row = False
            wgs84_title = row[-1].value
            for cell in row:
                print(f"{cell.value}")

        else:

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

            territory_draft = {
                "terr_info_full": " ---- ".join(map(lambda x: str(x.value), row[1:-2])),
                "mggt": mggt_points,
                "wgs84": wgs84,
                "polygons": {}
            }

            territory_types.add(row[3].value)

            if len(mggt_points) > 0 and len(wgs84) > 0:

                polys_zip = list(map(combine_points, mggt_points, wgs84[0]))

                for poly in polys_zip:
                    new_polygon = Polygon(poly["wgs84"])
                    poly["geo_pd"] = new_polygon

                    territory_draft["polygons"][poly["uid"]] = poly

                wgs84_polygons_marked = territory_draft["polygons"]

                for poly_id in wgs84_polygons_marked.keys():
                    print(f"check polygon {poly_id} has holes")
                    contains_all = True
                    for p_id in wgs84_polygons_marked.keys():
                        if p_id != poly_id:
                            current_poly = wgs84_polygons_marked[poly_id]["geo_pd"]
                            poly_to_check = wgs84_polygons_marked[p_id]["geo_pd"]
                            if not current_poly.contains(poly_to_check):
                                contains_all = False
                    if contains_all:
                        territory_draft["terr_id"] = poly_id

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

            else:
                territory_draft["terr_id"] = str(uuid.uuid4())
                print(f"no polygons in row {territory_draft['terr_id']}")

    for terr in territories["geo_cards"]:
        curr_terr_id = terr["terr_id"]
        territory_contains = []
        curr_geo_pd_contour = terr["contour_geo_pd"]
        if curr_geo_pd_contour is not None:
            for terr_to_check in territories["geo_cards"]:
                check_terr_id = terr_to_check["terr_id"]
                if check_terr_id != curr_terr_id:
                    geo_pd_contour_to_check = terr_to_check["contour_geo_pd"]
                    if geo_pd_contour_to_check is not None:
                        if curr_geo_pd_contour.contains(geo_pd_contour_to_check):
                            territory_contains.append(check_terr_id)
        if len(territory_contains) > 0:
            terr["terr_class"] = "area"
        else:
            terr["terr_class"] = "court"

        terr["contains"] = territory_contains

    return territories

