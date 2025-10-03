import ctypes
import os
import shlex
import subprocess
import requests
import traceback
import time

def is_elevated():
    if os.name == 'nt':
        try:
            ctypes.windll.shell32.IsUserAnAdmin()
            return True
        except Exception:
            return False
    elif os.name == 'posix':
        return os.geteuid() == 0

    return False


def fix_execute_permission_in_directory(api_data_dir):
    if os.name == 'nt':
        return

    for root, dirs, files in os.walk(api_data_dir):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                subprocess.run(shlex.split("chmod +x {}".format(filepath)))
            except Exception as error:
                print("Failed to fix permission for file {} ERROR: {}".format(filepath, error))


def what_is_my_ip():
    try:
        response = requests.get('https://api.ipify.org')
        public_ip = response.text
        return public_ip
    except requests.exceptions.RequestException as e:
        print("Unable to get public IP: {} Traceback: {}".format(e, traceback.format_exc()))
        return None


def calc_took_time(func):
    def wrap(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print("Took time: {}".format(time.time() - start))
        return result

    return wrap
