import datetime
import threading
import psycopg
import traceback
import time

class DatabaseManager:
    def __init__(self, config, logger, max_api_access_rate=420):
        self.db_connected = False
        self.conn = None
        self.cursor = None
        self.max_api_access_rate = max_api_access_rate
        self.logger = logger

        self.config = config

        self.last_block_ip_update_time = None
        self.updater_daemon = threading.Thread(target=self.DatabaseDaemon(self))

        self.connect_to_db()


    def get_cursor(self):
        if not self.db_connected:
            return None

        return self.conn.cursor()


    def connect_to_db(self):
        if self.config.get("database-name", None) is None:
            self.logger.error("The database_url is None. Did you forget to set it?")

        if self.config.get("username", None) is None:
            self.logger.error("The database_name is None. Did you forget to set it?")

        if self.config.get("password", None) is None:
            self.logger.error("The database_username is None. Did you forget to set it?")

        if self.config.get("database-url", None) is None:
            self.logger.error("The database_password is None. Did you forget to set it?")

        try:
            self.conn = psycopg.connect(
                dbname=self.config.get("database-name", None),
                user=self.config.get("username", None),
                password=self.config.get("password", None),
                host=self.config.get("database-url", None)
            )
            self.db_connected = True
        except psycopg.Error as e:
            self.logger.error("Connection to database failed. Error: {}".format(e))
            self.logger.error(traceback.format_exc())
            self.logger.warning("All database related functions will be unavailable.")

    class DatabaseDaemon(threading.Thread):
        def __init__(self, parent):
            threading.Thread.__init__(self)
            self.parent = parent
            self.daemon = True
            self.logger = parent.logger

        def run(self):
            while True:
                self.refresh_check()
                time.sleep(10)

        def refresh_check(self):
            try:
                self.check_database_connect()
            except psycopg.Error as e:
                self.logger.warning("The connection to the database is disconnected. Reconnecting...")
                self.parent.connect_to_db()

                try:
                    self.check_database_connect()
                except psycopg.Error as e:
                    self.logger.critical("Unable to refresh database connection. ERROR: {}".format(e))
                    return

                self.logger.info("Finished refreshing database connection.")

        def check_database_connect(self):
            cursor = self.parent.get_cursor()

            cursor.execute("SELECT version();")

            self.parent.conn.commit()




