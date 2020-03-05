from typing import List
import datetime
import uuid

import attr


def cls_instantiator(cls):
    def converter(instance_args):
        if isinstance(instance_args, cls):
            return instance_args
        else:
            if instance_args:
                instance = cls(**instance_args)
            else:
                instance = None

            return instance

    return converter


def list_cls_instantiator(cls):
    def converter(instances_args):
        instances = [
            cls(**instance_args) for instance_args in instances_args if instance_args
        ]

        return instances

    return converter


@attr.s(slots=True, auto_attribs=True)
class WebHook:
    id: str = None
    type: str = None


@attr.s(slots=True, auto_attribs=True)
class By:
    type: str = None
    id: str = None
    name: str = None
    login: str = None

    def get_box_user(self, box_client):
        # Get User instance from sdk for self.created_by.login
        # Return the User instance
        pass


@attr.s(slots=True)
class CreatedBy(By):
    pass


@attr.s(slots=True)
class ModifiedBy(By):
    pass


@attr.s(slots=True)
class OwnedBy(By):
    pass


@attr.s(slots=True, auto_attribs=True)
class FileVersion:
    type: str = None
    id: str = None
    sha1: str = None


@attr.s(slots=True, auto_attribs=True)
class Item:
    type: str = None
    id: str = None
    sequence_id: str = None
    etag: str = None
    name: str = None


@attr.s(slots=True)
class PathCollectionEntry(Item):
    pass


@attr.s(slots=True)
class Parent(Item):
    pass


@attr.s(slots=True)
class Permission:
    can_preview: bool = None
    can_download: bool = None


@attr.s(slots=True, auto_attribs=True)
class PathCollection:
    entries: List[PathCollectionEntry] = attr.ib(converter=list_cls_instantiator(PathCollectionEntry), default=None)
    total_count: int = None


@attr.s(slots=True, auto_attribs=True)
class Source:
    file_version: FileVersion = attr.ib(converter=cls_instantiator(FileVersion), default=None)
    created_by: CreatedBy = attr.ib(converter=cls_instantiator(CreatedBy), default=None)
    modified_by: ModifiedBy = attr.ib(converter=cls_instantiator(ModifiedBy), default=None)
    owned_by: OwnedBy = attr.ib(converter=cls_instantiator(OwnedBy), default=None)
    permissions: Permission = attr.ib(converter=cls_instantiator(Permission), default=None)
    item: Item = attr.ib(converter=cls_instantiator(Item), default=None)
    path_collection: PathCollection = attr.ib(converter=cls_instantiator(PathCollection), default=None)
    parent: Parent = attr.ib(converter=cls_instantiator(Parent), default=None)
    id: str = None
    type: str = None
    sequence_id: str = None
    etag: str = None
    sha1: str = None
    name: str = None
    description: str = None
    size: int = None
    created_at: datetime.datetime = None
    modified_at: datetime.datetime = None
    trashed_at: datetime.datetime = None
    purged_at: datetime.datetime = None
    content_created_at: datetime.datetime = None
    content_modified_at: datetime.datetime = None
    shared_link: str = None
    folder_upload_email: str = None
    item_status: str = None
    invite_email: str = None
    role: str = None
    acknowledged_at: datetime.datetime = None
    url: str = None
    download_url: str = None
    vanity_url: str = None
    effective_access: str = None
    effective_permission: str = None
    is_password_enabled: str = None
    unshared_at: datetime.datetime = None
    download_count: str = None
    preview_count: str = None
    access: str = None


@attr.s(slots=True, auto_attribs=True)
class Detail:
    type: str
    id: uuid.UUID
    created_at: datetime.datetime
    trigger: str
    additional_info: List[str]
    webhook: WebHook = attr.ib(converter=cls_instantiator(WebHook), default=None)
    created_by: CreatedBy = attr.ib(converter=cls_instantiator(CreatedBy), default=None)
    source: Source = attr.ib(converter=cls_instantiator(Source), default=None)


@attr.s(slots=True, auto_attribs=True)
class BoxWebhook:
    version: str
    id: uuid.UUID
    detail_type: str
    source: str
    account: str
    time: datetime.datetime
    region: str
    resources: List[str]
    detail: Detail = attr.ib(converter=cls_instantiator(Detail), default=None)
