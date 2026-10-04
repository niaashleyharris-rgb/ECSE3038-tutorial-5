import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError #importing the error that is raised when a duplicate key is inserted into a collection

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


# Your handlers go below this line.

@app.get("/devices")
def get_devices():
    return list(devices.find({},{"_id":0}))


@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if device is None:
        raise HTTPException(status_code=404,
                            detail="No device called " + name)
    return device


@app.post("/devices", status_code=201)
def create_device(device: Device):
    new_device = device.model_dump()
    try:
        devices.insert_one(new_device)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail=f"Device with name {device.name} already exists")
    new_device.pop("_id")
    return new_device

#create a put handler that PUT /devices/{name}
@app.put("/devices/{name}")
def update_device(name: str, device: Device):
    result = devices.replace_one({"name": name}, device.model_dump())
    if result.matched_count == 0:
        raise HTTPException(status_code=404,
                            detail="No device called " + name)
    return device

#write a delete handler that DELETE /devices/{name}
@app.delete("/devices/{name}")
def delete_device(name: str):
    result = devices.delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404,
                            detail="No device called " + name)
    return {"message": "Device deleted"}