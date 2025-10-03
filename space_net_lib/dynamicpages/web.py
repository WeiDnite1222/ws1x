import hashlib
import json
import os
import threading
import time
from webinsert import WebInsertUtil


class WEBResourceUpdater(threading.Thread):
    def __init__(self, logger, dynamic_pages_config):
        threading.Thread.__init__(self)
        self.logger = logger
        self.dynamic_pages_config = dynamic_pages_config
        self.resources_loaded = False
        self.resources = {}
        self.resources_hash = {}
        self.daemon = True
        self.encoding_allow_list = [".txt", ".js", ".md", ".html"]
        self.file_finder()

    def run(self):
        while True:
            self.file_finder()
            time.sleep(5)

    def file_finder(self):
        for root_dir, dirs, files in os.walk(self.dynamic_pages_config.DPDefaultSettings["websiteRootDir"]):
            for file in files:
                _, file_ext = os.path.splitext(file)
                if not file_ext in self.encoding_allow_list:
                    continue

                sha1_hash = hashlib.sha1()
                file_content = b""
                with open(os.path.join(root_dir, file), 'rb') as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        sha1_hash.update(chunk)
                        file_content += chunk

                sha1 = sha1_hash.hexdigest()
                file_data = file_content.decode("utf-8")

                if not self.resources_loaded:
                    self.resources[file] = file_data
                    self.resources_hash[file] = sha1
                else:
                    original_hash = self.resources_hash.get(file, None)

                    if original_hash is None:
                        continue

                    if sha1 != original_hash:
                        print("[FileWatcher] File name {} hash has changed, updating...".format(file))
                        self.resources[file] = file_data
                        self.resources_hash[file] = sha1

        self.resources_loaded = True

    def get_file(self, filename):
        try:
            file_content = self.resources[filename]
            return True, file_content
        except KeyError:
            return False, None


class PagesResourceUpdater(threading.Thread):
    def __init__(self, root_dir, resources_updater):
        self.web_insert = WebInsertUtil()
        threading.Thread.__init__(self)
        self.resources_updater: WEBResourceUpdater = resources_updater
        self.page_resources = {}
        self.pages_config = [
            {
                "__sample__": True,
                "filename": 'index.html',
                "updateMethodList": ["method_name"]
            }
        ]

        self.init()

    def run(self):
        while True:
            self.read_cfg()
            for file in self.pages_config:
                if file.get("__sample__"):
                    continue

                filename = file["filename"]

                method_name_list = file["updateMethodList"]

                page_data = self.resources_updater.resources[filename]

                for method_name in method_name_list:
                    try:
                        method = getattr(self.web_insert, method_name)
                        page_data = method(page_data)
                    except Exception as error:
                        print("Unexpected error: {}".format(error))

                self.page_resources[filename] = page_data

            time.sleep(5)

    def init(self):
        self.create_cfg()

