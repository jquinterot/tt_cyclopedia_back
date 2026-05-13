from fastapi import HTTPException, status


class ForumNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum not found",
            headers={"X-Error-Code": "FORUM_001"},
        )


class ForumNotAuthorized(HTTPException):
    def __init__(self, action="edit"):
        codes = {"edit": "FORUM_002", "delete": "FORUM_003"}
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You can only {action} your own forums",
            headers={"X-Error-Code": codes.get(action, "FORUM_002")},
        )


class ForumCommentNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
            headers={"X-Error-Code": "FORUM_004"},
        )


class ForumCommentNotAuthorized(HTTPException):
    def __init__(self, action="edit"):
        codes = {"edit": "FORUM_005", "delete": "FORUM_006"}
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You can only {action} your own comments",
            headers={"X-Error-Code": codes.get(action, "FORUM_005")},
        )
