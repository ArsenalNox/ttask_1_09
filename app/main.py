import logging
import uvicorn
import sys

from fastapi import Depends, FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import (
        users, pictures
    )

import os
from app import Tags, logger

app = FastAPI()

origins = [
    # "http://127.0.0.1",
    # "http://127.0.0.1:8000",
    # "https://127.0.0.1",
    # "http://localhost",
    # "http://localhost:8080",
    "*"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    users.router,
    prefix="/api",
    tags=[Tags.users]
)

app.include_router(
    pictures.router,
    prefix="/api",
    tags=[Tags.pictures]
)



if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)