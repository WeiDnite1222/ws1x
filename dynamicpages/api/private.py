import requests


def check_register_token(register_token: str, user_ip, api_key):
    r = requests.post("https://api.weispace.net/account/check/register_token",
                      headers={
                          'Content-Type': 'application/json',
                          'Authorization': 'Bearer ' + api_key
                      },
                      json={"register_token": register_token,
                            "user_ip": user_ip})

    data = r.json()

    status_code = data["ResponseData"]["result"]["registerTokenValid"]

    return status_code

def check_login_token(login_token: str, user_ip, api_key):
    r = requests.post("https://api.weispace.net/account/check/login_token",
                      headers={
                          'Content-Type': 'application/json',
                          'Authorization': 'Bearer ' + api_key
                      },
                      json={"login_token": login_token,
                            "user_ip": user_ip})

    data = r.json()

    status_code = data["ResponseData"]["result"]["loginTokenValid"]
    account_address = data.get("ResponseData", {}).get("result", {}).get("accountAddress")

    return status_code, account_address

def check_banned(ip: str, api_key):
    try:
        r = requests.post("https://api.weispace.net/private/check_ip_ban",
                          headers={
                              'Content-Type': 'application/json',
                              'Authorization': 'Bearer ' + api_key
                          },
                          json={"ip": ip})

        data = r.json()
        return data["ResponseData"]["result"]["isBanned"]
    except requests.exceptions.RequestException as e:
        print("Unable to check ip {} ban status.\n"
              "ERRPR: {}", ip, e)
        return False


def unban_ip(ip: str, turnstile_token, api_key):
    try:
        r = requests.post("https://api.weispace.net/private/unban",
                          headers={
                              'Content-Type': 'application/json',
                              'Authorization': 'Bearer ' + api_key
                          },
                          json={"turnstile_token": turnstile_token,
                                "user_ip": ip})

        data = r.json()

        return data["responseData"]["result"]

    except requests.exceptions.RequestException as e:
        print("Unable to unban ip {}\n"
              "ERRPR: {}", ip, e)
        return False