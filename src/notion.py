import yaml
import requests
import logging
import logging.config
from typing import Union, List, Dict, Any


def read_yaml(filename: str) -> Dict:
    """Read and parse a YAML file."""
    with open(filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_yaml(filename: str, data: dict) -> None:
    """Save data to a YAML file."""
    with open(filename, 'w') as f:
        yaml.safe_dump(data, f)


class Parameters:
    def save_parameters(self, ignore: list[str] = None, **kwargs):
        ignore = ignore or []
        for k, v in kwargs.items():
            if k not in ignore: setattr(self, k, v)


def update_dict_from_path(dictionary: Dict, path: str, value: Union[str, List]) -> Dict:
    """
    Nested dictionary update using dot-notation path.
    
    Args:
        dictionary: The dictionary to update
        path: Dot-separated path to the key
        value: Value to set at the specified path
    
    Returns:
        Updated dictionary
    """
    keys = path.split('.')
    current = dictionary
    for key in keys[:-1]:
        # Handle list indexing
        if '[' in key:
            key_split = key.split('[')
            key = key_split[0]
            idx = int(key_split[1][:-1])
            try:
                current = current[key][idx]
            except:
                current = current[key]
                current.append({})
                current = current[-1]
        else:
            if key not in current:
                current[key] = {}
            current = current[key]
    current[keys[-1]] = value
    return dictionary

class NotionObject:
    """Helper class for creating Notion-compatible objects."""
    _OBJECTS_FILE = "objects.yaml"
    def __init__(self, name: str):
        self.name = name
        self._objects = read_yaml(self._OBJECTS_FILE)
    
    def __call__(self, values: Dict, children: List[Dict] = None) -> Dict:
        if values is None: return None
        template = self._objects[self.name].copy()
        item = template["object"].copy()
        paths = template["paths"]

        # Handle children recursively
        if children is not None:
            values["children"] = [
                NotionObject(item["type"])(child["values"])
                for child in children]

        # Update object with provided values
        for name, val in values.items():
            # Dynamically extend paths if configured
            if template.get("extend_paths", False):
                try:
                    idx = int(name[-1])
                    val_extend = paths[name[:-1]].replace('0', str(idx))
                    paths[name] = val_extend
                except: pass

            item = update_dict_from_path(item, paths[name], val).copy()

        return item


class NotionApiHandler(Parameters):
    """Comprehensive handler for Notion API interactions."""
    _KEYS_FILE = "keys.yaml"
    _OBJECTS_FILE = "objects.yaml"

    # Notion API endpoints
    _PAGES_ENDPOINT = "https://api.notion.com/v1/pages"
    _DATABASE_ENDPOINT = "https://api.notion.com/v1/databases"
    _QUERY_ENDPOINT = "https://api.notion.com/v1/databases/%s/query"
    _max_chars = 1999
    _BLOCKS_ENDPOINT = "https://api.notion.com/v1/blocks/%s/children"

    def __init__(self) -> None:
        self.keys = read_yaml(self._KEYS_FILE)
        self.objects = read_yaml(self._OBJECTS_FILE)
        self.headers = self._create_headers()
    
    def _create_headers(self) -> Dict[str, str]:
        """Create authentication headers for Notion API."""
        return {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "Authorization": "Bearer %s" % self.keys.get("api_token")
        }
    
    @staticmethod
    def get_logger(name: str):
        """Configure and return a logger."""
        log_config_dict = read_yaml("log-config.yaml")
        logging.config.dictConfig(log_config_dict)
        return logging.getLogger(name)

    @staticmethod
    def extend_rich_text(text):
        return {f"text{i+1}": text[i*2000:(i+1)*2000] for i in range(len(text)//2000+1)}


    def fill_object(self, property_object: str, property_values: List[Any]) -> Dict:
        assert isinstance(property_values, list), "Enter a list please."
        args = self.objects[property_object].copy()
        item = args["object"].copy()
        for path, value in zip(args["paths"], property_values):
            item = update_dict_from_path(item, path, value).copy()
        return item

    def create_page(self, parent_id: str, page_title: str, icon: str = None, cover: str = None):
        response = requests.post(
            url=self._PAGES_ENDPOINT,
            headers=self.headers,
            json={
                "parent": NotionObject("page_parent")({"id": parent_id}),
                "icon": NotionObject("icon")({"url": icon} if icon is not None else None),
                "cover": NotionObject("icon")({"url": cover} if cover is not None else None),
                "properties": {
                    "title": {"id": "title", "type": 'title', **NotionObject("page_title")({"title": page_title})}
                }
                
            }
        )
        try:
            response.raise_for_status()
            url = response.json()["url"]
            print("Page creation")
            print("%s: %s" % ("Name".rjust(10), page_title))
            print("%s: %s" % ("URL".rjust(10), url))
        except:
            print(response.text)

    def retrieve_page(self, page_id: str):
        response = requests.get(
            url=f"{self._PAGES_ENDPOINT}/{page_id}",
            headers=self.headers
        )
        try:
            response.raise_for_status()
            return response.json()
        except:
            print("FAIL\n\n")
            print(response.text)
    
    def create_database(self, parent_id: str, db_title: str, properties: list[dict], icon: str = None, cover: str = None):
        init_properties = self.objects["init_properties"]
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
                "parent": NotionObject("database_parent")({"id": parent_id}),
                "icon": NotionObject("icon")({"url": icon} if icon is not None else None),
                "cover": NotionObject("icon")({"url": cover} if cover is not None else None),
                **NotionObject("page_title")({"title": db_title}),
                "properties": {"Name": {"title": {}}, **properties}
            }
        )
        try:
            response.raise_for_status()
            url = response.json()["url"]
            print("Database creation")
            print("%s: %s" % ("Name".rjust(10), db_title))
            print("%s: %s" % ("URL".rjust(10), url))
        except:
            print("FAIL\n\n")
            print(response.text)

    def create_page_in_database(self, database_id: str, data: dict):
        response = requests.post(
            url=self._PAGES_ENDPOINT,
            headers=self.headers,
            json={
                "parent": NotionObject("database_parent")({"id": database_id}),
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
            print("Page creation into database")
            print("%s: %s" % ("URL".rjust(10), url))
            return response.json()
        except:
            print(response.text)
    
    def query_database(self, database_id: str, limit: int = 10, filters: dict = {"or": []}, sorts=[]) -> List[dict]:
        response = requests.post(
            url=self._QUERY_ENDPOINT % database_id,
            headers=self.headers,
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

    def add_children(self, page_id: str, data: dict):
        response = requests.patch(
            url=self._BLOCKS_ENDPOINT % page_id,
            headers=self.headers,
            json={
                "children": [
                    NotionObject(item["type"])(values=item["values"], children=item.get("children"))
                    for item in data.get("children", [])
                ]
            }
        )
        try:
            response.raise_for_status()
            return response.json()
        except:
            print(response.text)

    def delete_page(self, page_id: str):
        response = requests.patch(
            url=self._PAGES_ENDPOINT + f"/{page_id}",
            headers=self.headers,
            json={"archived": True}
        )
        try:
            response.raise_for_status()
        except:
            print(response.text)

