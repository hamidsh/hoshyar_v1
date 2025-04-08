from .api_base import TwitterAPIRequests
from .auth import Auth
from .exceptions import ValidationError

class ListAPI:
    def __init__(self, api_key):
        self.api = TwitterAPIRequests(Auth(api_key))

    def fetch_list_tweets(self, list_id, max_tweets=100, cursor="", include_replies=True):
        if not list_id:
            raise ValidationError("List id باید وارد شود")
        params = {
            "listId": list_id,
            "includeReplies": str(include_replies).lower(),
            "cursor": cursor
        }
        return self.api.fetch_paginated("twitter/list/tweets", params, max_tweets)

    def fetch_members(self, list_id, max_users=100, cursor=""):
        if not list_id:
            raise ValidationError("List id باید وارد شود")
        params = {"listId": list_id, "cursor": cursor}
        return self.api.fetch_paginated("twitter/list/members", params, max_users)