from structure import SpaceNETManage
import asyncio
import os, sys
import requests
import threading
import time
import datetime

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

from space_net_lib.definition.path import manage_data_path
from space_net_lib.utils.tool import what_is_my_ip


class CloudflareManage:
    def __init__(self, logger, main_store, cf_config, secret_cf):
        self.logger = logger

        self.main_store = main_store
        self.secret = secret_cf
        self.cf_config = cf_config

        self.date_data = {
            "lastCallDate": datetime.datetime.now(),
            "inited": False
        }

    def update_domain_dns_record_if_ip_change(self):
        new_ip = what_is_my_ip()

        if new_ip is None:
            self.main_store["currentIP"] = "999.99.99.99"
            self.logger.warning("Unable to get the current IP. Is the server's internet connection down?")
            return True

        do_day_cycle = True if self.date_data["lastCallDate"] - datetime.datetime.now() >= datetime.timedelta(days=1) else False

        # print("IP: {} | New IP: {}".format(self.main_store.get("currentIP"), new_ip))
        # print(self.date_data["inited"], do_day_cycle)

        if new_ip != self.main_store.get("currentIP") or not self.date_data["inited"] or do_day_cycle:
            self.logger.info("IP change detected. Updating DNS record...")
            self.main_store["currentIP"] = new_ip

            if not self.date_data["inited"]:
                self.date_data["inited"] = True

            self.update_domain_dns_record(new_ip)

            return True

        return True

    def update_domain_dns_record(self, ip):
        domains = self.cf_config.get("dnsRecordList", [])

        if type(domains) is str:
            domains = [domains]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.secret.get("cf-dns-record-secret-token", None)}",
        }

        r = requests.get("https://api.cloudflare.com/client/v4/zones", headers=headers)

        if r.status_code == 401 or r.status_code == 403:
            self.logger.error("Unable to get zone ID . Did the token expired or does it have no permissions to access DNS records?")
            return False
        elif r.status_code != 200:
            self.logger.error("Unable to get zone id. HTTP status code: " + str(r.status_code))
            return False

        try:
            zone_id = r.json().get("result", {})[0].get("id", None)
        except IndexError:
            self.logger.error("Unable to get zone id. Unsupported format of the response.")
            return False

        r = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records", headers=headers)

        if r.status_code != 200:
            self.logger.error("Unable to get zone id.\n"
                              "Response data:" + str(r.json()))
            return False

        result = r.json().get("result", {})
        record_id = None

        # if self.cf_config.get("currentRootDomain", None) is None:
        #     self.logger.error("The key name \"currentRootDomain\" is undefined.")
        #     self.logger.warning("DNS record update process canceled.")
        #     return

        if len(self.cf_config.get("dnsRecordList", [])) == 0:
            self.logger.warning("The key name \"dnsRecordList\" is empty. Try disabling DNS update to "
                                "reduce data consumption.")
            return False

        self.logger.info(f"These domains dns record will be updated to IP address {ip} :\n{", ".join(map(str, domains))}")

        for domain in domains:
            for record in result:
                name = record.get("name", None)

                if name == domain:
                    record_id = record.get("id", None)
                    break

            if record_id is None:
                self.logger.error("Failed to get record id. Maybe current server domain {} name doesn't exist.".format(domain))
                continue

            ddns_data = {
                "type": "A",
                "name": domain,
                "content": self.main_store["currentIP"],
                "ttl": 120,
                "proxied": True
            }

            r = requests.put(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}",
                             headers=headers, json=ddns_data)

            if r.status_code == 200:
                self.logger.info(f"Successfully updated DNS record {domain} with IP address {ip}.")
            else:
                self.logger.error(f"Failed to update DNS record {domain} with IP address {ip}.\n"
                                  f"HTTP status code: {r.status_code}.")

        return True


class ManageDaemon(threading.Thread):
    def __init__(self, logger, main_store, daemon_config, secret, daemon=True):
        threading.Thread.__init__(self, daemon=daemon)
        self.logger = logger

        self.main_store = main_store
        self.config = daemon_config
        self.secret = secret
        self.cf_manage = CloudflareManage(logger=logger,
                                          cf_config=self.config.get("Cloudflare", {}),
                                          main_store=self.main_store,
                                          secret_cf=self.secret.get("Cloudflare", {}),)

        self.work = [
            {
                # Update cloudflare dns records when IP changes.
                "name": "CF DDNS Updater",
                "status": self.config.get("Cloudflare", {}).get("enableDomainDNSRecordUpdater", None),
                "mapFunc": self.cf_manage.update_domain_dns_record_if_ip_change,
                "parameters": None,
                "sleepTime": datetime.timedelta(seconds=10),
                "doDayCycle": True,
                "lastCallTime": datetime.datetime.now(),
                "failRecord": 0
            }
        ]

    def run(self):
        self.logger.info("Server daemon started.")
        while True:
            for work, index in zip(self.work, range(len(self.work))):
                max_attempt = self.config.get("processAttempt", 5)
                name = work.get("name", None)
                status = work.get("status", None)
                mapFunc = work.get("mapFunc", None)
                parameters = work.get("parameters", None)
                sleepTime = work.get("sleepTime", None)
                lastCallTime = work.get("lastCallTime", None)

                if not status:
                    continue

                if datetime.datetime.now() - lastCallTime >= datetime.timedelta(seconds=10):
                    self.logger.info("Processing work name {}".format(name))

                    if mapFunc is not None:
                        fail_record = self.work[index]["failRecord"]
                        status = mapFunc()
                        if status is False and fail_record < max_attempt:
                            attempt_left = max_attempt - fail_record
                            self.logger.warning(f"Seems like we got something wrong when processing work {name}? ({attempt_left} attempt left)")
                            self.work[index]["failRecord"] += 1
                        elif status is False:
                            self.work[index]["status"] = False
                            self.logger.warning(f"The process name {name} has been suspend. (Attempt count > {fail_record})")
                        else:
                            self.work[index]["failRecord"] = 0

                    self.work[index].update({"lastCallTime": datetime.datetime.now()})
            time.sleep(1)

class Manage(SpaceNETManage):
    def __init__(self):
        SpaceNETManage.__init__(self)

        self.main_store = {
            "currentIP": what_is_my_ip(),
            "initializeTime": time.time(),
        }

        self.server_daemon = ManageDaemon(self.logger,
            main_store=self.main_store,
            daemon_config=self.config.server_daemon,
            secret=self.config.secret)

        self.server_daemon.start()

        self.main()

    def main(self):
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.closing()
                sys.exit()