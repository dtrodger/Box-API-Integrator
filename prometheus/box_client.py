"""
Box Consulting Box Python SDK boxsdk.Client subclass
"""

from __future__ import annotations
from typing import Dict, AnyStr, Optional, List, Tuple
import logging
import asyncio
import json

import boxsdk
import aioredis
import boxsdk.exception as boxsdk_exception

import prometheus.file_system.files.config_file as prometheus_config_file
import prometheus.http_client as prometheus_http_client
import prometheus.redis_client as prometheus_redis_client


log = logging.getLogger(__name__)


class PrometheusBoxClient(boxsdk.Client):
    def __init__(
        self,
        config_file: prometheus_config_file.PrometheusConfigFile = None,
        oauth: boxsdk.JWTAuth = None,
        rate_limited: bool = True,
        rate_limit: int = 15,
        **kwargs,
    ) -> PrometheusBoxClient:

        if not oauth:
            oauth = self.configure_standard_box_auth(config_file)

        super().__init__(oauth, **kwargs)

        self.auth_enterprise_id = self.auth._enterprise_id
        self.auth_client_id = self.auth._client_id

        self.rate_limiter = (
            prometheus_http_client.RateLimiter(rate_limit)
            if rate_limited
            else None
        )

    def __repr__(self) -> AnyStr:
        return f"<{type(self).__name__}-EID-{self.auth_enterprise_id}-ClientID-{self.auth_client_id}>"

    @staticmethod
    def build_skill_card(
        text: AnyStr, skill_card_type: AnyStr, skill_card_title: AnyStr
    ) -> Dict:
        """
            Create a skills card
            Args:
                input (list): subunits (e.g. sentences) to be formatted to card
                skill_card_type (str): type of skill card to create ['transcript', 'timeline', 'keyword']
                skill_card_title (str): title of skill card once written on file
            Returns:
                card (dict): formatted card to be written to Box metadata
        """
        return {
            "type": "skill_card",
            "skill_card_type": skill_card_type,
            "skill": {"type": "images", "id": "defaultID"},
            "invocation": {"type": "skill_invocation", "id": "defaultID"},
            "skill_card_title": {"message": skill_card_title},
            "duration": 1,
            "entries": [{"type": "text", "text": text, "appears": []}],
        }

    @staticmethod
    def configure_standard_box_auth(
        config_file: prometheus_config_file.PrometheusConfigFile,
    ) -> boxsdk.JWTAuth:

        box_auth = boxsdk.JWTAuth.from_settings_dictionary(
            config_file["box_client"]["jwt_auth"]
        )
        box_auth.authenticate_instance()

        return box_auth

    def create_sub_folder(self, parent_id: AnyStr, sub_folder_name: AnyStr):
        """Create the boxbot test folder and return the folderID

        Args:
        boxclient: Session Client
        parent_id: Box Folder ID of root folder

        Returns:
        folderid: Folder ID of the new subfolder, ERROR if a problem
        """
        new_folder_id = None
        try:
            parent_folder = self.folder(folder_id=parent_id).get()
            new_folder_id = parent_folder.create_subfolder(sub_folder_name).id
        except Exception as e:
            log.error(
                f"{self} failed to create folder in parent with id {parent_id} and name {sub_folder_name} with {e}"
            )

        return new_folder_id

    def delete_folder(self, box_folder_id):
        """Delete the boxbot test folder

        Args:
        boxclient: Session Client
        session_root_id: ID of subfolder to delete
        """
        deleted = False
        try:
            self.folder(folder_id=box_folder_id).delete()
            deleted = True
        except Exception as e:
            log.error(f"{self} failed folder delete with {e}")

        return deleted

    def make_request(
        self, method: AnyStr, url: AnyStr, **kwargs
    ) -> boxsdk.network.default_network.DefaultNetworkResponse:
        """
        Base class override to rate limit requests
        """
        if self.rate_limiter:
            with self.rate_limiter:
                resp = super().make_request(method, url, **kwargs)
        else:
            resp = super().make_request(method, url, **kwargs)

        return resp

    def get_list_cached_box_user_from_email(
        self, box_user_email: str, box_users: List[boxsdk.object.user.User],
    ) -> Tuple[boxsdk.object.user.User, List]:
        """
        Checks in memory cache for the Box user associated with an email. If the Box user is not found, it calls Box APIs
        for the user, then caches the user in memory.
        """

        try:

            box_user = None

            # Check for cached Box users
            for cached_box_user in box_users:
                if cached_box_user.response_object["login"] == box_user_email:
                    box_user = cached_box_user
                    break

            else:

                # Search Box API for a user by their primary email
                box_user = self.search_user_by_primary_email(box_user_email)

                assert box_user

                # Cache the Box user
                box_users.append(box_user)
                log.debug(f"cached Box user {box_user}")

        except Exception as e:
            log.error(f"failed to find Box user with email {box_user_email} {e}")

        return box_user, box_users

    def get_file_by_id(
        self,
        file_id: str,
        box_user: Optional[boxsdk.object.user.User] = None,
    ) -> Optional[boxsdk.object.file.File]:

        file = None
        try:
            if box_user:
                file = self.as_user(box_user).file(file_id).get()
            else:
                file = self.file(file_id).get()

            log.debug(f"{self} got file {file}")

        except boxsdk_exception.BoxAPIException as e:
            log.info(f"{self} failed to get file with id {file_id} with {e}")

        return file

    def get_folder_by_id(
        self,
        folder_id: str,
        box_user: Optional[boxsdk.object.user.User] = None,
    ) -> Optional[boxsdk.object.folder.Folder]:

        folder = None
        try:
            if box_user:
                folder = self.as_user(box_user).folder(folder_id).get()
            else:
                folder = self.folder(folder_id).get()

            log.debug(f"{self} got folder OP")
        except boxsdk_exception.BoxAPIException as e:
            log.info(f"{self} failed to get folder with id {folder} with {e}")

        return folder

    async def get_folder_id_from_path(
        self,
        redis_client: aioredis.Redis,
        box_user: boxsdk.object.user.User,
        box_user_id: AnyStr,
        folder_path: AnyStr,
    ) -> Tuple[AnyStr, List]:
        """
        Checks Redis for a cached folder path -> id association record. If the record is not found, it calls Box APIs
        for the folder paths id, then sets the association to Redis.
        """

        try:

            source_folder_id = None

            # Check Redis cache for Box user folder path ID association
            source_folder_path_redis_key = (
                f"box-folder-path-id:box-user-{box_user_id}:{folder_path}"
            )

            source_folder_id = await prometheus_redis_client.get(
                redis_client, source_folder_path_redis_key
            )

            if not source_folder_id:
                # Search Box API for the folder ID by its path
                source_folder_response = self.get_folder_by_path(folder_path, box_user)

                source_folder_id = source_folder_response.json()["entries"][0]["id"]

                # Set Box user folder path ID association to Redis
                await prometheus_redis_client.set(
                    redis_client, source_folder_path_redis_key, source_folder_id
                )

        except boxsdk_exception.BoxException as e:
            log.info(
                f"{self} failed to find Box folder with path {folder_path} with {e}"
            )

        return source_folder_id

    def get_groups_list(self) -> List:
        groups = None
        try:
            groups = [(str(group.name), group) for group in self.groups()]
            log.debug(f"got groups list {groups}")
        except Exception as e:
            log.error(f"{self} failed to get groups with {e}")

        return groups

    @staticmethod
    def generate_item_path(item: boxsdk.object.item.Item) -> AnyStr:
        """ Takes a folder or file object
            Returns the path to that item as a string
        """

        path = ""

        for entry in item.path_collection["entries"]:
            path += "/" + entry["name"]

        path += "/" + item.name

        log.debug(f"built item path {path}")

        return path

    def get_current_user(self):
        current_user = None
        try:
            current_user = self.user(user_id="me").get()
            log.info(
                f"{self} current user: {current_user.login} ({current_user.name}) user_id: {current_user.id}"
            )
        except boxsdk_exception.BoxException as e:
            log.error(f"{self} failed to log current user info with {e}")

        return current_user

    def get_events_in_time_range(
        self,
        admin_events: Optional[bool] = True,
        event_types: Optional[AnyStr] = None,
        created_before: Optional[AnyStr] = None,
        created_after: Optional[AnyStr] = None,
        stream_position: Optional[AnyStr] = None,
        limit: Optional[int] = 500,
    ) -> boxsdk.network.default_network.DefaultNetworkResponse:

        req_url = f"https://api.box.com/2.0/events?limit={limit}"

        if admin_events:
            req_url += f"&stream_type=admin_logs"

        if event_types:
            req_url += f"&event_type={event_types}"

        if created_before:
            req_url += f"&created_before={created_before}"

        if created_after:
            req_url += f"&created_after={created_after}"

        if stream_position:
            req_url += f"&stream_position={stream_position}"

        response = self.make_request("GET", req_url).json()

        return response

    def get_folder_by_path(
        self,
        folder_path: AnyStr,
        box_user: Optional[boxsdk.object.user.User] = None,
        base_folder_id: Optional[AnyStr] = None,
    ) -> boxsdk.network.default_network.DefaultNetworkResponse:

        req_url = f"https://api.box.com/2.0/folders?path={folder_path}"
        if base_folder_id:
            req_url += f"&parent_id={base_folder_id}"

        if not box_user:
            response = self.make_request("GET", req_url)
        else:
            response = self.as_user(box_user).make_request("GET", req_url)

        return response

    @staticmethod
    def parse_skill_webhook_request(request: Dict) -> Dict:
        index_event = json.loads(request["body"])

        return {
            "read_token": index_event["token"]["read"]["access_token"],
            "write_token": index_event["token"]["write"]["access_token"],
            "file_id": index_event["source"]["id"],
            "file_name": index_event["source"]["name"],
        }

    def search_user_by_primary_email(
        self, primary_email: AnyStr
    ) -> Optional[boxsdk.object.user.User]:
        box_user = None
        try:
            box_user = self.users(filter_term=primary_email, limit=1).next()
        except:
            log.debug(
                f"{self} failed to find box user with email {primary_email} from search api. checking all users"
            )
            for user in self.users():
                if user.response_object["login"] == primary_email:
                    box_user = user

        if box_user:
            log.debug(f"found box user with primary email {primary_email}")
        else:
            log.debug(f"failed to find box user with primary email {primary_email}")

        return box_user

    def write_skills_card(
        self, file_id: AnyStr, skills_card: Dict
    ) -> boxsdk.network.default_network.DefaultNetworkResponse:
        """
            Write Skills and Standard metadata to Box
            Params:
                box_client (obj): Box client to make calls to Box API
                metadata (dict): formatted Skills metadata to write
            Returns:
                response (str): response from write metadata call
        """

        return (
            self.file(file_id=file_id)
            .metadata("global", "boxSkillsCards")
            .create(skills_card)
        )


