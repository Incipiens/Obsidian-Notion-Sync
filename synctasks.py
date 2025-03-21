import requests
import os
import re
import time

# Set your Notion integration token and database ID
NOTION_TOKEN = "your notion token here" 
DATABASE_ID = "your database id here" 
TASKS = "tasks.md" # Replace this with the name of your to-do list

# Headers required for Notion API requests
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28" 
}

def parse_markdown_tasks(filepath):
    """
    Reads the markdown file and parses tasks.
    Expected format:
      - [ ] Task description
      - [x] Completed task.
    Returns a list of dictionaries with title and status.
    """
    tasks = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = re.match(r"- \[( |x)\] (.+)", line)
            if match:
                raw_status = "Completed" if match.group(1) == "x" else "Incomplete"
                task_desc = match.group(2)
                tasks.append({
                    "title": task_desc,
                    "status": raw_status
                })
    return tasks

def query_task(task_title):
    """
    Queries Notion for a task with the given title.
    Returns the page data (including page ID and current properties) if found, otherwise return None.
    """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": "Name",
            "title": {
                "equals": task_title
            }
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Error querying for task '{task_title}': {response.status_code} {response.text}")
        return None
    data = response.json()
    results = data.get("results", [])
    if results:
        return results[0]
    return None

def create_notion_page(task):
    """
    Creates a new page in the Notion database for the given task.
    Expects the database to have properties: 'Name' (title) and 'Status' (status).
    """
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": task["title"]}}
                ]
            },
            "Status": {
                "status": {
                    "name": task["status"]
                }
            }
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print(f"Task '{task['title']}' created successfully!")
    else:
        print(f"Failed to create task '{task['title']}': {response.status_code} {response.text}")

def update_notion_page(page_id, task):
    """
    Updates an existing Notion page with the new status.
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "properties": {
            "Status": {
                "status": {
                    "name": task["status"]
                }
            }
        }
    }
    response = requests.patch(url, json=data, headers=headers)
    if response.status_code == 200:
        print(f"Task '{task['title']}' updated successfully!")
    else:
        print(f"Failed to update task '{task['title']}': {response.status_code} {response.text}")

def get_all_notion_tasks():
    """
    Retrieves all active (non-archived) tasks from the Notion database.
    Returns a dictionary mapping task titles to their page IDs.
    """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    tasks = {}
    payload = {
        "page_size": 100  # Adjust if required
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Error retrieving tasks from Notion: {response.status_code} {response.text}")
        return tasks
    data = response.json()
    for page in data.get("results", []):
        properties = page.get("properties", {})
        title_prop = properties.get("Name", {})
        title_text = ""
        if "title" in title_prop and title_prop["title"]:
            title_text = title_prop["title"][0]["plain_text"]
        if title_text:
            tasks[title_text] = page["id"]
    return tasks

def archive_notion_page(page_id, task_title):
    """
    Archives the given Notion page (removing it from the active list).
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {"archived": True}
    response = requests.patch(url, json=data, headers=headers)
    if response.status_code == 200:
        print(f"Task '{task_title}' archived successfully!")
    else:
        print(f"Failed to archive task '{task_title}': {response.status_code} {response.text}")

if __name__ == "__main__":
    markdown_file = TASKS
    markdown_tasks = parse_markdown_tasks(markdown_file)
    
    # Reverse the order of tasks to sync them in the order they appear in Markdown (as Notion adds new tasks at the top).
    markdown_tasks = markdown_tasks[::-1]
    
    markdown_task_titles = {task["title"] for task in markdown_tasks}
    
    # Retrieve all tasks currently in Notion
    notion_tasks = get_all_notion_tasks()
    
    # Process tasks from Markdown file
    for task in markdown_tasks:
        existing_page = query_task(task["title"])
        if existing_page:
            page_id = existing_page["id"]
            update_notion_page(page_id, task)
        else:
            create_notion_page(task)
        time.sleep(0.2)  # slight delay to avoid rate limits
    
    # Archive tasks in Notion that are not present in the Markdown file:
    for notion_title, page_id in notion_tasks.items():
        if notion_title not in markdown_task_titles:
            print(f"Task '{notion_title}' not found in Markdown. Archiving it...")
            archive_notion_page(page_id, notion_title)
            time.sleep(0.2)


            