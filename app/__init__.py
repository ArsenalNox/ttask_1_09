from dotenv import load_dotenv

import os

from enum import Enum

import logging
import logging.config

load_dotenv()

logger = logging.getLogger(__name__)

class Tags(Enum):
    users = "Users"
    pictures = 'Pictures'

