from django_cron import CronJobBase, Schedule
from . import models

import time
import logging

class FetchEntries(CronJobBase):
    RUN_EVERY_MINS = 10

    schedule = Schedule(run_every_mins = RUN_EVERY_MINS)
    code = 'feed.FetchEntries'
    def do(self):
        for feed in models.Feed.objects.filter(enabled=True):
            feed.fetch()
