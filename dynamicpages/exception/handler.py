from fastapi import HTTPException
from fastapi.responses import HTMLResponse
import asyncio
import os

error_map = {
    "400": {"title": "Bad Request", "desc": "The request is invalid. Check your request header or body is"
                                            " correct.",
            "homePortal": True},
    "401": {"title": "Unauthorized", "desc": "The specified resource/URL requires authorized identity.",
            "homePortal": True},
    "403": {"title": "Forbidden", "desc": "The current resource/URL is not accessible to you."
                                          "\n (Access Denied)",
            "homePortal": True},
    "404": {"title": "Not Found", "desc": "The specified resource/site dose not exist.",
            "homePortal": True},
    "405": {"title": "Method Not Allowed", "desc": "Current resource are not allowed to access by this method."
                                                   "\n(CURT_ERR_RES_TYPE>HTMLResponse)",
            "homePortal": True},
    "422": {"title": "Unprocessable Entity", "desc": "An invalid value(s) in the request entity was detected.",
            "homePortal": True},
    "500": {"title": "Internal Server Error", "desc": "An unexpected error has occurred on the server side.",
            "homePortal": True},
    "503": {"title": "Service Unavailable", "desc": "The service is currently unavailable.",
            "homePortal": False},
    "553": {"title": "Server Maintenance", "desc": "The server is currently unavailable."
                                                   "\nWe will be back soon until the maintenance is completed.",
            "homePortal": False},
    "554": {"title": "Update Mode", "desc": "The server is in update mode.",
            "homePortal": False},
    "666": {"title":"Server Service Unready", "desc": "Current website root does not exist.",
            "homePortal": True},
    "<DEFAULT>": {"title": "Unknown Error ?", "desc": "An undefined error has occurred."
                                                      "\nFor Admin/Owner : Please check the server logs to obtain more information.",
            "homePortal": True},
}

error_map_color = {
    "400": {"side": "to bottom", "top": "#886aff", "bottom": "#ffffff"},
    "401": {"side": "to bottom", "top": "#ff6060", "bottom": "#000000"},
    "403": {"side": "to bottom", "top": "#ff8b8b", "bottom": "#fff53f"},
    "404": {"side": "to bottom", "top": "#e66465", "bottom": "#9198e5"},
    "405": {"side": "to bottom", "top": "#00ea2e", "bottom": "#37ffd8"},
    "422": {"side": "to bottom", "top": "#000000", "bottom": "#ffffff"},
    "500": {"side": "to bottom", "top": "#2676ff", "bottom": "#ffffff"},
    "503": {"side": "to bottom", "top": "#a4ff3f", "bottom": "#ffffa7"},
    "553": {"side": "to bottom", "top": "#a4ff3f", "bottom": "#ffffa7"},
    "554": {"side": "to right", "top": "#ff9011", "bottom": "#ffe109"},
    "666": {"side": "to bottom", "top": "#ff5252", "bottom": "#ff5252"},
    "<DEFAULT>": {"side": "to bottom", "top":"#ff5252", "bottom": "#ff5252"},
}


