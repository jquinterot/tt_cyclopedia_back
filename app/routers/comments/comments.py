from fastapi import APIRouter

router = APIRouter(prefix="/comments",
                   )


@router.get("")
def get_comments():
    return {"comment": "this is a comment", "commentId": "6j542e"}
