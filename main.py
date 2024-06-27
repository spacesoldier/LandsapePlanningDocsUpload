from fastapi import FastAPI

from areas.api.areas_router import areas_router
from db import mongo
from demography.api.demography_router import demography_router
from mafs.api.mafs_router import mafs_router


from decouple import config


app = FastAPI()

app.include_router(mafs_router, prefix="/maf/catalog")
app.include_router(areas_router, prefix="/maf/territories")
app.include_router(demography_router, prefix="/maf/demography")

PLANNER_DB = "landscape_planner_data"


@app.on_event("startup")
async def connect_to_mongo():
    DB_URL = config('MONGO_URL', cast=str)
    mongo.connect_to_mongo(DB_URL, PLANNER_DB)


@app.on_event("shutdown")
async def disconnect_from_mongo():
    mongo.disconnect_from_mongo()


