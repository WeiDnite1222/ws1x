from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from datetime import datetime
import sys
import os


class SubsitesRouter:
    def __init__(self, prefix="/subsites", tags=["subsites"]):
        self.router = APIRouter(prefix=prefix, tags=tags)

        @self.router.get("/downloads.html#package=net.wei.bookshelf", response_class=HTMLResponse)
        async def legacy_bookshelf_downloads():
            return RedirectResponse(
                url="https://storage.weispace.net/old_server/0.x/subsites/downloads.html#package=net.wei.bookshelf")

        @self.router.get("/downloads", response_class=HTMLResponse)
        @self.router.get("/downloads.html", response_class=HTMLResponse)
        async def legacy_vdt_downloads():
            return RedirectResponse(url="https://storage.weispace.net/old_server/0.x/subsites/downloads.html")