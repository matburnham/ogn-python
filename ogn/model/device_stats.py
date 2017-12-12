from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geometry
from sqlalchemy import Column, String, Integer, Date, Float, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class DeviceStats(Base):
    __tablename__ = "device_stats"

    id = Column(Integer, primary_key=True)

    date = Column(Date)
    receiver_count = Column(Integer)
    aircraft_beacon_count = Column(Integer)
    max_altitude = Column(Float)

    # Relations
    device_id = Column(Integer, ForeignKey('device.id', ondelete='SET NULL'), index=True)
    device = relationship('Device', foreign_keys=[device_id])
