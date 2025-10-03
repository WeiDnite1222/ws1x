import requests
from fastapi import Request

def get_user_ip(request: Request):
    """
    Get user ip from request.
    """
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip

    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()

    return request.client.host

def check_turnstile_token(turnstile_token, cf_turnstile_secret_token, user_ip):
    try:
        response = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify",
                                 headers={"Content-Type": "application/json"},
                                 json={
                                     "secret": cf_turnstile_secret_token,
                                     "response": turnstile_token,
                                     "remoteip": user_ip,
                                 })

        if response.status_code == 200:
            return True
        else:
            print("Could not verify turnstile token. Did the cf_turnstile_secret_token is valid?")

        return False
    except Exception as error:
        raise Exception("Unexpected error while checking turnstile_token. {}".format(error))