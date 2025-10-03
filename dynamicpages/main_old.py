import os
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi import FastAPI, Request, Response, HTTPException
from api import check_register_token, get_user_ip
from server_util import WEBResourceUpdater, PagesResourceUpdater
from starlette.exceptions import HTTPException as StarletteHTTPException

root_dir = os.path.dirname(__file__)
web_root_dir = os.path.join(root_dir, "..", "www")

html_resource_updater = WEBResourceUpdater(web_root_dir)
html_resource_updater.start()

pages_resource_updater = PagesResourceUpdater(root_dir, html_resource_updater)
pages_resource_updater.start()

app = FastAPI()

@app.exception_handler(500)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return HTMLResponse(html_resource_updater.resources["500.html"], status_code=500)

@app.exception_handler(404)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return HTMLResponse(html_resource_updater.resources["404.html"], status_code=404)

@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
@app.get("/index", response_class=HTMLResponse)
@app.get("/home.html", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
async def home_page():
    return HTMLResponse(pages_resource_updater.safe_get("home.html"))

@app.get("/blog", response_class=HTMLResponse)
@app.get("/blog.html", response_class=HTMLResponse)
async def blog_page():
    return HTMLResponse(pages_resource_updater.safe_get("blog.html"))


@app.get("/500", response_class=HTMLResponse)
async def crashtest_internal_server_error():
    return HTMLResponse(html_resource_updater.resources["500.html"], status_code=500)

@app.get("/403", response_class=HTMLResponse)
async def forbidden():
    return HTMLResponse(html_resource_updater.resources["403.html"], status_code=403)

@app.get("/crashtest/404", response_class=HTMLResponse)
async def crashtest_not_found():
    return HTMLResponse(html_resource_updater.resources["404.html"], status_code=404)

@app.get("/crashtest/503", response_class=HTMLResponse)
async def crashtest_not_found():
    return HTMLResponse(html_resource_updater.resources["503.html"], status_code=404)

@app.get("/yazule/v1", response_class=HTMLResponse)
async def yazule_login():
    return HTMLResponse(html_resource_updater.resources["login_1.html"], status_code=200)

@app.get("/yazule/v1/register", response_class=HTMLResponse)
def yazule_register():
    return HTMLResponse(html_resource_updater.resources["register_1.html"], status_code=200)

@app.get("/yazule/v1/finished", response_class=HTMLResponse)
def yazule_finished():
    return HTMLResponse(html_resource_updater.resources["finished_register.html"], status_code=200)

@app.get("/yazule/v1/register_valid", response_class=HTMLResponse)
async def yazule_register(request: Request, register_token: str):
    user_ip = get_user_ip(request)
    result = check_register_token(register_token, user_ip, "kuaikuaiissocute")

    if not result:
        return HTMLResponse(html_resource_updater.resources["expired.html"], status_code=404)
    else:
        return HTMLResponse(html_resource_updater.resources["register_2.html"], status_code=200)

@app.get("/yazule/v1/iforgot", response_class=HTMLResponse)
async def yazule_login():
    return HTMLResponse(html_resource_updater.resources["iforgot_1.html"], status_code=200)

@app.get("/yazule/v1/AUTH")
async def yazule_account_name_authentication(account_name: str, request: Request):
    return {"name": account_name, "header": request.headers}

@app.get("/yazule/v1/AUTH")
async def yazule_account_name_authentication(password: str, tab_access_token, request: Request):
    return {"name": password, "header": request.headers}

@app.get("/{full_path:path}")
async def serve_static(full_path: str, request: Request):
    file_path = os.path.join(web_root_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        return HTMLResponse(html_resource_updater.resources["404.html"], status_code=404)