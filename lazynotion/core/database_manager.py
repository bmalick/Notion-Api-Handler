import requests
from typing import Union, List, Dict, Any
from .api import NotionObject, NotionApi

# TODO: add print to each method

class DatabaseManager:
    def __init__(self, api, parent_id: str=None, database_id: str=None):
        self.parent_id = parent_id
        self.database_id = database_id
        self.api = api

    # TODO: to adapt
    def create_database(self, db_title: str, properties: list[dict], icon: str = None, cover: str = None):
        init_properties = self.api.objects["init_properties"]
        # properties = {
        #     item["name"]: init_properties[item["type"]]
        #     for item in properties
        # }
        properties = {
            prop_name: init_properties[prop_type] for prop_name, prop_type in properties.items()
        }
        response = requests.post(
            url=self._DATABASE_ENDPOINT,
            headers=self.headers,
            json={
                "parent": NotionObject("database_parent")({"id": self.parent_id}),
                "icon": NotionObject("icon")({"url": icon} if icon is not None else None),
                "cover": NotionObject("icon")({"url": cover} if cover is not None else None),
                **NotionObject("page_title")({"title": db_title}),
                "properties": {"Name": {"title": {}}, **properties}
            }
        )
        try:
            response.raise_for_status()
            url = response.json()["url"]
            # print("Database creation")
            # print("%s: %s" % ("Name".rjust(10), db_title))
            # print("%s: %s" % ("URL".rjust(10), url))
        except:
            # print("FAIL\n\n")
            print(response.text)

    # TODO: to adapt
    def add_page(self, data: dict):
        response = requests.post(
            url=self.api._PAGES_ENDPOINT,
            headers=self.api.headers,
            json={
                "parent": NotionObject("database_parent")({"id": self.database_id}),
                "icon": NotionObject("icon")(data.get("icon")),
                "cover": NotionObject("icon")(data.get("cover")),
                "properties": {
                    item["name"]: NotionObject(item["type"])(item["values"])
                    for item in data["properties"]
                },
                "children": [
                    NotionObject(item["type"])(values=item["values"], children=item.get("children"))
                    for item in data.get("children", [])
                ]
            }
        )
        try:
            response.raise_for_status()
            url = response.json()["url"]
            # print("Page creation into database")
            # print("%s: %s" % ("URL".rjust(10), url))
            return response.json()
        except:
            print(response.text)

    def query(self, limit: int = 10, filters: dict = {"or": []}, sorts=[]) -> List[dict]:
        if isinstance(filters, str):
            if len(filters)==0: filters = {"or": []}
            else:
                command = filters.strip().split(";")
                filters_args = []
                for c in command[1:]:
                    c = list(map(lambda x: x.strip(), c.split(',')))
                    filters_args.append({"property": c[0], c[1]: {c[2]: c[3]}})
                filters = {
                    command[0].strip(): filters_args
                }
        if isinstance(sorts, str):
            if len(sorts)==0: sorts = []
            else:
                command = sorts.strip().split(";")
                sorts = []
                for c in command[1:]:
                    c = list(map(lambda x: x.strip(), c.split(',')))
                    sorts.append({"property": c[0], "direction": c[1]})

        response = requests.post(
            url=self.api._QUERY_ENDPOINT % self.database_id,
            headers=self.api.headers,
            json={
                "page_size": limit,
                "filter": filters,
                "sorts": sorts
            }
        )
        try:
            response.raise_for_status()
            return response.json()["results"]
        except:
            print(response.text)

    def extend_rich_text(self, text):
        return {f"text{i+1}": text[i*2000:(i+1)*2000] for i in range(len(text)//2000+1)}
    
    def find_id_from_name(self, name):
        result = self.query(
            limit=100,
            filters={"property": "Nom", "rich_text": {"contains": name}},
            # filters={"property": "Name", "rich_text": {"contains": name}}
        )
        return result[0]["id"]
