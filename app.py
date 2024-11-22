"""FastAPI server."""

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

try:
    app = FastAPI()

except Exception as e:
    print(e)


@app.get("/health")
async def health_check():
    msg: dict = {}
    msg["response"] = "server is alive and healthy!!!"
    json_compatible_msg = jsonable_encoder(msg)
    return JSONResponse(json_compatible_msg, status_code=200)
