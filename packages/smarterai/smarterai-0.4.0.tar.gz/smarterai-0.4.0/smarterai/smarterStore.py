import json
import os.path
import logging
import collections.abc

logging.root.setLevel(logging.ERROR)
logger = logging.getLogger("__smarterStore__")
logger.setLevel(level=logging.ERROR)


class SmarterStore:
    def __init__(self, store_dir):
        self.__store_dir = store_dir

    @staticmethod
    def _get_filename(pattern: str):
        return pattern.split(".")[0] + ".json"

    @staticmethod
    def _create_dict_from_pattern(pattern: str, value):
        split_str = pattern.split(".")
        keys = split_str[1:-1]
        new_data = {split_str[-1]: value} if len(split_str) > 1 else value
        for key in keys[::-1]:
            new_data = {key: new_data}
        return new_data

    def _read_json(self, filename: str):
        if not os.path.isfile(self.__store_dir + filename):
            return
        with open(self.__store_dir + filename, "r") as jsonFile:
            data = json.load(jsonFile)
        return data

    def _write_json(self, path: str, data):
        with open(self.__store_dir + path, "w") as jsonFile:
            try:
                jsonFile.write(json.dumps(data))
            except Exception as ex:
                logger.error(f"Failed to save data to file, please check data is json serializable. Got Error {ex}")

    def _update(self, original_data, update_data):
        if type(original_data) != dict:
            original_data = {}
        for k, v in update_data.items():
            if isinstance(v, collections.abc.Mapping):
                original_data[k] = self._update(original_data.get(k, {}), v)
            else:
                original_data[k] = v
        return original_data

    def _update_pattern_data(self, pattern_filename: str, new_data):
        if not os.path.isfile(pattern_filename):
            return new_data
        original_data = self._read_json(pattern_filename)
        if type(original_data) != dict:
            return new_data
        self._update(original_data, new_data)
        return original_data

    def _get_data(self, pattern: str):
        pattern_filename = self._get_filename(pattern=pattern)
        data = self._read_json(pattern_filename)
        if not data:
            return None
        keys = pattern.split(".")[1:]
        for key in keys:
            if type(data) != dict or key not in data:
                data = None
                break
            data = data[key]
        return data

    def _set_pattern_data(self, pattern: str, data):
        pattern_filename = self._get_filename(pattern)
        new_data = self._create_dict_from_pattern(pattern=pattern, value=data)
        data = self._update_pattern_data(pattern_filename, new_data) if type(new_data) == dict else new_data
        self._write_json(path=pattern_filename, data=data)

    def _append_pattern_data(self, pattern: str, new_data):
        original_data = self._get_data(pattern=pattern)
        if not original_data:
            original_data = new_data
        else:
            if type(original_data) != list:
                logger.error(f"Error: Can't append {type(new_data)} to a {type(original_data)} json object")
                return
            original_data.append(new_data)
        self._set_pattern_data(pattern=pattern, data=original_data)

    def _prepend_pattern_data(self, pattern: str, new_data):
        original_data = self._get_data(pattern=pattern)
        if not original_data:
            original_data = new_data
        else:
            if type(original_data) != list:
                logger.error(f"Error: Can't append {type(new_data)} to a {type(original_data)} json object")
                return
            original_data.insert(0, new_data)
        self._set_pattern_data(pattern=pattern, data=original_data)

    def get_pattern_data(self, pattern: str):
        try:
            return self._get_data(pattern)
        except Exception as ex:
            logger.error(f"Failed to get pattern data. Error: {ex}")

    def set_pattern_data(self, pattern: str, data):
        try:
            self._set_pattern_data(pattern, data)
        except Exception as ex:
            logger.error(f"Failed to set pattern data. Error: {ex}")

    def append_pattern_data(self, pattern: str, data):
        try:
            self._append_pattern_data(pattern=pattern, new_data=data)
        except Exception as ex:
            logger.error(f"Failed to append pattern data. Error: {ex}")

    def prepend_pattern_data(self, pattern: str, data):
        try:
            self._prepend_pattern_data(pattern=pattern, new_data=data)
        except Exception as ex:
            logger.error(f"Failed to prepend pattern data. Error: {ex}")
