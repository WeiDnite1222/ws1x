import logging
import os
import pathlib
import argparse
import subprocess
import sys
import textwrap
from space_net_lib.definition import path
from space_net_lib.utils import tool
from space_net_lib.logger.logger import DefaultLogger
import random
import string

root_dir = os.path.dirname(os.path.realpath(__file__))

print("""
\033[94m
 ____                       _   _ _____ _____                   
/ ___| _ __   __ _  ___ ___| \\ | | ____|_   _|                  
\\___ \\| '_ \\ / _` |/ __/ _ \\  \\| |  _|   | |                    
 ___) | |_) | (_| | (_|  __/ |\\  | |___  | |                    
|____/| .__/ \\__,_|\\___\\___|_| \\_|_____|_|_|
                                                            _   
|_ _|_|_|  ___| |_ __ _| | | ___ _ __ / ___|_   _  ___  ___| |_ 
 | || '_ \\/ __| __/ _` | | |/ _ \\ '__| |  _| | | |/ _ \\/ __| __|
 | || | | \\__ \\ || (_| | | |  __/ |  | |_| | |_| |  __/\\__ \\ |_ 
|___|_| |_|___/\\__\\__,_|_|_|\\___|_|   \\____|\\__,_|\\___||___/\\__|
\033[0m
""")

applications = {
    "dynamicpages": {
        "serviceName": "spacenet.dynamicpages.service",
        "path": pathlib.Path(root_dir, "dynamicpages"),
        "executeCommand": "uvicorn main:app",
        "useCustomPort": False,
        "defaultPort": 8443,
        "setPortArg": "--port ",
        "description": "SpaceNET DynamicPages Web Server",
        "currentUser": "spacenet-dynamicpages-user"
    },
    "dynamicpages-dev": {
        "serviceName": "spacenet.dynamicpages-dev.service",
        "path": pathlib.Path(root_dir, "dynamicpages"),
        "executeCommand": "uvicorn main:app --reload",
        "defaultPort": 8883,
        "useCustomPort": False,
        "setPortArg": "--port ",
        "description": "SpaceNET DynamicPages Web Server [DEV]",
        "currentUser": "spacenet-dynamicpages-user"
    },
    "api": {
        "serviceName": "spacenet.api.service",
        "path": pathlib.Path(root_dir, "api"),
        "executeCommand": "uvicorn main:app --reload",
        "defaultPort": 8000,
        "useCustomPort": False,
        "setPortArg": "--port ",
        "description": "SpaceNET API Service",
        "currentUser": "spacenet-api-user"
    },
    "api-dev": {
        "serviceName": "spacenet.api-dev.service",
        "path": pathlib.Path(root_dir, "api"),
        "executeCommand": "uvicorn main:app --reload",
        "defaultPort": 8001,
        "useCustomPort": False,
        "setPortArg": "--port ",
        "description": "SpaceNET API Service",
        "currentUser": "spacenet-api-user"
    },
    "manage-server": {
        "serviceName": "spacenet.manage.server.service",
        "path": pathlib.Path(root_dir, "manage"),
        "executeCommand": "python3 main.py --side server",
        "defaultPort": None,
        "useCustomPort": False,
        "setPortArg": None,
        "description": "SpaceNET Server Manager [Server]",
        "currentUser": "spacenet-manage-user"
    },
    "manage-client": {
        "serviceName": "spacenet.manage.client.service",
        "path": pathlib.Path(root_dir, "manage"),
        "executeCommand": "python3 main.py --side client",
        "defaultPort": None,
        "useCustomPort": False,
        "setPortArg": None,
        "description": "SpaceNET Server Manager [Client]",
        "currentUser": "spacenet-manage-user"
    }
}


user_current_dict = {
            "spacenet-api-user": [
                path.api_data_path, path.api_config_path
            ],
            "spacenet-manage-user": [
                path.manage_data_path, path.manage_config_path
            ],
            "spacenet-dynamicpages-user": [
                path.dynamic_pages_data_path, path.dynamic_pages_config_path
            ]
        }

