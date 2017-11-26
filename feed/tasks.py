from . import models
import time
import logging
log = logging.getLogger(__name__)
from django.conf import settings
from celery import shared_task
from django.core.cache import cache
from celery.five import monotonic
from contextlib import contextmanager
import functools

LOCK_EXPIRE = 60*60

@contextmanager
def django_lock(lock_id, oid):
    timeout_at = monotonic() + LOCK_EXPIRE - 3
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        if monotonic() < timeout_at:
            cache.delete(lock_id)

def once(func):
    @functools.wraps(func)
    def lock_once(*args, **kwargs):
        lock_id = ':celery_lock:once:' + func.__name__
        with django_lock(lock_id, 1) as acquired:
            if acquired:
                return func(*args, **kwargs)
    return lock_once

@shared_task
@once
def fetch_feeds():
    for feed in models.Feed.objects.filter(enabled=True):
        feed.fetch()
