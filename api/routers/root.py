from fastapi import APIRouter, HTTPException, Request, Header
from datetime import datetime
from typing import Annotated, Optional
import sys
import os

api_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(api_root_dir)

from libraries.cloudflare.tool import get_user_ip

# private
from private.tool import check_server_2_status


class RootRouter:
    def __init__(self, access, prefix="", tags=["root"]):
        self.router = APIRouter(prefix=prefix, tags=tags)

        self.access = access

        @self.router.get(path="/")
        def read_root(request: Request):
            return {
                "responseDate": datetime.now(),
                "contentTopic": "Read root tab.",
                "ResponseData": {
                    "apiMessage": f"Check documents to get more information. Link: {request.base_url}docs",
                }
            }

        @self.router.get("/status")
        async def read_status():
            status_code = check_server_2_status()
            return {
                "responseDate": datetime.now(),

                "contentTopic": "Get server status tab.",
                "ResponseData": {
                    "serverStatus": {
                        "server-1-Online": True,
                        "server-2-Online": status_code,
                    }
                }
            }

        @self.router.put("/click")
        def increase_page_views(request: Request):
            user_ip = get_user_ip(request)
            self.access.count_page_views(user_ip)
            return {
                "responseDate": datetime.now(),
                "contentTopic": "Increase page views.",
                "ResponseData": {
                    "success?": True,
                    "__comment__": "YES! Finally it works."
                }
            }

        @self.router.get("/print")
        def find_pages(request: Request,
                       sec_ch_ua: Annotated[Optional[str], Header(alias="Sec-CH-UA")] = None,
                       sec_ch_ua_mobile: Annotated[Optional[str], Header(alias="Sec-CH-UA-Mobile")] = None,
                       sec_ch_ua_platform: Annotated[Optional[str], Header(alias="Sec-CH-UA-Platform")] = None,
                       ):
            return {
                "responseDate": datetime.now(),
                "contentTopic": "Print request info.",
                "ResponseData": {
                    "requestData": {
                        "headers": request.headers,
                        "body": request.body,
                        "sec_ch_ua": sec_ch_ua,
                        "sec_ch_ua_mobile": sec_ch_ua_mobile,
                        "sec_ch_ua_platform": sec_ch_ua_platform,
                    },
                }
            }