from enum import Enum


class StatesSet(Enum):
    BA = 'Bahia'

    def get(value):
        value = value.lower()
        if 'ba' == value:
            return StatesSet.BA.value
