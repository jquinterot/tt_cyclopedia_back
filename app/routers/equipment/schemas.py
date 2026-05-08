from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

# ========== Equipment Base ==========
class EquipmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    name: str = Field(..., min_length=1, max_length=255, description="Equipment name")
    brand: str = Field(..., min_length=1, max_length=100, description="Equipment brand")
    category: str = Field(..., pattern="^(blade|rubber|ball|table|net|shoes|other)$", description="Equipment category")
    subcategory: Optional[str] = Field(None, max_length=100, description="Equipment subcategory")
    description: Optional[str] = Field(None, max_length=5000, description="Detailed description")
    image_url: Optional[str] = Field(None, max_length=500, description="Image URL")
    price_usd: Optional[float] = Field(None, ge=0, description="Price in USD")
    release_year: Optional[int] = Field(None, ge=1900, le=2100, description="Release year")
    discontinued: int = Field(0, ge=0, le=1, description="0 = active, 1 = discontinued")

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentResponse(EquipmentBase):
    id: str = Field(..., description="Equipment ID")
    timestamp: datetime = Field(..., description="Creation timestamp")
    avg_rating: Optional[float] = Field(None, ge=0, le=10, description="Average rating")
    review_count: int = Field(0, ge=0, description="Number of reviews")

# ========== Blade Specs ==========
class BladeSpecsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    speed: Optional[float] = Field(None, ge=0, le=100, description="Speed rating")
    control: Optional[float] = Field(None, ge=0, le=100, description="Control rating")
    stiffness: Optional[float] = Field(None, ge=0, le=100, description="Stiffness rating")
    hardness: Optional[float] = Field(None, ge=0, le=100, description="Hardness rating")
    weight_min: Optional[int] = Field(None, ge=50, le=200, description="Minimum weight in grams")
    weight_max: Optional[int] = Field(None, ge=50, le=200, description="Maximum weight in grams")
    plies: Optional[int] = Field(None, ge=1, le=15, description="Number of plies")
    material: Optional[str] = Field(None, max_length=100, description="Blade material")
    thickness: Optional[float] = Field(None, ge=0, description="Thickness in mm")
    head_size: Optional[str] = Field(None, max_length=50, description="Head size")
    handle_types: Optional[str] = Field(None, max_length=100, description="Handle types (comma-separated)")

class BladeSpecsCreate(BladeSpecsBase):
    pass

class BladeSpecsResponse(BladeSpecsBase):
    id: str = Field(..., description="Spec ID")
    equipment_id: str = Field(..., description="Associated equipment ID")

# ========== Rubber Specs ==========
class RubberSpecsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    speed: Optional[float] = Field(None, ge=0, le=100, description="Speed rating")
    spin: Optional[float] = Field(None, ge=0, le=100, description="Spin rating")
    control: Optional[float] = Field(None, ge=0, le=100, description="Control rating")
    tackiness: Optional[float] = Field(None, ge=0, le=100, description="Tackiness rating")
    grip: Optional[float] = Field(None, ge=0, le=100, description="Grip rating")
    sponge_thickness: Optional[str] = Field(None, max_length=50, description="Sponge thickness")
    sponge_hardness: Optional[str] = Field(None, max_length=50, description="Sponge hardness")
    top_sheet: Optional[str] = Field(None, pattern="^(inverted|short_pips|long_pips|antispin)$", description="Top sheet type")
    weight: Optional[str] = Field(None, max_length=50, description="Weight range")
    durability: Optional[float] = Field(None, ge=0, le=100, description="Durability rating")

class RubberSpecsCreate(RubberSpecsBase):
    pass

class RubberSpecsResponse(RubberSpecsBase):
    id: str = Field(..., description="Spec ID")
    equipment_id: str = Field(..., description="Associated equipment ID")

# ========== Combined Equipment with Specs ==========
class EquipmentDetailResponse(EquipmentResponse):
    blade_specs: Optional[BladeSpecsResponse] = Field(None, description="Blade specifications")
    rubber_specs: Optional[RubberSpecsResponse] = Field(None, description="Rubber specifications")

# ========== Reviews ==========
class EquipmentReviewBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    rating: int = Field(..., ge=1, le=10, description="Overall rating (1-10)")
    speed_rating: Optional[float] = Field(None, ge=0, le=100, description="Speed rating")
    spin_rating: Optional[float] = Field(None, ge=0, le=100, description="Spin rating")
    control_rating: Optional[float] = Field(None, ge=0, le=100, description="Control rating")
    review_text: Optional[str] = Field(None, max_length=5000, description="Review text")
    setup_blade_id: Optional[str] = Field(None, description="Blade used in setup")
    setup_rubber_forehand_id: Optional[str] = Field(None, description="Forehand rubber used")
    setup_rubber_backhand_id: Optional[str] = Field(None, description="Backhand rubber used")

class EquipmentReviewCreate(EquipmentReviewBase):
    pass

class EquipmentReviewResponse(EquipmentReviewBase):
    id: str = Field(..., description="Review ID")
    equipment_id: str = Field(..., description="Associated equipment ID")
    user_id: str = Field(..., description="Author user ID")
    username: str = Field(..., description="Author username")
    timestamp: datetime = Field(..., description="Review timestamp")

# ========== Setup Recommendation ==========
class SetupRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    playing_style: str = Field(..., pattern="^(attacker|all_rounder|defender|beginner|intermediate|advanced)$", description="Playing style")
    budget_usd: Optional[float] = Field(None, ge=0, description="Maximum budget in USD")
    preferred_brands: Optional[List[str]] = Field(None, max_length=20, description="Preferred brands")
    hand: Optional[str] = Field("right", pattern="^(right|left)$", description="Playing hand")
    grip: Optional[str] = Field("shakehand", pattern="^(shakehand|penhold)$", description="Grip style")

class SetupRecommendation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    blade: EquipmentDetailResponse = Field(..., description="Recommended blade")
    rubber_forehand: EquipmentDetailResponse = Field(..., description="Recommended forehand rubber")
    rubber_backhand: EquipmentDetailResponse = Field(..., description="Recommended backhand rubber")
    total_price_usd: Optional[float] = Field(None, ge=0, description="Total estimated price")
    reasoning: str = Field(..., description="Recommendation explanation")
