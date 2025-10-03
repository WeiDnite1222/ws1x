from bs4 import BeautifulSoup as bs


def do_theme_replace(current_theme_url, theme_name, theme_icon_map, html):
    if not type(html) is bs:
        soup = bs(html, "html.parser")
    else:
        soup = html

    themes = soup.find_all("link", attrs={"id": "theme"})

    for theme in themes:
        if theme["href"] == current_theme_url:
            del button['disabled']
        else:
            button['disabled'] = ''

    switch_theme_btn = soup.find("input", attrs={"id": "switch_theme_btn"})

    theme_icon_url = theme_icon_map.get(theme_name)

    if switch_theme_btn is not None:
        switch_theme_btn['src'] = theme_icon_url

    return soup