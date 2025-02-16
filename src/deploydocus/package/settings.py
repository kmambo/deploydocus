from pydantic import BaseModel


# TODO: Remove this and simplify
class InstanceSettings(BaseModel):
    instance_name: str
    instance_version: str
    instance_namespace: str
    image_name_with_tag: str | None = None
