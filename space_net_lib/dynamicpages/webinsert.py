import time
import traceback
import requests
from bs4 import BeautifulSoup as bs

class WebInsertUtil:
    def __init__(self):
        pass

    def update_latest_post_list(self, home_html):
        """
        The home.html must be encoded as utf-8!
        """
        # Soup
        soup = bs(home_html, "html.parser")

        try:
            api_articles_index = requests.get("https://api.weispace.net/sites/articles")
            index_data = api_articles_index.json()
        except Exception as error:
            print("ERROR: Failed to get articles index from api server.", error)
            return home_html

        try:
            articles_list = index_data["responseInfo"]["articlesIndexData"]["dataList"]
        except Exception as _:
            print("ERROR: Unsupported format of articles index.")
            return home_html

        # Delete old post
        articles_list = articles_list[:-3] if len(articles_list) >= 8 else articles_list

        # Find blog_card_list
        blog_card_list = soup.find('div', id="spacenet_latest_post_list")

        if blog_card_list is None:
            print("ERROR: No card list found.")
            return home_html

        for data in articles_list:
            try:
                title = data["title"]
                description = data["description"]
                preview_img = data["previewImage"]
                link = data["link"]
            except Exception as error:
                print("ERROR: Unable to get value from article index. If the article index format has changed,"
                      " please update the keywords of the function.", error)
                return home_html

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
                post_preview_title["color"] = title_color

            if description_color is not None:
                post_card_short_description["color"] = description_color

            # Append subitem to blog_card
            post_card_wrapper.append(img)
            post_card_wrapper.append(img_overlay)
            post_card_wrapper.append(post_card_short_description)
            post_card_wrapper.append(post_preview_title)

            blog_card.append(post_card_wrapper)
            blog_card.append(post_card_direct)
            blog_card_list.append(blog_card)

        return soup

    def update_blog_list(self, home_html):
        """
        The home.html must be encoded as utf-8!
        """
        # Soup
        soup = bs(home_html, "html.parser")

        try:
            # 文章索引
            api_articles_index = requests.get("https://api.weispace.net/sites/articles")
            index_data = api_articles_index.json()
        except Exception as error:
            print("ERROR: Failed to get articles index from api server.", error)
            return home_html

        try:
            articles_list = index_data["responseInfo"]["articlesIndexData"]["dataList"]
        except Exception as _:
            print("ERROR: Unsupported format of articles index.")
            return home_html

        # Delete old post
        articles_list = articles_list[:-3] if len(articles_list) >= 8 else articles_list

        # Find blog_card_list
        blog_card_list = soup.find('div', id="blog_card_list")

        if blog_card_list is None:
            print("ERROR: No card list found.")
            return home_html

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
                return home_html

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
                blog_card_title["color"] = title_color

            if description_color is not None:
                blog_card_short_description["color"] = description_color

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

        return soup


    def update_server_message(self, html):
        # Soup
        if not type(html) is bs:
            soup = bs(html, "html.parser")
        else:
            soup = html

        try:
            # 文章索引
            api_message_data = requests.get("https://api.weispace.net/sites/server/message")
            message_data = api_message_data.json()
        except Exception as error:
            print("ERROR: Failed to get articles index from api server.", error)
            return html

        try:
            message_list = message_data["responseInfo"]["messageData"]["messageList"]
        except Exception as _:
            print("ERROR: Unsupported format of articles index.")
            return html

        server_news_list = soup.find('div', id="server_news_list")

        if server_news_list is None:
            print("ERROR: No server_news_list found.")
            return html

        for data in message_list:
            try:
                message_content = data["content"]
                message_date = data["date"]
            except Exception as error:
                print("ERROR: Unable to get value from message data. If the message format has changed,"
                      " please update the keywords of the function.", error)
                return html

            message = soup.new_tag("div", attrs={"class": "spacenet_server_news_item"})
            content = soup.new_tag("p")
            date = soup.new_tag("a", attrs={"class": "post_time"})

            content.string = message_content
            date.string = message_date

            message.append(content)
            message.append(date)

            server_news_list.append(message)

        return soup