from fastapi import APIRouter, status, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.auth.dependencies import get_current_user, get_current_user_optional
from app.routers.users.models import Users
from app.config.postgres_config import get_db
from app.middleware.rate_limiter import read_rate_limit, write_rate_limit
from .schemas import (
    EquipmentResponse, EquipmentDetailResponse,
    EquipmentReviewCreate, EquipmentReviewResponse,
    SetupRecommendationRequest, SetupRecommendation
)
from . import service

router = APIRouter(prefix="/equipment")


@router.get("", response_model=List[EquipmentResponse], status_code=status.HTTP_200_OK)
def get_equipment(
    category: Optional[str] = Query(None, description="Filter by category: blade, rubber, ball, table, net, shoes, other"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    search: Optional[str] = Query(None, description="Search by name or description", min_length=1, max_length=100),
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_equipment_list(db, category, brand, subcategory, search)


@router.get("/{equipment_id}", response_model=EquipmentDetailResponse, status_code=status.HTTP_200_OK)
def get_equipment_by_id(
    equipment_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_equipment_by_id(db, equipment_id)


@router.get("/{equipment_id}/reviews", response_model=List[EquipmentReviewResponse], status_code=status.HTTP_200_OK)
def get_equipment_reviews(
    equipment_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.get_equipment_reviews(db, equipment_id)


@router.post("/{equipment_id}/reviews", response_model=EquipmentReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    equipment_id: str,
    review: EquipmentReviewCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: bool = Depends(write_rate_limit),
):
    return service.create_equipment_review(db, equipment_id, review, current_user)


@router.post("/recommend-setup", response_model=SetupRecommendation, status_code=status.HTTP_200_OK)
def recommend_setup(
    request: SetupRecommendationRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(read_rate_limit),
):
    return service.recommend_setup(db, request)
