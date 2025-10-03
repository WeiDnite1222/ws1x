

def generate_web_root_dir_not_found_site():
    """
    <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Server Service Unready - DynamicPages</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        </head>
        <body>
            <h1 class="title">Current website root does not exist.</h1>
            <div id="dp_info_bar">
                <svg aria-hidden="true" viewBox="0 0 24 24" id="dp_info_svg" class="dp_status_icon">
                    <path d="M12 2a10 10 0 1 0 .001 20.001A10 10 0 0 0 12 2zm0 4a1.25 1.25 0 1 1 0 2.5A1.25 1.25 0 0 1 12 6zm1.4 12h-2.8a.6.6 0 0 1-.6-.6v-1.2c0-.331.269-.6.6-.6h.6v-4.2h-.6a.6.6 0 0 1-.6-.6V9.6c0-.331.269-.6.6-.6h2.2c.331 0 .6.269.6.6v5.4h.6c.331 0 .6.269.6.6v1.2c0 .331-.269.6-.6.6z"
                          fill="currentColor"></path>
                </svg>
                <span role="separator"
                      class="separator"></span>
                <div class="dp_message" id="dp_message">
                    Want to return back to the home page?
                </div>
                <button type="button"
                        onclick="document.getElementById('dp_info_bar').style.display='none'; document.getElementById('body').classList.remove('disable_bar')"
                        class="dp_message_button">
                    Bring me back
                </button>
            </div>
        </body>
        <style>
            html, body {
                font-family: Arial, Helvetica, sans-serif;
                height: 100%;
                margin: 0;
                padding: 0;
            }

            body {
                background: linear-gradient(#e66465, #9198e5);
            }

            .title {
                font-family: Arial, Helvetica, sans-serif;
                padding-left: 20px;
                font-size: 40pt;
                color: #ffffff;
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

            @media (max-width: 767px) {
                #dp_info_bar {
                    height:6.2em;
                }
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
    </html>
    """