from fastapi import HTTPException, status


class EquipmentNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
            headers={"X-Error-Code": "EQUIP_001"},
        )


class EquipmentNoData(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No equipment data available",
            headers={"X-Error-Code": "EQUIP_002"},
        )


class EquipmentNoBlades(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching blades found",
            headers={"X-Error-Code": "EQUIP_003"},
        )


class EquipmentNoRubbers(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching rubbers found",
            headers={"X-Error-Code": "EQUIP_004"},
        )


class EquipmentAlreadyReviewed(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this equipment",
            headers={"X-Error-Code": "EQUIP_005"},
        )
