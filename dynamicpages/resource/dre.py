import threading
import os
from api.main import logger


class DynamicResourceUpdater(threading.Thread):
    def __init__(self, config, logger):
        threading.Thread.__init__(self, daemon=True)
        self.config = config
        self.logger = logger
        self.resources_loaded = False
        self.resources = {}
        self.resources_hash = {}
        self.blocked_files = []
        self.encoding_allow_list = [".txt", ".js", ".md", ".html"]
        self.web_root_dir = self.config.get("webRootDir")

        if not os.path.exists(self.web_root_dir):
            self.logger.error("Current website root directory (PATH: {}) does not exist.".format(self.web_root_dir))

        self.file_finder()

    def run(self):
        while True:
            self.file_finder()
            time.sleep(5)

    def file_finder(self):
        def add_file_to_blocked_files(filepath):
            self.blocked_files.append(filepath)

        for root_dir, dirs, files in os.walk(self.web_root_dir):
            for file in files:
                file_path = os.path.join(root_dir, file)
                _, file_ext = os.path.splitext(file)

                if file_path in self.blocked_files:
                    continue

                if not file_ext in self.encoding_allow_list:
                    continue

                try:
                    sha1_hash = hashlib.sha1()
                    file_content = b""
                    with open(file_path, 'rb') as f:
                        while True:
                            chunk = f.read(4096)

                            # EOF
                            if not chunk:
                                break

                            sha1_hash.update(chunk)
                            file_content += chunk
                except Exception as e:
                    self.logger.error("Unable to read file >"
                                      "\nPATH : {} "
                                      "\nNAME : {}"
                                      "\nERROR : {}"
                                      "\nSkipping this file...".format(file_path, file, e))
                    add_file_to_blocked_files(file_path)
                    continue

                try:
                    sha1 = sha1_hash.hexdigest()
                except Exception as e:
                    self.logger.error("Unable to get file sha1 hash."
                                      "\nPATH : {} "
                                      "\nNAME : {}"
                                      "\nERROR : {}"
                                      "\nSkipping this file...".format(file_path, file, e))
                    add_file_to_blocked_files(file_path)
                    continue

                try:
                    file_data = file_content.decode("utf-8")
                except Exception as e:
                    self.logger.error("Unable to decode file in utf-8 format."
                                      "\nPATH : {} "
                                      "\nNAME : {}"
                                      "\nERROR : {}"
                                      "\nSkipping this file...".format(file_path, file, e))
                    add_file_to_blocked_files(file_path)
                    continue

                remove_prefix = self.web_root_dir + "/" if not file_path.endswith("/") else self.web_root_dir
                new_path = file_path.replace(remove_prefix, "", 1)

                if not self.resources_loaded:
                    self.resources[new_path] = file_data
                    self.resources_hash[new_path] = sha1
                else:
                    original_hash = self.resources_hash.get(new_path, None)

                    if original_hash is None:
                        continue

                    if sha1 != original_hash:
                        print("[FileWatchDog] File name {} hash has changed, updating...".format(file))
                        self.resources[new_path] = file_data
                        self.resources_hash[new_path] = sha1
                        return

        self.resources_loaded = True

    def get_file(self, filepath):
        try:
            file_content = self.resources[filepath]
            return True, file_content
        except KeyError:
            return False, None