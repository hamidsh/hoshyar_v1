from django.core.management.base import BaseCommand
from twitter.client import TwitterClient

class Command(BaseCommand):
    help = "استخراج و ذخیره توییت‌ها از TwitterAPI.io"

    def add_arguments(self, parser):
        parser.add_argument("search", type=str, help="عبارت جستجو")
        parser.add_argument("--max_tweets", type=int, default=10, help="حداکثر تعداد توییت‌ها")

    def handle(self, *args, **options):
        search = options["search"]
        max_tweets = options["max_tweets"]
        client = TwitterClient()
        tweets = client.fetch_and_save_tweets(search, max_tweets)
        self.stdout.write(self.style.SUCCESS(f"با موفقیت {len(tweets)} توییت ذخیره شد"))