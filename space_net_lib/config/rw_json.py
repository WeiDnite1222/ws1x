import os
import json

def json_parser(json_filepath:str or os.PathLike) -> dict or list:
    """
    :INFO: Read json file. (Use method safe_load instead of the unsafe "load" method)
    讀取json檔案 (使用safe_load而不是load來避免可能的安全隱患)

    :WARN: You may need call this func within try-except block to avoid unexpected errors.
    警告>你可能會在呼叫此函式時需要將其(呼叫代碼)包裝在try-except(錯誤處理)裡來避免例外情況發生。
    """
    with open(json_filepath) as f:
        data = json.load(f)
        f.close()
        return data


def json_parser_with_except(json_filepath:str or os.PathLike) -> (dict or list, str):
    """
    Same as json_parser, but with exception handling.
    No chinese ver because I hate writing comments twice when creating new classes/methods/functions

    Return (dict, None) if there is no error.
    """
    if not os.path.exists(json_filepath):
        return {}, "[jsonParser] File not found."

    try:
        with open(json_filepath) as f:
            try:
                data = json.load(f)
                f.close()
                return data, None
            except json.JSONDecodeError as error:
                return {}, "[jsonParser] Unexpected error when parsing json file > {}".format(error)
    except Exception as error:
        return {}, "[jsonParser] Unexpected error when reading json file > {}".format(error)


def json_writer(target_json_filepath:str or os.PathLike, new_json_data:dict or list, indent=4) -> None:
    """
    Write new data to json file.

    :WARN: You may need call this func within try-except block to avoid unexpected errors.
    警告>你可能會在呼叫此函式時需要將其(呼叫代碼)包裝在try-except(錯誤處理)裡來避免例外情況發生。
    """

    with open(target_json_filepath, 'w') as f:
        json.dump(new_json_data, f, indent=indent)
        f.close()
        return


def json_writer_with_except(json_filepath:str or os.PathLike, new_json_data:dict or list, indent=4) -> None or str:
    """
    Write new data to json file, with exception handling.

    Return None if there is no error.
    """

    if not os.path.exists(json_filepath):
        os.makedirs(os.path.dirname(json_filepath), exist_ok=True)

    try:
        with open(json_filepath, "w") as f:
            try:
                json.dump(new_json_data, f, indent=indent)
                return None
            except json.JSONDecodeError as error:
                return "[jsonParser] Unexpected error when parsing json file > {}".format(error)
    except Exception as error:
        return "[jsonParser] Unexpected error when reading json file > {}".format(error)

