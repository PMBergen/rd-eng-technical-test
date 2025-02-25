"""
File holding DataRow class
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DataRow:
    """
    DataRow class to hold the data that is received from the OPCUA server
    """
    timestamp: datetime
    name: str
    bool_value: bool | None = None
    float_value: float | None = None
    int_value: int | None = None
    str_value: str | None = None

    def is_valid(self) -> bool:
        """
        Check if the data row is valid
        """
        if sum(x is not None for x in [self.bool_value, self.float_value, self.int_value, self.str_value]) != 1:  # noqa: SIM103
            return False

        return True
