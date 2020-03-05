from __future__ import annotations
from typing import Optional, List, AnyStr
import os
import logging

import watchdog.events as wd_events

from prometheus.file_system.files import prometheus_file


log = logging.getLogger(__name__)


class PrometheusDirectory:
    """
    Implements a Watchdog file system event handler

    Watchdog
    https://pythonhosted.org/watchdog/

    Reference line 317 watchdog.events.FileSystemEventHandler
    https://github.com/gorakhargosh/watchdog/blob/master/src/watchdog/events.py
    """

    prometheus_file_type = prometheus_file.PrometheusFile
    directory_event_types = [
        wd_events.DirDeletedEvent,
        wd_events.DirModifiedEvent,
        wd_events.DirCreatedEvent,
        wd_events.DirMovedEvent,
    ]
    file_event_types = [
        wd_events.FileDeletedEvent,
        wd_events.FileModifiedEvent,
        wd_events.FileCreatedEvent,
        wd_events.FileMovedEvent,
    ]

    def __init__(
        self,
        file_system_path: AnyStr,
        monitor_prometheus_files_on_init: bool = True,
        ignored_files: Optional[list] = None,
        ignored_extensions: Optional[list] = None,
        ignored_directories: Optional[list] = None,
        included_file_prefix: Optional[list] = None,
        included_directories: Optional[list] = None,
        prometheus_files: Optional[list] = None
    ) -> PrometheusDirectory:

        if not prometheus_files:
            prometheus_files = list()

        if not ignored_files:
            ignored_files = list()

        if not ignored_extensions:
            ignored_extensions = list()

        if not ignored_directories:
            ignored_directories = list()

        if not included_file_prefix:
            included_file_prefix = list()

        if not included_directories:
            included_directories = list()

        self.file_system_path = file_system_path
        self.prometheus_files = prometheus_files
        self.dir_alias = os.path.split(self.file_system_path)[-1]
        self.included_directories = included_directories
        self.included_file_prefix = included_file_prefix
        self.ignored_directories = ignored_directories
        self.ignored_files = ignored_files
        self.ignored_extensions = ignored_extensions

        if monitor_prometheus_files_on_init:
            self.monitor_prometheus_files()

    def __repr__(self) -> AnyStr:
        return f"<{type(self).__name__}-{self.dir_alias}>"

    @property
    def prometheus_files_names(self) -> List:
        names = [prometheus_file.file_name for prometheus_file in self.prometheus_files]
        log.debug(f"{str(self)} files names {names}")

        return names

    @property
    def prometheus_files_paths(self) -> List:
        paths = [prometheus_file.file_path for prometheus_file in self.prometheus_files]
        log.debug(f"{str(self)} files paths {paths}")

        return paths

    @property
    def deleteable_prometheus_files(self) -> List[prometheus_file.prometheusFile]:
        deleteable_prometheus_files = list()
        for prometheus_file in self.prometheus_files:
            if prometheus_file.check_ready_for_delete():
                log.debug(f"monitored deletable file {str(prometheus_file)}")
                deleteable_prometheus_files.append(prometheus_file)

        return deleteable_prometheus_files

    @property
    def file_system_event_type_handler_map(self):
        return {
            wd_events.DirCreatedEvent: self._handle_dir_created_event,
            wd_events.DirDeletedEvent: self._handle_dir_deleted_event,
            wd_events.DirModifiedEvent: self._handle_dir_modified_event,
            wd_events.DirMovedEvent: self._handle_dir_moved_event,
            wd_events.FileCreatedEvent: self._handle_file_created_event,
            wd_events.FileDeletedEvent: self._handle_file_deleted_event,
            wd_events.FileModifiedEvent: self._handle_file_modified_event,
            wd_events.FileMovedEvent: self._handle_file_moved_event,
            wd_events.FileSystemMovedEvent: self._handle_file_system_moved_event,
        }

    def validate_file_path(self, file_path: AnyStr) -> bool:
        valid = True

        split_file_path = os.path.split(file_path)
        file_name = split_file_path[-1]
        file_name_prefix, file_extension = os.path.splitext(file_name)

        if file_name in self.ignored_files or file_extension in self.ignored_extensions:
            log.debug(f"{self} found invalid file with name {file_name}")
            valid = False

        if valid and self.included_file_prefix:
            for included_file_prefix in self.included_file_prefix:
                if included_file_prefix in file_name_prefix.lower():
                    log.debug(f"{self} found invalid file with name {file_name} and invalid prefix {included_file_prefix}")
                    break
            else:
                valid = False

        if valid and self.included_directories:
            for included_directory in self.included_directories:
                valid_directory = False
                for directory in split_file_path[0].split(os.sep):
                    if included_directory == directory:
                        log.debug(
                            f"{self} found invalid file with name {file_name} and directory {directory} match included directory")
                        valid_directory = True
                        break
                if valid_directory:
                    break
            else:
                log.debug(
                    f"{self} found invalid file with name {file_name} is not in valid directory")
                valid = False

        log.debug(f"{self} found file with name {file_name} has valid file path {valid}")

        return valid

    def validate_directory_path(self, directory_path: AnyStr) -> bool:
        valid = False
        directory_path_items = os.path.split(directory_path)
        for directory_path_item in directory_path_items:
            if directory_path_item in self.ignored_directories:
                log.debug(f"event with directory path {directory_path} in included directories")
                break
        else:
            valid = True

        log.debug(f"{self} validated directory path for event with path {directory_path} to {valid}")

        return valid

    def validate_directory_event_for_handlers(
        self, event: wd_events.FileSystemEvent
    ) -> bool:
        valid = None

        if type(event) in self.directory_event_types:
            valid = self.validate_directory_path(event.src_path)

        if valid is None:
            log.debug(f"{self} passing validate event {event} because not directory event")
        else:
            log.debug(f"{self} validated directory event {event} with {valid}")

        return valid

    def validate_file_event_for_handlers(
        self, event: wd_events.FileSystemEvent
    ) -> bool:
        valid = None

        if type(event) in self.file_event_types:
            valid = self.validate_file_path(event.src_path)

        if valid is None:
            log.debug(f"{self} passing validate event {event} because not file event")
        elif valid is False:
            log.debug(f"{self} validated file event {event} with {valid}")

        return valid

    def validate_event_for_handlers(self, event: wd_events.FileSystemEvent) -> bool:
        valid = True
        valid_directory_event_for_handling = self.validate_directory_event_for_handlers(
            event
        )

        if valid_directory_event_for_handling is False:
            valid = False

        elif valid_directory_event_for_handling is None:

            valid_file_event_for_handling = self.validate_file_event_for_handlers(event)

            if valid_file_event_for_handling is False:
                valid = False

        log.debug(f"{self} validated event {event} with {valid}")

        return valid

    def dispatch(self, event: wd_events.FileSystemEvent):
        """
        Watchdog file system event dispatcher. Route FileSystemEvents to event handlers based on their type.
        """

        valid_event_for_handlers = self.validate_event_for_handlers(event)

        if not valid_event_for_handlers:
            log.debug(
                f"invalid event {str(event)} for handling at path {event.src_path}"
            )

        else:
            log.debug(f"{self} routing event {event} to handlers")
            self._handle_any_file_system_event(event)

            return self.file_system_event_type_handler_map[type(event)](event)
    def _handle_any_file_system_event(self, event: wd_events.FileSystemEvent) -> None:
        """
        Watchdog FileSystemEvent handler.
        """

        log.debug(f"{str(self)} monitored file system event for {event.src_path}")

    def _handle_file_system_moved_event(
        self, event: wd_events.FileSystemMovedEvent
    ) -> None:
        """
        Watchdog FileSystemMovedEvent handler.
        """

        log.debug(f"{str(self)} monitored file system moved {event.src_path}")

    def _handle_file_deleted_event(self, event: wd_events.FileDeletedEvent) -> None:
        """
        Watchdog FileDeletedEvent handler.
        """

        prometheus_file = self._prometheus_file_from_event(event)
        if prometheus_file:
            log.debug(f"{str(self)} monitored file deleted {prometheus_file.file_name}")

            self.prometheus_files.remove(prometheus_file)
            log.debug(
                f"removed {str(prometheus_file)} from directory {str(self)} prometheus file cache"
            )
        else:
            file_name = self._event_path_postfix(event)
            log.debug(
                f"{str(self)} monitored {file_name} removal but file not found in prometheus files"
            )

    def _handle_file_modified_event(self, event: wd_events.FileModifiedEvent) -> None:
        """
        Watchdog FileModifiedEvent handler.
        """

        # TODO handle file name changes w/in self.prometheus_files
        file_name = self._event_path_postfix(event)
        log.debug(f"{str(self)} monitored file modified {file_name}")

    def _handle_file_created_event(self, event: wd_events.FileCreatedEvent) -> None:
        """
        Watchdog FileCreatedEvent handler.
        """

        file_name = self._event_path_postfix(event)
        log.debug(f"{str(self)} monitored new file {file_name}")

        try:
            prometheus_file = self.prometheus_file_type(file_name=file_name, file_path=event.src_path)
            self.prometheus_files.append(prometheus_file)
            log.debug(f"added {str(prometheus_file)} to directory {str(self)} prometheus file cache")
        except Exception as e:
            log.error(f"failed to construct prometheus file with path {str(event.src_path)}")

    def _handle_file_moved_event(self, event: wd_events.FileMovedEvent) -> None:
        """
        Watchdog FileMovedEvent handler.
        """

        file_name = self._event_path_postfix(event)
        log.debug(f"{str(self)} monitored file move {file_name}")

    def _handle_dir_deleted_event(self, event: wd_events.DirDeletedEvent) -> None:
        """
        Watchdog DirDeletedEvent handler.
        """

        directory = self._event_path_postfix(event)
        log.debug(f"{str(self)} monitored directory deleted {directory}")

    def _handle_dir_modified_event(self, event: wd_events.DirDeletedEvent) -> None:
        """
        Watchdog DirDeletedEvent handler.
        """

        directory = self._event_path_postfix(event)
        log.debug(f"{str(self)} monitored directory modified {directory}")

    def _handle_dir_created_event(self, event: wd_events.DirCreatedEvent) -> None:
        """
        Watchdog DirCreatedEvent handler.
        """

        directory = self._event_path_postfix(event)
        log.debug(f"{str(self)} monitored directory created {directory}")

    def _handle_dir_moved_event(self, event: wd_events.DirMovedEvent) -> None:
        """
        Watchdog DirMovedEvent handler.
        """

        directory = self._event_path_postfix(event)
        log.debug(f"{str(self)} monitored directory moved {directory}")

    def monitor_prometheus_files(self) -> List[prometheus_file.prometheusFile]:
        new_prometheus_files = list()
        new_prometheus_file_detected = False

        for root, subdirs, files in os.walk(self.file_system_path):
            for file_name in files:

                file_path = os.path.join(root, file_name)

                if (
                    self.validate_file_path(file_path)
                    and file_path not in self.prometheus_files_paths
                ):
                    if not new_prometheus_file_detected:
                        new_prometheus_file_detected = True

                    try:
                        prometheus_file = self.prometheus_file_type(
                            file_name=file_name, file_path=file_path
                        )
                        log.debug(
                            f"new file {str(prometheus_file)} monitored for prometheus file cache in directory {str(self)}"
                        )

                        self.prometheus_files.append(prometheus_file)
                        new_prometheus_files.append(prometheus_file)
                    except Exception as e:
                        log.error(
                            f"failed to construct prometheus file with path {str(file_path)} with error {str(e)}"
                        )

        if not new_prometheus_file_detected:
            log.debug(f"no new files for prometheus cache monitored in directory {str(self)}")

        return new_prometheus_files

    def _prometheus_file_from_event(
        self, event: wd_events.FileSystemEvent
    ) -> Optional[prometheus_file.prometheusFile]:
        file_name = self._event_path_postfix(event)
        return self.prometheus_file_from_file_name(file_name)

    def prometheus_file_from_file_name(self, file_name: AnyStr) -> Optional[prometheus_file.prometheusFile]:
        for prometheus_file in self.prometheus_files:
            if prometheus_file.file_name == file_name:
                return prometheus_file

    @staticmethod
    def _event_path_postfix(event: wd_events.FileSystemEvent) -> AnyStr:
        return os.path.split(event.src_path)[-1]

    def remove_file(self, prometheus_file: prometheus_file.prometheusFile) -> bool:
        removed = False
        if prometheus_file in self.prometheus_files:
            self.prometheus_files.remove(prometheus_file)
            removed = True
            log.debug(f"removed {str(prometheus_file)} from {str(self)} prometheus files")
        else:
            log.debug(f"failed to remove {str(prometheus_file)} from {str(self)} prometheus files")

        return removed

    @property
    def uploadable_prometheus_files(self) -> List[prometheus_file.prometheusFile]:
        uploadable_prometheus_files = list()
        for prometheus_file in self.prometheus_files:
            if prometheus_file.is_ready_for_box_upload():
                uploadable_prometheus_files.append(prometheus_file)

        log.debug(f"uploadable prometheus files {uploadable_prometheus_files}")

        return uploadable_prometheus_files
