from io import BytesIO

from fastapi import APIRouter, UploadFile
from starlette.responses import JSONResponse

from areas.logic.parse_territories import parse_territory_list
from db import mongo

areas_router = APIRouter()


@areas_router.get("/swap/coord")
async def swap_lat_lon():
    mongo_terr_cards_coll = mongo.db.get_collection("territory_cards")
    all_cards_cursor = mongo_terr_cards_coll.find({})
    all_cards = await all_cards_cursor.to_list(length=10000)

    card_updates = {

    }

    for card in all_cards:
        card_id = card["terr_id"]
        card_contour = card["contour"]

        if len(card_contour["coordinates"]) > 0:
            coords = card_contour["coordinates"][0]

            for point_coords in coords:
                point_coords.reverse()

        card_updates[card_id] = {
            "contour": card_contour
        }

        card_geo = card["geo_data_all"]
        if len(card_geo["wgs84"]) > 0:
            if len(card_geo["wgs84"][0]) > 0:
                for poly in card_geo["wgs84"][0]:
                    for point_coords in poly:
                        point_coords.reverse()
        card_updates[card_id]["geo_data_all"] = card_geo

    for id_to_upd in card_updates.keys():
        upd_rs = await mongo_terr_cards_coll.update_one(
                                                    {"terr_id": id_to_upd},
                                                    {
                                                        "$set": {
                                                            "contour": card_updates[id_to_upd]["contour"],
                                                            "geo_data_all": card_updates[id_to_upd]["geo_data_all"]
                                                        }
                                                    }
                                                )

    response_data = {
        "status": "ok"
    }

    return JSONResponse(status_code=200, content=response_data)




async def update_territory_types_in_db(territories):
    terr_classes = territories["area_types_classes"]
    extracted_terr_types = []
    types_to_save = []
    mongo_terr_types = mongo.db.get_collection("territory_types")
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


@areas_router.post("/upload")
async def upload_territory_list(territory_plan_file: UploadFile):
    if territory_plan_file.filename.endswith('.xlsx'):
        f_terr_plan = await territory_plan_file.read()
        xlsx = BytesIO(f_terr_plan)

        territories = parse_territory_list(xlsx)

        await update_territory_types_in_db(territories)

        mongo_terr_cards = mongo.db.get_collection("territory_cards")

        terr_data_to_save = territories["territory_model_cards"]

        write_result = await mongo_terr_cards.insert_many(terr.model_dump() for terr in terr_data_to_save)
        if write_result.acknowledged:
            print(f"uploaded {len(write_result.inserted_ids)} items of territory plan")

    return {
        "result": "ok"
    }


@areas_router.get("/maf/territories/backup/all")
async def backup_all_area_data():
    response_data = {
        "status": "ok"
    }

    areas_collection = mongo.db.get_collection("territory_cards")
    get_areas_cursor = areas_collection.find({}, {"_id": 0})

    all_areas = await get_areas_cursor.to_list(length=10000)

    areas_collection_bckup = mongo.db.get_collection("territory_cards_bckup3")
    bckup_rs = await areas_collection_bckup.insert_many(all_areas)

    return JSONResponse(status_code=200, content=response_data)



