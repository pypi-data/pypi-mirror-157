from typing import List, Optional
from pydantic import BaseModel, Field
from .base import PerPageRequest

class AttributeFilter(PerPageRequest):
    name: Optional[str] = Field(None, alias="filter[name]")
    type: Optional[List[str]] = Field(None, alias="filter[type][]")
    group: Optional[List[str]] = Field(None, alias="filter[group][]")
    
    class Config:
        allow_population_by_field_name = True


class BaseAttribute(BaseModel):
    name: str
    type: str
    code: str
    group: str
    is_required: bool
    is_editable: bool
    is_filterable: bool
    is_visible: bool
    position: int

class AttributeListItem(BaseAttribute):
    id: str
    value: dict
    group: dict
    type_translation: str


class AttributeGroupItem(BaseModel):
    id: str
    name: str
    code: str
    position: int