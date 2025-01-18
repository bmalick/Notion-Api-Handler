import sys
from src.notion import NotionApiHandler

if __name__ == "__main__":
    handler = NotionApiHandler()
    logger = handler.get_logger("delete")

    if len(sys.argv)!=2:
        print("Usage: %s <database token>" % sys.argv[0])
        sys.exit()

    db_token = sys.argv[1]

    filters = {
        "and": [
            {"property": "Completed",
            "checkbox": {"equals": True}},
            {"property": "Project",
             "relation": {"is_empty": True}}
        ]
    }
    sorts = [
        {"property": "Date creation", "direction": "ascending"}
    ]

    while True:

        data = handler.query_database(database_id=db_token,
                                      filters=filters, limit=100,
                                      sorts=sorts)
        if len(data)==0: break
        for task in data:
            task_id = task["id"]
            task_name = task["properties"]["Nom"]["title"][0]["plain_text"]
        handler.delete_page(task_id)
        logger.info(task_name)

