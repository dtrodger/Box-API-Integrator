from __future__ import annotations
import logging
from typing import Dict, Optional
import datetime
import uuid

import yaml
import attr
import boxsdk

from prometheus.file_system.files import prometheus_file


log = logging.getLogger(__name__)


@attr.s(slots=True, auto_attribs=True)
class YMLFile(prometheus_file.PrometheusFile):
    file_path: str = None
    attempted_upload_to_box_on: Optional[datetime.datetime] = None
    box_file: Optional[boxsdk.object.file.File] = None
    box_file_id: Optional[str] = None
    box_upload_folder_id: Optional[str] = None
    box_upload_folder_path: Optional[str] = None
    box_upload_user: Optional[boxsdk.object.user.User] = None
    box_upload_user_email: Optional[str] = None
    box_upload_user_id: Optional[str] = None
    current_directory: Optional[str] = None
    deleted: bool = False
    deleted_on: bool = False
    directory_entry_on: Optional[datetime.datetime] = None
    file_directory_path: Optional[str] = None
    file_name: Optional[str] = None
    id: uuid.UUID = uuid.uuid4()
    initial_monitor_on: Optional[datetime.datetime] = None
    input_complete: bool = False
    min_elapsed_for_box_upload_attempt: int = 1
    min_elapsed_for_box_upload_fail: int = 3
    min_elapsed_for_delete: int = 0
    min_elapsed_for_input_complete: int = 1
    ready_for_delete: bool = False
    ready_for_upload: bool = False
    st_check_on: Optional[datetime.datetime] = None
    st_creation_time: Optional[int] = None
    st_last_accessed_time: Optional[int] = None
    st_last_modified_time: Optional[int] = None
    st_size: Optional[int] = None
    st_size_diff_from_cache_on: Optional[datetime.datetime] = None
    uploaded_to_box: bool = False
    uploaded_to_box_on: datetime = None
    cached_disk_self: dict = None

    @property
    def disk_self(self):
        loaded_dict = None

        if self.exists:
            with open(self.file_path) as fh:
                loaded_dict = yaml.load(fh, Loader=yaml.FullLoader)

        return loaded_dict

    def set_disk_self_from_cache(self):
        set_self = False
        if self.exists:
            with open(self.file_path, "w") as fh:
                yaml.dump(self.cached_disk_self, fh, default_flow_style=False)
            set_self = True

        return set_self

    def __getitem__(self, key, recache_disk_self: bool = False):
        if recache_disk_self:
            self.cached_disk_self = self.disk_self

        return self.cached_disk_self[key]

    def __setitem__(self, key, value, set_disk_self: bool = True):
        self.cached_disk_self[key] = value
        if set_disk_self:
            self.set_disk_self_from_cache()

        return True
