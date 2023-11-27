"""File to hold the Agency class and its associated methods."""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ..base import GTFSBase


class Agency(GTFSBase):
    """Agency"""

    __tablename__ = "agencies"
    __filename__ = "agency.txt"

    agency_id = Column(String, primary_key=True)
    agency_name = Column(String)
    agency_url = Column(String)
    agency_timezone = Column(String)
    agency_lang = Column(String)
    agency_phone = Column(String)

    routes = relationship("Route", back_populates="agency", passive_deletes=True)

    def __repr__(self) -> str:
        return f"<Agency(agency_id={self.agency_id})>"

    def as_html(self) -> str:
        """Return the agency as HTML

        Returns:
            str: agency as HTML"""
        return f"""<a href = {self.agency_url} target="_blank"> {self.agency_name}</a> ({self.agency_phone})"""
