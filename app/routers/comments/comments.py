from fastapi import APIRouter

router = APIRouter(prefix="/comments",
                   )


@router.get("")
def get_comments():
    comments = [
        {"comment": "this is a comment", "id": "6j542e"},
        {"comment": "another comment  test", "id": "7k637f"},
        # Add more comments as needed
    ]
    return comments
@router.post("")
def post_comments():
    return {"comment", "txt"}
