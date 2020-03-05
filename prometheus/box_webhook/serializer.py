from marshmallow import Schema, fields, post_load

import prometheus.box_webhook.model as webhook_model


class WebHookSchema(Schema):
    id = fields.String()
    type = fields.String()


class BySchema(Schema):
    type = fields.String()
    id = fields.String()
    name = fields.String()
    login = fields.String()


class CreatedBySchema(BySchema):
    pass


class ModifiedBySchema(BySchema):
    pass


class OwnedBySchema(BySchema):
    pass


class FileVersionSchema(Schema):
    type = fields.String()
    id = fields.String()
    sha1 = fields.String()


class ItemSchema(Schema):
    type = fields.String()
    id = fields.String()
    sequence_id = fields.String(allow_none=True)
    etag = fields.String(allow_none=True)
    name = fields.String()


class PathCollectionEntrySchema(ItemSchema):
    pass


class ParentSchema(ItemSchema):
    pass


class PathCollectionSchema(Schema):
    total_count = fields.Integer()
    entries = fields.List(
        fields.Nested(PathCollectionEntrySchema())
    )


class SourceSchema(Schema):
    id = fields.String()
    type = fields.String()
    file_version = fields.Nested(FileVersionSchema())
    sequence_id = fields.String()
    etag = fields.String()
    sha1 = fields.String()
    name = fields.String()
    description = fields.String(allow_none=True)
    size = fields.Integer()
    path_collection = fields.Nested(PathCollectionSchema())
    created_at = fields.DateTime()
    modified_at = fields.DateTime()
    trashed_at = fields.DateTime(allow_none=True)
    purged_at = fields.DateTime(allow_none=True)
    content_created_at = fields.DateTime()
    content_modified_at = fields.DateTime()
    created_by = fields.Nested(CreatedBySchema())
    modified_by = fields.Nested(ModifiedBySchema())
    owned_by = fields.Nested(OwnedBySchema())
    shared_link = fields.String(allow_none=True)
    parent = fields.Nested(ParentSchema())
    item_status = fields.String()
    access = fields.String()
    preview_count = fields.String()
    download_count = fields.String()
    unshared_at = fields.DateTime()
    is_password_enabled = fields.String()
    effective_permission = fields.String()
    effective_access = fields.String()
    vanity_url = fields.String()
    download_url = fields.String()
    url = fields.String()
    acknowledged_at = fields.DateTime()
    folder_upload_email = fields.String()
    invite_email = fields.String()
    role = fields.String()


class DetailSchema(Schema):
    type = fields.String()
    id = fields.UUID()
    created_at = fields.DateTime()
    trigger = fields.String()
    webhook = fields.Nested(WebHookSchema())
    created_by = fields.Nested(CreatedBySchema())
    source = fields.Nested(SourceSchema())
    additional_info = fields.List(fields.String(), allow_none=True)


class BoxWebhookSchema(Schema):
    version = fields.String()
    id = fields.UUID()
    detail_type = fields.String(data_key="detail-type")
    source = fields.String()
    account = fields.String()
    time = fields.DateTime()
    region = fields.String()
    resources = fields.List(fields.String())
    detail = fields.Nested(DetailSchema())

    @post_load
    def init_model(self, data, **kwargs):
        return webhook_model.BoxWebhook(**data)
