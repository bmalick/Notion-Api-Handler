import sys
sys.path.append('.')
from src.notion import NotionApiHandler

if __name__=="__main__":
    handler = NotionApiHandler()
    page = handler.retrieve_page(
        page_id=handler.keys["api_handler_page_id"]
    )
    for k,v in page.items():
        print(k, ":", v)
