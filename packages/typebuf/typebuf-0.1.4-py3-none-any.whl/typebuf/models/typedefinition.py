from pydantic import BaseModel
from typing import Optional

from .typefield import TypeField


class TypeDefinition(BaseModel):
    """
    Represents one new Type in the list of typedefs
    {'typename': 'User',
     'imports': ...,
     'fields': [
        {'name': 'first_name', 'type': 'string', 'optional': False},
        {'name': 'last_name', 'type': 'string', 'optional': False},
        {'name': 'age', 'type': 'int', 'optional': False},
        {'name': 'weight', 'type': 'float', 'optional': True} ]
    }
    """
    typename: str
    imports: Optional[dict[str, list[str]]]
    fields: list[TypeField]
