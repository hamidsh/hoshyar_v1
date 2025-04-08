import requests
from datetime import datetime
from .response import APIResponse

class TwitterAPIRequests:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": self.api_key})
        self.timeout = 10
        self.BASE_URL = "https://api.twitterapi.io/"  # بدون /v1/

    def request(self, method, endpoint, params=None, data=None):
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return APIResponse.from_response(response.json(), endpoint)
        except requests.exceptions.RequestException as e:
            error_msg = f"خطا در درخواست {method} به {endpoint}: {str(e)}"
            if hasattr(e.response, "text"):
                error_msg += f" - پاسخ: {e.response.text}"
            raise Exception(error_msg) from e

    def get(self, endpoint, params=None):
        return self.request("GET", endpoint, params=params)

class TweetAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api = TwitterAPIRequests(self.api_key)

    def fetch_tweets(self, search, max_tweets=100, cursor=""):
        params = {"query": search, "queryType": "Latest", "cursor": cursor}
        all_tweets = []
        endpoint = "twitter/tweet/advanced_search"
        while len(all_tweets) < max_tweets:
            response = self.api.get(endpoint, params)
            tweets = response.get_data()
            if not tweets:
                break
            remaining = max_tweets - len(all_tweets)
            all_tweets.extend(tweets[:remaining])
            if not response.has_next_page():
                break
            params["cursor"] = response.next_page
        return all_tweets

class TwitterClient:
    def __init__(self, api_key="cf5800d7a52a4df89b5df7ffe1c7303d"):
        self.api_key = api_key
        self.tweet_api = TweetAPI(self.api_key)

    def fetch_and_save_tweets(self, search, max_tweets=100):
        from .models import Tweet
        tweets = self.tweet_api.fetch_tweets(search, max_tweets)
        saved_tweets = []
        for data in tweets:
            # تبدیل فرمت تاریخ Twitter به فرمت Django
            created_at = datetime.strptime(data["createdAt"], "%a %b %d %H:%M:%S %z %Y")
            tweet, created = Tweet.objects.get_or_create(
                tweet_id=data["id"],
                defaults={
                    "text": data["text"],
                    "created_at": created_at,
                    "username": data["author"]["userName"],
                    "search_query": search
                }
            )
            saved_tweets.append(tweet)
        return saved_tweets