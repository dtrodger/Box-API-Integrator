from __future__ import annotations
import logging
from typing import Optional
import datetime

import lxml.etree as lxml_etree
import boxsdk
import attr
import uuid

from prometheus.file_system.files import prometheus_file


log = logging.getLogger(__name__)


@attr.s(slots=True, auto_attribs=True)
class XMLFile(prometheus_file.PrometheusFile):
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
    parsed_xml: Optional[lxml_etree.ElementTree()] = None
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

    def set_parsed_xml(self):
        self.parsed_xml = lxml_etree.parse(self.file_path)
