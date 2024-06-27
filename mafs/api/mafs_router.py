from decimal import Decimal
from typing import List

from fastapi import APIRouter, UploadFile, File

from bson.codec_options import CodecOptions

from bson.codec_options import TypeRegistry
from bson.decimal128 import Decimal128
from bson.codec_options import TypeCodec

from db import mongo
from mafs.logic.maf_card import MafCard
from mafs.logic.parse_mafs import parse_catalog_from_str
from mafs.util.mafs_util import decode_file


class DecimalCodec(TypeCodec):
    python_type = Decimal
    bson_type = Decimal128

    def transform_python(self, value):
        return Decimal128(value)

    def transform_bson(self, value):
        return value.to_decimal()


decimal_codec = DecimalCodec()
type_registry = TypeRegistry([decimal_codec])


async def insert_maf_to_db(new_maf: MafCard):
    codec_opts = CodecOptions(type_registry=type_registry)
    result = mongo.db.get_collection("maf_catalog", codec_options=codec_opts).insert_one(new_maf.model_dump())
    return result


mafs_router = APIRouter()


@mafs_router.post("/items")
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


