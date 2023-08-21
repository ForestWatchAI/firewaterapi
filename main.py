from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from pydantic import BaseModel
import requests
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from datetime import datetime

currenttime = datetime.now()
capturelocation = "Zone A : Sensor 1"

app = FastAPI()


class FireSensorData(BaseModel):
    firesensordata: int


class FloodSensorData(BaseModel):
    floodsensordata: int


mongo_uri = "mongodb+srv://forestwatchai:hackathon%4069@forestwatchai.kshtlwm.mongodb.net/"


mongo_client = MongoClient(mongo_uri)
db = mongo_client["main_db"]
collection1 = db["forest_fire_data"]
collection2 = db["forest_flood_data"]


emailapi_url = "https://emailapi-lfle.onrender.com"

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {
    "status":"running successfully"
    }


@app.post("/alert/fire/{firesensordata}")
def alert_fire(firesensordata: int):
    email_data = {
        "subject": f"URGENT: Fire Alert in the Forest {capturelocation}",
        "body": f'''Dear Forest Watch Team,

This is to alert you about a critical fire situation with temperatures reaching {firesensordata} degrees Celsius within the forest. Immediate action is imperative. The detection was confirmed at {currenttime.strftime("%H:%M:%S, %Y-%m-%d")} at {capturelocation}.


Please activate all emergency protocols, coordinate with firefighting units, and implement precautionary measures to contain and extinguish the fire.

Best regards,
Forest Watch AI

[Note: This email is generated automatically by the Forest Watch AI API. Please do not reply to this email. For any queries or concerns, contact the Forest Watch Team.]''',
        "imagedata": ""
    }
    response = requests.post(
        f"{emailapi_url}/sendmail/",
        json=email_data
    )


@app.post("/alert/flood/{floodsensordata}")
def alert_flood(floodsensordata: int):
    email_data = {
        "subject": f"URGENT: Flood Alert in the Forest {capturelocation}",
        "body": f'''Dear Forest Watch Team,

This is to alert you about a severe forest flood alert due to rapidly rising water levels reaching {floodsensordata} centimetres at {currenttime.strftime("%H:%M:%S, %Y-%m-%d")}. The area at {capturelocation} is experiencing critical flooding conditions that demand immediate attention.


Activate all emergency protocols without delay. Coordinate with relevant teams, including rescue and relief units, to ensure the safety and well-being of all living entities in the forest.

Best regards,
Forest Watch AI

[Note: This email is generated automatically by the Forest Watch AI API. Please do not reply to this email. For any queries or concerns, contact the Forest Watch Team.]''',
        "imagedata": ""
    }
    response = requests.post(
        f"{emailapi_url}/sendmail/",
        json=email_data
    )


@app.post("/insert_into_forest_fire_data/", response_model=dict)
def insert_into_forest_fire_data(firesensordata):
    inserted_data = collection1.insert_one(
        jsonable_encoder({"Temperature": firesensordata,
                          "capturetime": currenttime.strftime("%H:%M:%S , %Y-%m-%d"),
                          "capturelocation": capturelocation}))


@app.post("/insert_into_forest_flood_data/", response_model=dict)
def insert_into_forest_flood_data(floodsensordata):
    inserted_data = collection2.insert_one(
        jsonable_encoder({"Temperature": floodsensordata,
                          "capturetime": currenttime.strftime("%H:%M:%S , %Y-%m-%d"),
                          "capturelocation": capturelocation}))


@app.post("/firedetector")
def firedetector(firesensordata: FireSensorData):
    if firesensordata.firesensordata > 100:
        insert_into_forest_fire_data(firesensordata.firesensordata)
        alert_fire(firesensordata.firesensordata)
        return f'Forest Fire Alert'
    else:
        return f'Temperature is normal. No fire alerts'


@app.post("/flooddetector")
def flooddetector(floodsensordata: FloodSensorData):
    if floodsensordata.floodsensordata > 50:
        insert_into_forest_flood_data(floodsensordata.floodsensordata)
        alert_flood(floodsensordata.floodsensordata)
        return f'Forest Flood Alert'
    else:
        return f'Water level is normal. No flood alerts'
