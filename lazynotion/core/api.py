import os
import yaml
import requests
import logging
import logging.config
from typing import Union, List, Dict, Any
from ..utils import read_yaml, save_yaml, get_api_key, update_dict_from_path, Parameters

class NotionObject:
    """Helper class for creating Notion-compatible objects."""
    
    def __init__(self, name: str):
        self.name = name
        filename = os.path.join(os.path.dirname(__file__), '../configs/objects.yaml')
        self._objects = read_yaml(filename)
    
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


class NotionApi(Parameters):
    """Comprehensive handler for Notion API interactions."""

    # Notion API endpoints
    _PAGES_ENDPOINT = "https://api.notion.com/v1/pages"
    _DATABASE_ENDPOINT = "https://api.notion.com/v1/databases"
    _QUERY_ENDPOINT = "https://api.notion.com/v1/databases/%s/query"
    _max_chars = 1999
    _BLOCKS_ENDPOINT = "https://api.notion.com/v1/blocks/%s/children"

    def __init__(self) -> None:
        # self.keys = read_yaml(self._KEYS_FILE)
        filename = os.path.join(os.path.dirname(__file__), '../configs/objects.yaml')
        self.objects = read_yaml(filename)
        self.headers = self._create_headers()
    
    def _create_headers(self) -> Dict[str, str]:
        """Create authentication headers for Notion API."""
        return {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "Authorization": "Bearer %s" % get_api_key()
        }
    
    def fill_object(self, property_object: str, property_values: List[Any]) -> Dict:
        assert isinstance(property_values, list), "Enter a list please."
        args = self.objects[property_object].copy()
        item = args["object"].copy()
        for path, value in zip(args["paths"], property_values):
            item = update_dict_from_path(item, path, value).copy()
        return item
    
