from django.db import models

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

import unicodedata
import feedparser
import datetime
import logging
import html2text
from django.utils import timezone
import time
import pytz
import re
from functools import reduce
class Subscriber(models.Model):
    name = models.TextField()
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Feed(models.Model):
    title = models.TextField()
    url = models.TextField(unique=True)
    last_fetch = models.DateTimeField()
    fetch_frequency = models.DurationField(default = datetime.timedelta(hours=1))
    subscribers = models.ManyToManyField(Subscriber)
    enabled = models.BooleanField()

    def age(self):
        return (timezone.now() - self.last_fetch).total_seconds()

    def __str__(self):
        return self.title

    def fetch(self, force = False):
        if self.last_fetch is not None:
            if self.last_fetch + self.fetch_frequency > timezone.now():
                return
        feed = feedparser.parse(self.url)
        if not feed.entries:
            # Failed to fetch
            log.error('Failed to fetch feed %s', self.url)
            return
        feedInstance = self
        parse_feed(feed, feedInstance)
        self.last_fetch = timezone.now()
        self.save()

class Entry(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    url = models.TextField(unique=True)
    title = models.TextField()
    blurb = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Entries'

    def __str__(self):
        return self.title
def wrap(text, width):
    # From http://code.activestate.com/recipes/148061/
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )

def parse_feed(feed, feedInstance):
    for item in feed.entries:
        published = datetime.datetime.fromtimestamp(time.mktime(item.published_parsed)).replace(tzinfo = pytz.utc)
        try:
            entry = Entry.objects.get(title=item.title)
        except Entry.DoesNotExist:
            title = item.get('title', item.link)
            blurb = wrap(
                    html2text.html2text(
                        item.get('description', '')
                        ),
                    80)
            entry = Entry(
                    title = item.title,
                    url = item.link,
                    feed = feedInstance,
                    blurb = blurb,
                    timestamp = published
                    )
            entry.save()
