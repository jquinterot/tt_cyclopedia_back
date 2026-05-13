from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ========== Equipment Base ==========
class EquipmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    name: str = Field(..., min_length=1, max_length=255, description="Equipment name")
    brand: str = Field(..., min_length=1, max_length=100, description="Equipment brand")
    category: str = Field(
        ..., pattern="^(blade|rubber|ball|table|net|shoes|other)$", description="Equipment category"
    )
    subcategory: str | None = Field(None, max_length=100, description="Equipment subcategory")
    description: str | None = Field(None, max_length=5000, description="Detailed description")
    image_url: str | None = Field(None, max_length=500, description="Image URL")
    price_usd: float | None = Field(None, ge=0, description="Price in USD")
    release_year: int | None = Field(None, ge=1900, le=2100, description="Release year")
    discontinued: int = Field(0, ge=0, le=1, description="0 = active, 1 = discontinued")


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentResponse(EquipmentBase):
    id: str = Field(..., description="Equipment ID")
    timestamp: datetime = Field(..., description="Creation timestamp")
    avg_rating: float | None = Field(None, ge=0, le=10, description="Average rating")
    review_count: int = Field(0, ge=0, description="Number of reviews")


# ========== Blade Specs ==========
class BladeSpecsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    speed: float | None = Field(None, ge=0, le=100, description="Speed rating")
    control: float | None = Field(None, ge=0, le=100, description="Control rating")
    stiffness: float | None = Field(None, ge=0, le=100, description="Stiffness rating")
    hardness: float | None = Field(None, ge=0, le=100, description="Hardness rating")
    weight_min: int | None = Field(None, ge=50, le=200, description="Minimum weight in grams")
    weight_max: int | None = Field(None, ge=50, le=200, description="Maximum weight in grams")
    plies: int | None = Field(None, ge=1, le=15, description="Number of plies")
    material: str | None = Field(None, max_length=100, description="Blade material")
    thickness: float | None = Field(None, ge=0, description="Thickness in mm")
    head_size: str | None = Field(None, max_length=50, description="Head size")
    handle_types: str | None = Field(
        None, max_length=100, description="Handle types (comma-separated)"
    )


class BladeSpecsCreate(BladeSpecsBase):
    pass


class BladeSpecsResponse(BladeSpecsBase):
    id: str = Field(..., description="Spec ID")
    equipment_id: str = Field(..., description="Associated equipment ID")


# ========== Rubber Specs ==========
class RubberSpecsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    speed: float | None = Field(None, ge=0, le=100, description="Speed rating")
    spin: float | None = Field(None, ge=0, le=100, description="Spin rating")
    control: float | None = Field(None, ge=0, le=100, description="Control rating")
    tackiness: float | None = Field(None, ge=0, le=100, description="Tackiness rating")
    grip: float | None = Field(None, ge=0, le=100, description="Grip rating")
    sponge_thickness: str | None = Field(None, max_length=50, description="Sponge thickness")
    sponge_hardness: str | None = Field(None, max_length=50, description="Sponge hardness")
    top_sheet: str | None = Field(
        None, pattern="^(inverted|short_pips|long_pips|antispin)$", description="Top sheet type"
    )
    weight: str | None = Field(None, max_length=50, description="Weight range")
    durability: float | None = Field(None, ge=0, le=100, description="Durability rating")


class RubberSpecsCreate(RubberSpecsBase):
    pass


class RubberSpecsResponse(RubberSpecsBase):
    id: str = Field(..., description="Spec ID")
    equipment_id: str = Field(..., description="Associated equipment ID")


# ========== Combined Equipment with Specs ==========
class EquipmentDetailResponse(EquipmentResponse):
    blade_specs: BladeSpecsResponse | None = Field(None, description="Blade specifications")
    rubber_specs: RubberSpecsResponse | None = Field(None, description="Rubber specifications")


# ========== Reviews ==========
class EquipmentReviewBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    rating: int = Field(..., ge=1, le=10, description="Overall rating (1-10)")
    speed_rating: float | None = Field(None, ge=0, le=100, description="Speed rating")
    spin_rating: float | None = Field(None, ge=0, le=100, description="Spin rating")
    control_rating: float | None = Field(None, ge=0, le=100, description="Control rating")
    review_text: str | None = Field(None, max_length=5000, description="Review text")
    setup_blade_id: str | None = Field(None, description="Blade used in setup")
    setup_rubber_forehand_id: str | None = Field(None, description="Forehand rubber used")
    setup_rubber_backhand_id: str | None = Field(None, description="Backhand rubber used")


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
    model_config = ConfigDict(extra="forbid")
    playing_style: str = Field(
        ...,
        pattern="^(attacker|all_rounder|defender|beginner|intermediate|advanced)$",
        description="Playing style",
    )
    budget_usd: float | None = Field(None, ge=0, description="Maximum budget in USD")
    preferred_brands: list[str] | None = Field(None, max_length=20, description="Preferred brands")
    hand: str | None = Field("right", pattern="^(right|left)$", description="Playing hand")
    grip: str | None = Field("shakehand", pattern="^(shakehand|penhold)$", description="Grip style")


class SetupRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    blade: EquipmentDetailResponse = Field(..., description="Recommended blade")
    rubber_forehand: EquipmentDetailResponse = Field(..., description="Recommended forehand rubber")
    rubber_backhand: EquipmentDetailResponse = Field(..., description="Recommended backhand rubber")
    total_price_usd: float | None = Field(None, ge=0, description="Total estimated price")
    reasoning: str = Field(..., description="Recommendation explanation")
