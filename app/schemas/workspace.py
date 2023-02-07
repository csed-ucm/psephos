from beanie import PydanticObjectId


# Custom PydanticObjectId class to override due to a bug
class WorkspaceID(PydanticObjectId):
    @classmethod
    def __modify_schema__(cls, field_schema):  # type: ignore
        field_schema.update(
            type="string",
            example="5eb7cf5a86d9755df3a6c593",
        )
