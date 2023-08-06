import aiohttp
import sys
import logging

from typing import Union

from .model import EnkaNetworkResponse
from .exception import VaildateUIDError, UIDNotFounded
from .json import Config
from .utils import create_path, VERSION, validate_uid
class EnkaNetworkAPI:
    USER_AGENT = "EnkaNetwork.py/{version} (Python {major}.{minor}.{micro})"
    LOGGER = logging.getLogger(__name__)

    def __init__(self, lang: str = "en", debug: bool = False) -> None:
        # Logging
        logging.basicConfig()
        logging.getLogger("enkanetwork").setLevel(logging.DEBUG if debug else logging.ERROR)

        # Set language and load config
        Config.set_languege(lang)

        Config.load_json_data()
        Config.load_json_lang()
    
    async def __get_headers(self):
        # Get python version
        python_version = sys.version_info

        return {
            "User-Agent": self.USER_AGENT.format(
                version=VERSION,
                major=python_version.major,
                minor=python_version.minor,
                micro=python_version.micro
            ),
        }

    async def fetch_user(self, uid: Union[str, int]) -> EnkaNetworkResponse:
        self.LOGGER.debug(f"Validating with UID {uid}...")
        if not validate_uid(str(uid)):
            raise VaildateUIDError("Validate UID failed. Please check your UID.")
        
        self.LOGGER.debug(f"Fetching user with UID {uid}...")
        async with aiohttp.ClientSession(headers=await self.__get_headers()) as session:
            # Fetch JSON data
            resp = await session.request(method="GET", url=create_path(f"u/{uid}/__data.json"))

            # Check if status code is not 200 (Ex. 500)
            if resp.status != 200:
                raise UIDNotFounded(f"UID {uid} not found.")

            # Parse JSON data
            data = await resp.json()
                        
            if not data:
                raise UIDNotFounded(f"UID {uid} not found.")

            self.LOGGER.debug("Got data from EnkaNetwork.")
            self.LOGGER.debug(f"Raw data: {data}")

            # Cleanup
            await session.close()

            # Return data
            self.LOGGER.debug("Parsing data...")
            return EnkaNetworkResponse.parse_obj(data)