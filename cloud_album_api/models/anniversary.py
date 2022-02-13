import datetime


class Anniversary:
    def __init__(self, id: str, title: str, date: datetime.date, type: str):
        self.id = id
        self.title = title
        self.date = date
        self.type = type

    @classmethod
    def from_dict(cls, anniversary_dict: dict):
        return Anniversary(
            id=anniversary_dict.get('id', ''),
            title=anniversary_dict.get('title', ''),
            date=datetime.datetime.strptime(
                anniversary_dict.get('date', ''), '%Y-%m-%d %H:%M:%S'),
            type=anniversary_dict.get('type', ''),
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'type': self.type,
        }
