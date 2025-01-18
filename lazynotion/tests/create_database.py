# import sys
# sys.path.append('.')
# from src.notion import NotionApiHandler
#
# if __name__=="__main__":
#     handler = NotionApiHandler()
#     properties = {
#         "Description": "text", "Checkbox": "checkbox",
#         "Date": "date", "Email": "email",
#         "File": "files", "Formula": "formula",
#         "Number": "number", "People": "people",
#         "Phone Number": "phone_number", "URL": "url",
#     }
#     # properties = {"name": n, "type": t for n,t in properties.items()}
#     # properties = {**properties,
#     #               }
#         # "Select": "select",
#         # "Multi Select": "multi_select",
#     handler.create_database(
#         parent_id=handler.keys["api_handler_page_id"], 
#         db_title="Database creation test",
#         icon="https://www.notion.so/icons/database_gray.svg",
#         properties=properties
#     )
