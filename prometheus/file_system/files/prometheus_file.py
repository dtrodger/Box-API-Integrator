from __future__ import annotations
from typing import Optional, Tuple, List, Dict, Union
import os
import datetime
import logging
import shutil
import uuid

import boxsdk
import aioredis
import attr

import prometheus.box_client as prometheus_box_client
import prometheus.redis_client as prometheus_redis_client
from prometheus import slot
from prometheus import exception as prometheus_exception
from prometheus import aiofiles as prometheus_aiofiles


log = logging.getLogger(__name__)


@attr.s(slots=True, auto_attribs=True)
class PrometheusFile(slot.SlotSerializer):
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

    def file_directory_path_from_file_path(self):
        if not self.file_directory_path:
            self.file_directory_path = os.path.dirname(self.file_path)

        return self.file_directory_path_from_file_path

    def file_name_from_file_path(self):
        if not self.file_name:
            self.file_name = os.path.basename(self.file_path)

        return self.file_name

    @property
    def cache_box_upload_folder_path_id_key(self) -> Optional[str]:
        redis_key = None
        if self.box_upload_folder_path is not None and self.box_upload_user_id:
            redis_key = f"box-folder-path-id:box-user-{self.box_upload_user_id}:{self.box_upload_folder_path}"

        return redis_key

    @property
    def cache_box_upload_user_email_id_key(self) -> Optional[str]:
        redis_key = None
        if self.box_upload_user_email:
            redis_key = f"box-user-email-id:{self.box_upload_user_email}"

        return redis_key

    def check_input_complete(self) -> bool:
        input_complete = False
        if self.input_complete:
            input_complete = True

        elif (
            self.elapsed_since_st_size_diff_from_cache
            < self.min_elapsed_for_input_complete
        ):
            input_complete = True
            self.input_complete = input_complete

        return input_complete

    def check_min_elapsed_for_box_upload(self) -> bool:
        can_upload = False
        if (
            not self.attempted_upload_to_box_on
            or self.elapsed_since_box_upload_attempt
            > self.min_elapsed_for_box_upload_attempt
        ):
            can_upload = True

        return can_upload

    def check_ready_for_delete(self) -> bool:

        ready_for_delete = False
        elapsed_since_directory_entry_on = self.elapsed_since_directory_entry_on
        if (
            not self.deleted
            and elapsed_since_directory_entry_on
            and elapsed_since_directory_entry_on > self.min_elapsed_for_delete
        ):
            ready_for_delete = True

        self.ready_for_delete = ready_for_delete

        log.debug(f"{self} ready for delete {ready_for_delete}")

        return ready_for_delete

    async def create_on_disk(self, override_existing: bool = True) -> bool:
        async def create():
            async with prometheus_aiofiles.open(self.file_path, mode="w") as fh:
                pass

        created = False
        try:
            if os.path.exists(self.file_path):
                if override_existing:
                    await create()
                    created = True
            else:
                await create()
                created = True
        except Exception as e:
            log.error(f"{self} failed create file with {str(e)}")

        if created:
            log.debug(f"created file {self} on disk")

        return created

    async def current_stats(self) -> Tuple[Optional[Dict], datetime.datetime]:
        st_check_on = datetime.datetime.utcnow()
        stats = None

        if self.file_path and os.path.exists(self.file_path):
            try:
                stats = await prometheus_aiofiles.os.stat(self.file_path)
                log.debug(f"{self} found stats {stats} on {st_check_on}")
            except Exception as e:
                log.error(f"{self} stats check failed with {str(e)}")

        return stats, st_check_on

    async def current_st_creation_time_diff_from_cache(
        self, stats: Dict = None
    ) -> Dict:

        return await self.current_st_diff_from_cache("creation_time", stats)

    async def current_st_diff_from_cache(
        self, stat: Union[str, bool], stats: Dict = None
    ) -> Dict:
        def build_st_diff_dict(previous, current):
            return {"previous": previous, "current": current}

        if not stats:
            stats, stats_checked_on = await self.current_stats()

        st_diff_from_cache = {}

        if stats:
            if stat == "creation_time" or stat is True:
                new_st_creation_time = stats[9]
                if self.st_creation_time != new_st_creation_time:
                    st_diff_from_cache["creation_time"] = build_st_diff_dict(
                        self.st_creation_time, new_st_creation_time
                    )
                    self.st_creation_time = new_st_creation_time

            elif stat == "last_accessed_time" or stat is True:
                new_st_last_accessed_time = stats[7]
                if self.st_last_accessed_time != new_st_last_accessed_time:
                    st_diff_from_cache["last_accessed_time"] = build_st_diff_dict(
                        self.st_last_accessed_time, new_st_last_accessed_time
                    )
                    self.st_last_accessed_time = new_st_last_accessed_time

            elif stat == "last_modified_time" or stat is True:
                new_st_last_modified_time = stats[8]
                if self.st_last_modified_time != new_st_last_modified_time:
                    st_diff_from_cache["last_modified_time"] = build_st_diff_dict(
                        self.st_last_modified_time, new_st_last_modified_time
                    )
                    self.st_size = new_st_last_modified_time

            elif stat == "size" or stat is True:
                new_st_size = stats[6]
                if self.st_size != new_st_size:
                    st_diff_from_cache["size"] = build_st_diff_dict(
                        self.st_size, new_st_size
                    )
                    self.st_size = new_st_size

        self.st_size_diff_from_cache_on = datetime.datetime.utcnow()

        log.debug(f"{self} st_{stat}_diff_from_cache {st_diff_from_cache}")

        return st_diff_from_cache

    async def current_st_last_accessed_time(self, stats: Dict = None) -> Dict:

        return await self.current_st_diff_from_cache("last_accessed_time", stats)

    async def current_st_last_modified_time_diff_from_cache(
        self, stats: Dict = None
    ) -> Dict:

        return await self.current_st_diff_from_cache("last_modified_time", stats)

    async def current_st_size_diff_from_cache(self, stats: Dict = None) -> Dict:

        return await self.current_st_diff_from_cache("size", stats)

    async def delete(self) -> bool:
        deleted = False
        try:
            await prometheus_aiofiles.os.remove(self.file_path)
            deleted = True
            log.debug(f"{self} deleted {deleted}")
            self.deleted = deleted
            self.deleted_on = datetime.datetime.utcnow()
            self.file_path = None
            self.current_directory = None
        except Exception as e:
            log.error(f"failed {self} delete with error {str(e)}")

        return deleted

    @property
    def elapsed_since_box_upload_attempt(self) -> Optional[float]:
        elapsed_secs = None
        if self.attempted_upload_to_box_on:
            elapsed_secs = (
                datetime.datetime.utcnow() - self.attempted_upload_to_box_on
            ).total_seconds()

        return elapsed_secs

    @property
    def elapsed_since_initial_monitor(self) -> Optional[float]:
        elapsed_secs = None
        if self.initial_monitor_on:
            elapsed_secs = (
                datetime.datetime.utcnow() - self.initial_monitor_on
            ).total_seconds()

        return elapsed_secs

    @property
    def elapsed_since_st_check(self) -> Optional[float]:
        elapsed_secs = None
        if self.st_check_on:
            elapsed_secs = (
                datetime.datetime.utcnow() - self.st_check_on
            ).total_seconds()

        return elapsed_secs

    @property
    def elapsed_since_st_size_diff_from_cache(self) -> Optional[float]:
        elapsed_secs = None
        if self.st_size_diff_from_cache_on:
            elapsed_secs = (
                datetime.datetime.utcnow() - self.st_size_diff_from_cache_on
            ).total_seconds()

        return elapsed_secs

    @property
    def elapsed_since_directory_entry_on(self) -> Optional[float]:
        elapsed_secs = None
        if self.directory_entry_on:
            elapsed_secs = (
                datetime.datetime.utcnow() - self.directory_entry_on
            ).total_seconds()

        return elapsed_secs

    @property
    def exists(self) -> bool:
        return os.path.exists(self.file_path)

    @property
    def file_name_prefix(self):
        return self.file_name.split(".")[0]

    async def get_box_upload_folder_path_id_from_cache(
        self, redis_client: aioredis.Redis
    ) -> str:

        redis_value = None
        if self.cache_box_upload_folder_path_id_key:
            redis_value = await redis_client.get(
                self.cache_box_upload_folder_path_id_key
            )

        if redis_value:
            log.debug(
                f"got redis box upload folder path key {self.cache_box_upload_folder_path_id_key}"
            )
        else:
            log.debug(
                f"failed to get box upload folder path key {self.cache_box_upload_folder_path_id_key} in redis"
            )

        return redis_value

    async def get_box_user_email_id_from_cache(self, redis_client: aioredis.Redis):
        redis_value = None
        if self.cache_box_upload_user_email_id_key:
            redis_value = await prometheus_redis_client.get(
                redis_client, self.cache_box_upload_user_email_id_key
            )

        if redis_value:
            log.debug(
                f"got redis box user email association from key {self.cache_box_upload_user_email_id_key}"
            )
        else:
            log.debug(
                f"failed to box user email association from key {self.cache_box_upload_user_email_id_key} in redis"
            )

        return redis_value

    async def is_ready_for_box_upload(self) -> bool:
        stats, st_check_on = await self.current_stats()

        ready_for_upload = False
        if (
            not self.deleted
            and not self.current_st_size_diff_from_cache(stats)
            and self.check_input_complete()
            and self.check_min_elapsed_for_box_upload()
        ):
            ready_for_upload = True
            self.ready_for_upload = ready_for_upload

        log.debug(f"{self} is ready for upload {ready_for_upload}")

        return ready_for_upload

    async def move_directories(
        self, new_directory_path: str, rename_dup=True
    ) -> bool:
        moved = False
        try:
            if os.path.exists(os.path.join(new_directory_path, self.file_name)):
                if rename_dup:
                    new_file_name = f"{int(datetime.datetime.utcnow().timestamp())}-{self.file_name}"
                    renamed = await self.rename_self(new_file_name)
                    if not renamed:
                        raise prometheus_exception.PrometheusFileError(
                            f"{self} failed to remain {self.file_path} to {new_file_name}"
                        )
                else:
                    raise prometheus_exception.PrometheusFileError(f"{self} duplicate name")

            shutil.move(self.file_path, new_directory_path)
            log.debug(f"moved {self} from {self.file_path} to {new_directory_path}")
            self.file_path = new_directory_path
            self.directory_entry_on = datetime.datetime.utcnow()

            self.current_directory = os.path.split(new_directory_path)[-1]
            moved = True
        except Exception as e:
            log.error(
                f"failed move {self} from {self.file_path} to {new_directory_path} with {str(e)}"
            )

        return moved

    async def read_line(self):
        try:
            async with prometheus_aiofiles.open(self.file_path, "r") as fh:
                line = await fh.readline()
                line = line.strip("\n")
            log.debug(f"{self} read line {line}")
        except Exception as e:
            log.error(f"{self} failed to read line with {e}")

        return line

    async def read_lines(self):
        lines = list()
        try:
            async with prometheus_aiofiles.open(self.file_path, "r") as fh:
                async for line in fh:
                    lines.append(line.replace("\r", "").replace("\n", ""))

            log.debug(f"{self} read lines {lines}")
        except Exception as e:
            log.error(f"{self} failed to read lines with {e}")

        return lines

    async def rename_self(self, new_file_name: str) -> bool:
        renamed = False
        new_file_path = os.path.join(
            os.path.dirname(__file__), self.file_directory_path, new_file_name
        )

        try:
            old_file_path = self.file_path
            prometheus_aiofiles.os.rename(self.file_path, new_file_path)
            self.file_path = new_file_path
            self.file_name = new_file_name
            renamed = True
            log.debug(f"{self} renamed form {old_file_path} to {new_file_path}")

        except Exception as e:
            log.error(f"failed rename {self} to {new_file_path} with {str(e)}")

        return renamed

    async def set_box_upload_user_from_cache(
        self,
        box_client: prometheus_box_client.prometheusBoxClient,
        redis_client: aioredis.Redis,
    ):

        set_box_upload_user = False

        if self.box_upload_user_email:

            redis_value = await self.get_box_user_email_id_from_cache(redis_client)

            if redis_value:
                try:
                    box_user = box_client.user(redis_value)
                    if not box_user.response_object:
                        box_user = box_client.search_user_by_primary_email(
                            self.box_upload_user_email
                        )

                except Exception as e:
                    box_user = None
                    log.error(
                        f"{box_client} failed to get user {self.box_upload_user_id}"
                    )

                if box_user.response_object:
                    self.set_box_upload_user_info_from_user(box_user)
                    set_box_upload_user = True
                    log.debug(
                        f"set box upload user id from cache {self.cache_box_upload_user_email_id_key}"
                    )
                else:
                    log.info(
                        f"{self} failed to associate {self.box_upload_user_email} to Box user"
                    )

            else:

                set_box_upload_user = await self.set_box_upload_user_to_cache(
                    box_client, redis_client
                )

        return set_box_upload_user

    def set_box_upload_user_info_from_user(self, box_user: boxsdk.object.user.User):
        self.box_upload_user = box_user
        self.box_upload_user_email = box_user.response_object["login"]
        self.box_upload_user_id = box_user.response_object["id"]
        log.debug(f"{self} set box upload user info from {box_user}")

    async def set_box_upload_user_to_cache(
        self,
        box_client: prometheus_box_client.prometheusBoxClient,
        redis_client: aioredis.Redis,
    ) -> bool:

        set_association = False

        box_user = box_client.search_user_by_primary_email(self.box_upload_user_email)

        if box_user:
            self.set_box_upload_user_info_from_user(box_user)

            set_association = await prometheus_redis_client.set_box_user_email_id_association(
                redis_client, self.box_upload_user_email, self.box_upload_user_id
            )
            log.debug(
                f"{self} associated {self.box_upload_user_email} to Box user ID {self.box_upload_user_id} and set to redis"
            )
        else:
            log.debug(
                f"{self} failed to associate {self.box_upload_user_email} to Box user ID"
            )

        return set_association

    async def update_stats(
        self,
        stats: Optional[Dict] = None,
        st_check_on: Optional[datetime.datetime] = None,
    ) -> None:

        if not stats:
            stats, st_check_on = await self.current_stats()

        if stats:
            self.st_check_on = st_check_on
            self.st_size = stats[6]
            self.st_last_accessed_time = stats[7]
            self.st_last_modified_time = stats[8]
            self.st_creation_time = stats[9]

    async def upload_to_box(
        self,
        box_client: prometheus_box_client.prometheusBoxClient,
        box_upload_folder_id: Optional[str] = None,
        as_box_upload_user: Optional[bool] = False,
        box_user: Optional[boxsdk.object.user.User] = None,
        to_box_upload_folder: Optional[bool] = True,
    ) -> Union[boxsdk.object.file.File, str]:

        try:
            self.attempted_upload_to_box_on = datetime.datetime.utcnow()

            if not self.st_size:
                await self.update_stats()

            if as_box_upload_user:
                box_user = self.box_upload_user

            if to_box_upload_folder:
                box_upload_folder_id = self.box_upload_folder_id

            if self.st_size < 50000000:
                log.debug(f"{self} attempting simple Box upload")

                if box_user:
                    box_file = (
                        box_client.as_user(box_user)
                        .folder(box_upload_folder_id)
                        .upload(self.file_path)
                    )
                else:
                    box_file = box_client.folder(box_upload_folder_id).upload(
                        self.file_path
                    )
            else:
                log.debug(f"{self} attempting chunked Box upload")

                if box_user:
                    chunked_uploader = (
                        box_client.as_user(box_user)
                        .folder(box_upload_folder_id)
                        .get_chunked_uploader(self.file_path)
                    )
                else:
                    chunked_uploader = box_client.folder(
                        box_upload_folder_id
                    ).get_chunked_uploader(self.file_path)

                box_file = chunked_uploader.start()

            log.debug(
                f"{self} uploaded to Box with {box_client} to folder {box_upload_folder_id} and created a Box file with ID {box_file.id}"
            )

            self.box_file = box_file
            self.box_file_id = box_file.id
            self.uploaded_to_box = True
            self.uploaded_to_box_on = datetime.datetime.now()
            uploaded = box_file
        except Exception as e:
            uploaded = str(e)
            log.error(
                f"{self} failed upload to box with client {box_client} to folder {box_upload_folder_id} failed with {uploaded}"
            )

        return uploaded

    def upload_to_box_failed(self) -> bool:
        upload_to_box_failed = False
        if (
            datetime.datetime.utcnow() - self.initial_monitor_on
        ).seconds > self.min_elapsed_for_box_upload_fail and not self.deleted:
            upload_to_box_failed = True

        return upload_to_box_failed

    async def write_line(self, line: str):
        wrote = False

        try:
            async with prometheus_aiofiles.open(self.file_path, "a+") as fh:
                await fh.write(line)

            wrote = True
            log.debug(f"{self} wrote line {line}")

        except Exception as e:
            log.error(f"{self} failed to write line with {e}")

        return wrote

    async def write_new_line(self, line: str):

        return await self.write_line(f"\n{line}")

    async def write_lines(self, lines: List):
        wrote = False
        lines = [f"{line}\n" for line in lines]
        try:
            async with prometheus_aiofiles.open(self.file_path, "a+") as fh:
                await fh.writelines(lines)

            wrote = True
            log.debug(f"{self} wrote lines {lines}")

        except Exception as e:
            log.error(f"{self} failed to write lines with {e}")

        return wrote