class BTCRedisManagedJWTAuth(boxsdk.auth.RedisManagedJWTAuth):
    """
    Box Consulting's boxsdk.auth.RedisManagedJWTAuth subclass
    """

    def _store_tokens(
        self, access_token: AnyStr, refresh_token: Optional[AnyStr]
    ) -> None:
        """
        Base class override to ensure serializable None type refresh_token
        """

        super(
            boxsdk.auth.redis_managed_oauth2.RedisManagedOAuth2Mixin, self
        )._store_tokens(access_token, refresh_token)

        if refresh_token is None:
            refresh_token = ""

        self._redis_server.hmset(
            self._unique_id, {"access": access_token, "refresh": refresh_token}
        )


async def gather_box_collaboration_deletion_tasks(
    configuration: Dict, collaboration_ids: List, headers: Dict
) -> List:

    http_client = prometheus_http_client.prometheusClientSession(configuration)
    rate_limiter = prometheus_http_client.RateLimiter(
        rate_limit=configuration["http"]["rate_limit"],
        rate_period=configuration["http"]["rate_period"],
    )

    async with http_client:
        coroutine_tasks = [
            asyncio.create_task(
                prometheus_http_client.request(
                    http_client,
                    rate_limiter,
                    f"https://api.box.com/2.0/collaborations/{collaboration_id}",
                    "delete",
                    response_handler=validate_response,
                    **headers,
                )
            )
            for collaboration_id in collaboration_ids
        ]

        return await asyncio.gather(*coroutine_tasks)


def validate_response(api_response: AnyStr) -> None:
    try:
        result_dict = json.loads(api_response)
        log.debug(result_dict)

        if result_dict["type"] == "error":
            log.error("collaboration deletion error")
            log.error(result_dict["context_info"]["errors"])
        else:
            log.info("Successful Box API Call")
    except Exception as e:
        log.error("failed json load")
        log.error(api_response)
        log.error(str(e))
