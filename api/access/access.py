import os
import sys
import threading
import time
import datetime

api_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(api_root_dir)

from database.database import DatabaseManager


class Access:
    def __init__(self, database: DatabaseManager, config, logger):
        """
        Control/Manage client access api system.
        """
        self.database = database
        self.config = config
        self.logger = logger

        self.access_daemon = self.AccessDaemon(database=database, config=config)
        self.access_daemon.start()

    def is_banned(self, ip: str):
        cursor = self.database.get_cursor()

        if cursor is None:
            return False

        cursor.execute(
            """
            SELECT
            CASE
                WHEN EXISTS (SELECT 1 FROM access.temporaryipban WHERE ip_address = %s) THEN 'IP Exists'
                ELSE 'IP does not exist'
            END AS RowStatus
            """,
            (ip,)
        )
        result_from_temp_ban = cursor.fetchone()

        if result_from_temp_ban[0] == "IP Exists":
            cursor.execute(
                "SELECT enddate FROM access.temporaryipban WHERE ip_address = %s",
                (ip,)
            )
            (endDate,) = cursor.fetchone()
            self.database.conn.commit()
            return True, endDate
        else:
            self.database.conn.commit()
            return False, None

    def ban_ip(self, ip: str):
        cursor = self.database.get_cursor()

        if cursor is None:
            return

        current_date = datetime.datetime.now()

        current_date += datetime.timedelta(minutes=10)

        cursor.execute(
            """
            INSERT INTO access.temporaryipban (ip_address, enddate)
            VALUES (%s, %s)
            """,
            (ip, current_date)
        )

        self.logger.info("IP {} of client got temporary IP ban. End until {}".format(ip, str(current_date)))

        self.database.conn.commit()


    def blocked_ip(self, ip: str):
        cursor = self.database.get_cursor()

        if cursor is None:
            return

        current_date = datetime.datetime.now()

        current_date += datetime.timedelta(minutes=10)

        cursor.execute(
            """
            INSERT INTO access.temporaryipban (ip_address, enddate)
            VALUES (%s)
            """,
            (ip, current_date)
        )

        self.logger.info("IP {} of client got blocked.".format(ip))

        self.database.conn.commit()


    def add_access_count(self, ip: str):
        cursor = self.database.get_cursor()

        if cursor is None:
            return

        cursor.execute(
            """
            SELECT
            CASE
                WHEN EXISTS (SELECT 1 FROM access.ipAccessTableRecord WHERE ip_address = %s) THEN 'IP Exists'
                ELSE 'IP does not exist'
            END AS RowStatus
            """,
            (ip,)
        )
        result = cursor.fetchone()

        if result and result[0] == 'IP Exists':
            cursor.execute(
                "SELECT accesscount FROM access.ipAccessTableRecord WHERE ip_address = %s",
                (ip,)
            )
            (accesscount,) = cursor.fetchone()

            if accesscount is None:
                accesscount = 0

            if accesscount > self.max_api_access_rate:
                self.do_ban_ip(ip)
                accesscount = 0

            accesscount += 1

            cursor.execute(
                """
                UPDATE access.ipAccessTableRecord
                SET accesscount = %s
                WHERE ip_address = %s
                """,
                (accesscount, ip)
            )

        else:
            cursor.execute(
                """
                INSERT INTO access.ipAccessTableRecord (ip_address)
                VALUES (%s)
                """,
                (ip,)
            )

        self.database.conn.commit()

    def unban(self, ip: str):
        cursor = self.database.get_cursor()

        if cursor is None:
            return

        cursor.execute(
            """
            DELETE FROM access.temporaryipban
            WHERE ip_address = %s
            """,
            (ip,)
        )

        self.database.conn.commit()

    def count_page_views(self, ip: str):
        cursor = self.database.get_cursor()

        if cursor is None:
            return False

        cursor.execute(
            """
            INSERT INTO normal.visitor_ip_record_logs (ip_address) 
            VALUES (%s)
            """,
            (ip,)
        )
        self.database.conn.commit()

        return True

    class AccessDaemon(threading.Thread):
        def __init__(self, database, config, daemon=True):
            threading.Thread.__init__(self)
            self.daemon = daemon

            self.database = database
            self.config = config

            self.current_dict = {
                "last_block_ip_update_time": None
            }

        def update_ban_ip_list(self):
            cursor = self.database.get_cursor()

            if not cursor:
                return


            cursor.execute(
                """
                DELETE FROM access.temporaryipban
                WHERE enddate < NOW()
                """
            )

            if self.current_dict.get("last_block_ip_update_time", None) is None:
                self.current_dict["last_block_ip_update_time"] = datetime.datetime.now()
            else:
                time_interval = datetime.datetime.now() - self.current_dict["last_block_ip_update_time"]

                if time_interval.min >= datetime.timedelta(minutes=10):
                    cursor.execute(
                        """
                        DELETE FROM access.temporaryipban
                        WHERE accesscount < %s
                        """,
                        (self.config["max_api_access_rate"],)
                    )

            self.database.conn.commit()

        def run(self):
            while True:
                self.update_ban_ip_list()

                time.sleep(10)



