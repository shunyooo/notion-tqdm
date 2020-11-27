import inspect
import json
import logging
import threading
from datetime import datetime, timezone
from time import time

import pytz
import requests
from IPython import get_ipython
from notion.block import TextBlock
from notion.client import NotionClient
from notion.collection import NotionDate
from tqdm import tqdm
from tzlocal import get_localzone

from .constants import (
    POST_INTERVAL_SEC,
    REQUIRED_COLUMNS,
    REQUIRED_STATUS_OPTIONS,
    Status,
)


def get_localzone_name():
    local_tz = get_localzone()
    return datetime.now(local_tz).tzname()


class notion_tqdm(tqdm):
    _is_configured = False
    post_interval_sec = POST_INTERVAL_SEC
    timezone = get_localzone_name()
    common_props = {}

    @classmethod
    def _get_table_schema_prop_names(cls):
        return set(
            [prop["name"] for prop in cls.table_view.collection.get_schema_properties()]
        )

    @classmethod
    def _validate_table_shcema(cls):
        # Check table view type
        if "collection" not in dir(cls.table_view):
            raise Exception(
                f"table_view is not referring to the table correctly. Make sure you are setting a table link that is not a page link."
            )
        # Check required columns
        table_view_columns = cls._get_table_schema_prop_names()
        missing_columns = REQUIRED_COLUMNS - table_view_columns
        if len(missing_columns) > 0:
            raise Exception(
                f"There are missing columns in the table: {missing_columns}. Did you duplicate this view?: https://www.notion.so/syunyo/notion-tqdm-template-7d2d53595e774c9eb7a020e00fd81fab"
            )
        # Check select options
        table_status_options = set(
            [
                op["value"]
                for op in cls.table_view.collection.get_schema_property("status")[
                    "options"
                ]
            ]
        )
        missing_options = REQUIRED_STATUS_OPTIONS - table_status_options
        if len(missing_options) > 0:
            raise Exception(
                f"There are missing options in the status columns: {missing_options}. Did you duplicate this view?: https://www.notion.so/syunyo/notion-tqdm-template-7d2d53595e774c9eb7a020e00fd81fab"
            )

    @classmethod
    def set_config(
        cls, token_v2, table_url, email=None, timezone=None, post_interval_sec=None
    ):
        # Common Config
        if timezone is not None:
            cls.timezone = timezone
        if post_interval_sec is not None:
            ls.post_interval_sec = post_interval_sec
        cls._timezone_pytz = pytz.timezone(cls.timezone)
        # Notion Config
        cls.client = NotionClient(token_v2=token_v2)
        if email is not None:
            cls.client.set_user_by_email(email)
        cls.table_view = cls.client.get_block(table_url)
        # Validation
        cls._validate_table_shcema()
        cls._is_configured = True

    @classmethod
    def set_common_props(cls, **kwargs):
        cls.common_props = kwargs
        missing_columns = set(kwargs) - cls._get_table_schema_prop_names()
        if len(missing_columns) > 0:
            logging.error(
                f"There are missing columns in the table: {missing_columns}."
            )

    def localize_timestamp(self, timestamp):
        utc_datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return utc_datetime.astimezone(notion_tqdm._timezone_pytz)

    def _update_row(self):
        if not notion_tqdm._is_configured:
            logging.warning(
                "notion_tqdm does not seem to be set yet. call notion_tqdm.set_config and configure it.\nrefer to https://github.com/shunyooo/notion-tqdm#usage"
            )
            return
        if self._row_creating:
            return
        if self.row is None and not self._row_creating:
            self._row_creating = True
            self.row = notion_tqdm.table_view.collection.add_row()
            self._row_creating = False
            for c, v in notion_tqdm.common_props.items():
                self.row.set_property(c, v)
        if self.row is not None:
            # Base props
            # TODO: Difference only updates
            now = time()
            row = self.row
            row.total = self.total
            row.name = self.desc
            row.status = self.status
            row.value = self.n
            row.start_timestamp = self.start_t
            row.update_timestamp = now
            row.timerange = NotionDate(
                self.localize_timestamp(self.start_t),
                self.localize_timestamp(now),
                timezone=notion_tqdm.timezone,
            )
            row.elapsed_sec = now - self.start_t
            # Custom props
            # TODO: Set the props that have been skipped during creating.
            for c, v in self.custom_props.items():
                row.set_property(c, v)
            # Add Text Blocks
            for text in self._pending_texts:
                self.row.children.add_new(TextBlock).title = text
            self._pending_texts = []

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

    def display(self, msg=None, pos=None, status=None, force=False):
        force = status is not None or force
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
        self.custom_props = {}
        self._pending_texts = []

    def __iter__(self, *args, **kwargs):
        try:
            for obj in super().__iter__(*args, **kwargs):
                yield obj
        except:
            self.display(status=Status.error)
            raise

    def add_text(self, text, force=False):
        self._pending_texts.append(text)
        self.display(force)

    def update_props(self, force=False, **kwags):
        self.custom_props = kwags
        self.display(force)

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