#
#    Copyright 2022 - Carlos A. <https://github.com/dealfonso>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
import os
import time
import json

class CacheData:
    # Validity of cache data (in seconds)
    _validity: float = 60 * 5

    def __init__(self) -> None:
        self._entries = {}

    @property
    def keys(self) -> list:
        """Returns the keys of the cache entries

        Returns:
            list: list of keys in the cache
        """
        return list(self._entries.keys())

    @property
    def validity(self) -> float:
        """Retrieves the validity of the items in the cache

        * if validity is negative, the items are never expired

        Returns:
            float: validity of the cache entries, in seconds
        """
        return self._validity

    @validity.setter
    def validity(self, validity: float) -> None:
        """Sets the global validity for the entries in the cache

        * if validity is negative, the items are never expired

        Args:
            validity (float): validity of the cache entries, in seconds
        """
        self._validity = validity

    def clear(self) -> None:
        """Clears the cache
        """
        self._entries = {}

    def add(self, key, data) -> bool:
        """Adds an entry to the cache

        Args:
            key (Any): the key of the entry in the cache
            data (Any): the data to be stored in the cache

        Returns:
            bool: True if the entry was added, False otherwise
        """
        self._entries[key] = {
            "data": data,
            "t": time.time()
        }
        return True

    def get(self, key, validity: float = None) -> dict:
        """Retrieves an entry from the cache, if it exists and is still valid

        Args:
            key (Any): the key of the entry in the cache
            validity (float): the validity of the entry in seconds, if None, the default validity is used

        Returns:
            dict: _description_
        """

        if key in self._entries:
            entry = self._entries[key]
            if validity is None:
                validity = self.validity
            if (validity < 0) or (time.time() - entry["t"] < validity):
                return entry["data"]
        return None

class CacheFile(CacheData):
    """Class to manage cache information using a file backend. It simply stores the entries of the cache in a file, and updates
       the file whenever a new entry is added
    """
    def __init__(self, filename: str) -> None:
        """Builds the object

        Args:
            filename (str): _description_
        """
        super().__init__()
        self.filename = filename
        self._entries = self.__load()

    def __load(self) -> dict:
        """Loads the entries from the file and sets them to the in-memory cache

        Returns:
            dict: the content of the cache file
        """
        if not os.path.exists(self.filename):
            return {}
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except:
            return {}

    def __save(self) -> bool:
        """Saves the entries to the cache file

        Returns:
            bool: True if the file has been written; False otherwise
        """
        try:
            with open(self.filename, "w") as f:
                json.dump(self._entries, f)
            return True
        except:
            return False

    def clear(self) -> None:
        """Clears the cache (and updates the file)
        """
        super().clear()
        self.__save()

    @staticmethod
    def create(filename: str, create_folder: bool = True) -> 'CacheData':
        """Creates a CacheData object, and creates the file if it does not exist. If the folder does not exist, this function will fail. To prevent such failure,
           the folder could automatically be created, to be able to store the file.

        Args:
            filename (str): The path of the file to be used to store the cache (accepts ~, $HOME, etc.)
            create_folder (bool, optional): Whether to create or not the folder in which the cache file is to be stored, if it does not exist. Defaults to True.

        Returns:
            CacheData: An object of type CacheData, if the file exists or could be created. None otherwise.
        """
        filename = os.path.expanduser(filename)
        folder = os.path.dirname(filename)
        try:
            if not os.path.exists(folder) and create_folder:
                os.makedirs(folder)
            if not os.path.exists(filename):
                with open(filename, "w") as f:
                    f.write(json.dumps({}))
            return CacheFile(filename)
        except:
            return None
    
    def add(self, key, data) -> bool:
        """Adds an entry to the cache, and updates the file that backs the cache

        Args:
            key (Any): the key of the entry in the cache
            data (Any): the data to be stored in the cache

        Returns:
            bool: True if the entry was added, False otherwise
        """
        super().add(key, data)
        self.__save()
        return True