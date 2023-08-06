from typing import Any, List


class Enum:
    @classmethod
    def all(cls) -> List[Any]:
        public_members = [a for a in vars(cls) if not a.startswith('_')]
        return [getattr(cls, a) for a in public_members if not callable(getattr(cls, a))]

    @classmethod
    def __len__(cls) -> int:
        return len(cls.all())
