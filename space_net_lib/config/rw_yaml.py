import os
import yaml

def yaml_parser(yaml_filepath:str or os.PathLike) -> dict or list:
    """
    :INFO: Read yaml file. (Use method safe_load instead of the unsafe "load" method)
    讀取YAML檔案 (使用safe_load而不是load來避免可能的安全隱患)

    :WARN: You may need call this func within try-except block to avoid unexpected errors.
    警告>你可能會在呼叫此函式時需要將其(呼叫代碼)包裝在try-except(錯誤處理)裡來避免例外情況發生。
    """
    with open(yaml_filepath, 'r') as f:
        data = yaml.safe_load(f)
        f.close()
        return data


def yaml_parser_with_except(yaml_filepath:str or os.PathLike) -> (dict or list, str):
    """
    Same as yaml_parser, but with exception handling.
    No chinese ver because I hate writing comments twice when creating new classes/methods/functions

    Return (dict, None) if there is no error.
    """
    if not os.path.exists(yaml_filepath):
        return {}, "[YAMLParser] File not found."

    try:
        with open(yaml_filepath, 'r') as f:
            try:
                data = yaml.safe_load(f)
                f.close()
                return data, None
            except yaml.YAMLError as error:
                return {}, "[YAMLParser] Unexpected error when parsing yaml file > {}".format(error)
    except Exception as error:
        return {}, "[YAMLParser] Unexpected error when reading yaml file > {}".format(error)


def yaml_writer(target_yaml_filepath:str or os.PathLike, new_yaml_data:dict or list, indent=4) -> None:
    """
    Write new data to yaml file.

    :WARN: You may need call this func within try-except block to avoid unexpected errors.
    警告>你可能會在呼叫此函式時需要將其(呼叫代碼)包裝在try-except(錯誤處理)裡來避免例外情況發生。
    """

    with open(target_yaml_filepath, 'w') as f:
        yaml.dump(new_yaml_data, f, indent=indent)
        f.close()
        return


def yaml_writer_with_except(yaml_filepath:str or os.PathLike, new_yaml_data:dict or list, indent=4) -> None or str:
    """
    Write new data to yaml file, with exception handling.

    Return None if there is no error.
    """

    if not os.path.exists(yaml_filepath):
        os.makedirs(os.path.dirname(yaml_filepath), exist_ok=True)

    try:
        with open(yaml_filepath, 'w') as f:
            try:
                yaml.dump(new_yaml_data, f, indent=indent)
                return None
            except yaml.YAMLError as error:
                return "[YAMLParser] Unexpected error when parsing yaml file > {}".format(error)
    except Exception as error:
        return "[YAMLParser] Unexpected error when reading yaml file > {}".format(error)

