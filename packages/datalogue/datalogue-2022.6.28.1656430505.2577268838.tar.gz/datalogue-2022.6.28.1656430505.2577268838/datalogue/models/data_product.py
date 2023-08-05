from datetime import datetime
from uuid import UUID
from typing import Union, Optional, List
from dateutil.parser import parse
from datalogue.errors import DtlError


class DataProduct:
    """
    Data Product is a collection of multiple pipelines, streaming from a user defined set of sources
    to a user defined set of destinations, creating a data set to service a specific use case.
    Grouping pipelines into use-case specific Data Products allows for clear ownership,
    governance as well as easy updating to ensure the end data set is fresh, trustable and reliable.

    :param name: name of the Data Product (name must be unique)
    :param description: description of your Data Product (Optional)
    :param pipeline_ids: list of pipeline ids (pipeline_id and Data Product mapping is unique)
    :id: unique uuid of the Data Product, auto-generated by backend
    :owner: represents the uuid of a user, who owns the Data Product, auto-generated by backend
    :created_by: uuid of the creator of the Data Product, auto-generated by backend
    :created_at: timestamp at which the Data Product is created, auto-generated by backend
    :last_updated_by: uuid of the user, who last modified the Data Product, auto-generated by backend
    :last_updated_at: timestamp at which the Data Product was last modified, auto-generated by backend
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        pipeline_ids: List[UUID] = [],
        id: Optional[UUID] = None,
        owner: Optional[UUID] = None,
        created_by: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        last_updated_by: Optional[UUID] = None,
        last_updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.owner = owner
        self.created_by = created_by
        self.created_at = created_at
        self.last_updated_by = last_updated_by
        self.last_updated_at = last_updated_at
        self.pipeline_ids = pipeline_ids

    def __eq__(self, other):
        return (
            (self.id == other.id)
            and (self.name == other.name)
            and (self.created_at == other.created_at)
            and (self.created_by == other.created_by)
        )

    def __repr__(self):
        """
        Represents a Data Product Object in a user friendly readable format.
        """
        return (
            f"{self.__class__.__name__}(\n "
            f"id= {self.id!r},\n "
            f"name= {self.name!r},\n "
            f"description= {self.description!r},\n "
            f"pipeline_ids= {self.pipeline_ids!r},\n "
            f"owner= {self.owner!r},\n "
            f"created_by= {self.created_by!r},\n "
            f"created_at= {self.created_at!r},\n "
            f"last_updated_by= {self.last_updated_by!r},\n "
            f"last_updated_at= {self.last_updated_at!r}\n "
            ")"
        )

    def _as_payload(self) -> dict:
        """
        Parses a Data Product object into a dictionary.
        """
        payload = {"name": self.name}
        if self.description is not None:
            payload["description"] = self.description
        payload["streamIds"] = [str(pipeline_id) for pipeline_id in self.pipeline_ids]
        return payload

    @classmethod
    def _from_payload(cls, json: dict) -> Union[DtlError, "DataProduct"]:
        """
        Parses a dictionary into a Data Product object.
        """
        id = json.get("id")
        if id is None:
            return DtlError("Data Product object should have a 'id' property")
        else:
            try:
                id = UUID(id)
            except ValueError:
                return DtlError("'id' field was not a proper uuid")

        name = json.get("name")
        if name is None:
            return DtlError("Data Product object should have a 'name' property")

        description = json.get("description")
        owner = json.get("owner")
        if owner is None:
            return DtlError("Data Product object should have a 'owner' property")
        else:
            try:
                owner = UUID(owner)
            except ValueError:
                return DtlError("'owner' field was not a proper uuid")

        created_by = json.get("createdBy")
        if created_by is None:
            return DtlError("Data Product object should have a 'createdBy' property")
        else:
            try:
                created_by = UUID(created_by)
            except ValueError:
                return DtlError("'createdBy' field was not a proper uuid")

        created_at = json.get("createdAt")
        if created_at is None:
            return DtlError("Data Product object should have a 'createdAt' property")
        else:
            try:
                created_at = parse(created_at)
            except ValueError:
                return DtlError("The 'createdAt' could not be parsed as a valid date")

        last_updated_by = json.get("lastUpdatedBy")
        if last_updated_by is None:
            return DtlError(
                "Data Product object should have a 'lastUpdatedBy' property"
            )
        else:
            try:
                last_updated_by = UUID(last_updated_by)
            except ValueError:
                return DtlError("'lastUpdatedBy' field was not a proper uuid")

        last_updated_at = json.get("lastUpdatedAt")
        if last_updated_at is None:
            return DtlError(
                "Data Product object should have a 'lastUpdatedAt' property"
            )
        else:
            try:
                last_updated_at = parse(last_updated_at)
            except ValueError:
                return DtlError(
                    "The 'lastUpdatedAt' could not be parsed as a valid date"
                )

        pipeline_ids = json.get("streamIds")
        if pipeline_ids is None:
            return DtlError("Data Product object should have a 'streamIds' property")

        return cls(
            name=name,
            id=id,
            description=description,
            owner=owner,
            created_by=created_by,
            created_at=created_at,
            last_updated_by=last_updated_by,
            last_updated_at=last_updated_at,
            pipeline_ids=pipeline_ids,
        )
