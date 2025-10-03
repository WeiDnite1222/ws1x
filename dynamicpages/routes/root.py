from fastapi import APIRouter, HTTPException, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse, JSONResponse
from datetime import datetime
import sys
import os



class RootRouter:
    def __init__(self, web_root_dir, pages, resources, prefix="", tags=["root"]):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.pages = pages
        self.resources = resources
        self.web_root_dir = web_root_dir

        @self.router.get("/", response_class=HTMLResponse)
        @self.router.get("/home", response_class=HTMLResponse)
        @self.router.get("/index", response_class=HTMLResponse)
        @self.router.get("/home.html", response_class=HTMLResponse)
        @self.router.get("/index.html", response_class=HTMLResponse)
        async def home_page(request: Request):
            return HTMLResponse(self.pages.get_html("home.html", request))

        @self.router.get("/blog", response_class=HTMLResponse)
        @self.router.get("/blog.html", response_class=HTMLResponse)
        async def blog_page(request: Request):
            return HTMLResponse(self.pages.get_html("blog.html", request))

        @self.router.get("/login", response_class=HTMLResponse)
        @self.router.get("/login.html", response_class=HTMLResponse)
        async def redirect_login_page():
            return RedirectResponse(url="https://www.weispace.net/yazule/v1")

        @self.router.get("/register", response_class=HTMLResponse)
        @self.router.get("/register.html", response_class=HTMLResponse)
        async def redirect_register_page():
            return RedirectResponse(url="https://www.weispace.net/yazule/v1/register")

        @self.router.get("/request_info", response_class=HTMLResponse)
        async def get_request_info(request: Request):
            return JSONResponse(
                content={
                    "title": "Request Info",
                    "headers": str(request.headers),
                    "body": str(request.body),
                }
            )

        @self.router.get("/{full_path:path}")
        async def serve_static(full_path: str, request: Request):
            file_path = os.path.join(self.web_root_dir, full_path)
            if full_path in self.resources.resources.keys() or (os.path.exists(file_path) and os.path.isfile(file_path)):
                if file_path.endswith(".html"):
                    return HTMLResponse(self.pages.get_html(full_path, request))
                else:
                    return FileResponse(file_path)

            raise HTTPException(status_code=404)