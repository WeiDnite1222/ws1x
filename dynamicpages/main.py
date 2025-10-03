import os, sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.root import RootRouter
from routes.subsites import SubsitesRouter
from routes.yazule import YazuleRouter
from config import DPConfig
from web.dynamic import DynamicResourceUpdater, DynamicPagesDaemon
from daemon.rpe import DynamicPagesServiceDaemon
from exception.handler import ExceptionHandler
from api.private import check_banned
from api.tool import get_user_ip

__version__ = 0.3

space_net_lib_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(space_net_lib_dir)

from space_net_lib.definition.path import dynamic_pages_data_path
from space_net_lib.logger.logger import DefaultLogger

log_file_path = os.path.join(dynamic_pages_data_path, "logs", "current.logs")
logger = DefaultLogger("DynamicPagesLogger", log_file_path)
config = DPConfig(logger=logger)

resources = DynamicResourceUpdater(config.dynamic_main)
pages = DynamicPagesDaemon(logger=logger, resources_updater=resources,
                            full_config=config,
                           version=__version__)
resources.start()
pages.start()

app = FastAPI(title=config.dynamic_main.get("server-name"))

service = DynamicPagesServiceDaemon(logger=logger, fastapi=app)
exception_handler = ExceptionHandler(app, resources, error_page_cfg=config.error_pages, web_root_dir=config.dynamic_main.get("webRootDir"))

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def check_ip_middleware(request: Request, call_next):
    user_ip = get_user_ip(request)
    if request.url.path not in ["/yazule/security/botcheck", "/yazule/v1/unban"]:
        result = check_banned(user_ip, config.communicate_support.get("communicate_token", "<NULL>"))
        if result:
            return RedirectResponse(url=f"{request.base_url}yazule/security/botcheck")

    return await call_next(request)


root_router = RootRouter(pages=pages, resources=resources, web_root_dir=config.dynamic_main.get("webRootDir"))
yazule_router = YazuleRouter(resources=resources, pages=pages, cloudflare_cfg=config.dp_cloudflare)
subsites_router = SubsitesRouter()

app.include_router(yazule_router.router)
app.include_router(subsites_router.router)
app.include_router(root_router.router)