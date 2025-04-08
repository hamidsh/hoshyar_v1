from .api_base import TwitterAPIRequests
from .auth import Auth
from .exceptions import ValidationError

class UserAPI:
    def __init__(self, api_key):
        self.api = TwitterAPIRequests(Auth(api_key))

    def fetch_user_info(self, username):
        if not username:
            raise ValidationError("username باید وارد شود")
        params = {"userName": username}
        response = self.api.get("twitter/user/info", params)
        return response.get_data()

    def fetch_last_tweets(self, username=None, user_id=None, max_tweets=100, cursor=""):
        if not username and not user_id:
            raise ValidationError("حداقل username یا user_id باید وارد شود")
        params = {"cursor": cursor}
        if username:
            params["userName"] = username
        if user_id:
            params["userId"] = user_id
        return self.api.fetch_paginated("twitter/user/last_tweets", params, max_tweets)

    def fetch_followers(self, username=None, user_id=None, max_users=100, cursor=""):
        if not username and not user_id:
            raise ValidationError("حداقل username یا user_id باید وارد شود")
        params = {"cursor": cursor}
        if username:
            params["userName"] = username
        if user_id:
            params["userId"] = user_id
        return self.api.fetch_paginated("twitter/user/followers", params, max_users)

    def fetch_following(self, username=None, user_id=None, max_users=100, cursor=""):
        if not username and not user_id:
            raise ValidationError("حداقل username یا user_id باید وارد شود")
        params = {"cursor": cursor}
        if username:
            params["userName"] = username
        if user_id:
            params["userId"] = user_id
        return self.api.fetch_paginated("twitter/user/following", params, max_users)