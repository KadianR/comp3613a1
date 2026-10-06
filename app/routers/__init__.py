from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.utilities.flash import get_flashed_messages
from jinja2 import Environment, FileSystemLoader
from app.config import get_settings


template_env = Environment(loader = FileSystemLoader("app/templates",), )
template_env.globals['get_flashed_messages'] = get_flashed_messages


def accommodation_image(accommodation) -> str:
	if getattr(accommodation, "image_url", None):
		return accommodation.image_url
	accommodation_id = accommodation.id
	upload_dir = Path("app/static/uploads")
	uploaded_images = sorted(upload_dir.glob(f"accommodation-{accommodation_id}-*"))
	if uploaded_images:
		return f"/static/uploads/{uploaded_images[0].name}"
	return "/static/img/accommodation-placeholder.svg"


template_env.globals['accommodation_image'] = accommodation_image
templates = Jinja2Templates(env=template_env)
static_files = StaticFiles(directory="app/static")

router = APIRouter(tags=["Jinja Based Endpoints"], include_in_schema=get_settings().env.lower() in ["dev","development"])
api_router = APIRouter(tags=["API Endpoints"], prefix="/api")

from . import (index, login, register, admin_home, user_home, users, logout, server_config, accommodations, landlord_requests, landlord_properties, reviews)