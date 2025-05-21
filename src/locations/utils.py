from typing import List, Dict
from src.locations.schemas import SLocationRead
from src.locations.models import Location


def build_tree(loc_models: List[Location]) -> List[SLocationRead]:
    """
    Преобразует плоский список моделей Location в дерево схем SLocationRead.
    """
    schema_map: Dict[int, SLocationRead] = {}
    for m in loc_models:
        sch = SLocationRead.model_validate(m)
        sch.children = []
        schema_map[sch.id] = sch
    tree: List[SLocationRead] = []
    for sch in schema_map.values():
        if sch.parent_id and sch.parent_id in schema_map:
            schema_map[sch.parent_id].children.append(sch)
        else:
            tree.append(sch)
    return tree