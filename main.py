import json
from decimal import Decimal

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

from typing import List
from io import StringIO
from models import MafCard, parse_catalog_from_str, parse_territory_list, AreaDemography, parse_area_demography

from decouple import config

from motor.motor_asyncio import AsyncIOMotorClient

from bson.codec_options import TypeRegistry
from bson.decimal128 import Decimal128
from bson.codec_options import TypeCodec

from io import BytesIO


class DecimalCodec(TypeCodec):
    python_type = Decimal
    bson_type = Decimal128

    def transform_python(self, value):
        return Decimal128(value)

    def transform_bson(self, value):
        return value.to_decimal()


decimal_codec = DecimalCodec()
type_registry = TypeRegistry([decimal_codec])


app = FastAPI()


def decode_file(input_file: UploadFile):
    file_bytes = input_file.file.read()
    buffer = StringIO(file_bytes.decode('utf-8'))
    content = buffer.read()
    buffer.close()
    input_file.file.close()
    return content


from bson.codec_options import CodecOptions


async def insert_maf_to_db(new_maf: MafCard):
    codec_opts = CodecOptions(type_registry=type_registry)
    result = app.planner_db.get_collection("maf_catalog", codec_options=codec_opts).insert_one(new_maf.model_dump())
    return result


@app.post("/maf/catalog/items")
async def upload_maf_card(maf_card_files: List[UploadFile] = File(...)):
    print("got new MAF card")

    maf_cards = []

    insert_results = []

    for card in maf_card_files:
        card_content = decode_file(card)
        maf_cards.extend(parse_catalog_from_str(card_content))

    for maf in maf_cards:
        result = await insert_maf_to_db(maf)
        insert_results.append(result)

    return {"message": f"got {len(maf_cards)} new MAF cards"}


@app.post("/maf/territories/develop")
async def upload_territory_list(territory_plan_file: UploadFile):
    if territory_plan_file.filename.endswith('.xlsx'):
        f_terr_plan = await territory_plan_file.read()
        xlsx = BytesIO(f_terr_plan)

        territories = parse_territory_list(xlsx)

        await update_territory_types_in_db(territories)

        mongo_terr_cards = app.planner_db.get_collection("territory_cards")

        terr_data_to_save = territories["territory_model_cards"]

        write_result = await mongo_terr_cards.insert_many(terr.model_dump() for terr in terr_data_to_save)
        if write_result.acknowledged:
            print(f"uploaded {len(write_result.inserted_ids)} items of territory plan")

    return {
        "result": "ok"
    }


async def update_areas_add_demography(dem_data: list):
    mongo_terr_cards = app.planner_db.get_collection("territory_cards")
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


@app.post("/maf/territories/demography")
async def upload_area_demography(demography_file: UploadFile):
    if demography_file.filename.endswith('.xlsx'):
        f_area_dem = await demography_file.read()
        xlsx = BytesIO(f_area_dem)

        demography_data = parse_area_demography(xlsx)
        await update_areas_add_demography(demography_data["parsed_records"])


    return {
        "result": "ok"
    }


async def update_territory_types_in_db(territories):
    terr_classes = territories["area_types_classes"]
    extracted_terr_types = []
    types_to_save = []
    mongo_terr_types = app.planner_db.get_collection("territory_types")
    for terr_class_name in terr_classes.keys():
        for t_type in terr_classes[terr_class_name]:
            terr_type_to_save = {
                "terr_type_name": t_type,
                "terr_class": terr_class_name
            }
            extracted_terr_types.append(terr_type_to_save)
    exist_t_type_cursor = mongo_terr_types.find({}, {"terr_type_name": 1})
    existing_t_types = await exist_t_type_cursor.to_list(length=100)
    known_t_types = map(lambda t: t["terr_type_name"], existing_t_types)
    for terr_type in extracted_terr_types:
        terr_type_name = terr_type["terr_type_name"]
        if terr_type_name not in known_t_types:
            types_to_save.append(terr_type)
    if len(types_to_save) > 0:
        save_res = await mongo_terr_types.insert_many(types_to_save)
        print(f"{len(types_to_save)} new territory type(s) saved")


PLANNER_DB = "landscape_planner_data"


@app.on_event("startup")
async def connect_to_mongo():
    DB_URL = config('MONGO_URL', cast=str)
    app.mongodb_client = AsyncIOMotorClient(DB_URL)
    app.planner_db = app.mongodb_client[PLANNER_DB]


@app.on_event("shutdown")
async def disconnect_from_mongo():
    app.mongodb_client.close()
