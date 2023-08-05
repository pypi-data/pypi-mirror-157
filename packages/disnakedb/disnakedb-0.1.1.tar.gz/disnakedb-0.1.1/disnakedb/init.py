import json
from typing import Any, Union


class Init:
    def __init__(self):
        """
        Create database
        """
        try:
            with open("db.json", "r") as _:
                pass
        except FileNotFoundError:
            with open("db.json", "w", encoding="utf-8") as writer:
                json.dump({}, writer, indent=4)
        self.cache = {}

    def get(self, name: str) -> Union[dict, str, int, float, None]:
        """
        Get data
        :param name: name of variable
        :return: Any
        """
        try:
            return self.cache[name]
        except KeyError:
            pass

        with open("db.json", "r", encoding="utf-8") as reader:
            doc = json.loads(reader.read())
        try:
            return doc[name]
        except KeyError:
            return None

    def set(self, name: str, value: Any) -> None:
        """
        Set data
        :param name: name of variable
        :param value: value for variable
        :return: None
        """
        self.cache[name] = value
        with open("db.json", "r", encoding="utf-8") as reader:
            doc = json.loads(reader.read())

        doc[name] = value

        with open("db.json", "w", encoding="utf-8") as writer:
            json.dump(doc, writer, indent=4)

    def remove(self, name: str) -> None:
        """
        Remove data
        :param name: name of variable
        :return: None
        """
        try:
            del self.cache[name]
        except KeyError:
            pass

        with open("db.json", "r", encoding="utf-8") as reader:
            doc = json.loads(reader.read())

        del doc[name]

        with open("db.json", "w", encoding="utf-8") as writer:
            json.dump(doc, writer, indent=4)

    def sync(self) -> None:
        """
        Sync cache
        :return: None
        """
        with open("db.json", "r", encoding="utf-8") as reader:
            doc: dict = json.loads(reader.read())
        for key in doc.keys():
            self.cache[key] = doc[key]

    def clear(self) -> None:
        """
        Clear cache
        :return: None
        """
        for key in self.cache.keys():
            del self.cache[key]
