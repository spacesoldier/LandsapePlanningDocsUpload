import json
from decimal import Decimal

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

from typing import List
from io import StringIO
from models import MafCard, parse_catalog_from_str, parse_territory_list

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


@app.post("/maf/territories")
async def upload_territory_list(territory_plan_file: UploadFile):
    if territory_plan_file.filename.endswith('.xlsx'):
        f_terr_plan = await territory_plan_file.read()
        xlsx = BytesIO(f_terr_plan)

        territories = parse_territory_list(xlsx)



        print(f"uploaded territory plan")

    return {
        "result": "ok"
    }


PLANNER_DB = "landscape_planner_data"

@app.on_event("startup")
async def connect_to_mongo():
    DB_URL = config('MONGO_URL', cast=str)
    app.mongodb_client = AsyncIOMotorClient(DB_URL)
    app.planner_db = app.mongodb_client[PLANNER_DB]


@app.on_event("shutdown")
async def disconnect_from_mongo():
    app.mongodb_client.close()
