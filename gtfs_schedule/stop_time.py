"""File to hold the Calendar class and its associated methods."""
from datetime import datetime

from sqlalchemy import Integer, ForeignKey, Column, String
from sqlalchemy.orm import relationship, reconstructor

from shared_code.gtfs_helper_time_functions import to_seconds, seconds_to_iso
from gtfs_loader.gtfs_base import GTFSBase


class StopTime(GTFSBase):
    """Stop Times"""

    __tablename__ = "stop_times"

    trip_id = Column(
        String,
        ForeignKey("trips.trip_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    arrival_time = Column(String)
    departure_time = Column(String)
    stop_id = Column(
        String, ForeignKey("stops.stop_id", onupdate="CASCADE", ondelete="CASCADE")
    )
    stop_sequence = Column(Integer, primary_key=True)
    stop_headsign = Column(String)
    pickup_type = Column(String)
    drop_off_type = Column(String)
    timepoint = Column(String)
    checkpoint_id = Column(String)
    continuous_pickup = Column(String)
    continuous_drop_off = Column(String)

    stop = relationship("Stop", back_populates="stop_times")
    trip = relationship("Trip", back_populates="stop_times")

    to_transfer = relationship(
        "Transfer",
        primaryjoin="""and_(
            StopTime.trip_id==foreign(Transfer.to_trip_id),
            StopTime.stop_id==foreign(Transfer.to_stop_id) 
            )""",
        viewonly=True,
    )

    from_transfer = relationship(
        "Transfer",
        primaryjoin="""and_(
            StopTime.trip_id==foreign(Transfer.from_trip_id),
            StopTime.stop_id==foreign(Transfer.from_stop_id)
            )""",
        viewonly=True,
    )

    @reconstructor
    def init_on_load(self):
        """Reconstructs the object on load from the database.
        executes after the object is loaded from the database and in init"""
        # pylint: disable=attribute-defined-outside-init

        self.arrival_seconds = to_seconds(self.arrival_time)
        self.departure_seconds = to_seconds(self.departure_time)
        self.destination_label = self.stop_headsign or self.trip.trip_headsign

    def __repr__(self) -> str:
        return f"<StopTime(trip_id={self.trip_id}, stop_id={self.stop_id})>"

    def is_destination(self) -> bool:
        """Returns True if the stop time is the destination for the trip"""
        return self == self.trip.destination_stop_time
