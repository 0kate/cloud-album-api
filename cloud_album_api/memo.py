from typing import Optional

class Memo:
    def __init__(
            self,
            id: str,
            title: str,
            done: bool = False,
            is_list: bool = False,
            parent: Optional[str] = None):
        self.id = id
        self.title = title
        self.done = done
        self.is_list = is_list
        self.parent = parent

    @classmethod
    def from_dict(cls, memo_dict: dict):
        return Memo(
            id=memo_dict.get('id', ''),
            title=memo_dict.get('title', ''),
            done=memo_dict.get('done', False),
            is_list=memo_dict.get('isList', False),
            parent=memo_dict.get('parent'),
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'done': self.done,
            'isList': self.is_list,
            'parent': self.parent,
        }
