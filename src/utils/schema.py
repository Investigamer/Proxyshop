"""
* Utils: Schema and Validation
"""
# Third Party Imports
from pydantic import BaseModel


class Schema(BaseModel):
    """Basic schema class."""


class DictSchema(Schema):
    """Dictionary schema class."""

    def __new__(cls, **data):
        """Return new instance as a dictionary."""
        new = super().__new__(cls)
        new.__init__(**data)
        return new.model_dump()
