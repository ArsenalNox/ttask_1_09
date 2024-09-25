from sqlalchemy.orm import Session, joinedload

from fastapi import APIRouter, Body, Security, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends

from app.models import get_db
from app import logger
# from app.validators import 

router = APIRouter()


@router.get("/clients")
async def get_clients(
    session: Session = Depends(get_db)
):
    logger.debug("Getting clients")
    pass