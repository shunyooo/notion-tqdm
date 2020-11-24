import inspect
import json
import logging
import threading
from datetime import datetime, timezone
from time import time

import pytz
import requests
from IPython import get_ipython
from tqdm import tqdm

from notion.client import NotionClient
from notion.collection import NotionDate

from .constants import POST_INTERVAL_SEC, Status


class notion_tqdm(tqdm):
    @classmethod
    def set_config(
        cls, token_v2, table_url, email=None, timezone=None, post_interval_sec=None
    ):
        cls.timezone = timezone
        cls.post_interval_sec = (
            POST_INTERVAL_SEC if post_interval_sec is None else post_interval_sec
        )
        cls._timezone_pytz = pytz.timezone(timezone)
        cls.client = NotionClient(token_v2=token_v2)
        if email is not None:
            cls.client.set_user_by_email(email)
        cls.table_view = cls.client.get_block(table_url)
        if "collection" not in dir(cls.table_view):
            logging.warning(f"Failed to refer to the table: {cls.table_view}")

    def localize_timestamp(self, timestamp):
        utc_datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return utc_datetime.astimezone(notion_tqdm._timezone_pytz)

    def _update_row(self):
        if self._row_creating:
            return
        if self.row is None and not self._row_creating:
            self._row_creating = True
            self.row = notion_tqdm.table_view.collection.add_row()
            self._row_creating = False
        if self.row is not None:
            row = self.row
            row.total = self.total
            row.name = self.desc
            row.status = self.status
            row.value = self.n
            row.timerange = NotionDate(
                self.localize_timestamp(self.start_t),
                self.localize_timestamp(self.last_print_t),
                timezone=notion_tqdm.timezone,
            )
            row.elapsed_sec = self.last_print_t - self.start_t

    @property
    def _can_post(self):
        is_past = (
            self.last_post_time is None
            or (time() - self.last_post_time) > notion_tqdm.post_interval_sec
        )
        return not self._loading and is_past

    def _post_if_need(self, force):
        if self._can_post or force:
            self._loading = True
            try:
                self._update_row()
            except Exception as e:
                logging.warning(e)
            self.last_post_time = time()
            self._loading = False

    def display(self, msg=None, pos=None, status=None):
        force = status is not None
        self.status = Status.doing if status is None else status
        threading.Thread(
            name="_post_if_need", target=self._post_if_need, args=[force]
        ).start()

    def __init__(self, *args, **kwargs):
        self.row = None
        self.total = 0
        self.last_post_time = None
        self.status = Status.doing
        self._loading = False
        self._row_creating = False
        super().__init__(*args, **kwargs)
        self.sp = self.display

    def __iter__(self, *args, **kwargs):
        try:
            for obj in super().__iter__(*args, **kwargs):
                yield obj
        except:
            self.display(status=Status.error)
            raise

    def update(self, *args, **kwargs):
        try:
            super().update(*args, **kwargs)
        except:
            self.display(status=Status.error)
            raise

    def close(self, *args, **kwargs):
        super().close(*args, **kwargs)
        if self.total and self.n < self.total:
            self.display(status=Status.error)
        else:
            self.display(status=Status.done)