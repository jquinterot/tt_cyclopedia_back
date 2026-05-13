from fastapi import HTTPException, status


class PostNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
            headers={"X-Error-Code": "POST_001"},
        )


class PostNotAuthorized(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
            headers={"X-Error-Code": "POST_002"},
        )


class PostInvalidStats(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid stats JSON format",
            headers={"X-Error-Code": "POST_003"},
        )


class PostEquipmentNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment not found",
            headers={"X-Error-Code": "POST_004"},
        )


class PostUnsupportedFileType(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only JPEG, PNG, and WEBP are allowed.",
            headers={"X-Error-Code": "POST_005"},
        )


class PostFileTooLarge(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit",
            headers={"X-Error-Code": "POST_006"},
        )


class PostImageUploadFailed(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image. Please try again.",
            headers={"X-Error-Code": "POST_007"},
        )


class PostCreationFailed(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post with this title already exists",
            headers={"X-Error-Code": "POST_008"},
        )


class PostDeleteFailed(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting posts. Please try again.",
            headers={"X-Error-Code": "POST_009"},
        )
