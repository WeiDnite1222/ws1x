import threading
import time
import datetime
import os
import hashlib
from dynamicpages.web.private import PagesUtil
from bs4 import BeautifulSoup as bs
import traceback
import sys
import tempfile
import re

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

from space_net_lib.definition.path import dynamic_pages_data_path
from space_net_lib.utils.tool import calc_took_time


class DynamicResourceUpdater(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.config = config
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
        for root_dir, dirs, files in os.walk(self.config.get("webRootDir")):
            for file in files:
                file_path = os.path.join(root_dir, file)
                _, file_ext = os.path.splitext(file)
                if not file_ext in self.encoding_allow_list:
                    continue

                sha1_hash = hashlib.sha1()
                file_content = b""
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        sha1_hash.update(chunk)
                        file_content += chunk

                sha1 = sha1_hash.hexdigest()
                file_data = file_content.decode("utf-8")

                remove_prefix = self.config.get("webRootDir") + "/" if not file_path.endswith("/") else self.config.get("webRootDir")
                new_path = file_path.replace(remove_prefix, "", 1)

                if not self.resources_loaded:
                    self.resources[new_path] = file_data
                    self.resources_hash[new_path] = sha1
                else:
                    original_hash = self.resources_hash.get(new_path, None)

                    if original_hash is None:
                        continue

                    if sha1 != original_hash:
                        print("[SHA1Watcher] File name {} hash has changed, updating...".format(file))
                        self.resources[new_path] = file_data
                        self.resources_hash[new_path] = sha1

        self.resources_loaded = True

    def get_file(self, filepath):
        try:
            file_content = self.resources[filepath]
            return True, file_content
        except KeyError:
            return False, None

class CacheDaemon(threading.Thread):
    def __init__(self, config, logger):
        threading.Thread.__init__(self)
        self.config = config
        self.logger = logger

        self.cache_data_queue = []
        self.cache_data_queue_2 = []

        self.sleep_time = 50

        if type(self.config.get("sleepTime")) == int:
            self.sleep_time = self.config.get("sleepTime")

        self.cache_dir = os.path.join(dynamic_pages_data_path, "page_cache")

        self.caching_flag = False

        os.makedirs(self.cache_dir, exist_ok=True)

    def run(self):
        while True:
            self.caching_flag = True
            for cache_data in self.cache_data_queue:
                try:
                    real_path = os.path.join(self.cache_dir, cache_data.get("webFilePath", "<NULL>"))

                    data = self.insert_cache_date(cache_data["pageData"])

                    with open(real_path, "w", encoding="utf-8") as f:
                        f.write(str(data))
                except Exception as e:
                    self.logger.error("Unable to cache file {}\n"
                                      "ERROR: {}\n"
                                      "Traceback: {}".format(cache_data.get("webFilePath", "<UNKNOWN>"),e,
                                                           traceback.format_exc()))
            self.cache_data_queue.clear()

            self.caching_flag = False

            time.sleep(self.sleep_time)

    def cache_page(self,web_filepath, page_data):
        # self.logger.info("Caching page {}".format(web_filepath))
        data = {
            "webFilePath": web_filepath,
            "pageData": page_data,
            "cacheDate": datetime.datetime.now()
        }

        if not self.caching_flag:
            self.cache_data_queue.append(data)

            if len(self.cache_data_queue_2) > 0:
                self.cache_data_queue.extend(self.cache_data_queue_2)
        else:
            self.cache_data_queue_2.append(data)

    def get_page_cached_data(self, web_filepath):
        real_path = os.path.join(self.cache_dir, web_filepath)

        if not os.path.exists(real_path) or not os.path.isfile(real_path):
            return None

        try:
            with open(real_path, "r", encoding="utf-8") as f:
                data = f.read()
        except Exception as error:
            self.logger.error("Unable to get cache data for file {}\n"
                              "ERROR: {}".format(web_filepath, error))
            return None

        return data

    @staticmethod
    def insert_cache_date(page_data):
        if type(page_data) == bs:
            soup = page_data
        else:
            soup = bs(page_data, "lxml")

        head = soup.find("head")

        cache_date_meta = soup.new_tag("meta", attrs={"latest-cache-date": datetime.datetime.now()})

        if head is not None:
            head.append(cache_date_meta)

        return soup


class DynamicPagesDaemon(threading.Thread):
    def __init__(self, logger, resources_updater, full_config, version):
        threading.Thread.__init__(self)
        self.logger = logger
        self.resources_updater = resources_updater
        self.version = version

        self.config = full_config.dynamic_pages_daemon
        self.sites_config = full_config.sites_config
        self.dp_insert_config = full_config.dynamic_insert_config
        self.comm_config = full_config.communicate_support
        self.cache_settings = full_config.cache_settings

        self.pages_data = {}
        self.web_root_dir = full_config.dynamic_main.get("webRootDir")

        self.cache_daemon = CacheDaemon(self.cache_settings, self.logger)
        self.cache_daemon.start()
        self.pages_util = PagesUtil(web_root_dir=self.web_root_dir, logger=self.logger, communicate_cfg=self.comm_config)

        self.init_site()

    def init_site(self):
        for page_path, data in self.sites_config.items():
            if not page_path in self.resources_updater.resources.keys():
                self.logger.warning(f"File {page_path} not in the resources.")
                continue

            updateMethodList = data.get("updateMethodList", [])

            for updateMethodInfo in updateMethodList:
                updateMethodInfo["lastCallTime"] = datetime.datetime.now()
                updateMethodInfo["failRecord"] = 0
                updateMethodInfo["status"] = True

            file_data = self.resources_updater.resources[page_path]

            if self.config.get("useOldCacheWhenStart", False):
                cache_data = self.cache_daemon.get_page_cached_data(page_path)

                if cache_data is not None:
                    self.logger.info("Found existing cache data for page {}\n".format(page_path))
                    file_data = cache_data

            self.pages_data[page_path] = {
                "processFailFlag": False,
                "filename": os.path.basename(page_path),
                "fileData": file_data,
                "lastFinishedFilePath": page_path,
                "lastFinishedTime": datetime.datetime.now(),
                "updateMethodList": updateMethodList,
            }

    def run(self):
        self.logger.info("Starting dynamic pages daemon...")
        while True:
            for page_path, page_data in self.pages_data.items():
                page_name = page_data.get("filename")
                max_attempt = self.config.get("processAttempt", 5)
                result_list = []

                byte_data = self.resources_updater.resources[page_path]
                updated = False

                if page_data["processFailFlag"]:
                    continue

                for page_process in page_data["updateMethodList"]:
                    status = page_process["status"]

                    if not status:
                        continue

                    sleep_time = datetime.timedelta(seconds=page_process.get("sleepTime", 10))
                    last_call_time = page_process.get("lastCallTime", datetime.datetime.now()-sleep_time)
                    func_name = page_process["mapFuncNameInPagesUtil"]
                    func = getattr(self.pages_util, func_name, None)

                    if func is None:
                        page_process["status"] = False
                        continue

                    if datetime.datetime.now() - last_call_time >= sleep_time:

                        try:
                            result, new_data = func(byte_data)
                        except Exception as err:
                            page_process["status"] = False
                            self.logger.error("An error occurred while processing page name {}\n"
                                              "At_Func_Name: {}\n"
                                              "Traceback: {}\n".format(page_name,
                                                                       func_name,
                                                                       traceback.format_exc()))
                            continue

                        result_list.append(result)
                        updated = True

                        if result is True:
                            byte_data = new_data
                            page_process["lastCallTime"] = datetime.datetime.now()
                        else:
                            fail_record = page_process["failRecord"]

                            if not self.config.get("enableFailAttempt", False):
                                self.logger.warning(f"Seems like we got something wrong when processing work {func_name}? (At {page_name})")
                            elif fail_record < max_attempt:
                                attempt_left = max_attempt - fail_record
                                self.logger.warning(
                                    f"Seems like we got something wrong when processing work {func_name}? (At {page_name})"
                                    f" ({attempt_left} attempt left)")
                                page_process["failRecord"] += 1
                            else:
                                page_process["status"] = False
                                self.logger.warning(
                                    f"The process name {func_name} has been suspend. (At {page_name})"
                                    f" (Attempt count > {fail_record})")

                if updated:
                    if False not in result_list:
                        page_data["fileData"] = byte_data

                        if self.cache_settings.get("savePageCache", False):
                            self.cache_daemon.cache_page(page_path, byte_data)
                        continue

                    if self.config.get("useCacheWhenProcessFailed", False):
                        self.logger.warning("Unable to process page {}. PageDaemon will use cache from memory/disk"
                                            " as the failback. This may cause your new change cannot be updated to server util"
                                            " a successful process data saved..\n".format(page_path))
                        if page_data["fileData"] == byte_data:
                            data = self.cache_daemon.get_page_cached_data(page_path)

                            if data is not None:
                                page_data["fileData"] = data
                                self.logger.info(
                                    "Use cached data from disk for page {} as failback.\n".format(page_path))
                            else:
                                self.logger.info(
                                    "Unable to grab cache data. Use original data as failback\n".format(page_path))
                                page_data["fileData"] = self.resources_updater.resources[page_path]
                        else:
                            self.logger.warning(
                                "Use cached data from memory for page {} as failback.\n".format(page_path))
                    elif self.config.get("skipUpdateIfAnyProcessFailed", False):
                        self.logger.warning("Skip update for page {} as failback.\n".format(page_path))
                    else:
                        self.logger.error("Update failed for page {}. Use original data as failback".format(page_path))
                        page_data["fileData"] = self.resources_updater.resources[page_path]

                # if False not in result_list:
                #     print("Saving process data for page {}\n".format(page_path))
                #     page_data["fileData"] = byte_data
                #
                #     if self.cache_settings.get("savePageCache", False):
                #         self.cache_daemon.cache_page(page_path, byte_data)
                # elif self.config.get("useCacheWhenProcessFailed", False):
                #     # Use memory cache first, if not found use disk cache
                #
                #     if page_data["fileData"] == byte_data:
                #         data = self.cache_daemon.get_page_cached_data(page_path)
                #
                #         if data is not None:
                #             page_data["fileData"] = data
                #             self.logger.warning(
                #                 "Use cached data from disk for page {} as failback.\n".format(page_path))
                #         else:
                #             self.logger.error(
                #                 "Unable to grab cache data. Use original data as failback\n".format(page_path))
                #             page_data["fileData"] = self.resources_updater.resources[page_path]
                #     else:
                #         self.logger.warning("Use cached data from memory for page {} as failback.\n".format(page_path))
                # elif self.config.get("skipUpdateIfAnyProcessFailed", False):
                #     self.logger.warning("Skip update for page {} as failback.\n".format(page_path))
                # else:
                #     self.logger.error("Update failed for page {}. Use original data as failback".format(page_path))
                #     page_data["fileData"] = self.resources_updater.resources[page_path]


            time.sleep(1)

    def safe_get(self, page_path):
        data = self.pages_data.get(page_path, {}).get("fileData", None)

        if data is None:
            data = self.resources_updater.resources.get(page_path, None)

            if data is None:
                return f"""<!DOCTYPE html>
                <h1>File {page_path} missing</h1>
                """

        return data

    # @calc_took_time
    def get_html(self, page_path, request):
        if page_path in self.pages_data.keys():
            html = self.pages_data.get(page_path, {}).get("fileData", None)
        else:
            print("Get from resources_updater {}".format(page_path))
            html = self.resources_updater.resources.get(page_path, None)

        if html is None:
            print("{} is None".format(page_path))
            return f"""<!DOCTYPE html>
            <h1>File {page_path} is missing</h1>"""

        current_page_work_list = self.dp_insert_config.get(page_path, {}).get("insertMethodList", [])

        current_page_work_list.extend(self.dp_insert_config.get("<ANY>", {}).get("insertMethodList", []))

        for func_data in current_page_work_list:
            func = getattr(self.pages_util, func_data["mapFuncNameInPagesUtil"], None)

            if func is not None:
                try:
                    html = func(html, request)
                except Exception as e:
                    print("Unexpected error while processing page insert function.\n"
                          "ERROR: {}\n"
                          "Traceback: {}".format(e, traceback.format_exc()))

        html = self.insert_dp_label(html)

        return html

    def insert_dp_label(self, page_data):
        if type(page_data) is bs:
            soup = page_data
        else:
            soup = bs(page_data, "lxml")

        head = soup.find("head")

        if head is None:
            return soup

        if soup.find("meta", attrs={"label": f"DynamicPages v{self.version}"}) is not None:
            return soup

        dp_meta_label = soup.new_tag("meta", attrs={"label": f"DynamicPages v{self.version}"})

        head.insert(0, dp_meta_label)

        soup.prettify()

        return soup.prettify()









