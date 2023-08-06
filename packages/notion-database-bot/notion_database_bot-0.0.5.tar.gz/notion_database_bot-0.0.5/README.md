# Notion Database Bot

Notion-Database-Bot is a python tool for synchronizing data in Notion Database through Notion official api. The main purpose is to facilitate the recording of daily experimental data.

## Installation

```
pip install notion-database-bot
```

## Prerequisites

1. [Create an integration](https://developers.notion.com/docs/getting-started#step-1-create-an-integration), then you can get your own Internal Integration Token (`token`).

2. [Share a database with your integration](https://developers.notion.com/docs/getting-started#step-2-share-a-database-with-your-integration).

3. Get your target database ID (`database_id`):
   > Here's a quick procedure to find the database ID for a specific database in Notion:
   >
   >> Open the database as a full page in Notion. Use the Share menu to Copy link. Now paste the link in your text editor so you can take a closer look. The URL uses the following format:
   >>
   >> https://www.notion.so/{workspace_name}/{database_id}?v={view_id}
   >> Find the part that corresponds to {database_id} in the URL you pasted. It is a 36 character long string. This value is your database ID.
   >> Note that when you receive the database ID from the API, e.g. the search endpoint, it will contain hyphens in the UUIDv4 format. You may use either the hyphenated or un-hyphenated ID when calling the API.

## Usage

- Init your Bot:
  ```python
  from notion_database_bot import NotionDatabaseBot
  bot = NotionDatabaseBot(token)
  ```

- Read database content:
  ```python
  content = bot.read_database(database_id)
  ```

- Add a page/row/sample to database
  ```python
  temp_dict = {"Model": "bert-base-uncased", "ppl": "5.21"}
  properties = bot.dict2properties(temp_dict, "Model")
  bot.create_page(database_id, properties)
  ```

## References:
- https://developers.notion.com/
- https://prettystatic.com/notion-api-python/