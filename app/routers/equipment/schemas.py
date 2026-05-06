from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

# ========== Equipment Base ==========
class EquipmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., min_length=1, max_length=255)
    brand: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., pattern="^(blade|rubber|ball|table|net|shoes|other)$")
    subcategory: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    price_usd: Optional[float] = None
    release_year: Optional[int] = None
    discontinued: int = 0

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentResponse(EquipmentBase):
    id: str
    timestamp: datetime
    avg_rating: Optional[float] = None
    review_count: int = 0

# ========== Blade Specs ==========
class BladeSpecsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    speed: Optional[float] = Field(None, ge=0, le=100)
    control: Optional[float] = Field(None, ge=0, le=100)
    stiffness: Optional[float] = Field(None, ge=0, le=100)
    hardness: Optional[float] = Field(None, ge=0, le=100)
    weight_min: Optional[int] = Field(None, ge=50, le=200)
    weight_max: Optional[int] = Field(None, ge=50, le=200)
    plies: Optional[int] = Field(None, ge=1, le=15)
    material: Optional[str] = None
    thickness: Optional[float] = None
    head_size: Optional[str] = None
    handle_types: Optional[str] = None

class BladeSpecsCreate(BladeSpecsBase):
    pass

class BladeSpecsResponse(BladeSpecsBase):
    id: str
    equipment_id: str

# ========== Rubber Specs ==========
class RubberSpecsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    speed: Optional[float] = Field(None, ge=0, le=100)
    spin: Optional[float] = Field(None, ge=0, le=100)
    control: Optional[float] = Field(None, ge=0, le=100)
    tackiness: Optional[float] = Field(None, ge=0, le=100)
    grip: Optional[float] = Field(None, ge=0, le=100)
    sponge_thickness: Optional[str] = None
    sponge_hardness: Optional[str] = None
    top_sheet: Optional[str] = Field(None, pattern="^(inverted|short_pips|long_pips|antispin)$")
    weight: Optional[str] = None
    durability: Optional[float] = Field(None, ge=0, le=100)

class RubberSpecsCreate(RubberSpecsBase):
    pass

class RubberSpecsResponse(RubberSpecsBase):
    id: str
    equipment_id: str

# ========== Combined Equipment with Specs ==========
class EquipmentDetailResponse(EquipmentResponse):
    blade_specs: Optional[BladeSpecsResponse] = None
    rubber_specs: Optional[RubberSpecsResponse] = None

# ========== Reviews ==========
class EquipmentReviewBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rating: int = Field(..., ge=1, le=10)
    speed_rating: Optional[float] = Field(None, ge=0, le=100)
    spin_rating: Optional[float] = Field(None, ge=0, le=100)
    control_rating: Optional[float] = Field(None, ge=0, le=100)
    review_text: Optional[str] = Field(None, max_length=5000)
    setup_blade_id: Optional[str] = None
    setup_rubber_forehand_id: Optional[str] = None
    setup_rubber_backhand_id: Optional[str] = None

class EquipmentReviewCreate(EquipmentReviewBase):
    pass

class EquipmentReviewResponse(EquipmentReviewBase):
    id: str
    equipment_id: str
    user_id: str
    username: str
    timestamp: datetime

# ========== Setup Recommendation ==========
class SetupRecommendationRequest(BaseModel):
    playing_style: str = Field(..., pattern="^(attacker|all_rounder|defender|beginner|intermediate|advanced)$")
    budget_usd: Optional[float] = None
    preferred_brands: Optional[List[str]] = None
    hand: Optional[str] = Field("right", pattern="^(right|left)$")
    grip: Optional[str] = Field("shakehand", pattern="^(shakehand|penhold)$")

class SetupRecommendation(BaseModel):
    blade: EquipmentDetailResponse
    rubber_forehand: EquipmentDetailResponse
    rubber_backhand: EquipmentDetailResponse
    total_price_usd: Optional[float] = None
    reasoning: str
