import datetime
import re
import os
import sys
import secrets
import threading
import time
import bcrypt
import logging

api_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(api_root_dir)

from database.database import DatabaseManager
from libraries.cloudflare.tool import check_turnstile_token

class Yazule:
    """
    Account system

    Some part of authentication structure referenced OAuth 2.0 authorization.
    """
    def __init__(self, database: DatabaseManager, config, logger: logging.Logger) -> None:
        self.yazule_version = "v1"

        self.database = database
        self.logger = logger
        self.config = config

        self.yazule_daemon = self.YazuleDaemon(database)
        self.yazule_daemon.start()

    def create_tab_access_token(self, user_ip:str, access_tab_name:str, cf_turnstile_token) -> (bool, str or None, datetime.datetime):
        """
        Create table tokens.tabaccesstoken before use this method.

        Create yazule access token
        CREATE TABLE tokens.tabaccesstoken (
        user_ip_address VARCHAR(45) NOT NULL,
        create_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        expired_at TIMESTAMP NOT NULL,
        access_tab_name VARCHAR(128)
        );
        """
        # Check cf_turnstile_token valid
        result = check_turnstile_token(cf_turnstile_token, self.config.get("cf_turnstile_secret_token"), user_ip)

        if not result:
            return False, None, None

        # Generate token
        tab_access_token = secrets.token_urlsafe(128)
        expired_date = datetime.datetime.now() + datetime.timedelta(minutes=10)

        cursor = self.database.get_cursor()

        if not cursor:
            return False, None, None

        # Insert new token data to table tokens.tabaccesstoken
        cursor.execute(
            """
            INSERT INTO tokens.tabaccesstoken (user_ip_address, expired_at, access_tab_name, token)
            VALUES (%s, %s, %s, %s);
            """,
            [user_ip, expired_date, access_tab_name, tab_access_token]
        )

        self.database.conn.commit()

        self.logger.info("User ip {} required access tab {} token created".format(user_ip, access_tab_name))

        return True, tab_access_token, expired_date

    def is_valid_tab_access_token(self, user_ip_address, tab_access_token, current_tab_name, with_addition_access_count=False) -> bool:
        cursor = self.database.get_cursor()

        if not cursor:
            return False

        cursor.execute(
            """
            SELECT
            CASE
                WHEN EXISTS (SELECT 1 FROM tokens.tabaccesstoken WHERE token = %s AND user_ip_address = %s) THEN 'Found token'
                ELSE 'Token does not exist'
            END AS RowStatus
            """,
            (tab_access_token, user_ip_address)
        )
        result = cursor.fetchone()

        if result[0] == "Token does not exist":
            self.database.conn.commit()
            return False

        cursor.execute(
            """
            SELECT access_tab_name FROM tokens.tabaccesstoken WHERE token = %s
            """,
            (tab_access_token,)
        )
        (db_original_tab_name,) = cursor.fetchone()

        if not db_original_tab_name == current_tab_name:
            self.database.conn.commit()
            return False

        if with_addition_access_count:
            cursor.execute(
                """
                SELECT access_count FROM tokens.tabaccesstoken WHERE token = %s
                """,
                (tab_access_token,)
            )

            access_count = cursor.fetchone()[0]

            access_count += 1

            cursor.execute(
                """
                UPDATE tokens.tabaccesstoken SET access_count = %s WHERE token = %s
                """,
                (access_count, tab_access_token)
            )

        self.database.conn.commit()

        return True


    def get_tab_access_token_access_tab_name(self, tab_access_token):
        cursor = self.database.get_cursor()

        if not cursor:
            return False, None

        cursor.execute(
            """
            SELECT
            CASE
                WHEN EXISTS (SELECT 1 FROM tokens.tabaccesstoken WHERE token = %s) THEN 'Found token'
                ELSE 'Token does not exist'
            END AS RowStatus
            """,
            (tab_access_token,)
        )
        result = cursor.fetchone()

        if result[0] == "Token does not exist":
            self.database.conn.commit()
            return False, None

        cursor.execute(
            """
            SELECT access_tab_name FROM tokens.tabaccesstoken WHERE token = %s
            """,
            (tab_access_token,)
        )
        (db_original_tab_name,) = cursor.fetchone()

        self.database.conn.commit()

        return True, db_original_tab_name

    @staticmethod
    def escape_regex_special_chars(text: str) -> str:
        return re.escape(text)

    def account_exist(self, account_address):
        cursor = self.database.get_cursor()

        if not cursor:
            return True

        cursor.execute(
            """
            SELECT
            CASE
                WHEN EXISTS (SELECT 1 FROM Yazule.Accounts WHERE account_address = %s) THEN 'Found account'
                ELSE 'Account does not exist'
            END AS RowStatus
            """,
            (account_address,)
        )
        result = cursor.fetchone()

        self.database.conn.commit()

        if result[0] == "Found account":
            return True

        return False

    def email_exist(self, email_address):
        cursor = self.database.get_cursor()

        if not cursor:
            return True

        cursor.execute(
            """
            SELECT
            CASE
                WHEN EXISTS (SELECT 1 FROM Yazule.Accounts WHERE email = %s) THEN 'Found account'
                ELSE 'Account does not exist'
            END AS RowStatus
            """,
            (email_address,)
        )
        result = cursor.fetchone()

        self.database.conn.commit()

        if result[0] == "Found account":
            return True

        return False

    class AccountCreatePart1Status:
        status: bool = False
        account_name_too_short: bool = False
        account_name_too_long: bool = False
        account_name_check_failed: bool = False
        not_allow_to_create_account: bool = False
        token: str = None

    def get_register_token(self, user_ip, account_name):
        status_instance = self.AccountCreatePart1Status()

        if len(account_name) < 2:
            status_instance.account_name_too_short = True
            return status_instance

        if len(account_name) > 31:
            status_instance.account_name_too_long = True
            return status_instance

        cursor = self.database.get_cursor()

        param = f"%{self.escape_like(account_name)}"

        cursor.execute(
            """
            SELECT * FROM yazule.wordfilter WHERE text ILIKE %s
            """,
            (param,)
        )

        result = cursor.fetchone()

        if result is not None:
            self.database.conn.commit()
            status_instance.account_name_check_failed = True
            return status_instance

        param = f"{self.escape_like(account_name)}%"

        cursor.execute(
            """
            SELECT * FROM yazule.wordfilter WHERE text ILIKE %s
            """,
            (param,)
        )

        result = cursor.fetchone()

        if result is not None:
            self.database.conn.commit()
            status_instance.account_name_check_failed = True
            return status_instance

        register_temp_token = secrets.token_urlsafe(128)
        expired_date = datetime.datetime.now() + datetime.timedelta(minutes=5)

        cursor.execute(
            """
            INSERT INTO Yazule.RegisterTempToken (account_name, user_ip, token, expired_at)
            VALUES (%s, %s, %s, %s)
            """,
            (account_name, user_ip, register_temp_token, expired_date)
        )

        status_instance.status = True
        status_instance.token = register_temp_token

        return status_instance


    def valid_register_token(self, user_ip, register_token):
        cursor = self.database.get_cursor()

        cursor.execute(
            """
            SELECT
            CASE
                WHEN EXISTS (SELECT 1 FROM Yazule.RegisterTempToken WHERE user_ip = %s AND token = %s) THEN 'Found token'
                ELSE 'Token does not exist'
            END AS RowStatus
            """,
            (user_ip, register_token)
        )

        (result,) = cursor.fetchone()

        self.database.conn.commit()

        if result == "Found token":
            return True
        else:
            return False

    def remove_register_token(self, register_token):
        cursor = self.database.get_cursor()

        cursor.execute(
            """
            DELETE FROM yazule.RegisterTempToken WHERE token = %s
            """,
            (register_token,)
        )

        self.database.conn.commit()

        return True

    def get_account_name_by_register_token(self, register_token):
        """
        Token MUST be existed!!!
        """
        cursor = self.database.get_cursor()

        cursor.execute(
            """
            SELECT account_name FROM Yazule.RegisterTempToken WHERE token = %s 
            """,
            (register_token,)
        )

        (account_name,) = cursor.fetchone()

        self.database.conn.commit()

        return account_name

    @staticmethod
    def escape_like(user_input: str) -> str:
        return user_input.replace('%', '\\%').replace('_', '\\_')

    class AccountCreateStatus:
        status: bool = False
        duplicate_address: bool = False
        duplicate_email: str = False
        account_email_check_failed: bool = False
        account_address_check_failed: bool = False
        account_address_too_short: bool = False
        account_address_too_long: bool = False
        password_check_failed: bool = False
        password_too_short: bool = False
        password_too_long: bool = False
        wrong_birthday_format: bool = False
        wrong_account_address_format: bool = False
        account_address_missing_at_sign: bool = False

    def create_account_full_process(self, register_token, account_address, account_name, account_birth_date,
                                    account_email, password):
        status_instance = self.AccountCreateStatus()

        result = self.account_exist(account_address)

        if result:
            status_instance.status = False
            status_instance.duplicate_address = True
            return status_instance

        def check_address(account_address):
            n = account_address.count('@')

            if n > 1 or n == 0:
                return False
            elif not account_address.startswith('@'):
                return False

            return True

        if not check_address(account_address):
            status_instance.wrong_account_address_format = True
            status_instance.status = False
            return status_instance

        result = self.email_exist(account_email)
        if result:
            status_instance.status = False
            status_instance.duplicate_email = True
            return status_instance

        def check_email(email):
            return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

        if not check_email(account_email):
            status_instance.status = False
            status_instance.account_email_check_failed = True
            return status_instance

        if len(password) < 10:
            status_instance.status = False
            status_instance.password_too_short = True
            return status_instance

        if len(password) > 35:
            status_instance.status = False
            status_instance.password_too_long = True
            return status_instance

        def check_password(password: str) -> bool:
            pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{10,35}$"
            return bool(re.match(pattern, password))

        if not check_password(password):
            status_instance.status = False
            status_instance.password_check_failed = True
            return status_instance

        if len(account_address) < 3:
            status_instance.status = False
            status_instance.account_address_too_short = True
            return status_instance

        if len(account_address) > 36:
            status_instance.status = False
            status_instance.account_address_too_long = True
            return status_instance

        cursor = self.database.get_cursor()

        param = f"%{self.escape_like(account_address)}"

        cursor.execute(
            """
            SELECT * FROM yazule.wordfilter WHERE text ILIKE %s
            """,
            (param,)
        )

        result = cursor.fetchone()

        if result is not None:
            status_instance.status = False
            status_instance.account_address_check_failed = True
            self.database.conn.commit()
            return status_instance

        param = f"{self.escape_like(account_address)}%"

        cursor.execute(
            """
            SELECT * FROM yazule.wordfilter WHERE text ILIKE %s
            """,
            (param,)
        )

        result = cursor.fetchone()

        if result is not None:
            status_instance.status = False
            status_instance.account_address_check_failed = True
            self.database.conn.commit()
            return status_instance

        param = f"{self.escape_like(password)}%"

        cursor.execute(
            """
            SELECT * FROM yazule.unsafepassword WHERE password ILIKE %s
            """,
            (param,)
        )

        result = cursor.fetchone()

        if result is not None:
            status_instance.status = False
            status_instance.password_check_failed = True
            self.database.conn.commit()
            return status_instance

        try:
            birth_date = datetime.datetime.strptime(account_birth_date, "%Y-%m-%d")
        except ValueError:
            birth_date = None

        if birth_date is None:
            status_instance.status = False
            status_instance.wrong_birthday_format = True
            return status_instance

        self.remove_register_token(register_token)

        result = self.create_account(account_address, account_name, birth_date, account_email, password)

        if result is False:
            status_instance.status = False
            return status_instance

        status_instance.status = True
        self.database.conn.commit()

        return status_instance

    def create_account(self, account_address, account_name, account_birth_date, account_email ,password):
        """
        CREATE TABLE Yazule.Accounts (
            account_address VARCHAR(35) PRIMARY KEY NOT NULL,
            username VARCHAR(30) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(128) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor = self.database.get_cursor()

        if not cursor:
            return False

        password_bytes = password.encode('utf-8')

        salt = bcrypt.gensalt()

        hashed_password = bcrypt.hashpw(password_bytes, salt)

        string_password = hashed_password.decode('utf-8')

        cursor.execute(
            """
            INSERT INTO Yazule.Accounts (account_address, username, password_hash, email)
            VALUES (%s, %s, %s, %s)
            """,
            (account_address, account_name, string_password, account_email)
        )

        cursor.execute(
            """
            INSERT INTO Yazule.AccountData (account_address, date_of_birth)
            VALUES (%s, %s)
            """,
            (account_address, account_birth_date)
        )

        cursor.execute(
            """
            INSERT INTO Yazule.account_security (account_address, current_group)
            VALUES (%s, %s)
            """,
            (account_address, "user")
        )

        self.database.conn.commit()

        self.logger.info("Account {} created.".format(account_address))

        return True

    def account_locked(self, account_address):
        cursor = self.database.get_cursor()

        if not cursor:
            return False

        cursor.execute(
            """
            SELECT
            CASE
                WHEN EXISTS (SELECT 1 FROM yazule.account_security WHERE account_address = %s AND locked = TRUE) THEN 'Account locked'
                ELSE 'Account is not locked yet'
            END AS RowStatus
            """,
            (account_address,)
        )

        (result,) = cursor.fetchone()

        self.database.conn.commit()

        if result == "Account locked":
            return True
        else:
            return False


    class LoginInstancer(object):
        status: bool = False
        account_does_not_exist: bool = False
        account_locked: bool = False
        token: str = ""

    def get_login_token(self, account_address, user_ip) -> LoginInstancer:
        instance = self.LoginInstancer()
        cursor = self.database.get_cursor()

        if not cursor:
            return instance

        if not self.account_exist(account_address):
            instance.account_does_not_exist = True
            return instance

        if self.account_locked(account_address):
            instance.account_locked = True
            return instance

        login_token = secrets.token_urlsafe(128)
        expired_date = datetime.datetime.now() + datetime.timedelta(minutes=2)

        cursor.execute(
            """
            INSERT INTO yazule.login_token (account_address, token, expired_at, client_ip)
            VALUES (%s, %s, %s, %s)
            """,
            (account_address, login_token, expired_date, user_ip)
        )

        self.database.conn.commit()

        instance.status = True
        instance.token = login_token

        return instance

    def check_login_token_with_address_result(self, token, ip=None):
        cursor = self.database.get_cursor()

        if not cursor:
            return False, False, None

        if ip is None:
            cursor.execute(
                """
                SELECT
                CASE
                    WHEN EXISTS (SELECT 1 FROM yazule.login_token WHERE token = %s) THEN 'Found'
                    ELSE 'Not found'
                END AS RowStatus
                """,
                (token,)
            )
        else:
            cursor.execute(
                """
                SELECT
                CASE
                    WHEN EXISTS (SELECT 1 FROM yazule.login_token WHERE token = %s AND client_ip = %s) THEN 'Found'
                    ELSE 'Not found'
                END AS RowStatus
                """,
                (token, ip)
            )

        (result,) = cursor.fetchone()

        if result == "Not found":
            self.database.conn.commit()
            return True, False, None

        cursor.execute(
            """
            SELECT account_address FROM yazule.login_token WHERE token = %s 
            """,
            (token,)
        )

        (account_address,) = cursor.fetchone()

        self.database.conn.commit()

        return True, True, account_address

    def check_password(self, account_address, password):
        cursor = self.database.get_cursor()

        if not cursor:
            return False, False

        cursor.execute(
            """
            SELECT password_hash FROM yazule.accounts WHERE account_address = %s
            """,
            (account_address,)
        )

        (password_hash,) = cursor.fetchone()

        return True, bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    class FullLoginInstancer(object):
        status: bool = False
        invalid_token: bool = False
        wrong_password: bool = False
        account_locked: bool = False
        token: str = ""
        expired_date: datetime.datetime

    def login(self, login_token, account_password, client_ip, client_name):
        instance = self.FullLoginInstancer()
        cursor = self.database.get_cursor()

        status, result, account_address = self.check_login_token_with_address_result(token=login_token, ip=client_ip)

        if not cursor:
            return instance

        if not status:
            return instance

        if result is False:
            instance.invalid_token = True
            return instance

        if self.account_locked(account_address):
            instance.account_locked = True
            return instance

        result, is_correct = self.check_password(account_address, account_password)

        if not result:
            return instance
        elif not is_correct:
            instance.wrong_password = True
            return instance

        refresh_token = secrets.token_urlsafe(128)
        expired_date = datetime.datetime.now() + datetime.timedelta(minutes=16)

        cursor.execute(
            """
            INSERT INTO yazule.refresh_token (account_address, token, expired_at, client_ip, client_name)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (account_address, refresh_token, expired_date, client_ip, client_name)
        )

        self.database.conn.commit()

        instance.status = True
        instance.token = refresh_token
        instance.expired_date = expired_date

        return instance

    def valid_refresh_token(self, refresh_token):
        cursor = self.database.get_cursor()

        if not cursor:
            return False, False

        cursor.execute(
            """
            SELECT
            CASE
                WHEN EXISTS (SELECT 1 FROM yazule.refresh_token WHERE token = %s) THEN 'Found'
                ELSE 'Not found'
            END AS RowStatus
            """,
            (refresh_token,)
        )

        (result,) = cursor.fetchone()

        if result == "Not found":
            return True, False

        return True, True

    class AccessTokenInstancer(object):
        status: bool = False
        invalid_token: bool = False

    def get_access_token_by_refresh_token(self, account_address, refresh_token, client_ip, client_name):
        instance = self.AccessTokenInstancer()
        cursor = self.database.get_cursor()

        if not cursor:
            return instance

        status, result = self.valid_refresh_token(refresh_token)

        if not status:
            return instance
        elif not result:
            instance.invalid_token = True
            return instance

        access_token = secrets.token_urlsafe(128)
        expired_date = datetime.datetime.now() + datetime.timedelta(days=1)

        cursor.execute(
            """
            INSERT INTO yazule.access_token (account_address, token, expired_at, client_ip, client_name)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (account_address, access_token, expired_date, client_ip, client_name)
        )

        self.database.conn.commit()

        instance.status = True
        instance.token = access_token

        return instance


    def valid_access_token(self, access_token, ip=None):
        cursor = self.database.get_cursor()

        if not cursor:
            return False, False, False

        if ip is None:
            cursor.execute(
                """
                SELECT
                CASE
                    WHEN EXISTS (SELECT 1 FROM yazule.access_token WHERE token = %s) THEN 'Found'
                    ELSE 'Not found'
                END AS RowStatus
                """,
                (access_token,)
            )
        else:
            cursor.execute(
                """
                SELECT
                CASE
                    WHEN EXISTS (SELECT 1 FROM yazule.access WHERE token = %s AND client_ip = %s) THEN 'Found'
                    ELSE 'Not found'
                END AS RowStatus
                """,
                (access_token, ip)
            )

        (result,) = cursor.fetchone()

        self.database.conn.commit()

        if result == "Not found":
            return True, True, False

        return True, True, True


    class YazuleDaemon(threading.Thread):
        def __init__(self, database: DatabaseManager):
            threading.Thread.__init__(self)
            self.daemon = True
            self.database = database

        def run(self):
            print("Yazule daemon running...")
            while True:
                self.cleanup_expired_token()
                time.sleep(1)

        def cleanup_expired_token(self):
            cursor = self.database.get_cursor()

            if not cursor:
                return

            cursor.execute(
                """
                DELETE FROM tokens.tabaccesstoken
                WHERE expired_at < NOW()
                """
            )

            cursor.execute(
                """
                DELETE FROM Yazule.RegisterTempToken
                WHERE expired_at < NOW()
                """
            )

            cursor.execute(
                """
                DELETE FROM Yazule.login_token
                WHERE expired_at < NOW()
                """
            )

            cursor.execute(
                """
                DELETE FROM Yazule.access_token
                WHERE expired_at < NOW()
                """
            )

            cursor.execute(
                """
                DELETE FROM Yazule.refresh_token
                WHERE expired_at < NOW()
                """
            )

            self.database.conn.commit()