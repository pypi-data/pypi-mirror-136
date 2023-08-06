from pydantic import BaseModel
from typing import Optional


class TypeField(BaseModel):
    """
    Represents one Field in a Type
    {'name': 'first_name', 'type': 'string', 'optional': False},
    """
    name: str
    type: str
    optional: Optional[bool] = False
