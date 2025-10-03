"""
Put your "process dynamic pages" function in here.
"""
import time
import traceback
import requests
from bs4 import BeautifulSoup as bs
import os, sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

from space_net_lib.config.rw_json import json_parser_with_except, json_writer_with_except
from space_net_lib.definition.path import dynamic_pages_data_path

class PagesUtil:
    def __init__(self, web_root_dir, communicate_cfg, logger):
        self.web_root_dir = web_root_dir
        self.logger = logger

        self.cache = {}
        self.comm_config = communicate_cfg

        self.headers = {
            'User-Agent': 'DynamicPages/1.0',
            "Authorization": f'Bearer {self.comm_config.get("communicate_token", None)}',
        }

    def get_and_save_api_data(self, data_name: str, url: str) -> (bool, dict):
        """
        Get response data from api server and save it to disk.
        :param data_name: Data name(e.g. product_index, themes...)
        :param url: api url
        Return True, dict on success, False, None on failure.
        """
        try:
            r = requests.get(url, headers=self.headers)
            index_data = r.json()
        except Exception as error:
            self.logger.error("Failed to get api data from URL: {}.\n"
                  "ERR: {}", url, error)
            return False, None

        file_path = os.path.join(dynamic_pages_data_path, f"{data_name}.json")

        err = json_writer_with_except(file_path, index_data)

        if err:
            self.logger.error("Unable to save api data.\n"
                              "Source: {}\n"
                              "Exception_At_Path: {}\n"
                              "ERROR: {}".format(url, file_path, err))
            return False, None

        return True, index_data

    def save_api_data(self, data: dict, data_name: str) -> bool:
        """
        Save API json response to disk.
        :param data: Data from api server's response.
        :param data_name: Data name(e.g. product_index, themes...)
        Return True on success, False on failure.
        """

        file_path = os.path.join(dynamic_pages_data_path, "pageUtil",f"{data_name}.json")

        err = json_writer_with_except(file_path, data)

        if err:
            self.logger.error("Unable to save api data.\n"
                              "Source: {}\n"
                              "Exception_At_Path: {}\n"
                              "ERROR: {}".format(url, file_path, err))
            return False

        return True

    def read_api_data(self, data_name: str) -> (bool, dict):
        """
        Read exist api data (from disk)
        :param data_name: Data name(e.g. product_index, themes...)

        Return (True, Dict) on success, False, on failure.
        """
        file_path = os.path.join(dynamic_pages_data_path, "pageUtil",f"{data_name}.json")

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return False, None

        data, err = json_parser_with_except(file_path)

        if err:
            self.logger.error("An error occurred while reading exist data.\n"
                              "Exception_At_Path: {}\n"
                              "ERROR: {}".format(url, err))
            return False, None

        return True, data

    def update_latest_post_list(self, home_html):
        """
        The home.html must be encoded as utf-8!
        """
        # Soup

        if not type(home_html) is bs:
            soup = bs(home_html, "lxml")
        else:
            soup = home_html

        # try:
        #     # 文章索引
        #     api_articles_index = requests.get("https://api.weispace.net/sites/articles",
        #                                       headers=self.headers)
        #     index_data = api_articles_index.json()
        # except Exception as error:
        #     print("ERROR: Failed to get articles index from api server.", error)
        #     return False, home_html

        result, data = self.get_and_save_api_data("articles_index", "https://api.weispace.net/sites/articles")

        if not result:
            self.logger.warning("Failed to get api data from server. Try using "
                                "exist data from disk as failback...\n")

            result, data = self.read_api_data(data)

            if not result:
                self.logger.warning("Unable to update latest post list while getting articles index. Process stopped.")
                return False, home_html

        try:
            articles_list = data["ResponseData"]["articlesIndexData"]["dataList"]
        except Exception as _:
            self.logger.error("Unsupported format of articles index.")
            return False, home_html

        # Delete old post
        articles_list = articles_list[:-3] if len(articles_list) >= 8 else articles_list

        # Find blog_card_list
        blog_card_list = soup.find('div', id="spacenet_latest_post_list")

        if blog_card_list is None:
            self.logger.error("No card list found.")
            return False, home_html

        for data in articles_list:
            try:
                title = data["title"]
                description = data["description"]
                preview_img = data["previewImage"]
                link = data["link"]
            except Exception as error:
                self.logger.error("Unable to get value from article index. If the article index format has changed,"
                      " please update the keywords of the function.", error)
                return False, home_html

            # css
            styles = data.get("styles", {})
            title_color = styles.get("titleColor", None)
            description_color = styles.get("descriptionColor", None)

            blog_card = soup.new_tag("div", attrs={"class": "spacenet_blog_post_card"})
            post_card_wrapper = soup.new_tag("div", attrs={"class": "post_card_wrapper"})
            post_card_direct = soup.new_tag("div", attrs={"class": "post_card_direct",
                                                          "href": link})
            img = soup.new_tag("img", attrs={"src": preview_img})
            img_overlay = soup.new_tag("div")
            post_card_short_description = soup.new_tag("p", attrs={"class": "post_card_short_description"})
            post_preview_title = soup.new_tag("a", attrs={"class": "post_preview_title"})

            # Replace element text to description/title
            post_card_short_description.string = description
            post_preview_title.string = title

            # Apply custom styles
            if title_color is not None:
                post_preview_title.attrs.update({"style": f"color: {title_color}"})

            if description_color is not None:
                post_card_short_description.attrs.update({"style": f"color: {description_color}"})

            # Append subitem to blog_card
            post_card_wrapper.append(img)
            post_card_wrapper.append(img_overlay)
            post_card_wrapper.append(post_card_short_description)
            post_card_wrapper.append(post_preview_title)

            blog_card.append(post_card_wrapper)
            blog_card.append(post_card_direct)
            blog_card_list.append(blog_card)

        return True, soup

    def update_blog_list(self, home_html):
        """
        The home.html must be encoded as utf-8!
        """
        # Soup
        if not type(home_html) is bs:
            soup = bs(home_html, "lxml")
        else:
            soup = home_html

        result, data = self.get_and_save_api_data("articles_index", "https://api.weispace.net/sites/articles")

        if not result:
            self.logger.warning("Failed to get api data from server. Try using "
                                "exist data from disk as failback...\n")

            result, data = self.read_api_data(data)

            if not result:
                self.logger.warning("Unable to update blog list while getting articles index. Process stopped.")
                return False, home_html

        try:
            articles_list = data["ResponseData"]["articlesIndexData"]["dataList"]
        except Exception as _:
            print("ERROR: Unsupported format of articles index.")
            return False, home_html

        # Delete old post
        articles_list = articles_list[:-3] if len(articles_list) >= 8 else articles_list

        # Find blog_card_list
        blog_card_list = soup.find('div', id="blog_card_list")

        if blog_card_list is None:
            print("ERROR: No card list found.")
            return False, home_html

        for data in articles_list:
            try:
                title = data["title"]
                description = data["description"]
                preview_img = data["previewImage"]
                link = data["link"]
                add_date = data["addDate"]
            except Exception as error:
                print("ERROR: Unable to get value from article index. If the article index format has changed,"
                      " please update the keywords of the function.", error)
                return False, home_html

            # css
            styles = data.get("styles", {})
            title_color = styles.get("titleColor", None)
            description_color = styles.get("descriptionColor", None)

            blog_card = soup.new_tag("div", attrs={"class": "blog_card"})
            blog_card_date_container = soup.new_tag("div", attrs={"class": "blog_card_date_container"})
            date = soup.new_tag("h3")
            line = soup.new_tag("hr", attrs={"class": "line_between_date_and_card"})
            blog_card_wrapper = soup.new_tag("div", attrs={"class": "blog_card_wrapper"})
            post_card_direct = soup.new_tag("div", attrs={"class": "post_card_direct",
                                                          "href": link})
            img = soup.new_tag("img", attrs={"src": preview_img})
            img_overlay = soup.new_tag("div")
            blog_card_short_description = soup.new_tag("p")
            blog_card_title = soup.new_tag("a", attrs={"class": "blog_card_title"})

            # Replace element text to description/title
            blog_card_short_description.string = description
            blog_card_title.string = title
            date.string = add_date

            # Apply custom styles
            if title_color is not None:
                blog_card_title.attrs.update({"style": f"color: {title_color}"})

            if description_color is not None:
                blog_card_short_description.attrs.update({"style": f"color: {description_color}"})

            # Append subitem to blog_card
            blog_card_date_container.append(date)
            blog_card_date_container.append(line)
            blog_card_wrapper.append(img)
            blog_card_wrapper.append(img_overlay)
            # blog_card_wrapper.append(post_card_short_description)
            blog_card_wrapper.append(blog_card_title)

            blog_card.append(blog_card_date_container)
            blog_card.append(blog_card_wrapper)
            blog_card.append(post_card_direct)

            # Append blog card to list
            blog_card_list.append(blog_card)

        return True, soup

    def update_server_message(self, html):
        # Soup
        if not type(html) is bs:
            soup = bs(html, "lxml")
        else:
            soup = html

        # try:
        #     # 文章索引
        #     api_message_data = requests.get("https://api.weispace.net/sites/server/message",
        #                                     headers=self.headers)
        #     message_data = api_message_data.json()
        # except Exception as error:
        #     print("ERROR: Failed to get articles index from api server.", error)
        #     return False, html

        result, data = self.get_and_save_api_data("server_message_history", "https://api.weispace.net/sites/server/message")

        if not result:
            self.logger.warning("Failed to get api data from server. Try using "
                                "exist data from disk as failback...\n")

            result, data = self.read_api_data(data)

            if not result:
                self.logger.warning("Unable to update latest server message list while getting message history. Process stopped.")
                return False, home_html

        try:
            message_list = data["ResponseData"]["messageData"]["messageList"]
        except Exception as _:
            print("ERROR: Unsupported format of articles index.")
            return False, html

        server_news_list = soup.find('div', id="server_news_list")

        if server_news_list is None:
            print("ERROR: No server_news_list found.")
            return False, html

        for data in message_list:
            try:
                message_content = data["content"]
                message_date = data["date"]
            except Exception as error:
                print("ERROR: Unable to get value from message data. If the message format has changed,"
                      " please update the keywords of the function.", error)
                return False, html

            message = soup.new_tag("div", attrs={"class": "spacenet_server_news_item"})
            content = soup.new_tag("p")
            date = soup.new_tag("a", attrs={"class": "post_time"})

            content.string = message_content
            date.string = message_date

            message.append(content)
            message.append(date)

            server_news_list.append(message)

        return True, soup

    def insert_content_to_homepage(self, html):
        usm_result, html = self.update_server_message(html)
        result, html = self.update_latest_post_list(html)

        if result and usm_result:
            return True, html

        return False, html

    def get_cookie_value(self, name, request):
        cookie = request.headers.get("Cookie")

        if cookie is None:
            return None

        cookies = cookie.split(";")

        value = None

        for cookie in cookies:
            cookie = cookie.strip()
            try:
                cookie_name, cookie_value = cookie.split("=")
            except ValueError:
                continue

            if cookie_name.lower() == name:
                value = cookie_value
                break

        return value


    def replace_theme(self, html, request):
        theme_name = self.get_cookie_value("theme_name", request)

        if theme_name is None:
            return html

        theme_json_path = os.path.join(self.web_root_dir, "themes", "themes.json")

        if not os.path.exists(theme_json_path):
            self.logger.warning("Themes file doesn't exist.")
            return html

        theme_data = self.cache.get("<ThemeData>", None)

        if theme_data is None:
            data, error = json_parser_with_except(theme_json_path)

            if error is not None:
                self.logger.error("Unable to parse the themes file. Error: {}".format(error))
                return html

            self.cache["<ThemeData>"] = data
            theme_data = data

        theme_image_url = theme_data.get(theme_name, {}).get("image_filepath", None)
        theme_css_url = theme_data.get(theme_name, {}).get("sourceList", None)

        if theme_image_url is None:
            self.logger.warning("Theme name {} image is missing.".format(theme_name))
        elif theme_css_url is None:
            self.logger.error("Theme name {} css file does not exist.".format(theme_name))
            return html

        if not type(html) is bs:
            soup = bs(html, "lxml")
        else:
            soup = html

        body = soup.find("body")

        if body is None:
            return html
        else:
            head = soup.find("head")

        if head is None:
            return html

        current_theme_name = soup.find("meta", id="current_theme_meta")

        if not current_theme_name is None:
            current_theme_name.attrs.update({"content" : theme_name})

        old_themes = soup.find_all("link", id='theme')

        for theme in old_themes:
            theme.decompose()

        for url in theme_css_url:
            theme_link = soup.new_tag("link", attrs={"rel": "stylesheet", "href": url, "id": "theme"})
            head.append(theme_link)

        body = soup.find("body")

        if body is None:
            return html

        nav = soup.find("nav")

        if nav is not None:
            switch_theme_icon = nav.find("img", attrs={"id": "theme_icon"})

            if switch_theme_icon is not None:
                switch_theme_icon.attrs.update({"src": theme_image_url})

        return soup


    def apply_toplevel_style(self, html, request):
        toplevel_current_style = self.get_cookie_value("toplevel_style", request)

        if toplevel_current_style is None:
            return html

        if type(html) is bs:
            soup = html
        else:
            soup = bs(html, "lxml")

        toplevel_container = soup.find("nav", id="toplevelcontainer")

        if toplevel_container is None:
            return html

        if toplevel_current_style == "wrapped":
            toplevel_container["class"].append("wrapped_mode")

        return soup


    @staticmethod
    def insert_account_address_to_login_page(html, account_address):
        if type(html) is bs:
            soup = html
        else:
            soup = bs(html, "lxml")

        current_account_address = soup.find("a", id="current_account_address")

        if current_account_address is None:
            return html

        current_account_address.string = f"{current_account_address.string} {account_address}"

        return soup










