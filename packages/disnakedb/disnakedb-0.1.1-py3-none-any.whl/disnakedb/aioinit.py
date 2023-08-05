import json
from typing import Any, Union
import aiofiles


class Aioinit:
    def __init__(self):
        """
        Create database
        """
        try:
            with open("db.json", "r") as _:
                pass
        except FileNotFoundError:
            with open("db.json", "w", encoding="utf-8") as writer:
                writer.write(json.dumps({}, indent=4))
        self.cache = {}

    async def get(self, name: str) -> Union[dict, str, int, float, None]:
        """
        Get data
        :param name: name of variable
        :return: Any
        """
        try:
            return self.cache[name]
        except KeyError:
            pass

        async with aiofiles.open("db.json", "r", encoding="utf-8") as reader:
            doc = json.loads(await reader.read())
        try:
            return doc[name]
        except KeyError:
            return None

    async def set(self, name: str, value: Any) -> None:
        """
        Set data
        :param name: name of variable
        :param value: value for variable
        :return: None
        """
        self.cache[name] = value
        async with aiofiles.open("db.json", "r", encoding="utf-8") as reader:
            doc = json.loads(await reader.read())

        doc[name] = value

        async with aiofiles.open("db.json", "w", encoding="utf-8") as writer:
            await writer.write(json.dumps(doc, indent=4))

    async def remove(self, name: str) -> None:
        """
        Remove data
        :param name: name of variable
        :return: None
        """
        try:
            del self.cache[name]
        except KeyError:
            pass

        async with aiofiles.open("db.json", "r", encoding="utf-8") as reader:
            doc = json.loads(await reader.read())

        del doc[name]

        async with aiofiles.open("db.json", "w", encoding="utf-8") as writer:
            await writer.write(json.dumps(doc, indent=4))

    async def sync(self) -> None:
        """
        Sync cache
        :return: None
        """
        async with aiofiles.open("db.json", "r", encoding="utf-8") as reader:
            doc: dict = json.loads(await reader.read())
        for key in doc.keys():
            self.cache[key] = doc[key]

    async def clear(self) -> None:
        """
        Clear cache
        :return: None
        """
        for key in self.cache.keys():
            del self.cache[key]
