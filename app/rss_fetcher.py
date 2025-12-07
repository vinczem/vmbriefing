import feedparser
import time
from datetime import datetime, timedelta
import email.utils

class RSSFetcher:
    def __init__(self, feeds, hours):
        self.feeds = feeds
        self.hours = hours

    def fetch_news(self):
        news_items = []
        cutoff_time = datetime.now() - timedelta(hours=self.hours)
        
        for feed_url in self.feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    # Try to parse published date
                    published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                    if published_parsed:
                        published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
                        if published_dt > cutoff_time:
                            news_items.append({
                                'title': entry.title,
                                'link': entry.link,
                                'summary': entry.get('summary', ''),
                                'source': feed.feed.get('title', feed_url),
                                'published': published_dt
                            })
            except Exception as e:
                print(f"Error fetching feed {feed_url}: {e}")
                
        return news_items
