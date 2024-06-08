from fastapi import APIRouter

router = APIRouter(prefix="/posts",
                   )


@router.get("")
def get_posts():
    return {"postName": "post", "postId": "1F3J"}
