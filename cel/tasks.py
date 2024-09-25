import random
import time
from typing import Optional

from .celery import celery_app

import hashlib
from PIL import Image
import io, os

from datetime import datetime
import logging
logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_picture(
        self,
        img_path: str,
        resize_width: Optional[int] = None,
        resize_height: Optional[int] = None,
        compression: Optional[int] = None,
        watermark: Optional[int] = None,
        ):
    """
    Обрабатывает картинку по заданным параметрам
    """
    current_task_id = self.request.id
    logger.debug(f"CURRENT TASK ID {current_task_id}")
    logger.debug(f"Opening image: '{img_path}'")

    with Image.open(img_path) as im:
        print(im.format, f"{im.size}x{im.mode}")

        new_w = resize_width if resize_width else im.size[0]
        new_h = resize_height if resize_height else im.size[1]

        im = im.resize((
                new_w,  
                new_h
            ))

        #Добавляем ватермарку
        foreground = Image.open('cel/res/wt.png').convert("RGBA")
        width, height = im.size
        # transparent = Image.new("RGBA", (width, height), (0,0,0,0))
        # transparent.paste(im, (0,0))
        
        im.paste(foreground, (0,0), foreground)

        new_store_path = os.path.join(os.getenv("EDIT_STORE_PATH"), f"{current_task_id}.jpg")

        if compression:
            im.save(new_store_path, optimize=True, quality=compression)
        else:
            im.save(new_store_path)
    

        return {
                "status": "Completed",
                "img_path": new_store_path,
                }

