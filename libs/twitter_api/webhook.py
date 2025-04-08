from .api_base import TwitterAPIRequests
from .auth import Auth

class WebhookAPI:
    def __init__(self, api_key):
        self.api = TwitterAPIRequests(Auth(api_key))

    def get_rules(self):
        response = self.api.get("twitter/webhook/get_rules")
        return response.get_data()

    def add_rule(self, tag, value, interval_seconds):
        payload = {"tag": tag, "value": value, "interval_seconds": interval_seconds}
        response = self.api.post("oapi/tweet_filter/add_rule", data=payload)
        return response.get_data()