import os

if os.name == "nt":
    main_data_dir = os.path.join(os.getenv('APPDATA'), "SpaceNET-Data")

    api_data_path = os.path.join(main_data_dir, "API")
    dynamic_pages_data_path = os.path.join(main_data_dir, "DynamicPages")
    manage_data_path = os.path.join(main_data_dir, "Manage")

    keyword_dict = {
        "${SPACENET_API_DATA_PATH}": api_data_path,
        "${SPACENET_DP_DATA_PATH}": dynamic_pages_data_path,
        "${SPACENET_MANAGE_DATA_PATH}": manage_data_path,
        "${SPACENET_API_CONFIG_PATH}": api_data_path,
        "${SPACENET_DP_CONFIG_PATH}": dynamic_pages_data_path,
        "${SPACENET_MANAGE_CONFIG_PATH}": manage_data_path
    }
elif os.name == "posix":
    main_data_dir = os.path.join("/", "var", "SpaceNET")
    main_config_dir = os.path.join("/", "etc", "SpaceNET")

    api_data_path = os.path.join(main_data_dir, "API")
    dynamic_pages_data_path = os.path.join(main_data_dir, "DynamicPages")
    manage_data_path = os.path.join(main_data_dir, "Manage")

    api_config_path = os.path.join(main_config_dir, "API")
    dynamic_pages_config_path = os.path.join(main_config_dir, "DynamicPages")
    manage_config_path = os.path.join(main_config_dir, "Manage")

    keyword_dict = {
        "${SPACENET_API_DATA_PATH}": api_data_path,
        "${SPACENET_DP_DATA_PATH}": dynamic_pages_data_path,
        "${SPACENET_MANAGE_DATA_PATH}": manage_data_path,
        "${SPACENET_API_CONFIG_PATH}": api_config_path,
        "${SPACENET_DP_CONFIG_PATH}": dynamic_pages_config_path,
        "${SPACENET_MANAGE_CONFIG_PATH}": manage_config_path,
    }


def convert_path_keyword_to_read_value(string_with_keyword):
    for key, value in keyword_dict.items():
        if key in string_with_keyword:
            string_with_keyword = string_with_keyword.replace(key, value)


    return string_with_keyword