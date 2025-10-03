import os
import sys
import json
import yaml
import logging
import uvicorn
import traceback
from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from libraries.cloudflare.tool import get_user_ip
from database.database import DatabaseManager
from access.access import Access
from yazule.yazule import Yazule
from config import APIConfig, D2OUpdater

# Router
from routers.root import RootRouter
from routers.account import AccountRouter
from routers.sites import SitesRouter
from routers.tab import TabRouter
from routers.private import PrivateRouter

space_net_lib_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(space_net_lib_dir)

from space_net_lib.definition.path import api_data_path
from space_net_lib.logger.logger import DefaultLogger

root_dir = os.path.dirname(os.path.abspath(__file__))

log_file_path = os.path.join(api_data_path, "logs", "current.logs")
logger = DefaultLogger("APILogger", log_file_path)
config = APIConfig(logger=logger)
database = DatabaseManager(config=config.api_database, logger=logger)
access = Access(database=database, config=config.api_access, logger=logger)
yazule = Yazule(database=database, config=config.api_yazule, logger=logger)

app = FastAPI(title=config.api_main.get("server-name"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    user_ip = get_user_ip(request)

    print((await request.body()).decode("utf-8", errors="ignore"))

    try:
        body = (await request.body()).decode("utf-8", errors="ignore")
    except Exception:
        body = "<unreadable>"
    logger.error(
        "Server response 422 when IP %s access method %s:%s\n"
        "Headers: %s\n"
        "Body: %s\n"
        "Exception: %s",
        user_ip, request.method, request.url.path,
        dict(request.headers), body[:4000], exc.errors()
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

@app.middleware("http")
async def check_ip_middleware(request: Request, call_next):
    client_ip = get_user_ip(request)

    # The IP with communicate_token(valid) can bypass access limit
    authorization_header = request.headers.get("Authorization")
    if authorization_header is not None and authorization_header.startswith("Bearer "):
        token = authorization_header.replace("Bearer ", "")
        if token == config.api_communicate_support.get('communicate_token'):
            return await call_next(request)
        else:
            logger.warning("The request from IP %s with an invalid credentials token.\n"
                           "If this IP is from your server, please check that the token"
                           " for the other service is set correctly.", client_ip)

    try:
        ban_status, end_date = access.is_banned(client_ip)
    except Exception as e:
        logger.error("An error occurred while checking ban list: %s", e)
        return await call_next(request)

    if ban_status:
        message = f"You can't access the API until {end_date}" if end_date is not None else "This restriction may be permanent."
        return JSONResponse(
            status_code=429,
            content={"detail": "You got ip banned. {}".format(message)},
        )

    return await call_next(request)

root_router = RootRouter(access=access)
sites_router = SitesRouter()
tab_router = TabRouter(yazule=yazule)
account_router = AccountRouter(yazule=yazule, communicate_config=config.api_communicate_support)
private_router = PrivateRouter(yazule_config=config.api_yazule,
                               communicate_config=config.api_communicate_support,
                               access=access)

app.include_router(root_router.router)
app.include_router(sites_router.router)
app.include_router(tab_router.router)
app.include_router(account_router.router)
app.include_router(private_router.router)

@app.on_event("startup")
async def on_startup():
    pass

@app.on_event("shutdown")
async def on_shutdown():
    logger.closing()