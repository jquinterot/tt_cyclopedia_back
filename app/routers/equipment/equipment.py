from fastapi import APIRouter, status, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from .models import Equipment, BladeSpecs, RubberSpecs, EquipmentReview
from .schemas import (
    EquipmentCreate, EquipmentResponse, EquipmentDetailResponse,
    BladeSpecsCreate, BladeSpecsResponse, RubberSpecsCreate, RubberSpecsResponse,
    EquipmentReviewCreate, EquipmentReviewResponse,
    SetupRecommendationRequest, SetupRecommendation
)
from app.auth.dependencies import get_current_user, get_current_user_optional
from app.routers.users.models import Users
from app.config.postgres_config import get_db
import shortuuid

router = APIRouter(prefix="/equipment")

# ========== Equipment CRUD ==========
@router.get("", response_model=List[EquipmentResponse], status_code=status.HTTP_200_OK)
def get_equipment(
    category: Optional[str] = Query(None, description="Filter by category: blade, rubber, ball, table, net, shoes, other"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    search: Optional[str] = Query(None, description="Search by name or description", min_length=1, max_length=100),
    db: Session = Depends(get_db)
):
    """Get all equipment with optional filters"""
    query = db.query(Equipment)
    
    if category:
        query = query.filter(Equipment.category == category)
    if brand:
        query = query.filter(Equipment.brand.ilike(f"%{brand}%"))
    if subcategory:
        query = query.filter(Equipment.subcategory == subcategory)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Equipment.name.ilike(search_term),
                Equipment.description.ilike(search_term),
                Equipment.brand.ilike(search_term)
            )
        )
    
    items = query.all()
    result = []
    for item in items:
        avg_rating = db.query(func.avg(EquipmentReview.rating)).filter(EquipmentReview.equipment_id == item.id).scalar()
        review_count = db.query(EquipmentReview).filter(EquipmentReview.equipment_id == item.id).count()
        result.append(EquipmentResponse(
            id=str(item.id),
            name=str(item.name),
            brand=str(item.brand),
            category=str(item.category),
            subcategory=item.subcategory,
            description=item.description,
            image_url=item.image_url,
            price_usd=item.price_usd,
            release_year=item.release_year,
            discontinued=item.discontinued,
            timestamp=item.timestamp,
            avg_rating=round(float(avg_rating), 1) if avg_rating else None,
            review_count=review_count
        ))
    return result


@router.get("/{equipment_id}", response_model=EquipmentDetailResponse, status_code=status.HTTP_200_OK)
def get_equipment_by_id(equipment_id: str, db: Session = Depends(get_db)):
    """Get detailed equipment with specs"""
    item = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    
    avg_rating = db.query(func.avg(EquipmentReview.rating)).filter(EquipmentReview.equipment_id == item.id).scalar()
    review_count = db.query(EquipmentReview).filter(EquipmentReview.equipment_id == item.id).count()
    
    blade_specs = db.query(BladeSpecs).filter(BladeSpecs.equipment_id == equipment_id).first()
    rubber_specs = db.query(RubberSpecs).filter(RubberSpecs.equipment_id == equipment_id).first()
    
    return EquipmentDetailResponse(
        id=str(item.id),
        name=str(item.name),
        brand=str(item.brand),
        category=str(item.category),
        subcategory=item.subcategory,
        description=item.description,
        image_url=item.image_url,
        price_usd=item.price_usd,
        release_year=item.release_year,
        discontinued=item.discontinued,
        timestamp=item.timestamp,
        avg_rating=round(float(avg_rating), 1) if avg_rating else None,
        review_count=review_count,
        blade_specs=BladeSpecsResponse(
            id=str(blade_specs.id),
            equipment_id=str(blade_specs.equipment_id),
            speed=blade_specs.speed,
            control=blade_specs.control,
            stiffness=blade_specs.stiffness,
            hardness=blade_specs.hardness,
            weight_min=blade_specs.weight_min,
            weight_max=blade_specs.weight_max,
            plies=blade_specs.plies,
            material=blade_specs.material,
            thickness=blade_specs.thickness,
            head_size=blade_specs.head_size,
            handle_types=blade_specs.handle_types,
        ) if blade_specs else None,
        rubber_specs=RubberSpecsResponse(
            id=str(rubber_specs.id),
            equipment_id=str(rubber_specs.equipment_id),
            speed=rubber_specs.speed,
            spin=rubber_specs.spin,
            control=rubber_specs.control,
            tackiness=rubber_specs.tackiness,
            grip=rubber_specs.grip,
            sponge_thickness=rubber_specs.sponge_thickness,
            sponge_hardness=rubber_specs.sponge_hardness,
            top_sheet=rubber_specs.top_sheet,
            weight=rubber_specs.weight,
            durability=rubber_specs.durability,
        ) if rubber_specs else None,
    )


