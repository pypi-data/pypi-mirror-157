from .base_class import BaseClass
from typing import Union

import random

import re


def prettyword(n: int, forms: Union[list, tuple, str]) -> str:
    if isinstance(forms, str):
        return forms

    if n == 0:
        return forms[0]

    elif n % 100 in [11, 12, 13, 14]:
        return forms[3]

    elif n % 10 == 1:
        return forms[1]

    elif n % 10 in [2, 3, 4]:
        return forms[2]

    else:
        return forms[3]


def prettyword_en(n: int, forms: Union[list, tuple]) -> str:
    if n == 1:
        return forms[0]

    else:
        return forms[1]


class TranslateList(list):
    def _(self, **kwargs):
        if kwargs.get("went_random", False):
            return TranslateStr(random.choice(self))(**kwargs)

        return self

    __call__ = _


class TranslateStr(str):
    def _(self, **kwargs):
        # phrases = [self._format(i, **kwargs) for i in re.split(r"{}", self)]
        return re.sub(r"{.+?}", lambda x: self._format(x.group()[1:-1], **kwargs), self)

    def _format(self, text: str, **kwargs) -> str:
        if "|" in text:
            cases = re.split(r"\s\|\s", text)

            VAR_TYPE_2 = r"\$\w{1,}"
            first_var = re.findall(VAR_TYPE_2, text)[0][1:]

            count = kwargs[first_var]

            if len(cases) == 2:
                text = cases[0] if count == (0, 1) else cases[1]

            text = prettyword(count, cases) if len(cases) > 2 else \
                prettyword_en(count, cases)

            return re.sub(VAR_TYPE_2, lambda x: str(kwargs[x.group()[1:]]), text)

        elif "::" in text:
            try:
                section, var = text.split("::")
            except:
                section, var = "current", text

            return _[section][var](**kwargs)
        
        else:
            return str(kwargs.get(text))

    __call__ = _


class Dict2Object(BaseClass):
    def __init__(self, **entries):
        self.__dict__.update(entries)


class Locale2Object(BaseClass):
    def __init__(self, **entries):
        for key, value in entries.items():
            if isinstance(value, str):
                entries[key] = TranslateStr(value)

            elif isinstance(value, list):
                entries[key] = TranslateList(value)

        self.__dict__.update(entries)


def dict_to_object(**kwargs) -> Dict2Object:
    return Dict2Object(**kwargs)
