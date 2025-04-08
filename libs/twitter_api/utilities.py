from datetime import datetime

def build_twitter_query(
    search=None, user=None, to=None, mentions=None, language=None,
    from_date=None, to_date=None, exact=False, verified=False,
    safe=False, exclude_retweets=False, media=False
):
    query_parts = []
    if search:
        query_parts.append(f'"{search}"' if exact else search)
    if user:
        query_parts.append(f"from:{user}")
    if to:
        query_parts.append(f"to:{to}")
    if mentions:
        query_parts.extend([f"@{m}" for m in mentions])
    if language:
        query_parts.append(f"lang:{language}")
    if from_date:
        query_parts.append(f"since:{from_date}")
    if to_date:
        query_parts.append(f"until:{to_date}")
    if verified:
        query_parts.append("filter:verified")
    if safe:
        query_parts.append("filter:safe")
    if exclude_retweets:
        query_parts.append("-filter:retweets")
    if media:
        query_parts.append("filter:media")
    return " ".join(query_parts) if query_parts else ""

def parse_twitter_date(date_str):
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601
        "%a %b %d %H:%M:%S %z %Y"  # Twitter قدیمی
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"فرمت تاریخ {date_str} پشتیبانی نمی‌شود")