
# Converting files to video
This application synchronizes a local Obsidian markdown file with [Notion's To-do list](https://www.notion.com/templates/to-do-list) template. 

This proof of concept shows how to work with the Notion API and requires removing all fields aside from the Task Name field and Status field to work in the template above.


## Execution

To execute this script you'll need to install the request Python library. Navigate to the folder in a terminal and run the following command.

```bash
  pip install requests
```

You will need to get your [Notion integration token](https://developers.notion.com/docs/create-a-notion-integration) and your Notion database ID for this to run. You will then need to add your integration to your Notion database.

To run:

```bash
  python synctasks.py
```

## Documentation
This program was written for an article on XDA-Developers by Adam Conway, Lead Technical Editor of the site.

[XDA-Developers article](https://www.xda-developers.com/i-used-python-sync-obsidian-to-do-list-notion/)