@router.get("/{equipment_id}/reviews", response_model=List[EquipmentReviewResponse], status_code=status.HTTP_200_OK)
def get_equipment_reviews(equipment_id: str, db: Session = Depends(get_db)):
    """Get reviews for a piece of equipment"""
    reviews = db.query(EquipmentReview).filter(EquipmentReview.equipment_id == equipment_id).order_by(EquipmentReview.timestamp.desc()).all()
    return reviews


@router.post("/{equipment_id}/reviews", response_model=EquipmentReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    equipment_id: str,
    review: EquipmentReviewCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a review for equipment"""
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    
    existing = db.query(EquipmentReview).filter_by(
        equipment_id=equipment_id, user_id=current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already reviewed this equipment")
    
    new_review = EquipmentReview(
        id=shortuuid.uuid(),
        equipment_id=equipment_id,
        user_id=current_user.id,
        username=current_user.username,
        rating=review.rating,
        speed_rating=review.speed_rating,
        spin_rating=review.spin_rating,
        control_rating=review.control_rating,
        review_text=review.review_text,
        setup_blade_id=review.setup_blade_id,
        setup_rubber_forehand_id=review.setup_rubber_forehand_id,
        setup_rubber_backhand_id=review.setup_rubber_backhand_id,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


# ========== Setup Recommendation ==========
@router.post("/recommend-setup", response_model=SetupRecommendation, status_code=status.HTTP_200_OK)
def recommend_setup(
    request: SetupRecommendationRequest,
    db: Session = Depends(get_db)
):
    """Get equipment recommendations based on playing style"""
    
    # Get all blades and rubbers
    blades = db.query(Equipment).filter(Equipment.category == "blade").all()
    rubbers = db.query(Equipment).filter(Equipment.category == "rubber").all()
    
    if not blades or not rubbers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No equipment data available")
    
    # Get specs for scoring
    blade_scores = []
    for blade in blades:
        specs = db.query(BladeSpecs).filter(BladeSpecs.equipment_id == blade.id).first()
        if not specs:
            continue
        score = 0
        
        if request.playing_style == "beginner":
            score = (specs.control or 0) * 3 + (100 - (specs.speed or 0)) * 2 + (specs.hardness or 0) * 0.5
        elif request.playing_style == "intermediate":
            score = (specs.control or 0) * 2 + (specs.speed or 0) * 1.5 + (specs.stiffness or 0)
        elif request.playing_style == "advanced":
            score = (specs.speed or 0) * 2 + (specs.stiffness or 0) * 1.5 + (specs.control or 0)
        elif request.playing_style == "attacker":
            score = (specs.speed or 0) * 2.5 + (specs.stiffness or 0) * 1.5 + (100 - (specs.control or 0)) * 0.5
        elif request.playing_style == "defender":
            score = (specs.control or 0) * 3 + (100 - (specs.speed or 0)) * 2 + (100 - (specs.stiffness or 0))
        else:  # all_rounder
            score = (specs.control or 0) * 2 + (specs.speed or 0) + abs(50 - (specs.speed or 0)) * -1
        
        # Filter by budget
        if request.budget_usd and blade.price_usd and blade.price_usd > request.budget_usd * 0.6:
            continue
            
        # Filter by brand preference
        if request.preferred_brands and blade.brand not in request.preferred_brands:
            continue
            
        blade_scores.append((score, blade, specs))
    
    rubber_scores = []
    for rubber in rubbers:
        specs = db.query(RubberSpecs).filter(RubberSpecs.equipment_id == rubber.id).first()
        if not specs:
            continue
        score = 0
        
        if request.playing_style == "beginner":
            score = (specs.control or 0) * 3 + (100 - (specs.speed or 0)) * 1.5 + (100 - (specs.spin or 0)) * 0.5
        elif request.playing_style == "intermediate":
            score = (specs.control or 0) * 1.5 + (specs.spin or 0) * 1.5 + (specs.speed or 0)
        elif request.playing_style == "advanced":
            score = (specs.speed or 0) * 2 + (specs.spin or 0) * 2 + (specs.control or 0)
        elif request.playing_style == "attacker":
            score = (specs.speed or 0) * 2 + (specs.spin or 0) * 2 + (specs.grip or 0)
        elif request.playing_style == "defender":
            score = (specs.control or 0) * 3 + (100 - (specs.speed or 0)) * 2
        else:  # all_rounder
            score = (specs.control or 0) * 2 + (specs.speed or 0) + (specs.spin or 0)
        
        if request.budget_usd and rubber.price_usd and rubber.price_usd > request.budget_usd * 0.25:
            continue
            
        if request.preferred_brands and rubber.brand not in request.preferred_brands:
            continue
            
        rubber_scores.append((score, rubber, specs))
    
    if not blade_scores:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching blades found")
    if not rubber_scores:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching rubbers found")
    
    # Sort by score
    blade_scores.sort(key=lambda x: x[0], reverse=True)
    rubber_scores.sort(key=lambda x: x[0], reverse=True)
    
    best_blade = blade_scores[0][1]
    best_blade_specs = blade_scores[0][2]
    
    # Pick FH rubber (more offensive)
    fh_rubber = rubber_scores[0][1]
    fh_rubber_specs = rubber_scores[0][2]
    
    # Pick BH rubber (more control, or same if limited options)
    bh_rubber = rubber_scores[1][1] if len(rubber_scores) > 1 else rubber_scores[0][1]
    bh_rubber_specs = rubber_scores[1][2] if len(rubber_scores) > 1 else rubber_scores[0][2]
    
    total_price = 0
    if best_blade.price_usd:
        total_price += best_blade.price_usd
    if fh_rubber.price_usd:
        total_price += fh_rubber.price_usd
    if bh_rubber.price_usd:
        total_price += bh_rubber.price_usd
    
    reasoning = f"For a {request.playing_style} player, we recommend:\n\n"
    reasoning += f"**Blade: {best_blade.name} ({best_blade.brand})**\n"
    reasoning += f"- Speed: {best_blade_specs.speed}/100, Control: {best_blade_specs.control}/100\n"
    reasoning += f"- Material: {best_blade_specs.material}\n\n"
    reasoning += f"**Forehand Rubber: {fh_rubber.name} ({fh_rubber.brand})**\n"
    reasoning += f"- Speed: {fh_rubber_specs.speed}/100, Spin: {fh_rubber_specs.spin}/100\n"
    reasoning += f"- Top sheet: {fh_rubber_specs.top_sheet}\n\n"
    reasoning += f"**Backhand Rubber: {bh_rubber.name} ({bh_rubber.brand})**\n"
    reasoning += f"- Speed: {bh_rubber_specs.speed}/100, Control: {bh_rubber_specs.control}/100\n"
    reasoning += f"- Top sheet: {bh_rubber_specs.top_sheet}\n\n"
    reasoning += f"Total estimated price: ${total_price:.2f}"
    
    def to_detail_response(equipment, db_session):
        blade_s = db_session.query(BladeSpecs).filter(BladeSpecs.equipment_id == equipment.id).first()
        rubber_s = db_session.query(RubberSpecs).filter(RubberSpecs.equipment_id == equipment.id).first()
        avg = db_session.query(func.avg(EquipmentReview.rating)).filter(EquipmentReview.equipment_id == equipment.id).scalar()
        count = db_session.query(EquipmentReview).filter(EquipmentReview.equipment_id == equipment.id).count()
        return EquipmentDetailResponse(
            id=str(equipment.id),
            name=str(equipment.name),
            brand=str(equipment.brand),
            category=str(equipment.category),
            subcategory=equipment.subcategory,
            description=equipment.description,
            image_url=equipment.image_url,
            price_usd=equipment.price_usd,
            release_year=equipment.release_year,
            discontinued=equipment.discontinued,
            timestamp=equipment.timestamp,
            avg_rating=round(float(avg), 1) if avg else None,
            review_count=count,
            blade_specs=BladeSpecsResponse(
                id=str(blade_s.id), equipment_id=str(blade_s.equipment_id),
                speed=blade_s.speed, control=blade_s.control, stiffness=blade_s.stiffness,
                hardness=blade_s.hardness, weight_min=blade_s.weight_min, weight_max=blade_s.weight_max,
                plies=blade_s.plies, material=blade_s.material, thickness=blade_s.thickness,
                head_size=blade_s.head_size, handle_types=blade_s.handle_types,
            ) if blade_s else None,
            rubber_specs=RubberSpecsResponse(
                id=str(rubber_s.id), equipment_id=str(rubber_s.equipment_id),
                speed=rubber_s.speed, spin=rubber_s.spin, control=rubber_s.control,
                tackiness=rubber_s.tackiness, grip=rubber_s.grip,
                sponge_thickness=rubber_s.sponge_thickness, sponge_hardness=rubber_s.sponge_hardness,
                top_sheet=rubber_s.top_sheet, weight=rubber_s.weight, durability=rubber_s.durability,
            ) if rubber_s else None,
        )
    
    return SetupRecommendation(
        blade=to_detail_response(best_blade, db),
        rubber_forehand=to_detail_response(fh_rubber, db),
        rubber_backhand=to_detail_response(bh_rubber, db),
        total_price_usd=round(total_price, 2) if total_price > 0 else None,
        reasoning=reasoning
    )
