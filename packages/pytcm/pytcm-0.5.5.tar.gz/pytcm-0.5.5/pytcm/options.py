# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod
from dataclasses import dataclass


class Option(ABC):
    def __init__(self, value: any = ...) -> None:
        self.value = value

    def parse(self) -> str:
        return "" if self.value is ... else str(self)

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


@dataclass
class Flag(Option):
    """A boolean option

    e.g.: --verbose
    """

    abbreviation: str
    value: str = ...

    def parse(self) -> str:
        if self.value is ...:
            return ""

        return str(self) if self.value else ""

    def __str__(self) -> str:
        return self.abbreviation


@dataclass
class Positional(Option):
    """A simple inline option

    e.g.: example.txt
    """
    value: str = ...

    def __str__(self) -> str:
        return self.value


@dataclass
class Implicit(Option):
    """An option separated by a space character

    e.g.: --exclude example.txt
    """

    abbreviation: str
    value: str = ...

    def __str__(self) -> str:
        return f"{self.abbreviation} {self.value}"


@dataclass
class Explicit(Option):
    """An option with an equal sign

    e.g.: --exclude=example.txt
    """

    abbreviation: str
    value: str = ...

    def __str__(self) -> str:
        return f"{self.abbreviation}={self.value}"
