import uuid, re, json, copy, hashlib
import random
from typing import List, Optional, Any
from typing import Union, Tuple, Optional, Dict, List
from uuid import UUID as m_uuid

from sqlalchemy import (
    create_engine, Column, Integer, String, 
    DateTime, Text, ForeignKey, Float, 
    Boolean, BigInteger, UUID, Text, Table)

from sqlalchemy.orm import declarative_base, relationship, backref, Session, Mapped, joinedload, sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy.sql import func
from datetime import datetime
from dotenv import load_dotenv
from os import getenv
from fastapi import HTTPException
from app import logger
from PIL import Image

import hashlib
import os

load_dotenv()


connection_url = URL.create(
    drivername="postgresql",
    username=getenv("POSTGRES_USER"),
    host=getenv("POSTGRES_HOST"),
    port=getenv("POSTGRES_PORT"),
    database=getenv("POSTGRES_DB"),
    password=getenv("POSTGRES_PASSWORD"),
)

logger.debug("postgresql")
logger.debug(getenv("POSTGRES_USER"))
logger.debug(getenv("POSTGRES_HOST"))
logger.debug(getenv("POSTGRES_PORT"))
logger.debug(getenv("POSTGRES_DB"))
logger.debug(getenv("POSTGRES_PASSWORD"))

Base = declarative_base()

def default_time():
    return datetime.now()


class Users(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    date_created = Column(DateTime(), default=default_time)
    last_updated = Column(DateTime(), default=default_time)
    
    email = Column(String(), unique=True, nullable=True)
    password = Column(String(), nullable=True)


    async def create_new(session: Session):
        pass


    async def get_or_create(session: Session):
        pass

    
    async def query_filtered(session: Session, filter):
        pass


class Pictures(Base):
    __tablename__ = 'pictures_original'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_created = Column(DateTime(), default=default_time)
    path = Column(String(), nullable=False)
    pic_hash = Column(String(), nullable=False)
    
    async def process_upload(img_hash: str, img_data, filename, session: Session, ):
        print("PROCESSING UPLOAD")
        img_hash_query = session.query(Pictures).filter(Pictures.pic_hash == img_hash).first()
        logger.info("Processing upload")
        if img_hash_query:
            logger.debug("Image has in database")
            #Изображение уже сохранено, отправить на обработку
            return img_hash_query
            
        #запустить таску
        store_path = os.path.join(os.getenv("DATA_STORE_PATH"), f"{img_hash}.{str(filename).split('.')[-1]}")
        logger.debug(store_path)

        img_data.save(store_path)

        logger.debug(os.path.isfile(store_path))

        new_pic = Pictures(
            path=store_path,
            pic_hash=img_hash
        )
        session.add(new_pic)

        return new_pic


    def process_picture(__self__, resize_height, resize_width, compression, watermark, session: Session):
        """
        Обработать изображение
        """
        logger.debug(f"Opening image: '{__self__.path}'")

        try:
            with Image.open(__self__.path) as im:
                print(im.format, f"{im.size}x{im.mode}")
        
                new_w = resize_width if resize_width else im.size[0]
                new_h = resize_height if resize_height else im.size[1]

                im = im.resize((
                        new_w,  
                        new_h
                    ))

                date_name=datetime.strftime( datetime.now(), "%Y-%m-%d_%H-%M-%S.%f") 
                new_store_path = os.path.join(os.getenv("EDIT_STORE_PATH"), f"{date_name}_{__self__.pic_hash}.jpg")

                if compression:
                    im.save(new_store_path, optimize=True, quality=compression)
                else:
                    im.save(new_store_path)
            

                new_edited_picture = PicturesEdited(
                    path=new_store_path,
                    pic_name=f"{date_name}_{__self__.pic_hash}.jpg",
                    child_of=__self__.id
                )
                session.add(new_edited_picture)

                return new_edited_picture

        except OSError as err:
            print(err)
            raise HTTPException(
                status_code=501,
                detail="Неудалось обработать изображение"
                )
        

class PicturesEdited(Base):
    __tablename__ = "pictures_edited"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_created = Column(DateTime(), default=default_time)
    path = Column(String(), nullable=False)
    pic_name = Column(String(), nullable=False)
    child_of = Column(UUID(as_uuid=True), ForeignKey('pictures_original.id'))

    async def get_by_hash():
        pass

logger.debug(connection_url)
logger.debug("Creating engine...")

engine = create_engine(connection_url)
session_local = sessionmaker(expire_on_commit=False, autoflush=False, bind=engine)

logger.debug("Creating database...")
try:
    if bool(os.getenv("CREATE_DATABASE")):
        Base.metadata.create_all(bind=engine)
except Exception as err:
    logger.critical(err)
    logger.critical("Failed to create database")

def get_db()->Session|Any:
    database = session_local()
    try:
        yield database
    finally:
        database.close()
