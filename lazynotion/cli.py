import os
import click
from typing import Optional
from dotenv import load_dotenv
from .core.page_manager import PageManager
from .core.database_manager import DatabaseManager
from .core.api import NotionApi

@click.group()
def cli():
    """LazyNotion CLI - Simplified Notion API interactions"""
    pass

@cli.group()
def page():
    """Page management commands"""
    pass

@cli.group()
def database():
    """Database management commands"""

@page.command(name="create")
@click.option("--parent-id", required=True, type=str, help='Parent page/database ID')
@click.option('--title', required=True, help='Page title')
@click.option('--icon', help='Icon URL')
@click.option('--cover', help='Cover image URL')
def create_page(parent_id: str, title: str, icon: Optional[str] = None, cover: Optional[str] = None):
    page_mgr = PageManager(api=NotionApi(), parent_id=parent_id)
    result = page_mgr.create(page_title=title, icon=icon, cover=cover)
    click.echo(f"Created page: {result}")

@page.command(name="retrieve")
@click.option("--page-id", required=True, type=str, help='Page ID')
def retrieve_page(page_id: str):
    page_mgr = PageManager(api=NotionApi(), page_id=page_id)
    result = page_mgr.retrieve()
    # click.echo(f"Created page: {result.get('url')}")

    for k,v in result.items():
        print(k, ":", v)
    click.echo(f"Retrieved page: {result}")

@page.command(name="create-tasks")
@click.option("--project", type=str)
@click.option("--file", type=str, required=True)
def create_tasks(project, file):
    load_dotenv()
    project_id = os.getenv("PROJECT_ID")
    task_id = os.getenv("TASK_ID")
    task_mgr = DatabaseManager(api=NotionApi(), database_id=task_id)
    project_mgr = DatabaseManager(api=NotionApi(), database_id=project_id)
    project_id = project_mgr.find_id_from_name(name=project)
    icon = "https://www.notion.so/icons/circle_gray.svg"
    with open(file) as f:
        lines = f.readlines()
    for line in lines:
        task_mgr.add_page(
            data = {
                # "icon": {"url": icon},
                "properties": [
                    {"name": "Project", "type": "relation", "values": {"id": project_id}},
                    {"name": "Nom", "type": "page_title", "values": {"title": line.strip()}}
                ]
                    
            }
        )


@database.command(name="query")
# @click.option("--parent-id", required=True, type=str, help='Parent page/database ID')
@click.option("--database-id", required=True, type=str, help='Database ID')
@click.option("--limit", type=int, default=10)
@click.option("--filters", type=str, default="")
@click.option("--sorts", type=str, default="")
def query_database(database_id: str, limit:int, filters, sorts):
    database_mgr = DatabaseManager(api=NotionApi(), database_id=database_id)
    result = database_mgr.query(limit=limit, filters=filters, sorts=sorts)

    click.echo(f"Retrieved page: {result}")

if __name__ == "__main__":
    cli()
