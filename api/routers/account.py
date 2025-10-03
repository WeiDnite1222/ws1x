from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request, HTTPException, Depends, status, Header
from libraries.cloudflare.tool import get_user_ip
from pydantic import BaseModel
from datetime import datetime
from typing import Annotated, Optional

class AccountRouter:
    def __init__(self, yazule, communicate_config, prefix="/account", tags=["account"]):
        self.router = APIRouter(prefix=prefix, tags=tags)

        self.yazule = yazule
        self.communicate_config = communicate_config

        class AccountRegisterValidationData(BaseModel):
            tabAccessToken: str
            newAccountName: str

        @self.router.post("/register/validation")
        def validation_before_register(request: Request, account_register_part1_data: AccountRegisterValidationData):
            current_tab_name = "/account/register/validation"

            user_ip = get_user_ip(request)
            result = self.yazule.is_valid_tab_access_token(user_ip,
                                                      account_register_part1_data.tabAccessToken,
                                                      current_tab_name)

            if not result:
                return JSONResponse(
                    status_code=401,
                    content={
                        "responseDate": str(datetime.now()),

                        "contentTopic": "Register",
                        "ResponseData": {
                            "result": {"registerStatus": False,
                                       "message": "The t-token is invalid.", }
                        }
                    }
                )

            register_instance = self.yazule.get_register_token(user_ip, account_register_part1_data.newAccountName)

            errorMappings = {
                "accountNameCheckFailed": register_instance.account_name_check_failed,
                "accountNameTooShort": register_instance.account_name_too_short,
                "accountNameTooLong": register_instance.account_name_too_long,
                "notAllowed": register_instance.not_allow_to_create_account,
            }

            return {
                "responseDate": datetime.now(),
                "contentTopic": "Register new account.",
                "ResponseData": {
                    "result": {"registerStatus": register_instance.status,
                               "registerTempToken": register_instance.token,
                               "errorMappings": errorMappings}
                }
            }

        class AccountRegisterTokenPass(BaseModel):
            user_ip: str
            register_token: str

        bearer_scheme = HTTPBearer(auto_error=False)

        @self.router.post("/check/register_token")
        def check_register_token(art: AccountRegisterTokenPass,
                creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
        ):

            if not creds or creds.scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Missing bearer token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            password = creds.credentials

            if password != communicate_config.get('dynamic_pages_secret_password'):
                return JSONResponse(
                    status_code=403,
                    content={
                        "responseDate": str(datetime.now()),
                        "contentTopic": "Check register token valid.",
                        "ResponseData": {
                            "result": {"allowAccess": False, "message": f"Invalid header."}
                        }
                    }
                )

            result = self.yazule.valid_register_token(art.user_ip, art.register_token)

            if not result:
                return {
                    "contentTopic": "Check register token valid.",
                    "ResponseData": {
                        "result": {"registerTokenValid": False}
                    }
                }

            return {
                "responseDate": datetime.now(),
                "contentTopic": "Check register token valid.",
                "ResponseData": {
                    "result": {"registerTokenValid": True}
                }
            }

        class AccountRegisterData(BaseModel):
            registerToken: str
            newAccountAddress: str
            newAccountBirthDate: str
            newAccountEmail: str
            newAccountPassword: str

        @self.router.post("/register")
        def register_account_part_2(request: Request, data: AccountRegisterData):
            user_ip = get_user_ip(request)

            r_token = data.registerToken
            address = data.newAccountAddress
            birthDate = data.newAccountBirthDate
            email = data.newAccountEmail
            password = data.newAccountPassword

            result = self.yazule.valid_register_token(user_ip, r_token)

            if not result:
                return JSONResponse(
                    status_code=401,
                    content={
                        "responseDate": str(datetime.now()),
                        "contentTopic": "Register new account.",
                        "ResponseData": {
                            "result": {"registerStatus": False,
                                       "message": f"Invalid register token."}
                        }
                    }
                )

            account_name = self.yazule.get_account_name_by_register_token(r_token)

            register_instance = self.yazule.create_account_full_process(data.registerToken,
                                                                   address, account_name, birthDate, email, password)

            errorMappings = {"accountAddressCheckError": register_instance.account_address_check_failed,
                             "accountAddressTooLong": register_instance.account_address_too_long,
                             "accountAddressTooShort": register_instance.account_address_too_short,
                             "missingAtSign": register_instance.account_address_missing_at_sign,
                             "passwordCheckFailed": register_instance.password_check_failed,
                             "passwordTooShort": register_instance.password_too_short,
                             "passwordTooLong": register_instance.password_too_long,
                             "wrongBirthFormat": register_instance.wrong_birthday_format,
                             "duplicateEmail": register_instance.duplicate_email,
                             "duplicateAddress": register_instance.duplicate_address,
                             "accountEmailCheckFailed": register_instance.account_email_check_failed,
                             "wrongAddressFormat": register_instance.wrong_account_address_format}

            if register_instance.status is False:
                return {
                    "responseDate": str(datetime.now()),
                    "contentTopic": "Register new account.",
                    "ResponseData": {
                        "result": {"registerStatus": False,
                                   "message": f"Account address check failed.",
                                   "errorMappings": errorMappings
                                   }
                    }
                }
            return {
                "responseDate": str(datetime.now()),
                "contentTopic": "Register new account.",
                "ResponseData": {
                    "result": {"registerStatus": True,
                               "message": f"Account name {account_name} created successfully."
                               }
                }
            }

        class AccountLoginP1Data(BaseModel):
            tabAccessToken: str
            accountAddress: str

        @self.router.post("/login/validation")
        def login_account_part_1(request: Request, account_login_p1_data: AccountLoginP1Data):
            current_tab_name = "/account/login/validation"

            user_ip = get_user_ip(request)

            result = self.yazule.is_valid_tab_access_token(user_ip,
                                                      account_login_p1_data.tabAccessToken,
                                                      current_tab_name)

            if not result:
                return JSONResponse(
                    status_code=401,
                    content={
                        "responseDate": str(datetime.now()),
                        "contentTopic": "Login",
                        "ResponseData": {
                            "result": {"loginStatus": False,
                                       "message": "The t-token is invalid.", }
                        }
                    }
                )

            instance = self.yazule.get_login_token(account_login_p1_data.accountAddress, user_ip)

            error_map = {
                "accountDoesNotExist": instance.account_does_not_exist,
                "accountLocked": instance.account_locked,
            }

            return JSONResponse(
                content={
                    "responseDate": str(datetime.now()),
                    "contentTopic": "Login account.",
                    "ResponseData": {
                        "result": {"loginStatus": instance.status,
                                   "errorMappings": error_map,
                                   "loginToken": instance.token,
                                   }
                    }
                }
            )

        class AccountLoginTokenPass(BaseModel):
            user_ip: str
            login_token: str

        @self.router.post("/check/login_token")
        def check_login_token(art: AccountLoginTokenPass,
                                  creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
                                  ):

            if not creds or creds.scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Missing bearer token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            password = creds.credentials

            if password != communicate_config.get('dynamic_pages_secret_password'):
                return JSONResponse(
                    status_code=403,
                    content={
                        "responseDate": str(datetime.now()),
                        "contentTopic": "Check login token valid.",
                        "ResponseData": {
                            "result": {"allowAccess": False, "message": f"Invalid header."}
                        }
                    }
                )

            result, valid_token, account_address = self.yazule.check_login_token_with_address_result(art.login_token, art.user_ip)


            if result is True and valid_token is True:
                return {
                    "responseDate": datetime.now(),
                    "contentTopic": "Check login token valid.",
                    "ResponseData": {
                        "result": {"loginTokenValid": True,
                                   "accountAddress": account_address}
                    }
                }

            return {
                "contentTopic": "Check login token valid.",
                "ResponseData": {
                    "result": {"loginTokenValid": False,
                               "accountAddress": "<NULL>"}
                }
            }

        class AccountLoginP2Data(BaseModel):
            accountPassword: str
            loginToken: str

        @self.router.post("/login")
        def login_account_part_2(account_log_data: AccountLoginP2Data,
                                 request: Request,
                                 sec_ch_ua_platform: Annotated[Optional[str], Header(alias="Sec-CH-UA-Platform")] = "<UNKNOWN>"
                                 ):
            current_tab_name = "/account/login_account"

            ip = get_user_ip(request)

            instance = self.yazule.login(account_log_data.loginToken, account_log_data.accountPassword, ip, sec_ch_ua_platform)

            error_map = {
                "wrongPassword": instance.wrong_password,
                "accountLocked": instance.account_locked,
            }

            if instance.invalid_token:
                return JSONResponse(
                    status_code=401,
                    content={
                        "responseDate": str(datetime.now()),
                        "contentTopic": "Login account.",
                        "ResponseData": {
                            "result": {"loginStatus": False,
                                       "message": f"The loginToken is invalid."}
                        }
                    }
                )

            return JSONResponse(
                content={
                    "responseDate": str(datetime.now()),
                    "contentTopic": "Login account.",
                    "ResponseData": {
                        "result": {"loginStatus":instance.status,
                                   "errorMappings": error_map,
                                   "refreshToken": instance.token,
                                   "expiresOn": str(instance.expired_date),
                                   }
                    }
                }
            )

        class AccessTokenBody(BaseModel):
            account_address: str

        @self.router.post("/access_token")
        async def get_access_token(request: Request,
                                   body: AccessTokenBody,
                                   sec_ch_ua_platform: Annotated[Optional[str], Header(alias="Sec-CH-UA-Platform")] = "<UNKNOWN>",
                                   creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):

            if not creds or creds.scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Missing bearer token (loginToken)",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            refresh_token = creds.credentials

            ip = get_user_ip(request)

            instance = self.yazule.get_access_token_by_refresh_token(body.account_address,
                refresh_token, ip, sec_ch_ua_platform)

            if instance.invalid_token:
                return JSONResponse(
                    status_code=403,
                    content={
                        "responseDate": str(datetime.now()),
                        "contentTopic": "Get access token.",
                        "ResponseData": {
                            "result": {"getTokenStatus": False,
                                       "message": f"The refreshToken is invalid.",
                                       "accessToken": instance.token,
                                       }
                        }

                    }
                )

            return JSONResponse(
                content={
                    "responseDate": str(datetime.now()),
                    "contentTopic": "Get access token.",
                    "ResponseData": {
                        "result": {"getTokenStatus": instance.status,
                                   "accessToken": instance.token,
                                   }
                    }
                }
            )