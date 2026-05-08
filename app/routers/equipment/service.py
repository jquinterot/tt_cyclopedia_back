from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
import shortuuid

from .models import Equipment, BladeSpecs, RubberSpecs, EquipmentReview
from .schemas import (
    EquipmentResponse, EquipmentDetailResponse,
    BladeSpecsResponse, RubberSpecsResponse,
    EquipmentReviewResponse, SetupRecommendation
)
from .exceptions import (
    EquipmentNotFound, EquipmentNoData,
    EquipmentNoBlades, EquipmentNoRubbers,
    EquipmentAlreadyReviewed,
)


def _to_equipment_response(item: Equipment, avg_rating: Optional[float], review_count: int) -> EquipmentResponse:
    return EquipmentResponse(
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
    )


def _to_detail_response(equipment: Equipment, db: Session) -> EquipmentDetailResponse:
    blade_s = db.query(BladeSpecs).filter(BladeSpecs.equipment_id == equipment.id).first()
    rubber_s = db.query(RubberSpecs).filter(RubberSpecs.equipment_id == equipment.id).first()
    avg = db.query(func.avg(EquipmentReview.rating)).filter(EquipmentReview.equipment_id == equipment.id).scalar()
    count = db.query(EquipmentReview).filter(EquipmentReview.equipment_id == equipment.id).count()
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


def get_equipment_list(
    db: Session,
    category: Optional[str],
    brand: Optional[str],
    subcategory: Optional[str],
    search: Optional[str],
) -> List[EquipmentResponse]:
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
                Equipment.brand.ilike(search_term),
            )
        )

    items = query.all()
    if not items:
        return []

    item_ids = [item.id for item in items]
    avg_ratings = {
        row.equipment_id: row.avg_rating
        for row in db.query(
            EquipmentReview.equipment_id,
            func.avg(EquipmentReview.rating).label("avg_rating")
        ).filter(EquipmentReview.equipment_id.in_(item_ids)).group_by(EquipmentReview.equipment_id).all()
    }
    review_counts = {
        row.equipment_id: row.count
        for row in db.query(
            EquipmentReview.equipment_id,
            func.count(EquipmentReview.id).label("count")
        ).filter(EquipmentReview.equipment_id.in_(item_ids)).group_by(EquipmentReview.equipment_id).all()
    }

    result = []
    for item in items:
        avg_rating = avg_ratings.get(item.id)
        review_count = review_counts.get(item.id, 0)
        result.append(_to_equipment_response(item, avg_rating, review_count))
    return result


def get_equipment_by_id(db: Session, equipment_id: str) -> EquipmentDetailResponse:
    item = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not item:
        raise EquipmentNotFound()
    return _to_detail_response(item, db)


def get_equipment_reviews(db: Session, equipment_id: str) -> List[EquipmentReviewResponse]:
    reviews = db.query(EquipmentReview).filter(
        EquipmentReview.equipment_id == equipment_id
    ).order_by(EquipmentReview.timestamp.desc()).all()
    return reviews


def create_equipment_review(db: Session, equipment_id: str, review_data, current_user) -> EquipmentReviewResponse:
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise EquipmentNotFound()

    existing = db.query(EquipmentReview).filter_by(
        equipment_id=equipment_id, user_id=current_user.id
    ).first()
    if existing:
        raise EquipmentAlreadyReviewed()

    new_review = EquipmentReview(
        id=shortuuid.uuid(),
        equipment_id=equipment_id,
        user_id=current_user.id,
        username=current_user.username,
        rating=review_data.rating,
        speed_rating=review_data.speed_rating,
        spin_rating=review_data.spin_rating,
        control_rating=review_data.control_rating,
        review_text=review_data.review_text,
        setup_blade_id=review_data.setup_blade_id,
        setup_rubber_forehand_id=review_data.setup_rubber_forehand_id,
        setup_rubber_backhand_id=review_data.setup_rubber_backhand_id,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


def recommend_setup(db: Session, request) -> SetupRecommendation:
    blades = db.query(Equipment).filter(Equipment.category == "blade").all()
    rubbers = db.query(Equipment).filter(Equipment.category == "rubber").all()

    if not blades or not rubbers:
        raise EquipmentNoData()

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
        else:
            score = (specs.control or 0) * 2 + (specs.speed or 0) + abs(50 - (specs.speed or 0)) * -1

        if request.budget_usd and blade.price_usd and blade.price_usd > request.budget_usd * 0.6:
            continue
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
        else:
            score = (specs.control or 0) * 2 + (specs.speed or 0) + (specs.spin or 0)

        if request.budget_usd and rubber.price_usd and rubber.price_usd > request.budget_usd * 0.25:
            continue
        if request.preferred_brands and rubber.brand not in request.preferred_brands:
            continue
        rubber_scores.append((score, rubber, specs))

    if not blade_scores:
        raise EquipmentNoBlades()
    if not rubber_scores:
        raise EquipmentNoRubbers()

    blade_scores.sort(key=lambda x: x[0], reverse=True)
    rubber_scores.sort(key=lambda x: x[0], reverse=True)

    best_blade = blade_scores[0][1]
    best_blade_specs = blade_scores[0][2]

    fh_rubber = rubber_scores[0][1]
    fh_rubber_specs = rubber_scores[0][2]

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

    return SetupRecommendation(
        blade=_to_detail_response(best_blade, db),
        rubber_forehand=_to_detail_response(fh_rubber, db),
        rubber_backhand=_to_detail_response(bh_rubber, db),
        total_price_usd=round(total_price, 2) if total_price > 0 else None,
        reasoning=reasoning,
    )
