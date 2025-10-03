

class LivePath(object):
    def __init__(self, keywords):
        self.keywords = keywords

    def convert_path_keyword_to_read_value(self, string_with_keyword):
        for key, value in self.keyword.items():
            if key in string_with_keyword:
                string_with_keyword = string_with_keyword.replace(key, value)

        return string_with_keyword