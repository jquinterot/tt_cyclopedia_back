from fastapi import APIRouter

router = APIRouter(prefix="/comments",
                   )


##Add Pydantic model and db schema to get comments from db, equal to insert in db

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
