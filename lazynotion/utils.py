import os
import yaml
import logging
from dotenv import load_dotenv
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

def get_api_key():
    load_dotenv()
    """
    Retrieve the Notion API key from the environment variable or fallback configuration.
    """
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Set NOTION_API_KEY as an environment variable.")
    return api_key


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


def get_logger(log_config_dict: str, name: str):
    """Configure and return a logger."""
    log_config_dict = read_yaml("log-config.yaml")
    logging.config.dictConfig(log_config_dict)
    return logging.getLogger(name)
