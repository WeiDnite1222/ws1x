from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from datetime import datetime
import sys
import os



class PostRouter:
    def __init__(self, web_root_dir, resources, prefix="/post", tags=["post"]):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.resources = resources
        self.web_root_dir = web_root_dir

        @self.router.get("/post/{post_id}")
        async def get_post(post_id: int, request: Request):
            file_path = os.path.join(self.web_root_dir, f"{str(post_id)}.html")
            file_path_in_resources = os.path.join("post", f"{str(post_id)}.html")

            if os.path.isfile(file_path) and os.path.exists(file_path):
                return HTMLResponse(self.pages.get_html(file_path_in_resources, request))
            else:
                return HTMLResponse(self.resources.resources["serverpage/404.html"], status_code=404)