from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
from pydantic import BaseModel
from libraries.cloudflare.tool import check_turnstile_token, get_user_ip

class TabRouter:
    def __init__(self, yazule, prefix="/tab", tags=["tab"]):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.yazule = yazule


        class TabAccessItem(BaseModel):
            requireAccessTabName: str
            cloudflare_turnstile_token: str


        @self.router.post("/access")
        def get_specified_api_tab_access_token(request: Request, tab_access_item: TabAccessItem):
            user_ip = get_user_ip(request)
            result, tab_access_token, expired_date = self.yazule.create_tab_access_token(user_ip,
                                                                                    tab_access_item.requireAccessTabName,
                                                                                    tab_access_item.cloudflare_turnstile_token)


            if not result:
                return {
                    "responseDate": datetime.now(),
                    "contentTopic": "Get specified api tab access token.",
                    "ResponseData": {
                        "specifiedAccessTabName": f"{tab_access_item.requireAccessTabName}",
                        "result": {"getTokenStatus": False, "message": f"Could not get tab access token. "
                                                                       f"Maybe server is not allow to create new token at this time."
                                                                       f" Or your turnstile token is invalid."}
                    }
                }

            return {
                "responseDate": datetime.now(),
                "contentTopic": "Get specified api tab access token.",
                "ResponseData": {
                    "specifiedAccessTabName": f"{tab_access_item.requireAccessTabName}",
                    "result": {"getTokenStatus": True,
                               "tabAccessToken": tab_access_token,
                               "allowAccessTabName": tab_access_item.requireAccessTabName,
                               "expiresOn": expired_date}
                }
            }

        @self.router.post("/find")
        def get_tab_token_access_tab_name(tab_access_token):
            result, tab_name = self.yazule.get_tab_access_token_access_tab_name(tab_access_token)

            if not result:
                return {
                    "responseDate": datetime.now(),
                    "contentTopic": "Find the target tab access token that allows access to the tab name.",
                    "ResponseData": {
                        "result": {"accessCheckStatus": False,
                                   "message": "T-token not found. Maybe the token is invalid.", },
                    }
                }
            else:
                return {
                    "responseDate": datetime.now(),
                    "ResponseData": {
                        "result": {"accessCheckStatus": True,
                                   "allowAccessTabName": tab_name}
                    }
                }


