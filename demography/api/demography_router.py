from io import BytesIO

from fastapi import APIRouter, UploadFile
from db import mongo
from demography.logic.parse_demography import parse_area_demography

demography_router = APIRouter()


async def update_areas_add_demography(dem_data: list):
    mongo_terr_cards = mongo.db.get_collection("territory_cards")
    update_count = 0
    for item in dem_data:
        if item["total_people"] > 0:
            item_id = item["area_id"]
            data = await mongo_terr_cards.find_one({"ods_sys_id": item_id})
            if "demography" not in data:
                update_res = await mongo_terr_cards.update_one(
                                                                {"ods_sys_id": item_id},
                                                                {"$set": {"demography": [item]}}
                                                              )
                print(f"add demography to area id {item_id}")
                update_count += 1
            else:
                update_res = await mongo_terr_cards.update_one(
                                                                    {"ods_sys_id": item_id},
                                                                    {"$push": {"demography": item}}
                                                                )
                print(f"area id {item_id} already has demography data, append new value")

    print(f"updated {update_count} area records in database")


@demography_router.post("/upload")
async def upload_area_demography(demography_file: UploadFile):
    if demography_file.filename.endswith('.xlsx'):
        f_area_dem = await demography_file.read()
        xlsx = BytesIO(f_area_dem)

        demography_data = parse_area_demography(xlsx)
        await update_areas_add_demography(demography_data["parsed_records"])


    return {
        "result": "ok"
    }


