# main.py
#
# Copyright 2022 Kim Timothy Engh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# RouteSequence
#
# Numbers series that range from AA0000 to ZZ9999, or 0 to 6759999.


from __future__ import annotations
from dataclasses import dataclass

import re
from typing import Iterator
from typing import Pattern
from typing import Union
from typing import Any
from typing_extensions import TypeGuard


class RouteSequence:
    __pattern: Pattern = re.compile("^[A-Z]{2}[0-9]{4}$")

    def __init__(self, seed: Union[int, str] = 'AA0000'):
        '''Route Sequence. Seed can be given either by:
        type: str, where the range is between AA0001 and ZZ9999.
        type: int, where the range is between 0 and 6759999.
        '''

        if self.is_valid_int(seed):
            self.__seed = seed
        
        elif self.is_valid_str(seed):
            self.__seed = self.to_int(seed)

        else:
            raise ValueError


    @classmethod
    def is_valid_str(cls, seed: Any) -> TypeGuard[str]:
        ''' Checks if a given string is a valid sequence number '''
        return True if re.findall(cls.__pattern, str(seed)) and isinstance(seed, str) else False

    @classmethod
    def is_valid_int(cls, seed: Any) -> TypeGuard[int]:
        ''' Checks if a given integer is a valid sequence number '''
        try:
            return seed >= 0 and seed < 6760000

        except TypeError:
            return False


    @classmethod
    def from_int(cls, seed: int) -> RouteSequence:
        ''' Creates a new class instance using an integer as a seed '''
        if cls.is_valid_int(seed):
            return cls(cls.to_str(seed))
        else:
            raise ValueError(f"Integer range is from 0 to 6760000")

    @classmethod
    def from_str(cls, seed: str) -> RouteSequence:
        ''' Creates a new class instance using an string as a seed '''
        return cls(seed)

    @staticmethod
    def to_str(value: int) -> str:
        ''' Converts a given integer to the corresponding string value '''
        a = chr(((value // 10000) // 26) % 26 + 65)
        b = chr((value // 10000) % 26 + 65)
        c = str(value % 10000).zfill(4)
    
        return a + b + c

    @staticmethod
    def to_int(value: str) -> int:
        ''' Converts a given string to the corresponding integer value '''
        a = (ord(value[0]) - 65) * 260000
        b = (ord(value[1]) - 65) * 10000
        c = int(value[2:])

        return a + b + c

    def as_int(self) -> int:
        return self.__seed

    def as_str(self) -> str:
        return self.to_str(self.__seed)

    def __str__(self) -> str:
        return f"{self.to_str(self.__seed)}"

    def __repr__(self) -> str:
        return f"RouteSequence({self.to_str(self.__seed)})"

    def __int__(self):
        return self.__seed

    def __next__(self) -> RouteSequence:
        if self.__seed == 6760000 - 1:
            raise StopIteration

        self.__seed += 1
        return type(self)(self.__seed)

    def __iter__(self) -> Iterator[RouteSequence]:
        while True:
            try:
                yield self.__next__()

            except StopIteration:
                break

    def __eq__(self, other: Union[str, int, RouteSequence]) -> bool: # type: ignore
        if isinstance(other, int):
            return True if self.as_int() == other else False
        else:
            return True if self.as_str() == other else False

    def __gt__(self, other:  Union[str, int, RouteSequence]) -> bool:
        return True if str(self) > str(other) else False

    def __lt__(self, other:  Union[str, int, RouteSequence]) -> bool:
        return True if str(self) < str(other) else False

    def __add__(self, other: Union[str, int, RouteSequence]) -> RouteSequence:
        if isinstance(other, RouteSequence):
            new_value = self.__seed + other.__seed

        elif isinstance(other, str):
            new_value =  self.__seed + self.to_int(other)

        elif isinstance(other, int):
            new_value =  self.__seed + other

        else:
            new_value =  self + other

        if new_value >= 6760000:
            raise OverflowError(f"Upper limit of 6759999 / ZZ9999 surpassed")

        return RouteSequence.from_int(new_value)

    def __sub__(self, other: Union[str, int, RouteSequence]) -> RouteSequence:
        if isinstance(other, RouteSequence):
            new_value = self.__seed - other.__seed

        elif isinstance(other, str):
            new_value = self.__seed - self.to_int(other)

        elif isinstance(other, int):
            new_value = self.__seed - other

        else:
            new_value = self + other

        if new_value < 0:
            raise OverflowError(f"Lower limit of 0 / AA0000 surpassed")

        return RouteSequence(new_value)

    def __mul__(self, other: Union[str, int, RouteSequence]) -> RouteSequence:
        if isinstance(other, RouteSequence):
            return RouteSequence(self.to_str(self.__seed * other.__seed))

        elif isinstance(other, str):
            return RouteSequence(self.to_str(self.__seed * self.to_int(other)))

        elif isinstance(other, int):
            return RouteSequence(self.to_str(self.__seed * other))

        else:
            return self * other

    def __div__(self, other: Union[str, int, RouteSequence]) -> RouteSequence:
        if isinstance(other, RouteSequence):
            return RouteSequence(self.to_str(self.__seed // other.__seed))

        elif isinstance(other, str):
            return RouteSequence(self.to_str(self.__seed // self.to_int(other)))

        elif isinstance(other, int):
            return RouteSequence(self.to_str(self.__seed // other))

        else:
            return self // other

    def __truediv__(self, other: Union[str, int, RouteSequence]) -> RouteSequence:
        return self.__div__(other)

    def __floordiv__(self, other: Union[str, int, RouteSequence]) -> RouteSequence:
        return self.__div__(other)
