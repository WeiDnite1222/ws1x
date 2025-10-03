import subprocess
import sys
from datastructure import data_list
import os
import yaml
import shlex


# for user in pwd.getpwall():
#     print(f"Username: {user.pw_name}, UID: {user.pw_uid}, Home Directory: {user.pw_dir}")
#
# username = str(input("Please enter a username as the api install place: "))
#
# home = None
#
# for user in pwd.getpwall():
#     username = user.pw_name
#     if username == username:
#         home = user.pw_dir
#         break
#
# if home is None:
#     print(f"No home directory found for {username}")
#     sys.exit(1)
# else:
#     print(f"Home directory for {username} is: {home}")

def is_running_as_root_unix():
    return os.geteuid() == 0


def replace_real_path(path):
    path = path.replace("${HOME}", os.path.join("/home", os.getenv("SUDO_USER")))
    path = path.replace("${SPACENET_API_ROOT}", os.path.join("/var", "SpaceNET-API"))
    return path

def create_data(api_data_dir):
    if os.path.exists(api_data_dir):
        print("API data exists. Would you like to overwrite it? y/n")
        if input().lower() != "y":
            print("Canceled...")
            sys.exit()

    for item in data_list:
        name = item.get("name")
        print("Creating cfg/data name {}".format(name))

        filepath = replace_real_path(item.get("savedLocation"))
        default_data = item.get("defaultData")

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as f:
            yaml.dump(default_data, f, indent=4)

        print("Creating cfg/data path {}".format(filepath))


def fix_execute_permission(api_data_dir):
    for root, dirs, files in os.walk(api_data_dir):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                subprocess.run(shlex.split("chmod +x {}".format(filepath)))
            except Exception as error:
                pass


def normal_exit(api_data_dir):
    print("Fixing permission...")

    print("Done")
    sys.exit(0)


