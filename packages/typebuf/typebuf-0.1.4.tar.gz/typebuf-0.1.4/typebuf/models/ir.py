from pydantic import BaseModel

from .typedefinition import TypeDefinition


class IR(BaseModel):
    """
    Intermediate Representation of the entire file that was passed in
    {'typedefs': [
        {'typename': 'User',
         'imports': ...,
         'fields': [
             {'name': 'first_name', 'type': 'string', 'optional': False},
             {'name': 'last_name', 'type': 'string', 'optional': False},
             {'name': 'age', 'type': 'int', 'optional': False},
             {'name': 'weight', 'type': 'float', 'optional': True} ]
         }
      ]
    }
    """
    typedefs: list[TypeDefinition]

    @property
    def typedef_c(self) -> int:
        """
        Count of type definitions we read
        :return: (int)
        """
        return len(self.typedefs)
