from fastapi import HTTPException, status

class CommentNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
            headers={"X-Error-Code": "COMMENT_001"},
        )

class CommentNotAuthorized(HTTPException):
    def __init__(self, action="edit"):
        codes = {"edit": "COMMENT_002", "delete": "COMMENT_003"}
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You can only {action} your own comments",
            headers={"X-Error-Code": codes.get(action, "COMMENT_002")},
        )
