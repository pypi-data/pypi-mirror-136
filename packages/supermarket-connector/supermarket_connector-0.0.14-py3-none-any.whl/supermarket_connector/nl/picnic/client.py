from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import typing
from typing import Any, Optional, Union

import requests
from requests.models import Response
from supermarket_connector import utils
from supermarket_connector.models.category import Category
from supermarket_connector.models.image import Image
from supermarket_connector.models.product import Product
from unidecode import unidecode


def get_items(list_: Optional[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    if list_ is None:
        return []

    temp: list[dict[str, Any]] = []

    for elem in list_:
        if elem.get("type") == "SINGLE_ARTICLE":
            temp.append(elem)

        temp.extend(get_items(elem.get("items")))

    return temp


class Client:
    BASE_URL = "https://storefront-prod.nl.picnicinternational.com/api/"
    DEFAULT_HEADERS = {"User-Agent": "okhttp/3.9.0", "Content-Type": "application/json"}
    AUTH_HEADER_KEY = "x-picnic-auth"
    TEMP_DIR = os.path.join(tempfile.gettempdir(), "Supermarket-Connector", "Debug", "PICNIC")

    access_token: Optional[str] = None

    def __init__(self, username: str, password: str, debug: bool = False, debug_fn: Optional[str] = None, debug_value: bool = True) -> None:
        if not os.path.isdir(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR)

        self.products = self.Products(self)
        self.categories = self.Categories(self)
        # self.images = self.Images(self)
        self.debug = debug
        self.debug_fn = debug_fn
        self.debug_value = debug_value

        self.username = username
        self.password = hashlib.md5(password.encode("utf-8")).hexdigest()

        self.login()

    def request(
        self,
        method: str,
        end_point: str,
        headers: dict[str, Any] = {},
        params: dict[str, Any] = {},
        request_data: dict[str, Any] = {},
        timeout: int = 10,
        authorized: bool = True,
        json_: bool = True,
        debug_key: Optional[str] = None,
    ) -> Union[str, list[Any], dict[Any, Any]]:

        headers.update(self.DEFAULT_HEADERS)

        if authorized:
            if self.access_token is None:
                raise Exception("Need token to make authorized requests")
            headers[self.AUTH_HEADER_KEY] = self.access_token

        while True:
            try:
                response: Response = requests.request(method, f"{self.BASE_URL}{end_point}", params=params, headers=headers, timeout=timeout, data=json.dumps(request_data))
            except Exception:
                continue
            else:
                break

        if not response.ok:
            if response.status_code == 401:
                self.login()

            if not self.access_token is None:
                if self.debug:
                    print(f"Connection error: {response.status_code}")
                return self.request(method, end_point, headers, params, request_data, timeout, authorized, json_, debug_key)

            response.raise_for_status()

        if json_:
            try:
                response_json: Union[list[Any], dict[Any, Any]] = response.json()

                if self.debug:
                    if self.debug_fn is None:
                        print("To debug response also give a filename")
                    elif not self.debug_fn.endswith(".json"):
                        print("Currently only json format is supported")
                    else:
                        debug_path = os.path.join(self.TEMP_DIR, self.debug_fn)
                        debug_path_temp = os.path.join(self.TEMP_DIR, self.debug_fn.replace(".json", "_old.json"))
                        if os.path.isfile(debug_path):
                            with open(debug_path, "r") as f:
                                try:
                                    data: dict[str, Any] = json.load(f)
                                    shutil.copyfile(debug_path, debug_path_temp)
                                except ValueError:
                                    data = {}
                        else:
                            data = {}

                        if not debug_key in data.keys() and not debug_key is None:
                            data[debug_key] = {}

                        if not end_point in data.keys() and debug_key is None:
                            data[end_point] = {}

                        if not debug_key is None:
                            key = debug_key
                        else:
                            key = end_point

                        with open(debug_path, "w") as f:
                            if isinstance(response_json, list):
                                data[key] = utils.process_type(response_json, data[key], self.debug_value)
                                json.dump(data, f)
                            else:
                                data[key] = utils.type_def_dict(response_json, data[key], self.debug_value)
                                json.dump(data, f)

                return response_json
            except ValueError:
                raise ValueError("Response is not in JSON format")
        else:
            return response.text

    def login(self):
        response: Response = requests.request("POST", f"{self.BASE_URL}15/user/login", headers=self.DEFAULT_HEADERS, data=json.dumps({"key": self.username, "secret": self.password, "client_id": 1}))

        if not response.ok:
            raise Exception("Login went wrong")

        self.access_token = response.headers.get(self.AUTH_HEADER_KEY)

        if self.access_token is None:
            raise Exception("No access token found")

    class Categories:
        def __init__(self, client: Client) -> None:
            self.__client = client
            self.data: dict[int, Client.Category] = {}

        def list(self, depth: int = 0):
            response = self.__client.request("GET", "15/my_store", params={"depth": depth})

            if not isinstance(response, dict):
                raise ValueError("Response is not in right format")

            catalog: list[dict[str, Any]] = response.get("catalog", [])

            for elem in catalog:
                id: Optional[str] = elem.get("id")

                if id is None:
                    print("expected ID")
                    continue

                if not id.isnumeric():
                    continue

                if not elem.get("type") == "CATEGORY":
                    continue

                category = self.__client.Category(self.__client, data=elem)

                if not category is None:
                    if not category.id in self.data.keys():
                        self.data[category.id] = category

            return self.data

    class Products:
        def __init__(self, client: Client) -> None:
            self.__client = client
            self.data: dict[int, list[dict[str, Any]]] = {}
            # self.data: dict[int, dict[int, Client.Product]] = {}

        # @typing.overload
        # def list(self) -> dict[int, dict[str, Client.Product]]:
        #     ...

        # @typing.overload
        # def list(self, category: Client.Category) -> dict[str, Client.Product]:
        #     ...

        def list(self, category: Optional[Client.Category] = None):
            if category is None:
                response = self.__client.request("GET", "15/my_store", params={"depth": 99999})
                if not isinstance(response, dict):
                    raise ValueError("Expected dict")

                catalog: list[dict[str, Any]] = response.get("catalog", [])

                for key in self.__client.categories.list().keys():
                    for elem in catalog:
                        if elem.get("id") == str(key):
                            articles: list[dict[str, Any]] = []

                            if elem.get("type") == "SINGLE_ARTICLE":
                                articles.append(elem)
                                self.data[key] = articles
                            else:
                                self.data[key] = get_items(elem.get("items"))

                return self.data
            else:
                pass

    class Category(Category):
        def __init__(
            self,
            client: Client,
            id: Optional[int] = None,
            slug_name: Optional[str] = None,
            name: Optional[str] = None,
            data: Optional[dict[str, Any]] = None,
        ) -> None:
            super().__init__()
            self.__client = client

            if data is None and not id is None:
                self.id = id
                self.slug_name = slug_name
                self.name = name
            elif not data is None:
                self.image_id = data.get("image_id")

                id = data.get("id")
                if id is None:
                    raise ValueError("Expected data to have ID")

                self.id = int(id)
                self.name = data.get("name")
                if not self.name is None:
                    self.slug_name = unidecode(self.name).lower().replace(",", "").replace("&", "").replace("  ", "-").replace(" ", "-")
            else:
                raise ValueError("When initilizing category need to have data or id")

            self.subs: list[Client.Category] = []
