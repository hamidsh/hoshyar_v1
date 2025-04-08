from django.core.management.base import BaseCommand
from libs.twitter_api import TwitterClient

class Command(BaseCommand):
    help = "استخراج و ذخیره توییت‌ها از TwitterAPI.io"

    def add_arguments(self, parser):
        parser.add_argument("search", type=str, help="عبارت جستجو")
        parser.add_argument("--max_tweets", type=int, default=10, help="حداکثر تعداد توییت‌ها")
        parser.add_argument("--query_type", type=str, default="Latest", help="نوع جستجو: Latest یا Top")
        parser.add_argument("--language", type=str, help="زبان توییت‌ها (مثال: en)")
        parser.add_argument("--from_date", type=str, help="از تاریخ (مثال: 2025-01-01)")
        parser.add_argument("--to_date", type=str, help="تا تاریخ (مثال: 2025-12-31)")
        parser.add_argument("--verified", action="store_true", help="فقط کاربران تأییدشده")
        parser.add_argument("--safe", action="store_true", help="محتوای ایمن")
        parser.add_argument("--exclude_retweets", action="store_true", help="حذف ریتوییت‌ها")
        parser.add_argument("--media", action="store_true", help="فقط توییت‌های با رسانه")

    def handle(self, *args, **options):
        search = options["search"]
        max_tweets = options["max_tweets"]
        query_type = options["query_type"]
        language = options.get("language")
        from_date = options.get("from_date")
        to_date = options.get("to_date")
        verified = options["verified"]
        safe = options["safe"]
        exclude_retweets = options["exclude_retweets"]
        media = options["media"]
        client = TwitterClient()
        tweets = client.fetch_and_save_tweets(
            search, max_tweets, query_type, language, from_date, to_date,
            verified, safe, exclude_retweets, media
        )
        self.stdout.write(self.style.SUCCESS(f"با موفقیت {len(tweets)} توییت ذخیره شد"))