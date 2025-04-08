from .api_base import TwitterAPIRequests
from .auth import Auth
from .utilities import build_twitter_query
from .exceptions import ValidationError

class TweetAPI:
    def __init__(self, api_key):
        self.api = TwitterAPIRequests(Auth(api_key))

    def fetch_tweets(self, search, max_tweets=100, query_type="Latest", cursor="", language=None, from_date=None, to_date=None):
        query = build_twitter_query(
            search=search, language=language, from_date=from_date, to_date=to_date
        )
        if not query:
            raise ValidationError("حداقل یک پارامتر جستجو باید وارد شود")
        if query_type not in ["Latest", "Top"]:
            raise ValidationError("query_type باید 'Latest' یا 'Top' باشد")
        params = {"query": query, "queryType": query_type, "cursor": cursor}
        try:
            return self.api.fetch_paginated("twitter/tweet/advanced_search", params, max_tweets)
        except Exception as e:
            if "400" in str(e):
                raise ValidationError(f"خطای جستجو: {str(e)}")
            raise

    def replies(self, tweet_id, max_tweets=100, cursor=""):
        if not tweet_id:
            raise ValidationError("Tweet id نمی‌تواند خالی باشد")
        params = {"tweetId": tweet_id, "cursor": cursor}
        return self.api.fetch_paginated("twitter/tweet/replies", params, max_tweets)