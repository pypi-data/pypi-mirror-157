from typing import Any


class BaseClass:
    def __getitem__(self, name: str) -> Any:
        return getattr(self, name)
