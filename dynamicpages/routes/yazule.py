from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from datetime import datetime
import sys
import os

dp_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(dp_root_dir)

from api.tool import get_user_ip, check_turnstile_token

# private
from api.private import check_register_token, check_login_token, unban_ip

class YazuleRouter:
    def __init__(self, resources, cloudflare_cfg, pages,prefix="/yazule", tags=["yazule"]):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.resources = resources

        self.pages = pages
        self.cloudflare_cfg = cloudflare_cfg

        @self.router.get("/v1", response_class=HTMLResponse)
        @self.router.get("/v1/login", response_class=HTMLResponse)
        async def yazule_login(request: Request):
            return HTMLResponse(self.pages.get_html("yazule/v1/login_1.html", request))

        @self.router.get("/v1/register", response_class=HTMLResponse)
        def yazule_register(request: Request):
            return HTMLResponse(self.pages.get_html("yazule/v1/register_1.html", request))

        @self.router.get("/v1/iforgot", response_class=HTMLResponse)
        def yazule_register(request: Request):
            return HTMLResponse(self.pages.get_html("yazule/v1/iforgot_1.html", request))

        @self.router.get("/v1/finished", response_class=HTMLResponse)
        def yazule_finished(request: Request):
            return HTMLResponse(self.pages.get_html("yazule/v1/finished_register.html", request))

        @self.router.get("/v1/register_valid", response_class=HTMLResponse)
        async def yazule_register(request: Request, register_token: str):
            user_ip = get_user_ip(request)
            result = check_register_token(register_token, user_ip, "kuaikuaiissocute")

            if not result:
                return HTMLResponse(self.pages.get_html("yazule/v1/expired.html", request), status_code=401)
            else:
                return HTMLResponse(self.pages.get_html("yazule/v1/register_2.html", request))

        @self.router.get("/v1/login_valid", response_class=HTMLResponse)
        async def yazule_login(login_token: str, request: Request):
            user_ip = get_user_ip(request)
            result, account_address = check_login_token(login_token, user_ip, "kuaikuaiissocute")

            if result is False:
                print("false")
                return HTMLResponse(self.pages.get_html("yazule/v1/expired.html", request), status_code=401)
            else:
                print("true")
                html = self.pages.pages_util.insert_account_address_to_login_page(self.pages.get_html("yazule/v1/login_2.html", request), account_address)
                print("true 2")
                return HTMLResponse(html, status_code=200)

        @self.router.get("/security/botcheck", response_class=HTMLResponse)
        async def yazule_botcheck(request: Request):
            return HTMLResponse(self.pages.get_html("yazule/security/botcheck.html", request))

        @self.router.get("/v1/unban", response_class=HTMLResponse)
        async def yazule_unban(turnstile_token, request: Request):
            user_ip = get_user_ip(request)
            result = check_turnstile_token(turnstile_token, self.cloudflare_cfg.get("turnstile-secret-token"),
                                           user_ip)

            if not result:
                return RedirectResponse(url=f"{request.base_url}yazule/security/botcheck.html")
            else:
                result = unban_ip(user_ip, turnstile_token,
                                  "kuaikuaiissocute")

                if result is False:
                    return RedirectResponse(url=f"{request.base_url}yazule/security/botcheck.html")

            return RedirectResponse(url=f"{request.base_url}")