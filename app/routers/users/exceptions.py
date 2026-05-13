from fastapi import HTTPException, status


class UserNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"X-Error-Code": "USER_001"},
        )


class UsernameExists(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
            headers={"X-Error-Code": "USER_002"},
        )


class EmailExists(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
            headers={"X-Error-Code": "USER_003"},
        )


class UserNotAuthorized(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
            headers={"X-Error-Code": "USER_004"},
        )
