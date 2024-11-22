"""FastAPI server."""

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

try:
    app = FastAPI()

except Exception as e:
    print(e)


@app.get("/")
async def root():
    msg: dict = {}
    msg["response"] = "Welcome to the Backend RAG Microservice!!!"
    json_compatible_msg = jsonable_encoder(msg)
    return JSONResponse(json_compatible_msg, status_code=200)


@app.get("/health")
async def health_check():
    msg: dict = {}
    msg["response"] = "The Server is alive and healthy!!!"
    json_compatible_msg = jsonable_encoder(msg)
    return JSONResponse(json_compatible_msg, status_code=200)
