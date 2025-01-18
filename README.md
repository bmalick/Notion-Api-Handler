# Notion API Handler

## Overview
A Python library for interacting with the Notion API, providing robust functionality for managing pages, databases, and content.

## Includes
- Create and manage Notion pages
- Create and query databases
- Add page children
- Handle complex Notion object creation

## Features
- [Notion Task Cleanup Script](#notion-task-cleanup-script)

## Installation
```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
pip install -r requirements.txt
```

## Configuration Files
### `keys.yaml`
```yaml
api_token: your_notion_api_token_here
task_db_token: your_task_database_id_here
```

### `objects.yaml`
Define Notion object templates for consistent object creation.

### `log-config.yaml`
Configure logging behavior

## Usage Examples

### Creating a Page
```python
handler = NotionApiHandler()
handler.create_page(
    parent_id="parent_page_id", 
    page_title="My New Page",
    icon="https://example.com/icon.png"
)
```

### Retrieve a Page
```python
handler = NotionApiHandler()
page = handler.retrieve_page(
    page_id="page_id", 
)
```

### Creating a Database
```python
properties = {
    "Description": "text", "Checkbox": "checkbox",
    "Date": "date", "Email": "email",
}
handler.create_database(
    parent_id="parent_page_id", 
    db_title="Project Tracker",
    properties=properties
)
```

### Querying a Database
```python
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

results = handler.query_database(
    database_id="database_id", 
    filters=filters, sorts=sorts,
    limit=50
)
```

## Logging
Configurable logging through `log-config.yaml`

## Notion Task Cleanup Script

Automatically delete completed tasks without associated projects from a Notion database.

### Configuration
Customize deletion criteria in script:
- Completed tasks filter
- Project relation filter
- Sorting preferences

### Logging
- Utilizes configurable logging
- Records task deletion information

### Example
```bash
# Delete completed tasks from specific database
python delete.py db_abc123
```
