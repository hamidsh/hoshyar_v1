ENDPOINT_DATA_MAP = {
    "twitter/tweet/advanced_search": "tweets",
    "twitter/tweet/replies": "tweets",
    "twitter/user/last_tweets": "tweets",
    "twitter/list/tweets": "tweets",
    "twitter/user/info": "data",
    "twitter/user/followers": "followings",
    "twitter/user/following": "followings",
    "twitter/list/members": "members",
    "twitter/webhook/get_rules": "rules",
}

class APIResponse:
    def __init__(self, data, status, message, next_page=None):
        self.data = data
        self.status = status
        self.message = message
        self.next_page = next_page

    @classmethod
    def from_response(cls, response, endpoint):
        data_key = ENDPOINT_DATA_MAP.get(endpoint, "data")
        data = response.get(data_key, [])
        status = response.get("status", "success")
        message = response.get("message", "")
        next_page = response.get("next_page") or response.get("next_cursor")
        return cls(data, status, message, next_page)

    def get_data(self):
        return self.data

    def has_next_page(self):
        return bool(self.next_page)