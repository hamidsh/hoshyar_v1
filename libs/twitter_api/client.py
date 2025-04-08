from .tweet import TweetAPI
from .user import UserAPI
from .list import ListAPI
from .webhook import WebhookAPI
from .auth import Auth
from .utilities import parse_twitter_date, build_twitter_query  # اضافه کردن build_twitter_query
from twitter.models import Tweet, User, TweetEntity, Keyword, TweetMedia

class TwitterClient:
    def __init__(self, api_key="cf5800d7a52a4df89b5df7ffe1c7303d"):
        self.api_key = api_key
        self.tweet_api = TweetAPI(self.api_key)
        self.user_api = UserAPI(self.api_key)
        self.list_api = ListAPI(self.api_key)
        self.webhook_api = WebhookAPI(self.api_key)

    def _process_tweet(self, data):
        tweet_data = {
            "type": data.get("type"),
            "id": data.get("id"),
            "url": data.get("url"),
            "text": data.get("text"),
            "source": data.get("source"),
            "created_at": parse_twitter_date(data["createdAt"]) if data.get("createdAt") else None,
            "retweet_count": data.get("retweetCount", 0),
            "like_count": data.get("likeCount", 0),
            "reply_count": data.get("replyCount", 0),
            "quote_count": data.get("quoteCount", 0),
            "view_count": data.get("viewCount", 0),
            "lang": data.get("lang"),
            "bookmark_count": data.get("bookmarkCount", 0),
            "is_reply": data.get("isReply", False),
            "in_reply_to_id": data.get("inReplyToId"),
            "conversation_id": data.get("conversationId"),
            "in_reply_to_user_id": data.get("inReplyToUserId"),
            "in_reply_to_username": data.get("inReplyToUsername"),
            "author": None,
            "entities": data.get("entities", {}),
            "extended_entities": data.get("extendedEntities", {}),
            "quoted_tweet": None,
            "retweeted_tweet": None
        }
        if "author" in data and data["author"] and data["author"].get("id"):
            author_data = data["author"]
            tweet_data["author"] = {
                "type": author_data.get("type"),
                "id": author_data.get("id"),
                "username": author_data.get("userName", "Unknown"),
                "url": author_data.get("url"),
                "name": author_data.get("name"),
                "is_blue_verified": author_data.get("isBlueVerified", False),
                "profile_picture": author_data.get("profilePicture"),
                "cover_picture": author_data.get("coverPicture"),
                "description": author_data.get("description"),
                "location": author_data.get("location"),
                "followers": author_data.get("followers", 0),
                "following": author_data.get("following", 0),
                "can_dm": author_data.get("canDm", False),
                "created_at": parse_twitter_date(author_data["createdAt"]) if author_data.get("createdAt") else None,
                "fast_followers_count": author_data.get("fastFollowersCount", 0),
                "favourites_count": author_data.get("favouritesCount", 0),
                "has_custom_timelines": author_data.get("hasCustomTimelines", False),
                "is_translator": author_data.get("isTranslator", False),
                "media_count": author_data.get("mediaCount", 0),
                "statuses_count": author_data.get("statusesCount", 0),
                "withheld_in_countries": author_data.get("withheldInCountries", []),
                "possibly_sensitive": author_data.get("possiblySensitive", False),
                "pinned_tweet_ids": author_data.get("pinnedTweetIds", []),
                "is_automated": author_data.get("isAutomated", False),
                "automated_by": author_data.get("automatedBy"),
                "unavailable": author_data.get("unavailable", False),
                "message": author_data.get("message"),
                "unavailable_reason": author_data.get("unavailableReason"),
                "profile_bio": author_data.get("profile_bio", {})
            }
        if "quoted_tweet" in data and data["quoted_tweet"] and data["quoted_tweet"].get("id"):
            tweet_data["quoted_tweet"] = self._process_tweet(data["quoted_tweet"])
        if "retweeted_tweet" in data and data["retweeted_tweet"] and data["retweeted_tweet"].get("id"):
            tweet_data["retweeted_tweet"] = self._process_tweet(data["retweeted_tweet"])
        return tweet_data

    def fetch_and_save_tweets(self, search, max_tweets=100, query_type="Latest", language=None, from_date=None, to_date=None, verified=False, safe=False, exclude_retweets=False, media=False):
        query = build_twitter_query(
            search=search, user=None, to=None, mentions=None, language=language,
            from_date=from_date, to_date=to_date, exact=False, verified=verified,
            safe=safe, exclude_retweets=exclude_retweets, media=media
        )
        raw_tweets = self.tweet_api.fetch_tweets(search=query, max_tweets=max_tweets, query_type=query_type)
        processed_tweets = []
        for tweet_data in raw_tweets:
            processed_data = self._process_tweet(tweet_data)
            tweet = self._save_tweet(processed_data, search_query=query, keyword=search)
            processed_tweets.append(tweet)
        return processed_tweets

    def _save_tweet(self, processed_data, search_query=None, keyword=None):
        author = None
        if processed_data["author"] and processed_data["author"]["id"]:
            author, _ = User.objects.get_or_create(
                user_id=processed_data["author"]["id"],
                defaults={
                    "username": processed_data["author"]["username"] or "Unknown",
                    "name": processed_data["author"]["name"] or "",
                    "bio": processed_data["author"]["description"] or "",
                    "followers_count": processed_data["author"]["followers"],
                    "following_count": processed_data["author"]["following"],
                    "created_at": processed_data["author"]["created_at"] or parse_twitter_date("1970-01-01T00:00:00Z")
                }
            )
        quoted_tweet = None
        if processed_data["quoted_tweet"]:
            quoted_tweet = self._save_tweet(processed_data["quoted_tweet"])
        retweeted_tweet = None
        if processed_data["retweeted_tweet"]:
            retweeted_tweet = self._save_tweet(processed_data["retweeted_tweet"])
        tweet, created = Tweet.objects.get_or_create(
            tweet_id=processed_data["id"],
            defaults={
                "type": processed_data["type"],
                "url": processed_data["url"],
                "text": processed_data["text"],
                "source": processed_data["source"],
                "created_at": processed_data["created_at"],
                "author": author,
                "search_query": search_query,
                "retweet_count": processed_data["retweet_count"],
                "like_count": processed_data["like_count"],
                "reply_count": processed_data["reply_count"],
                "quote_count": processed_data["quote_count"],
                "view_count": processed_data["view_count"],
                "lang": processed_data["lang"],
                "bookmark_count": processed_data["bookmark_count"],
                "is_reply": processed_data["is_reply"],
                "in_reply_to_id": processed_data["in_reply_to_id"],
                "conversation_id": processed_data["conversation_id"],
                "in_reply_to_user_id": processed_data["in_reply_to_user_id"],
                "in_reply_to_username": processed_data["in_reply_to_username"],
                "quoted_tweet": quoted_tweet,
                "retweeted_tweet": retweeted_tweet
            }
        )
        # ذخیره کلمات کلیدی
        if keyword:
            keyword_obj, _ = Keyword.objects.get_or_create(word=keyword)
            tweet.keywords.add(keyword_obj)
        # ذخیره موجودیت‌ها
        for hashtag in processed_data["entities"].get("hashtags", []):
            TweetEntity.objects.get_or_create(tweet=tweet, hashtag=hashtag["text"] or "")
        for url in processed_data["entities"].get("urls", []):
            TweetEntity.objects.get_or_create(tweet=tweet, url=url["expanded_url"] or "")
        for mention in processed_data["entities"].get("user_mentions", []):
            mention_user = None
            if mention["id_str"]:
                mention_user, _ = User.objects.get_or_create(
                    user_id=mention["id_str"],
                    defaults={"username": mention["screen_name"] or "Unknown"}
                )
            TweetEntity.objects.get_or_create(
                tweet=tweet,
                mention_username=mention["screen_name"] or "",
                mention_user=mention_user
            )
        # ذخیره رسانه‌ها
        for media in processed_data["extended_entities"].get("media", []):
            TweetMedia.objects.get_or_create(
                tweet=tweet,
                type=media["type"],
                url=media["media_url_https"],
                media_key=media["media_key"]
            )
        return tweet

    def fetch_and_save_user(self, username):
        user_data = self.user_api.fetch_user_info(username)
        if user_data:
            created_at = parse_twitter_date(user_data["createdAt"])
            user, created = User.objects.get_or_create(
                user_id=user_data["id"],
                defaults={
                    "username": user_data["userName"],
                    "name": user_data.get("name", ""),
                    "bio": user_data.get("description", ""),
                    "followers_count": user_data.get("followersCount", 0),
                    "following_count": user_data.get("followingsCount", 0),
                    "created_at": created_at
                }
            )
            return user
        return None

    def fetch_and_save_list_tweets(self, list_id, max_tweets=100):
        raw_tweets = self.list_api.fetch_list_tweets(list_id, max_tweets)
        processed_tweets = []
        for tweet_data in raw_tweets:
            processed_data = self._process_tweet(tweet_data)
            tweet = self._save_tweet(processed_data, search_query=f"list:{list_id}")
            processed_tweets.append(tweet)
        return processed_tweets

    def fetch_user_tweets(self, username, max_tweets=100):
        return self.user_api.fetch_last_tweets(username, max_tweets)

    def fetch_followers(self, username, max_users=100):
        return self.user_api.fetch_followers(username, max_users)

    def fetch_following(self, username, max_users=100):
        return self.user_api.fetch_following(username, max_users)

    def fetch_list_members(self, list_id, max_users=100):
        return self.list_api.fetch_members(list_id, max_users)