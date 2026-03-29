from abc import ABC, abstractmethod
from collections import defaultdict


class BaseGenerator(ABC):
    name: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "name"):
            _REGISTRY[cls.name] = cls

    @abstractmethod
    def generate(self, **kwargs) -> object:
        """Generate and return single value."""
        ...

    @classmethod
    def get(cls, name: str) -> type["BaseGenerator"]:
        if name not in _REGISTRY:
            raise ValueError(f"Unknown generator: {name}")
        return _REGISTRY[name]

    @classmethod
    def all(cls) -> defaultdict[str, type["BaseGenerator"]]:
        return _REGISTRY


_REGISTRY: defaultdict[str, type[BaseGenerator]] = defaultdict(lambda: BaseGenerator)
