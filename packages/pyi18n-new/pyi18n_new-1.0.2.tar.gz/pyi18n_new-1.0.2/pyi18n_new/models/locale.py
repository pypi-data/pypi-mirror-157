import yaml

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pyi18n_new.lib.dict_to_object import Locale2Object
from pyi18n_new.lib.base_class import BaseClass


@dataclass
class LocaleConfig:
    lang: str
    path: Path

    maintainer: Optional[str] = None
    plurals: str = ""
    version: str = "0.0"


@dataclass
class Locale(BaseClass):
    __config: LocaleConfig

    def __post_init__(self):
        self.load()

    def load(self):
        for file in self.__config.path.glob("[!_]*.yml"):
            with file.open(encoding="utf-8") as f:
                raw_dict = yaml.safe_load(f.read().replace("%{", "{"))
                setattr(self, file.stem, Locale2Object(**raw_dict))
