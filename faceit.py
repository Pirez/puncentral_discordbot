
import os
import sys
import json
import requests

from loguru import logger
from dotenv import load_dotenv


class FaceitData:
    """
    The Data API for Faceit
    
    Source code @ LaughingLove: 
    https://github.com/LaughingLove/faceit_api.py/blob/master/faceit_data.py
    """

    def __init__(self):
        load_dotenv(override=True)

        faceit_token = os.getenv("FACEIT_TOKEN", None)
        if faceit_token is None:
            logger.error("Did not provide FACEIT token, exiting!")
            sys.exit(1)
        
        self.api_token = faceit_token
        self.base_url = 'https://open.faceit.com/data/v4'

        self.headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.api_token)
        }

        logger.info("Init Faceit!")

    def get_userstat(self, username: str):
        url = os.path.join(self.base_url, f"search/players?nickname={username}")
        res = requests.get(url, headers=self.headers)
        if res.status_code == 200:
            return json.loads(res.content.decode('utf-8'))
        else:
            return None


if __name__ == "__main__":
    # An example
    username = "DrWho"
    fd = FaceitData()
    stat = fd.get_userstat(username)
    level = stat['items'][0]['games'][0]['skill_level']
    logger.info(f"{stat}")
    logger.info(f"{level}")
    