def check_venv_exists(venv_path):
    bin_dir = os.path.join(venv_path, "bin")

    if not os.path.exists(bin_dir):
        return False
    else:
        return True

def create_venv(venv_path):
    try:
        subprocess.run(["python3", "-m", "venv", venv_path], check=True)
    except Exception as error:
        raise Exception("Unable to create virtual environment. {}".format(error))

def install_requirements(requirements_file_path):
    try:
        subprocess.run(["pip", "install", "-r", requirements_file_path, "--break-system-packages"],
                       check=True)
    except Exception as error:
        raise Exception("Unable to install requirements name {} ERROR:{}".format(requirements_file_path, error))

def mkdir_in_sudo(venv_path):
    os.system("sudo mkdir -p {}".format(venv_path))

def mkdir_windows(venv_path):
    os.system("mkdir -p {}".format(venv_path))

def check_user_exists(user_name):
    try:
        subprocess.run(["sudo", "id", user_name], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def create_user(username):
    try:
        subprocess.run(["sudo", "useradd", username], check=True)
    except Exception as error:
        raise Exception("Unable to create user {} ERROR:{}".format(username, error))

def change_file_ownership(username, group_name, file_path):
    try:
        subprocess.run(["sudo", "chown", "{}:{}".format(username, group_name), file_path], check=True)
    except Exception as error:
        raise Exception("Unable to change ownership of file {} ERROR:{}".format(file_path, error))

def fix_file_permissions(file_path):
    try:
        subprocess.run(["sudo", "chmod", "-R", "u+rwx", file_path], check=True)
    except Exception as error:
        raise Exception("Unable to change permissions of file {} ERROR:{}".format(file_path, error))

def make_child_file_inherit_parent_permissions(file_path):
    try:
        subprocess.run(["sudo", "chmod", "g+s", file_path], check=True)
    except Exception as error:
        raise Exception("Unable to change permissions of file {} ERROR:{}".format(file_path, error))

def create_group(group_name):
    try:
        subprocess.run(["sudo", "groupadd", group_name], check=True)
    except Exception as error:
        raise Exception("Unable to create new group name {} ERROR:{}".format(group_name, error))

def check_group_exists(group_name):
    try:
        subprocess.run(["getent", "group", group_name], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def add_user_to_group(group_name, user_name):
    try:
        subprocess.run(["sudo", "usermod", "-aG", group_name, user_name], check=True)
    except Exception as error:
        raise Exception("Unable to add user {} to group {} ERROR:{}".format(user_name, group_name, error))

def allow_user_access_and_execute_in_folder_acl(username, group_name, dir, ignore_error=False, recursion=False):
    try:
        if recursion:
            subprocess.run(["sudo", "setfacl", "-R", "-m", f"u:{username}:rx", dir], check=True)
            subprocess.run(["sudo", "setfacl", "-R", "-d", "-m", f"u:{username}:rx", dir], check=True)
        else:
            subprocess.run(["sudo", "setfacl", "-m", f"u:{username}:rx", dir], check=True)
            subprocess.run(["sudo", "setfacl", "-d", "-m", f"u:{username}:rx", dir], check=True)
    except Exception as error:
        if not ignore_error:
            raise Exception("Unable to fix permissions of folder {} ERROR:{}".format(dir, error))

def chmod_execute(file):
    try:
        subprocess.run(["sudo", "chmod", "o+x", file], check=True)
    except Exception as error:
        raise Exception("Unable to fix permissions of file {} ERROR:{}".format(file, error))

def get_sudo():
    try:
        return subprocess.run(["sudo", "echo", "Hello from sudo"], check=True)
    except Exception as error:
        raise Exception("Unable to get sudo. ERROR:{}".format(error))

def is_sudo_exist():
    try:
        subprocess.run(["sudo", "-n", "true"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


class Setup:
    def __init__(self):
        self.logger = DefaultLogger("SetupLogger",
                                    "./installer.log",
                                    dump_output_to_file=True,
                                    stdout_output_format="%(log_color)s%(levelname)s%(reset)s > %(message)s")
        self.logger.setLevel(logging.INFO)

        self.install_application_list = []
        self.bypass_create_group = True
        self.bypass_create_user = True

        self.arguments_parser()

    def main(self):
        # if not tool.is_elevated():
        #     self.logger.error("This script must be run as root(administrator mode in Windows)")
        #     sys.exit(1)

        self.logger.info(f"These applications will be install: \n{", ".join(map(str, self.install_application_list))}")

        result = str(input("To confirm the install, type 'yes' to continue: "))

        if result.lower() != "yes":
            self.logger.info("Canceled...")
            return

        if not check_venv_exists("main-venv"):
            self.logger.info("Creating virtual environment")
            create_venv("main-venv")
        else:
            self.logger.info("Virtual environment already exists")

        current_venv_path = os.path.join(root_dir, "main-venv")

        # print("Entering virtual environment....")
        # try:
        #     subprocess.run(["source", os.path.join(current_venv_path, "bin", "activate")])
        # except Exception as error:
        #     print("Failed to enter virtual environment with method A. Try method B instead...")
        #     try:
        #         subprocess.run([".", f".{os.path.join(current_venv_path, "bin", "activate")}"], check=True)
        #     except Exception as error:
        #         raise Exception("Unable to enter virtual environment ERROR:{}".format(error))

        print("Installing required packages...")

        for app_name, app_info in applications.items():
            app_path = app_info["path"]
            print("Processing {}".format(app_name))

            if os.path.exists(os.path.join(app_path, "requirements.txt")):
                print(os.path.join(app_path, "requirements.txt"))
                install_requirements(os.path.join(app_path, "requirements.txt"))

        print("Creating dependencies folder....")

        for _, dir in path.keyword_dict.items():
            if not os.path.exists(dir):
                print("Creating folder {}".format(dir))
                mkdir_in_sudo(dir)

        # user_dict = {
        #     "spacenet-api-user": [
        #         path.api_data_path, path.api_config_path
        #     ],
        #     "spacenet-manage-user": [
        #         path.manage_data_path, path.manage_config_path
        #     ],
        #     "spacenet-dynamicpages-user": [
        #         path.dynamic_pages_data_path, path.dynamic_pages_config_path
        #     ]
        # }

        if not self.bypass_create_group:
            print("Creating group...")
            for app_name, app_info in applications.items():
                group_name = app_info["currentUser"]

                if check_group_exists(group_name):
                    continue

                print("Creating group {}".format(group_name))
                create_group(group_name)

        # for username, dir in user_dict.items():
        #     group_name = username.replace("-user", "-group")
        #     if check_group_exists(group_name):
        #         continue
        #
        #     print("Creating group {}".format(group_name))
        #     create_group(group_name)

        if not is_sudo_exist():
            print("\033[31mAUTHENTICATING REQUIRED\033[0m")
            print("Install guest requires root(sudo) permissions to run perform subsequent processes.")
            get_sudo()
        else:
            print("Sudo session exists.")

        if not self.bypass_create_user:
            print("Creating account for service usage...")

            for app_name, app_info in applications.items():
                username = app_info["currentUser"]

                exists = check_user_exists(username)

                if exists:
                    continue

                print("Creating user {}".format(username))
                create_user(username)

        # for username, _ in user_dict.items():
        #     exists = check_user_exists(username)
        #
        #     if exists:
        #         continue
        #
        #     print("Creating user {}".format(username))
        #     create_user(username)

        print("Adding user to group...")

        for app_name, app_info in applications.items():
            username = app_info["currentUser"]
            group_name = username.replace("-user", "-group")

            print("Adding user {}".format(username))
            add_user_to_group(group_name, username)

        # for username, dir in user_dict.items():
        #     group_name = username.replace("-user", "-group")
        #
        #     print("Adding user {}".format(username))
        #     add_user_to_group(group_name, username)

        print("Fixing file permissions...")

        for app_name, app_info in applications.items():
            username = app_info["currentUser"]
            group_name = username.replace("-user", "-group")
            dirs = user_current_dict.get(username, [])

            for dir in dirs:
                print("Current {} | User {}".format(dir, username))

                change_file_ownership(username, group_name, dir)
                fix_file_permissions(dir)
                make_child_file_inherit_parent_permissions(dir)

        # for username, dirs in user_dict.items():
        #     group_name = username.replace("-user", "-group")
        #     for dir in dirs:
        #         print("Current {} | User {}".format(dir, username))
        #
        #         change_file_ownership(username, group_name, dir)
        #         fix_file_permissions(dir)
        #         make_child_file_inherit_parent_permissions(dir)

        print("Fixing execute permissions...")

        for app_name, app_info in applications.items():
            floor = str(root_dir).count("/")
            username = app_info["currentUser"]
            group_name = username.replace("-user", "-group")
            current = root_dir

            while floor > -1:
                self.logger.info("Current {} | User {}".format(current, username))
                allow_user_access_and_execute_in_folder_acl(username, group_name, current, ignore_error=True)

                current = os.path.dirname(current)
                floor = floor - 1
            allow_user_access_and_execute_in_folder_acl(username, group_name, root_dir, ignore_error=True,
                                                        recursion=True)

        # for username in user_dict.keys():
        #     floor = str(root_dir).count("/")
        #     group_name = username.replace("-user", "-group")
        #     current = root_dir
        #     while floor > -1:
        #         self.logger.info("Current {} | User {}".format(current, username))
        #         allow_user_access_and_execute_in_folder_acl(username, group_name, current, ignore_error=True)
        #
        #         current = os.path.dirname(current)
        #         floor = floor - 1
        #     allow_user_access_and_execute_in_folder_acl(username, group_name, root_dir, ignore_error=True, recursion=True)

        print("Current {}".format(root_dir))
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                chmod_execute(os.path.join(root, file))

        print("Creating bootstrap.sh...")

        try:
            subprocess.run(["sudo", "mkdir", "-p", os.path.join("/opt", "SpaceNET")], check=True)
        except Exception as error:
            raise Exception("Unable to create folder for bootstrap script. ERROR:{}".format(error))

        for app_name, app_info in applications.items():
            if not app_name in self.install_application_list:
                continue

            app_exec_command = app_info["executeCommand"]

            if app_info['useCustomPort'] is True:
                app_exec_command += " " + app_info['setPortArg']
            elif app_info.get("defaultPort") is not None:
                app_exec_command += " " + app_info['setPortArg'] + app_info['defaultPort']

            bootstrap = textwrap.dedent(f"""#!/bin/bash
                                        # shellcheck disable=SC2164
                                        source "{current_venv_path}/bin/activate"
                                        cd "{os.path.join(app_info['path'])}"
                                        {app_exec_command}
                                        """, )

            temp_path = os.path.join(root_dir, "temp", random.choice(string.ascii_letters))
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)

            with open(temp_path, "w") as file:
                file.write(bootstrap)

            bootstrap_file_path = os.path.join("/opt", "SpaceNET", app_name, "bootstrap.sh")

            try:
                subprocess.run(["sudo", "mkdir", "-p", os.path.dirname(bootstrap_file_path)], check=True)
            except Exception as error:
                raise Exception("Unable to create folder for bootstrap script. ERROR:{}".format(error))

            try:
                subprocess.run(["sudo", "mv", temp_path, bootstrap_file_path], check=True)
            except Exception as error:
                raise Exception(
                    "Unable to move service file path {} into service folder. ERROR:{}".format(temp_path, error))


        print("Creating service...")

        exists_service_names = []

        for app_name, app_info in applications.items():
            if not app_name in self.install_application_list:
                continue

            app_service_name = app_info["serviceName"]
            app_description = app_info["description"]
            app_exec_command = app_info["executeCommand"]
            print("Processing {}".format(app_service_name))

            if app_info['useCustomPort'] is True:
                app_exec_command += " " + app_info['setPortArg']

            bootstrap_file_path = os.path.join("/opt", "SpaceNET", app_name, "bootstrap.sh")

            service_data = textwrap.dedent(f"""[Unit]
            Description={app_description}
            After=network.target
            
            [Service]
            ExecStart=sudo -u {app_info["currentUser"]} bash {bootstrap_file_path}
            
            [Install]
            WantedBy=multi-user.target
            """)

            temp_path = os.path.join(root_dir,"temp", random.choice(string.ascii_letters))
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)

            service_file_path = os.path.join("/", "etc", "systemd", "system", app_service_name)

            with open(temp_path, "w") as service_file:
                service_file.write(service_data)

            try:
                subprocess.run(["sudo", "mv", temp_path, service_file_path], check=True)
            except Exception as error:
                raise Exception("Unable to move service file path {} into service folder. ERROR:{}".format(temp_path, error))

            exists_service_names.append(app_service_name)


        result = str(input("Would you like to start the service when startup? (y/n)"))

        if result.lower() == "y":
            for service_name in exists_service_names:
                print("Enabling auto boot for service name {}".format(service_name))
                try:
                    subprocess.run(["sudo", "systemctl", "enable", service_name], check=True)
                except Exception as error:
                    raise Exception("Unable to process service name {} ERROR:{}".format(service_name, error))

        result = str(input("Would you like to start the service right now? (y/n)"))

        if result.lower() == "y":
            for service_name in exists_service_names:
                print("Starting service name {}".format(service_name))
                try:
                    subprocess.run(["sudo", "systemctl", "start", service_name], check=True)
                except Exception as error:
                    raise Exception("Unable to start service name {} ERROR:{}".format(service_name, error))


        print("Restarting service...")
        try:
            subprocess.run(['sudo', "systemctl", "daemon-reload"], check=True)
        except Exception as error:
            raise Exception("Unable to restart service. ERROR:{}".format(error))

        print("\033[32mInstallation completed. \033[0m")


    def arguments_parser(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('--install-app-names', nargs='*', help='Install app names')
        parser.add_argument('--list-apps', help='List available apps', action='store_true')
        parser.add_argument('--bypass-create-group', help='Bypass create group process', action='store_true')
        parser.add_argument('--bypass-create-user', help='Bypass create user process', action='store_true')

        args = parser.parse_args()

        if args.list_apps:
            print("Available apps: ")
            for app_name, app_info in applications.items():
                print("_"*10)
                self.logger.info("App name: {}".format(app_name))
                self.logger.info("Description: {}".format(app_info["description"]))
                service_name = app_info["serviceName"]
                if not service_name is None:
                    self.logger.info("Service name: {}".format(service_name))
                print("‾" * 10)
            sys.exit(0)

        if args.install_app_names is None:
            self.logger.error("The install-app-names list is empty. Try run this script with \"--install-app-names <App Name> <Second App Name>\"")
            self.logger.info("If you don't know which application you want to install, use \"--list-apps\" to list available apps.")
            sys.exit(1)

        if args.bypass_create_group:
            self.bypass_create_group = True
            self.logger.info("Bypass create group process flag is enabled.")

        if args.bypass_create_user:
            self.bypass_create_user = True
            self.logger.info("Bypass create user process flag is enabled.")

        for app_name in args.install_app_names:
            if app_name not in applications.keys():
                startswith_match = []
                for name in applications.keys():

                    if name.startswith(app_name):
                        startswith_match.append(name)

                if len(startswith_match) > 0:
                    self.logger.warning(f"Invalid app name '{app_name}'. Did you mean {", ".join(map(str, startswith_match))}")
                else:
                    self.logger.warning(f"Invalid app name '{app_name}'.")

                continue

            if ":" in app_name and app_name.count(":") == 1:
                app_name, custom_port = app_name.split(":")

                applications[app_name]["useCustomPort"] = True

                if applications[app_name]["setPortArg"] is not None:
                    applications[app_name]["setPortArg"] = applications[app_name]["setPortArg"] + custom_port
                else:
                    self.logger.warning("App name '{}' not support custom port.".format(app_name))

            self.install_application_list.append(app_name)

        if len(self.install_application_list) == 0:
            self.logger.error("Install process aborted because no app names were specified.")
            sys.exit(1)

setup = Setup()


if __name__ == "__main__":
    setup.main()