def setup():
    # Permissions Check
    if not is_running_as_root_unix():
        print("This script must be run as root. Exiting...")
        sys.exit(1)
    else:
        sudo_username = os.getenv("SUDO_USER")

        if sudo_username == "root":
            print("Could not find sudo user. Exiting...")
            sys.exit(1)

    print("> SpaceNET API Installation")

    # Root Dir (API program file store location)
    root_dir = os.path.abspath(os.path.dirname(__file__))
    api_data_dir = os.path.join(os.path.join("/var", 'SpaceNET-API'))

    print("Creating virtual environments for api...")

    try:
        subprocess.run(["python3", "-m", "venv", "apivenv"], check=True)
    except Exception as error:
        print("Unable to create virtual environment. {}".format(error))
        print("Canceled...")

    print("Creating api data...")
    create_data(api_data_dir)

    boot_api_sh_data = """\
    #!/bin/bash
    # shellcheck disable=SC2164
    cd '{}'
    source apivenv/bin/activate
    uvicorn main:app --reload
    """.format(root_dir)

    print("Creating bootstrap...")
    bootstrap_sh_filepath = os.path.join("/opt", "api_service", "bootstrap.sh")
    os.makedirs(os.path.dirname(bootstrap_sh_filepath), exist_ok=True)

    with open(bootstrap_sh_filepath, "w") as f:
        f.write(boot_api_sh_data)

    print("Creating new group/account for api service...")

    try:
        try:
            subprocess.run(["getent", "group", "spacenet-service-group"], check=True)
            subprocess.run(["groupadd", "--system", "spacenet-service-group"], check=True)
            subprocess.run(["groupadd", "spacenet-service-group"], check=True)
        except subprocess.CalledProcessError:
            print("Group already exists. Bypassing...")
    except Exception as error:
        print("Unable to create new group/account for api service. {}".format(error))
        print("Canceled...")
        sys.exit()

    try:
        try:
            subprocess.run(["id", "-u", "spacenet-api-user"], check=True)
        except subprocess.CalledProcessError:
            subprocess.run(["useradd", "-m", "spacenet-api-user"], check=True)

        # Add spacenet-api-user to group
        subprocess.run(["usermod", "-a", "-G", "spacenet-service-group", "spacenet-api-user"], check=True)

        # Add root to group
        subprocess.run(["usermod", "-a", "-G", "spacenet-service-group", "root"], check=True)
    except Exception as error:
        print("Unable to create new account for api service: {}".format(error))
        print("Canceled...")
        sys.exit()

    print("Fixing permission...")
    path_list = [api_data_dir, root_dir, os.path.dirname(bootstrap_sh_filepath)]

    try:
        for path in path_list:
            subprocess.run(["chown", "-R", 'spacenet-api-user:spacenet-service-group', '{}'.format(
                os.path.abspath(path)
            )], check=True)

            term = subprocess.Popen(["find", '{}'.format(os.path.abspath(path)),
                                     "-type", "d", "-print0"], stdout=subprocess.PIPE)
            find_out = term.communicate()[0]
            term2 = subprocess.Popen(['xargs', "-0", "-r", "chmod", "2755"],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            op = term2.communicate(find_out)[0].decode()
            print(op)

            term = subprocess.Popen(["find", '{}'.format(os.path.abspath(path)),
                                     "-type", "f", "-print0"], stdout=subprocess.PIPE)
            find_out = term.communicate()[0]
            term2 = subprocess.Popen(['xargs', "-0", "-r", "chmod", "664"],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            op = term2.communicate(find_out)[0].decode()
            print(op)

            subprocess.run(shlex.split('setfacl -R -m g:"spacenet-service-group":rwx {}'.format(
                os.path.abspath(path)
            )), check=True)

            subprocess.run(shlex.split('setfacl -R -d -m g:"spacenet-service-group":rwx {}'.format(
                os.path.abspath(path)
            )), check=True)

            subprocess.run(shlex.split('setfacl -R -m g:"root":rwx {}'.format(
                os.path.abspath(path)
            )), check=True)

            subprocess.run(shlex.split('setfacl -R -d -m g:"root":rwx {}'.format(
                os.path.abspath(path)
            )), check=True)

            subprocess.run(shlex.split('setfacl -R -m g:"{}":rwx {}'.format(os.getenv("SUDO_USER"),
                                                                            os.path.abspath(path)
                                                                            )), check=True)

            subprocess.run(shlex.split('setfacl -R -d -m g:"{}":rwx {}'.format(os.getenv("SUDO_USER"),
                                                                               os.path.abspath(path)
                                                                               )), check=True)

            fix_execute_permission(path)

            while path != "/":
                subprocess.run(["setfacl", "-m", "g:spacenet-service-group:rx", os.path.abspath(path)], check=True)
                path = os.path.dirname(path)

    except Exception as error:
        print("Unable to fix permission. {}".format(error))
        print("Canceled...")
        sys.exit(1)

    print("Would you like to create a service for api? y/n")
    result = input().lower()

    if result != "y":
        print("Run script {} to launch api service".format(bootstrap_sh_filepath))
        print("Installation completed.")
        sys.exit()

    api_service_data = """
    [Unit]
    Description=SpaceNET API Service
    After=network.target

    [Service]
    User=spacenet-api-user
    ExecStart=bash {}

    [Install]
    WantedBy=multi-user.target
    """.format(bootstrap_sh_filepath)

    service_filepath = os.path.join("/", "etc", "systemd", "system", "spacenet.api.service")
    os.makedirs(os.path.dirname(service_filepath), exist_ok=True)

    with open(service_filepath, "w") as f:
        f.write(api_service_data)
        f.close()

    print("Reloading daemon...")
    os.system("systemctl daemon-reload")

    print("Would you like to start api service now? y/n")

    result = input().lower()
    if result != "y":
        os.system("systemctl restart spacenet.api.service")

    print("Do you want to start api service when startup? y/n")

    os.system("systemctl enable spacenet.api.service")

    print("Installation completed.")


if __name__ == "__main__":
    setup()