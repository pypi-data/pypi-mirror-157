import requests, json


class NotionDatabaseBot:
    """"""

    def __init__(self, token: str):
        """
        Init an Notion Database Bot object.
        Parameters:
            - token: Internal Integration Token
        """
        self.token = token
        self.headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json", "Notion-Version": "2022-02-22"}

    def read_database(self, database_id: str):
        """
        Read Notion Database content.
        Parameters:
            - database_id: Notion Database ID
        """
        readUrl = f"https://api.notion.com/v1/databases/{database_id}/query"

        res = requests.request("POST", readUrl, headers=self.headers)
        data = res.json()
        print(res.status_code)
        print(res.text)

        return data

    def create_page(self, database_id, properties):
        """
        Create a new page/row/sample in Notion Database.
        Parameters:
            - database_id: Notion Database ID
            - properties: Notion Database Property object (dict), refer to https://developers.notion.com/reference/property-object
        """
        createUrl = "https://api.notion.com/v1/pages"

        newPageData = {
            "parent": {"database_id": database_id},
            "properties": properties,
        }

        data = json.dumps(newPageData)

        res = requests.request("POST", createUrl, headers=self.headers, data=data)

        print(res.status_code)
        print(res.text)

    def update_page(self, page_id, properties):
        """
        Update page/row/sample content stored in Notion Database.
        Parameters:
            - page_id: Notion Page ID
            - properties: Notion Database Property object (dict), refer to https://developers.notion.com/reference/property-object
        """
        update_url = f"https://api.notion.com/v1/pages/{page_id}"

        update_data = {"properties": properties}

        data = json.dumps(update_data)

        response = requests.request("PATCH", update_url, headers=self.headers, data=data)

        print(response.status_code)
        print(response.text)

    @staticmethod
    def dict2properties(src_dict: dict, title_key: str = None):
        """
        Turn a dict to Property object.
        Parameters:
            - src_dict: Source dict, contains a title key/value pair and other properties key/value pairs.
            - title_key: Title key string.
        """
        assert title_key is not None, "title_key must be provided."
        properties = dict()
        for key, value in src_dict.items():
            if key == title_key:
                properties[key] = {"title": [{"text": {"content": str(value)}}]}
            else:
                properties[key] = {"rich_text": [{"text": {"content": str(value)}}]}
        return properties


if __name__ == "__main__":

    # Init your Bot
    token = ""
    bot = NotionDatabaseBot(token)

    # Read database content
    database_id = ""
    content = bot.read_database(database_id)

    # Add a page/row/sample to database
    temp_dict = {"Model": "bert-base-uncased", "ppl": "5.21"}
    properties = bot.dict2properties(temp_dict, "Model")
    bot.create_page(database_id, properties)