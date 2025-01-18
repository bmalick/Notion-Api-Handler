import requests
from .api import NotionObject, NotionApi

# TODO: add print to each method

class PageManager:
    def __init__(self, api, parent_id: str=None, page_id: str=None):
        self.parent_id = parent_id
        self.page_id = page_id
        self.api = api

    def create(self, page_title: str, icon: str = None, cover: str = None):
        response = requests.post(
            url=self.api._PAGES_ENDPOINT,
            headers=self.api.headers,
            json={
                "parent": NotionObject("page_parent")({"id": self.parent_id}),
                "icon": NotionObject("icon")({"url": icon} if icon is not None else None),
                "cover": NotionObject("icon")({"url": cover} if cover is not None else None),
                "properties": {
                    "title": {"id": "title", "type": 'title', **NotionObject("page_title")({"title": page_title})}
                }
                
            }
        )
        try:
            response.raise_for_status()
            return response.json()
        except:
            print(response.text)

    def retrieve(self):
        if self.page_id is None:
            print("This page does not exists")
            return
        response = requests.get(
            url=f"{self.api._PAGES_ENDPOINT}/{self.page_id}",
            headers=self.api.headers
        )
        try:
            response.raise_for_status()
            return response.json()
        except:
            print("FAIL\n\n")
            print(response.text)

    def add_children(self, data: dict):
        response = requests.patch(
            url=self.api._BLOCKS_ENDPOINT % self.page_id,
            headers=self.api.headers,
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

    # def delete_page(self):
    #     response = requests.patch(
    #         url=self.api._PAGES_ENDPOINT + f"/{page_id}",
    #         headers=self.api.headers,
    #         json={"archived": True}
    #     )
    #     try:
    #         response.raise_for_status()
    #     except:
    #         print(response.text)
