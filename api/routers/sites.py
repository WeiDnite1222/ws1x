from fastapi import APIRouter, HTTPException
from datetime import datetime

# Private
from private.tool import get_articles_index_data, get_server_message_data

class SitesRouter:
    def __init__(self, prefix="/sites", tags=["sites"]):
        self.router = APIRouter(prefix=prefix, tags=tags)

        @self.router.get("/articles")
        def get_sites_articles_index():
            data = get_articles_index_data()

            if data is None:
                raise HTTPException(status_code=400,
                                    detail="Could not get sites articles index. Server-02 may not be online.")

            return {
                "responseDate": datetime.now(),
                "contentTopic": "Get sites articles index.",
                "ResponseData": {
                    "articlesIndexData": data
                }
            }

        @self.router.get("/server/message")
        def get_server_message():
            data = get_server_message_data()

            if data is None:
                raise HTTPException(status_code=400,
                                    detail="Could not get sites articles index. Server-02 may not be online.")

            return {
                "responseDate": datetime.now(),
                "contentTopic": "Get sites articles index.",
                "ResponseData": {
                    "messageData": data
                }
            }