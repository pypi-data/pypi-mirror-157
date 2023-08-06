from typing import Any, Union, Optional
import yaml

from dataclasses import dataclass
from pathlib import Path

from .models.locale import Locale, LocaleConfig
from pyi18n_new.lib.base_class import BaseClass


@dataclass
class I18N(BaseClass):
    path: Path
    default: str = "en"

    def __post_init__(self):
        folders = list(self.path.iterdir())

        for folder in folders:
            locale = self.get_locale(folder)
            setattr(self, folder.name, locale)

    def __getattr__(self, name: str) -> Any:
        return self[self.default][name]

    @property
    def languages(self) -> list[str]:
        """Get list of used languages"""

        return [_ for _, locale in self.__dict__.items() if isinstance(locale, Locale)]

    def get_locale(self, path: Path) -> Locale:
        """Get locale with params"""

        with (path / "__init__.yml").open() as file:
            config = yaml.safe_load(file.read())
            return Locale(LocaleConfig(lang=path.name, path=path, **config))

    def translate(self, path: str, lang: Optional[str] = None, **kwargs) -> Union[str, list]:
        """python-i18n compatible interface"""

        section, name = path.split(".")

        return self[lang or self.default][section][name](**kwargs)
