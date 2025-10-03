from fastapi import APIRouter, HTTPException, Request, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from typing import Annotated, Optional
import sys
import os
from pydantic import BaseModel

api_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(api_root_dir)

from libraries.cloudflare.tool import get_user_ip

# private
from private.tool import check_server_2_status
from libraries.cloudflare.tool import check_turnstile_token


class PrivateRouter:
    def __init__(self, yazule_config, communicate_config, access, prefix="/private", tags=["private"]):
        self.router = APIRouter(prefix=prefix, tags=tags)

        self.access = access
        self.yazule_config = yazule_config
        self.communicate_config = communicate_config

        bearer_scheme = HTTPBearer(auto_error=False)

        class CheckIPBanInstance(BaseModel):
            ip: str

        @self.router.post("/check_ip_ban")
        def check_ip_ban(instance: CheckIPBanInstance,
                         creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):

            if not creds or creds.scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Missing bearer token (communicateToken)",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            ctoken = creds.credentials

            if ctoken != self.communicate_config.get("communicate_token", "diwjdisjdu3908e9023"):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid communicate token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            banned, _ = self.access.is_banned(instance.ip)

            return {
                "responseDate": str(datetime.now()),
                "contentTopic": "Check ip status",
                "ResponseData": {
                    "result": {"isBanned": banned},
                }
            }

        class UnBanInstance(BaseModel):
            user_ip: str
            turnstile_token: str

        @self.router.post("/unban")
        def unban_ip_by_turnstile_token(instance: UnBanInstance,
                         creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):

            if not creds or creds.scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Missing bearer token (communicateToken)",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            ctoken = creds.credentials

            if ctoken != self.communicate_config.get("communicate_token", "diwjdisjdu3908e9023"):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid communicate token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            result = check_turnstile_token(instance.turnstile_token, self.yazule_config.get("cf_turnstile_secret_token"), instance.user_ip)

            self.access.unban(instance.user_ip)

            return {
                "responseDate": str(datetime.now()),
                "contentTopic": "Unban ip.",
                "responseData": {
                    "result": result,
                }
            }