from datetime import UTC, datetime

import shortuuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint

from app.config.postgres_config import Base, get_schema_kwargs

schema_kwargs = get_schema_kwargs()


class Equipment(Base):
    """Base equipment table - blades, rubbers, balls, etc."""

    __tablename__ = "equipment"
    if schema_kwargs:
        __table_args__ = schema_kwargs

    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    name = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # blade, rubber, ball, table, etc.
    subcategory = Column(String(50), nullable=True)  # offensive, allround, defensive, etc.
    description = Column(Text, nullable=True)
    image_url = Column(String(512), nullable=True)
    price_usd = Column(Float, nullable=True)
    release_year = Column(Integer, nullable=True)
    discontinued = Column(Integer, default=0)  # 0 = active, 1 = discontinued
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))


class BladeSpecs(Base):
    """Detailed specifications for blades"""

    __tablename__ = "blade_specs"
    if schema_kwargs:
        __table_args__ = schema_kwargs

    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    equipment_id = Column(String(255), ForeignKey("equipment.id"), nullable=False, unique=True)
    speed = Column(Float, nullable=True)  # 1-10 or 1-100 scale
    control = Column(Float, nullable=True)
    stiffness = Column(Float, nullable=True)
    hardness = Column(Float, nullable=True)
    weight_min = Column(Integer, nullable=True)  # grams
    weight_max = Column(Integer, nullable=True)
    plies = Column(Integer, nullable=True)
    material = Column(String(100), nullable=True)  # wood, carbon, arylate-carbon, etc.
    thickness = Column(Float, nullable=True)  # mm
    head_size = Column(String(50), nullable=True)  # standard, oversize, etc.
    handle_types = Column(String(200), nullable=True)  # FL, ST, AN, CS (comma separated)


class RubberSpecs(Base):
    """Detailed specifications for rubbers"""

    __tablename__ = "rubber_specs"
    if schema_kwargs:
        __table_args__ = schema_kwargs

    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    equipment_id = Column(String(255), ForeignKey("equipment.id"), nullable=False, unique=True)
    speed = Column(Float, nullable=True)
    spin = Column(Float, nullable=True)
    control = Column(Float, nullable=True)
    tackiness = Column(Float, nullable=True)  # 0 = non-tacky, 10 = very tacky
    grip = Column(Float, nullable=True)  # how well it grips the ball
    sponge_thickness = Column(String(50), nullable=True)  # max, 2.0, 1.9, 1.5, etc.
    sponge_hardness = Column(String(50), nullable=True)  # degrees or soft/medium/hard
    top_sheet = Column(String(100), nullable=True)  # inverted, short pips, long pips, antispin
    weight = Column(String(50), nullable=True)  # uncut weight range
    durability = Column(Float, nullable=True)  # 1-10


class EquipmentReview(Base):
    """User reviews and ratings for equipment"""

    __tablename__ = "equipment_reviews"
    if schema_kwargs:
        __table_args__ = (
            UniqueConstraint("user_id", "equipment_id", name="_user_equipment_review_uc"),
            schema_kwargs,
        )
    else:
        __table_args__ = (
            UniqueConstraint("user_id", "equipment_id", name="_user_equipment_review_uc"),
        )

    id = Column(String(255), primary_key=True, default=lambda: shortuuid.uuid())
    equipment_id = Column(String(255), ForeignKey("equipment.id"), nullable=False)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False)
    username = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars or 1-10
    speed_rating = Column(Float, nullable=True)
    spin_rating = Column(Float, nullable=True)
    control_rating = Column(Float, nullable=True)
    review_text = Column(Text, nullable=True)
    setup_blade_id = Column(String(255), nullable=True)  # blade used with this rubber
    setup_rubber_forehand_id = Column(String(255), nullable=True)
    setup_rubber_backhand_id = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
