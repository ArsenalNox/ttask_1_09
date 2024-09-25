import uuid

from pydantic import BaseModel, EmailStr, UUID4, Field, ValidatorFunctionWrapHandler, validator, field_validator
from typing import Optional, Annotated, Any, List, Union, Tuple
from typing_extensions import TypedDict
from datetime import datetime


class PictureEditData(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    compression: Optional[float] = None
    watermark: Optional[str] = None #Добавляет указанный текст в виде ватермарки

