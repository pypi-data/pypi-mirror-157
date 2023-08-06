from dataclasses import dataclass
from typing import List
from typing import Optional
from mlplatform_lib.dataclass import DataObjectOutCol

# example
# "name": "TEST",
# "sourceTableName": "TEST",
# "subtype": "Table",
# "outCols": [
#     {
#         "name": "C1"
#     },
#     {
#         "name": "C2"
#     }
# ],
# "shareRelation": [
# ]


@dataclass
class DataObject:
    id: str
    name: str
    out_cols: List[DataObjectOutCol]
    share_relation: List[str]
    source_table_name: str
    subtype: str
    author: str
    description: str
    created_on: str
    last_edited: str
    scope_regex: str

    def __post_init__(self):
        self.scope_regex = self.scope_regex if self.scope_regex else ""

