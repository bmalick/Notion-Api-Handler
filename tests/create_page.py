import sys
sys.path.append('.')
from src.notion import NotionApiHandler

if __name__=="__main__":
    handler = NotionApiHandler()
    handler.create_page(
        parent_id=handler.keys["api_handler_page_id"], 
        page_title="Page creation test",
        icon="https://www.notion.so/icons/document_gray.svg"
    )
