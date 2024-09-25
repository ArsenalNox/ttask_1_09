from sqlalchemy.orm import Session, joinedload

from typing import Optional, Annotated, Any, List, Union, Tuple
from fastapi import APIRouter, Body, Security, Query, Depends, HTTPException, Request, Response, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends

from app.models import get_db, Pictures
from app import logger
from app.validators import PictureEditData

import hashlib
from PIL import Image
import io, os

from celery import Celery
from dotenv import load_dotenv
load_dotenv()

celery_app = Celery(
    "cel",
    broker=f"redis://{os.getenv('REDIS_HOST')}:6379/0",
    backend=f"redis://{os.getenv('REDIS_HOST')}:6379/1",
    include=["cel.tasks"],
)

router = APIRouter()

@router.post("/picture/edit")
async def modify_picture(
    file: UploadFile,
    resize_width: Optional[int] = None,
    resize_height: Optional[int] = None,
    compression: Optional[int] = None,
    watermark: Optional[str] = None,
    session: Session = Depends(get_db),
):
    #Загрузить изображение
    #Записать хеш изображения в бд
    #Отправить изображение в целери на обработку, Записать айди к хешу
    #Вернуть айди таски

    plain_picture_data = await file.read()

    logger.debug(f"Processing filename: {file.filename}")
    img = Image.open(io.BytesIO(plain_picture_data))
    img_hash = hashlib.md5(img.tobytes()).hexdigest()

    logger.debug(f"height: '{resize_height}', width: '{resize_width}'")
    logger.debug(f"compression: {compression}, watermark: {watermark}")
    logger.debug("TEST RUN TASK")
    logger.debug(f"image hash: {img_hash}")

    try:
        new_pic = await Pictures.process_upload(
            img_hash=img_hash,
            img_data=img,
            session=session,
            filename=file.filename
            )
    except Exception as err:
        logger.error(f"Failed to save picture, err; {err}")
        raise HTTPException(status_code=500, detail='Произошла ошибка при загрузке изображения')

    session.commit()

    logger.debug(f'Saved path: {new_pic.path}')
    logger.debug(os.path.isfile(new_pic.path))

    # await new_pic.process_picture(
    #     resize_height=resize_height,
    #     resize_width=resize_width,
    #     compression=compression,
    #     watermark=watermark,
    #     session=session
    #     )

    # session.commit()

    logger.debug(new_pic.id)
    task = celery_app.send_task("cel.tasks.process_picture", args=[], kwargs={
        "resize_height": resize_height,
        "resize_width": resize_width,
        "compression": compression,
        "watermark": watermark,
        "img_path": new_pic.path
    })

    return JSONResponse(
        {"task_id": task.id}
    )

    return new_pic


@router.get('/picture/edited/{filename}')
def return_edited_picture(filename):
    return FileResponse(f'/app/data/{filename}')


@router.get("/picture/status/{task_id}")
def picture_status(task_id):
    """Query tasks status."""
    task = celery_app.AsyncResult(task_id)
    logger.debug(task.state)
    logger.debug(task)
    if task.state == "PENDING":
        response = {
            "state": task.state,
            "status": "Pending...",
        }
    elif task.state != "FAILURE":
        response = {
            "state": task.state,
            "status": task.info.get("status", ""),
        }
        if "img_path" in task.info:
            response["result"] = task.info["img_path"]
    else:
        response = {
            "state": task.state,
            "status": str(task.info),  
        }
    return response