import threading
import time
import asyncio, os, sys
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware

dp_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(dp_root_dir)

from config import D2OUpdater, DPSConfig
from exception.handler import get_default_error_page
from api.tool import get_user_ip

class DynamicPagesServiceDaemon(threading.Thread):
    def __init__(self, logger, fastapi, daemon=True):
        threading.Thread.__init__(self)
        self.daemon = daemon
        self.logger = logger
        self.service_daemon_config = DPSConfig(self.logger)
        self.cfg_updater = D2OUpdater([self.service_daemon_config], refresh_time=5)
        self.cfg_updater.start()

        self.app = fastapi

        @self.app.middleware("http")
        async def service_middleware(request: Request, call_next):
            if self.service_daemon_config.service_daemon_main.get("blockAllRequests", False) is True:
                return HTMLResponse(status_code=503,
                                    content=get_default_error_page("517", request.base_url))

            if self.service_daemon_config.service_daemon_main.get("enableMaintenanceModeA", False) is True:
                return HTMLResponse(status_code=553,
                                    content=get_default_error_page("553", request.base_url))

            if self.service_daemon_config.service_daemon_main.get("enableMaintenanceModeB", False) is True:
                ip = get_user_ip(request)

                if ip in self.service_daemon_config.service_daemon_main.get("allowIPList", []):
                    return await call_next(request)
                else:
                    return HTMLResponse(status_code=553,
                                        content=get_default_error_page("553", request.base_url))

            custom_error_code = self.service_daemon_config.service_daemon_main.get("responseCustomHTTPStatusCode", None)

            if (self.service_daemon_config.service_daemon_main.get("enableHTTPStatusMode", False) is True and
                custom_error_code is not None):
                return HTMLResponse(status_code=custom_error_code,
                                    content=get_default_error_page(custom_error_code, request.base_url))

            return await call_next(request)

        @self.app.middleware("http")
        async def add_global_header(request: Request, call_next):
            response = await call_next(request)
            if self.service_daemon_config.service_daemon_main.get("disableCDNCache", False) is True:
                response.headers["Cache-Control"] = "no-cache"
            return response

        self.start()


    def run(self):
        while True:
            """
            Do something here.
            """
            time.sleep(1)

