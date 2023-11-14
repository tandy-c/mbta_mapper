"""Holds the base class for all GTFS elements"""
from typing import Iterable, Any
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.inspection import inspect


class GTFSBase(DeclarativeBase):
    """Base class for all GTFS elements

    Attributes:
        __tablename__ (str): name of the table
        __table_args__ (dict[str, Any]): table arguments
    """

    __filename__: str
    __table_args__ = {"sqlite_autoincrement": False, "sqlite_with_rowid": False}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({''.join(key + '=' + str(getattr(self, key, None)) for key in self.__get_primary())})>"

    def __str__(self) -> str:
        return self.as_dict().__str__()

    def __get_primary(self) -> Iterable[str]:
        """Returns the primary keys of the table.

        Returns:
            Iterable[str]: primary keys of the table
        """

        return (key.name for key in inspect(__class__).primary_key)

    def as_dict(
        self, exclude: list[str] = None, include: list[str] = None
    ) -> dict[str, Any]:
        """Returns a dict representation of the object.

        Args:
            exclude (list[str]): columns to exclude from the dict (default: None)
            include (list[str]): ORMS to include in the dict (default: None)
        Returns:
            dict[str, Any]: dict representation of the object
        """
        class_dict = self.__dict__
        for key in include or []:
            if not hasattr(self, key):
                continue
            __attr = getattr(self, key)
            class_dict[key] = (
                [i.as_dict(exclude, include) for i in __attr]
                if isinstance(__attr, list)
                else __attr.as_dict(exclude, include)
                if __attr
                else None
            )
        for key in (exclude or []) + ["_sa_instance_state"]:
            del class_dict[key]
        return class_dict