def get_default_error_page(status_code, default_page_url):
    title = error_map.get(str(status_code), error_map.get("<DEFAULT>"))["title"]
    desc = error_map.get(str(status_code), error_map.get("<DEFAULT>"))["desc"]
    enable_return_back = error_map.get(str(status_code), error_map.get("<DEFAULT>"))["homePortal"]

    info_bar_message = "Want to return back to the home page?" if enable_return_back else "The return to homepage function is temporarily unavailable."
    btn_message = "Bring me back" if enable_return_back else "Ok"

    js_back_to_home = f"window.location.href='{default_page_url}'" if enable_return_back else """document.getElementById('dp_info_bar').style.display='none';
    """

    info_bar = f"""
    <div id="dp_info_bar">
        <svg aria-hidden="true" viewBox="0 0 24 24" id="dp_info_svg" class="dp_status_icon">
            <path d="M12 2a10 10 0 1 0 .001 20.001A10 10 0 0 0 12 2zm0 4a1.25 1.25 0 1 1 0 2.5A1.25 1.25 0 0 1 12 6zm1.4 12h-2.8a.6.6 0 0 1-.6-.6v-1.2c0-.331.269-.6.6-.6h.6v-4.2h-.6a.6.6 0 0 1-.6-.6V9.6c0-.331.269-.6.6-.6h2.2c.331 0 .6.269.6.6v5.4h.6c.331 0 .6.269.6.6v1.2c0 .331-.269.6-.6.6z"
                    fill="currentColor"></path>
        </svg>
        <span role="separator"
                  class="separator"></span>
        <div class="dp_message" id="dp_message">
            {info_bar_message}
        </div>
        <button type="button"
                onclick="{js_back_to_home}"
                class="dp_message_button"
                id="dp_message_button">
            {btn_message}
        </button>
    </div>
    """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{title} - DynamicPages</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    </head>
    <body>
        <h1 class="title">{title}</h1>
        <p class="message">{desc}</p>
        {info_bar}
    </body>
    </html>
    """

    html += """
        <style>
        html, body {
            font-family: Arial, Helvetica, sans-serif;
            height: 100%;
            margin: 0;
            padding: 0;
        }

        body {
    """

    side, top, bottom = (error_map_color.get(str(status_code), error_map_color.get("<DEFAULT>"))["side"],
                         error_map_color.get(str(status_code), error_map_color.get("<DEFAULT>"))["top"],
                         error_map_color.get(str(status_code), error_map_color.get("<DEFAULT>"))["bottom"])

    html += f"""
            background: linear-gradient({side}, {top}, {bottom});
    """

    html += """
        }

        .title {
            font-family: Arial, Helvetica, sans-serif;
            padding-left: 20px;
            font-size: 40pt;
            color: #ffffff;
        }

        .message {
            font-family: Arial, Helvetica, sans-serif;
            padding-left: 20px;
            font-size: 20pt;
            color: #ffffff;
            white-space: revert;
            text-overflow:ellipsis;
        }

        #dp_info_bar {
            position:fixed;
            bottom: 0;
            left:0;
            right:0;
            height:4.2em;
            ;z-index:3;
            /*background:#111827;*/
            background: #f8f8f8;
            color:#ffffff;
            display:inline-flex;
            align-items:center;
            padding:0 12px;
            gap:12px;
            font:14px/1 system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
            border-radius:10px;
        }

        .dp_status_icon {
            width:40px;
            height:40px;
            flex:0 0 25px;
            display:block;
            color: #000000;
        }

        .separator {
            width:1px;
            height:16px;
            background:rgba(255,255,255,0.35);
            display:inline-block;
        }

        .dp_message {
            flex:1;
            min-width:0;
            white-space: revert;
            text-overflow:ellipsis;
            color: #000000;
        }

        .dp_message_button {
            height:35px;
            padding:0 12px;
            border:0;
            border-radius:6px;
            background: #3d79ff;
            color:#fff;
            cursor:pointer;
            font:600 13px/28px system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
            box-shadow: 5px 4px #888888;
        }
    </style>
    <style>
            @media (max-width: 767px) {
            #dp_info_bar {
                height:6.2em;
                }
            }
    </style>
    """
    return html


class ExceptionHandler:
    def __init__(self, app, resources, error_page_cfg, web_root_dir):
        self.app = app
        self.config = error_page_cfg
        self.web_root_dir = web_root_dir
        self.resources = resources

        @self.app.exception_handler(HTTPException)
        async def main_handler(request, exception):
            error_directory = self.config.get(str(exception.status_code))
            error_page_path = os.path.join(self.web_root_dir, error_directory if error_directory is not None else "not_found")

            if error_directory is None or not os.path.exists(error_page_path):
                content = get_default_error_page(exception.status_code, request.base_url)
                return HTMLResponse(status_code=exception.status_code, content=content)

            return HTMLResponse(status_code=exception.status_code, content=self.resources.resources[self.config[exception.status_code]])